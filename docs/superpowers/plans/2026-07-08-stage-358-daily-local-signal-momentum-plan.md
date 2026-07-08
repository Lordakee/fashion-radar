# Stage 358 Daily Local Signal Momentum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage momentum panel that surfaces the
current day's strongest saved local brands, products, and themes from existing
Stage 350 leaderboard data.

**Architecture:** Reuse the existing
`RowOneSavedArticleDailySignalLeaderboard` model and builder. Add a homepage
renderer in `templates.py`, pass the existing leaderboard into
`render_index_html(...)`, and compute a pure safe detail-path-to-local-article
href mapping in `render.py` before writing `index.html`. Keep the feature HTML
only: no app contract, schema, runtime, manifest, sidecar, route-family, or JSON
artifact changes.

**Tech Stack:** Python 3, dataclasses already present in Stage 350, existing ROW
ONE render pipeline, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/render.py`
  - Build the existing saved article daily signal leaderboard before
    `render_index_html(...)`.
  - Add a pure helper that computes safe first-class local article page hrefs by
    detail path without writing files.
  - Pass the leaderboard and local article href mapping to the homepage renderer.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept optional `daily_local_signal_momentum` and
    `daily_local_signal_momentum_hrefs_by_detail_path`.
  - Render `_render_daily_local_signal_momentum(...)`.
  - Add defensive href validation and scoped CSS for `.daily-local-signal-momentum`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for escaping, href safety, placement, CSS, and
    homepage-only site generation.
- Modify `tests/test_workflows.py`
  - Add contract payload absence checks, forbidden artifact checks, and a
    generated-site-only wrapper.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 358 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Homepage Momentum Rendering Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing direct render test**

Add `test_render_index_html_includes_daily_local_signal_momentum` near the
Stage 357 digest template tests. Build a hand-written
`RowOneSavedArticleDailySignalLeaderboard` with one brands bucket, one products
bucket, one themes bucket, and supports that include:

```python
RowOneSavedArticleDailySignalLeaderboardSupport(
    title=LocalizedText(en="The Row source <script>", zh="The Row 来源 <script>"),
    source_name="Vogue <Business>",
    href="details/the-row-signal-1234567890.html#local-article-digest",
    detail_path="details/the-row-signal-1234567890.html",
)
```

Pass:

```python
daily_local_signal_momentum=leaderboard,
daily_local_signal_momentum_hrefs_by_detail_path={
    "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
},
```

Assert:
- `class="daily-local-signal-momentum"` renders;
- `Daily Local Signal Momentum` and `每日本地信号动量` render;
- brand/product/theme labels render;
- article/source count text renders;
- escaped display text appears and raw `<script>` / `<Business>` does not;
- `href="articles/the-row-signal-1234567890.html#local-article-digest"` renders.

Also include a valid fallback support whose `detail_path` is not present in
`daily_local_signal_momentum_hrefs_by_detail_path`, but whose support `href` is
`details/the-row-signal-fallback-1234567890.html#local-article-digest`. Assert
`href="details/the-row-signal-fallback-1234567890.html#local-article-digest"`
renders.

