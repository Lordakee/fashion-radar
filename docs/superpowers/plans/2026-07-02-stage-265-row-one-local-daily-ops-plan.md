# Stage 265 ROW ONE Local Daily Ops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a print-only ROW ONE local daily-ops command that tells users how to refresh the ROW ONE site at 04:00, serve it on a fixed IP:port, and keep only the latest generated site during local testing.

**Architecture:** Keep this as a pure ROW ONE runbook/rendering layer. Add `fashion_radar.row_one.ops.render_row_one_local_ops_runbook(...)`, reuse existing scheduling and server helpers, and expose it through a new `fashion-radar row-one local-ops` Typer subcommand. The command prints deterministic commands and does not install timers, start servers, build sites, read SQLite, or mutate files.

**Tech Stack:** Python 3.11+, Typer CLI, existing `fashion_radar.scheduling` helpers, existing ROW ONE server URL formatting, pytest, ruff, uv.

---

## Files

- Create: `src/fashion_radar/row_one/ops.py`
  - Add `render_row_one_local_ops_runbook(...)`.
- Modify: `src/fashion_radar/row_one/__init__.py`
  - Export `render_row_one_local_ops_runbook`.
- Modify: `src/fashion_radar/cli.py`
  - Add `row-one local-ops` command using existing path/time/host/port options.
- Modify: `scripts/check_first_run_smoke.py`
  - Add help and output smoke coverage for `row-one local-ops --time 04:00`.
- Modify: `scripts/check_package_archives.py`
  - Add `src/fashion_radar/row_one/ops.py` to required source files.
- Modify: `tests/test_scheduling.py`
  - Add unit tests for the runbook renderer.
- Modify: `tests/test_row_one_cli.py`
  - Add CLI help/invocation tests.
- Modify: `tests/test_first_run_smoke.py`
  - Update deterministic command sequence mock for the new smoke command.
- Modify: `tests/test_package_archives.py`
  - Add `src/fashion_radar/row_one/ops.py` to the sdist fixture.
- Modify: `tests/test_row_one_docs.py`
  - Add docs assertions for `row-one local-ops`.
- Modify: `docs/row-one.md`, `docs/cli-reference.md`, `docs/github-upload-checklist.md`, `README.md`
  - Document the local-ops command and the non-installing boundary.

---

### Task 1: Pure Local-Ops Runbook Renderer

**Files:**
- Create: `src/fashion_radar/row_one/ops.py`
- Modify: `src/fashion_radar/row_one/__init__.py`
- Test: `tests/test_scheduling.py`

- [ ] **Step 1: Write failing renderer tests**

Add import and tests in `tests/test_scheduling.py`:

```python
from fashion_radar.row_one.ops import render_row_one_local_ops_runbook


def test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron() -> None:
    output = render_row_one_local_ops_runbook(
        project_dir="/repo",
        config_dir="/repo/configs",
        data_dir="/repo/data",
        reports_dir="/repo/reports",
        output_dir="/repo/reports/row-one/site",
        time="04:00",
        host="0.0.0.0",
        port=8787,
    )

    assert "ROW ONE local daily ops" in output
    assert "AS_OF=\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" in output
    assert "fashion-radar run" in output
    assert "fashion-radar row-one build" in output
    assert "--config-dir /repo/configs" in output
    assert "--data-dir /repo/data" in output
    assert "--reports-dir /repo/reports" in output
    assert "--output-dir /repo/reports/row-one/site" in output
    assert "--as-of \"$AS_OF\"" in output
    assert "--latest-only" in output
    assert "fashion-radar row-one preview" in output
    assert "--dry-run-serve-url" in output
    assert "fashion-radar row-one serve" in output
    assert "--host 0.0.0.0" in output
    assert "--port 8787" in output
    assert "Open locally: http://127.0.0.1:8787" in output
    assert "Open from LAN: http://<LAN-IP>:8787" in output
    assert "0 4 * * *" in output
    assert "/repo/reports/row-one/site" in output
    assert "directory marked with a .row-one-site file" in output


def test_render_row_one_local_ops_runbook_rejects_invalid_time() -> None:
    with pytest.raises(ValueError, match="time must be in 24-hour HH:MM format"):
        render_row_one_local_ops_runbook(
            project_dir="/repo",
            config_dir="/repo/configs",
            data_dir="/repo/data",
            reports_dir="/repo/reports",
            output_dir="/repo/reports/row-one/site",
            time="4am",
            host="127.0.0.1",
            port=8787,
        )
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_scheduling.py::test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron tests/test_scheduling.py::test_render_row_one_local_ops_runbook_rejects_invalid_time -q
```

Expected: FAIL because `fashion_radar.row_one.ops` is not defined.

- [ ] **Step 3: Implement renderer**

Create `src/fashion_radar/row_one/ops.py`:

