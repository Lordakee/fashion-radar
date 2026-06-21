## Stage 153 Plan Rereview — Findings

### Prior review status (verified resolved)

- **C1 (pinning breaks real smoke)** — Resolved. `validate_community_handoff_workflow()` now takes `expected_directory`/`expected_config_dir`/`expected_data_dir` as keyword-only args (design.md:62-69, plan.md:158-166), and `run_first_run_flow()` passes `str(context.exports_dir)`/`str(context.config_dir)`/`str(context.data_dir)` (plan.md:208-215). Defaults match the fixture literals, so positional unit-test callers still work.
- **C2 (verification skips smoke script)** — Resolved. The smoke script now appears in focused verification (design.md:169, plan.md:243), task 4 step 1 (plan.md:260), and the release gate (plan.md:284).
- **I1 (directory-drift false RED via `match="directory"`)** — Resolved. Match is now `"community-handoff-workflow directory"` (design.md:121, plan.md:80). `re.search("community-handoff-workflow directory", ...)` does not match `"community-handoff-workflow lint_handoff_directory command"` (space vs. underscore-delimited `directory`). Also, the test now coordinates field+command drift via `replace_workflow_command_fragments`, so the current validator truly does not raise.
- **I2 (`DID NOT RAISE` rationale)** — Resolved. With both field and command fragments mutated together (design.md:112-153), the current validator's payload-derived synthesis produces matching commands, so it genuinely does not raise.

### CRITICAL (blocking)

**C3. The fix for C1 breaks `test_run_first_run_flow_uses_deterministic_local_command_sequence`.**

`tests/test_first_run_smoke.py:3470-3561` calls `smoke.run_first_run_flow(context)` directly. Its `fake_run_cli` returns the raw fixture payload for `community-handoff-workflow` (`tests/test_first_run_smoke.py:3536`: `"community-handoff-workflow": json.dumps(community_handoff_workflow_payload())`), which has `directory="/tmp/export"`, `config_dir="configs"`, `data_dir="data"` (`tests/test_first_run_smoke.py:655-660`).

The context built by `make_context(tmp_path)` (`tests/test_first_run_smoke.py:1407-1418`) uses temp-derived paths: `exports_dir = tmp_path / "runtime" / "exports"`, `config_dir = tmp_path / "runtime" / "config"`, `data_dir = tmp_path / "runtime" / "data"`.

After task 3 step 3 (plan.md:204-215), `run_first_run_flow` will call:
```python
validate_community_handoff_workflow(
    "community-handoff-workflow",
    community_handoff_workflow,           # fixture: directory="/tmp/export"
    expected_directory=str(context.exports_dir),   # tmp_path/runtime/exports
    expected_config_dir=str(context.config_dir),   # tmp_path/runtime/config
    expected_data_dir=str(context.data_dir),       # tmp_path/runtime/data
)
```

The new `assert_equal("community-handoff-workflow directory", payload.get("directory"), expected_directory)` (`scripts/check_first_run_smoke.py:1119` after the edit) compares `"/tmp/export"` against `str(tmp_path / "runtime" / "exports")` and raises `SmokeError`. The test fails.

The plan's focused `-k "community_handoff_workflow"` run (plan.md:233) does **not** match `test_run_first_run_flow_uses_deterministic_local_command_sequence` (the name lacks that substring), so the failure surfaces only at task 4 step 1 (`pytest tests/test_first_run_smoke.py -q`, plan.md:259) — after the implementer believes GREEN is complete. Neither the design's "Scope" (design.md:36-48) nor the plan's task list mentions updating this test.

**Fix:** Add a step (e.g., in task 3, before the GREEN runs) to update `fake_run_cli` in `test_run_first_run_flow_uses_deterministic_local_command_sequence` so the `community-handoff-workflow` payload reflects `fake_context`'s temp paths — cleanest by building it via `build_community_handoff_workflow(directory=fake_context.exports_dir, config_dir=fake_context.config_dir, data_dir=fake_context.data_dir, ...)` and serializing with `model_dump_json()`, which keeps step commands consistent with the top-level fields. Other commands in `stdout_by_command` are unaffected because their validators (`validate_imported_review_workflow` at `scripts/check_first_run_smoke.py:1007`, `validate_external_tool_workflow`/`validate_external_tool_readiness`) still read paths from the payload or only assert populated strings (`scripts/check_first_run_smoke.py:1460-1463, 1821-1824`).

### Non-issues (verified OK)

- New assertion labels `"community-handoff-workflow directory"`, `"... config_dir"`, `"... data_dir"` do not collide with any existing command/metadata/effect labels (which use `<step_name> command`, `step metadata`, `import step effect`, `post-review step effect`). `tests/test_first_run_smoke.py:2113` coordinated-metadata drift test still fails on `input_format` (checked before the new fields) and its regex `"source_name|as_of|input_format|pattern"` excludes the new labels.
- Defaults match fixture and builder: fixture (`tests/test_first_run_smoke.py:655-660`), validator defaults (plan.md:162-164), and `test_community_handoff_workflow_payload_matches_real_builder` inputs (`tests/test_first_run_smoke.py:1393-1400`) all agree on `"/tmp/export"`/`"configs"`/`"data"`.
- Placement after `source_name` and before `expected_community_handoff_workflow_command_parts(...)` is preserved (plan.md:170; current site `scripts/check_first_run_smoke.py:1118-1127`). The three now-unused locals (`directory`, `config_dir`, `data_dir` at `scripts/check_first_run_smoke.py:1119, 1122-1123`) should be deleted when replacing the `expected_commands` call (plan.md:190-202 implies this but does not state it explicitly — ruff F841 would flag them if left).
- Runtime builder, CLI, dashboard, and import semantics remain untouched.

### Recommendation

Do not proceed as written. Add a task-3 step that updates `test_run_first_run_flow_uses_deterministic_local_command_sequence`'s `fake_run_cli` to emit a `community-handoff-workflow` payload whose `directory`/`config_dir`/`data_dir` (and step commands) track `fake_context`'s temp paths, and add `-k "deterministic_local_command_sequence"` to one of the focused verification runs so the fix is confirmed locally before the release gate. With that addition, there are no further blocking issues.