Also include unsafe supports and assert these do not render:
- `javascript:alert(1)`;
- `../details/the-row-signal-1234567890.html#local-article-digest`;
- `details/the-row-signal-1234567890.html#summary`;
- unsafe mapping value `../secret.html`;
- unsafe mapping value `unsafe/story.html`.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_index_html_includes_daily_local_signal_momentum -q
```

Expected: fail because `render_index_html(...)` does not accept the new
arguments.

- [ ] **Step 2: Write failing placement test**

Add `test_render_index_html_places_daily_local_signal_momentum_between_sections`.
Use small fixtures for saved article briefs, Stage 357 digest, Stage 358
leaderboard, and saved article content organization. Assert:

```python
assert html.index('class="daily-local-key-signals-digest"') < html.index(
    'class="daily-local-signal-momentum"'
)
assert html.index('class="daily-local-signal-momentum"') < html.index(
    'class="saved-article-content-organization"'
)
```

Run the new test and expect the same missing-argument failure.

## Task 2: Template Implementation and CSS

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add optional render arguments**

Update `render_index_html(...)`:

```python
daily_local_signal_momentum: RowOneSavedArticleDailySignalLeaderboard | None = None,
daily_local_signal_momentum_hrefs_by_detail_path: Mapping[str, str] | None = None,
```

Compute:

```python
daily_local_signal_momentum_section = _render_daily_local_signal_momentum(
    daily_local_signal_momentum,
    local_article_page_hrefs_by_detail_path=daily_local_signal_momentum_hrefs_by_detail_path,
)
```

Insert it between:

```html
{daily_local_key_signals_digest_section}
{saved_article_content_organization_section}
```

- [ ] **Step 2: Add homepage renderer helpers**

Add helpers near the Stage 357 digest renderer:

```python
def _render_daily_local_signal_momentum(
    leaderboard: RowOneSavedArticleDailySignalLeaderboard | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    ...
```

Also add:

- `_render_daily_local_signal_momentum_bucket(...)`
- `_render_daily_local_signal_momentum_item(...)`
- `_render_daily_local_signal_momentum_support(...)`
- `_daily_local_signal_momentum_support_href(...)`
- `_safe_daily_local_signal_momentum_detail_href(...)`

Href rules:
- Prefer mapping values that are exactly one safe local article page filename,
  then render `articles/<story-id>.html#local-article-digest`.
- Reject mapping values with whitespace, leading `.`, leading `/`, nested `/`,
  or unsafe story IDs.
- Fallback accepts only `details/<safe-detail>.html#local-article-digest`, then
  renders that safe detail href.
- Reject external schemes, traversal, and wrong fragments.

- [ ] **Step 3: Add scoped CSS**

Add selectors:

- `.daily-local-signal-momentum`
- `.daily-local-signal-momentum-header`
- `.daily-local-signal-momentum-metrics`
- `.daily-local-signal-momentum-grid`
- `.daily-local-signal-momentum-bucket`
- `.daily-local-signal-momentum-item`
- `.daily-local-signal-momentum-label`
- `.daily-local-signal-momentum-supports`
- `.daily-local-signal-momentum-support`

Add mobile grid fallback in the existing responsive block.

- [ ] **Step 4: Verify direct render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_signal_momentum \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_signal_momentum_between_sections \
  -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing site integration test**

Add `test_render_row_one_site_writes_daily_local_signal_momentum_homepage_only`
after the Stage 357 homepage-only test. Render a small edition with
`_signal_briefing_local_article()` and assert:

- `index.html` contains `class="daily-local-signal-momentum"`;
- `index.html` contains `Daily Local Signal Momentum`;
- support links prefer
  `href="articles/the-row-signal-1234567890.html#local-article-digest"`;
- `articles/index.html`, generated detail pages, and
  `articles/<story-id>.html` pages do not contain
  `.daily-local-signal-momentum`;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain `daily_local_signal_momentum`, `daily-local-signal-momentum`, or
  `Daily Local Signal Momentum`;
- no root, `articles/`, or `data/` artifact/route file exists for
  `daily-local-signal-momentum`, `daily-local-momentum`, or
  `signal-momentum` with `.json` or `.html` extensions.

Run the test and expect failure because integration is not wired.

- [ ] **Step 2: Implement safe local article page href mapping**

Add a pure helper in `render.py` near `_write_local_article_pages(...)`:

```python
def _local_article_page_hrefs_by_detail_path(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> dict[str, str]:
    return {
        detail_path: article_page_href
        for story, _article, article_page_href, detail_path in _local_article_page_specs(
            edition,
            local_articles_by_story_id=local_articles_by_story_id,
        )
    }
```

Use it in `render_row_one_site(...)` before writing `index.html` and pass it to
`render_index_html(...)`:

```python
local_article_page_hrefs_by_detail_path = _local_article_page_hrefs_by_detail_path(
    edition,
    local_articles_by_story_id,
)
...
daily_local_signal_momentum=saved_article_daily_signal_leaderboard,
daily_local_signal_momentum_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
```

Pass the same mapping through `_write_saved_article_library_page(...)` into
`_write_local_article_pages(...)` as a new optional keyword argument so the
mapping is computed once in `render_row_one_site(...)` and reused by both the
homepage and article-library writers:

```python
_write_saved_article_library_page(
    ...,
    local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
)
```

Update `_write_local_article_pages(...)` to accept
`local_article_page_hrefs_by_detail_path: Mapping[str, str] | None = None` and
fall back to `_local_article_page_hrefs_by_detail_path(...)` only when the
mapping is absent. This preserves existing direct/internal call behavior while
avoiding duplicate `_local_article_page_specs(...)` work in the normal
`render_row_one_site(...)` flow.

- [ ] **Step 3: Verify site integration passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_signal_momentum_homepage_only \
  -q
```

Expected: pass.

## Task 4: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add docs test**

Add `test_row_one_docs_describe_stage_358_daily_local_signal_momentum_boundary`
before Stage 357. Assert the Stage 358 paragraph appears in both docs, appears
before Stage 357, and rejects stale phrases:

- `historical trend`
- `time-series`
- `creates data/daily-local-signal-momentum.json`
- `row-one-app/v8`
- `adds fetching`
- `adds scoring`
- `adds llm`
- `adds compliance review`

- [ ] **Step 2: Update docs**

Insert a Stage 358 paragraph immediately before Stage 357 in `README.md` and
`docs/row-one.md`. It must say:

- generated-site only;
- homepage-only section inside `index.html`;
- after Daily Local Key Signals Digest and before Saved Article Content
  Organization;
- reuses Stage 350 Saved Article Daily Signal Leaderboard data;
- current-edition support counts only, not historical trend deltas;
- no app contracts, schemas, JSON artifacts, fetching, scoring, LLM, connector,
  scheduling, deployment, analytics, personalization, recommendation, or
  compliance-review behavior.

- [ ] **Step 3: Update workflow guards**

In `tests/test_workflows.py`, add generated contract payload absence checks for:

- `daily_local_signal_momentum`
- `daily_local_momentum`
- `signal_momentum`
- `Daily Local Signal Momentum`
- `daily-local-signal-momentum`
- `daily-local-momentum`
- `signal-momentum`

Add forbidden artifact checks under root, `articles/`, and `data/` for `.json`
and `.html` stems:

- `daily-local-signal-momentum`
- `daily-local-momentum`
- `signal-momentum`
- `daily_local_signal_momentum`
- `daily_local_momentum`
- `signal_momentum`

Add `test_stage_358_daily_local_signal_momentum_stays_generated_site_only(...)`
near the stage wrappers. Monkeypatch
`row_one_templates._render_daily_local_signal_momentum` to return `""`, then
call the central workflow guard.

- [ ] **Step 4: Verify docs/workflow tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_358_daily_local_signal_momentum_boundary \
  tests/test_workflows.py::test_stage_358_daily_local_signal_momentum_stays_generated_site_only \
  -q
```

Expected: pass.

## Task 5: Review, Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-358-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-358-plan-review.md`
- Add: `docs/reviews/claude-code-stage-358-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-358-code-review.md`

- [ ] **Step 1: Request Claude Code plan review before coding**

Ask Claude Code to review the Stage 358 design and plan for scope creep,
duplication with Stage 350/357, render ordering, href safety, and contract
changes.

- [ ] **Step 2: Request code review after implementation**

Ask reviewers to inspect:
- homepage-only scope;
- no JSON/app/schema/runtime/manifest/sidecar changes;
- reuse of Stage 350 model without mutating it;
- support href safety;
- escaping;
- tests/docs/workflow guard coverage.

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
Stage 358: add daily local signal momentum
```

Push:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy git push origin main
```
