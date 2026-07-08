# Stage 341 ROW ONE Local Article Information Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated HTML-only local article information panel to first-class `articles/<story-id>.html` pages using existing ROW ONE story and saved local article data, without changing app-facing contracts or JSON artifacts.

**Architecture:** Keep the change in `src/fashion_radar/row_one/templates.py`. `render_local_article_page_html()` already has `edition`, `story`, `section_title`, and `local_article`, so it can render a local information panel before the existing `_render_local_article(local_article)` output. CSS stays in `row_one_css()`, and tests stay in `tests/test_row_one_render.py` plus existing docs/workflow guard files.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses/models, static HTML/CSS template rendering, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add constants for panel caps.
  - Add `_render_local_article_information_panel(...)`.
  - Add small helpers for bilingual panel body-source labels, section cards, strict paragraph links, and deduped reference chips.
  - Do not replace the existing string-returning `_local_article_body_source_label()` used by local article provenance.
  - Call the panel from `render_local_article_page_html()` before `{local_article_section}`.
  - Add CSS selectors for `.local-article-information*`.

- Modify `tests/test_row_one_render.py`
  - Add local article page panel tests.
  - Extend the existing first-class local article page contract-stability assertions.
  - Add CSS selector test.

- Modify `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, `tests/test_workflows.py`
  - Document Stage 341 and pin no-contract/no-artifact boundaries.

- Create/modify `docs/reviews/`
  - Add compact Stage 341 plan review prompt/result.
  - Add Stage 341 code review prompt/result after implementation.

---

### Task 1: Add failing render tests for the local article information panel

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add panel presence test**

Add near `test_render_row_one_site_writes_first_class_local_article_page`:

```python
def test_render_local_article_page_includes_information_panel() -> None:
    edition = _edition()
    story = edition.stories[0]

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'class="local-article-information"' in html
    assert 'id="local-article-information-title"' in html
    assert "Local Article Information" in html
    assert "本地文章信息" in html
    assert "Signal Source" in html
    assert "Extracted article" in html
    assert "2 paragraphs" in html
    assert "2 organized sections" in html
    assert html.index('class="local-article-information"') < html.index('id="local-article"')
```

- [ ] **Step 2: Add local-anchor test**

```python
def test_render_local_article_page_information_panel_uses_local_anchors() -> None:
    edition = _edition()
    story = edition.stories[0]
    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
    )
    panel = _html_between(html, '<section class="local-article-information"', "</section>")

    assert 'href="#local-article-reader"' in panel
    assert 'href="#local-article-digest"' in panel
    assert 'href="#local-article-paragraph-evidence"' in panel
    assert 'href="#local-article-content-section-1"' in panel
    assert 'href="#local-article-paragraph-1"' in panel
    assert "http://" not in panel
    assert "https://" not in panel
    assert "../details/" not in panel
```

Use an existing local helper if the file already has an HTML-section extraction helper; otherwise add a small test-local helper.
`tests/test_row_one_render.py` currently has `_signal_briefing_local_article()` but no `_html_between()` helper, so add a module-level test utility before the new panel tests:

```python
def _html_between(html: str, start: str, end: str) -> str:
    start_index = html.index(start)
    end_index = html.index(end, start_index)
    return html[start_index:end_index]
```

- [ ] **Step 3: Add escaping, dedupe, and cap test**

Create a `local_article` copy with:

- unsafe `source_name`, reference name/label, and content item text containing `<script>`.
- duplicate references across content items.
- more references than the cap.

Assert:

```python
assert "<script>" not in panel
assert "&lt;script&gt;" in panel
assert panel.count("The Row") == 1
assert panel.count('class="local-article-information-ref"') <= 6
```

- [ ] **Step 4: Add invalid paragraph-index filtering test**

Create a `local_article` copy whose first content item has `paragraph_indices=[0, 0, 99]`. Pydantic model construction coerces bool/string inputs before template rendering, so this render-level test covers duplicate and out-of-range filtering; the strict bool rejection branch is already covered by the existing helper-level paragraph evidence tests. Assert:

```python
assert 'href="#local-article-paragraph-1"' in panel
assert 'href="#local-article-paragraph-100"' not in panel
assert 'href="#local-article-paragraph-2"' not in panel
assert panel.count('href="#local-article-paragraph-1"') == 1
```

- [ ] **Step 5: Extend contract stability test**

In `test_render_row_one_site_writes_first_class_local_article_page`, add:

```python
assert "local-article-information" in article_html
for contract_json in (
    json.dumps(edition_payload, ensure_ascii=False),
    json.dumps(manifest_payload, ensure_ascii=False),
    json.dumps(runtime_payload, ensure_ascii=False),
):
    assert "local_article_information" not in contract_json
    assert "local-article-information" not in contract_json
    assert "local_article_reading_improvements" not in contract_json
