# Stage 345 Saved Article Daily Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Saved Article Daily Summary orientation section to `articles/index.html`.

**Architecture:** Implement the summary as private render helpers inside `src/fashion_radar/row_one/templates.py`, deriving factual counts and quick links from existing saved article library, theme digest, reference atlas, signal index, reading paths, evidence board, and content organization objects. Add focused render tests, workflow contract guards, and docs boundary text without changing models, schemas, JSON artifacts, source collection, extraction, ranking, scheduling, deployment, or recommendation behavior.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add CSS selectors for the daily summary.
  - Add small private helpers for summary metrics, section-anchor links, first safe reading link, and summary rendering.
  - Insert the summary after the saved article library hero and before the theme digest.
- Modify `tests/test_row_one_render.py`
  - Add focused tests for summary placement, available links, safe omission, escaping, CSS selectors, and contract absence.
- Modify `tests/test_workflows.py`
  - Add generated contract negative assertions and artifact absence checks.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 345 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 345 boundary paragraph.
- Add `docs/reviews/claude-code-stage-345-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-345-plan-review-prompt.md`

## Task 1: Write Render Tests First

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add a failing test for daily summary placement and quick links**

Add a render-row-one-site test near the existing saved article library module tests:

```python
def test_render_row_one_site_includes_saved_article_daily_summary_in_article_library(
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
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_daily_summary_section_html(library_html)
    detail_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")

    assert 'class="saved-article-daily-summary"' in section_html
    assert "Saved Article Daily Summary" in section_html
    assert "保存文章每日导览" in section_html
    assert "saved local article" in section_html
    assert "source" in section_html
    assert 'href="#saved-article-theme-digest"' in section_html
    assert 'href="#saved-article-reference-atlas"' in section_html
    assert 'href="#saved-article-library-grid"' in section_html
    assert f'href="{story.id}.html#local-article-digest"' in section_html
    assert 'id="local-article-digest"' in detail_html
    assert (
        library_html.index('class="saved-article-library-hero"')
        < library_html.index('class="saved-article-daily-summary"')
        < library_html.index('class="saved-article-theme-digest"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-daily-summary"' not in homepage_html

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_daily_summary" not in contract_json
        assert "daily_saved_article_summary" not in contract_json
        assert "saved-article-daily-summary" not in contract_json
        assert "Saved Article Daily Summary" not in contract_json
        assert "保存文章每日导览" not in contract_json
    assert not (tmp_path / "data" / "saved-article-daily-summary.json").exists()
```

- [ ] **Step 2: Add a helper to slice the summary section**

Place this near the other `_saved_article_*_section_html` helpers:

```python
def _saved_article_daily_summary_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-daily-summary"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid">')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]
```

- [ ] **Step 3: Run the test and confirm it fails**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_daily_summary_in_article_library -q
```

Expected: fail because the summary class does not exist yet.

- [ ] **Step 4: Add a failing direct renderer test for unsafe empty summary omission**

Add:

```python
def test_render_saved_article_library_html_omits_daily_summary_without_targets() -> None:
    html = render_saved_article_library_html(
        _edition(),
        RowOneSavedArticleLibrary(
            article_count=0,
            source_count=0,
            reference_count=0,
            paragraph_count=0,
            body_count=0,
            groups=[],
        ),
    )

    assert 'class="saved-article-daily-summary"' not in html
```

- [ ] **Step 5: Add a failing CSS selector test**

Extend the existing CSS selector test with:

```python
for selector in (
    ".saved-article-daily-summary",
    ".saved-article-daily-summary-header",
    ".saved-article-daily-summary-metrics",
    ".saved-article-daily-summary-links",
    ".saved-article-daily-summary-link",
):
    assert selector in css
```

## Task 2: Implement Daily Summary Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add anchors to existing library sections**

Add stable IDs only to generated `articles/index.html` sections:

```python
<section class="saved-article-theme-digest"
  id="saved-article-theme-digest"
  aria-label="Saved article theme digest">
