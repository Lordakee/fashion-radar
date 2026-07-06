# Stage 321 ROW ONE Editorial Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only ROW ONE homepage Editorial Brief section that turns existing saved local article and story data into readable bilingual editorial paragraphs.

**Architecture:** Build a deterministic private editorial brief object during generated-site rendering, pass it only into `render_index_html()`, and render it as HTML between saved article content organization and the lead story. Keep the app payload and all JSON contracts unchanged.

**Tech Stack:** Python, Pydantic models already in `row_one.models`, string-rendered HTML/CSS in `templates.py`, pytest, Ruff, Claude Code plan/code review workflow.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Build the generated-site-only editorial brief from `edition` and `local_articles_by_story_id`.
  - Import `_EditorialBrief` and `_EditorialBriefItem` from `templates.py`.
  - Pass it to `render_index_html()` only.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Define private frozen dataclasses `_EditorialBriefItem` and `_EditorialBrief`.
  - Accept optional `editorial_brief`.
  - Render the homepage `editorial-brief` section after saved article content organization and before lead story.
  - Add private helpers and CSS.
- Modify: `tests/test_row_one_render.py`
  - Add direct render tests for content, omission, escaping, safe links, ordering, and CSS.
- Modify: `tests/test_workflows.py`
  - Add generated-site-only HTML/JSON boundary assertions.
- Modify: `tests/test_row_one_docs.py`
  - Add Stage 321 docs boundary test.
- Modify: `README.md`
  - Add Stage 321 generated-site-only boundary paragraph.
- Modify: `docs/row-one.md`
  - Add Stage 321 generated-site-only boundary paragraph.
- Create: `docs/reviews/claude-code-stage-321-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-321-code-review.md`

## Task 1: Failing Render Tests

- [ ] **Step 1: Add homepage content test**

Add a test near the saved article content organization and Daily Edit tests in `tests/test_row_one_render.py`:

```python
def test_render_row_one_site_includes_editorial_brief_from_local_articles(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="brand")]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert '<span data-lang="en">Editorial Brief</span>' in section_html
    assert '<span data-lang="zh">编辑正文</span>' in section_html
    assert "What changed today" in section_html
    assert "今日变化" in section_html
    assert "Why it matters" in section_html
    assert "为什么重要" in section_html
    assert "What to read locally" in section_html
    assert "本地阅读路径" in section_html
    assert "The Row is today's priority signal." in section_html
    assert "The saved article frames a new signal." in section_html
    assert "Vogue Business" in section_html
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert index_html.index('class="saved-article-content-organization"') < section_start
    assert section_start < index_html.index('class="lead-story"')
```

The existing `_signal_briefing_local_article()` fixture already includes a `what_happened` brief-section body with `"The saved article frames a new signal."`; this test intentionally asserts that the `What changed today` paragraph combines story editorial takeaway text with local article `what_happened` brief-section text.

- [ ] **Step 2: Add omission test**

```python
def test_render_index_html_omits_editorial_brief_without_usable_content() -> None:
    index_html = render_index_html(_edition(), editorial_brief=None)

    assert 'class="editorial-brief"' not in index_html
    assert "Editorial Brief" not in index_html
    assert "编辑正文" not in index_html
```

- [ ] **Step 3: Add escaping and link safety test**

Extend the `templates` import block in `tests/test_row_one_render.py` with:

```python
    EDITORIAL_BRIEF_BODY_EXCERPT_CHARS,
    _EditorialBrief,
    _EditorialBriefItem,
```

```python
def test_render_index_html_escapes_editorial_brief_and_filters_links() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Unsafe <b>", zh="危险 <b>"),
                    body=LocalizedText(en="Body <script>", zh="正文 <script>"),
                    href="javascript:alert(1)",
                    meta=LocalizedText(en="Meta <i>", zh="元信息 <i>"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="External", zh="外链"),
                    body=LocalizedText(en="External body.", zh="外链正文。"),
                    href="https://evil.example/story",
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Safe detail", zh="安全详情"),
                    body=LocalizedText(en="Detail body.", zh="详情正文。"),
                    href="details/the-row-signal-1234567890.html",
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Safe", zh="安全"),
                    body=LocalizedText(en="Safe body.", zh="安全正文。"),
                    href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Unsafe &lt;b&gt;" in section_html
    assert "Body &lt;script&gt;" in section_html
    assert "Meta &lt;i&gt;" in section_html
    assert "<script>" not in section_html
    assert "<b>" not in section_html
    assert "javascript:alert" not in section_html
    assert "https://evil.example" not in section_html
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    # The paragraph-fragment item is fourth and is excluded by the 3-item cap;
    # this assertion is not a paragraph-link rejection rule.
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' not in section_html
```

- [ ] **Step 4: Add story fallback test**

