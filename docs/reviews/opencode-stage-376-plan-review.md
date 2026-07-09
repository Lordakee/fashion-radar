# Stage 376 Daily Local News Timeline — opencode Plan Review

All five original Claude Code findings are verified resolved in the current spec/plan:
- **C1/C2** — plan Task 2 Step 1 fixture now uses `section_key="top_stories"` (plan:139) and `story_type="tracked_entity"` (plan:140); both are valid per `models.py:10,19`.
- **I1** — `_safe_article_page_href` now checks `"://" in href or "//" in href` before the `startswith` guard (plan:344), matching peers.
- **I2** — generated-site-only guard now patches `row_one_templates._render_daily_local_news_timeline` (plan:673-680), consistent with stages 370-372 (`test_workflows.py:1509,1524,1539`).
- **I3** — `_first_paragraph`/`_localized_excerpt` contracts are explicit in both spec (spec:120-138) and plan (plan:364-386), including `paragraphs_zh` length-alignment and index preservation for the anchor.

## Critical

**C1 — Render test invocation references a non-existent fixture and a non-existent `render_index_html` parameter (plan Task 4, Step 2)**

The proposed render test calls:
```python
html = render_index_html(
    _edition(),
    daily_local_theme_summary_strip=_daily_local_theme_summary_strip_fixture(),
    daily_local_news_timeline=_daily_local_news_timeline_fixture(),
    daily_local_article_intelligence_brief=_daily_local_article_intelligence_brief_fixture(),
)
```
Two independent defects, both fatal regardless of timeline implementation:

1. `_daily_local_theme_summary_strip_fixture()` does not exist in `tests/test_row_one_render.py`. Only `_daily_local_article_intelligence_brief_fixture` (`:14510`) and `_daily_local_reading_itinerary_fixture` (`:14688`) exist. Result: `NameError` at collection/run time.
2. `daily_local_theme_summary_strip=` is not a parameter of `render_index_html`. The theme strip is fed by `daily_local_theme_summary_strip_hrefs_by_detail_path=` (`templates.py:456,458` show the real signatures; all six existing call sites use the `_hrefs_by_detail_path` form, e.g. `test_row_one_render.py:14781`). Result: `TypeError: unexpected keyword argument`.

This is the same defect class as the original C1/C2: the RED test fails for the wrong reason, and the GREEN test still fails, so the Task 4 RED→GREEN cycle cannot close. Secondary effect: even after those two are fixed, the placement assertion `html.index('class="daily-local-theme-summary-strip"')` will raise `ValueError: substring not found` unless the strip actually renders, which requires passing a valid `daily_local_theme_summary_strip_hrefs_by_detail_path` mapping (mirror `test_row_one_render.py:14781`). Fix: drop the bogus fixture/parameter, pass `daily_local_theme_summary_strip_hrefs_by_detail_path={...}` so the strip renders, and confirm the wrapper class literal against `_render_daily_local_theme_summary_strip` (`templates.py:12771`).

## Important

**I1 — `clean_row_one_text` is imported but never used by any specified helper (plan Task 3, Step 1)**

The builder import block pulls `clean_row_one_text, normalize_row_one_paragraph` (plan:244), but every helper the plan actually specifies uses only `normalize_row_one_paragraph` (`_first_paragraph` at plan:369,374; `_localized_excerpt` at plan:382). The remaining helpers (`_title`, `_source_name`, `_published_label`) are governed by the design's Text Rules, which reference no cleaning step. `clean_row_one_text` is therefore a stray import → ruff `F401`, which fails the release gate in Task 8 Step 3 and Task 9 Step 4 (`ruff check .`). Fix: drop `clean_row_one_text` from the import, or specify where it is used.

## Minor

**M1 — Builder `_published_label` should mirror the existing in-codebase date format exactly**

`templates.py:18585` already defines `_published_label(story)` producing `en` = `"%b %d, %Y"` and `zh` = `"%Y-%m-%d"`, and `:16830` uses the same `%b %d, %Y` form. The plan's builder-side `_published_label(published_at: datetime)` must produce byte-identical output because the tests assert exact strings (`latest_label.en == "Jul 10, 2026"`, `.zh == "2026-07-10"`). The spec fixes the format (spec:143-146); just confirm the implementer uses the same `strftime` tokens and does not introduce locale-dependent variation.

**M2 — Renderer anchor validator: confirm `paragraph-N` edge cases beyond `N=0`**

The unsafe-href list (plan:464-477) covers `paragraph-0`, traversal, external, whitespace, and `javascript:` — good. Consider also listing `paragraph-` (empty N), `paragraph-01`/`paragraph-1x` (non-integer) to make the `N >= 1` integer contract (plan:582) explicit at the test surface, matching the strictness of the route-safety tests in peer renderers.

**M3 — `source_count` casefold semantics are unspecified in the design**

The builder sketch computes `len({item.source_name.casefold() for item in items ...})` (plan:318), i.e. case-insensitive distinct sources, but the design only says "source_count". The builder test asserts `source_count == 2` for two distinct sources, which passes either way. Worth one line in the design so the case-insensitive distinct-source rule is intentional rather than incidental.

## Affirmative coverage of requested axes

- **Feasibility**: Sound. Pure builder; integration point in `render.py` confirmed — `local_article_page_hrefs_by_story_id` is computed at `:207-209`, before the sibling daily-local builders, so the timeline build slots in cleanly before the `render_index_html(...)` call at `:228`. All required model fields exist (`RowOneStory.published_at`, `RowOneLocalArticle.published_at/paragraphs/paragraphs_zh/source_name/title`).
- **Route safety**: Adequate. `_safe_article_page_href` (plan:339-358) rejects protocol, protocol-relative, absolute, traversal, whitespace, multi-part, non-`.html`, story-id mismatch, and unsafe ids; renderer-side `_safe_daily_local_news_timeline_href` is specified to re-validate `articles/<safe-story-id>.html#local-article-paragraph-N` with `N >= 1`. Defense-in-depth (builder + renderer) matches peer stages.
- **Date ordering**: Correct. Sort key `(-published_at.timestamp(), story_index, story_id)` (plan:314) yields newest-first with edition-order then story-id tie-breaks, exactly as specified (spec:90-95). `published_at` is always `datetime` after the `mode="before"` validators (`models.py:151-154,208-211`), so `.timestamp()` is safe; `parse_datetime_utc` yields tz-aware values, avoiding naive-local ambiguity.
- **Generated-site-only boundaries**: Solid. Boundary paragraph (spec:171-196, plan:694-696) is exhaustive; denylist tokens (plan:654-664) match the existing mechanism (`test_workflows.py:671-701,1302-1305`); the renderer-patch guard proves no JSON/artifact leakage and homepage-only rendering. App/manifest/runtime/schema contracts untouched.
- **Test coverage**: Comprehensive across builder (ordering, tie-breaks, published_at preference, paragraph anchoring, filtering, cap, None) and render/docs/workflow — contingent on fixing C1.
- **Docs boundaries**: The exact Stage 376 boundary paragraph and "before Stage 375 in both README and docs/row-one.md" assertion are well-defined (plan:690-698).
- **Duplication**: None. The chronological newest-first, 6-item, first-paragraph-anchor shape is distinct from the theme strip (theme), article intelligence brief (brand/product/heat lanes), saved article organizer, and reading itinerary (sequence). It shares the `articles/<story-id>.html#local-article-paragraph-N` routing and saved-paragraph infrastructure by design, which is reuse, not duplication.
