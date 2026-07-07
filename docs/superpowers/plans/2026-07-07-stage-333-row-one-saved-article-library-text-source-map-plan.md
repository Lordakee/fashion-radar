# Stage 333 ROW ONE Saved Article Library Text-Source Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only text-source map to the ROW ONE saved article library so `articles/index.html` shows whether included saved article bodies are extracted article text, ROW ONE summary fallback, or skipped.

**Architecture:** Extend the existing `RowOneSavedArticleLibrary` dataclass view model with body-source counts and per-entry provenance, populate it from existing `RowOneLocalArticle.body_source`, then render compact metrics and per-card chips in existing static HTML. Keep the feature HTML-only; do not change sidecar schemas, `data/edition.json`, manifest/runtime contracts, collection, extraction, ranking, LLM, connectors, scheduling, or compliance-review behavior.

**Tech Stack:** Python 3.13, existing ROW ONE dataclass view models, existing static HTML renderer, pytest, Ruff, Claude Code review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Modify: `src/fashion_radar/row_one/saved_article_library.py`
  - Add `body_source` to `RowOneSavedArticleLibraryEntry`.
  - Add `extracted_article_count`, `summary_fallback_article_count`, and
    `skipped_article_count` to `RowOneSavedArticleLibrary`.
  - Populate per-entry and aggregate fields from existing
    `RowOneLocalArticle.body_source`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Render nonzero text-source metrics in `_render_saved_article_library_metrics()`.
  - Render one static text-source chip on each saved article library card.
- Modify: `tests/test_row_one_saved_article_library.py`
  - Add builder coverage for body-source propagation and counts.
- Modify: `tests/test_row_one_render.py`
  - Update test fixtures and add render coverage for article-library metrics and
    card chips.
- Modify: `tests/test_row_one_docs.py`
  - Add Stage 333 docs sentinel.
- Modify: `README.md`
  - Document Stage 333 generated-site-only boundary.
- Modify: `docs/row-one.md`
  - Document Stage 333 generated-site-only boundary.
- Create review artifacts under `docs/reviews/`.

## Task 1: Builder Model And Count Tests

**Files:**
- Modify: `tests/test_row_one_saved_article_library.py`
- Modify: `src/fashion_radar/row_one/saved_article_library.py`

- [ ] **Step 1: Add failing helper support and builder test**

Update `_article()` in `tests/test_row_one_saved_article_library.py`:

```python
def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
    body_source: str = "extracted",
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh or [],
        content_sections=content_sections or [],
        body_source=body_source,
    )
```

Add:

```python
def test_saved_article_library_tracks_body_source_counts_for_included_articles() -> None:
    extracted_story = _story("extracted-1234567890", "Extracted story")
    fallback_story = _story("fallback-1234567890", "Fallback story")
    skipped_story = _story("skipped-1234567890", "Skipped story")
    empty_skipped_story = _story("empty-skipped-1234567890", "Empty skipped story")

    library = build_row_one_saved_article_library(
        _edition(extracted_story, fallback_story, skipped_story, empty_skipped_story),
        {
            extracted_story.id: _article(extracted_story.id, body_source="extracted"),
            fallback_story.id: _article(
                fallback_story.id,
                body_source="summary_fallback",
            ),
            skipped_story.id: _article(
                skipped_story.id,
                body_source="skipped",
                paragraphs=["Diagnostic paragraph."],
            ),
            empty_skipped_story.id: _article(
                empty_skipped_story.id,
                body_source="skipped",
                paragraphs=["   "],
            ),
        },
    )

    assert library is not None
    assert library.article_count == 3
    assert library.extracted_article_count == 1
    assert library.summary_fallback_article_count == 1
    assert library.skipped_article_count == 1
    assert [entry.body_source for entry in library.groups[0].entries] == [
        "extracted",
        "summary_fallback",
        "skipped",
    ]
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py::test_saved_article_library_tracks_body_source_counts_for_included_articles -q
```

