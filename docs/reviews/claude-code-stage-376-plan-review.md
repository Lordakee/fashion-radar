Here are my findings, ordered by severity.

---

## Critical

**C1 — `section_key="runway"` is not a valid `RowOneSectionKey` (plan Task 2, Step 1 fixture)**

`RowOneSectionKey = Literal["top_stories", "brand_moves", "celebrity_style", "hot_products", "rising_radar"]` (`models.py:10`). `RowOneStory` uses `ConfigDict(extra="forbid")`. Constructing `RowOneStory(section_key="runway",...)` raises a Pydantic `ValidationError` at fixture-build time. Every builder test in `test_row_one_daily_local_news_timeline.py` fails before reaching any assertion — in RED, in GREEN, and in focused verification. Existing tests use `section_key="top_stories"` (e.g., `test_row_one_render.py:233`). Fix: change to any valid value such as `"top_stories"`.

**C2 — `story_type="trend"` is not a valid `RowOneStoryType` (plan Task 2, Step 1 fixture)**

`RowOneStoryType = Literal["tracked_entity", "candidate_signal", "recent_item"]` (`models.py:18`). Same failure mode as C1. Existing tests use `story_type="tracked_entity"` (e.g., `test_row_one_render.py:234`). Fix: change to `"tracked_entity"`.

Both C1 and C2 mean the RED-phase test fails with a Pydantic error, not the expected `ImportError`. After the builder module lands, the GREEN-phase tests still fail, so the plan's RED→GREEN cycle never closes.

---

## Important

**I1 — Builder `_safe_article_page_href` is missing the `"://" in href` guard**

Every analogous builder in the codebase checks both `"://" in href` and `"//" in href` before proceeding (`daily_local_saved_article_organizer.py:487`, `daily_local_reading_itinerary.py` pattern). The plan's proposed implementation (Task 3, Step 3) checks only `href.startswith((".", "/", "//"))`. An href like `"http://example.com/story-id.html"` does not start with `.`, `/`, or `//`, so it passes this guard. It is ultimately caught by the `len(path.parts) != 1` check via `PurePosixPath`, but the defense is shallower than every peer builder and would fail a code-consistency review. The fix is one additional predicate: `if "://" in href or "//" in href or href.startswith(...)`.

**I2 — Generated-site-only guard patches the builder, not the renderer — weaker than all analogous guards**

Stages 371, 372 (and most others) patch the template renderer to return `""`:
```python
monkeypatch.setattr(row_one_templates, "_render_daily_local_reading_itinerary", lambda _: "",...)
```
This proves that even when the builder returns a live model, the renderer produces no HTML section and creates no artifact.

The plan's Stage 376 guard (Task 6, Step 1) patches `row_one_render.build_row_one_daily_local_news_timeline` to return `None`. This only tests the builder-returns-`None` path. It does not verify that a live `RowOneDailyLocalNewsTimeline` flowing through `_render_daily_local_news_timeline` produces no JSON artifact — the core claim of a generated-site-only guard. The fix: patch `row_one_templates._render_daily_local_news_timeline` (the renderer), consistent with stages 371–372.

**I3 — `_first_paragraph` return shape diverges from the spec's bilingual excerpt rule without a concrete bridge**

The plan's builder sketch (Task 3, Step 2) calls `_first_paragraph(article)` and destructures it as `paragraph_index, excerpt` — a 2-tuple where `excerpt` is already a `LocalizedText`. The spec requires: "If aligned `paragraphs_zh` is available for the same paragraph index, it supplies the Chinese excerpt; otherwise the English excerpt is reused." The plan's Task 3, Step 3 says only "Also implement `_first_paragraph`, `_excerpt`, `_title`, `_source_name`, and `_published_label` using the design rules" without specifying any of these signatures or the `paragraphs_zh` alignment check. The analogous function in `daily_local_saved_article_organizer.py:347` returns a 3-tuple `(index, paragraph_en, paragraph_zh)`, which keeps the index and both language values separate for downstream use.

The gap: nothing in the plan specifies how `_first_paragraph` returns a `LocalizedText` excerpt, what the alignment logic looks like, or how the paragraph index for the anchor is preserved while building the excerpt. An implementer following the plan literally may either produce an incorrect anchor or miss the bilingual fallback. The spec should specify these two helpers explicitly, or the plan should reference the `daily_local_saved_article_organizer` implementation as the model.

---

## Minor

**M1 — `_esc` and `_count_label` are module-scope functions in `templates.py`, but the plan does not note this**

Both are confirmed at `templates.py:18735` and `templates.py:14943`. The plan uses them without import notes. Because they are already in `templates.py` and the new code is also in `templates.py`, they are in scope without additional imports. No code change required, but the plan would be clearer if it noted "use existing `_esc` and `_count_label` helpers."

**M2 — Template unsafe-href test list omits `javascript:` URIs with `.html` suffixes**

The existing test list covers the standard attack vectors (absolute, protocol-relative, path-traversal, space, missing/empty fragment, `N=0`). A `"articles/javascript:void(0).html#local-article-paragraph-1"` input is not listed. The `safe_local_article_story_id` check catches it (`:`, `(`, `)` fail the regex), but including it makes the test surface explicit and consistent with security-focused test suites in the codebase.

**M3 — Render test fixture imports `datetime` and `UTC` without confirming they are already imported in `test_row_one_render.py`**

The `_daily_local_news_timeline_fixture` uses `datetime(2026, 7, 10, 8, 30, tzinfo=UTC)`. Existing imports in that test file include `from datetime import UTC, datetime` (confirmed by Stage 370/371/372 fixture blocks), so no new import is needed. Worth noting in the plan to avoid a red herring import error during development.

**M4 — Denylist tokens in Task 6 Step 1 include `"每日本地新闻时间线"` but not the Chinese artifact path equivalent**

All hyphenated/underscored tokens are listed. The Chinese token tests string presence in JSON payloads. This is consistent with how prior stages handle Chinese denylist entries and presents no functional gap — just worth confirming the denylist test iterates JSON payloads (not only filenames), which the existing pattern does.
