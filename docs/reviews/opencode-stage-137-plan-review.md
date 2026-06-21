# Stage 137 Plan Review

## Critical findings
None.

## Important findings
None.

## Minor findings
1. **Redundant guard on `steps[10]`.** The existing block at `scripts/check_first_run_smoke.py:1086-1093` already defines `import_step = steps[10]` with a `dict` guard and message `"{command_name} import step must be a JSON object"`. Task 2 Step 2 introduces a second variable `import_signals_step = steps[10]` with the same guard and an identical error string. Harmless (the first guard runs earlier and short-circuits), but a reader may wonder why the same step gets two names. Consider reusing the existing `import_step` binding for the command check, or note the intentional separation of concerns in the plan.
2. **Drift choice documentation for `print_handoff_workflow`.** The RED mutation appends `--format json` to a command that intentionally omits `--format` (workflow metadata, not importable rows). The choice is valid and the expected argv correctly excludes `--format`; consider a one-line note in the design so future maintainers don't "fix" the expected argv by adding `--format`.
3. **RED-test hardcoded values.** The parametrized mutations hardcode `"exports"`, `"configs"`, `"data"`, `"2026-06-13T12:00:00+00:00"`, `"Rednote MCP Export"` rather than reading them from `external_tool_workflow_payload()`. These match the fixture today, so the test is correct. If the fixture defaults ever drift, the RED mutations could accidentally coincide with the expected argv and the test would silently weaken. Low risk given the frozen fixture, but worth noting.

## Cross-cutting checks (all pass)
- The 8 unguarded steps are correctly identified (indices 3, 4, 5, 7, 8, 9, 10, 11 of `EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS`).
- Each RED mutation produces an argv that provably differs from the expected while keeping `name`/`suggested_effect` and payload fields valid, so it isolates command-shape drift as claimed.
- `validate_expected_external_tool_command` (with its `shlex.split()` exact-list comparison) is reused; no second parser or substring check is introduced.
- Expected argv values are derived from payload fields (`directory`, `input_format`, `pattern`, `config_dir`, `data_dir`, `as_of`, `source_name`), not hardcoded first-run paths, in both insertion blocks.
- Existing registry, readiness, template, lint, step-count, step-name, step-effect, and boundary checks remain intact; the new blocks are inserted between them without reordering.
- Scope is validation-only: no CLI runtime, command execution, PATH lookup, directory inspection, handoff reads, import/SQLite changes, artifact creation, dependency/`uv.lock` changes, or any of the AGENTS.md-forbidden behaviors.
- Error labels round-trip correctly through `assert_equal(f"{command_name} {label} command", …)` and match every `match=` string in the parametrized test.
- Focused and release-gate verification commands are sufficient and consistent with `AGENTS.md` mirror-frozen `uv --no-config run --frozen` conventions.

## Final statement
There are **no Critical or Important blockers**. The Stage 137 design and implementation plan are approved for implementation.
