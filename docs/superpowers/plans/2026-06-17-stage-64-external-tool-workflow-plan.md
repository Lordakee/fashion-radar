# Stage 64 External Tool Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local, print-only `fashion-radar external-tool-workflow` command that prints a structured workflow for user-controlled external/community tool handoff into sanitized CSV/JSON local files.

**Architecture:** Create a dedicated workflow module that reuses the static external tool adapter registry for adapter defaults, then emits shell-quoted commands for existing local Fashion Radar commands. The Typer command renders table or JSON on stdout only; it does not run commands, read export directories, write files, open SQLite, call upstream tools, or perform platform collection.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, pytest, ruff, existing `uv --no-config` validation workflow.

---

## File Structure

- Create `src/fashion_radar/external_tool_workflow.py`: workflow constants, Pydantic models, adapter-aware builder, command construction, and table renderer.
- Modify `src/fashion_radar/cli.py`: import workflow helpers, add output format alias/option, and register `external-tool-workflow`.
- Create `tests/test_external_tool_workflow.py`: model, builder, override, renderer, boundary, and error tests.
- Modify `tests/test_cli.py`: CLI help, JSON, table, invalid option, invalid timestamp, unknown adapter, and side-effect guard tests.
- Modify `scripts/check_first_run_smoke.py`: add JSON validator and first-run invocation for `external-tool-workflow`.
- Modify `tests/test_first_run_smoke.py`: fake-command and validator expectations for the new smoke command.
- Modify `tests/test_cli_docs.py`: docs-drift tests requiring examples, workflow step names, and boundary language.
- Modify docs: `README.md`, `docs/community-signal-import.md`, `docs/community-signal-quality.md`, `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `docs/github-upload-checklist.md`, `AGENTS.md`, and `CHANGELOG.md`.
- Add review artifacts under `docs/reviews/`.

## Parallel Work Boundaries

- Worker A owns `src/fashion_radar/external_tool_workflow.py` and `tests/test_external_tool_workflow.py`.
- Worker B owns docs and `tests/test_cli_docs.py`.
- Main thread or Worker C owns `src/fashion_radar/cli.py`, `tests/test_cli.py`, `scripts/check_first_run_smoke.py`, and `tests/test_first_run_smoke.py`.
- Workers must not revert edits from other workers. If a file outside their ownership needs a change, report it instead of editing it.

## Task 1: Workflow Model And Unit Tests

**Files:**
- Create: `src/fashion_radar/external_tool_workflow.py`
- Create: `tests/test_external_tool_workflow.py`

- [ ] **Step 1: Write failing workflow contract tests**

Create `tests/test_external_tool_workflow.py` with tests that import:

```python
from pathlib import Path

import pytest
from pydantic import ValidationError

from fashion_radar.external_tool_workflow import (
    EXTERNAL_TOOL_WORKFLOW_BOUNDARIES,
    ExternalToolWorkflow,
    build_external_tool_workflow,
    render_external_tool_workflow_table,
)
```

Add these tests:

```python
def test_workflow_has_stable_instaloader_contract_and_steps() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    payload = workflow.model_dump(mode="json")
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "adapter_id",
        "display_name",
        "platform_label",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert workflow.contract_version == "external-tool-workflow/v1"
    assert workflow.execution_mode == "print_only"
    assert workflow.adapter_id == "instaloader"
    assert workflow.display_name == "Instaloader Export"
    assert workflow.platform_label == "instagram"
    assert workflow.directory == "exports"
    assert workflow.input_format == "json"
    assert workflow.pattern == "*.json"
    assert workflow.as_of == "2026-06-13T12:00:00+00:00"
    assert workflow.config_dir == "configs"
    assert workflow.data_dir == "data"
    assert workflow.source_name == "Instaloader Export"
    assert workflow.step_count == 11
    assert [step.name for step in workflow.steps] == [
        "inspect_adapter_registry",
        "print_adapter_template_json",
        "print_signal_profile",
        "print_handoff_manifest",
        "print_handoff_workflow",
        "lint_export_directory",
        "preview_candidate_phrases",
        "review_handoff_readiness",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert [step.suggested_effect for step in workflow.steps] == [
        "print_only",
        "print_only",
        "print_only",
        "print_only",
        "print_only",
        "read_only",
        "read_only",
        "read_only",
        "read_only",
        "updates_local_imports",
        "print_only",
    ]
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
```

Add command content tests:

```python
def test_workflow_commands_use_adapter_defaults_and_shell_quote_paths() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="instaloader",
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
    )
    commands = {step.name: step.command for step in workflow.steps}
    assert commands["inspect_adapter_registry"] == (
        "fashion-radar external-tool-adapters --adapter instaloader "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--format table"
    )
    assert commands["print_adapter_template_json"] == (
        "fashion-radar external-tool-template --adapter instaloader "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--format json"
    )
    assert "community-handoff-manifest 'exports ? # & %'" in commands[
        "print_handoff_manifest"
    ]
    assert "--input-format json" in commands["print_handoff_manifest"]
    assert "--pattern '*.json'" in commands["print_handoff_manifest"]
    assert "--source-name 'Instaloader Export'" in commands["print_handoff_manifest"]
    assert "--dry-run" in commands["dry_run_directory_import"]
    assert "--dry-run" not in commands["import_directory_signals"]