Expected: FAIL because library entries/counts do not expose body source yet.

- [ ] **Step 2: Implement saved article library fields**

In `src/fashion_radar/row_one/saved_article_library.py`, import the body-source
alias:

```python
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleBodySource,
    RowOneReference,
)
```

Add to `RowOneSavedArticleLibraryEntry`:

```python
    body_source: RowOneLocalArticleBodySource
```

This required dataclass field will intentionally create transient failures in
direct render-test fixtures such as `_saved_article_library_fixture()` until
Task 2 Step 1 adds the matching fixture values. Do not investigate those
intermediate `TypeError` failures as unrelated regressions; complete Task 2 Step
1 before running broad render tests.

Add to `RowOneSavedArticleLibrary`:

```python
    extracted_article_count: int
    summary_fallback_article_count: int
    skipped_article_count: int
```

When constructing each entry:

```python
            body_source=article.body_source,
```

When returning the library:

```python
        extracted_article_count=sum(1 for entry in entries if entry.body_source == "extracted"),
        summary_fallback_article_count=sum(
            1 for entry in entries if entry.body_source == "summary_fallback"
        ),
        skipped_article_count=sum(1 for entry in entries if entry.body_source == "skipped"),
```

- [ ] **Step 3: Verify builder test passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py::test_saved_article_library_tracks_body_source_counts_for_included_articles -q
```

Expected: PASS.

## Task 2: Render Text-Source Metrics And Card Chips

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Update render fixture with body-source fields**

In `_saved_article_library_fixture()` in `tests/test_row_one_render.py`, add
`body_source="summary_fallback"` to the fixture entry and the matching aggregate
counts to `RowOneSavedArticleLibrary`:

```python
        body_source="summary_fallback",
```

```python
        extracted_article_count=0,
        summary_fallback_article_count=1,
        skipped_article_count=0,
```

Update any direct `RowOneSavedArticleLibrary` construction if required by the
new dataclass fields.

- [ ] **Step 2: Add failing render assertions**

  In `test_render_row_one_site_writes_saved_article_library_page()`, keep the
  local article's default `body_source="extracted"` (no constructor change) so
  the render test drives the extracted text-source chip and the homepage metric
  end-to-end. Add assertions:

  ```python
      assert "1 extracted text" in html
      assert "1 篇提取正文" in html
      assert '<span data-lang="en">Text source</span>' in html
      assert '<span data-lang="zh">正文来源</span>' in html
      assert "Extracted article text" in html
      assert "1 extracted text" in home_html
  ```

  In `test_render_saved_article_library_filters_content_organization_links_on_library_page()`,
  the fixture entry updated in Step 1 to `body_source="summary_fallback"`
  drives the summary-fallback chip and metric end-to-end. Add assertions:

  ```python
      assert "1 summary fallback" in html
      assert "1 篇摘要兜底" in html
      assert "ROW ONE summary fallback" in html
      assert 'href="ROW ONE summary fallback"' not in html
  ```

  Run:

  ```bash
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page -q
  ```

  Expected: FAIL until templates render text-source metrics and chips.

- [ ] **Step 3: Implement template labels and chips**

In `src/fashion_radar/row_one/templates.py`, add helpers near saved article
library render helpers:

```python
def _saved_article_library_body_source_label(body_source: str) -> str:
    if body_source == "summary_fallback":
        return "ROW ONE summary fallback"
    if body_source == "skipped":
        return "Skipped"
    return "Extracted article text"


def _render_saved_article_library_body_source_chip(
    entry: RowOneSavedArticleLibraryEntry,
) -> str:
    return (
        '<li class="saved-article-library-text-source">'
        '<span>'
        '<span data-lang="en">Text source</span>'
        '<span data-lang="zh">正文来源</span>'
        "</span>"
        f"<span>{_esc(_saved_article_library_body_source_label(entry.body_source))}</span>"
        "</li>"
    )
