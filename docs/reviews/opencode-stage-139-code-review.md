# Stage 139 Code Review Findings

**No blocking findings.** Stage 139 is approvable.

## Verified against each requirement

1. **Reject argv drift, not just missing substrings** - `validate_imported_review_workflow` (`scripts/check_first_run_smoke.py:706-758`) and `validate_community_handoff_workflow` (`scripts/check_first_run_smoke.py:785-802`) now route through `validate_expected_external_tool_command`, which `shlex.split`s and compares the full argv list. This catches suffix drift (`heat-movers-extra`, `community-handoff-check-dir-extra`), value drift (`--current-days 14`, `--config-dir configsets`), extra flags, reordering, and missing flags.

2. **Runtime CLI builders unchanged** - `git diff 969a0b9 -- src/` is empty. Only `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py` changed.

3. **Fixture metadata mirrors real workflow JSON** - `imported_review_workflow_payload()` top-level keys (`as_of, config_dir, data_dir, source_name, lookback_days, current_days, baseline_days, execution_mode, step_count, steps`) match `ImportedReviewWorkflow` field order exactly (`imported_review_workflow.py:23-35`). Expected argv order in the validator matches the builder at `community_handoff_workflow.py:101-116` and `imported_review_workflow.py:112-182`.

4. **Tests prove failures the old substring validators missed** - Each replacement in `tests/test_first_run_smoke.py:1604-1653` and `1690-1704` preserves every old substring fragment while drifting real argv, such as `heat-movers-extra` still containing `fashion-radar heat-movers` and `--config-dir configsets` still containing `--config-dir`.

## Verification run

- `pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q`: 93 passed
- `ruff check` and `ruff format --check`: clean
- `python scripts/check_first_run_smoke.py --repo-root .`: `First-run sample smoke passed.`

## Minor observations

- `validate_imported_review_workflow` still does not structurally check steps 3 (`compare_imported_entities`) or 6 (`review_unmatched_imported_rows`); these were never substring-checked either, so this is not a regression and is a candidate for a future stage.
- No automated parity test exists for `imported_review_workflow_payload()` or `community_handoff_workflow_payload()` against their real Pydantic builders, unlike the external-tool payloads which have guards in `tests/test_first_run_smoke.py:1235-1320`. This is a pre-existing gap.
- The `review_imported_entity_evidence` and `compare_imported_entities` fixture commands gained `--current-days 7 --baseline-days 7` purely for parity, since no validator checks step 3.
