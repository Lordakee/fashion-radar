# Stage 356 Saved Article Key Signals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional generated-site-only `Saved Article Key Signals`
section to each saved local article page so readers can see why the article
matters, which brands/products/people are present, and which existing themes
structure the article before reading the full saved text.

**Architecture:** Build a focused in-memory view model from existing
`RowOneStory` and `RowOneLocalArticle` fields. Pass that view model into
`render_local_article_page_html()` and render it after the Stage 355 section
binder and before the existing local article body. Keep the feature HTML-only
and avoid app contract, schema, runtime, manifest, sidecar, route-family, or
generated JSON artifact changes.

**Tech Stack:** Python 3, dataclasses, existing ROW ONE render pipeline,
pytest, ruff.

## File Map

- Create `src/fashion_radar/row_one/saved_article_key_signals.py`
  - Owns the new view model and builder.
  - Selects Why It Matters, Brands, Products, People, and Themes from existing
    local article and story fields.
  - Uses `row_one_saved_article_reference_bucket(...)` for reference buckets.
  - Filters paragraph indices and creates renderer-owned same-page fragment
    hrefs.
- Modify `src/fashion_radar/row_one/render.py`
  - Build key signals for each eligible generated local article page.
  - Pass key signals into `render_local_article_page_html()`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept optional key-signals object in `render_local_article_page_html()`.
  - Render `_render_saved_article_key_signals(...)`.
  - Add scoped CSS for `.saved-article-key-signals`.
- Create `tests/test_row_one_saved_article_key_signals.py`
  - Unit coverage for builder behavior.
- Modify `tests/test_row_one_render.py`
  - Template and generated-site integration coverage.
- Modify `tests/test_row_one_docs.py`, `tests/test_workflows.py`,
  `README.md`, and `docs/row-one.md`
  - Guard and document the generated-site-only boundary.
- Add review prompts under `docs/reviews/`
  - Keep plan and code review artifacts for the node.

## Task 1: Builder Test and Model

**Files:**
- Create: `tests/test_row_one_saved_article_key_signals.py`
- Create: `src/fashion_radar/row_one/saved_article_key_signals.py`

- [ ] **Step 1: Write failing builder tests**

Cover:
- article/story id mismatch returns `None`;
- unsafe story ids return `None`;
- `Why It Matters` uses `local_article.brief_sections[key="why_it_matters"]`
  before `story.why_it_matters`;
- `Why It Matters` story fallback is allowed only when the local article has at
  least one nonblank saved paragraph;
- `Why It Matters` does not invent paragraph evidence when the source is a brief
  section or `story.why_it_matters`;
- `Brands`, `Products`, and `People` use only existing references bucketed by
  `row_one_saved_article_reference_bucket(...)`;
- `Brands`, `Products`, and `People` skip blank reference names and dedupe by
  normalized displayed name in first-seen order;
- `Brands`, `Products`, and `People` attach a readable support statement from
  the first supporting content item body, item label, or section title when one
  exists, and do not become a pure link directory;
- `Themes` uses only existing content section titles and item labels as
  displayed labels, with no raw section-key display and no inferred labels;
- `Themes` skips labels that duplicate displayed brand, product, or people
  reference names;
- paragraph indices reject bools, negatives, duplicates, blanks, and
  out-of-range values;
- paragraph anchors use one-based `#local-article-paragraph-N` fragments;
- `paragraphs_zh` is used only when aligned with `paragraphs` and nonblank at
  the same index;
