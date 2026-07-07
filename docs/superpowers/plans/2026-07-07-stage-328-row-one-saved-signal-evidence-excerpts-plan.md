# Stage 328 ROW ONE Saved Signal Evidence Excerpts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add display-only local evidence excerpts to the existing ROW ONE Saved Signal Index inside `articles/index.html`.

**Architecture:** Extend the existing generated-site-only saved signal index builder with one optional `LocalizedText` excerpt per support row. Render the excerpt in the current `articles/index.html` Saved Signal Index template, using existing escaping and bilingual language toggles; keep app/runtime/manifest/schema/JSON contracts unchanged.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, existing static HTML/CSS template strings, pytest, Ruff, `UV_NO_CONFIG=1 uv --no-config run --frozen`, Claude Code/opencode review gates.

---

## Files

- Modify: `src/fashion_radar/row_one/saved_signal_index.py`
  - Append `excerpt: LocalizedText | None = None` to
    `RowOneSavedSignalIndexSupport`.
  - Add a private excerpt character limit constant.
  - Add private helpers to normalize/cap excerpt text, select item-body
    excerpts, and select paragraph-fallback excerpts.
  - Pass the computed excerpt when building each support row.
- Modify: `tests/test_row_one_saved_signal_index.py`
  - Add failing builder tests for item-body excerpts, paragraph fallback,
    Chinese alignment/fallback, invalid index filtering, and capping.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Render optional excerpts inside `_render_saved_signal_index_support_row()`.
  - Add CSS for `.saved-signal-index-support-excerpt`.
- Modify: `tests/test_row_one_render.py`
  - Add failing render tests for escaped excerpts, placement, link safety, CSS,
    and JSON contract stability.
- Modify: `README.md`
  - Add one Stage 328 generated-site-only boundary note near Stage 327.
- Modify: `docs/row-one.md`
  - Add the same Stage 328 boundary note with the same contract language.
- Modify: `tests/test_row_one_docs.py`
  - Add docs sentinel tests for Stage 328 wording and drift phrases.
- Modify: `tests/test_workflows.py`
  - Extend generated contract payload assertions to reject excerpt-specific JSON
    keys and sidecar/page artifacts.
- Create review artifacts:
  - `docs/reviews/claude-code-stage-328-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-328-plan-review.md` when Claude Code returns
    usable output
  - `docs/reviews/opencode-stage-328-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-328-plan-review.md` when opencode is used as
    revision reviewer or fallback
  - `docs/reviews/claude-code-stage-328-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-328-code-review.md` when Claude Code returns
    usable output
  - `docs/reviews/opencode-stage-328-code-review-prompt.md`
  - `docs/reviews/opencode-stage-328-code-review.md` when opencode is used as
    fallback

## Task 1: Builder Excerpt Selection

**Files:**
- Modify: `tests/test_row_one_saved_signal_index.py`
- Modify: `src/fashion_radar/row_one/saved_signal_index.py`

- [ ] **Step 1: Write failing builder tests**

Add these tests to `tests/test_row_one_saved_signal_index.py`.

```python
def test_saved_signal_index_support_uses_matching_item_body_excerpt() -> None:
    story = _story("the-row-excerpt-1234567890", "The Row signal")
    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Paragraph fallback should not win."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body="  The Row appears in the saved item body.  ",
                                body_zh="The Row 出现在本地整理正文中。",
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    support = index.entries[0].supports[0]
    assert support.excerpt is not None
    assert support.excerpt.en == "The Row appears in the saved item body."
    assert support.excerpt.zh == "The Row 出现在本地整理正文中。"
```

```python
def test_saved_signal_index_support_excerpt_uses_first_matching_item_body() -> None:
    story = _story("multi-item-excerpt-1234567890", "Multi item signal")

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Paragraph fallback should not win."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row first",
                                body="First matching body wins.",
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            ),
                            _item(
                                "The Row second",
                                body="Second matching body should not win.",
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            ),
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    support = index.entries[0].supports[0]
    assert support.excerpt is not None
    assert support.excerpt.en == "First matching body wins."
```

```python
def test_saved_signal_index_support_excerpt_falls_back_from_blank_body() -> None:
    story = _story("blank-body-excerpt-1234567890", "Blank body signal")

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Fallback paragraph wins."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body="   ",
                                body_zh="  ",
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    support = index.entries[0].supports[0]
    assert support.excerpt is not None
    assert support.excerpt.en == "Fallback paragraph wins."
    assert support.excerpt.zh == "Fallback paragraph wins."
```

