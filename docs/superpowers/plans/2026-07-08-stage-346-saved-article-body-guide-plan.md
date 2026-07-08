# Stage 346 Saved Article Body Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only body-guide layer to saved article cards in `articles/index.html`.

**Architecture:** Reuse the existing per-card organized-snippet view model in `src/fashion_radar/row_one/templates.py`, reshape that slot into a `saved-article-body-guide`, and render up to two concise, escaped guide bullets inside each saved article card. Keep the feature HTML-only and contract-neutral: no model, schema, JSON artifact, source collection, extraction, LLM, ranking, scheduling, deployment, or compliance-review changes.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Reduce the per-card content-organization cap from three items to two items
    for the body-guide surface.
  - Reuse the existing `RowOneSavedArticleContentOrganizationCard` lookup by
    detail path.
  - Render the existing organized-snippet slot as a `saved-article-body-guide`
    block inside each saved article card.
  - Reuse existing href validation, detail-path keying, paragraph evidence href,
    and excerpt helpers.
  - Add CSS selectors for the guide block.
- Modify `tests/test_row_one_render.py`
  - Add focused render tests for guide text, placement, caps, dedupe, escaping,
    unsafe href filtering, empty omission, CSS selectors, and JSON contract
    absence, while updating existing snippet tests to assert the body-guide
    surface instead of a duplicate snippet surface.
- Modify `tests/test_workflows.py`
  - Add generated contract negative assertions and artifact absence checks.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 346 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 346 boundary paragraph.
- Add `docs/reviews/claude-code-stage-346-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-346-plan-review-prompt.md`

## Task 1: Write Render Tests First

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add a failing site-render test for body-guide text**

Add near the saved article library tests:

```python
def test_render_row_one_site_includes_saved_article_body_guide_in_article_cards(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    card_html = _saved_article_library_first_card_html(library_html)
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert 'class="saved-article-body-guide"' in card_html
    assert "What this article says" in card_html
    assert "正文导读" in card_html
    assert "Start with The Row retail signal." in card_html
    assert "先看 The Row 零售信号。" in card_html
    assert "People &amp; Brands" in card_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"'
        in card_html
    )
    assert card_html.index('class="saved-article-body-guide"') < card_html.index(
        'class="saved-article-library-refs"'
    )
    assert 'class="saved-article-body-guide"' not in (
        tmp_path / "index.html"
    ).read_text(encoding="utf-8")

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_body_guide" not in contract_json
        assert "saved-article-body-guide" not in contract_json
        assert "What this article says" not in contract_json
        assert "正文导读" not in contract_json
    assert not (tmp_path / "data" / "saved-article-body-guide.json").exists()
```

- [ ] **Step 2: Add a helper to slice the first saved article card**

Place near existing saved article section slicing helpers:

```python
def _saved_article_library_first_card_html(index_html: str) -> str:
    marker = '<article class="saved-article-library-card">'
    assert marker in index_html
    card_start = index_html.index(marker)
    next_card = index_html.find(marker, card_start + len(marker))
    source_boundary = index_html.find("</section>", card_start)
    card_end = next_card if next_card >= 0 else source_boundary
    assert card_end > card_start
    return index_html[card_start:card_end]
```

