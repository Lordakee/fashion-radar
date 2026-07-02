## Stage 268 Plan Re-Review — ROW ONE Refresh Command

### Critical

- **C1 — `tests/test_scheduling.py` is entirely out of scope and will break the release gate.** Task 2 rewrites `render_row_one_cron_example` (`scheduling.py:85,103-104`), `render_row_one_systemd_service` (`scheduling.py:139,149-150`), and `render_row_one_local_ops_runbook` (`row_one/ops.py:17,36,41,44,50`), but three unit tests pin the exact old text of exactly those functions and are never touched: `test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log` (`test_scheduling.py:100`, pins `uv run fashion-radar run`, `row-one build`, `{ uv run fashion-radar run ... && `, `--latest-only; }`), `test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron` (`:137`, pins `fashion-radar run`, `row-one build`, `--latest-only`), and `test_render_row_one_systemd_uses_one_timestamp_and_output_env` (`:185`, pins `run`, `build`, `--output-dir "$ROW_ONE_OUTPUT_DIR" --latest-only`). `tests/test_scheduling.py` is not in the plan's Files list. Task 4 Step 3 runs the full `pytest -q`, so release fails.

- **C2 — `test_row_one_scheduling_docs_keep_two_step_refresh_order` (`test_row_one_docs.py:214`) pins the wording Task 3 Step 6 removes.** That test requires `"two-step refresh"`, `` `fashion-radar run` ``, and `` `fashion-radar row-one build --latest-only` `` in `docs/scheduling.md`, while Task 3 Step 6 rewrites `docs/scheduling.md` to drop exactly those phrases. No step updates/removes this test, so `pytest tests/test_row_one_docs.py` (Task 4 Step 1) fails. Prior I1 was only half-fixed (doc updated, its pinning test forgotten).

### Important

- **I1 — Renderer wording vs. smoke validator mismatch.** Task 3 Step 3 asserts `validate_row_one_schedule_output` sees `"ROW ONE scheduled refresh runs the single refresh command."`, but Task 2 Step 3 only changes the command body in the renderer and never instructs it (or the `row-one schedule` CLI) to print that header sentence. The exact emitted wording must be agreed between Task 2 and Task 3 or the smoke validator fails.

- **I2 — `--latest-only` expectations left dangling.** Since refresh is always latest-only, the new snippets/docs no longer print `--latest-only`, yet several assertions still require it: smoke local-ops (`check_first_run_smoke.py:2951`), the three `test_scheduling.py` tests above (`:119,158,198`), and `test_row_one_schedule_prints_refresh_then_build` (`test_row_one_cli.py:401`). The plan only drops it by omission in the renamed schedule test. Each needs an explicit removal instruction.

- **I3 — Smoke helper name drift.** Task 3 Step 3 writes `assert_output_contains(...)`/`assert_output_not_contains(...)`, but the existing helper is `assert_output_contains_text(command_name, output, tuple)` (`check_first_run_smoke.py:1063,1075`) and there is no negative variant. The plan permits adding one, but the implementer must reuse `_contains_text` verbatim and add a consistent negative helper or the script errors before assertions run.

### Minor

- **M1 — Discoverability still partial (prior M1).** `docs/cli-reference.md`, `docs/github-upload-checklist.md`, and `test_row_one_upload_checklist_covers_subcommand_help` (`test_row_one_docs.py:229-243`) still won't list `row-one refresh`. "Docs cover the new command" acceptance is only partially met; no test breakage.
- **M2 — Refresh help insertion order unspecified.** Task 3 Step 2 says keep the deterministic list and real help loop in the same order but not where `refresh` goes. Non-blocking (strict-equality is on captured tuples), but keep Typer registration order sane.
- **M3 — Task 1 CLI test (prior M2).** `collect_configured_sources(now=AS_OF)` is feasible (`workflows.py:146`); also assert `data_dir`/`sources` forwarding to lock parity with `run` (`cli.py:2429`).

### Verified positive

- Command order collect → match → report → ROW ONE site is correct, matching `run` (`cli.py:2429-2438`) + `_write_row_one_site_from_cli_options(..., latest_only=True)` (`cli.py:1472,1479`). ✓
- Scope is clean: no timers, daemon, schema changes, new collectors, LLM calls, or compliance-review features. ✓
- Snippets will call a single `row-one refresh` (no shell chain) once Task 2 lands (pending C1/C2). ✓
- Helper reuse is feasible: `collect_configured_sources`, `match_stored_items`, `write_daily_report_files`, `_write_row_one_site_from_cli_options(latest_only=True)`, `build_row_one_readiness`, and `format_row_one_site_access_message` (→ `Open: http://127.0.0.1:8787` for host 127.0.0.1, `server.py:25`) all exist with the needed signatures. ✓
- Prior C1/C2/C3 fixed in scope (script added to Files; validator + local-ops + help loop updated; deterministic fake + expected list updated together, same order); prior I2 (preserve phrases in `row-one.md`) and I3 (deterministic fake) addressed. ✓

### Verdict

**Do not proceed as written.** The prior blockers are resolved, but C1 (`tests/test_scheduling.py`) and C2 (the scheduling-docs pinning test) are new blocking gaps that will fail the Task 4 release gate. Required fixes before implementation: (1) add `tests/test_scheduling.py` to Files and update its three renderer tests in lockstep with Task 2; (2) explicitly update/remove `test_row_one_scheduling_docs_keep_two_step_refresh_order` in Task 3; (3) reconcile the `--latest-only` and exact emitted-wording expectations across renderer, smoke validator, and docs (I1/I2).
