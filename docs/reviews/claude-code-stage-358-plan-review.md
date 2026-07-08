Now I have a full picture of the codebase. Here is the review.

---

## Stage 358Plan Review — Daily Local Signal Momentum

### 1. Product fit

Strong. The section directly answers "which local-source labels are most concentrated today?" — the exact signal a daily fashion reader needs to triage what to open first. Surfacing brand/product/theme counts from the current saved set, with direct links to first-class article pages, is a natural complement to the adjacent Stage 357 digest (which shows *what was said*) and the Stage 350 leaderboard on the library page (which shows the full ranked list in depth). No gaps or over-reach found.

---

### 2. Reuse of Stage 350 data / no conflict with Stage 357

Clean. `saved_article_daily_signal_leaderboard` is already built at `render.py:179` in `render_row_one_site`, before `index.html` is written at line 190. Passing it to `render_index_html` costs nothing and touches no builder logic. The Stage 350 model/builder is read-only here; the design explicitly forbids mutating Stage 350 dataclasses unless a test proves a compatibility bug.

No conflict with Stage 357. `RowOneDailyLocalKeySignalsDigest` (357) and `RowOneSavedArticleDailySignalLeaderboard` (350/358) are separate data structures, separate render helpers, and separate CSS class families. The homepage template inserts one after the other without any shared state.

---

### 3. Homepage placement

Technically sound. The current `render_index_html` template (templates.py:356–358) places `{daily_local_key_signals_digest_section}` immediately before `{saved_article_content_organization_section}` already. Inserting the new `{daily_local_signal_momentum_section}` between them is a one-line template change with a clear existing slot. The placement test in Task 1 Step 2 using `str.index(...)` comparisons is the right test for this.

---

### 4. Avoids all forbidden behaviors

Yes. Nothing in the plan adds app contracts, schemas, JSON artifacts, runtime/manifest/sidecar changes, fetching, extraction, scoring, LLM calls, connectors, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior. The workflow guards in Task 4 Step 3 — checking both snake_case and kebab-case variants across all output directories — are thorough. The monkeypatch test approach (mock `_render_daily_local_signal_momentum` to return `""` and run the central guard) is correct and consistent with how earlier stage boundaries are enforced.

---

### 5. Safe detail-path-to-local-article href mapping

Sound conceptually, but **the plan has a double-call inefficiency that could be refined before implementation.**

Looking at `render_row_one_site` (render.py:120–249):
- `index.html` is written at line 190.
- `_write_local_article_pages` is called later inside `_write_saved_article_library_page` (line 211).
- `_write_local_article_pages` already builds `hrefs_by_detail_path` inline at lines 373–376 via `_local_article_page_specs`.

The plan says:

> Add `_local_article_page_hrefs_by_detail_path(edition, local_articles_by_story_id)` as a pure helper, call it before writing `index.html`, and update `_write_local_article_pages` to call the same helper instead of duplicating the dict comprehension.

This means `_local_article_page_specs` runs twice: once for `render_index_html`, and once when `_write_local_article_pages` internally calls the new helper. Both calls use identical inputs, so there is no correctness risk — but it's unnecessary work and leaves the two copies loosely coupled.

**Correction:** Compute the mapping once in `render_row_one_site`, then pass it into `_write_local_article_pages` as a new keyword argument:

```python
# in render_row_one_site, before writing index.html:
local_article_page_hrefs = _local_article_page_hrefs_by_detail_path(
    edition, local_articles_by_story_id
)
index_path.write_text(
    render_index_html(
        ...
        daily_local_signal_momentum=saved_article_daily_signal_leaderboard,
        daily_local_signal_momentum_hrefs_by_detail_path=local_article_page_hrefs,
    ),
    ...
)
# then, inside _write_saved_article_library_page → _write_local_article_pages:
# accept hrefs_by_detail_path as a parameter instead of rebuilding it
```

Update `_write_local_article_pages` signature to accept an optional `hrefs_by_detail_path: dict[str, str] | None = None` and fall back to computing it internally only when not provided. This eliminates the double computation without breaking the existing call site in the library page writer.

---

### 6. Template href validation and tests

The validation rules are correct and well-specified. The test cases in Task 1 Step 1 cover the important attack surfaces: `javascript:` scheme, traversal (`../`), wrong fragment (`#summary` instead of `#local-article-digest`), unsafe mapping values with leading `.` or nested `/`.

**One missing test case:** the valid fallback path. The plan tests that unsafe supports do not render, and that the primary mapping-based href renders correctly — but there is no test asserting that when a support's `detail_path` is absent from the mapping (but the support carries a valid `details/<safe>.html#local-article-digest` href), the fallback detail href renders. Add one support fixture where `detail_path` is not in the `hrefs_by_detail_path` dict and assert that `href="details/the-row-signal-fallback.html#local-article-digest"` appears in the output.

---

### 7. Concrete corrections before implementation

**Required:**

1. **Compute href mapping once, not twice.** Refactor Task 3 Step 2 so `render_row_one_site` computes `_local_article_page_hrefs_by_detail_path` once and passes the result to both `render_index_html` and (as a new keyword argument) `_write_local_article_pages`, rather than having `_write_local_article_pages` independently call the helper. This keeps the two callers synchronized by construction.

2. **Add fallback href test.** In Task 1 Step 1, add a support fixture with no matching mapping entry and a valid `details/...#local-article-digest` href. Assert the fallback detail href renders. Without this, the fallback branch in `_safe_daily_local_signal_momentum_detail_href` goes untested at the direct render level.

**Advisory (pre-existing, no Stage 358 action needed but worth noting):**

- `build_row_one_saved_article_daily_signal_leaderboard` has no direct unit test coverage per the codegraph blast-radius report. Stage 358 adds a second consumer on `index.html`. If the leaderboard builder is already trusted as an integration-tested path, no change needed — but it is a coverage gap if you want to isolate leaderboard-builder bugs from render bugs.

---

**Overall verdict:** The design and plan are correct in scope, placement, and data reuse. Two targeted corrections — coalescing the href mapping computation into a single call site, and adding the fallback href test case — should be made before implementation begins. No other blocking issues.
