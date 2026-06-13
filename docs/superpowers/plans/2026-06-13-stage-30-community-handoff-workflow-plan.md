# Stage 30 Community Handoff Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar community-handoff-workflow DIRECTORY`, a local print-only checklist command for the community signal directory handoff path.

**Architecture:** Add a focused workflow builder module that mirrors `imported_review_workflow`: Pydantic output models, deterministic shell-command generation, and a table renderer. Wire it into Typer with a thin CLI wrapper and update docs around the existing community handoff/import workflow.

**Tech Stack:** Python 3.11, Typer, Pydantic v2, `shlex.join`, pytest, ruff, existing Markdown docs. No new dependencies.

---

## Boundaries

In scope:

- New module `src/fashion_radar/community_handoff_workflow.py`.
- New tests `tests/test_community_handoff_workflow.py`.
- CLI import/option/command/tests in `src/fashion_radar/cli.py` and
  `tests/test_cli.py`.
- Docs updates in README, changelog, architecture, community signal docs,
  source boundaries, candidate discovery if needed, and upload checklist.
- Process review artifacts under `docs/reviews/`.

Out of scope:

- scraping, crawling, platform automation, source acquisition, browser
  automation, login, account automation, watchers, schedulers, source/platform
  connectors;
- reading the supplied directory;
- validating files;
- importing rows;
- opening or writing SQLite;
- report/dashboard/digest/config/entity generation;
- dependency or `uv.lock` changes.

## Task 0: Preflight

**Files:**
- No edits.

- [ ] **Step 1: Check current worktree**

Run:

```bash
git status --short --branch
git diff --cached --name-only
git status --short -- uv.lock
```

Expected:

- branch is `main`;
- no staged changes;
- `uv.lock` may show the known unstaged mirror diff and must remain unstaged.

## Task 1: Workflow Builder Module

**Files:**
- Create: `src/fashion_radar/community_handoff_workflow.py`
- Create: `tests/test_community_handoff_workflow.py`

- [ ] **Step 1: Write tests for deterministic workflow output**

Create `tests/test_community_handoff_workflow.py` with tests that assert:

```python
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.community_handoff_workflow import (
    CommunityHandoffWorkflow,
    CommunityHandoffWorkflowStep,
    build_community_handoff_workflow,
    render_community_handoff_workflow_table,
)


def test_build_community_handoff_workflow_returns_deterministic_steps() -> None:
    workflow = build_community_handoff_workflow(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        input_format="csv",
        pattern="*.csv",
        as_of=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
        source_name="Community Tool Export",
    )

    assert workflow.directory == "exports"
    assert workflow.config_dir == "configs"
    assert workflow.data_dir == "data"
    assert workflow.input_format == "csv"
    assert workflow.pattern == "*.csv"
    assert workflow.as_of == "2026-06-13T12:00:00+00:00"
    assert workflow.source_name == "Community Tool Export"
    assert workflow.execution_mode == "print_only"
    assert workflow.step_count == 5
    assert [step.name for step in workflow.steps] == [
        "lint_handoff_directory",
        "preview_candidate_phrases",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert [step.suggested_effect for step in workflow.steps] == [
        "read_only",
        "read_only",
        "read_only",
        "updates_local_imports",
        "print_only",
    ]
```

Add exact command assertions:

```python
assert workflow.steps[0].command == (
    "fashion-radar community-signal-lint-dir exports --input-format csv "
    "--pattern '*.csv' --source-name 'Community Tool Export' --strict"
)
assert workflow.steps[1].command == (
    "fashion-radar community-candidates-dir exports --input-format csv "
    "--pattern '*.csv' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 "
    "--source-name 'Community Tool Export'"
)
assert workflow.steps[2].command == (
    "fashion-radar import-signals-dir exports --format csv --pattern '*.csv' "
    "--data-dir data --source-name 'Community Tool Export' "
    "--imported-at 2026-06-13T12:00:00+00:00 --dry-run"
)
assert workflow.steps[3].command == (
    "fashion-radar import-signals-dir exports --format csv --pattern '*.csv' "
    "--data-dir data --source-name 'Community Tool Export' "
    "--imported-at 2026-06-13T12:00:00+00:00"
)
assert workflow.steps[4].command == (
    "fashion-radar imported-review-workflow --config-dir configs --data-dir data "
    "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Community Tool Export'"
)
```

