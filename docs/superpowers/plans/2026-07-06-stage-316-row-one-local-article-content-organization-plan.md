# Stage 316 ROW ONE Local Article Content Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site homepage section that organizes existing saved local article `content_sections` into scan-first groups, so ROW ONE shows useful article content instead of only links.

**Architecture:** Add a pure builder module for saved article content organization, wire it into `render_row_one_site()` and `render_index_html()`, and render a homepage-only section from existing sidecar data. Keep the app payload, manifest, runtime, schemas, source collection, extraction, scoring, connectors, and compliance-review behavior unchanged.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, deterministic HTML rendering in `templates.py`, pytest, Ruff, existing Claude Code review workflow.

---

## Files

- Create: `src/fashion_radar/row_one/saved_article_content_organization.py`
- Create: `tests/test_row_one_saved_article_content_organization.py`
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Create: `docs/reviews/claude-code-stage-316-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-316-plan-review.md`
- Later implementation review artifacts:
  - `docs/reviews/claude-code-stage-316-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-316-code-review.md`

---

### Task 1: Saved Article Content Organization Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_content_organization.py`
- Create: `tests/test_row_one_saved_article_content_organization.py`

- [ ] **Step 1: Add failing builder tests**

Create `tests/test_row_one_saved_article_content_organization.py` with tests for:

- Current-edition filtering.
- Mismatched `article.story_id` exclusion.
- Unsafe detail path exclusion.
- Invalid story ID exclusion.
- Blank paragraph exclusion.
- Empty `content_sections` omission.
- Group order: `takeaways`, `entities`, `product_signals`, `brand_signals`.
- Card caps at four cards per group.
- Multi-item content sections aggregate and dedupe valid paragraph indices in
  first-seen order.

Use existing helper patterns from `tests/test_row_one_saved_article_briefs.py` and
`tests/test_row_one_saved_article_coverage.py`.

- [ ] **Step 2: Verify tests fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_content_organization.py -q
```

Expected: fail with missing module.

- [ ] **Step 3: Implement builder**

Create `src/fashion_radar/row_one/saved_article_content_organization.py` with:

- `RowOneSavedArticleContentOrganizationCard`
- `RowOneSavedArticleContentOrganizationGroup`
- `RowOneSavedArticleContentOrganization`
- `build_row_one_saved_article_content_organization()`

Filtering must mirror saved article coverage/briefs:

- only current `edition.stories`
- `article.story_id == story.id`
- `safe_local_article_story_id(story.id)`
- `is_safe_row_one_detail_path(story.detail_path)`
- at least one nonblank paragraph
- at least one usable `content_sections` item

Group mapping:

- `takeaways` → `Read First`
- `entities` → `People & Brands`
- `product_signals` → `Products`
- `brand_signals` → `Source Structure`

Each card should carry:

- story headline as title
- source display name
- edition section title
- content section title
- lead text from first usable item body, falling back to first nonblank paragraph
- detail link to `details/...html#local-article-content-section-N`
- valid paragraph indices aggregated and deduped from all usable items in the
  selected content section while preserving first-seen order
- deduped references from the content item

`N` is the one-based position used by the existing detail-page renderer:
`enumerate(article.content_sections, start=1)`.
Use deterministic group deks:

- Read First: `Key takeaways from saved articles` / `保存正文中的关键要点`
- People & Brands: `Brands, people, and designers mentioned` / `正文提到的品牌、人物与设计师`
- Products: `Bags, shoes, and product signals` / `包袋、鞋履与产品信号`
- Source Structure: `Source structure and brand-signal context` / `来源结构与品牌信号背景`

- [ ] **Step 4: Verify builder tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_content_organization.py -q
```

Expected: pass.

---

### Task 2: Homepage Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add failing render/workflow assertions**

Extend `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` to assert:

- `index.html` contains `Saved Article Content Organization`
- `index.html` contains `保存正文内容整理`
- `index.html` links to `#local-article-content-section-`
- `data/edition.json` does not contain `saved_article_content_organization`
- `data/manifest.json` does not contain `saved_article_content_organization`
- `data/runtime.json` does not contain `saved_article_content_organization`