assert not (tmp_path / "data" / "local-article-reading-improvements.json").exists()
```

- [ ] **Step 6: Add CSS selector test**

Add near existing `row_one_css()` tests:

```python
def test_row_one_css_includes_local_article_information_styles() -> None:
    css = row_one_css()
    for selector in (
        ".local-article-information",
        ".local-article-information-header",
        ".local-article-information-metrics",
        ".local-article-information-grid",
        ".local-article-information-card",
        ".local-article-information-refs",
        ".local-article-information-paragraphs",
    ):
        assert selector in css
```

- [ ] **Step 7: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_information or first_class_local_article_page"
```

Expected: new panel/CSS tests fail because the panel is not implemented yet.

---

### Task 2: Implement local article information panel

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add panel caps**

Near existing template constants, add:

```python
LOCAL_ARTICLE_INFORMATION_MAX_SECTIONS = 4
LOCAL_ARTICLE_INFORMATION_MAX_ITEMS_PER_SECTION = 2
LOCAL_ARTICLE_INFORMATION_MAX_REFS = 6
LOCAL_ARTICLE_INFORMATION_MAX_PARAGRAPH_LINKS = 5
LOCAL_ARTICLE_INFORMATION_BODY_MAX_CHARS = 120
```

- [ ] **Step 2: Call panel from `render_local_article_page_html()`**

After computing `detail_href`, add:

```python
    information_panel = _render_local_article_information_panel(
        edition,
        story,
        local_article,
        section_title,
    )
```

Then render `{information_panel}` before `{local_article_section}`.
The exact insertion point is inside `<div class="local-article-page-article">`, after:

```html
<p class="story-source">...</p>
```

and before:

```html
{local_article_section}
```

- [ ] **Step 3: Add localized body-source label helper**

```python
def _local_article_body_source_label_localized(article: RowOneLocalArticle) -> LocalizedText:
    if article.body_source == "summary_fallback":
        return LocalizedText(en="ROW ONE summary fallback", zh="ROW ONE 摘要补全文")
    if article.body_source == "skipped" or article.skipped:
        return LocalizedText(en="Skipped", zh="已跳过")
    return LocalizedText(en="Extracted article", zh="抽取正文")
```

Do not edit or replace the existing `_local_article_body_source_label(article) -> str`; it is used by `_render_local_article_provenance()`.

- [ ] **Step 4: Add strict local paragraph link helper**

Inside `_render_local_article_information_panel()`, call `_local_article_rendered_paragraph_indices(article)` to build `rendered_indices`. Pass that set into the existing `_strict_valid_local_article_paragraph_indices()` helper, and use `_local_article_paragraph_anchor(index)` to build only `href="#local-article-paragraph-N"` links.

- [ ] **Step 5: Add reference dedupe helper**

Dedupe references by normalized `(name, type, label)`, escape all display values, and cap at `LOCAL_ARTICLE_INFORMATION_MAX_REFS`.

- [ ] **Step 6: Add section-card helper**

Render up to `LOCAL_ARTICLE_INFORMATION_MAX_SECTIONS` content sections. For each section:

- link title to `#local-article-content-section-N`
- render up to two item title/body snippets
- render deduped reference chips
- render up to five valid paragraph links

- [ ] **Step 7: Add `_render_local_article_information_panel()`**

The panel should:

