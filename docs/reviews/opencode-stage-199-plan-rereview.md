# Stage 199 Plan Rereview

## Verdict

**Approved.** All previously required plan changes are fully resolved and verified
against the current codebase. No Critical or Important blockers. The revised plan is
ready for implementation. A handful of minor observations below are non-blocking.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

1. **Rounding location is implied, not pinned.** Task 2's test asserts
   `evidence.avg_confidence == 0.85` and `evidence.min_confidence == 0.7` on the
   *model attribute* (`tests/test_reports.py` via the revised plan lines 437-439),
   not on serialized JSON. This is numerically sound for the given fixture
   (`(0.95+0.9+0.7)/3 == 0.85` exactly; `min == 0.7`, `max == 0.95` all hold as
   float-equal), but only if `_match_evidence(...)` rounds before constructing
   `EntityMatchEvidence`. The plan says "compute ... rounded to four decimal
   places" in the helper (line 493), which implies in-helper rounding; an
   implementer who defers rounding to a JSON serializer would break the equality.
   Consider adding one clause: "round in the helper, not via a model serializer."

2. **Forbidden-string additions are true-but-unexercised for the Miu Miu path.**
   Task 3 Step 1 extends `test_json_report_excludes_internal_database_and_matcher_fields`
   with `"raw duplicate context must stay internal"` and `"raw safe alias must stay
   internal"` (plan lines 525-528). That test uses the refactored `_store_item`
   path, which still stores only the single Miu Miu sentinel match (alias
   `"raw alias must stay internal"`). The two newly added strings are never
   present in that report, so the assertions are trivially satisfied. Raw-leakage
   protection is in fact structural (`EntityMatchEvidence` and `EntityReport` both
   use `ConfigDict(extra="forbid")`, and `match_evidence` exposes only counts +
   three confidence scalars). Not wrong; just note the Task 2 fixture aliases are
   not scanned for leakage anywhere.

3. **Negative-case entity choice unspecified.** The `matched_items == -1`
   negative case (plan line 708) does not name which entity receives the value.
   Placing `-1` on a non-`The Row` entity (e.g. `Ballet Flats`) exercises the
   non-negative-integer guard cleanly without colliding with the `>= 1`-for-
   `The Row` check. Cosmetic; resolvable at implementation time.

4. **No Markdown evidence-line coverage in the smoke validator.** Task 4 Step 2
   adds only JSON-side checks; `report_markdown()` and `validate_report_outputs`
   do not assert the rendered `- Match evidence:` line. This is consistent with
   the first review's "don't over-pin" guidance, and Task 3's unit tests cover
   the line directly. Informational only.

5. **`_representative_items` vs `_match_evidence` filter-width divergence.**
   `reports.py:447` filters representative items by `entity_name` only, while the
   new helper filters by both `entity_name` and `entity_type`. Evidence's stricter
   filter is more correct and matches scoring's `(entity_name, entity_type,
   item_id)` identity (`docs/scoring.md:24`). The representative-items behavior is
   pre-existing and out of scope for Stage 199; noted for awareness only.

## Resolution Status For Previous Required Changes

| # | Previous required change | Status | Evidence |
|---|---|---|---|
| 1 | Task 4 Step 3: name `report_payload()` + full 9-key dicts + missing-key negative | **Resolved** | Plan lines 682-709 explicitly update `report_payload()` with the exact 9-key dict for all three entities and add both negative cases. Verified `report_payload()` at `tests/test_first_run_smoke.py:524-670` currently has no `match_evidence` key, so the instruction is necessary and correctly targeted. |
| 2 | Task 4 Step 2: soften `matched_items >= 1` or confirm empirically | **Resolved** | Plan lines 666-671 require non-negative int for all entities and `>= 1` only for `The Row`. Option (b) from the first review. |
| 3 | Task 4 Step 4: docs placement outside `## Limits` | **Resolved** | Plan lines 713-715 insert `## Match Evidence` after `## Formula`, before `## Labels`. Confirmed `docs/scoring.md` heading order (`Formula`@50 to `Labels`@88 to `Limits`@164) and that `tests/test_scoring_docs.py:17-20` parses `## Limits` via `split(marker,1)[1].split("\n## ",1)[0]`, which is unaffected. |
| 4 | Task 2: tie-break + sub-threshold tests | **Resolved** | Plan lines 366-405 add the `the-row-tie` fixture (0.7/0.7, `safe_alias` vs `parent_brand` lex winner `parent_brand`) and `the-row-low-confidence` (0.3, excluded). Arithmetic verified: `matched_items=3`, `parent_brand=2`, `safe_alias=1`, `min=0.7`, `avg=0.85`, `max=0.95`. |
| 5 | Task 3 Step 3: `min == max` Markdown form | **Resolved** | Plan lines 137-139, 597-598 keep the range form (`confidence 1.00-1.00 avg 1.00`) for a single stable shape. |
| Opt | Raise `sed -n '1,260p'` to 400 | **Resolved** | Plan lines 191, 810, 879 now use `sed -n '1,400p'`. |

## Answers To Review Questions

1. **Previous required changes fully resolved?** Yes — all five required changes
   and the optional truncation fix are addressed (see table above).

2. **Is filtering by both `entity_name` and `entity_type` correct and sufficient?**
   Yes. It matches scoring's `(entity_name, entity_type, item_id)` identity
   (`docs/scoring.md:24`) and the `EntityHeatMetric`/`EntityReport` carry both
   fields (`reports.py:117-118`). Since the filter fixes name+type, the remaining
   dedup key is effectively `item_id`, identical to scoring's highest-confidence
   dedup. This is strictly more correct than `_representative_items`' name-only
   filter. Sufficient.

3. **Are the revised tests practical and not over-brittle?** Yes. Task 2 pins
   exact bucket counts and confidence stats on a fully synthetic, deterministic
   fixture (covering dedup, lex tie-break, sub-threshold exclusion, and window
   exclusion in one test). The CLI smoke pins values that are structurally
   guaranteed by its fixture (`test_cli.py:7761-7772`: one `accepted` match at
   confidence `1.0` for `The Row` brand yields `matched_items=1`,
   `accepted_without_context_items=1`, `1.0/1.0/1.0`). The first-run validator
   requires only key presence + non-negative int universally and `>= 1` for
   `The Row` alone, avoiding brittle count-pinning on product/category entities.
   All float-equality assertions verified stable.

4. **New Critical/Important blockers?** No. Only the five Minor observations
   above, none of which block implementation.

## Required Plan Changes Before Implementation

None. The plan may proceed to implementation. (Optional polish: add an explicit
"round in the helper, not at serialization" clause to Task 2 Step 3 to harden
Minor Finding 1.)