- [ ] **Step 2: Verify render assertions fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite -q
```

Expected: fail because homepage section is not rendered.

- [ ] **Step 3: Wire builder into render**

In `src/fashion_radar/row_one/render.py`:

- import `build_row_one_saved_article_content_organization`
- build it next to saved article coverage/briefs
- pass it into `render_index_html()`
- do not add it to app payload, runtime payload, manifest payload, or schemas

In `src/fashion_radar/row_one/templates.py`:

- import the new dataclasses
- add `saved_article_content_organization` parameter to `render_index_html()`
- render after saved article briefs
- add safe renderer helpers that skip unsafe links
- link cards to existing detail fragment anchors

- [ ] **Step 4: Verify render/workflow tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_content_organization.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite -q
```

Expected: pass.

---

### Task 3: Documentation Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs test**

Add `test_row_one_docs_describe_local_article_content_organization_boundary()` to
`tests/test_row_one_docs.py`.

Also update the existing Stage 315 guard so its slice ends at Stage 316 instead
of Stage 310:

```python
readme_stage_315 = readme[
    readme.index("Stage 315 adds ROW ONE article readiness diagnostics") : readme.index("Stage 316 adds")
]
docs_stage_315 = docs[
    docs.index("Stage 315 adds ROW ONE article readiness diagnostics") : docs.index("Stage 316 adds")
]
```

The Stage 316 slice should be inserted after Stage 315 and before Stage 310:

```python
readme_stage_316 = readme[
    readme.index("Stage 316 adds local article content organization") : readme.index("Stage 310 adds")
]
docs_stage_316 = docs[
    docs.index("Stage 316 adds local article content organization") : docs.index("Stage 310 adds")
]
```

Expected phrases:

- `local article content organization`
- `existing \`data/articles/<story-id>.json\` sidecars`
- `existing saved local paragraphs`
- `existing \`content_sections\``
- `generated-site only`
- `does not change \`row-one-app/v7\``
- `does not change \`data/edition.json\``
- `does not change \`row-one-manifest/v1\``
- `does not change \`row-one-runtime/v1\``
- `does not change detail routes`
- `does not change paragraph anchors`
- `does not change schemas`
- `does not write a new json artifact`
- `does not add source collection`
- `does not fetch article pages`
- `does not add scoring`
- `does not add llm calls`
- `does not add connectors`
- `not a compliance review feature`

Forbidden phrases:

- `row-one-app/v8`
- `row-one-manifest/v2`
- `row-one-runtime/v2`
- `changes schemas`
- `adds source collection`
- `adds scoring`
- `adds llm calls`
- `adds social connectors`
- `adds community connectors`
- `adds compliance review`

- [ ] **Step 2: Verify docs test fails**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary -q
```

Expected: fail because Stage 316 docs are not present.

- [ ] **Step 3: Add Stage 316 docs**

Add a Stage 316 paragraph after Stage 315 in both `README.md` and
`docs/row-one.md`:

```md
Stage 316 adds local article content organization for ROW ONE: the generated
homepage groups existing `data/articles/<story-id>.json` sidecars, existing
saved local paragraphs, and existing `content_sections` into scan-first
read-first, people/brands, products, and source-structure groups. This is a
generated-site only presentation surface; it does not change `row-one-app/v7`,
does not change `data/edition.json`, does not change `row-one-manifest/v1`,
does not change `row-one-runtime/v1`, does not change detail routes, does not
change paragraph anchors, does not change schemas, does not add source
collection, does not fetch article pages, does not add scoring, does not add
llm calls, does not add connectors, and is not a compliance review feature.
```

- [ ] **Step 4: Verify docs tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: pass.

---

### Task 4: Review, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-316-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-316-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_content_organization.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

- [ ] **Step 2: Request Claude Code review**

Create and run a Stage 316 code review prompt with:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  -p "$(cat docs/reviews/claude-code-stage-316-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-316-code-review.md
```

Fix any Critical or Important findings and rerun focused verification.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

- [ ] **Step 4: Commit and push**

Stage only Stage 316 files. Do not stage `uv.lock`, `reports/row-one/site/**`,
`.codegraph/**`, cookies, tokens, or local account data.

Commit:

```bash
git commit -m "Stage 316: add row one article content organization"
git push origin main
```

---

## Plan Self-Review

- Spec coverage: builder, rendering, docs, reviews, verification.
- Placeholder scan: no TBD/TODO/fill-in-later text remains.
- Scope check: generated-site presentation only.
- Contract check: app, manifest, runtime, schemas, source collection, extraction,
  connectors, scoring, LLMs, and compliance review stay untouched.
