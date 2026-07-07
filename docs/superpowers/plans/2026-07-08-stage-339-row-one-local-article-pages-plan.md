# Stage 339 ROW ONE First-Class Local Article Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate first-class `articles/<story-id>.html` local article pages for current-edition saved local article bodies while preserving existing detail-page anchors and ROW ONE contract stability.

**Architecture:** Extend the existing ROW ONE static render layer. `_write_saved_article_library_page()` will continue writing `articles/index.html` and will also write one safe local article page per publishable current-edition `RowOneLocalArticle`. `templates.py` will add a `render_local_article_page_html()` entry point that reuses the existing local article rendering helpers.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses/models, static HTML/CSS templates, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/render.py`
  - Thread `local_articles_by_story_id` into `_write_saved_article_library_page()`.
  - Add safe writer logic for `articles/<story-id>.html`.
  - Compute a generated-page eligibility map once and pass it to both the library index template and the article-page writer.
  - Keep generated children and latest-only cleanup unchanged because `articles/` is already generated.

- Modify `src/fashion_radar/row_one/templates.py`
  - Add `render_local_article_page_html(edition, story, local_article)`.
  - Add allowlisted article-library link support on saved article library cards.
  - Add CSS selectors for the local article page shell.

- Modify `tests/test_row_one_render.py`
  - Add render tests for article-page generation, safe-route omission, allowlisted library links, contract stability, latest-only stale cleanup, unsafe detail-path `ValueError`, and CSS selectors.

- Modify `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, `tests/test_workflows.py`
  - Document Stage 339 and pin boundaries.

- Create/modify review artifacts under `docs/reviews/` only after implementation when requesting code review.

---

### Task 1: Add failing render tests for first-class local article pages

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add test for generated article page**

Add a test near existing saved article library tests:

```python
def test_render_row_one_site_writes_first_class_local_article_page(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    article_path = tmp_path / "articles" / f"{story.id}.html"
    assert article_path.exists()
    article_html = article_path.read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert 'class="local-article-page"' in article_html
    assert 'href="index.html"' in article_html
    assert 'href="../index.html"' in article_html
    assert 'href="../details/the-row-signal-1234567890.html"' in article_html
    assert 'id="local-article"' in article_html
    assert 'id="local-article-reader"' in article_html
    assert 'id="local-article-paragraph-1"' in article_html
    assert "Signal source article" in article_html
    assert "The Row Margaux bag appears in saved source text." in article_html
    assert f'href="{story.id}.html"' in library_html
    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "local_article_pages" not in contract_json
        assert "first_class_local_article" not in contract_json
        assert "local-article-page" not in contract_json
    assert not (tmp_path / "data" / "local-article-pages.json").exists()
```

- [ ] **Step 2: Add safe omission tests**

Add tests that assert no page is written when:

```python
def test_render_row_one_site_omits_local_article_page_for_mismatched_article_id(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={"story_id": "other-story-1234567890"},
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    assert not (tmp_path / "articles" / f"{story.id}.html").exists()


def test_render_row_one_site_omits_local_article_page_for_empty_saved_body(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={"paragraphs": ["", "   "], "paragraphs_zh": []},
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    assert not (tmp_path / "articles" / f"{story.id}.html").exists()


def test_render_row_one_site_keeps_existing_error_for_unsafe_detail_path(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={"detail_path": "../unsafe.html"},
    )
    edition.stories = [story]

    with pytest.raises(ValueError):
        render_row_one_site(
            edition,
            tmp_path,
            local_articles_by_story_id={story.id: _signal_briefing_local_article()},
        )
```

- [ ] **Step 3: Add latest-only stale cleanup test**

```python
def test_render_row_one_site_latest_only_removes_stale_local_article_page(tmp_path) -> None:
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir(parents=True)
    (tmp_path / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (articles_dir / "stale.html").write_text("stale", encoding="utf-8")

    render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert not (articles_dir / "stale.html").exists()
```

- [ ] **Step 4: Add direct template no-allowlist test**

Add a test that calls `render_saved_article_library_html(_edition(), _saved_article_library_fixture())`
without a generated-page allowlist and asserts `href="the-row-signal-1234567890.html"`
is absent while the existing detail-anchor actions remain present. This prevents
template-level usage from emitting broken article-page links for synthetic
libraries.