- [ ] **Step 3: Run the new test and confirm it fails**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_body_guide_in_article_cards -q
```

Expected: fail because the existing organized snippet slot still renders
`saved-article-library-snippets`.

- [ ] **Step 4: Add a direct-renderer test for escaping, caps, and dedupe**

Add:

```python
def test_render_saved_article_library_body_guide_escapes_dedupes_and_caps() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row source", zh="The Row 来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People <Brands>", zh="品牌 <人物>"),
        lead=LocalizedText(
            en="Long <script>body</script> " + ("detail " * 80),
            zh="很长 <script>正文</script> " + ("细节 " * 80),
        ),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    base_card,
                    replace(base_card),
                    replace(
                        base_card,
                        section_label=LocalizedText(en="Products", zh="单品"),
                        lead=LocalizedText(en="Second body guide.", zh="第二条正文导读。"),
                        paragraph_indices=(1,),
                    ),
                    replace(
                        base_card,
                        section_label=LocalizedText(en="Overflow", zh="溢出"),
                        lead=LocalizedText(en="Third body guide.", zh="第三条正文导读。"),
                        paragraph_indices=(2,),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    guide_html = _saved_article_body_guide_html(html)

    assert 'class="saved-article-body-guide"' in guide_html
    assert guide_html.count('class="saved-article-body-guide-item"') == 2
    assert "People &lt;Brands&gt;" in guide_html
    assert "Long &lt;script&gt;body&lt;/script&gt;" in guide_html
    assert "<script>" not in guide_html
    assert guide_html.count("Long &lt;script&gt;body&lt;/script&gt;") == 1
    assert "Second body guide." in guide_html
    assert "Third body guide." not in guide_html
    assert guide_html.count("detail") < 80
```

- [ ] **Step 5: Add the guide HTML slicing helper**

```python
def _saved_article_body_guide_html(index_html: str) -> str:
    marker = '<div class="saved-article-body-guide"'
    assert marker in index_html
    start = index_html.index(marker)
    end = index_html.index("</div>", start) + len("</div>")
    return index_html[start:end]
```

- [ ] **Step 6: Add a direct-renderer unsafe href omission test**

Add:

```python
def test_render_saved_article_library_body_guide_filters_unsafe_hrefs() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe", zh="安全"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Safe guide", zh="安全导读"),
        lead=LocalizedText(en="Safe body guide.", zh="安全正文导读。"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Script guide", zh="脚本导读"),
                        lead=LocalizedText(en="Script body guide.", zh="脚本正文导读。"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Traversal guide", zh="越界导读"),
                        lead=LocalizedText(en="Traversal body guide.", zh="越界正文导读。"),
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Boolean guide", zh="布尔导读"),
                        lead=LocalizedText(en="Boolean body guide.", zh="布尔正文导读。"),
                        paragraph_indices=(True,),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    guide_html = _saved_article_body_guide_html(html)

    assert "Safe body guide." in guide_html
    assert "Script body guide." not in guide_html
    assert "Traversal body guide." not in guide_html
    assert "Boolean body guide." not in guide_html
    assert "javascript:" not in guide_html
    assert "../secret.html" not in guide_html
    assert "#local-article-paragraph-True" not in guide_html
```

- [ ] **Step 7: Add an empty-shell omission test**

Add:

```python
def test_render_saved_article_library_html_omits_empty_body_guide_shell() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=None,
    )

    assert 'class="saved-article-body-guide"' not in html
    assert "What this article says" not in html
```

- [ ] **Step 8: Add a CSS selector test**

Extend the CSS selector tests with:

```python
def test_row_one_css_includes_saved_article_body_guide_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-body-guide",
        ".saved-article-body-guide-header",
        ".saved-article-body-guide-list",
        ".saved-article-body-guide-item",
        ".saved-article-body-guide-label",
        ".saved-article-body-guide-body",
        ".saved-article-body-guide-link",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)
```

## Task 2: Implement Body Guide Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Rename and cap the existing per-card snippet surface**

Replace the existing per-card cap:

```python
SAVED_ARTICLE_BODY_GUIDE_ITEMS_PER_CARD = 2
```

Use this constant where `_saved_article_library_snippets_by_detail_path()`
currently caps `SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD`.

- [ ] **Step 2: Keep the existing lookup path**

Keep `render_saved_article_library_html()` building the existing
`snippets_by_detail_path` lookup from `saved_article_content_organization`.
Do not add a second `body_guides_by_detail_path` lookup unless tests prove the
existing lookup cannot satisfy the behavior.

- [ ] **Step 3: Render existing snippet cards as a body guide**

Rename the existing render helpers in place or add wrapper aliases that keep the
same card input:

```python
def _render_saved_article_body_guide(
    cards: Sequence[RowOneSavedArticleContentOrganizationCard],
) -> str:
    rendered_items = [_render_saved_article_body_guide_item(card) for card in cards]
    rendered_items = [item for item in rendered_items if item]
    if not rendered_items:
        return ""
    return (
        '<div class="saved-article-body-guide" aria-label="Saved article body guide">'
        '<div class="saved-article-body-guide-header">'
        '<span data-lang="en">What this article says</span>'
        '<span data-lang="zh">正文导读</span>'
        "</div>"
        '<ul class="saved-article-body-guide-list">'
        + "".join(rendered_items)
        + "</ul></div>"
    )
```

Render the result in `_render_saved_article_library_card()` in the same slot
where snippets currently render:

```python
body_guide = _render_saved_article_body_guide(
    _saved_article_library_entry_snippets(entry, snippets_by_detail_path)
)
...
          {body_guide}
          {refs}
