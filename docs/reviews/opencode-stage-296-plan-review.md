# opencode Stage 296 Plan Review

**Reviewer:** opencode (GLM 5.2, max variant) — fallback, Claude Code plan review unavailable
**Plan:** `docs/superpowers/plans/2026-07-05-stage-296-row-one-unique-detail-pages-plan.md`
**Verdict:** APPROVE — no Critical or Important findings; implementation may proceed after addressing the Minor notes below.

## Findings

### Critical
None.

### Important
None.

### Minor / Notes (non-blocking)

**M1 — Final post-`max_stories` guard is redundant (clarity, not correctness).**
The plan adds `stories = _unique_stories_by_id(stories)` after the `max_stories` slice (plan line 166). Because `story.id` is derived from `sha1("{section_key}|{title}|{discriminator}")` at `src/fashion_radar/row_one/edition.py:522-525`, two stories in *different* sections can never collide on `id` (or on `detail_path`, which is `details/{story_id}.html`). The per-section de-dupe at `src/fashion_radar/row_one/edition.py:118` is the only one that can ever fire. The final guard is harmless belt-and-suspenders, but the plan's wording ("after `max_stories` as a final guard" at plan line 21) could imply cross-section de-dupe is required. Suggest a one-line code comment or plan note stating the guard exists solely to make the invariant explicit / protect future refactors that might widen the id formula.

**M2 — Render invariant's `detail_path`-only branch is untested.**
`_validate_unique_story_routes` (plan lines 174-184) checks both `story.id` duplicates and `story.detail_path` duplicates independently. The proposed RED test (`test_render_row_one_site_rejects_duplicate_story_routes`, plan lines 112-121) duplicates a whole story, so both `id` and `detail_path` collide and the `id` branch raises first — the `detail_path` branch is never exercised. This branch is unreachable via `build_row_one_edition` (path is derived from id) but protects hand-built editions. Consider a second case with distinct ids but a shared `detail_path` to cover that line. Optional; does not block the fix.

**M3 — Render test assertion is weak but valid.**
`assert not (tmp_path / "details" / "the-row-signal-1234567890.html").exists()` (plan line 120) holds because validation precedes any filesystem write and `tmp_path` is fresh. It is correct but only checks one path that never existed. A stronger form (`not (tmp_path / "details").exists()` or `assert not any(tmp_path.iterdir())`) would better express "no partial output". Minor.

**M4 — De-dupe may leave sections below their caps (expected behavior, worth noting).**
After per-section de-dupe, a section with duplicates among its top-N ranked stories will publish fewer than `SECTION_CAPS[section_key]` stories; the plan does not backfill from rank N+1 for non-top sections (only `_top_stories` backfills, from `recent_items`, at `src/fashion_radar/row_one/edition.py:215-228`). This is the correct call — do not pad a section with lower-quality signals just to saturate the cap — and `story_count` will now finally equal the number of unique detail pages, which is the user-facing requirement. Flagging only so implementers do not mistake the reduced count for a regression. No change needed.

**M5 — Section-count snapshot in existing tests remains valid.**
Checked `tests/test_row_one_app_contract.py`, `tests/test_row_one_edition.py`, `tests/test_row_one_render.py`, and `tests/test_row_one_first_run_smoke.py` references: no existing test hand-builds an edition with duplicate `id`/`detail_path`, and every multi-story edition uses distinct ids (e.g. `the-row-signal-1234567890`, `brand-move-2222222222`, ...). The render fail-fast will not break existing tests. The `test_build_row_one_edition_backfills_top_stories_after_deduplication` test at `tests/test_row_one_edition.py:330` already relies on `_top_stories`' internal `seen` de-dupe and only asserts `top_stories`, so the new per-section de-dupe (a no-op there) is safe.

## Answers To Review Questions

1. **Is generation de-dupe plus render fail-fast the right boundary?** Yes. Generation de-dupe fixes the actual root cause — duplicate `story.id` produced within a single section when two candidates (or an entity plus a candidate) share the same representative-item `title` and `source_url` (see `_story_from_candidate` at `src/fashion_radar/row_one/edition.py:285-295` and `_story_from_entity` at `src/fashion_radar/row_one/edition.py:232-238`). The render-time fail-fast is correct defense-in-depth for hand-built `RowOneEdition` instances and any future generator path that bypasses `build_row_one_edition`. Placing validation *before* `clean_row_one_site_children` and `output_dir.mkdir` (plan line 186) ensures no partial output is written on failure.

2. **Is preserving the first ranked story for duplicate ids technically reasonable?** Yes. Every section feed is sorted by rank immediately before de-dupe: `_entity_stories` sorts by `(-heat_score, casefold, name)` (`edition.py:139-141`), `_candidate_stories` by `(-score, casefold, phrase)` (`edition.py:157-159`), `_brand_stories` by `(-score, casefold, name)` over the merged entity+candidate list (`edition.py:189-195`), and `_top_stories` already de-dupes by `seen` in ranked order (`edition.py:215-228`). So "first occurrence" == "highest ranked". Stable and deterministic.

3. **Is a contract bump unnecessary?** Correct, no bump. `ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v7"` (`src/fashion_radar/row_one/render.py:32`) governs the JSON payload *shape*. The plan does not add, remove, rename, or retype any payload field; it only guarantees an invariant (`story_count == len(unique stories) == len(unique detail_paths)`) that the contract tests already assume (see `test_row_one_app_payload_has_stable_counts` at `tests/test_row_one_app_contract.py:295-322` and `test_row_one_app_payload_includes_story_directory_for_clients` at `tests/test_row_one_app_contract.py:351-376`). The render fail-fast is a build-time guard, not a schema change.

4. **Are the tests sufficient to prove unique local detail-page publication?** Sufficient for the primary case, with one minor gap. The edition RED test (`test_build_row_one_edition_dedupes_duplicate_candidate_story_ids`) reproduces the production collision shape exactly — two `brand_or_designer` candidates sharing one representative item — and asserts global `id` and `detail_path` uniqueness. The render RED test proves the fail-fast fires before any file is written. Task 4 Step 3 rebuilds today's site and asserts `story_count == unique ids == unique hrefs == details/*.html count == local article sidecar count`, which is the real end-to-end proof for the `19 → 17` regression. Gap (M2): the `detail_path`-only branch of the render invariant is not exercised. Recommend adding it but it is not a blocker.

5. **Critical or Important issues before implementation?** None. The plan's scope (edition de-dupe + render invariant), its boundary (no scraping/source/deployment changes, no compliance-review feature, `reports/row-one/` stays ignored), and its verification commands (`UV_NO_CONFIG=1 uv --no-config run --frozen ...`) all conform to `AGENTS.md`. The four Minor notes above are polish, not gates.

## Recommendation

Proceed to Task 2 (RED tests). Optionally address M2 (add a distinct-id / shared-`detail_path` render case) and M3 (strengthen the negative filesystem assertion) while authoring the RED tests, since both are cheap and improve the contract surface. M1 and M4 are documentation/awareness only.
