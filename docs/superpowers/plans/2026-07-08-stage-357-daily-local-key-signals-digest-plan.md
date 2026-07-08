# Stage 357 Daily Local Key Signals Digest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage digest that aggregates Stage 356
local article key signals into a daily scan-first summary.

**Architecture:** Build a focused in-memory homepage view model from
`RowOneEdition`, current local articles, and Stage 356
`build_row_one_saved_article_key_signals(...)` outputs. Pass that model to
`render_index_html()` and render it after Saved Article Briefs and before Saved
Article Content Organization. Keep the feature HTML-only and avoid app contract,
schema, runtime, manifest, sidecar, route-family, or generated JSON artifact
changes.

**Tech Stack:** Python 3, dataclasses, existing ROW ONE render pipeline,
pytest, ruff.

---

## File Map

- Create `src/fashion_radar/row_one/daily_local_key_signals_digest.py`
  - Owns the homepage digest view model and builder.
  - Aggregates Stage 356 key-signal outputs across current-edition local
    articles.
  - Emits renderer-owned local article hrefs only.
- Modify `src/fashion_radar/row_one/render.py`
  - Build the digest before `render_index_html(...)`.
  - Pass it to the homepage renderer only.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept optional `daily_local_key_signals_digest` in `render_index_html(...)`.
  - Render `_render_daily_local_key_signals_digest(...)`.
  - Add scoped CSS for `.daily-local-key-signals-digest`.
- Create `tests/test_row_one_daily_local_key_signals_digest.py`
  - Unit coverage for aggregation behavior.
- Modify `tests/test_row_one_render.py`
  - Template, CSS, and generated-site integration coverage.
- Modify `tests/test_row_one_docs.py`, `tests/test_workflows.py`,
  `README.md`, and `docs/row-one.md`
  - Guard and document the generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Builder Test and Model

**Files:**
- Create: `tests/test_row_one_daily_local_key_signals_digest.py`
- Create: `src/fashion_radar/row_one/daily_local_key_signals_digest.py`

- [ ] **Step 1: Write failing builder tests**

Cover:
- mismatched story/article IDs and unsafe story IDs are skipped;
- stories without Stage 356 key signals are skipped;
- `Why It Matters` entries preserve edition story order;
- brand/product/people references dedupe by normalized displayed name while
  preserving first-seen order;
- support counts are computed from all eligible local articles before display
  caps;
- theme labels dedupe by normalized displayed label;
- hrefs point only to `articles/<story-id>.html#saved-article-key-signals-title`,
  `articles/<story-id>.html#local-article-paragraph-N`, or
  `articles/<story-id>.html#local-article-content-section-N`;