```python
def test_render_row_one_site_editorial_brief_falls_back_to_story_text(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="brand")]

    render_row_one_site(edition, tmp_path, local_articles_by_story_id={})

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="editorial-brief"' in index_html
    assert "The Row is today's priority signal." in index_html
    assert "This signal belongs in Top Stories." in index_html
```

- [ ] **Step 5: Add content-section fragment href test**

```python
def test_render_index_html_accepts_editorial_brief_content_section_href() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Content Section", zh="内容段落"),
                    body=LocalizedText(en="Content section body.", zh="内容段落正文。"),
                    href="details/the-row-signal-1234567890.html#local-article-content-section-1",
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert 'href="details/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
```

- [ ] **Step 6: Add three-item cap test**

```python
def test_render_index_html_caps_editorial_brief_to_three_items() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="One", zh="一"),
                    body=LocalizedText(en="First body.", zh="第一条。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Two", zh="二"),
                    body=LocalizedText(en="Second body.", zh="第二条。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Three", zh="三"),
                    body=LocalizedText(en="Third body.", zh="第三条。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Four", zh="四"),
                    body=LocalizedText(en="Fourth body.", zh="第四条。"),
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "First body." in section_html
    assert "Second body." in section_html
    assert "Third body." in section_html
    assert "Fourth body." not in section_html
```

- [ ] **Step 7: Add body length cap test**

```python
def test_render_index_html_caps_editorial_brief_body_length() -> None:
    long_body = "Long body " * 40
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Long", zh="长正文"),
                    body=LocalizedText(en=long_body, zh=long_body),
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]
    body_match = re.search(
        r'<span data-lang="en">(?P<body>Long body.*?)</span>',
        section_html,
        re.S,
    )

    assert body_match is not None
    assert long_body not in section_html
    assert "Long body Long body" in section_html
    assert body_match.group("body").endswith("…")
    # +1 allows the trailing ellipsis appended when text is truncated.
    assert len(body_match.group("body")) <= EDITORIAL_BRIEF_BODY_EXCERPT_CHARS + 1
```

- [ ] **Step 8: Add duplicate-body omission test**

```python
def test_render_index_html_deduplicates_editorial_brief_bodies() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="One", zh="一"),
                    body=LocalizedText(en="Same body.", zh="相同正文。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Two", zh="二"),
                    body=LocalizedText(en=" Same body. ", zh=" 相同正文。 "),
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert section_html.count("Same body.") == 1
    assert "Two" not in section_html
```

- [ ] **Step 9: Add empty-item omission test**

```python
def test_render_index_html_omits_editorial_brief_with_empty_items() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="   ", zh=" "),
                    body=LocalizedText(en="   ", zh=" "),
                ),
            )
        ),
    )

    assert 'class="editorial-brief"' not in index_html
```

- [ ] **Step 10: Add CSS selector test**

```python
def test_row_one_css_includes_editorial_brief_styles(tmp_path) -> None:
    index_path = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (index_path.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".editorial-brief",
        ".editorial-brief-header",
        ".editorial-brief-grid",
        ".editorial-brief-card",
        ".editorial-brief-link",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)

    assert "@media (max-width: 760px)" in css_text
    mobile_css = css_text[css_text.index("@media (max-width: 760px)") :]
    assert re.search(
        r"\.editorial-brief-grid\s*\{[^}]*grid-template-columns:\s*1fr",
        mobile_css,
        re.DOTALL,
    )
```

- [ ] **Step 11: Run tests and confirm failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_editorial_brief_from_local_articles \
  tests/test_row_one_render.py::test_render_index_html_omits_editorial_brief_without_usable_content \
  tests/test_row_one_render.py::test_render_index_html_escapes_editorial_brief_and_filters_links \
  tests/test_row_one_render.py::test_render_row_one_site_editorial_brief_falls_back_to_story_text \
  tests/test_row_one_render.py::test_render_index_html_accepts_editorial_brief_content_section_href \
  tests/test_row_one_render.py::test_render_index_html_caps_editorial_brief_to_three_items \
  tests/test_row_one_render.py::test_render_index_html_caps_editorial_brief_body_length \
  tests/test_row_one_render.py::test_render_index_html_deduplicates_editorial_brief_bodies \
  tests/test_row_one_render.py::test_render_index_html_omits_editorial_brief_with_empty_items \
  tests/test_row_one_render.py::test_row_one_css_includes_editorial_brief_styles -q
```

Expected: fail before implementation because `editorial_brief` is not accepted/rendered and CSS selectors do not exist.

## Task 2: Implement Generated-Site-Only Editorial Brief

- [ ] **Step 1: Add typed editorial brief classes and parameter**

In `templates.py`, add the private dataclasses near other generated-site-only render data declarations:

```python
EDITORIAL_BRIEF_MAX_ITEMS = 3
EDITORIAL_BRIEF_BODY_EXCERPT_CHARS = 220