- return `""` if the article has no nonblank saved paragraphs.
- render bilingual text with `data-lang="en"` / `data-lang="zh"` where applicable.
- render source/body/paragraph/section metrics.
- render quick jumps to reader, digest, paragraph evidence, section cards, and paragraphs.
- avoid outbound links.

- [ ] **Step 8: Add CSS**

Add styles near existing local article page styles:

```css
.local-article-information { ... }
.local-article-information-header { ... }
.local-article-information-metrics { ... }
.local-article-information-grid { ... }
.local-article-information-card { ... }
.local-article-information-refs { ... }
.local-article-information-paragraphs { ... }
```

Mirror the existing ROW ONE visual language; do not create a card inside a card.

- [ ] **Step 9: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_information or first_class_local_article_page"
```

Expected: pass.

---

### Task 3: Document Stage 341 and pin generated-site-only boundaries

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add Stage 341 documentation paragraph**

Add this exact paragraph to both docs directly before Stage 340:

```text
Stage 341 adds generated-site only local article reading improvements for ROW ONE first-class local article pages; it reuses current-edition saved local article sidecars, existing local article rendering sections, existing saved article library routes, existing detail-page `#local-article-*` anchors, and existing `articles/<story-id>.html` pages to improve how readers scan already-saved local text without changing the app-facing contracts; it does not create `data/local-article-reading-improvements.json`, does not create new article-source sidecars, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs guard test**

Add `test_row_one_docs_describe_stage_341_local_article_reading_improvements_boundary()` before the Stage 340 docs test. Assert:

- exact paragraph appears in both docs.
- Stage 341 appears before Stage 340.
- Stage 341 slice excludes forbidden phrases from the design doc.

- [ ] **Step 3: Extend workflow guards**

In `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`, assert generated contract payloads do not contain:

```python
(
    "local_article_reading_improvements",
    "local_article_reader_improvements",
    "article_reading_improvements",
    "reading_improvements",
    "local-article-reading-improvements",
    "article-reading-improvements",
    "Local Article Reading Improvements",
    "local-article-reading-improvements.json",
)
```

Also assert absence of:

```python
output_dir / "local-article-reading-improvements.json"
output_dir / "articles" / "local-article-reading-improvements.json"
output_dir / "data" / "local-article-reading-improvements.json"
output_dir / "local-article-reading-improvements.html"
output_dir / "articles" / "local-article-reading-improvements.html"
output_dir / "data" / "local-article-reading-improvements.html"
```

- [ ] **Step 4: Run docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: pass.

---

### Task 4: Review and verification

**Files:**
- Create: `docs/reviews/claude-stage-341-code-review-prompt.md`
- Create: `docs/reviews/claude-stage-341-code-review.md`

- [ ] **Step 1: Run focused regression**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q
```

- [ ] **Step 2: Request Claude Code review**

Create a compact review prompt covering:

- information panel correctness
- local-anchor safety
- escaping/dedupe/caps
- contract/artifact stability
- no schema/render.py/model changes

Run:

```bash
claude --print --effort max --add-dir /home/ubuntu/fashion-radar < docs/reviews/claude-stage-341-code-review-prompt.md > docs/reviews/claude-stage-341-code-review.md
```

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
if git diff -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}'; then exit 1; else echo "No token-shaped secrets in current diff"; fi
```

- [ ] **Step 4: Commit and push**

Run:

```bash
git add README.md docs/row-one.md src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py docs/superpowers/specs/2026-07-08-stage-341-row-one-local-article-information-panel-design.md docs/superpowers/plans/2026-07-08-stage-341-row-one-local-article-information-panel-plan.md docs/reviews/claude-stage-341-plan-review-prompt.md docs/reviews/claude-stage-341-plan-review.md docs/reviews/claude-stage-341-code-review-prompt.md docs/reviews/claude-stage-341-code-review.md
git commit -m "Stage 341: add local article information panel"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

- [ ] **Step 5: Handoff Summary**

Report:

- repo status
- latest commit SHA
- pushed branch
- verified commands
- uncommitted files
- next recommended stage
