# Stage 144 Plan Review

## Findings

No blocking issues. The plan is correct, complete, and safe to implement.

## Verified

The planned expected-command helper matches `build_imported_review_workflow()` for all seven steps:

| Index | Step name | Helper label | Expected command shape |
|---:|---|---|---|
| 0 | `summarize_imported_sources` | `summary` | `imported-signals-summary --data-dir <data>` |
| 1 | `refresh_stored_matches` | `match refresh` | `match --config-dir <config> --data-dir <data>` |
| 2 | `compare_imported_entities` | `entity delta` | `imported-entity-deltas --data-dir <data> --as-of <as_of> --current-days <current_days> --baseline-days <baseline_days> [--source-name <source>]` |
| 3 | `review_imported_entity_evidence` | `entity evidence` | `imported-entity-evidence --data-dir <data> --as-of <as_of> --entity-name 'The Row' --entity-type brand --current-days <current_days> --baseline-days <baseline_days> [--source-name <source>]` |
| 4 | `review_imported_candidate_phrases` | `candidate` | `imported-candidates --config-dir <config> --data-dir <data> --as-of <as_of> [--source-name <source>]` |
| 5 | `review_unmatched_imported_rows` | `unmatched rows` | `imported-signals --data-dir <data> --as-of <as_of> --lookback-days <lookback_days> --unmatched-only [--source-name <source>]` |
| 6 | `review_local_heat_movers` | `final heat` | `heat-movers --config-dir <config> --data-dir <data> --as-of <as_of>` |

`source_args` mirrors the runtime builder's optional source-name behavior. Coercing `lookback_days`, `current_days`, and `baseline_days` to strings in the smoke validator matches the runtime command rendering.

## RED/GREEN Assessment

The current validator only exact-argv-checks indices 3, 4, and 6. The four new drift mutations target indices 0, 1, 2, and 5, so each should fail RED with `DID NOT RAISE` before implementation. After the loop is added, all four mutations should raise `SmokeError` with the planned label substring. The three existing drift cases should keep passing because the preserved labels still appear in the command error message.

## Runtime Scope

Runtime behavior remains unchanged. The plan modifies only `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and Stage 144 docs/review artifacts. `src/fashion_radar/imported_review_workflow.py` stays untouched.

## Notes

- Retaining the explicit final-step assertion is redundant with the ordered step-name assertion, but it preserves the existing error surface and is acceptable.
- Focused verification and release gate commands cover the changed test and validator surfaces.

## Verdict

Proceed with implementation.
