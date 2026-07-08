# Stage 344 Saved Article Organization Coverage Matrix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Saved Article Organization Coverage Matrix to `articles/index.html`.

**Architecture:** Implement the matrix as private render helpers inside `src/fashion_radar/row_one/templates.py`, reusing existing content organization cards and safe href helpers. Add focused render tests, workflow contract guards, and docs boundary text without changing models, schemas, JSON artifacts, app contracts, source collection, extraction, ranking, scheduling, deployment, or recommendation behavior.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add CSS selectors for the coverage matrix.
  - Add constants for row and reference caps.
  - Add private helpers for safe card grouping, strict paragraph counting,
    reference dedupe/capping, and row rendering.
  - Insert matrix HTML inside `_render_saved_article_content_organization()`
    before the existing groups.
- Modify `tests/test_row_one_render.py`
  - Add focused failing tests for matrix rendering, grouping, unsafe filtering,
    strict paragraph counts, reference capping/escaping, CSS selectors, and
    no contract leakage.
- Modify `tests/test_workflows.py`
  - Add generated contract negative assertions and artifact absence checks.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 344 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 344 boundary paragraph.
- Add `docs/reviews/claude-code-stage-344-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-344-plan-review-prompt.md`

## Task 1: Write Render Tests First

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add a failing test for matrix placement and facts**

Add a test near the existing saved article content organization tests:

```python
def test_render_saved_article_content_organization_includes_coverage_matrix() -> None:
    first_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row signal", zh="The Row 信号"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="A brand signal.", zh="一个品牌信号。"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1),
        references=(RowOneReference(name="The Row", type="brand", label="brand"),),
    )
    second_card = replace(
        first_card,
        section_label=LocalizedText(en="Products", zh="产品"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-2",
        paragraph_indices=(1, 2),
        references=(RowOneReference(name="Margaux", type="product", label="bag"),),
    )
    third_card = replace(
        first_card,
        title=LocalizedText(en="Alaia signal", zh="Alaia 信号"),
        source_name="Business of Fashion",
        detail_path="details/alaia-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(RowOneReference(name="Alaia", type="brand", label="brand"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[first_card, third_card],
            ),
            RowOneSavedArticleContentOrganizationGroup(
                key="products",
                title=LocalizedText(en="Products", zh="产品"),
                dek=LocalizedText(en="Product context", zh="产品背景"),
                cards=[second_card],
            ),
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert 'class="saved-article-organization-coverage-matrix"' in section_html
    assert section_html.index('class="saved-article-organization-coverage-matrix"') < (
        section_html.index('class="saved-article-content-organization-groups"')
    )
    assert "The Row signal" in section_html
    assert "Alaia signal" in section_html
    assert "2 organized sections" in section_html
    assert "3 evidence paragraphs" in section_html
    assert "People &amp; Brands" in section_html
    assert "Products" in section_html
    assert "The Row" in section_html
    assert "Margaux" in section_html
```