- returned digest is `None` when no groups can be built.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_key_signals_digest.py -q
```

Expected: fail because the module/function does not exist.

- [ ] **Step 2: Implement minimal builder**

Add frozen dataclasses:

- `RowOneDailyLocalKeySignalsDigestEntry`
- `RowOneDailyLocalKeySignalsDigestGroup`
- `RowOneDailyLocalKeySignalsDigest`

Add:

```python
def build_row_one_daily_local_key_signals_digest(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneDailyLocalKeySignalsDigest | None:
    ...
```

Implementation requirements:
- iterate `edition.stories` order;
- call `build_row_one_saved_article_key_signals(...)` for valid matching local
  articles;
- build groups with keys `why_it_matters`, `brands`, `products`, `people`, and
  `themes`;
- generate only `articles/<story-id>.html#...` local article links;
- reconstruct full `articles/<safe-story-id>.html#fragment` hrefs from Stage
  356 evidence/theme fragment-only hrefs such as `#local-article-paragraph-1`
  and `#local-article-content-section-1`;
- dedupe references/themes by normalized displayed name;
- keep counts from full eligible input and cap visible entries;
- return `None` when no meaningful groups can be built.

- [ ] **Step 3: Verify builder tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_key_signals_digest.py -q
```

Expected: pass.

## Task 2: Homepage Template Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing template tests**

Add a direct `render_index_html(...)` test with a digest fixture and assert:

- section class `.daily-local-key-signals-digest` and title
  `Daily Local Key Signals Digest`;
- article statement, reference name, theme label, support count, and local
  article href render;
- invalid hrefs such as `javascript:...`, `../details/...`,
  `articles/unsafe/story.html#...`, `articles/<story-id>.html#bad`, and
  `articles/<story-id>.html#local-article-paragraph-0` do not render;
- all display text is escaped;
- render order is after Saved Article Briefs and before Saved Article Content
  Organization when both sections exist;
- section is omitted when the digest argument is `None`.

- [ ] **Step 2: Render optional digest**

Add optional keyword argument:

```python
daily_local_key_signals_digest: RowOneDailyLocalKeySignalsDigest | None = None
```

Render:

```python
daily_local_key_signals_digest_section = _render_daily_local_key_signals_digest(
    daily_local_key_signals_digest
)
```

Place `{daily_local_key_signals_digest_section}` after
`{saved_article_briefs_section}` and before
`{saved_article_content_organization_section}`.

- [ ] **Step 3: Add scoped CSS**

Add `.daily-local-key-signals-digest` styles near Saved Article Briefs / Saved
Article Content Organization styles. Keep the surface compact and editorial,
with signal cards and small support chips.

- [ ] **Step 4: Verify template tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_index_html_includes_daily_local_key_signals_digest -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing integration tests**

Render a small edition with saved local articles and assert:

- `index.html` contains `.daily-local-key-signals-digest`;
- `articles/index.html`, generated detail pages, and
  `articles/<story-id>.html` pages do not contain `.daily-local-key-signals-digest`;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain Stage 357 class names or keys;
- no root, `articles/`, or `data/` artifact/route file is written for
  `daily-local-key-signals-digest`, `local-key-signals-digest`, or
  `daily-key-signals` with `.json` or `.html` extensions.

- [ ] **Step 2: Implement integration**

Import `build_row_one_daily_local_key_signals_digest` in `render.py`.

Inside `render_row_one_site(...)`, build:

```python
daily_local_key_signals_digest = build_row_one_daily_local_key_signals_digest(
    edition,
    local_articles_by_story_id,
)
```

Pass it to `render_index_html(...)` as
`daily_local_key_signals_digest=daily_local_key_signals_digest`.

- [ ] **Step 3: Verify integration tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_key_signals_digest_homepage_only -q
```

Expected: pass.

## Task 4: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write/update docs tests**

Guard that docs mention `Daily Local Key Signals Digest`, homepage-only scope,
and the generated-site-only boundary.

- [ ] **Step 2: Update docs**

Describe Stage 357 as a homepage-only section that aggregates existing Stage
356 local article key signals without changing app contracts, schemas, JSON
artifacts, fetching, extraction, scoring, LLM, scheduling, deployment, or
compliance behavior.

- [ ] **Step 3: Update workflow guards**

Add contract-payload absence checks and forbidden artifact families:

- `daily_local_key_signals_digest`
- `daily_local_key_signals`
- `daily_key_signals`
- `local_key_signals_digest`
- `daily-local-key-signals-digest`
- `daily-local-key-signals`
- `daily-key-signals`
- `local-key-signals-digest`

Add a generated-site-only wrapper that monkeypatches
`_render_daily_local_key_signals_digest` while reusing the existing site
workflow guard.

## Task 5: Review, Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-357-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-357-plan-review.md`
- Add: `docs/reviews/claude-code-stage-357-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-357-code-review.md`

- [ ] **Step 1: Request plan review before coding**

Use `docs/reviews/claude-code-stage-357-plan-review-prompt.md` to ask Claude
Code to inspect the design and plan for scope creep, duplicated surfaces,
render ordering, href safety, and contract/schema changes.

- [ ] **Step 2: Request code review after implementation**

Ask reviewers to inspect the diff for:
- homepage-only scope;
- local article link safety;
- counts computed before caps;
- escaping;
- omission from app payloads and JSON artifacts.

- [ ] **Step 3: Run full gates**

Run:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] **Step 4: Commit and push**

Commit message:

```text
Stage 357: add daily local key signals digest
```

Push with proxy variables cleared if needed:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy git push origin main
```