```python
def test_saved_signal_index_support_falls_back_to_valid_saved_paragraph_excerpt() -> None:
    story = _story("paragraph-excerpt-1234567890", "Paragraph signal")
    item = _item(
        "The Row",
        references=[_signal_ref("The Row")],
    ).model_copy(update={"paragraph_indices": [True, -1, 1, "2", 0, 0, 99]})

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["First paragraph wins.", "   "],
                paragraphs_zh=["第一段胜出。"],
                content_sections=[
                    _section("entities", "People & Brands", items=[item])
                ],
            )
        },
    )

    assert index is not None
    support = index.entries[0].supports[0]
    assert support.excerpt is not None
    assert support.excerpt.en == "First paragraph wins."
    assert support.excerpt.zh == "第一段胜出。"
    assert [link.href for link in support.paragraph_links] == [
        "details/paragraph-excerpt-1234567890.html#local-article-paragraph-1"
    ]
```

```python
def test_saved_signal_index_support_excerpt_uses_english_when_zh_missing() -> None:
    story = _story("paragraph-zh-fallback-1234567890", "Fallback signal")

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["English paragraph only."],
                paragraphs_zh=[],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    support = index.entries[0].supports[0]
    assert support.excerpt is not None
    assert support.excerpt.en == "English paragraph only."
    assert support.excerpt.zh == "English paragraph only."
```

```python
def test_saved_signal_index_support_excerpt_is_capped() -> None:
    story = _story("long-excerpt-1234567890", "Long signal")
    long_body = " ".join(["The Row signal"] * 80)

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Fallback."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body=long_body,
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    support = index.entries[0].supports[0]
    assert support.excerpt is not None
    assert len(support.excerpt.en) <= 220
    assert support.excerpt.en.endswith("...")
```

```python
def test_saved_signal_index_support_excerpt_capping_edge_cases() -> None:
    story_exact = _story("exact-excerpt-1234567890", "Exact excerpt")
    story_long = _story("edge-long-excerpt-1234567890", "Long edge excerpt")

    exact_index = build_row_one_saved_signal_index(
        _edition(story_exact),
        {
            story_exact.id: _article(
                story_exact.id,
                paragraphs=["Fallback."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body="a" * 220,
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    )
                ],
            )
        },
    )
    long_index = build_row_one_saved_signal_index(
        _edition(story_long),
        {
            story_long.id: _article(
                story_long.id,
                paragraphs=["Fallback."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body="a" * 221,
                                paragraph_indices=[0],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert exact_index is not None
    assert long_index is not None
    exact_excerpt = exact_index.entries[0].supports[0].excerpt
    long_excerpt = long_index.entries[0].supports[0].excerpt
    assert exact_excerpt is not None
    assert long_excerpt is not None
    assert len(exact_excerpt.en) == 220
    assert not exact_excerpt.en.endswith("...")
    assert len(long_excerpt.en) == 220
    assert long_excerpt.en.endswith("...")
```

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py -q
```

Expected: fail because `RowOneSavedSignalIndexSupport` has no `excerpt`
attribute yet.

- [ ] **Step 3: Implement minimal builder support**

In `src/fashion_radar/row_one/saved_signal_index.py`:

```python
from fashion_radar.row_one.text import normalize_row_one_paragraph

SAVED_SIGNAL_INDEX_EXCERPT_CHARS = 220
```

Append the dataclass field:

```python
@dataclass(frozen=True)
class RowOneSavedSignalIndexSupport:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    content_section_title: LocalizedText
    section_path: str
    paragraph_links: tuple[RowOneSavedSignalIndexParagraphLink, ...] = ()
    excerpt: LocalizedText | None = None
```

Add private helpers:

```python
def _saved_signal_excerpt_text(value: str) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= SAVED_SIGNAL_INDEX_EXCERPT_CHARS:
        return normalized
    return normalized[: SAVED_SIGNAL_INDEX_EXCERPT_CHARS - 3].rstrip() + "..."


def _localized_excerpt(en: str, zh: str) -> LocalizedText | None:
    en_text = _saved_signal_excerpt_text(en)
    zh_text = _saved_signal_excerpt_text(zh)
    if not en_text and not zh_text:
        return None
    if not en_text:
        en_text = zh_text
    if not zh_text:
        zh_text = en_text
    return LocalizedText(en=en_text, zh=zh_text)


