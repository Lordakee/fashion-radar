# Stage 354 Saved Article Local Reading Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional generated-site-only reading companion to each saved local article page so readers can orient, continue locally, and jump within stored article content.

**Architecture:** Build a focused in-memory view model from existing saved article library and content-organization models, pass it into `render_local_article_page_html()`, and render an optional section between the information panel and the local article body. Keep all data local to render-time HTML generation and avoid contract/schema/artifact changes.

**Tech Stack:** Python 3, dataclasses, existing ROW ONE render pipeline, pytest, ruff.

---

## File Map

- Create `src/fashion_radar/row_one/saved_article_local_reading_companion.py`
  - Owns the new view model and builder.
  - Sanitizes current and related article routes.
  - Produces capped local-first companion rows.
- Modify `src/fashion_radar/row_one/render.py`
  - Build/publish local article href map before writing local article pages.
  - Pass library, organization, and href map into local article page rendering.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept optional companion object in `render_local_article_page_html()`.
  - Render `_render_saved_article_local_reading_companion(...)`.
  - Add CSS for the new section.
- Create `tests/test_row_one_saved_article_local_reading_companion.py`
  - Unit coverage for builder behavior and unsafe inputs.
- Modify `tests/test_row_one_render.py`
  - Template and generated-site integration coverage.
- Modify `tests/test_row_one_docs.py`, `tests/test_workflows.py`, `README.md`,
  and `docs/row-one.md`
  - Guard and document the new generated local reading surface.

## Task 1: Builder Test and Model

**Files:**
- Create: `tests/test_row_one_saved_article_local_reading_companion.py`
- Create: `src/fashion_radar/row_one/saved_article_local_reading_companion.py`

- [ ] **Step 1: Write failing builder tests**

Cover:
- current article is matched by safe canonical detail path;
- companion preserves organization-group context;
- read-next items prefer generated local article page hrefs;
- current article is excluded from read-next items;
- unsafe detail paths and unsafe local hrefs are filtered;
- empty inputs return `None`.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_reading_companion.py -q
```

Expected: fail because module/function does not exist.

- [ ] **Step 2: Implement minimal builder**

Add frozen dataclasses:

- `RowOneSavedArticleLocalReadingCompanionLink`
- `RowOneSavedArticleLocalReadingCompanionItem`
- `RowOneSavedArticleLocalReadingCompanion`

Add:

```python
def build_row_one_saved_article_local_reading_companion(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleLocalReadingCompanion | None:
    ...
```

Use existing route helpers and Stage 353-style local href validation.

- [ ] **Step 3: Verify builder tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_reading_companion.py -q
```

Expected: pass.

## Task 2: Template Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing template tests**

Add tests that call `render_local_article_page_html(...)` directly with a
companion fixture and assert:

- section title `Saved Article Local Reading Companion`;
- current article context appears;
- read-next local href appears;
- unsafe hrefs do not render;
- HTML escaping works for companion title/source text.

Run the targeted tests and verify failure before implementation.

- [ ] **Step 2: Render optional companion**

Add optional keyword argument:

```python
saved_article_local_reading_companion: RowOneSavedArticleLocalReadingCompanion | None = None
```

Render the companion after `information_panel` and before `local_article_section`.

- [ ] **Step 3: Add scoped CSS**

Add `.saved-article-local-reading-companion` styles near local article page CSS.
Keep the visual style consistent with existing local information and saved
article sections.

- [ ] **Step 4: Verify targeted render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing integration test**

Render a small edition with two saved local articles and assert:

- `articles/<story-id>.html` contains the companion section;
- read-next links point to another generated `articles/*.html` page;
- `articles/index.html` remains generated as before;
- no contract/version constants change.

- [ ] **Step 2: Implement integration**

Adjust `_write_local_article_pages(...)` to accept:

- `saved_article_library`
- `saved_article_content_organization`
- `local_article_page_hrefs_by_detail_path`

Compute href map before writing pages with a helper that mirrors the existing
write eligibility checks, then pass it into both local article pages and the
library page.

- [ ] **Step 3: Verify integration tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: pass.

## Task 4: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write/update docs tests**

Guard that docs mention `Saved Article Local Reading Companion`.

- [ ] **Step 2: Update docs**

Describe the companion as a generated local-article page surface built from
existing saved article library and organization data.

- [ ] **Step 3: Update workflow guard**

Add the builder and template helper names to workflow coverage checks.

## Task 5: Review, Gates, Commit, Push

**Files:**
- Add review prompts under `docs/reviews/`

- [ ] **Step 1: Request code review**

Ask a reviewer to inspect the diff for scope creep, route safety, render order,
and contract/schema changes.

- [ ] **Step 2: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] **Step 3: Commit and push**

Commit message:

```bash
git commit -m "Stage 354: add saved article local reading companion"
```

Push by normal git if available; otherwise use the existing GitHub API fallback.

## Self-Review

- Spec coverage: builder, template, integration, docs, workflow guards, review,
  gates, commit, and push are covered.
- Placeholder scan: no implementation step relies on TODO/TBD behavior.
- Type consistency: all named model/function names are stable across tasks.
- Scope guard: no app contracts, schemas, JSON artifacts, scraping, scheduling,
  compliance-review behavior, or outbound-primary navigation are included.
