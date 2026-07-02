# Stage 268 ROW ONE Refresh Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar row-one refresh` as the single local command that collects, matches, writes daily reports, rebuilds the ROW ONE latest-only site, and prints the fixed local URL.

**Architecture:** Keep collection/reporting logic in existing workflow helpers and keep ROW ONE rendering unchanged. Wire a new Typer subcommand in `cli.py`, then update scheduling/local-ops examples to call that command instead of duplicating a two-command shell chain. Tests should monkeypatch workflow helpers to prove ordering without doing network or long-running work.

**Tech Stack:** Python 3.11+, Typer CLI, existing workflow helpers, existing scheduling renderer, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/cli.py`
  - Add `row-one refresh` command.
- Modify: `src/fashion_radar/row_one/ops.py`
  - Update local runbook command text to call `row-one refresh`.
- Modify: `src/fashion_radar/scheduling.py`
  - Update ROW ONE cron/systemd snippets to call `row-one refresh`.
- Modify: `scripts/check_first_run_smoke.py`
  - Update ROW ONE schedule/local-ops smoke assertions and help discovery for `row-one refresh`.
- Modify: `tests/test_row_one_cli.py`
  - Add command behavior/output tests and update schedule/local-ops expectations.
- Modify: `tests/test_scheduling.py`
  - Update ROW ONE cron, systemd, and local-ops renderer tests from the old run/build chain to the single refresh command.
- Modify: `tests/test_first_run_smoke.py`
  - Add refresh help discovery to the deterministic first-run command sequence and update fake ROW ONE outputs.
- Modify: `tests/test_row_one_docs.py`
  - Pin docs language for `row-one refresh`, update scheduling-doc assertions, and preserve ROW ONE cleanup wording.
- Modify: `docs/row-one.md`
  - Document `row-one refresh` as the single local automation command.
- Modify: `docs/first-run.md`
  - Update source-checkout ROW ONE sample to mention refresh.
- Modify: `docs/scheduling.md`
  - Replace the pinned two-step ROW ONE refresh wording with the single-command refresh wording.
- Modify: `README.md`
  - Mention refresh in the first-run/ROW ONE summary.

---

### Task 1: CLI Refresh Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing CLI test**

In `tests/test_row_one_cli.py`, import `fashion_radar.cli as cli_module` and add a test that monkeypatches `collect_configured_sources`, `match_stored_items`, `write_daily_report_files`, and `_write_row_one_site_from_cli_options`. The test must invoke `row-one refresh` and assert:

- call order is `["collect", "match", "report", "row-one"]`;
- `collect_configured_sources(now=AS_OF)` receives the same `as_of`;
- ROW ONE build receives `latest_only=True`;
- output includes `ROW ONE refresh`, `Stored 1 matches`, Markdown/JSON/HTML report paths, site path, app JSON path, manifest path, readiness, and `Open: http://127.0.0.1:8787`.

- [ ] **Step 2: Run the targeted test and verify it fails**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_refresh_runs_daily_pipeline_then_rebuilds_site -q
```

Expected: FAIL because `row-one refresh` does not exist.

- [ ] **Step 3: Implement `row-one refresh`**

In `src/fashion_radar/cli.py`, add `@row_one_app.command(name="refresh")` near the other ROW ONE commands. The command should:

- load source, entity, and scoring configs;
- call `collect_configured_sources`;
- call `match_stored_items`;
- call `write_daily_report_files`;
- call `_write_row_one_site_from_cli_options(..., latest_only=True)`;
- print report paths, ROW ONE site paths, readiness counts, and `format_row_one_site_access_message(host, port)`;
- return `typer.Exit(1)` with clear error text on config/workflow failures.

- [ ] **Step 4: Add help test**

Add `test_row_one_refresh_help_is_discoverable` asserting `row-one refresh --help` exits 0 and shows the command summary plus `--output-dir`, `--host`, and `--port`.

- [ ] **Step 5: Run targeted CLI tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_refresh_runs_daily_pipeline_then_rebuilds_site tests/test_row_one_cli.py::test_row_one_refresh_help_is_discoverable -q
```

Expected: PASS.

---

### Task 2: Scheduling And Local Ops Use Refresh

