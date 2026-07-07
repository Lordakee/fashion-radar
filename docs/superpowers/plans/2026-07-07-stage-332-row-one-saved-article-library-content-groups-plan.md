# Stage 332 ROW ONE Saved Article Library Content Groups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render ROW ONE saved article content groups inside `articles/index.html` so the dedicated saved article library organizes local saved bodies by read-first, people/brands, products, and source structure.

**Architecture:** Reuse the existing `RowOneSavedArticleContentOrganization` view model that `render_row_one_site()` already builds for the homepage. Thread it into `render_saved_article_library_html()`, render it between the optional saved signal index and the source grid, and add a context-specific href prefix so article-library links point to `../details/...` while homepage links remain `details/...`.

**Tech Stack:** Python 3.13, existing ROW ONE static HTML renderer, dataclass view models, pytest, Ruff, Claude Code review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Pass `saved_article_content_organization` into `_write_saved_article_library_page()`.
  - Add a matching parameter to `_write_saved_article_library_page()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Add optional `saved_article_content_organization` to `render_saved_article_library_html()`.
  - Render the existing content organization section on `articles/index.html`.
  - Add an internal `href_prefix` parameter to the content-organization renderer and helper functions.
- Modify: `tests/test_row_one_render.py`
  - Add render integration coverage for `articles/index.html`.
  - Add direct renderer safety coverage for prefixed safe links and filtered unsafe links.
- Modify: `tests/test_row_one_docs.py`
  - Add docs sentinel for the Stage 332 boundary.
- Modify: `README.md`
  - Document the generated-site-only boundary.
- Modify: `docs/row-one.md`
  - Document the generated-site-only boundary.
- Create review artifacts under `docs/reviews/`.

## Task 1: Add Red Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add the article-library integration test**

Add a test near `test_render_row_one_site_includes_saved_signal_index_in_article_library`:

```python
def test_render_row_one_site_includes_saved_article_content_organization_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_content_organization_section_html(library_html)

    assert 'class="saved-article-content-organization"' in section_html
    assert "Saved Article Content Organization" in section_html
    assert "保存正文内容整理" in section_html
    assert "People &amp; Brands" in section_html
    assert "Products" in section_html
    assert "The Row appears in paragraph one." in section_html
    assert "Alaia flats appear in paragraph two." in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html'
        '#local-article-content-section-1"'
    ) in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html'
        '#local-article-paragraph-1"'
    ) in section_html
    assert (
        library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert (
        'href="details/the-row-signal-1234567890.html'
        '#local-article-content-section-1"'
    ) in homepage_html

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_content_organization" not in contract_json
        assert "content_organization" not in contract_json
        assert "saved-article-content-organization" not in contract_json
        assert "Saved Article Content Organization" not in contract_json
    assert not (tmp_path / "data" / "saved-article-content-organization.json").exists()
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_content_organization_in_article_library -q
```

Expected: FAIL because `articles/index.html` does not yet render the content
organization section.

- [ ] **Step 2: Add the direct renderer safety test**

Add a test near
`test_render_index_html_filters_saved_article_content_organization_evidence_links`:

```python
def test_render_saved_article_library_filters_content_organization_links_on_library_page() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 2),
        references=(),
    )
    invalid_path_cards = (
        replace(
            safe_card,
            title=LocalizedText(en="JS card", zh="JS 卡片"),
            detail_path="javascript:alert(1)#local-article-content-section-1",
        ),
        replace(
            safe_card,
            title=LocalizedText(en="Traversal card", zh="穿越卡片"),
            detail_path="../secrets.html#local-article-content-section-1",
        ),
        replace(
            safe_card,
            title=LocalizedText(en="Wrong fragment card", zh="错误片段卡片"),
            detail_path="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
    )
    bad_index_card = replace(
        safe_card,
        title=LocalizedText(en="Bad index card", zh="坏索引卡片"),
        paragraph_indices=(-1, True),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, *invalid_path_cards, bad_index_card],
            ),
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert (
        'href="../details/the-row-signal-1234567890.html'
        '#local-article-content-section-1"'
    ) in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-3"'
        in section_html
    )
    assert "javascript:alert" not in section_html
    assert "../secrets" not in section_html
    assert "#local-article-paragraph-0" not in section_html
    assert "#local-article-paragraph-2" not in section_html
    assert "JS card" not in section_html
    assert "Traversal card" not in section_html
    assert "Wrong fragment card" not in section_html
    assert "Bad index card" in section_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page -q
