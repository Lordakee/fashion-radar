# Stage 355 Saved Article Local Section Binder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional generated-site-only compact section binder to each saved local article page so readers can scan the article's organized sections, references, cited paragraphs, and unfiled saved paragraphs before reading the full local text.

**Architecture:** Build a focused in-memory view model from existing `RowOneLocalArticle.content_sections`, item labels, references, paragraph indices, and saved paragraphs. Pass that view model into `render_local_article_page_html()` and render it between the Stage 354 local reading companion and the existing local article body. Keep it as a compact index layer, not a duplicate of the existing Local Article Information cards, and avoid app contract, schema, runtime, manifest, sidecar, or generated JSON artifact changes.

**Tech Stack:** Python 3, dataclasses, existing ROW ONE render pipeline, pytest, ruff.

---

## File Map

- Create `src/fashion_radar/row_one/saved_article_local_section_binder.py`
  - Owns the new view model and builder.
  - Converts existing content sections into capped compact index rows.
  - Filters paragraph indices and creates renderer-owned fragment hrefs.
- Modify `src/fashion_radar/row_one/render.py`
  - Build the binder for each eligible generated local article page.
  - Pass the binder into `render_local_article_page_html()`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept optional binder object in `render_local_article_page_html()`.
  - Render `_render_saved_article_local_section_binder(...)`.
  - Add scoped CSS for `.saved-article-local-section-binder`.
- Create `tests/test_row_one_saved_article_local_section_binder.py`
  - Unit coverage for builder behavior.
- Modify `tests/test_row_one_render.py`
  - Template and generated-site integration coverage.
- Modify `tests/test_row_one_docs.py`, `tests/test_workflows.py`, `README.md`,
  and `docs/row-one.md`
  - Guard and document the generated-site-only boundary.
- Add review prompts under `docs/reviews/`
  - Keep plan and code review artifacts for the node.

## Task 1: Builder Test and Model

**Files:**
- Create: `tests/test_row_one_saved_article_local_section_binder.py`
- Create: `src/fashion_radar/row_one/saved_article_local_section_binder.py`

- [ ] **Step 1: Write failing builder tests**

Cover:
- article/story id mismatch returns `None`;
- unsafe story ids return `None`;
- content section and item order are preserved;
- original content-section positions are preserved for
  `#local-article-content-section-N`, even after skipped rows or caps;
- item labels become capped chips;
- references are deduped and capped in first-seen order;
- paragraph indices reject bools, negatives, duplicates, blanks, and out-of-range
  values;
- paragraph anchors use one-based `#local-article-paragraph-N` fragments;
- aligned Chinese paragraph excerpts are used when present;
- uncited nonblank paragraphs are collected in an unfiled row;
- empty articles return `None`.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_section_binder.py -q
```

Expected: fail because the module/function does not exist.

- [ ] **Step 2: Implement minimal builder**

Add frozen dataclasses:

- `RowOneSavedArticleLocalSectionBinderParagraph`
- `RowOneSavedArticleLocalSectionBinderRow`
- `RowOneSavedArticleLocalSectionBinder`

Add:

```python
def build_row_one_saved_article_local_section_binder(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleLocalSectionBinder | None:
    ...
```

Implementation requirements:
- call `safe_local_article_story_id(story.id)`;
- require `story.id == local_article.story_id`;
- use only existing local article fields;
- preserve content-section order;
- store the original one-based content-section position on each row;
- skip rows that have no title, no item labels, no references, and no valid
  paragraph links;
- compute unfiled paragraphs from nonblank saved paragraphs not cited by valid
  section item indices;
- generate only `#local-article-content-section-N` and
  `#local-article-paragraph-N` hrefs.

- [ ] **Step 3: Verify builder tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_section_binder.py -q
```

Expected: pass.

## Task 2: Template Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing template tests**

Add tests that call `render_local_article_page_html(...)` directly with a binder
fixture and assert:

- section title `Saved Article Local Section Binder`;
- compact section row, item chip, reference text, and paragraph excerpt render;
- `href="#local-article-content-section-1"` and
  `href="#local-article-paragraph-1"` render;
- the binder appears after `.saved-article-local-reading-companion` when the
  companion is present and before `id="local-article"`;
- HTML escaping works for section titles, item labels, references, and excerpts;
- the section is omitted when the binder argument is `None`.

Run the targeted test and verify failure before implementation.

- [ ] **Step 2: Render optional binder**

Add optional keyword argument:

```python
saved_article_local_section_binder: RowOneSavedArticleLocalSectionBinder | None = None
```

Render:

```python
local_section_binder = _render_saved_article_local_section_binder(
    saved_article_local_section_binder
)
```

Place `{local_section_binder}` after `{local_reading_companion}` and before
`{local_article_section}`.

- [ ] **Step 3: Add scoped CSS**

Add `.saved-article-local-section-binder` styles near the Stage 354 companion
CSS. Keep the visual treatment consistent with existing local article page
cards and avoid changing unrelated generated-site surfaces.

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

- [ ] **Step 1: Write failing integration tests**

Render a small edition with a saved local article and assert:

- `articles/<story-id>.html` contains `.saved-article-local-section-binder`;
- the binder is absent from `articles/index.html`;
- the binder is absent from generated detail pages;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain Stage 355 class names or keys;
- no `data/saved-article-local-section-binder.json` is written.

- [ ] **Step 2: Implement integration**

Import `build_row_one_saved_article_local_section_binder` in `render.py`.

Inside `_write_local_article_pages(...)`, build:

```python
binder = build_row_one_saved_article_local_section_binder(
    story=story,
    local_article=article,
)
```

Pass it to `render_local_article_page_html(...)` as
`saved_article_local_section_binder=binder`.

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

Guard that docs mention `Saved Article Local Section Binder` and the generated
site only boundary.

- [ ] **Step 2: Update docs**

Describe Stage 355 as a local article page section that organizes existing
saved content sections, references, and paragraph anchors without changing app
contracts, schemas, JSON artifacts, fetching, scoring, LLM, scheduling,
deployment, or compliance behavior.

- [ ] **Step 3: Update workflow guard**

Add the builder and template helper names to workflow coverage checks.

## Task 5: Review, Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-355-code-review-prompt.md`

- [ ] **Step 1: Request plan review before coding**

Use the existing `docs/reviews/claude-code-stage-355-plan-review-prompt.md` to
ask a reviewer to inspect the design and plan for scope creep, duplication with
Stage 354 and the Local Article Information cards, paragraph index handling,
render order, and contract/schema changes.

- [ ] **Step 2: Request code review after implementation**

Ask a reviewer to inspect the diff for:
- generated-site-only scope;
- same-page fragment safety;
- one-based paragraph anchor rendering from zero-based indices;
- escaping;
- omission from app payloads and JSON artifacts.

- [ ] **Step 3: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] **Step 4: Commit and push**

Commit message:

```bash
git commit -m "Stage 355: add saved article local section binder"
```

Push by normal git if available; otherwise use the existing GitHub API fallback.

## Self-Review

- Spec coverage: builder, template, integration, docs, workflow guards, review,
  gates, commit, and push are covered.
- Placeholder scan: no implementation step relies on TODO/TBD behavior.
- Type consistency: all named model/function names are stable across tasks.
- Scope guard: no app contracts, schemas, JSON artifacts, scraping, scheduling,
  deployment, compliance-review behavior, or outbound navigation are included.
