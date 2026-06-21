# Stage 138 Plan Review

## Critical findings

None.

## Important findings

None.

## Minor findings

1. **RED test uses hardcoded fixture values.** The parametrized replacement commands in Task 1 hardcode `"exports"`, `"configs"`, `"data"`, `"rednote_mcp"`, `"2026-06-13T12:00:00+00:00"`, `"Rednote MCP Export"`, `"*.json"`, and `"json"` rather than reading them from `external_tool_readiness_payload()`. This is acceptable for a RED test proving the current gap (the values match the fixture exactly), and the Task 2 implementation correctly derives args from payload fields. Non-blocking; noting for maintainability.

2. **Plan-review artifact creation not explicitly tasked.** The Files section and the Task 4 commit list reference `docs/reviews/opencode-stage-138-plan-review-prompt.md` and `docs/reviews/opencode-stage-138-plan-review.md`, but no Task step creates them. This is implied by the `REVIEW_PROTOCOL.md` pre-coding workflow (this review produces them), and the code-review artifacts do have explicit Task 3 steps. Minor documentation gap.

3. **Index-based step access in Task 2.** The new checks use `steps[0]`, `steps[1]`, `steps[3]`, `steps[4]`, `steps[5]` without re-checking step names at each index. This is safe because step names are validated against `EXPECTED_EXTERNAL_TOOL_READINESS_STEPS` at `scripts/check_first_run_smoke.py:1466-1471` before any index access, and it matches the existing `workflow_step = steps[2]` / `dry_run_step = steps[-1]` pattern. Consistent with codebase style.

## Focus verification

1. **Five unguarded steps correctly identified.** `validate_external_tool_readiness()` at `scripts/check_first_run_smoke.py:1375-1561` only exact-checks `steps[2]` (workflow, line 1487) and `steps[-1]` (dry-run, line 1515). The five unchecked steps are `steps[0]` inspect_adapter_registry, `steps[1]` print_adapter_template_json, `steps[3]` print_signal_profile, `steps[4]` lint_export_directory, and `steps[5]` review_handoff_readiness. Confirmed.

2. **RED tests are specific.** Each mutation changes only the command argv (format flag swap or `--strict` removal) while leaving step `name`, `suggested_effect`, and all surrounding payload fields valid. The current validator checks names and effects but not these command strings, so each mutation will pass today (test fails as expected) and fail after Task 2 (test passes as expected). Each expected error label (`registry command`, `template command`, `signal profile command`, `lint command`, `handoff readiness command`) matches the `label` argument passed to `validate_expected_external_tool_command`, which flows into the `assert_equal` message at `scripts/check_first_run_smoke.py:386-390`.

3. **Reuses existing exact argv checker.** Task 2 calls `validate_expected_external_tool_command()` for all five steps. That helper uses `shlex.split()` and compares against `["fashion-radar", *parts]` (lines 382-390). No second parser, no substring checks.

4. **Expected argv derived from payload fields.** Task 2 snippets use `adapter_id`, `directory`, `config_dir`, `data_dir`, `as_of`, `input_format`, `pattern`, `source_name` — all extracted from the payload at `scripts/check_first_run_smoke.py:1417-1424`. No hardcoded `"exports"`/`"configs"`/`"data"` in the implementation. The real CLI round-trips correctly because `test_readiness_commands_use_overrides_and_shell_quote_values` at `tests/test_external_tool_readiness.py:189-241` confirms the CLI shell-quotes special-char paths and the validator's `shlex.split()` reverses that exactly.

5. **Existing validation preserved.** The plan inserts new checks before `workflow_step = steps[2]` (line 1487) and after the workflow block / before `dry_run_step = steps[-1]` (line 1515). Step-count (line 1461), step-name (line 1466), step-effect (line 1472), checks block (lines 1426-1456), boundary phrases (lines 1537-1561), install-hint (lines 1442-1447), and forbidden-scope (lines 1559-1561) validation all remain untouched.

6. **Scope boundaries respected.** Only `scripts/check_first_run_smoke.py` (first-run smoke validator) and `tests/test_first_run_smoke.py` change. No `src/fashion_radar/` CLI code, no dependency changes, no `uv.lock`, no artifact creation, no execution, no PATH/directory/file/SQLite/import behavior changes, no connectors/scraping/browser-automation/platform-APIs/account-cookie-token/media-download/monitoring/scheduling/source-acquisition/demand-proof/ranking/coverage-verification/compliance-audit behavior.

7. **Verification commands sufficient.** Focused verification covers the new RED test, the broader readiness/workflow/adapters test slice, contract parity (`tests/test_external_tool_contract_parity.py`), ruff check + format, the smoke script itself, and `git diff --check`. Release gate adds full pytest, repo-wide ruff, lockfile check, `uv.lock` diff, and GitHub token/auth-header secret scan.

## Verdict

There are **no Critical or Important blockers**. The Stage 138 design and implementation plan are approved for implementation. The three minor observations are non-blocking and primarily stylistic/documentation notes.