- [ ] **Step 2: Add quoting/source/table tests**

Add tests for:

```python
def test_build_community_handoff_workflow_quotes_paths_pattern_and_source_name() -> None:
    workflow = build_community_handoff_workflow(
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        input_format="json",
        pattern="*.json",
        as_of="2026-06-13T12:00:00Z",
        source_name="Community | Tool Export",
    )

    assert workflow.source_name == "Community | Tool Export"
    assert "'exports ? # & %'" in workflow.steps[0].command
    assert "--pattern '*.json'" in workflow.steps[0].command
    assert "--source-name 'Community | Tool Export'" in workflow.steps[0].command
    assert "--config-dir 'config ? # & %'" in workflow.steps[1].command
    assert "--data-dir 'data ? # & %'" in workflow.steps[2].command


def test_build_community_handoff_workflow_blank_source_name_uses_default() -> None:
    workflow = build_community_handoff_workflow(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00Z",
        source_name=" ",
    )

    assert workflow.source_name == "Community Tool Export"
    assert "--source-name 'Community Tool Export'" in workflow.steps[0].command


def test_render_community_handoff_workflow_table_sanitizes_cells() -> None:
    workflow = CommunityHandoffWorkflow(
        directory="./exports",
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        source_name="Community | Tool",
        step_count=1,
        steps=[
            CommunityHandoffWorkflowStep(
                order=1,
                name="first | step\\nname",
                purpose="Read | local\\nstate.",
                command="fashion-radar community-signal-lint-dir ./exports",
                suggested_effect="read_only",
            )
        ],
    )

    assert render_community_handoff_workflow_table(workflow) == [
        "Community signal handoff workflow.",
        "Execution mode: print_only",
        "Commands were not executed.",
        "Directory: ./exports",
        "Input format: csv",
        "Pattern: *.csv",
        "As of: 2026-06-13T12:00:00+00:00",
        "Config dir: ./configs",
        "Data dir: ./data",
        "Source name: Community / Tool",
        "Steps: 1",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | first / step name | read_only | Read / local state. | "
        "fashion-radar community-signal-lint-dir ./exports",
    ]


def test_build_community_handoff_workflow_invalid_as_of_raises() -> None:
    with pytest.raises(ValueError):
        build_community_handoff_workflow(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            input_format="csv",
            pattern="*.csv",
            as_of="not-a-date",
            source_name="Community Tool Export",
        )
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_handoff_workflow.py -q
```

Expected: fails with `ModuleNotFoundError` or missing symbols.

- [ ] **Step 4: Implement workflow builder**

Create `src/fashion_radar/community_handoff_workflow.py`:

```python
from __future__ import annotations

import shlex
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.importers.manual_signals import ManualSignalFormat
from fashion_radar.utils.dates import parse_datetime_utc

DEFAULT_COMMUNITY_SOURCE_NAME = "Community Tool Export"


class CommunityHandoffWorkflowStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    name: str
    purpose: str
    command: str
    suggested_effect: Literal["read_only", "updates_local_imports", "print_only"]


class CommunityHandoffWorkflow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    as_of: str
    config_dir: str
    data_dir: str
    source_name: str = DEFAULT_COMMUNITY_SOURCE_NAME
    execution_mode: Literal["print_only"] = "print_only"
    step_count: int = 0
    steps: list[CommunityHandoffWorkflowStep] = Field(default_factory=list)


def build_community_handoff_workflow(
    *,
    directory: Path,
    config_dir: Path,
    data_dir: Path,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of: str | datetime,
    source_name: str = DEFAULT_COMMUNITY_SOURCE_NAME,
) -> CommunityHandoffWorkflow:
    as_of_text = parse_datetime_utc(as_of).isoformat()
    source_text = source_name.strip() or DEFAULT_COMMUNITY_SOURCE_NAME
    directory_text = str(directory)
    config_text = str(config_dir)
    data_text = str(data_dir)

    steps = [
        CommunityHandoffWorkflowStep(
            order=1,
            name="lint_handoff_directory",
            purpose="Lint local community handoff files before import.",
            command=_shell_command(
                "fashion-radar",
                "community-signal-lint-dir",
                directory_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_text,
                "--strict",
            ),
            suggested_effect="read_only",
        ),
        CommunityHandoffWorkflowStep(
            order=2,
            name="preview_candidate_phrases",
            purpose="Preview aggregate candidate phrases before import.",
            command=_shell_command(
                "fashion-radar",
                "community-candidates-dir",
                directory_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_text,
                "--as-of",
                as_of_text,
                "--source-name",
                source_text,
            ),
            suggested_effect="read_only",
        ),
        CommunityHandoffWorkflowStep(
            order=3,
            name="dry_run_directory_import",
            purpose="Validate matched local files through the importer without writing rows.",
            command=_shell_command(
                "fashion-radar",
                "import-signals-dir",
                directory_text,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_text,
                "--source-name",
                source_text,
                "--imported-at",
                as_of_text,
                "--dry-run",
            ),
            suggested_effect="read_only",
        ),
        CommunityHandoffWorkflowStep(
            order=4,
            name="import_directory_signals",
            purpose="Import the validated local handoff rows into local SQLite.",
            command=_shell_command(
                "fashion-radar",
                "import-signals-dir",
                directory_text,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_text,
                "--source-name",
                source_text,
                "--imported-at",
                as_of_text,
            ),
            suggested_effect="updates_local_imports",
        ),
        CommunityHandoffWorkflowStep(
            order=5,
            name="print_post_import_review",
            purpose="Print the local post-import review checklist.",
            command=_shell_command(
                "fashion-radar",
                "imported-review-workflow",
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--source-name",
                source_text,
            ),
            suggested_effect="print_only",
        ),
    ]
    return CommunityHandoffWorkflow(
        directory=directory_text,
        input_format=input_format,
        pattern=pattern,
        as_of=as_of_text,
        config_dir=config_text,
        data_dir=data_text,
        source_name=source_text,
        step_count=len(steps),
        steps=steps,
    )


def render_community_handoff_workflow_table(workflow: CommunityHandoffWorkflow) -> list[str]:
    lines = [
        "Community signal handoff workflow.",
        f"Execution mode: {workflow.execution_mode}",
        "Commands were not executed.",
        f"Directory: {_table_cell(workflow.directory)}",
        f"Input format: {workflow.input_format}",
        f"Pattern: {_table_cell(workflow.pattern)}",
        f"As of: {workflow.as_of}",
        f"Config dir: {_table_cell(workflow.config_dir)}",
        f"Data dir: {_table_cell(workflow.data_dir)}",
        f"Source name: {_table_cell(workflow.source_name)}",
        f"Steps: {workflow.step_count}",
        "Order | Step | Suggested Effect | Purpose | Command",
    ]
    for step in workflow.steps:
        lines.append(
            f"{step.order} | {_table_cell(step.name)} | {step.suggested_effect} | "
            f"{_table_cell(step.purpose)} | {step.command}"
        )
    return lines


def _shell_command(*parts: str) -> str:
    return shlex.join(str(part) for part in parts)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 5: Run module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_handoff_workflow.py -q
```

Expected: all tests pass.

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add CLI tests first**

Add imports at the top of `tests/test_cli.py` if they are not already present:

```python
import os
import subprocess
```

Add tests near the imported workflow and community candidate CLI tests:

```python
def test_community_handoff_workflow_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["community-handoff-workflow", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "Print a local community handoff command checklist" in result.output
```

Add JSON/table/missing-directory tests:

```python
def test_community_handoff_workflow_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "config dir"
    data_dir = tmp_path / "data dir"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
            str(directory),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            "Community Tool Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "execution_mode",
        "step_count",
        "steps",
    ]
    assert payload["directory"] == str(directory)
    assert payload["execution_mode"] == "print_only"
    assert payload["step_count"] == 5
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    assert [step["name"] for step in payload["steps"]] == [
        "lint_handoff_directory",
        "preview_candidate_phrases",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert payload["steps"][3]["suggested_effect"] == "updates_local_imports"
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_community_handoff_workflow_command_prints_table_without_artifacts(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
            str(directory),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Community signal handoff workflow." in result.output
    assert "Commands were not executed." in result.output
    assert "community-signal-lint-dir" in result.output
    assert "community-candidates-dir" in result.output
    assert "import-signals-dir" in result.output
    assert "imported-review-workflow" in result.output
    assert str(directory) in result.output
    assert str(config_dir) in result.output
    assert str(data_dir) in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()
```