```

Append the chip inside `_render_saved_article_library_card()` count list after
organized section count:

```python
            {_render_saved_article_library_body_source_chip(entry)}
```

In `_render_saved_article_library_metrics()`, append nonzero metrics:

```python
    if library.extracted_article_count:
        metrics.append(
            _render_saved_article_library_metric(
                _count_label(
                    library.extracted_article_count,
                    "extracted text",
                    "extracted text",
                ),
                f"{library.extracted_article_count} 篇提取正文",
            )
        )
    if library.summary_fallback_article_count:
        metrics.append(
            _render_saved_article_library_metric(
                _count_label(
                    library.summary_fallback_article_count,
                    "summary fallback",
                    "summary fallback",
                ),
                f"{library.summary_fallback_article_count} 篇摘要兜底",
            )
        )
    if library.skipped_article_count:
        metrics.append(
            _render_saved_article_library_metric(
                _count_label(library.skipped_article_count, "skipped", "skipped"),
                f"{library.skipped_article_count} 篇跳过",
            )
        )
```

- [ ] **Step 4: Verify render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page -q
```

Expected: PASS.

## Task 3: Docs Boundary

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add failing docs sentinel**

Add near the Stage 332 docs test:

```python
def test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary() -> None:
    expected = _normalized(
        "Stage 333 adds a generated-site only saved article library text-source "
        "map inside `articles/index.html`; it reuses existing saved local article "
        "`body_source` values to show included-library counts and per-card text "
        "source chips for extracted article text, ROW ONE summary fallback, and "
        "skipped saved bodies; it does not expose fallback reasons, does not "
        "change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, "
        "JSON artifacts, source collection, fetching, matching, extraction, "
        "scoring, ranking, LLM, connector, scheduling, deployment, market "
        "grouping, domestic/international classification, or compliance-review "
        "behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Add docs paragraph**

Add this exact paragraph to `README.md` and `docs/row-one.md` before Stage 332:

```markdown
Stage 333 adds a generated-site only saved article library text-source map inside `articles/index.html`; it reuses existing saved local article `body_source` values to show included-library counts and per-card text source chips for extracted article text, ROW ONE summary fallback, and skipped saved bodies; it does not expose fallback reasons, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 3: Verify docs test passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary -q
```

Expected: PASS.

## Task 4: Focused Verification, Review, And Full Node Close

**Files:**
- Create: `docs/reviews/claude-code-stage-333-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-333-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py::test_saved_article_library_tracks_body_source_counts_for_included_articles tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page tests/test_row_one_docs.py::test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py tests/test_row_one_render.py -q -k "saved_article_library or body_source"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: all commands exit 0.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-333-code-review-prompt.md` and run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-333-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-333-code-review.md
rm -f "$tmp_review"
```

Expected: review output is captured in the markdown file. Fix Critical and
Important findings before proceeding.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv venv "$tmp_env/venv"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
git diff --cached --check
```

Expected: all commands exit 0. `tmp_build` and `tmp_env` are temporary paths and
must not be committed. The mirror is used only for local temporary venv
installation, not lockfile generation.

- [ ] **Step 4: Secret scan, commit, push**

Run staged secret scan before committing:

```bash
secret_pattern='gh''p_|s''k-[A-Za-z0-9]{16,}|api[_-]?ke''y|to''ken|Authori''zation:|Bear''er '
git diff --cached -- README.md docs/row-one.md docs/reviews docs/superpowers src tests | rg --case-sensitive -n "$secret_pattern" && exit 1 || true
```

Commit and push:

```bash
git add README.md docs/row-one.md docs/reviews docs/superpowers src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
git commit -m "Stage 333: add row one saved article text source map"
GIT_TERMINAL_PROMPT=0 git -c http.version=HTTP/1.1 push origin main
```

Expected: push succeeds and `git status --short --branch` shows
`main...origin/main` with no uncommitted changes.
