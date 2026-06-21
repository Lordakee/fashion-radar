# Stage 137 Code Review

## Critical findings

None.

## Important findings

None.

## Minor findings

1. **Plan vs implementation divergence (step 10), functionally equivalent and arguably cleaner.** The plan specifies `import_signals_step = steps[10]` with its own `isinstance(..., dict)` guard before the new import command check. The implementation instead reuses the existing `import_step` variable already defined and type-checked at `scripts/check_first_run_smoke.py:1086-1088`. This is DRY (no redundant `steps[10]` access or dict check) and the type guard is still satisfied earlier in the function. No behavior change. Worth noting only because the code-review prompt asks whether eight new `isinstance` blocks were added: seven were; the eighth was intentionally elided for step 10.

2. **Verbose repetition is acknowledged in the design.** Eight near-identical `validate_expected_external_tool_command(...)` blocks are inserted in step order. The design doc (`docs/superpowers/specs/2026-06-21-stage-137-external-tool-workflow-step-argv-design.md:124-129`) explicitly justifies this as following existing style and avoiding abstraction during a validation-only hardening stage. Acceptable.

## Review focus answers

1. **RED tests prove the previous gap.** `test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift` (`tests/test_first_run_smoke.py:2071`) parametrizes eight cases, one per previously unguarded step. Each mutation isolates a single step's command shape drift (wrong `--format`, dropped `--strict`, dropped/added `--dry-run`, swapped `--source-name`, extra flag, etc.) while leaving step `name`, `suggested_effect`, and all other steps' commands intact. Before this stage, the validator only exact-checked steps 0/1/2/6 and only checked `suggested_effect` for step 10, so all eight mutations would have passed silently. The test confirms each now raises `SmokeError` with the matching step label.

2. **All eight previously unguarded step commands are now exact argv-checked.** Confirmed at `scripts/check_first_run_smoke.py:1187-1364` for indices 3, 4, 5, 7, 8, 9, 10, 11, each delegating to `validate_expected_external_tool_command()` which `shlex.split()`s and compares to `["fashion-radar", *parts]` exactly (helper at `scripts/check_first_run_smoke.py:376-390`).

3. **Expected argv is payload-derived.** Every expected argument is built from `directory`, `input_format`, `pattern`, `config_dir`, `data_dir`, `as_of`, `source_name` extracted from the payload at `scripts/check_first_run_smoke.py:1063-1069`. No hardcoded `exports`, `configs`, `data`, or timestamp literals appear in the new blocks; the validator will accept any first-run payload whose commands match its declared field values.

4. **Existing checks preserved.** Registry (step 0, `:1115-1135`), readiness (step 1, `:1137-1163`), template (step 2, `:1165-1185`), lint (step 6, `:1247-1263`), step_count (`:1057`, `:1074-1078`), step names (`:1080-1084`), import-step effect (`:1086-1093`), step effects list (`:1095-1113`), and boundaries (`:1366-1372`) are all intact and unchanged.

5. **Validation-only and within AGENTS.md boundaries.** The diff touches only `scripts/check_first_run_smoke.py` (smoke validator) and `tests/test_first_run_smoke.py` (smoke tests). No CLI runtime code, no `subprocess` execution of generated commands, no PATH lookup, no directory inspection, no handoff file reads, no SQLite access, no import behavior, no artifact creation. `uv.lock` and `pyproject.toml` are unchanged (verified `git diff --exit-code -- uv.lock` is clean). The change only compares parsed shell argv lists against payload-derived literals; it introduces no connectors, scraping, browser automation, platform APIs, account/session/cookie/token behavior, media downloads, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit product behavior.

## Verification notes

All commands from the prompt were re-run and passed:

- `pytest ...::test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift -q`: 8 passed.
- `pytest ... -k "external_tool_workflow or external_tool_readiness or external_tool_adapters"`: 29 passed, 49 deselected.
- `pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q`: 84 passed.
- `ruff check` and `ruff format --check` on both files: clean.
- `python scripts/check_first_run_smoke.py --repo-root .`: "First-run sample smoke passed."
- `git diff --check`: clean.
- Additional: full `tests/test_first_run_smoke.py` suite: 78 passed. `git diff --exit-code -- uv.lock` clean. `pyproject.toml` unchanged.

## Final release statement

No Critical or Important blockers are present. Stage 137 is approved for release.
