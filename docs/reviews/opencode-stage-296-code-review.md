# opencode Stage 296 Code Review

**Reviewer:** opencode (GLM 5.2, max variant)
**Scope:** uncommitted Stage 296 diff vs. base `18f02dc` (`Stage 295: deepen row one editorial briefing`)
**Files reviewed:** `src/fashion_radar/row_one/edition.py`, `src/fashion_radar/row_one/render.py`, `tests/test_row_one_edition.py`, `tests/test_row_one_render.py`
**Verdict:** **APPROVE — no Critical or Important findings; safe to commit and push.**

Per the prompt's "Do not edit files" instruction, I am returning the review body only and not writing it to disk.

## Findings

### Critical
None.

### Important
None.

### Minor / Notes (non-blocking)

**m1 — Final post-`max_stories` guard is unreachable defensive code.**
`stories = _unique_stories_by_id(stories)` at `src/fashion_radar/row_one/edition.py:123` can never remove a story under the current id formula. `_story_id` hashes `f"{section_key}|{title}|{discriminator}"` (`edition.py:537`), so two stories in *different* sections cannot share an `id`, and per-section de-dupe at `edition.py:118` already removes same-section collisions. The line is harmless belt-and-suspenders that protects future refactors of the id formula; the absence of an explanatory code comment is consistent with the repo's no-comment convention. Not a blocker.

**m2 — `detail_path`-only collision is now exercised (plan-review M2 closed).**
The implementer split the single planned render test into two: `test_render_row_one_site_rejects_duplicate_story_ids` (whole-story copy → id branch fires first) and `test_render_row_one_site_rejects_duplicate_detail_paths` (distinct id, shared `detail_path` via `model_copy(update={"id": ...})` → detail-path branch fires). Both branches of `_validate_unique_story_routes` are now covered.

**m3 — Negative filesystem assertions strengthened (plan-review M3 closed).**
Both render tests now assert `not (tmp_path / ".row-one-site").exists()` and `not (tmp_path / "details").exists()` — strictly stronger than the originally proposed single-file check, and correct because `_validate_unique_story_routes` runs before `clean_row_one_site_children` and `output_dir.mkdir`.

**m4 — Section caps may bind below `SECTION_CAPS[section_key]` after de-dupe (expected, plan-review M4).**
When duplicate ids appear within a section's top-N, the section publishes fewer than the cap. This is the desired behavior (no padding with lower-rank signals) and is exactly what makes the new `story_count == unique detail pages` invariant hold. The site-rebuild proof (`18/18/18/18/18`) confirms the user-facing requirement.

## Answers To Review Questions

1. **Is generation de-dupe correct and deterministic?** Yes. `_unique_stories_by_id` (`edition.py:234-242`) preserves first-occurrence order; every section feed is pre-sorted by deterministic keys before de-dupe runs (`_entity_stories` by `(-heat_score, casefold, name)` at `edition.py:142`; `_candidate_stories` by `(-score, casefold, phrase)` at `edition.py:160`; `_brand_stories` over the merged entity+candidate ranking at `edition.py:191-197`; `_top_stories` already de-dupes internally via its own `seen` set at `edition.py:217-221`, so the new pass is a no-op there). "First occurrence" == "highest ranked", so de-dupe never degrades editorial quality.

2. **Is render fail-fast placed early enough to avoid partial output?** Yes. `_validate_unique_story_routes(edition)` is the first statement in `render_row_one_site` (`render.py:54`), preceding `clean_row_one_site_children` (`render.py:56`), `output_dir.mkdir` (`render.py:58`), the `.row-one-site` marker write (`render.py:59`), `_write_assets`, and all index/detail/data writes. A failed rebuild therefore neither destroys the prior site (no clean runs) nor leaves any partial artifact behind. Both new render tests verify `.row-one-site` and `details/` are absent after the raise.

3. **Are app contract and existing rendering behavior preserved?** Yes. `ROW_ONE_APP_CONTRACT_VERSION` stays `"row-one-app/v7"` (`render.py:32`); no payload fields were added, removed, renamed, or retyped. The change only guarantees an invariant (`story_count == len(unique ids) == len(unique detail hrefs)`) that `tests/test_row_one_app_contract.py` already assumes. The reported `1956 passed` full suite and `216 passed` focused suite (including `test_row_one_app_contract.py`) confirm no regression.

4. **Are tests sufficient for the duplicate-id and duplicate-detail-path cases?** Yes. The edition test (`test_build_row_one_edition_dedupes_duplicate_candidate_story_ids`) reproduces the production collision shape exactly — two `brand_or_designer` candidates sharing one representative item — and asserts both per-section (`len(brand_stories) == 1`) and global (`len({ids}) == len(stories)`, `len({paths}) == len(stories)`) uniqueness. The two render tests cover both branches of the invariant independently. End-to-end count proof (18 stories → 18 unique ids → 18 detail hrefs → 18 `details/*.html` → 18 `data/articles/*.json`) closes the loop.

5. **Are any Critical or Important issues blocking commit/push?** No. Four minor notes above are informational; none block. The implementation also resolved the two optional polish items (M2, M3) raised in `docs/reviews/opencode-stage-296-plan-review.md`.

## Recommendation

Proceed to commit and push:

```
Stage 296: enforce row one unique detail pages
```