```

Expected: FAIL because `render_saved_article_library_html()` does not accept the
new keyword argument yet.

## Task 2: Thread The Existing View Model Into The Article Library Page

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Update `render_row_one_site()` call site**

In `src/fashion_radar/row_one/render.py`, update the `_write_saved_article_library_page()`
call:

```python
    _write_saved_article_library_page(
        edition,
        output_dir / "articles",
        saved_article_library=saved_article_library,
        saved_signal_index=saved_signal_index,
        saved_article_content_organization=saved_article_content_organization,
    )
```

- [ ] **Step 2: Update `_write_saved_article_library_page()` signature and renderer call**

Change the helper signature:

```python
def _write_saved_article_library_page(
    edition: RowOneEdition,
    articles_dir: Path,
    *,
    saved_article_library: RowOneSavedArticleLibrary | None,
    saved_signal_index: RowOneSavedSignalIndex | None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None,
) -> None:
```

Pass the value into `render_saved_article_library_html()`:

```python
        render_saved_article_library_html(
            edition,
            saved_article_library,
            saved_signal_index=saved_signal_index,
            saved_article_content_organization=saved_article_content_organization,
        ),
```

Add `RowOneSavedArticleContentOrganization` to the existing import from
`fashion_radar.row_one.saved_article_content_organization`; `render.py` already
imports the builder, but the new `_write_saved_article_library_page()`
annotation also needs the view-model type.

- [ ] **Step 3: Update `render_saved_article_library_html()`**

In `src/fashion_radar/row_one/templates.py`, change the signature:

```python
def render_saved_article_library_html(
    edition: RowOneEdition,
    library: RowOneSavedArticleLibrary,
    *,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
) -> str:
```

Build the section with the library-page prefix:

```python
    content_organization = _render_saved_article_content_organization(
        saved_article_content_organization,
        href_prefix="../",
    )
```

Render it between `signal_index` and the source grid:

```html
  {signal_index}
  {content_organization}
  <div class="saved-article-library-grid">{groups}</div>
```

- [ ] **Step 4: Run the focused integration test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_content_organization_in_article_library -q
```

Expected: still FAIL until href-prefix behavior is implemented, or PASS if the
prefix is already threaded by Task 3.

## Task 3: Add Safe Href Prefixing For Content Organization Links

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add `href_prefix` to renderer helpers**

Change the helper signatures:

```python
def _render_saved_article_content_organization(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    href_prefix: str = "",
) -> str:
```

```python
def _render_saved_article_content_organization_group(
    group: RowOneSavedArticleContentOrganizationGroup,
    *,
    href_prefix: str = "",
) -> str:
```

```python
def _render_saved_article_content_organization_card(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
```

```python
def _render_saved_article_content_organization_chips(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
```

```python
def _render_saved_article_content_organization_evidence(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
```

Forward `href_prefix` through each call chain.

- [ ] **Step 2: Add a tiny prefix helper**

Add near `_safe_saved_article_content_organization_href()`:

```python
def _prefixed_saved_article_content_organization_href(href: str, href_prefix: str) -> str:
    if not href_prefix:
        return href
    return f"{href_prefix}{href}"
```

Use it only after `_safe_saved_article_content_organization_href()` or
`_safe_saved_article_content_organization_evidence_href()` has returned a safe
href:

```python
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, href_prefix)
```

For evidence:

```python
        href = _safe_saved_article_content_organization_evidence_href(
            card.detail_path,
            paragraph_index,
        )
        if href is None:
            continue
        href = _prefixed_saved_article_content_organization_href(href, href_prefix)
```

Do not pass prefixed hrefs into validation, because `../details/...` is only
safe in the article-library page context after the canonical `details/...`
target has already been validated.