- [ ] **Step 2: Run the test and confirm it fails**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_saved_article_content_organization_includes_coverage_matrix -q
```

Expected: fail because the matrix class does not exist yet.

- [ ] **Step 3: Add a failing test for unsafe filtering and strict counts**

Add:

```python
def test_saved_article_organization_matrix_filters_unsafe_and_strict_counts() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe article", zh="安全文章"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 0, 1, True, -1),
        references=(RowOneReference(name="Safe Ref", type="brand", label="tracked"),),
    )
    unsafe_card = replace(
        safe_card,
        title=LocalizedText(en="Unsafe article", zh="不安全文章"),
        source_name="Unsafe Source",
        detail_path="javascript:alert(1)#local-article-content-section-1",
        paragraph_indices=(0, 1, 2),
        references=(RowOneReference(name="Unsafe Ref", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, unsafe_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "Safe article" in section_html
    assert "Unsafe article" not in section_html
    assert "Unsafe Ref" not in section_html
    assert "Unsafe Source" not in section_html
    assert "2 evidence paragraphs" in section_html
    assert "javascript:alert" not in section_html
```

- [ ] **Step 4: Add a failing test for reference escaping and cap**

Add:

```python
def test_saved_article_organization_matrix_caps_and_escapes_references() -> None:
    references = tuple(
        RowOneReference(name=f"Ref <{index}>", type="brand", label=f"Label <{index}>")
        for index in range(1, 8)
    )
    card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Reference article", zh="引用文章"),
        source_name="Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Lead", zh="摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=references,
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)
    matrix_start = section_html.index('class="saved-article-organization-coverage-matrix"')
    matrix_end = section_html.index('class="saved-article-content-organization-groups"')
    matrix_html = section_html[matrix_start:matrix_end]

    assert "Ref &lt;1&gt;" in matrix_html
    assert "Label &lt;1&gt;" in matrix_html
    assert "Ref <1>" not in matrix_html
    assert "Ref &lt;7&gt;" not in matrix_html
```

## Task 2: Implement Matrix Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add constants**

Near the existing saved article content organization constants, add:

```python
SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_ROWS = 6
SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_REFS = 5
```

- [ ] **Step 2: Add CSS selectors**

Near the existing saved article content organization CSS, add styles for:

```css
.saved-article-organization-coverage-matrix
.saved-article-organization-coverage-header
.saved-article-organization-coverage-grid
.saved-article-organization-coverage-row
.saved-article-organization-coverage-title
.saved-article-organization-coverage-meta
.saved-article-organization-coverage-chip
.saved-article-organization-coverage-ref
.saved-article-organization-coverage-link
```

Use the same restrained visual language as the Stage 343 summary strip: thin
`var(--line)` borders, `var(--panel)` backgrounds, compact typography, and no
new hero-scale treatment.

- [ ] **Step 3: Add private helper functions**

Add helpers near `_render_saved_article_content_organization()`:

```python
def _render_saved_article_organization_coverage_matrix(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    href_prefix: str = "",
) -> str:
    ...
```

The helper should:

- Iterate groups in current order.
- Keep only cards with `_safe_saved_article_content_organization_href(card.detail_path)`.
- Group by `_saved_article_content_organization_detail_path_key(safe_href)`.
- Preserve first-seen article order.
- Deduplicate group chips by group key.
- Count sections/cards per article from safe cards.
- Count evidence paragraphs using strict integer paragraph indices only.
- Deduplicate references by normalized `(name, type, label)`.
- Render at most `SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_ROWS` rows and
  `SAVED_ARTICLE_ORGANIZATION_COVERAGE_MAX_REFS` refs per row.

- [ ] **Step 4: Insert matrix before group list**

Inside `_render_saved_article_content_organization()`, compute:

```python
coverage_matrix = _render_saved_article_organization_coverage_matrix(
    organization,
    href_prefix=href_prefix,
)
```

Insert `{coverage_matrix}` between the section header and:

```html
<div class="saved-article-content-organization-groups">
```

- [ ] **Step 5: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "organization_coverage_matrix or saved_article_content_organization"
```

Expected: all selected tests pass.

## Task 3: Add Docs And Contract Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add Stage 344 docs paragraph**

Add this paragraph before Stage 343 in both docs:

```text
Stage 344 adds a generated-site only Saved Article Organization Coverage Matrix inside `articles/index.html`; it reuses existing saved article content organization groups, existing safe card detail-path anchors, existing card references, and existing paragraph indices to show article-by-article organization coverage across groups without changing app-facing contracts; it does not create `data/saved-article-organization-coverage.json`, does not create `data/organization-coverage-matrix.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs test**

In `tests/test_row_one_docs.py`, assert the paragraph appears in both docs and
that forbidden broadening phrases are absent from the Stage 344 paragraph.

- [ ] **Step 3: Add workflow negative guards**

In `tests/test_workflows.py`, assert generated contract payloads do not include:

```python
"saved_article_organization_coverage"
"organization_coverage_matrix"
"Saved Article Organization Coverage Matrix"
"saved-article-organization-coverage"
"organization-coverage-matrix"
```

Add artifact absence checks for:

```python
output_dir / "saved-article-organization-coverage.json"
output_dir / "articles" / "saved-article-organization-coverage.json"
output_dir / "data" / "saved-article-organization-coverage.json"
output_dir / "saved-article-organization-coverage.html"
output_dir / "articles" / "saved-article-organization-coverage.html"
output_dir / "data" / "saved-article-organization-coverage.html"
output_dir / "organization-coverage-matrix.json"
output_dir / "articles" / "organization-coverage-matrix.json"
output_dir / "data" / "organization-coverage-matrix.json"
output_dir / "organization-coverage-matrix.html"
output_dir / "articles" / "organization-coverage-matrix.html"
output_dir / "data" / "organization-coverage-matrix.html"
```

- [ ] **Step 4: Run docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: pass.

## Task 4: Verification And Review

**Files:**
- Add: `docs/reviews/claude-code-stage-344-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-344-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
git diff --check
```

Expected: pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

Expected: pass.

- [ ] **Step 3: Run staged secret scan before commit**

Run:

```bash
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}'; then exit 1; else echo "No token-shaped secrets in staged diff"; fi
```

Expected: `No token-shaped secrets in staged diff`.

- [ ] **Step 4: Commit and push**

Run:

```bash
git commit -m "Stage 344: add organization coverage matrix"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: commit and push succeed.

## Self-Review

- Spec coverage: each acceptance criterion maps to Tasks 1-4.
- Placeholder scan: no TBD/TODO/fill-in placeholders remain.
- Type consistency: all referenced dataclasses and helper names already exist
  except the Stage 344 private helpers introduced in Task 2.
- Scope check: this is a single generated-site-only rendering node.
