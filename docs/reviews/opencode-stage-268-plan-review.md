## Stage 268 Plan Review — ROW ONE Refresh Command

### Critical

- **C1 — Smoke script pins the old two-step schedule chain; plan never updates it.** `validate_row_one_schedule_output` (`scripts/check_first_run_smoke.py:1074-1086`, called at `:2852`) hard-asserts `fashion-radar run`, `fashion-radar row-one build`, and `--latest-only` with strict ordering. Task 2 rewrites `render_row_one_cron_example`/`render_row_one_systemd_service` to emit `row-one refresh`, so `python scripts/check_first_run_smoke.py --repo-root .` (Task 4 Step 1, `plan:216`; release gate `plan:240`) will fail. `scripts/check_first_run_smoke.py` is not in the plan's Files list and no step touches this validator.

- **C2 — Smoke script pins old local-ops text; plan never updates it.** `run_first_run_flow` asserts local-ops output contains `fashion-radar run` and `fashion-radar row-one build` (`scripts/check_first_run_smoke.py:2941-2953`). Task 2 Step 4 replaces the run+build section with a single `row-one refresh`, so this real-subprocess assertion also fails in the smoke script. Not addressed.

- **C3 — Adding `("row-one","refresh","--help")` to the test's expected list without adding the call to the script breaks strict-equality.** Task 3 Step 2 edits `expected_first_run_flow_commands` only. The actual help loop (`scripts/check_first_run_smoke.py:2843-2850`) is unchanged, so `run_first_run_flow` never invokes `row-one refresh --help`. `test_run_first_run_flow_uses_deterministic_local_command_sequence` asserts `captured == expected_first_run_flow_commands(...)` (`tests/test_first_run_smoke.py:4439`), so it fails. (Mirror image of the stage-267 review's finding.)

### Important

- **I1 — `docs/scheduling.md` + its test still describe a "two-step refresh".** `docs/scheduling.md:49-75` and `test_row_one_scheduling_docs_keep_two_step_refresh_order` (`tests/test_row_one_docs.py:214-226`) pin `fashion-radar run` + `fashion-radar row-one build --latest-only`. Rendered snippets become single-command, so docs contradict the output. Plan touches neither.

- **I2 — `test_row_one_docs_include_user_required_phrases` pins `fashion-radar run` and `--latest-only` in `docs/row-one.md`** (`tests/test_row_one_docs.py:66-89`). Task 3's row-one.md rewrite centers on `row-one refresh` with no instruction to preserve these phrases (or update the test) — likely breakage.

- **I3 — Deterministic test fake is stale and must move in lockstep.** The fake schedule/local-ops stdout (`tests/test_first_run_smoke.py:4247-4251`, `4339-4346`) emits the old two-step text. Once C1/C2 validators are corrected to expect `row-one refresh`, this fake must be updated too, or the deterministic test fails. Plan never touches the fake.

### Minor

- **M1 — Discoverability gap.** `docs/cli-reference.md` (`test_row_one_cli_docs_list_...:195-211`) and `docs/github-upload-checklist.md` (`test_row_one_upload_checklist_...:229-243`) aren't updated to list `row-one refresh`, so "docs cover the new command" is only partially met. (No test breakage.)
- **M2 — Task 1 CLI test** asserts `collect_configured_sources(now=AS_OF)`; feasible (signature confirmed at `workflows.py:146`), but should also assert `data_dir`/`sources` forwarding to lock parity with `run` (`cli.py:2429`).

### Scope / order check
Command order (collect → match → report → ROW ONE site) is correct and matches `run` (`cli.py:2424`) plus `_write_row_one_site_from_cli_options(..., latest_only=True)` (`cli.py:1472`). Scope is clean: no timers, daemon, schema, collectors, LLM, or compliance-review. Reused helpers (`build_row_one_readiness`, `format_row_one_site_access_message`→`Open: http://127.0.0.1:8787`) are all present and correct.

### Verdict
**Do not proceed as written.** C1–C3 each independently break a release-gate or named test the plan expects to pass. Required fix: add `scripts/check_first_run_smoke.py` to Files and add one task updating, *together*, `validate_row_one_schedule_output`, the local-ops smoke assertion (`:2941`), the `run_first_run_flow` help loop (`:2843`), and the deterministic test's fake+expected list. Reconcile I1/I2 (scheduling.md + row-one.md pinned phrases) before implementing.