- [ ] **Step 3: Run the direct safety test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page -q
```

Expected: PASS.

- [ ] **Step 4: Verify homepage links remain unprefixed**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_index_html_filters_saved_article_content_organization_evidence_links tests/test_row_one_render.py::test_render_row_one_site_saved_article_content_organization_links_evidence_paragraphs -q
```

Expected: PASS. Existing homepage links should remain `details/...`.

## Task 4: Add Documentation Boundary Test And Docs

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add a failing docs sentinel**

Add near `test_row_one_docs_describe_daily_saved_article_library_boundary()`:

```python
def test_row_one_docs_describe_stage_332_saved_article_library_content_groups_boundary() -> None:
    expected = _normalized(
        "Stage 332 adds generated-site only saved article content groups inside "
        "`articles/index.html`; it reuses existing saved local article sidecars and "
        "existing `content_sections` to organize the current edition's saved local "
        "articles by read-first, people/brands, products, and source structure, "
        "with links back to existing detail-page content-section and paragraph "
        "anchors; it does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, "
        "matching, extraction, scoring, ranking, LLM, connector, scheduling, "
        "deployment, market grouping, domestic/international classification, or "
        "compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_332_saved_article_library_content_groups_boundary -q
```

Expected: FAIL because docs do not yet mention Stage 332.

- [ ] **Step 2: Update README and ROW ONE docs**

Add the exact Stage 332 paragraph to `README.md` and `docs/row-one.md` near the
Stage 331/328/327/326 ROW ONE generated-site boundary notes:

```markdown
Stage 332 adds generated-site only saved article content groups inside
`articles/index.html`; it reuses existing saved local article sidecars and
existing `content_sections` to organize the current edition's saved local
articles by read-first, people/brands, products, and source structure, with
links back to existing detail-page content-section and paragraph anchors; it
does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1,
schemas, JSON artifacts, source collection, fetching, matching, extraction,
scoring, ranking, LLM, connector, scheduling, deployment, market grouping,
domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 3: Run docs test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_332_saved_article_library_content_groups_boundary -q
```

Expected: PASS.

## Task 5: Focused Verification, Review, And Full Node Close

**Files:**
- Create: `docs/reviews/claude-code-stage-332-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-332-code-review.md`
- Create/rereview if needed: `docs/reviews/claude-code-stage-332-code-rereview*.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_content_organization_in_article_library tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page tests/test_row_one_docs.py::test_row_one_docs_describe_stage_332_saved_article_library_content_groups_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page tests/test_row_one_render.py::test_render_row_one_site_includes_saved_signal_index_in_article_library tests/test_row_one_render.py::test_render_index_html_filters_saved_article_content_organization_evidence_links tests/test_row_one_render.py::test_render_row_one_site_saved_article_content_organization_links_evidence_paragraphs tests/test_row_one_saved_article_content_organization.py tests/test_row_one_docs.py::test_row_one_docs_describe_daily_saved_article_library_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: all commands exit 0.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-332-code-review-prompt.md` with:

```markdown
Review Stage 332 for Fashion Radar / ROW ONE.

Goal: render existing saved article content groups inside `articles/index.html`
using the existing `RowOneSavedArticleContentOrganization` model, with
article-library links prefixed as `../details/...` after existing safety
validation, while leaving homepage links and JSON contracts unchanged.

Please review the diff from `origin/main` to `HEAD` for:
- correctness and route safety
- generated-site-only boundary
- test adequacy
- docs accuracy
- accidental contract/schema/collector/compliance-review scope creep

Classify findings as Critical, Important, Minor, or None.
```

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-332-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-332-code-review.md
rm -f "$tmp_review"
```

Expected: review output is captured in the markdown file. Fix Critical and
Important findings before proceeding.

- [ ] **Step 3: Run full node verification**

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
git add README.md docs/row-one.md docs/reviews docs/superpowers src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
git commit -m "Stage 332: add row one saved article content groups"
GIT_TERMINAL_PROMPT=0 git -c http.version=HTTP/1.1 push origin main
```

Expected: push succeeds and `git status --short --branch` shows `main...origin/main`
with no uncommitted changes.
