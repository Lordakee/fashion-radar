# Stage 139 Plan Review

## Findings

**No blocking issues.** The plan is sound and can proceed to implementation.

### Verified

1. **Runtime CLI behavior preserved** - Plan modifies only `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`. The two `src/fashion_radar/*` workflow builders are untouched.

2. **Expected argv lists match runtime builders exactly:**
   - Entity evidence: matches `imported_review_workflow.py:112-128` (incl. `--current-days`/`--baseline-days` and optional `--source-name`).
   - Imported candidates: matches `imported_review_workflow.py:138-148`.
   - Final heat movers: matches `imported_review_workflow.py:173-182` and preserves the "no `--source-name`" invariant.
   - Community readiness: matches `community_handoff_workflow.py:101-116`.

3. **Fixture metadata mirrors real Pydantic payload** - Proposed fields (`as_of`, `config_dir`, `data_dir`, `source_name`, `lookback_days`, `current_days`, `baseline_days`) match `ImportedReviewWorkflow` field names/order in `imported_review_workflow.py:23-35`. `community_handoff_workflow_payload()` already has the needed top-level fields.

4. **RED tests would fail before, pass after:**
   - `--current-days 14` drift bypasses current substring loop (which never checks `--current-days`).
   - `--config-dir configsets` preserves the `--config-dir` substring.
   - `heat-movers-extra` and `community-handoff-check-dir-extra` both preserve their substring prefixes.
   - All four labels (`entity evidence command`, `candidate command`, `final heat command`, `readiness command`) match the `label` arguments proposed in Task 3, so the `pytest.raises(..., match=...)` will hit the `assert_equal` message format `{command_name} {label} command expected ...`.
   - GREEN phase confirmed by hand: post-fixture-update commands shlex-split to exactly the expected argv built from payload metadata.

### Minor observations (non-blocking)

- **Task 2 Step 1 fixture-update precision**: The plan says to insert `"--current-days 7 --baseline-days 7 "` into the `compare_imported_entities` fixture command but doesn't specify position. Runtime emits these between `--as-of` and `--source-name` (`imported_review_workflow.py:98-104`). The validator does not check step 2, so this is cosmetic - but the implementer should place them between `--as-of` and `--source-name` for true parity.
- **Pre-existing fixture drift caught as a side effect**: The current `compare_imported_entities` and `review_imported_entity_evidence` fixture commands are already missing `--current-days 7 --baseline-days 7` versus the runtime builder. Task 2 Step 1 fixes this; worth noting in the code review that the fixture was drifted before this stage.

## Verdict

Plan is approvable. Proceed to Task 2 (RED tests).