```python
from __future__ import annotations

import shlex

from fashion_radar.row_one.server import format_row_one_site_access_message
from fashion_radar.scheduling import (
    raw_as_of_shell,
    render_row_one_cron_example,
    validate_hhmm,
)


def _shell_quote(value: str) -> str:
    return shlex.quote(value)


def render_row_one_local_ops_runbook(
    *,
    project_dir: str,
    config_dir: str,
    data_dir: str,
    reports_dir: str,
    output_dir: str,
    time: str,
    host: str,
    port: int,
) -> str:
    validate_hhmm(time)
    access_message = format_row_one_site_access_message(host, port)
    cron_snippet = render_row_one_cron_example(
        project_dir=project_dir,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        time=time,
    ).rstrip()
    return f"""ROW ONE local daily ops

Manual refresh:
AS_OF="{raw_as_of_shell()}"
fashion-radar run --config-dir {_shell_quote(config_dir)} --data-dir {_shell_quote(data_dir)} --reports-dir {_shell_quote(reports_dir)} --as-of "$AS_OF"
fashion-radar row-one build --config-dir {_shell_quote(config_dir)} --data-dir {_shell_quote(data_dir)} --reports-dir {_shell_quote(reports_dir)} --output-dir {_shell_quote(output_dir)} --as-of "$AS_OF" --latest-only

Preview before serving:
fashion-radar row-one preview --config-dir {_shell_quote(config_dir)} --data-dir {_shell_quote(data_dir)} --reports-dir {_shell_quote(reports_dir)} --output-dir {_shell_quote(output_dir)} --as-of "$AS_OF" --latest-only --host {_shell_quote(host)} --port {port} --dry-run-serve-url

Serve fixed local URL:
fashion-radar row-one serve --site-dir {_shell_quote(output_dir)} --host {_shell_quote(host)} --port {port}

Access:
{access_message}

Daily 04:00-style cron snippet:
{cron_snippet}

Storage:
--latest-only keeps only the latest generated ROW ONE site children inside a directory marked with a .row-one-site file.
"""
```

In `src/fashion_radar/row_one/__init__.py`, export:

```python
from fashion_radar.row_one.ops import render_row_one_local_ops_runbook
```

and add `"render_row_one_local_ops_runbook"` to `__all__`.

- [ ] **Step 4: Run tests and verify they pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_scheduling.py::test_render_row_one_local_ops_runbook_prints_refresh_serve_and_cron tests/test_scheduling.py::test_render_row_one_local_ops_runbook_rejects_invalid_time -q
```

Expected: PASS.

---

### Task 1b: Package Archive Guardrail

**Files:**
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add required source path**

Add `src/fashion_radar/row_one/ops.py` to `SDIST_REQUIRED_PATHS` in `scripts/check_package_archives.py`.

- [ ] **Step 2: Add fixture source path**

Add `src/fashion_radar/row_one/ops.py` to `SDIST_FILES` in `tests/test_package_archives.py`.

- [ ] **Step 3: Run archive guard tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
```

Expected: PASS.

---

### Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add failing CLI tests**

In `tests/test_row_one_cli.py`, add:

```python
def test_row_one_local_ops_command_prints_runbook(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "local-ops",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local daily ops" in result.output
    assert "fashion-radar run" in result.output
    assert "fashion-radar row-one build" in result.output
    assert "fashion-radar row-one preview" in result.output
    assert "fashion-radar row-one serve" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert "0 4 * * *" in result.output


def test_row_one_local_ops_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "local-ops", "--help"])

    assert result.exit_code == 0
    assert "Print ROW ONE local daily ops runbook" in result.output
    assert "--time" in result.output
    assert "--host" in result.output
    assert "--port" in result.output
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_local_ops_command_prints_runbook tests/test_row_one_cli.py::test_row_one_local_ops_help_is_discoverable -q
```

Expected: FAIL because `local-ops` is not registered.

- [ ] **Step 3: Implement CLI command**

In `src/fashion_radar/cli.py`, import `render_row_one_local_ops_runbook` from `fashion_radar.row_one.ops`.

Add under the ROW ONE command group:

```python
@row_one_app.command(name="local-ops")
def row_one_local_ops(
    project_dir: Path = PROJECT_DIR_OPTION,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    time: str = typer.Option("04:00", help="Daily ROW ONE refresh time in 24-hour HH:MM format."),
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
) -> None:
    """Print ROW ONE local daily ops runbook without installing anything."""
    try:
        typer.echo(
            render_row_one_local_ops_runbook(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                output_dir=str(output_dir),
                time=time,
                host=host,
                port=port,
            )
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
```