Add invalid timestamp and no-access guards:

```python
def test_community_handoff_workflow_invalid_as_of_is_clean_error(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
            str(tmp_path / "exports"),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not build community handoff workflow: invalid --as-of" in result.output


def test_community_handoff_workflow_does_not_read_directory_or_run_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    guarded_paths = {directory}

    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    def is_guarded_path(path) -> bool:
        try:
            return Path(path) in guarded_paths
        except TypeError:
            return False

    def guard_path_method(name: str):
        original = getattr(Path, name)

        def guarded(self: Path, *args, **kwargs):
            if self in guarded_paths:
                raise AssertionError(f"{name} should not inspect supplied paths")
            return original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, guarded)

    def guard_os_function(name: str):
        original = getattr(os, name)

        def guarded(path, *args, **kwargs):
            if is_guarded_path(path):
                raise AssertionError(f"os.{name} should not inspect supplied path: {path}")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)

    for name in ("iterdir", "glob", "rglob", "exists", "is_dir", "stat", "lstat"):
        guard_path_method(name)
    for name in ("scandir", "stat", "listdir", "walk"):
        guard_os_function(name)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_directory_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(
        app,
        [
            "community-handoff-workflow",
            str(directory),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
```

- [ ] **Step 2: Run CLI tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q
```

Expected: new tests fail because the command is not registered yet.

- [ ] **Step 3: Wire CLI command**

Update `src/fashion_radar/cli.py`:

Add imports:

```python
from fashion_radar.community_handoff_workflow import (
    build_community_handoff_workflow,
    render_community_handoff_workflow_table,
)
```

Add type/option constants near community candidates:

```python
CommunityHandoffWorkflowOutputFormat = Literal["table", "json"]
COMMUNITY_HANDOFF_WORKFLOW_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC handoff workflow timestamp, for example 2026-06-13T12:00:00Z.",
)
```

Add command near community candidate/import directory commands:

```python
@app.command(name="community-handoff-workflow")
def community_handoff_workflow_command(
    directory: str,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    output_format: CommunityHandoffWorkflowOutputFormat = COMMUNITY_HANDOFF_WORKFLOW_FORMAT_OPTION,
) -> None:
    """Print a local community handoff command checklist without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build community handoff workflow: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        workflow = build_community_handoff_workflow(
            directory=Path(directory),
            config_dir=config_dir,
            data_dir=data_dir,
            input_format=input_format,
            pattern=pattern,
            as_of=as_of_value,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build community handoff workflow: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(workflow.model_dump_json(indent=2))
        return
    for line in render_community_handoff_workflow_table(workflow):
        typer.echo(line)
```

The positional `directory` parameter is intentionally typed as `str` so Typer
does not perform `Path` metadata access for this print-only command.

- [ ] **Step 4: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_handoff_workflow.py tests/test_cli.py -q
```

Expected: focused tests pass.

## Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/architecture.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Add quickstart example**

In README community tool commands, add:

```bash
uv run fashion-radar community-handoff-workflow ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
```

- [ ] **Step 2: Add boundary prose**

Add concise prose:

```markdown
`community-handoff-workflow` is local and print-only. It does not read the
supplied directory, validate files, import rows, open SQLite, execute commands,
fetch URLs, collect sources, watch folders, schedule work, generate reports,
update dashboards, or create config/entity files. It intentionally prints the
supplied directory/config/data paths inside copyable local commands.
```

- [ ] **Step 3: Update architecture and source boundary docs**

Document that the command sits before directory lint/import and only prints the
local sequence. Use negative language for platform/search/source-acquisition
boundaries.

- [ ] **Step 4: Update changelog and upload checklist**

Add a changelog bullet and a checklist item that this command is print-only,
does not read the directory, does not execute commands, and intentionally prints
copyable local paths.

## Task 4: Verification And Review

**Files:**
- Add review prompt files under `docs/reviews/`.

- [ ] **Step 1: Run final local verification**

Run:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
.venv/bin/python -m pytest tests/test_community_handoff_workflow.py tests/test_cli.py -q
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 2: Run build and installed-wheel smoke**

Run:

```bash
rm -rf /tmp/fashion-radar-dist-stage30 /tmp/fashion-radar-wheel-stage30
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage30
uv venv /tmp/fashion-radar-wheel-stage30/.venv
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python /tmp/fashion-radar-wheel-stage30/.venv/bin/python /tmp/fashion-radar-dist-stage30/*.whl
/tmp/fashion-radar-wheel-stage30/.venv/bin/fashion-radar community-handoff-workflow --help
/tmp/fashion-radar-wheel-stage30/.venv/bin/fashion-radar community-handoff-workflow /tmp/fashion-radar-wheel-stage30/missing --input-format csv --pattern "*.csv" --config-dir /tmp/fashion-radar-wheel-stage30/configs --data-dir /tmp/fashion-radar-wheel-stage30/data --as-of 2026-06-13T12:00:00Z --format json
```

Expected: installed command help exits `0`; missing-directory JSON smoke exits
`0` and prints `execution_mode: print_only`.

- [ ] **Step 3: Run boundary scans**

Run:

```bash
git diff -- src tests README.md CHANGELOG.md docs | rg -n "fetch|url|login|download|browser|automation|scrape|scraper|scraping|monitor|monitors|monitoring|watcher|watchers|scheduler|schedulers|schedule|scheduled|source acquisition|platform coverage|demand|proof of demand|rank sources|ranking|database import|database writes|report generation|dashboard generation|config generation|entity generation"
```

Expected: matches are only negative boundary language or existing context.

- [ ] **Step 4: Submit code/docs to Claude Code review**

Create `docs/reviews/claude-code-stage-30-code-review-prompt.md` asking Claude
Code to review:

- print-only behavior;
- no directory read;
- no SQLite/report/dashboard/config/entity artifact creation;
- no subprocess execution;
- correct shell quoting;
- stable JSON keys;
- path echo documented as intentional for copyable commands;
- no platform/source-acquisition/scraping/monitoring implications;
- `uv.lock` excluded.

Run:

```bash
claude --effort max --permission-mode plan -p "$(cat docs/reviews/claude-code-stage-30-code-review-prompt.md)" > docs/reviews/claude-code-stage-30-code-review.md
```

Required approval phrase:

```text
APPROVED FOR STAGE 30 COMMIT AND PUSH
```

Fix any Critical or Important findings and rereview before committing.

## Task 5: Commit, Push, Handoff

**Files:**
- Git only.

- [ ] **Step 1: Stage only Stage 30 files**

Run:

```bash
git add src/fashion_radar/community_handoff_workflow.py src/fashion_radar/cli.py tests/test_community_handoff_workflow.py tests/test_cli.py README.md CHANGELOG.md docs/architecture.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/github-upload-checklist.md docs/superpowers/specs/2026-06-13-stage-30-community-handoff-workflow-design.md docs/superpowers/plans/2026-06-13-stage-30-community-handoff-workflow-plan.md docs/reviews/claude-code-stage-30-*.md
git diff --cached --name-only
git diff --cached -- uv.lock
```

Expected: `uv.lock` staged diff is empty.

- [ ] **Step 2: Commit and push**

Run:

```bash
git commit -m "Add community handoff workflow"
```

Push with the existing token only through a non-persistent extraheader. Do not
change the remote URL and do not persist the token.

- [ ] **Step 3: Post-push checks**

Run:

```bash
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
git remote get-url origin
git config --get-regexp '^http\..*extraheader$' || true
git status --short --branch
git diff --quiet --cached
```

Expected: `HEAD` and `origin/main` match; remote URL is token-free; no
extraheader is persisted; staged diff is empty; only the known unstaged
`uv.lock` mirror diff may remain.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- uncommitted files;
- next step.