```

Apply equivalent IDs for available sections:

- `saved-article-reference-atlas`
- `saved-signal-index`
- `saved-article-reading-paths`
- `saved-article-evidence-board`
- `saved-article-content-organization`

Change the library grid wrapper to keep its existing class-first exact string
for current slicing helpers while adding the stable anchor with a wrapping
attribute order that tests can search explicitly:

```python
<div class="saved-article-library-grid" id="saved-article-library-grid">{groups}</div>
```

- [ ] **Step 2: Add CSS selectors**

Near the existing saved article library CSS, add concise styles for:

```css
.saved-article-daily-summary
.saved-article-daily-summary-header
.saved-article-daily-summary-header h2
.saved-article-daily-summary-header p
.saved-article-daily-summary-metrics
.saved-article-daily-summary-metrics li
.saved-article-daily-summary-links
.saved-article-daily-summary-link
```

Use existing ROW ONE spacing, borders, and palette. Do not introduce a new visual system.

- [ ] **Step 3: Add private summary helpers**

Add helpers near `_render_saved_article_library_source()`:

```python
def _render_saved_article_daily_summary(
    library: RowOneSavedArticleLibrary,
    *,
    signal_index_html: str,
    content_organization_html: str,
    reading_paths_html: str,
    theme_digest_html: str,
    reference_atlas_html: str,
    evidence_board_html: str,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    article_count = sum(len(group.entries) for group in library.groups)
    source_count = len([group for group in library.groups if group.entries])
    links = []
    if theme_digest_html:
        links.append(_render_saved_article_daily_summary_link("#saved-article-theme-digest", "Theme Digest", "主题简报"))
    if reference_atlas_html:
        links.append(_render_saved_article_daily_summary_link("#saved-article-reference-atlas", "Reference Atlas", "引用图谱"))
    if signal_index_html:
        links.append(_render_saved_article_daily_summary_link("#saved-signal-index", "Signal Index", "信号索引"))
    if reading_paths_html:
        links.append(_render_saved_article_daily_summary_link("#saved-article-reading-paths", "Reading Paths", "阅读路径"))
    if evidence_board_html:
        links.append(_render_saved_article_daily_summary_link("#saved-article-evidence-board", "Evidence Board", "证据板"))
    if content_organization_html:
        links.append(_render_saved_article_daily_summary_link("#saved-article-content-organization", "Content Organization", "内容整理"))
    if article_count:
        links.append(_render_saved_article_daily_summary_link("#saved-article-library-grid", "Source Grid", "来源网格"))
    reading_href = _first_saved_article_daily_summary_reading_href(
        library,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    if reading_href is not None:
        links.append(_render_saved_article_daily_summary_link(reading_href, "Start Reading", "开始阅读"))
    links = [link for link in links if link]
    if not links or not article_count:
        return ""
    surface_count = max(len(links) - (1 if reading_href is not None else 0), 0)
    return ...
```

Keep the implementation compact and escape all labels. If an existing dataclass uses a different field name, adapt to the actual type definitions before writing code.

Important: the summary must receive already-rendered section HTML from
`render_saved_article_library_html()`, not raw dataclass availability. Existing
section renderers can filter all child cards and return an empty string, so raw
objects can otherwise create dead anchor links.

- [ ] **Step 4: Add safe first-reading-link helper**

Implement:

```python
def _first_saved_article_daily_summary_reading_href(
    library: RowOneSavedArticleLibrary,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    for group in library.groups:
        for entry in group.entries:
            article_page_href = _saved_article_library_entry_article_page_href(
                entry,
                local_article_page_hrefs_by_detail_path,
            )
            if article_page_href is not None:
                return f"{article_page_href}#local-article-digest"
            digest_href = safe_row_one_detail_fragment_href(
                entry.digest_path,
                "local-article-digest",
            )
            if digest_href is not None:
                return _saved_article_library_page_href(digest_href)
    return None
```

Use the actual existing helper names available in `templates.py`; do not extend
`_safe_daily_local_intelligence_href()`. Reuse
`_saved_article_library_entry_article_page_href()` for first-class local article
page routes and `safe_row_one_detail_fragment_href()` for the detail-page
fallback.

- [ ] **Step 5: Insert summary into `render_saved_article_library_html()`**

Create the summary before `theme_digest` and render it after the hero:

```python
theme_digest = _render_saved_article_theme_digest(saved_article_theme_digest, section_id="saved-article-theme-digest")
reference_atlas = _render_saved_article_reference_atlas(saved_article_reference_atlas, section_id="saved-article-reference-atlas")
signal_index = _render_saved_signal_index(saved_signal_index, section_id="saved-signal-index")
reading_paths = _render_saved_article_reading_paths(saved_article_reading_paths, section_id="saved-article-reading-paths")
evidence_board = _render_saved_article_evidence_board(saved_article_evidence_board, section_id="saved-article-evidence-board")
content_organization = _render_saved_article_content_organization(
    saved_article_content_organization,
    href_prefix="../",
    section_id="saved-article-content-organization",
)
daily_summary = _render_saved_article_daily_summary(...)
...
  {daily_summary}
  {theme_digest}
```

## Task 3: Add Workflow And Documentation Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add workflow negative assertions**

Extend the generated contract guard with these forbidden tokens:

```python
assert "saved_article_daily_summary" not in generated_contract_payload
assert "daily_saved_article_summary" not in generated_contract_payload
assert "saved-article-daily-summary" not in generated_contract_payload
assert "saved-article-daily-summary.json" not in generated_contract_payload
```

Extend forbidden artifact paths:

```python
output_dir / "saved-article-daily-summary.json",
output_dir / "articles" / "saved-article-daily-summary.json",
output_dir / "data" / "saved-article-daily-summary.json",
output_dir / "saved-article-daily-summary.html",
output_dir / "articles" / "saved-article-daily-summary.html",
output_dir / "data" / "saved-article-daily-summary.html",
```

- [ ] **Step 2: Add docs boundary paragraph**

Add this paragraph to both `README.md` and `docs/row-one.md`, immediately before Stage 344:

```markdown
Stage 345 adds a generated-site only Saved Article Daily Summary inside `articles/index.html`; it reuses existing saved article content organization groups, existing organization coverage rows, existing safe card detail-path anchors, existing card references, and existing paragraph indices to summarize the daily saved article library without changing app-facing contracts; it does not create `data/saved-article-daily-summary.json`, does not create `data/daily-saved-article-summary.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 3: Add docs test**

Add a `test_row_one_docs_describe_stage_345_saved_article_daily_summary_boundary()`
that mirrors the Stage 344 test, asserts the exact paragraph in both docs,
asserts Stage 345 appears before Stage 344, and checks the stage slice for stale
broadening phrases.

## Task 4: Review, Verify, Commit, And Push

**Files:**
- Add `docs/reviews/claude-code-stage-345-code-review-prompt.md`
- Add `docs/reviews/opencode-stage-345-code-review-prompt.md`
- Add clean review/status files if local review commands time out.

- [ ] **Step 1: Run focused tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_daily_summary_in_article_library \
  tests/test_row_one_render.py::test_render_saved_article_library_html_omits_daily_summary_without_targets \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_345_saved_article_daily_summary_boundary \
  -q
```

- [ ] **Step 2: Run broader verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

- [ ] **Step 3: Run staged secret scan**

```bash
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}'; then
  exit 1
else
  echo "No token-shaped secrets in staged diff"
fi
```

- [ ] **Step 4: Commit and push**

```bash
git commit -m "Stage 345: add saved article daily summary"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```