def _item_body_excerpt(
    items: Iterable[RowOneLocalArticleContentItem],
) -> LocalizedText | None:
    for item in items:
        if item.body is None:
            continue
        excerpt = _localized_excerpt(item.body.en, item.body.zh)
        if excerpt is not None:
            return excerpt
    return None


def _paragraph_excerpt(
    article: RowOneLocalArticle,
    paragraph_indices: Iterable[object],
) -> LocalizedText | None:
    for index in paragraph_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index < 0 or index >= len(article.paragraphs):
            continue
        en = article.paragraphs[index]
        zh = article.paragraphs_zh[index] if index < len(article.paragraphs_zh) else ""
        excerpt = _localized_excerpt(en, zh)
        if excerpt is not None:
            return excerpt
    return None


def _support_excerpt(
    article: RowOneLocalArticle,
    items: Iterable[RowOneLocalArticleContentItem],
    paragraph_indices: Iterable[object],
) -> LocalizedText | None:
    item_list = tuple(items)
    return _item_body_excerpt(item_list) or _paragraph_excerpt(article, paragraph_indices)
```

Pass the excerpt by keyword where the support row is created:

```python
excerpt=_support_excerpt(article, items, paragraph_indices),
```

- [ ] **Step 4: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py -q
```

Expected: all saved signal index tests pass.

## Task 2: Template Rendering And Contract Safety

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write failing render tests**

Add render coverage in `tests/test_row_one_render.py` that builds an edition
with one local article content item containing:

```python
body=LocalizedText(
    en='The Row <script>alert("x")</script> body points to Margaux.',
    zh='The Row <script>alert("x")</script> 中文正文。',
)
```

Assert the rendered `articles/index.html` contains:

```python
assert "saved-signal-index-support-excerpt" in articles_html
assert "The Row &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; body points to Margaux." in articles_html
assert "The Row <script>" not in articles_html
assert articles_html.index("saved-signal-index-support-meta") < articles_html.index(
    "saved-signal-index-support-excerpt"
) < articles_html.index("saved-signal-index-actions")
assert "../details/the-row-1234567890.html#local-article-content-section-1" in articles_html
assert "#local-article-paragraph-1" in articles_html
assert "../details/The Row" not in articles_html
assert "../details/<script>" not in articles_html
```

Add a CSS selector assertion:

```python
assert ".saved-signal-index-support-excerpt" in css
```

Add a focused direct-render case where a
`RowOneSavedSignalIndexSupport(..., excerpt=None)` support row renders no empty
excerpt paragraph:

```python
assert "saved-signal-index-support-excerpt" not in support_row_html
```

Extend the generated contract payload test in `tests/test_workflows.py`:

```python
assert '"saved_signal_excerpt"' not in generated_contract_payload
assert '"signal_excerpt"' not in generated_contract_payload
assert "saved-signal-excerpts.json" not in generated_contract_payload
assert not (output_dir / "data" / "saved-signal-excerpts.json").exists()
assert not (output_dir / "saved-signal-excerpt.html").exists()
assert not (output_dir / "articles" / "saved-signal-excerpt.html").exists()
```

When the workflow fixture generates a saved signal index, also assert the
generated page carries the display-only excerpt surface:

```python
articles_html_path = output_dir / "articles" / "index.html"
if articles_html_path.exists():
    articles_html = articles_html_path.read_text(encoding="utf-8")
    if "saved-signal-index-support-row" in articles_html:
        assert "saved-signal-index-support-excerpt" in articles_html
```

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py -q
```

Expected: fail because the excerpt class and excerpt text are not rendered yet.

- [ ] **Step 3: Implement template rendering**

In `src/fashion_radar/row_one/templates.py`, update
`_render_saved_signal_index_support_row()`:

```python
    excerpt = _render_saved_signal_support_excerpt(support.excerpt)
    return f"""<div class="saved-signal-index-support-row">
        ...
        <div class="saved-signal-index-support-meta">...</div>
        {excerpt}
        {actions}
        {paragraphs}
      </div>"""
```

Add:

```python
def _render_saved_signal_support_excerpt(excerpt: LocalizedText | None) -> str:
    if excerpt is None:
        return ""
    return f"""<p class="saved-signal-index-support-excerpt">
          <span data-lang="en">{_esc(excerpt.en)}</span>
          <span data-lang="zh">{_esc(excerpt.zh)}</span>
        </p>"""