**Files:**
- Modify: `src/fashion_radar/scheduling.py`
- Modify: `src/fashion_radar/row_one/ops.py`
- Modify: `tests/test_row_one_cli.py`
- Modify: `tests/test_scheduling.py`

- [ ] **Step 1: Add failing scheduling assertions**

Update `test_row_one_schedule_prints_refresh_then_build` into `test_row_one_schedule_prints_single_refresh_command` and assert:

```python
assert "fashion-radar row-one refresh" in result.output
assert "fashion-radar run" not in result.output
assert "fashion-radar row-one build --as-of" not in result.output
```

Update `test_row_one_local_ops_command_prints_runbook` to assert:

```python
assert "fashion-radar row-one refresh" in result.output
assert "fashion-radar row-one build" not in result.output
```

In `tests/test_scheduling.py`, update:

- `test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log`
- `test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron`
- `test_render_row_one_systemd_uses_one_timestamp_and_output_env`

The updated assertions should require `fashion-radar row-one refresh`, `--output-dir`, the shared `AS_OF`, and the existing log/grouping behavior, while removing old direct requirements for `uv run fashion-radar run`, `uv run fashion-radar row-one build`, and an explicit printed `--latest-only` flag.

- [ ] **Step 2: Run targeted tests and verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_schedule_prints_single_refresh_command tests/test_row_one_cli.py::test_row_one_local_ops_command_prints_runbook tests/test_scheduling.py::test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log tests/test_scheduling.py::test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron tests/test_scheduling.py::test_render_row_one_systemd_uses_one_timestamp_and_output_env -q
```

Expected: FAIL because snippets still print `fashion-radar run` plus `row-one build`.

- [ ] **Step 3: Update scheduling snippets**

In `src/fashion_radar/scheduling.py`, update `render_row_one_cron_example` and `render_row_one_systemd_service` so their command body calls:

```bash
uv run fashion-radar row-one refresh --as-of "$AS_OF" --output-dir <output_dir>
```

Keep existing environment variables, grouped cron logging, shared `AS_OF`, and path quoting. Also update the human-readable schedule comment to the exact smoke-pinned sentence:

```text
# ROW ONE scheduled refresh runs the single refresh command.
```

Do not install timers. The refresh command itself always uses latest-only cleanup, so generated snippets do not need to print `--latest-only` explicitly.

- [ ] **Step 4: Update local ops runbook**

In `src/fashion_radar/row_one/ops.py`, replace the manual two-step refresh section with a single `fashion-radar row-one refresh` command using `--config-dir`, `--data-dir`, `--reports-dir`, `--output-dir`, `--as-of "$AS_OF"`, `--host`, and `--port`.

- [ ] **Step 5: Run targeted tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_schedule_prints_single_refresh_command tests/test_row_one_cli.py::test_row_one_local_ops_command_prints_runbook tests/test_scheduling.py::test_render_row_one_cron_uses_one_timestamp_shared_env_and_grouped_log tests/test_scheduling.py::test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron tests/test_scheduling.py::test_render_row_one_systemd_uses_one_timestamp_and_output_env -q
```

Expected: PASS.

---

### Task 3: Docs And First-Run Smoke Discovery

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md`
- Modify: `README.md`

- [ ] **Step 1: Add failing docs assertions**

In `tests/test_row_one_docs.py`, add assertions that `docs/row-one.md` contains `` `row-one refresh` `` and "single local daily refresh command", `docs/first-run.md` contains "ROW ONE refresh", and `README.md` contains "row-one refresh".

- [ ] **Step 2: Update first-run command sequence**

In `tests/test_first_run_smoke.py`, add `("row-one", "refresh", "--help")` to the ROW ONE help entries in `expected_first_run_flow_commands(...)`.

In `scripts/check_first_run_smoke.py`, add `"refresh"` to the ROW ONE help loop so the real smoke flow calls `row-one refresh --help`. Keep the deterministic test strict-equality list in the same order as the real help loop.

- [ ] **Step 3: Update first-run ROW ONE schedule/local-ops assertions**

In `scripts/check_first_run_smoke.py`, update `validate_row_one_schedule_output` so it asserts:

```python
assert_output_contains_text(
    "row-one schedule",
    output,
    (
        "ROW ONE scheduled refresh runs the single refresh command.",
        "fashion-radar row-one refresh",
        "--output-dir",
        "04:00",
    ),
)
assert_output_not_contains_text(
    "row-one schedule",
    output,
    ("fashion-radar run", "fashion-radar row-one build --as-of"),
)
```

There is already `assert_output_contains_text(...)`; add a tiny matching `assert_output_not_contains_text(...)` helper if no negative helper exists.

Also update the local-ops assertion in `run_first_run_flow` so it expects `fashion-radar row-one refresh`, `fashion-radar row-one serve`, `Open from LAN: http://<LAN-IP>:8787`, and `0 4 * * *`, but no longer expects `fashion-radar run` or `fashion-radar row-one build`.