```

- [ ] **Step 4: Render guide items from existing cards**

Add:

```python
def _render_saved_article_body_guide_item(
    card: RowOneSavedArticleContentOrganizationCard,
) -> str:
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    evidence = _render_saved_article_content_organization_evidence(
        card,
        href_prefix="../",
    )
    evidence_block = (
        f'\n              <span class="saved-article-body-guide-evidence">{evidence}</span>'
        if evidence
        else ""
    )
    return f"""<li class="saved-article-body-guide-item">
                <p class="saved-article-body-guide-label">
                  <span data-lang="en">{_esc(card.section_label.en)}</span>
                  <span data-lang="zh">{_esc(card.section_label.zh)}</span>
                </p>
                <p class="saved-article-body-guide-body">
                  <span data-lang="en">{_esc(_local_article_digest_excerpt(card.lead.en))}</span>
                  <span data-lang="zh">{_esc(_local_article_digest_excerpt(card.lead.zh))}</span>
                </p>
                <a class="saved-article-body-guide-link" href="{_esc(href)}">
                  <span data-lang="en">Open organized section</span>
                  <span data-lang="zh">打开整理栏目</span>
                </a>{evidence_block}
              </li>"""
```

- [ ] **Step 5: Add CSS styles**

Add CSS near the saved article library card/snippet styles:

```css
.saved-article-body-guide {
  border: 1px solid rgba(18, 18, 18, 0.12);
  background: rgba(255, 255, 255, 0.62);
  padding: 1rem;
}

.saved-article-body-guide-header {
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.75rem;
}

.saved-article-body-guide-list {
  display: grid;
  gap: 0.75rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.saved-article-body-guide-item {
  display: grid;
  gap: 0.45rem;
}

.saved-article-body-guide-label,
.saved-article-body-guide-body {
  margin: 0;
}

.saved-article-body-guide-label {
  font-size: 0.72rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.saved-article-body-guide-body {
  color: var(--ink);
  line-height: 1.55;
}

.saved-article-body-guide-link {
  color: var(--ink);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.22em;
}
```

Adjust variable names only if the local CSS uses different design variables.

## Task 3: Add Contract Guards And Docs

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add workflow negative assertions**

Find the existing generated-site-only artifact/contract guard for saved article
features and add forbidden strings:

```python
"saved_article_body_guide",
"saved-article-body-guide",
"saved_article_body_guides",
"saved-article-body-guides",
"What this article says",
"正文导读",
```

Also assert this file does not exist when the workflow guard checks generated
data artifacts:

```python
assert not (output_dir / "data" / "saved-article-body-guide.json").exists()
```

- [ ] **Step 2: Add docs test guard**

Find the Stage 345 docs guard in `tests/test_row_one_docs.py` and add Stage 346
required docs text checks for:

```python
"Saved Article Body Guide"
"generated-site-only"
"no new JSON artifacts"
```

- [ ] **Step 3: Add README and row-one docs boundary text**

Add one short paragraph to both `README.md` and `docs/row-one.md`:

```markdown
Stage 346 adds a generated-site-only Saved Article Body Guide inside
`articles/index.html`: each saved article card can show up to two concise
body-guide bullets from existing saved local article content, with safe local
paragraph anchors. It does not add JSON artifacts, schemas, app contract keys,
fetching, extraction, LLM summaries, ranking, scheduling, deployment, or
compliance-review product behavior.
```

## Task 4: Verify, Review, Commit, Push

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run focused red/green tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py -q -k "body_guide or saved_article_library"
```

Expected: pass after implementation.

- [ ] **Step 2: Run related docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py tests/test_row_one_docs.py -q
```

Expected: pass.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

Expected: all pass.

- [ ] **Step 4: Run staged secret scan before commit**

Run the repo's staged secret scan command used by prior stages. If no
single wrapper exists, run the existing release hygiene command after staging
and inspect staged diffs for credential-like strings.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add docs/superpowers/specs/2026-07-08-stage-346-saved-article-body-guide-design.md \
  docs/superpowers/plans/2026-07-08-stage-346-saved-article-body-guide-plan.md \
  docs/reviews/claude-code-stage-346-plan-review-prompt.md \
  docs/reviews/opencode-stage-346-plan-review-prompt.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/row-one.md
git commit -m "Stage 346: add saved article body guide"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: commit and push succeed.

## Self-Review Checklist

- The body guide is per-card, not a new top-level module.
- The feature is generated-site-only and does not touch app contracts or JSON
  artifacts.
- Guide text is escaped, capped, and deduped.
- Unsafe hrefs and invalid paragraph indices do not render.
- Empty guide shells do not render.
- Tests cover behavior, safety, docs, and workflow boundaries.
