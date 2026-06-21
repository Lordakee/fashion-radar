## Stage 153 Code Review — `community-handoff-top-level-field-exactness`

### Verification performed
- Empirically confirmed RED: checked out base `acaee74` in an isolated worktree, applied only the new tests → all 3 drift tests fail with `DID NOT RAISE SmokeError` (the old validator echoed payload paths into expected commands, so consistent drift passed silently).
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q` → **121 passed**.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .` → **First-run sample smoke passed.**
- `ruff check` / `ruff format --check` on both files → clean. `git diff --check` → clean.

### Findings

**No blocking issues.** No important or minor issues found.

| # | Aspect | Verdict | Reference |
|---|--------|---------|-----------|
| 1 | New tests prove the prior drift gap with true RED cases | ✅ Pass | `tests/test_first_run_smoke.py:2137-2170`; empirically RED against base (`DID NOT RAISE` on all 3). The `replace_workflow_command_fragments` calls keep commands internally consistent so the old validator had nothing to catch — isolating exactly the field-level gap. | 
| 2 | Validator checks exact `directory`/`config_dir`/`data_dir` equality with caller-supplied values | ✅ Pass | `scripts/check_first_run_smoke.py:1089-1095` (kw-only signature), `:1126-1128` (assertions placed *before* command synthesis, as the design requires). The same `expected_*` values feed command synthesis at `:1134-1142`, so field checks and command checks are now independent layers. |
| 3 | `run_first_run_flow(context)` passes real temp paths | ✅ Pass | `scripts/check_first_run_smoke.py:2502-2508` — `str(context.exports_dir/config_dir/data_dir)`, matching the CLI args fed to `community-handoff-workflow` at `:2482-2500`. |
| 4 | Deterministic test returns a temp-path handoff payload | ✅ Pass | `tests/test_first_run_smoke.py:3572-3580` — uses `build_community_handoff_workflow(directory=context.exports_dir, config_dir=context.config_dir, data_dir=context.data_dir, …)`, aligned with the validator call inside `run_first_run_flow`. |
| 5 | Existing command/metadata/effect labels unchanged | ✅ Pass | Import-step effect `updates_local_imports` (`:1157-1161`), post-review effect `print_only` (`:1163-1170`), and `EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA` block (`:1183-1187`) are byte-for-byte unchanged. Existing drift tests (`:2226-2285`) still pass. |
| 6 | Runtime behavior unchanged | ✅ Pass | No edits under `src/`; only the test-time validator and its callers changed. Defaults (`/tmp/export`, `configs`, `data`) preserve the fixture contract, so all prior unit tests pass unmodified. |
| 7 | Verification coverage sufficient, incl. direct script run | ✅ Pass | Direct `scripts/check_first_run_smoke.py --repo-root .` exercised and passing. |

### Notes (non-blocking, no action required)
- The kw-only defaults (`/tmp/export`, `configs`, `data`) intentionally match the fixture payload, so the validator's contract is backward-compatible — no other call sites needed updating (grep confirms the only callers are the unit tests with defaults and the one `run_first_run_flow` site with explicit paths).
- `build_community_handoff_workflow` accepts `Path` and internally `str()`-coerces (`community_handoff_workflow.py:53-55`); `run_first_run_flow` passes `str(context.*)`, so serialization is symmetric with `model_dump_json()`.

The change is minimal, correctly scoped to the two files, matches the design/plan exactly, and closes the top-level path-drift gap with genuine RED→GREEN coverage.