@dataclass(frozen=True)
class _EditorialBriefItem:
    title: LocalizedText
    body: LocalizedText
    meta: LocalizedText | None = None
    href: str | None = None


@dataclass(frozen=True)
class _EditorialBrief:
    items: tuple[_EditorialBriefItem, ...]
```

In `render_index_html()` add:

```python
    editorial_brief: _EditorialBrief | None = None,
```

Then compute:

```python
    editorial_brief_section = _render_editorial_brief(editorial_brief)
```

Insert `{editorial_brief_section}` after `{saved_article_content_organization_section}` and before `{lead_story_block}`.

- [ ] **Step 2: Build brief in `render_row_one_site()`**

In `src/fashion_radar/row_one/render.py`, import the dataclasses from `templates.py` in the existing template import list:

```python
    EDITORIAL_BRIEF_MAX_ITEMS,
    _EditorialBrief,
    _EditorialBriefItem,
```

Do not import `render.py` from `templates.py`.

After saved article organization is built, add:

```python
    editorial_brief = _editorial_brief_payload(edition, local_articles_by_story_id)
```

Pass it to `render_index_html(editorial_brief=editorial_brief)`.

Add private builder helpers in `render.py`:

```python
def _editorial_brief_payload(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> _EditorialBrief | None:
    lead_story = _lead_story_for_editorial_brief(edition)
    if lead_story is None:
        return None
    local_article = local_articles_by_story_id.get(lead_story.id)
    items = _editorial_brief_items(lead_story, local_article)
    return _EditorialBrief(items=tuple(items[:EDITORIAL_BRIEF_MAX_ITEMS])) if items else None
```

The payload should contain up to three `_EditorialBriefItem` objects and should return `None` if no usable items exist. Use this preference chain:

- `_lead_story_for_editorial_brief(edition)`: return the first story in `edition.stories` whose `editorial_takeaway` or `summary` has at least one non-empty localized string after cleanup. If none exists, return `None`. Do not select by entity refs, heat, section, or source.
- `What changed today / 今日变化`: lead story `editorial_takeaway`; else lead story `summary`; append the local article brief section with key `what_happened` to the body when it exists and is not a duplicate; append concise saved article source/title context in `meta` when a local article exists. Apply the `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS` cap to the final combined localized body, not to each component before joining, and append `…` when truncation occurs.
- `Why it matters / 为什么重要`: lead story `why_it_matters`; else lead story `signal_context`; else local article brief section with key `why_it_matters`.
- `What to read locally / 本地阅读路径`: local article brief section with key `watch_next`; else lead story `reader_path`; link to `details/<story>.html#local-article-paragraph-1` when saved paragraphs exist, otherwise the detail page. Do not look up `reader_path` in `local_article.brief_sections`; `reader_path` is a `RowOneStory` field, not a valid `RowOneLocalArticleBriefKey`.

For local article brief section lookup, iterate `local_article.brief_sections` and choose the first section whose `key` matches the requested key. Skip empty or duplicate bodies; empty means both localized body strings are blank or whitespace-only after cleanup. Treat bodies as duplicates when `clean_row_one_text(a) == clean_row_one_text(b)` after cleanup. Cap each final localized body string to `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS` after cleanup and after combining any components; append `…` if the cleaned final text is longer than the cap. Determine saved paragraph availability with `bool(local_article.paragraphs)`. The workflow fixture in `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` already creates two matched The Row items, which the real ROW ONE edition builder routes through `_story_from_entity()` and `_entity_synthesis()` to produce a non-empty story `editorial_takeaway`; it also creates a local article extractor and the existing `generated_contract_payload` string built from `edition_payload`, `manifest_payload`, and `runtime_payload`. Implementation should add a workflow precondition assertion that at least one generated story has non-empty `editorial_takeaway.en` or `summary.en`, then assert the full pipeline renders the section and add only the new `'"editorial_brief"'` absence assertion to the existing `generated_contract_payload`. The `'"daily_information_layer"'` absence assertion is already present in this workflow test and should be confirmed, not duplicated.

- [ ] **Step 3: Add render helpers**

In `templates.py`, add private helpers near the Daily Edit / saved article helpers:

```python
def _render_editorial_brief(editorial_brief: _EditorialBrief | None) -> str:
    ...

def _render_editorial_brief_card(item: _EditorialBriefItem) -> str:
    ...

def _safe_editorial_brief_href(href: object) -> str | None:
    ...
```

`_render_editorial_brief` should filter to the first `EDITORIAL_BRIEF_MAX_ITEMS` renderable cards, skip items where both `body.en` and `body.zh` are blank or whitespace-only after cleanup, deduplicate cards whose cleaned localized body strings match exactly, cap final localized body strings to `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS`, and omit the section entirely if no items remain after filtering. The cap is intentionally enforced both in the builder and renderer: the builder keeps generated payloads small, while the renderer defends direct `render_index_html()` callers and tests that inject `_EditorialBrief` objects.

`_safe_editorial_brief_href` should allow validated detail routes and validated local article paragraph/content-section fragments, and reject everything else.

Use existing route helpers where possible:

```python
def _safe_editorial_brief_href(href: object) -> str | None:
    text = str(href or "").strip()
    if not text:
        return None
    base, separator, fragment = text.partition("#")
    safe_base = validated_row_one_detail_relative_path(base)
    if safe_base is None:
        return None
    if not separator:
        return str(safe_base)
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) or (
        _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment)
    ):
        return f"{safe_base}#{fragment}"
    return None
```

- [ ] **Step 4: Add CSS**

Add `.editorial-brief`, `.editorial-brief-header`, `.editorial-brief-grid`, `.editorial-brief-card`, `.editorial-brief-link` styles following existing section patterns. Add mobile rule:

```css
  .editorial-brief-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 5: Run render tests**

Run the Task 1 command. Expected: all pass.

## Task 3: Workflow And Docs Boundaries

- [ ] **Step 1: Extend workflow test**

In `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`, assert:

```python
assert any(
    story.get("editorial_takeaway", {}).get("en") or story.get("summary", {}).get("en")
    for story in edition_payload["stories"]
)
assert 'class="editorial-brief"' in index_html
assert "Editorial Brief" in index_html
assert "编辑正文" in index_html
assert '"editorial_brief"' not in generated_contract_payload
# Confirm the existing assertion remains present:
# assert '"daily_information_layer"' not in generated_contract_payload
```

- [ ] **Step 2: Add docs paragraphs**

Add this paragraph after Stage 320 and before Stage 310 in both README and `docs/row-one.md`. Both files currently contain `"Stage 310 adds"`, so use that as the Stage 321 slice endpoint:

```markdown
Stage 321 adds homepage Editorial Brief to generated ROW ONE index pages. It is
generated-site only and turns existing story summaries, existing story signal
context, existing saved local article brief sections, existing
`data/articles/<story-id>.json` sidecars, and existing paragraph anchors into a
short bilingual Editorial Brief / 编辑正文 section with safe internal detail and
paragraph links. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not add `editorial_brief`, does not change
`row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not change
schemas, does not write a new json artifact, does not add source collection,
does not fetch article pages, does not add scoring, does not add llm calls, does
not add connectors, and is not a compliance review feature.
```

- [ ] **Step 3: Update Stage 320 docs slice**

After inserting the Stage 321 docs paragraph, update the existing Stage 320 docs test slice in `tests/test_row_one_docs.py` so Stage 320 stops at `"Stage 321 adds"` instead of `"Stage 310 adds"`. This update must happen in the same edit as the Stage 321 README/docs paragraph insertion.

- [ ] **Step 4: Add docs test**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_homepage_editorial_brief_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_321 = readme[
        readme.index("Stage 321 adds homepage Editorial Brief") : readme.index("Stage 310 adds")
    ]
    docs_stage_321 = docs[
        docs.index("Stage 321 adds homepage Editorial Brief") : docs.index("Stage 310 adds")
    ]
    readme_stage_321_normalized = _normalized(readme_stage_321)
    docs_stage_321_normalized = _normalized(docs_stage_321)

    expected_phrases = [
        "homepage editorial brief",
        "generated-site only",
        "existing story summaries",
        "existing story signal context",
        "existing saved local article brief sections",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing paragraph anchors",
        "editorial brief / 编辑正文",
        "safe internal detail and paragraph links",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not add `editorial_brief`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_321_normalized
        assert phrase in docs_stage_321_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_321_normalized
        assert phrase not in docs_stage_321_normalized
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py -q
```

Expected: pass.

## Task 4: Review And Verification

- [ ] **Step 1: Run formatting and static checks**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --fix src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-321-code-review-prompt.md`, then run:

```bash
claude --bare --effort max --permission-mode plan --no-session-persistence --print \
  "$(cat docs/reviews/claude-code-stage-321-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-321-code-review.md
```

Fix any Critical or Important findings and rerun focused verification.

- [ ] **Step 3: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git status --short --branch
```

- [ ] **Step 4: Commit and push**

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-321-code-review-prompt.md \
  docs/reviews/claude-code-stage-321-code-review.md \
  docs/reviews/claude-code-stage-321-plan-review-prompt.md \
  docs/reviews/claude-code-stage-321-plan-review.md \
  docs/superpowers/plans/2026-07-07-stage-321-row-one-editorial-brief-plan.md \
  docs/superpowers/specs/2026-07-07-stage-321-row-one-editorial-brief-design.md \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py
git commit -m "Stage 321: add row one homepage editorial brief"
git push origin main
```