```

Add this rule immediately after the existing `.saved-signal-index-support-meta`
rule:

```css
.saved-signal-index-support-excerpt {
  margin: 0;
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}
```

- [ ] **Step 4: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py -q
```

Expected: all selected render/workflow tests pass.

## Task 3: Documentation Sentinels

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Write failing docs tests**

Add constants:

```python
STAGE_328_PLAN_BOUNDARY_DOCS = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-plan.md",
    ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-design.md",
)
```

Add:

```python
def test_row_one_docs_describe_saved_signal_evidence_excerpts_boundary() -> None:
    expected = _normalized(
        "Stage 328 adds generated-site only evidence excerpts to the existing "
        "ROW ONE Saved Signal Index inside `articles/index.html`; it shows "
        "capped snippets from existing saved local article item bodies or saved "
        "paragraphs and links back into existing detail-page local article "
        "anchors; it does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, matching, extraction, scoring, ranking, LLM, connector, "
        "scheduling, deployment, market grouping, domestic/international "
        "classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_328_pos = normalized.index(
            "stage 328 adds generated-site only evidence excerpts"
        )
        stage_327_pos = normalized.index("stage 327 adds a generated-site only row one")
        assert stage_328_pos < stage_327_pos
        stage = normalized[stage_328_pos:stage_327_pos]
        for phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "saved_signal_excerpt",
            "signal_excerpt",
            "saved-signal-excerpts.json",
            "saved-signal-excerpt.html",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds market grouping",
            "adds domestic",
            "adds international",
            "adds compliance review",
        ):
            assert phrase not in stage

    for path in STAGE_328_PLAN_BOUNDARY_DOCS:
        normalized = _normalized(_read(path))
        for phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
        ):
            assert phrase not in normalized
```

- [ ] **Step 2: Run docs tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: fail because README and `docs/row-one.md` do not describe Stage 328
yet.

- [ ] **Step 3: Update docs**

Add this exact sentence near the Stage 327 note in both `README.md` and
`docs/row-one.md`:

```markdown
Stage 328 adds generated-site only evidence excerpts to the existing ROW ONE Saved Signal Index inside `articles/index.html`; it shows capped snippets from existing saved local article item bodies or saved paragraphs and links back into existing detail-page local article anchors; it does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 4: Run docs tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: docs tests pass.

## Task 4: Review, Verification, Commit, Push

**Files:**
- Create/modify Stage 328 review artifacts under `docs/reviews/`.
- Commit all Stage 328 changes.

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q
```

Expected: selected Stage 328 coverage passes.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
if git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'; then exit 1; else exit 0; fi
```

Expected: every command exits 0 and the secret scan reports no committed-source
matches.

- [ ] **Step 3: Request code review**

Create `docs/reviews/claude-code-stage-328-code-review-prompt.md` with:

```markdown
Review Stage 328 code changes in /home/ubuntu/fashion-radar.

Scope:
- Generated-site-only evidence excerpts for the existing ROW ONE Saved Signal Index.
- Existing `articles/index.html` only.
- No new page, JSON sidecar, app/runtime/manifest/schema contract, source collection, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, or compliance-review feature.

Please identify Critical, Important, Medium, and Minor issues. Focus on correctness, contract safety, escaping/link safety, TDD coverage, and whether the implementation satisfies docs/superpowers/plans/2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-plan.md.
Do not edit files.
```

Run primary review:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-328-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-328-code-review.md
rm -f "$tmp_review"
```

Before copying a review artifact, inspect the temporary output and make sure it
is one complete review body, not a live-capture stub, timeout note, duplicated
draft, or truncated review. If the review is incomplete, retry with a narrower
prompt or use the opencode fallback route.

If Claude Code is unavailable or times out, create
`docs/reviews/opencode-stage-328-code-review-prompt.md` with the same review
request and run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-328-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-328-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 4: Fix blocking review findings**

Fix all Critical and Important review findings, then rerun the focused and full
verification commands from Steps 1 and 2.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add README.md docs/row-one.md docs/superpowers/specs/2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-design.md docs/superpowers/plans/2026-07-07-stage-328-row-one-saved-signal-evidence-excerpts-plan.md docs/reviews src/fashion_radar/row_one/saved_signal_index.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
git commit -m "Stage 328: add row one saved signal evidence excerpts to index"
git push origin main
```

Expected: commit is created and pushed to `origin/main`.
