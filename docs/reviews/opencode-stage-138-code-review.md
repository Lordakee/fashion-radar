# Stage 138 Code Review

## Critical findings

None.

## Important findings

None.

## Minor findings

1. **Drift-test replacements hardcode canonical fixture values.** The parametrized `replacement_command` calls in `tests/test_first_run_smoke.py:2147-2225` inline literals (`"rednote_mcp"`, `"exports"`, `"configs"`, `"data"`, `"2026-06-13T12:00:00+00:00"`, `"Rednote MCP Export"`, `"*.json"`, `"json"`) instead of reading them from `external_tool_readiness_payload()`. This is acceptable: the literals mirror the fixture exactly, each mutation still produces a real argv drift (format-flag swap or `--strict` removal), and the pattern matches the sibling `test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift` at `tests/test_first_run_smoke.py:1929-2070`. Pure maintainability note; non-blocking.

2. **New index accesses rely on the earlier name check.** `validate_external_tool_readiness()` now reads `steps[0]`, `steps[1]`, `steps[3]`, `steps[4]`, `steps[5]` (`scripts/check_first_run_smoke.py:1487,1509,1559,1571,1589`) without re-asserting each step's `name`. This is safe because step names are pinned against `EXPECTED_EXTERNAL_TOOL_READINESS_STEPS` at `scripts/check_first_run_smoke.py:1466-1471` before any index access, and it mirrors the pre-existing `workflow_step = steps[2]` / `dry_run_step = steps[-1]` style. Consistent with codebase conventions; non-blocking.

## Focus verification

1. **Prior gap demonstrably closed.** At `HEAD`, `validate_external_tool_readiness()` exact-checked only `steps[2]` (workflow) and `steps[-1]` (dry-run). The new parametrized test (`test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift`) covers all five previously unguarded steps with concrete argv drifts:
   - `inspect_adapter_registry`: `--format table` -> `--format json` -> "registry command"
   - `print_adapter_template_json`: `--format json` -> `--format table` -> "template command"
   - `print_signal_profile`: `--format json` -> `--format table` -> "signal profile command"
   - `lint_export_directory`: drops `--strict` -> "lint command"
   - `review_handoff_readiness`: drops `--strict` -> "handoff readiness command"

   The main TDD run verified these five cases failed before the implementation with `DID NOT RAISE`, then passed after the validator changes. Each `expected_error` string is a substring of the `{command_name} {label} command expected ...` message produced via `assert_equal` at `scripts/check_first_run_smoke.py:367-369`, so `pytest.raises(..., match=...)` anchors correctly.

2. **All five steps now exact argv-checked.** `scripts/check_first_run_smoke.py:1487-1609` calls `validate_expected_external_tool_command()` for `registry`, `template`, `signal profile`, `lint`, and `handoff readiness` labels. That helper (`scripts/check_first_run_smoke.py:376-390`) uses `shlex.split()` and compares against `["fashion-radar", *parts]`, so order, flags, and flag values are all positionally pinned. Combined with the existing workflow (`scripts/check_first_run_smoke.py:1531-1557`) and dry-run (`scripts/check_first_run_smoke.py:1611-1631`) checks, all seven readiness steps are now exact-checked.

3. **Expected argv derived from payload fields.** All new checks pass `adapter_id`, `directory`, `config_dir`, `data_dir`, `as_of`, `input_format`, `pattern`, `source_name` extracted from the payload at `scripts/check_first_run_smoke.py:1417-1424`. No hardcoded `"exports"`/`"configs"`/`"data"` in the implementation. The payload-equality test `test_external_tool_readiness_payload_matches_real_rednote_readiness` still passes, so the validator's expected argv round-trips with the real CLI output.

4. **Existing validation preserved.** Step-count (`scripts/check_first_run_smoke.py:1461-1465`), step-name (`scripts/check_first_run_smoke.py:1466-1471`), step-effect (`scripts/check_first_run_smoke.py:1472-1485`), checks block (`scripts/check_first_run_smoke.py:1426-1456`), boundary phrases (`scripts/check_first_run_smoke.py:1633-1654`), install-hint (`scripts/check_first_run_smoke.py:1442-1447`), and forbidden-scope (`scripts/check_first_run_smoke.py:1655-1657`) checks are untouched. Workflow and dry-run exact argv checks remain. Full readiness/workflow/adapters slice: 34 passed. Combined `tests/test_first_run_smoke.py` + `tests/test_external_tool_contract_parity.py`: 89 passed.

5. **Scope boundaries respected.** Diff is limited to `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`; both are validation-only. No `src/fashion_radar/` CLI changes, no `uv.lock` changes, no new dependencies, no artifact creation by the smoke script, no PATH lookup, no directory inspection, no handoff file reads, no SQLite, no import behavior change, no connectors/scraping/browser-automation/platform-APIs/account-session-cookie-token/media-download/monitoring/scheduling/source-acquisition/demand-proof/ranking/coverage-verification/compliance-audit behavior. `external-tool-readiness` remains local read-only guidance per the boundary phrases still enforced by the validator.

## Verification run

- `pytest ...::test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift` -> 5 passed
- `pytest tests/test_first_run_smoke.py -k "external_tool_readiness or external_tool_workflow or external_tool_adapters"` -> 34 passed
- `pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py` -> 89 passed
- `ruff check` -> All checks passed
- `ruff format --check` -> 2 files already formatted
- `python scripts/check_first_run_smoke.py --repo-root .` -> First-run sample smoke passed
- `git diff --check` -> clean

## Verdict

There are **no Critical or Important blockers** before release. Stage 138 is approved.