- statements and evidence excerpts are truncated;
- raw section keys alone do not make the builder return a non-`None` result;
- empty articles return `None`.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_key_signals.py -q
```

Expected: fail because the module/function does not exist.

- [ ] **Step 2: Implement minimal builder**

Add frozen dataclasses:

- `RowOneSavedArticleKeySignalEvidence`
- `RowOneSavedArticleKeySignalReference`
- `RowOneSavedArticleKeySignalGroup`
- `RowOneSavedArticleKeySignals`

Add:

```python
def build_row_one_saved_article_key_signals(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleKeySignals | None:
    ...
```

Implementation requirements:
- call `safe_local_article_story_id(story.id)`;
- require `story.id == local_article.story_id`;
- build groups with keys `why_it_matters`, `brands`, `products`, `people`, and
  `themes`;
- use the explicit mapping from the design spec;
- preserve existing section, item, and reference order;
- skip blank reference names;
- dedupe references within each group by normalized displayed name while
  preserving first-seen support metadata;
- dedupe and cap theme labels;
- use section keys for support classification/anchors only, not raw display
  labels;
- keep paragraph evidence optional for `why_it_matters` and only attach evidence
  from validated content-section item paragraph indices;
- generate only `#local-article-paragraph-N` and
  `#local-article-content-section-N` hrefs;
- return `None` when no meaningful groups can be built. A meaningful group has
  at least one nonblank display statement, nonblank display reference name,
  nonblank display theme label, or validated paragraph/content-section support
  row; a raw section key alone is not meaningful.

- [ ] **Step 3: Verify builder tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_key_signals.py -q
```

Expected: pass.

## Task 2: Template Rendering

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing template tests**

Add tests that call `render_local_article_page_html(...)` directly with a
key-signals fixture and assert:

- section title `Saved Article Key Signals`;
- Why It Matters statement, readable support statement, reference text, theme
  text, and evidence excerpt render;
- same-page fragment hrefs render;
- the section appears after `.saved-article-local-section-binder` when the
  binder is present and before `id="local-article"`;
- the section still renders before `id="local-article"` when the binder is
  absent;
- HTML escaping works for labels, statements, references, themes, and excerpts;
- unsafe evidence hrefs do not render;
- the section is omitted when the key-signals argument is `None`.

Run the targeted test and verify failure before implementation.

- [ ] **Step 2: Render optional key signals**

Add optional keyword argument:

```python
saved_article_key_signals: RowOneSavedArticleKeySignals | None = None
```

Render:

```python
key_signals = _render_saved_article_key_signals(saved_article_key_signals)
```

Place `{key_signals}` after `{local_section_binder}` and before
`{local_article_section}`.

- [ ] **Step 3: Add scoped CSS**

Add `.saved-article-key-signals` styles near the Stage 355 binder CSS. Keep the
visual treatment distinct from the binder by emphasizing compact readable
signals and chips rather than another navigation index.

- [ ] **Step 4: Verify targeted render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_local_article_page_includes_saved_article_key_signals -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing integration tests**

Render a small edition with a saved local article and assert:

- `articles/<story-id>.html` contains `.saved-article-key-signals`;
- `index.html` does not contain `.saved-article-key-signals`;
- the section is absent from `articles/index.html`;
- the section is absent from generated detail pages;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain Stage 356 class names or keys;
- no root, `articles/`, or `data/` artifact/route file is written for
  `saved-article-key-signals`, `article-key-signals`,
  `local-article-key-signals`, `key-signals`, or `local-key-signals` with
  `.json` or `.html` extensions.

- [ ] **Step 2: Implement integration**

Import `build_row_one_saved_article_key_signals` in `render.py`.

Inside `_write_local_article_pages(...)`, build:

```python
key_signals = build_row_one_saved_article_key_signals(
    story=story,
    local_article=article,
)
```

Pass it to `render_local_article_page_html(...)` as
`saved_article_key_signals=key_signals`.

- [ ] **Step 3: Verify integration tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_write_row_one_site_files_writes_key_signals_only_on_local_article_pages -q
```

Expected: pass.

## Task 4: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write/update docs tests**

Guard that docs mention `Saved Article Key Signals` and the generated-site-only
boundary.

- [ ] **Step 2: Update docs**

Describe Stage 356 as a local article page section that organizes existing
local article brief sections, `RowOneStory.why_it_matters` only as the Why It
Matters fallback, reference buckets, theme labels, and
paragraph/content-section anchors into readable signals without changing app
contracts, schemas, JSON artifacts, fetching, extraction, scoring, LLM,
scheduling, deployment, or compliance behavior. Also state that it does not
alter Stage 319 detail `Signal Briefing`, Stage 349 `Saved Article Signal
Facets`, Stage 350 `Saved Article Daily Signal Leaderboard`,
`articles/index.html`, the homepage, or generated data payloads.

- [ ] **Step 3: Update workflow guard**

Add builder/helper names and forbidden artifact families:

- `saved_article_key_signals`
- `article_key_signals`
- `local_article_key_signals`
- `saved-article-key-signals`
- `article-key-signals`
- `local-article-key-signals`
- `key-signals`
- `local-key-signals`

Add a Stage-356-doc-only stale-name guard for these retired names:

- `Saved Article Local Signal Brief`
- `saved_article_local_signal_brief`
- `saved-article-local-signal-brief`
- `local-signal-brief`

Do not add a broad `signal_brief` or `Signal Briefing` guard because Stage 319
already owns a valid generated detail-page signal briefing surface.

## Task 5: Review, Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-356-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-356-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-356-code-review.md`

- [ ] **Step 1: Request plan review before coding**

Use `docs/reviews/claude-code-stage-356-plan-review-prompt.md` to ask Claude
Code to inspect the design and plan for scope creep, duplication with Stage
355, paragraph index handling, render order, fallback mapping, and
contract/schema changes.

- [ ] **Step 2: Request code review after implementation**

Ask a reviewer to inspect the diff for:
- generated-site-only scope;
- same-page fragment safety;
- statement/excerpt truncation;
- one-based paragraph anchor rendering from zero-based indices;
- reference bucketing with `row_one_saved_article_reference_bucket(...)`;
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

```text
Stage 356: add saved article key signals
```

Push with proxy variables cleared if needed:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy git push origin main
```