- [ ] **Step 5: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_page or saved_article_library"
```

Expected: at least the new article-page test fails because `articles/<story-id>.html` is not generated and library cards do not link to it.

---

### Task 2: Implement local article page rendering

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Import template function**

In `render.py`, import `render_local_article_page_html` from `templates.py`.

- [ ] **Step 2: Extend `_write_saved_article_library_page()` signature**

Add `local_articles_by_story_id: Mapping[str, RowOneLocalArticle]` to `_write_saved_article_library_page()` and pass it from `render_row_one_site()`.

- [ ] **Step 3: Add eligibility helper**

Add helpers in `render.py`:

```python
def _local_article_page_href(story_id: str) -> str | None:
    if not safe_local_article_story_id(story_id):
        return None
    return f"{story_id}.html"


def _local_article_page_hrefs_by_detail_path(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> dict[str, str]:
    hrefs: dict[str, str] = {}
    for story in edition.stories:
        article_page_href = _local_article_page_href(story.id)
        if article_page_href is None:
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        if not any(paragraph.strip() for paragraph in article.paragraphs):
            continue
        pure_detail_path = _validated_detail_relative_path(story.detail_path)
        if pure_detail_path is None:
            continue
        hrefs[str(pure_detail_path)] = article_page_href
    return hrefs
```

- [ ] **Step 4: Add writer helper**

Add a helper in `render.py`:

```python
def _write_local_article_pages(
    edition: RowOneEdition,
    articles_dir: Path,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_page_hrefs_by_detail_path: Mapping[str, str],
) -> None:
    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        pure_detail_path = _validated_detail_relative_path(story.detail_path)
        if pure_detail_path is None:
            continue
        article_page_href = article_page_hrefs_by_detail_path.get(str(pure_detail_path))
        if article_page_href is None:
            continue
        html = render_local_article_page_html(edition, story, local_article=article)
        if not html:
            continue
        (articles_dir / article_page_href).write_text(html, encoding="utf-8")
```

- [ ] **Step 5: Pass eligibility map to library index and writer**

Inside `_write_saved_article_library_page()`:

1. Compute `article_page_hrefs_by_detail_path = _local_article_page_hrefs_by_detail_path(...)`.
2. Pass that mapping into `render_saved_article_library_html(...)`.
3. After writing `index.html`, call `_write_local_article_pages(...)` with the same mapping.

- [ ] **Step 6: Add template entry point**

Add in `templates.py`:

```python
def render_local_article_page_html(
    edition: RowOneEdition,
    story: RowOneStory,
    *,
    local_article: RowOneLocalArticle,
) -> str:
    safe_detail_path = _validated_detail_relative_path(story.detail_path)
    if safe_detail_path is None:
        return ""
    detail_href = f"../{safe_detail_path}"
    local_article_section = _render_local_article(local_article)
    if not local_article_section:
        return ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{_render_meta_tags(title=local_article.title or story.headline, description=story.summary.en, page_type="article")}
<title>{_esc(local_article.title or story.headline)} — {_esc(edition.brand)}</title>
<link rel="stylesheet" href="../assets/row-one.css">
</head>
<body>
<header class="detail-header local-article-page-header">
  <a class="back-link" href="../index.html">ROW ONE</a>
  <a class="back-link" href="index.html">Article Library</a>
  <div class="language-toggle" aria-label="Language">
    <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
    <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
  </div>
</header>
<main class="detail-main local-article-page">
  <article class="detail-article local-article-page-article">
    <p class="story-section">
      <span data-lang="en">Local Article</span>
      <span data-lang="zh">本地文章</span>
    </p>
    <p class="section-return"><a href="{_esc(detail_href)}"><span data-lang="en">Open ROW ONE story</span><span data-lang="zh">打开 ROW ONE 故事</span></a></p>
    <h1>{_esc(local_article.title or story.headline)}</h1>
    {local_article_section}
  </article>
</main>
<script src="../assets/row-one.js"></script>
</body>
</html>
"""
```

- [ ] **Step 7: Run focused tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_page or saved_article_library"
```

Expected: local article page tests pass.

---

### Task 3: Link saved article library cards to generated local article pages

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/saved_article_library.py` only if current entry data is insufficient; prefer no model changes.
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add template parameter for generated-page allowlist**

Extend `render_saved_article_library_html()` with:

```python
local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None
```

Thread it into `_render_saved_article_library_source()` and
`_render_saved_article_library_card()`.

- [ ] **Step 2: Add helper to derive article-page href from allowlist**

In `templates.py`:

```python
def _saved_article_library_entry_article_page_href(
    entry: RowOneSavedArticleLibraryEntry,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    if not local_article_page_hrefs_by_detail_path:
        return None
    detail_path = _saved_article_library_entry_detail_path(entry)
    if detail_path is None:
        return None
    href = local_article_page_hrefs_by_detail_path.get(detail_path)
    if href is None:
        return None
    if "/" in href or href.startswith(".") or not href.endswith(".html"):
        return None
    return href
```

- [ ] **Step 3: Update library actions**

Modify `_render_saved_article_library_actions(entry)` so it renders the first action as:

```html
<a class="saved-article-library-primary-action" href="the-row-signal-1234567890.html">Read local article</a>
```

when `_saved_article_library_entry_article_page_href(entry, allowlist)` is available. Keep existing digest/evidence actions to `../details/*.html#...`.

- [ ] **Step 4: Add unsafe and no-allowlist link tests**

Add render tests where:

- no allowlist means no first-class article-page link is rendered;
- an allowlist value containing `/`, starting `.`, or missing `.html` is rejected.

- [ ] **Step 5: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_page or saved_article_library"
```

Expected: library primary action points to the first-class local article page and unsafe entries do not get unsafe page links.

---

### Task 4: Add page styling and docs guards

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add CSS selectors**

Add minimal selectors near existing detail/local article CSS:

```css
.local-article-page {}
.local-article-page-header {}
.local-article-page-article {}
.saved-article-library-primary-action {}
```

Use existing ROW ONE typography and border system. Do not introduce a separate visual theme.

- [ ] **Step 2: Add CSS test**

Extend existing CSS tests to assert the new selectors appear.

- [ ] **Step 3: Update docs**

Add Stage 339 text to `README.md` and `docs/row-one.md`:

```text
Stage 339 adds generated-site only first-class local article pages at articles/<story-id>.html for current-edition saved local article sidecars; it reuses existing saved local article paragraphs, provenance, article maps, digest, reader, paragraph evidence, content sections, and existing detail-page routes. It does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 4: Update doc guard tests**

Add assertions in `tests/test_row_one_docs.py` and `tests/test_workflows.py` that the Stage 339 boundary wording exists and contract payloads do not contain `local_article_pages` or `first_class_local_article`.

- [ ] **Step 5: Run docs/workflow focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_339 or local_article_pages or row_one"
```

Expected: docs and workflow boundary tests pass.

---

### Task 5: Review, verification, commit, and push

**Files:**
- Create: `docs/reviews/claude-code-stage-339-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-339-code-review-prompt.md`
- Create review-result docs if Claude/opencode returns text that should be preserved.

- [ ] **Step 1: Request plan review before implementation**

Before implementation, run Claude Code with `--effort max` and the design/plan files. Fix Critical/Important findings before starting code.

- [ ] **Step 2: Request code review after implementation**

After implementation, run Claude Code with `--effort max` against the diff. Fix Critical/Important findings.

- [ ] **Step 3: Run focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "local_article_page or saved_article_library or stage_339 or row_one"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

- [ ] **Step 4: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

- [ ] **Step 5: Secret scan changed and cached files**

Run a changed-file and cached-file scan for token patterns before commit. Do not print secret values.

- [ ] **Step 6: Commit and push**

```bash
git add README.md docs/row-one.md docs/superpowers/specs/2026-07-08-stage-339-row-one-local-article-pages-design.md docs/superpowers/plans/2026-07-08-stage-339-row-one-local-article-pages-plan.md src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py docs/reviews/claude-code-stage-339-code-review-prompt.md docs/reviews/claude-code-stage-339-plan-review-prompt.md
git commit -m "Stage 339: add local article pages"
git push || git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1 -c http.lowSpeedTime=300 push
```

- [ ] **Step 7: Final handoff summary**

Report repo state, commit SHA, verified commands, uncommitted files, and next step.
