# Stage 157 Plan Review

## Verification of the gap (Q1)

The gap is real and accurately described. Confirmed by reading the actual code:

- `community_handoff_workflow.py:57-160` emits the strict chain (`--strict`, `community-handoff-check-dir --strict`, `--imported-at AS_OF`).
- `check_first_run_smoke.py:2537-2543` validates the workflow JSON against that strict chain.
- `check_first_run_smoke.py:2544-2595` (`run_first_run_flow`) then executes a *looser* chain: `community-signal-lint-dir` without `--strict` (line 2544), no `community-handoff-check-dir`, and `import-signals-dir --dry-run` without `--imported-at` (line 2580). The plan targets exactly this gap.

## Command order (Q2)

The proposed order (lint-strict -> candidates -> check-strict -> import-dry-run-with-imported-at) matches the validated workflow steps 1-4 in `community_handoff_workflow.py` verbatim and preserves the existing smoke ordering. Reasonable and consistent.

## Scope preservation (Q3)

The plan keeps `--dry-run` on `import-signals-dir`, excludes the write-capable step, makes no runtime CLI changes, and adds no platform collection. Scope is preserved.

## Test sufficiency (Q4)

`test_run_first_run_flow_uses_deterministic_local_command_sequence` (`tests/test_first_run_smoke.py:3661`) replaces `run_cli` with a fake that captures args and asserts `captured == expected_first_run_flow_commands(...)`. Updating the expected list (Task 1) will make it fail RED against the unchanged smoke; updating the smoke (Task 2) will make it pass GREEN. The fake's generic `stdout_by_command.get(command_name, "")` branch (`test_first_run_smoke.py:3766`) handles the new `community-handoff-check-dir` call without modification, and `run_first_run_flow()` does not parse that command's output, so no fake update is needed. Sufficient.

## Critical findings

**None.** No blocking issues.

## Important findings

**None.** The plan is internally consistent, correctly scoped, and the test-first ordering is sound.

## Minor findings

1. **Task 2 Step 2 anchor ambiguity** (`plan.md:133-136`): "Insert this call after the existing `community-candidates-dir` JSON validation" is correct, but the smoke script actually has `validate_community_candidates(...)` at `check_first_run_smoke.py:2575` between the candidates call and the import dry-run. Consider rewording to "after `validate_community_candidates(...)` returns" to remove any chance the implementer inserts it between the candidates invocation and its validator.

2. **Strict-precheck evidence** (`design.md:102-104`): The design asserts a local pre-check confirmed `Warnings: 0` on the example directory, but the smoke copies `examples/community-signals.example.csv` (single file) into the runtime exports dir, not the `examples/community-tool-handoff-directory.example` directory. Task 3 Step 2 (real smoke run) will surface any strict failure, so this is non-blocking; just flag that the pre-check evidence should be re-confirmed against the actual single-file exports layout used by the smoke, not the multi-file example directory.

3. **`--imported-at` value source**: Plan Step 3 of Task 2 says add `"--imported-at", AS_OF`. `AS_OF = "2026-06-13T12:00:00Z"` (Z suffix), while the validated workflow's `as_of_text` is the ISO form `2026-06-13T12:00:00+00:00`. Both parse to the same instant via `parse_datetime_utc`, and the `import-signals-dir` command accepts either form. Non-blocking, but worth noting the smoke will pass `AS_OF` while the workflow metadata prints the `+00:00` form - a cosmetic asymmetry that already exists for the other `--as-of AS_OF` calls in the smoke.

## Additional validation needed (Q5)

None required before implementation. The release-gate commands in `design.md:120-130` and `plan.md:255-268` already include the real smoke run, full pytest, ruff, lock check, and token/header sweep - sufficient to catch any strict-mode regression on the example CSV.

**Verdict: No blocking findings. The plan is approved to proceed.**
