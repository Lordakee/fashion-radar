# Stage 265 Plan Review — ROW ONE Local Daily Ops

## Verdict: Approve with revisions (one Important blocker to fix before coding)

The approach is sound: print-only runbook, reuses `render_row_one_cron_example` (scheduling.py:85) and `format_row_one_site_access_message` (server.py:15), mirrors the existing `row-one schedule` command shape (cli.py:1518), and the boundary is clean (no file/DB/server/cron side effects — `format_row_one_site_access_message` is pure string work). Scope, `row-one-app/v1` JSON, and scoring/ranking/collection semantics are untouched. No circular import (verified no `row_one` submodule imports `scheduling`).

## Critical
None.

## Important
**I-1. Task 1 unit test assertions contradict the Task 1 renderer (Step 4 "Expected: PASS" will fail).**
The test asserts contiguous substrings (plan lines 59–60):
```python
assert "fashion-radar run --as-of \"$AS_OF\"" in output
assert "fashion-radar row-one build --as-of \"$AS_OF\"" in output
```
But the renderer (plan lines 133–134) injects `--config-dir/--data-dir/--reports-dir` (and `--output-dir` for build) between the verb and `--as-of`, producing e.g. `fashion-radar run --config-dir /repo/configs --data-dir ... --as-of "$AS_OF"`. The asserted substrings never appear contiguously, so both assertions fail. Note the design doc's Proposed Surface (lines 37–38) shows the *minimal* form without dirs, so design and renderer also disagree on which is canonical.
**Fix:** either split into token checks (`"fashion-radar run"`, `'--as-of "$AS_OF"'`, etc., like the CLI test does) or assert the full rendered line. Reconcile design-vs-plan on whether manual commands carry the dir flags (keeping them is more pasteable/correct).

## Minor
- **M-1 Layering.** Putting `render_row_one_local_ops_runbook` in `scheduling.py` + `from fashion_radar.row_one.server import ...` makes the previously leaf-level `scheduling` module depend on the `row_one` package. Not a cycle, but consider housing the renderer under `row_one/` (e.g. `row_one/ops.py`) so `scheduling` stays a pure leaf and the dependency direction is one-way.
- **M-2 Help-coverage asymmetry.** Task 4 adds `row-one local-ops` to the upload-checklist help-smoke list and cli-reference, but Task 3 does not add `row-one local-ops --help` to the deterministic command sequence (test_first_run_smoke.py:1846–1850), and `test_row_one_upload_checklist_covers_subcommand_help` / `test_row_one_cli_docs_list_build_preview_serve_and_schedule_commands` (test_row_one_docs.py:156,189) aren't updated to require it. Pick one side: either omit from help-smoke, or add the `--help` call + expected tuple + docs-test assertions.
- **M-3 Docs-test mapping.** Task 4 Step 1 lists required strings but doesn't bind them to test functions; add `row-one local-ops` to `test_row_one_docs_include_user_required_phrases` and a bullet to the cli-reference test.
- **M-4 Missing import.** Task 1 Step 1 test omits the `from fashion_radar.scheduling import render_row_one_local_ops_runbook` line in `tests/test_scheduling.py`.
- **M-5 Mock placement.** Task 3 Step 2 `fake_run_cli` handler must sit before the `stdout_by_command.get(command_name, "")` fallthrough (alongside the schedule/preview handlers at test_first_run_smoke.py:4213–4249); state the insertion point explicitly.
- **M-6 Storage note wording.** "under a marked `.row-one-site` directory" is imprecise — the marker is a file `output_dir/.row-one-site` (render.py:18,39) and cleanup only removes `GENERATED_CHILDREN`. Prefer "inside a directory marked with a `.row-one-site` file".
- **M-7 Style.** Redundant `\"` escapes inside the triple-quoted f-string are harmless but unnecessary.

**Recommendation:** resolve I-1 (and ideally M-1/M-2) in the plan, then proceed. All other tasks (CLI command, smoke wiring, docs, release gate) are executable as written once the renderer/test are reconciled.