- [ ] **Step 4: Update deterministic fake ROW ONE outputs**

In `tests/test_first_run_smoke.py`, update the fake `row-one schedule` branch to emit the new single refresh command text and update the fake `row-one local-ops` branch to emit `fashion-radar row-one refresh` instead of the old run/build chain.

- [ ] **Step 5: Run docs / smoke tests and verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: FAIL until docs and smoke helper list are updated.

- [ ] **Step 6: Update docs**

In `docs/row-one.md`:
- add `row-one refresh` to the command list;
- describe it as the single local daily refresh command;
- say it runs collect/match/report and then rebuilds ROW ONE with latest-only cleanup;
- keep `row-one schedule` documented as snippet-only.
- preserve existing generated-file and cleanup language that tests pin, including `fashion-radar run`, `--latest-only`, and the fact that schedule/local-ops do not install timers, unless the matching tests are deliberately updated in this stage.

In `docs/first-run.md`, include a `row-one refresh` command in the ROW ONE sample flow.

In `docs/scheduling.md`, replace the ROW ONE "two-step refresh" wording with the new single-command `row-one refresh` wording while preserving the warning that scheduled jobs should not overlap.

In `tests/test_row_one_docs.py`, update `test_row_one_scheduling_docs_keep_two_step_refresh_order` to a refresh-command test. It should require `row-one refresh`, `"single refresh command"`, and the overlap warning, and it should no longer require `"two-step refresh"` or the exact old `fashion-radar run` -> `fashion-radar row-one build --latest-only` order.

In `README.md`, mention that the local ROW ONE path now has a single refresh command for 04:00 automation.

- [ ] **Step 7: Run docs / smoke tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: PASS.

---

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-268-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-268-code-review.md`

- [ ] **Step 1: Run focused checks**

Run:

```bash
git diff --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_smoke.py tests/test_scheduling.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/cli.py src/fashion_radar/scheduling.py src/fashion_radar/row_one/ops.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_smoke.py tests/test_scheduling.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/cli.py src/fashion_radar/scheduling.py src/fashion_radar/row_one/ops.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_smoke.py tests/test_scheduling.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: all pass.

- [ ] **Step 2: Run opencode code review**

Create `docs/reviews/opencode-stage-268-code-review-prompt.md`, run opencode with `--model zhipuai-coding-plan/glm-5.2 --variant max`, and clean review artifact process chatter before release hygiene.

- [ ] **Step 3: Run full release gate**

Run:

```bash
rm -rf dist
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config build
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py dist
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: all pass.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/cli.py src/fashion_radar/scheduling.py src/fashion_radar/row_one/ops.py scripts/check_first_run_smoke.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_smoke.py tests/test_scheduling.py docs/row-one.md docs/first-run.md docs/scheduling.md README.md docs/reviews/opencode-stage-268-code-review-prompt.md docs/reviews/opencode-stage-268-code-review.md docs/reviews/opencode-stage-268-plan-review-prompt.md docs/reviews/opencode-stage-268-plan-review.md docs/reviews/opencode-stage-268-plan-rereview-prompt.md docs/reviews/opencode-stage-268-plan-rereview.md docs/reviews/opencode-stage-268-plan-final-review-prompt.md docs/reviews/opencode-stage-268-plan-final-review.md docs/superpowers/specs/2026-07-02-stage-268-row-one-refresh-command-design.md docs/superpowers/plans/2026-07-02-stage-268-row-one-refresh-command-plan.md
git diff --cached --check
git commit -m "Stage 268: add ROW ONE refresh command"
git push origin main
```

Expected: commit and push succeed.