- [ ] **Step 4: Run tests and verify they pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_cli.py::test_row_one_local_ops_command_prints_runbook tests/test_row_one_cli.py::test_row_one_local_ops_help_is_discoverable -q
```

Expected: PASS.

---

### Task 3: First-Run Smoke Coverage

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add help smoke command to first-run script**

In the existing ROW ONE help loop in `scripts/check_first_run_smoke.py`, add:

```python
("row-one", "local-ops", "--help"),
```

- [ ] **Step 2: Add local-ops smoke command to first-run script**

After `row-one preview` smoke validation, call:

```python
row_one_local_ops = run_cli(
    context,
    "row-one",
    "local-ops",
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--reports-dir",
    str(context.reports_dir),
    "--output-dir",
    str(row_one_output_dir),
    "--time",
    "04:00",
    "--host",
    "0.0.0.0",
    "--port",
    "8787",
).stdout
assert_output_contains_text(
    "row-one local-ops",
    row_one_local_ops,
    (
        "ROW ONE local daily ops",
        "fashion-radar run",
        "fashion-radar row-one build",
        "fashion-radar row-one preview",
        "fashion-radar row-one serve",
        "Open from LAN: http://<LAN-IP>:8787",
        "--latest-only",
    ),
)
```

- [ ] **Step 3: Update deterministic command sequence test**

In `tests/test_first_run_smoke.py`, add this expected help tuple inside the existing ROW ONE help block, immediately after `("row-one", "preview", "--help")`:

```python
("row-one", "local-ops", "--help"),
```

Add this full invocation tuple after the existing `row-one preview` full invocation tuple:

```python
(
    "row-one",
    "local-ops",
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--reports-dir",
    str(context.reports_dir),
    "--output-dir",
    str(context.reports_dir / "row-one" / "site"),
    "--time",
    "04:00",
    "--host",
    "0.0.0.0",
    "--port",
    "8787",
),
```

In `fake_run_cli`, insert this handler alongside the existing `row-one schedule` and `row-one preview` handlers, before the `stdout_by_command.get(command_name, "")` fallthrough. Keep it scoped to the full runbook invocation so the `row-one local-ops --help` call can use the generic zero-output mock:

```python
if args[:2] == ("row-one", "local-ops") and "--help" not in args:
    return subprocess.CompletedProcess(
        ["python", "-m", "fashion_radar", *args],
        0,
        stdout=(
            "ROW ONE local daily ops\n"
            "fashion-radar run\n"
            "fashion-radar row-one build --latest-only\n"
            "fashion-radar row-one preview --dry-run-serve-url\n"
            "fashion-radar row-one serve --host 0.0.0.0 --port 8787\n"
            "Open from LAN: http://<LAN-IP>:8787\n"
        ),
        stderr="",
    )
```

- [ ] **Step 4: Run focused smoke tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: PASS.

---

### Task 4: Docs And Help Surface

**Files:**
- Modify: `docs/row-one.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `README.md`
- Test: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs assertions**

Update `tests/test_row_one_docs.py`:

- In `test_row_one_docs_include_user_required_phrases`, require:

```python
"row-one local-ops"
"fixed IP:port"
"Open from LAN: http://<LAN-IP>:8787"
"prints snippets only"
"does not install timers"
```

- In the CLI docs test, require:

```python
"`row-one local-ops`"
```

- In the upload checklist help-smoke test, require:

```python
"row-one local-ops --help"
```

- [ ] **Step 2: Update docs**

Add `row-one local-ops` to:

- `docs/row-one.md` Quick Start, Commands, Scheduling sections.
- `docs/cli-reference.md` Daily site command list and command bullet.
- `docs/github-upload-checklist.md` installed-wheel help smoke list.
- `README.md` ROW ONE quick run section.

The docs must state that `local-ops` prints a runbook only, prints snippets only, and does not install cron/systemd timers or start the server.

- [ ] **Step 3: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

---

### Task 5: Review, Release Gate, Commit

**Files:**
- Create: `docs/reviews/opencode-stage-265-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-265-plan-review.md`
- Create: `docs/reviews/opencode-stage-265-plan-rereview-prompt.md`
- Create: `docs/reviews/opencode-stage-265-plan-rereview.md`
- Create: `docs/reviews/opencode-stage-265-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-265-code-review.md`

- [ ] **Step 1: Plan rereview before coding**

Run local opencode rereview before implementation:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-265-plan-rereview-prompt.md)"
```

Proceed only if no Critical or Important findings remain.

- [ ] **Step 2: Full verification**

Run:

```bash
rm -rf dist
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: PASS.

- [ ] **Step 3: Code review**

Run local opencode code/release review. Capture only the clean review body in `docs/reviews/opencode-stage-265-code-review.md`.

- [ ] **Step 4: Commit and push**

Run:

```bash
git add -A
git diff --cached --check
git commit -m "Stage 265: add ROW ONE local daily ops runbook"
git push origin main
```

Expected: pushed to `origin/main`.