```

Add override/default/error tests:

```python
def test_workflow_defaults_to_generic_adapter_and_accepts_local_overrides() -> None:
    workflow = build_external_tool_workflow(
        adapter_id=None,
        directory=Path("./handoff"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        input_format="json",
        pattern="*.handoff.json",
        source_name="Local Desk Export",
    )
    assert workflow.adapter_id == "generic_community_export"
    assert workflow.input_format == "json"
    assert workflow.pattern == "*.handoff.json"
    assert workflow.source_name == "Local Desk Export"
    assert "--source-name 'Local Desk Export'" in workflow.steps[3].command


def test_workflow_blank_source_name_falls_back_to_adapter_source_name() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="x_search_export",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        source_name="   ",
    )
    assert workflow.source_name == "X Search Export"


def test_workflow_rejects_unknown_adapter_and_invalid_as_of() -> None:
    with pytest.raises(ValueError, match="Unknown external tool adapter: missing"):
        build_external_tool_workflow(
            adapter_id="missing",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        )
    with pytest.raises(ValueError):
        build_external_tool_workflow(
            adapter_id="instaloader",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="not-a-date",
        )
```

Add renderer and model strictness tests:

```python
def test_workflow_table_renderer_sanitizes_cells_and_prints_boundaries() -> None:
    workflow = build_external_tool_workflow(
        adapter_id="generic_community_export",
        directory=Path("exports|one"),
        config_dir=Path("configs|one"),
        data_dir=Path("data|one"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Source | One",
    )
    lines = render_external_tool_workflow_table(workflow)
    assert lines[0] == "External tool handoff workflow."
    assert "Execution mode: print_only" in lines
    assert "Commands were not executed." in lines
    assert "Directory: exports/one" in lines
    assert "Source name: Source / One" in lines
    assert "Order | Step | Suggested Effect | Purpose | Command" in lines
    assert any("Boundaries:" == line for line in lines)
    assert any("No platform collection" in line for line in lines)


def test_workflow_boundaries_include_external_tool_no_scope_terms() -> None:
    boundary_text = " ".join(EXTERNAL_TOOL_WORKFLOW_BOUNDARIES)
    for term in (
        "Does not run generated commands.",
        "Does not inspect the supplied directory.",
        "No platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    ):
        assert term in boundary_text


def test_workflow_model_rejects_extra_fields() -> None:
    payload = build_external_tool_workflow(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    ).model_dump(mode="json")
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExternalToolWorkflow.model_validate({**payload, "unexpected": "value"})
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py -q
```

Expected: fail because `fashion_radar.external_tool_workflow` does not exist.

- [ ] **Step 3: Implement workflow module**

Create `src/fashion_radar/external_tool_workflow.py` with:

```python
from __future__ import annotations

import shlex
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.external_tool_adapters import (
    DEFAULT_ADAPTER_AS_OF,
    DEFAULT_EXPORT_DIRECTORY,
    build_external_tool_adapter_registry,
)
from fashion_radar.importers.manual_signals import ManualSignalFormat
from fashion_radar.utils.dates import parse_datetime_utc

EXTERNAL_TOOL_WORKFLOW_CONTRACT_VERSION = "external-tool-workflow/v1"
EXTERNAL_TOOL_WORKFLOW_EXECUTION_MODE = "print_only"
DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID = "generic_community_export"
EXTERNAL_TOOL_WORKFLOW_BOUNDARIES = [
    "Prints local external/community tool handoff workflow commands only.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, "
        "no ranking, and no coverage verification."
    ),
    "Does not provide a compliance-review workflow.",
]
```

Define models:

```python
class ExternalToolWorkflowStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    name: str
    purpose: str
    command: str
    suggested_effect: Literal["print_only", "read_only", "updates_local_imports"]


class ExternalToolWorkflow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["print_only"]
    adapter_id: str
    display_name: str
    platform_label: str
    directory: str
    input_format: ManualSignalFormat
    pattern: str
    as_of: str
    config_dir: str
    data_dir: str
    source_name: str
    step_count: int = 0
    steps: list[ExternalToolWorkflowStep] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
```

Implement `build_external_tool_workflow(...)` with this signature:

```python
def build_external_tool_workflow(
    *,
    adapter_id: str | None,
    directory: Path = Path(DEFAULT_EXPORT_DIRECTORY),
    config_dir: Path = Path("./configs"),
    data_dir: Path = Path("./data"),
    as_of: str | datetime = DEFAULT_ADAPTER_AS_OF,
    input_format: ManualSignalFormat | None = None,
    pattern: str | None = None,
    source_name: str | None = None,
) -> ExternalToolWorkflow:
```

Inside the builder:

```python
adapter_key = adapter_id or DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID
as_of_text = parse_datetime_utc(as_of).isoformat()
registry = build_external_tool_adapter_registry(
    directory=directory,
    config_dir=config_dir,
    data_dir=data_dir,
    as_of=as_of_text,
)
try:
    adapter = registry.adapter_by_id(adapter_key)
except KeyError as exc:
    raise ValueError(f"Unknown external tool adapter: {adapter_key}") from exc

directory_text = str(directory)
config_text = str(config_dir)
data_text = str(data_dir)
input_format_value = input_format or adapter.recommended_input_format
pattern_text = (pattern or adapter.recommended_pattern).strip() or adapter.recommended_pattern
source_text = (source_name or "").strip() or adapter.suggested_source_name
steps = _workflow_steps(...)
return ExternalToolWorkflow(
    contract_version=EXTERNAL_TOOL_WORKFLOW_CONTRACT_VERSION,
    execution_mode=EXTERNAL_TOOL_WORKFLOW_EXECUTION_MODE,
    adapter_id=adapter.id,
    display_name=adapter.display_name,
    platform_label=adapter.platform_label,
    directory=directory_text,
    input_format=input_format_value,
    pattern=pattern_text,
    as_of=as_of_text,
    config_dir=config_text,
    data_dir=data_text,
    source_name=source_text,
    step_count=len(steps),
    steps=steps,
    boundaries=[*EXTERNAL_TOOL_WORKFLOW_BOUNDARIES],
)
```

Implement `_workflow_steps(...)` with the eleven step names from the design.
Use `_shell_command(*parts: str) -> str` for every command. Include these
important command shapes:

```python
_shell_command(
    "fashion-radar",
    "external-tool-adapters",
    "--adapter",
    adapter_id,
    "--directory",
    directory_text,
    "--config-dir",
    config_text,
    "--data-dir",
    data_text,
    "--as-of",
    as_of_text,
    "--format",
    "table",
)
```

```python
_shell_command(
    "fashion-radar",
    "external-tool-template",
    "--adapter",
    adapter_id,
    "--directory",
    directory_text,
    "--config-dir",
    config_text,
    "--data-dir",
    data_text,
    "--as-of",
    as_of_text,
    "--format",
    "json",
)
```

Use existing local workflow command shapes for:

- `community-signal-profile --format json`
- `community-handoff-manifest <directory> --input-format <format> --pattern <pattern> --config-dir <config> --data-dir <data> --as-of <as_of> --source-name <source> --format json`
- `community-handoff-workflow <directory> --input-format <format> --pattern <pattern> --config-dir <config> --data-dir <data> --as-of <as_of> --source-name <source>`
- `community-signal-lint-dir <directory> --input-format <format> --pattern <pattern> --source-name <source> --strict`
- `community-candidates-dir <directory> --input-format <format> --pattern <pattern> --config-dir <config> --as-of <as_of> --source-name <source>`
- `community-handoff-check-dir <directory> --input-format <format> --pattern <pattern> --config-dir <config> --as-of <as_of> --source-name <source> --strict`
- `import-signals-dir <directory> --format <format> --pattern <pattern> --source-name <source> --data-dir <data> --imported-at <as_of> --dry-run`
- `import-signals-dir <directory> --format <format> --pattern <pattern> --source-name <source> --data-dir <data> --imported-at <as_of>`
- `imported-review-workflow --config-dir <config> --data-dir <data> --as-of <as_of> --source-name <source>`

Implement table rendering:

```python
def render_external_tool_workflow_table(workflow: ExternalToolWorkflow) -> list[str]:
    lines = [
        "External tool handoff workflow.",
        f"Contract version: {workflow.contract_version}",
        f"Execution mode: {workflow.execution_mode}",
        "Commands were not executed.",
        f"Adapter: {_table_cell(workflow.adapter_id)}",
        f"Platform: {_table_cell(workflow.platform_label)}",
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
            f"{_table_cell(step.purpose)} | {_table_cell(step.command)}"
        )
    lines.append("Boundaries:")
    for boundary in workflow.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines
```

Add helpers:

```python
def _shell_command(*parts: str) -> str:
    return shlex.join(str(part) for part in parts)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 4: Run unit tests to verify pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py -q
```

Expected: all tests in the file pass.

## Task 2: CLI Command And CLI Tests

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add tests near the existing external tool tests in `tests/test_cli.py`:

```python
def test_external_tool_workflow_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["external-tool-workflow", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--adapter" in result.output
    assert "--directory" in result.output
    assert "--input-format" in result.output
    assert "--pattern" in result.output
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "Print local external tool workflow commands" in result.output


def test_external_tool_workflow_command_prints_json_with_stable_keys(tmp_path: Path) -> None:
    directory = tmp_path / "exports ? # & %"
    config_dir = tmp_path / "config ? # & %"
    data_dir = tmp_path / "data ? # & %"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "instaloader",
            "--directory",
            str(directory),
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
    payload = json.loads(result.output)
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "adapter_id",
        "display_name",
        "platform_label",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert payload["contract_version"] == "external-tool-workflow/v1"
    assert payload["execution_mode"] == "print_only"
    assert payload["adapter_id"] == "instaloader"
    assert payload["step_count"] == 11
    assert payload["steps"][0]["name"] == "inspect_adapter_registry"
    assert payload["steps"][9]["suggested_effect"] == "updates_local_imports"
    assert "'exports ? # & %'" in payload["steps"][3]["command"]
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()
```

Add table and override tests:

```python
def test_external_tool_workflow_command_prints_table_without_artifacts(tmp_path: Path) -> None:
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "External tool handoff workflow." in result.output
    assert "Contract version: external-tool-workflow/v1" in result.output
    assert "Commands were not executed." in result.output
    assert "inspect_adapter_registry" in result.output
    assert "print_adapter_template_json" in result.output
    assert "community-handoff-manifest" in result.output
    assert "community-candidates-dir" in result.output
    assert "imported-review-workflow" in result.output
    assert "No platform collection" in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_external_tool_workflow_command_applies_overrides() -> None:
    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "x_search_export",
            "--input-format",
            "json",
            "--pattern",
            "*.handoff.json",
            "--source-name",
            "Local Desk Export",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "x_search_export"
    assert payload["input_format"] == "json"
    assert payload["pattern"] == "*.handoff.json"
    assert payload["source_name"] == "Local Desk Export"
```

Add error and side-effect tests:

```python
def test_external_tool_workflow_command_rejects_unknown_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-workflow", "--adapter", "missing"])

    assert result.exit_code == 1
    assert (
        "Could not build external tool workflow: Unknown external tool adapter: missing"
        in result.output
    )


def test_external_tool_workflow_command_rejects_invalid_as_of_without_builder(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_workflow",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_workflow should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        ["external-tool-workflow", "--as-of", "not-a-date"],
    )

    assert result.exit_code == 1
    assert "Could not build external tool workflow: invalid --as-of" in result.output
    assert "build_external_tool_workflow should not be called" not in result.output


def test_external_tool_workflow_command_rejects_invalid_format_without_builder(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_workflow",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_workflow should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        ["external-tool-workflow", "--format", "xml"],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "build_external_tool_workflow should not be called" not in result.output
```

Add no-data-access guard:

```python
def test_external_tool_workflow_command_does_not_read_directory_or_run_side_effects(
    tmp_path: Path,
    monkeypatch,
) -> None:
    directory = tmp_path / "exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    guarded_paths = {directory, config_dir, data_dir}

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

    for path_method in ("exists", "is_file", "is_dir", "iterdir", "glob", "rglob", "stat", "lstat"):
        guard_path_method(path_method)
    for os_function in ("scandir", "stat", "listdir", "walk"):
        guard_os_function(os_function)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_directory_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "check_community_handoff_directory", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(
        app,
        [
            "external-tool-workflow",
            "--adapter",
            "instaloader",
            "--directory",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "instaloader"
```

- [ ] **Step 2: Run CLI tests to verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_workflow"
```

Expected: fail because the CLI command does not exist.

- [ ] **Step 3: Wire CLI command**

Modify imports in `src/fashion_radar/cli.py`:

```python
from fashion_radar.external_tool_workflow import (
    DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID,
    build_external_tool_workflow,
    render_external_tool_workflow_table,
)
```

Add an output format alias and option:

```python
ExternalToolWorkflowOutputFormat = Literal["table", "json"]
EXTERNAL_TOOL_WORKFLOW_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Register this command near `external-tool-template`:

```python
@app.command(name="external-tool-workflow")
def external_tool_workflow_command(
    adapter: str = typer.Option(
        DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID,
        "--adapter",
        help="Adapter id to print a workflow for.",
    ),
    directory: str = typer.Option(
        DEFAULT_EXPORT_DIRECTORY,
        "--directory",
        help="Local export directory used in printed commands only.",
    ),
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = typer.Option(
        DEFAULT_ADAPTER_AS_OF,
        "--as-of",
        help="UTC timestamp used in printed commands only.",
    ),
    input_format: ManualSignalInputFormat | None = typer.Option(
        None,
        "--input-format",
        help="Override adapter input file format.",
    ),
    pattern: str | None = typer.Option(
        None,
        "--pattern",
        help="Override adapter handoff file glob pattern.",
    ),
    source_name: str | None = typer.Option(
        None,
        "--source-name",
        help="Override adapter source name.",
    ),
    output_format: ExternalToolWorkflowOutputFormat = EXTERNAL_TOOL_WORKFLOW_FORMAT_OPTION,
) -> None:
    """Print local external tool workflow commands without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build external tool workflow: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        workflow = build_external_tool_workflow(
            adapter_id=adapter,
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of_value,
            input_format=input_format,
            pattern=pattern,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build external tool workflow: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(workflow.model_dump_json(indent=2))
        return
    for line in render_external_tool_workflow_table(workflow):
        typer.echo(line)
```

- [ ] **Step 4: Run CLI tests to verify pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_workflow"
```

Expected: all `external_tool_workflow` CLI tests pass.

## Task 3: First-Run Smoke Coverage

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Write failing first-run smoke tests**

In `tests/test_first_run_smoke.py`, add expectations that the fake command
sequence includes:

```python
[
    "external-tool-workflow",
    "--adapter",
    "rednote_mcp",
    "--directory",
    str(context.exports_dir),
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--as-of",
    "2026-06-13T12:00:00Z",
    "--format",
    "json",
]
```

Add a validator test:

```python
def test_validate_external_tool_workflow_checks_contract_and_commands() -> None:
    payload = {
        "contract_version": "external-tool-workflow/v1",
        "execution_mode": "print_only",
        "adapter_id": "rednote_mcp",
        "display_name": "Rednote MCP Export",
        "platform_label": "rednote",
        "directory": "exports",
        "input_format": "json",
        "pattern": "*.json",
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": "configs",
        "data_dir": "data",
        "source_name": "Rednote MCP Export",
        "step_count": 11,
        "steps": [
            {"order": 1, "name": "inspect_adapter_registry", "purpose": "p", "command": "fashion-radar external-tool-adapters --adapter rednote_mcp --format table", "suggested_effect": "print_only"},
            {"order": 2, "name": "print_adapter_template_json", "purpose": "p", "command": "fashion-radar external-tool-template --adapter rednote_mcp --format json", "suggested_effect": "print_only"},
            {"order": 3, "name": "print_signal_profile", "purpose": "p", "command": "fashion-radar community-signal-profile --format json", "suggested_effect": "print_only"},
            {"order": 4, "name": "print_handoff_manifest", "purpose": "p", "command": "fashion-radar community-handoff-manifest exports --input-format json --pattern '*.json' --config-dir configs --data-dir data --as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export' --format json", "suggested_effect": "print_only"},
            {"order": 5, "name": "print_handoff_workflow", "purpose": "p", "command": "fashion-radar community-handoff-workflow exports --input-format json --pattern '*.json' --config-dir configs --data-dir data --as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export'", "suggested_effect": "print_only"},
            {"order": 6, "name": "lint_export_directory", "purpose": "p", "command": "fashion-radar community-signal-lint-dir exports --input-format json --pattern '*.json' --source-name 'Rednote MCP Export' --strict", "suggested_effect": "read_only"},
            {"order": 7, "name": "preview_candidate_phrases", "purpose": "p", "command": "fashion-radar community-candidates-dir exports --input-format json --pattern '*.json' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export'", "suggested_effect": "read_only"},
            {"order": 8, "name": "review_handoff_readiness", "purpose": "p", "command": "fashion-radar community-handoff-check-dir exports --input-format json --pattern '*.json' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export' --strict", "suggested_effect": "read_only"},
            {"order": 9, "name": "dry_run_directory_import", "purpose": "p", "command": "fashion-radar import-signals-dir exports --format json --pattern '*.json' --source-name 'Rednote MCP Export' --data-dir data --imported-at 2026-06-13T12:00:00+00:00 --dry-run", "suggested_effect": "read_only"},
            {"order": 10, "name": "import_directory_signals", "purpose": "p", "command": "fashion-radar import-signals-dir exports --format json --pattern '*.json' --source-name 'Rednote MCP Export' --data-dir data --imported-at 2026-06-13T12:00:00+00:00", "suggested_effect": "updates_local_imports"},
            {"order": 11, "name": "print_post_import_review", "purpose": "p", "command": "fashion-radar imported-review-workflow --config-dir configs --data-dir data --as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export'", "suggested_effect": "print_only"},
        ],
        "boundaries": ["No platform collection, no connectors, no scraping, no platform APIs."],
    }

    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "adapter_id",
        "display_name",
        "platform_label",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]
    smoke.validate_external_tool_workflow("external-tool-workflow", payload)
```

- [ ] **Step 2: Run first-run smoke tests to verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or first_run_flow"
```

Expected: fail because the validator and invocation do not exist.

- [ ] **Step 3: Add smoke validator and invocation**

In `scripts/check_first_run_smoke.py`, add:

```python
def validate_external_tool_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(
        f"{command_name} contract_version",
        payload.get("contract_version"),
        "external-tool-workflow/v1",
    )
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} adapter_id", payload.get("adapter_id"), "rednote_mcp")
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "json")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), "*.json")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), "Rednote MCP Export")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 11)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    expected_names = [
        "inspect_adapter_registry",
        "print_adapter_template_json",
        "print_signal_profile",
        "print_handoff_manifest",
        "print_handoff_workflow",
        "lint_export_directory",
        "preview_candidate_phrases",
        "review_handoff_readiness",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert_equal(
        f"{command_name} step names",
        [step.get("name") for step in steps if isinstance(step, dict)],
        expected_names,
    )
    assert_equal(f"{command_name} first step effect", steps[0].get("suggested_effect"), "print_only")
    assert_equal(f"{command_name} dry-run step effect", steps[8].get("suggested_effect"), "read_only")
    assert_equal(
        f"{command_name} import step effect",
        steps[9].get("suggested_effect"),
        "updates_local_imports",
    )
    command_text = "\n".join(str(step.get("command", "")) for step in steps)
    for expected in (
        "external-tool-adapters",
        "external-tool-template",
        "community-signal-profile",
        "community-handoff-manifest",
        "community-handoff-workflow",
        "community-signal-lint-dir",
        "community-candidates-dir",
        "community-handoff-check-dir",
        "import-signals-dir",
        "imported-review-workflow",
        "--input-format json",
        "--pattern '*.json'",
        "--config-dir",
        "--data-dir",
        "--as-of",
        "--source-name 'Rednote MCP Export'",
        "--strict",
        "--dry-run",
    ):
        if expected not in command_text:
            raise SmokeError(f"{command_name}: expected command text {expected!r}")
    boundary_text = " ".join(str(item) for item in payload.get("boundaries", []))
    for forbidden_gap in ("No platform collection", "no connectors", "no scraping"):
        if forbidden_gap not in boundary_text:
            raise SmokeError(f"{command_name}: missing boundary {forbidden_gap!r}")
```

Add the matching first-run fake payload helper near the other payload fixtures:

```python
def external_tool_workflow_payload() -> dict[str, object]:
    return {
        "contract_version": "external-tool-workflow/v1",
        "execution_mode": "print_only",
        "adapter_id": "rednote_mcp",
        "display_name": "Rednote MCP Export",
        "platform_label": "rednote",
        "directory": "/tmp/export",
        "input_format": "json",
        "pattern": "*.json",
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": "configs",
        "data_dir": "data",
        "source_name": "Rednote MCP Export",
        "step_count": 11,
        "steps": [
            {
                "order": 1,
                "name": "inspect_adapter_registry",
                "purpose": "Print the adapter registry before composing the workflow.",
                "command": (
                    "fashion-radar external-tool-adapters --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --format table"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 2,
                "name": "print_adapter_template_json",
                "purpose": "Print adapter template JSON before authoring local handoff rows.",
                "command": (
                    "fashion-radar external-tool-template --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --format json"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 3,
                "name": "print_signal_profile",
                "purpose": "Print the producer contract.",
                "command": "fashion-radar community-signal-profile --format json",
                "suggested_effect": "print_only",
            },
            {
                "order": 4,
                "name": "print_handoff_manifest",
                "purpose": "Print the community handoff manifest.",
                "command": (
                    "fashion-radar community-handoff-manifest exports --input-format json "
                    "--pattern '*.json' --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export' "
                    "--format json"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 5,
                "name": "print_handoff_workflow",
                "purpose": "Print the community handoff workflow.",
                "command": (
                    "fashion-radar community-handoff-workflow exports --input-format json "
                    "--pattern '*.json' --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export'"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 6,
                "name": "lint_export_directory",
                "purpose": "Lint the export directory before handoff.",
                "command": (
                    "fashion-radar community-signal-lint-dir exports --input-format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 7,
                "name": "preview_candidate_phrases",
                "purpose": "Preview candidate phrases before import.",
                "command": (
                    "fashion-radar community-candidates-dir exports --input-format json "
                    "--pattern '*.json' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 8,
                "name": "review_handoff_readiness",
                "purpose": "Review handoff readiness before import.",
                "command": (
                    "fashion-radar community-handoff-check-dir exports --input-format json "
                    "--pattern '*.json' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 9,
                "name": "dry_run_directory_import",
                "purpose": "Dry-run the directory import.",
                "command": (
                    "fashion-radar import-signals-dir exports --format json --pattern '*.json' "
                    "--source-name 'Rednote MCP Export' --data-dir data "
                    "--imported-at 2026-06-13T12:00:00+00:00 --dry-run"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 10,
                "name": "import_directory_signals",
                "purpose": "Import the directory rows into local SQLite.",
                "command": (
                    "fashion-radar import-signals-dir exports --format json --pattern '*.json' "
                    "--source-name 'Rednote MCP Export' --data-dir data "
                    "--imported-at 2026-06-13T12:00:00+00:00"
                ),
                "suggested_effect": "updates_local_imports",
            },
            {
                "order": 11,
                "name": "print_post_import_review",
                "purpose": "Print the post-import review checklist.",
                "command": (
                    "fashion-radar imported-review-workflow --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Rednote MCP Export'"
                ),
                "suggested_effect": "print_only",
            },
        ],
        "boundaries": ["No platform collection, no connectors, no scraping, no platform APIs."],
    }
```

Add a first-run invocation near the existing adapter/template smoke calls:

```python
external_tool_workflow = validate_json_output(
    "external-tool-workflow",
    run_cli(
        context,
        "external-tool-workflow",
        "--adapter",
        "rednote_mcp",
        "--directory",
        str(context.exports_dir),
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--as-of",
        AS_OF,
        "--format",
        "json",
    ).stdout,
)
validate_external_tool_workflow(
    "external-tool-workflow",
    external_tool_workflow,
)
```

Update `test_run_first_run_flow_uses_deterministic_local_command_sequence`:

- Add `"external-tool-workflow": json.dumps(external_tool_workflow_payload())`
  to `stdout_by_command`.
- Insert `"external-tool-workflow"` immediately after `"external-tool-template"`
  in the captured command-name list.
- Add `external-tool-workflow` to the command sets that must include
  `--config-dir`, `--data-dir`, and `smoke.AS_OF`.
- Add this exact captured command assertion after the existing
  `external-tool-template` assertion:

```python
external_tool_workflow = captured[5]
assert external_tool_workflow == (
    "external-tool-workflow",
    "--adapter",
    "rednote_mcp",
    "--directory",
    str(context.exports_dir),
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--as-of",
    smoke.AS_OF,
    "--format",
    "json",
)
```

- Shift the directory command index checks because the new workflow command is
  inserted before the directory workflow checks:

```python
assert captured[17][1] == str(context.exports_dir)
assert "--format" in captured[17]
assert "json" in captured[17]
assert captured[18][1] == str(context.exports_dir)
assert captured[19][1] == str(context.exports_dir)
assert captured[20][1] == str(context.exports_dir)
```

- [ ] **Step 4: Run smoke tests to verify pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or first_run_flow"
```

Expected: selected tests pass.

## Task 4: Documentation And Docs Drift

**Files:**
- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write failing docs drift tests**

In `tests/test_cli_docs.py`, add a Stage 64 test near the Stage 62/63 tests:

```python
def test_external_tool_workflow_docs_are_linked_and_bounded() -> None:
    docs = {
        "README.md": ROOT / "README.md",
        "docs/community-signal-import.md": ROOT / "docs/community-signal-import.md",
        "docs/community-signal-quality.md": ROOT / "docs/community-signal-quality.md",
        "docs/cli-reference.md": ROOT / "docs/cli-reference.md",
        "docs/github-upload-checklist.md": ROOT / "docs/github-upload-checklist.md",
        "docs/source-boundaries.md": ROOT / "docs/source-boundaries.md",
        "docs/architecture.md": ROOT / "docs/architecture.md",
        "AGENTS.md": ROOT / "AGENTS.md",
        "CHANGELOG.md": ROOT / "CHANGELOG.md",
    }
    required_terms = (
        "external-tool-workflow",
        "local",
        "print-only",
        "sanitized CSV/JSON local file handoff",
        "user-controlled external/community tools",
        "not platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    )
    for label, path in docs.items():
        text = path.read_text(encoding="utf-8")
        missing = [term for term in required_terms if term not in text]
        assert not missing, f"{label} missing {missing}"
```

Add exact command and step-name checks:

```python
def test_external_tool_workflow_docs_include_examples_and_steps() -> None:
    cli_reference = (ROOT / "docs/cli-reference.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs/github-upload-checklist.md").read_text(encoding="utf-8")
    import_doc = (ROOT / "docs/community-signal-import.md").read_text(encoding="utf-8")
    expected_commands = (
        "fashion-radar external-tool-workflow --adapter instaloader --format table",
        "fashion-radar external-tool-workflow --adapter instaloader --format json",
    )
    for command in expected_commands:
        assert command in cli_reference
        assert command in checklist
    for step_name in (
        "inspect_adapter_registry",
        "print_adapter_template_json",
        "print_signal_profile",
        "print_handoff_manifest",
        "print_handoff_workflow",
        "lint_export_directory",
        "preview_candidate_phrases",
        "review_handoff_readiness",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ):
        assert step_name in import_doc
```

- [ ] **Step 2: Run docs tests to verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "external_tool_workflow"
```

Expected: fail because docs do not mention the new command yet.

- [ ] **Step 3: Update public docs**

Update docs with these exact public facts:

- `external-tool-workflow` prints a local, print-only workflow for
  user-controlled external/community tools targeting sanitized CSV/JSON local
  file handoff.
- It is not platform collection.
- It has no connectors, no scraping, no browser automation, no platform APIs,
  no monitoring, no scheduling, no source acquisition, no demand proof, no
  ranking, and no coverage verification.
- It does not run generated commands, adapters, or upstream tools.
- It does not inspect the supplied directory, read handoff files, validate
  rows, import rows, write artifacts, or open SQLite.
- Canonical examples:

```bash
fashion-radar external-tool-workflow --adapter instaloader --format table
fashion-radar external-tool-workflow --adapter instaloader --format json
```

Add the eleven step names to `docs/community-signal-import.md` and explain that
the command prints a producer-facing wrapper around existing local commands.

Add the command to the installed-wheel help loop and smoke examples in
`docs/github-upload-checklist.md`.

- [ ] **Step 4: Run docs tests to verify pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "external_tool_workflow or documented"
```

Expected: selected docs tests pass.

## Task 5: Verification, Review, Commit, Push

**Files:**
- Create: `docs/reviews/opencode-stage-64-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-64-release-review.md`
- Possibly modify: files touched by release review fixes.

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Expected: selected tests pass.

- [ ] **Step 2: Run full quality gates**

Run:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config lock --check
git diff --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: every command exits `0`.

- [ ] **Step 3: Run packaging gates**

Run:

```bash
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
python3 scripts/check_package_archives.py "$tmp_build"
uv --no-config venv "$tmp_env/venv"
uv --no-config pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --adapter instaloader --format json | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --adapter instaloader --format table >/dev/null
```

Expected: every command exits `0`.

- [ ] **Step 4: Run token and mirror scans**

Run:

```bash
if rg -n "ghp_[A-Za-z0-9_]{20,}" .; then exit 1; fi
if rg -n "mirrors|tuna|aliyun|ustc|pypi.tuna|pypi.mirrors|index-url" uv.lock; then exit 1; fi
```

Expected: no matches. If any review artifact contains a token-like false
positive, redact the artifact further instead of excluding paths.

- [ ] **Step 5: Run opencode release review**

Create `docs/reviews/opencode-stage-64-release-review-prompt.md` summarizing:

- Base commit before Stage 64.
- Changed files.
- Stage 64 objective and boundaries.
- Verification commands and results.
- Request Critical/Important findings only.

Run:

```bash
opencode run --dir /home/ubuntu/fashion-radar --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat docs/reviews/opencode-stage-64-release-review-prompt.md)"
```

Save output to `docs/reviews/opencode-stage-64-release-review.md`.

If review returns Critical or Important findings, fix them, rerun focused/full
verification as relevant, and rerun opencode release review until no Critical
or Important findings remain.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status -sb
git add src/fashion_radar/external_tool_workflow.py src/fashion_radar/cli.py scripts/check_first_run_smoke.py tests/test_external_tool_workflow.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py README.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md docs/cli-reference.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-17-stage-64-external-tool-workflow-design.md docs/superpowers/plans/2026-06-17-stage-64-external-tool-workflow-plan.md docs/reviews/opencode-stage-64-plan-review-prompt.md docs/reviews/opencode-stage-64-plan-review.md docs/reviews/opencode-stage-64-release-review-prompt.md docs/reviews/opencode-stage-64-release-review.md
git commit -m "Add external tool workflow output"
git status -sb
```

Push with the configured safe method. Do not write credentials into the remote
URL, docs, logs, or committed files.

- [ ] **Step 7: Poll GitHub Actions**

After push, poll the latest GitHub Actions run for `main`. If it fails, inspect
the failed job, fix the issue, rerun verification, commit, push, and poll again.

## Self-Review

- Every task has a test-first step before production implementation.
- The command only prints commands and metadata; it does not execute or collect
  platform data.
- Docs and tests explicitly preserve the no-connector/no-scraping/no-platform
  API boundary.
- Work can be split across agents without overlapping file ownership.
