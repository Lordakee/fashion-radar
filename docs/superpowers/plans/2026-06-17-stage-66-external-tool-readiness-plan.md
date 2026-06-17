# Stage 66 External Tool Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local read-only `external-tool-readiness` command that reports local upstream command availability and copyable Fashion Radar handoff next steps for known free external/community tools.

**Architecture:** Add a focused `external_tool_readiness` module beside the existing adapter/template/workflow modules. The builder reuses adapter registry metadata, checks command availability only through an injectable `which` function, emits stable Pydantic models, and renders table/JSON without reading directories, running upstream tools, opening SQLite, or creating artifacts.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic models, pytest, ruff, uv.

---

## File Map

- Create `src/fashion_radar/external_tool_readiness.py`
  - Owns readiness models, static upstream command mapping, builder, and table renderer.
- Create `tests/test_external_tool_readiness.py`
  - Covers model shape, command availability statuses, defaults/overrides, quoting, sanitization, and boundaries.
- Modify `src/fashion_radar/cli.py`
  - Imports builder/renderer, adds output format alias/options, and adds `external-tool-readiness`.
- Modify `tests/test_cli.py`
  - Adds command help, JSON/table, errors, and no-side-effect coverage.
- Modify `scripts/check_first_run_smoke.py`
  - Adds first-run flow execution and validator for `external-tool-readiness` JSON.
- Modify `tests/test_first_run_smoke.py`
  - Adds expected readiness payload and validator tests.
- Modify `tests/test_cli_docs.py`
  - Adds docs drift checks and installed-wheel checklist expectations.
- Modify docs:
  - `README.md`
  - `docs/cli-reference.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Create review artifacts:
  - `docs/reviews/opencode-stage-66-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-66-plan-review.md`
  - `docs/reviews/opencode-stage-66-code-review-prompt.md`
  - `docs/reviews/opencode-stage-66-code-review.md`

## Task 1: Core Readiness Models And Builder

**Files:**
- Create: `src/fashion_radar/external_tool_readiness.py`
- Create: `tests/test_external_tool_readiness.py`

- [ ] **Step 1: Write failing stable contract test**

Create `tests/test_external_tool_readiness.py` with:

```python
from pathlib import Path

import pytest
from pydantic import ValidationError

import fashion_radar.external_tool_readiness as readiness_module
from fashion_radar.external_tool_readiness import (
    EXTERNAL_TOOL_READINESS_BOUNDARIES,
    ExternalToolReadiness,
    build_external_tool_readiness,
    render_external_tool_readiness_table,
)


def test_readiness_has_stable_instaloader_contract_and_keys(monkeypatch) -> None:
    monkeypatch.setattr(readiness_module.shutil, "which", lambda command: f"/usr/bin/{command}")

    readiness = build_external_tool_readiness(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    payload = readiness.model_dump(mode="json")

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
        "checks",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert readiness.contract_version == "external-tool-readiness/v1"
    assert readiness.execution_mode == "local_read_only"
    assert readiness.adapter_id == "instaloader"
    assert readiness.display_name == "Instaloader Export"
    assert readiness.platform_label == "instagram"
    assert readiness.directory == "exports"
    assert readiness.input_format == "json"
    assert readiness.pattern == "*.json"
    assert readiness.as_of == "2026-06-13T12:00:00+00:00"
    assert readiness.config_dir == "configs"
    assert readiness.data_dir == "data"
    assert readiness.source_name == "Instaloader Export"
    assert len(readiness.checks) == 1
    assert readiness.checks[0].name == "upstream_command"
    assert readiness.checks[0].status == "found"
    assert readiness.checks[0].command == "instaloader"
    assert readiness.checks[0].path == "/usr/bin/instaloader"
    assert readiness.step_count == 7
    assert [step.name for step in readiness.steps] == [
        "inspect_adapter_registry",
        "print_adapter_template_json",
        "print_external_tool_workflow",
        "print_signal_profile",
        "lint_export_directory",
        "review_handoff_readiness",
        "dry_run_directory_import",
    ]
```

- [ ] **Step 2: Run the new test and verify it fails**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py::test_readiness_has_stable_instaloader_contract_and_keys -q
```

Expected: fail because `fashion_radar.external_tool_readiness` does not exist.

- [ ] **Step 3: Implement models and minimal builder**

Create `src/fashion_radar/external_tool_readiness.py` with complete implementation:

```python
from __future__ import annotations

import shlex
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.external_tool_adapters import (
    DEFAULT_ADAPTER_AS_OF,
    DEFAULT_EXPORT_DIRECTORY,
    build_external_tool_adapter_registry,
)
from fashion_radar.external_tool_workflow import DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID
from fashion_radar.importers.manual_signals import ManualSignalFormat
from fashion_radar.utils.dates import parse_datetime_utc

EXTERNAL_TOOL_READINESS_CONTRACT_VERSION = "external-tool-readiness/v1"
EXTERNAL_TOOL_READINESS_EXECUTION_MODE = "local_read_only"
DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID = DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID

EXTERNAL_TOOL_READINESS_BOUNDARIES = [
    "Prints local external/community tool readiness guidance only.",
    "Checks local command availability only with PATH lookup.",
    "Does not run adapters, upstream tools, generated commands, or install commands.",
    "Does not inspect directories, read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, workflow, or handoff artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review workflow.",
]


class ExternalToolReadinessCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: Literal["found", "missing", "not_applicable"]
    command: str | None = None
    path: str | None = None
    detail: str
    install_hint: str | None = None


class ExternalToolReadinessStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    name: str
    purpose: str
    command: str
    suggested_effect: Literal["print_only", "read_only", "updates_local_imports"]


class ExternalToolReadiness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["local_read_only"]
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
    checks: list[ExternalToolReadinessCheck] = Field(default_factory=list)
    step_count: int = 0
    steps: list[ExternalToolReadinessStep] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


_COMMAND_METADATA = {
    "rednote_mcp": (
        "rednote-mcp",
        "npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp",
        "Checks whether the Rednote MCP command is discoverable locally.",
    ),
    "xiaohongshu_crawler": (
        "xiaohongshu-crawler",
        (
            "Follow the upstream xiaohongshu-crawler docs; when using pip, prefer "
            "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ..."
        ),
        "Checks whether a local Xiaohongshu crawler command is discoverable.",
    ),
    "instaloader": (
        "instaloader",
        "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple instaloader",
        "Checks whether the Instaloader CLI is discoverable locally.",
    ),
    "tiktok_api": (
        None,
        "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple TikTokApi",
        "TikTok-Api is normally used as a Python package; no single CLI command is required.",
    ),
    "yt_dlp": (
        "yt-dlp",
        "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple yt-dlp",
        "Checks whether the yt-dlp CLI is discoverable locally.",
    ),
    "x_search_export": (
        None,
        (
            "Use a user-controlled X/search export tool, then save sanitized CSV/JSON "
            "rows that match the community signal contract."
        ),
        "No single upstream command is required for sanitized X/search exports.",
    ),
    "generic_community_export": (
        None,
        "Prepare sanitized CSV/JSON rows with your user-controlled local/community tool.",
        "No upstream command is required for generic community exports.",
    ),
}


def build_external_tool_readiness(
    *,
    adapter_id: str | None,
    directory: Path = Path(DEFAULT_EXPORT_DIRECTORY),
    config_dir: Path = Path("./configs"),
    data_dir: Path = Path("./data"),
    as_of: str | datetime = DEFAULT_ADAPTER_AS_OF,
    input_format: ManualSignalFormat | None = None,
    pattern: str | None = None,
    source_name: str | None = None,
    which: Callable[[str], str | None] | None = None,
) -> ExternalToolReadiness:
    adapter_key = adapter_id or DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID
    as_of_text = parse_datetime_utc(as_of).isoformat()
    effective_which = which if which is not None else shutil.which
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
    checks = [_upstream_command_check(adapter.id, which=effective_which)]
    steps = _readiness_steps(
        adapter_id=adapter.id,
        directory_text=directory_text,
        config_text=config_text,
        data_text=data_text,
        input_format=input_format_value,
        pattern=pattern_text,
        as_of_text=as_of_text,
        source_name=source_text,
    )
    return ExternalToolReadiness(
        contract_version=EXTERNAL_TOOL_READINESS_CONTRACT_VERSION,
        execution_mode=EXTERNAL_TOOL_READINESS_EXECUTION_MODE,
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
        checks=checks,
        step_count=len(steps),
        steps=steps,
        boundaries=[*EXTERNAL_TOOL_READINESS_BOUNDARIES],
    )


def render_external_tool_readiness_table(readiness: ExternalToolReadiness) -> list[str]:
    lines = [
        "External tool readiness.",
        f"Contract version: {readiness.contract_version}",
        f"Execution mode: {readiness.execution_mode}",
        "Commands were not executed.",
        f"Adapter: {_table_cell(readiness.adapter_id)}",
        f"Display name: {_table_cell(readiness.display_name)}",
        f"Platform label: {_table_cell(readiness.platform_label)}",
        f"Directory: {_table_cell(readiness.directory)}",
        f"Input format: {readiness.input_format}",
        f"Pattern: {_table_cell(readiness.pattern)}",
        f"As of: {readiness.as_of}",
        f"Config dir: {_table_cell(readiness.config_dir)}",
        f"Data dir: {_table_cell(readiness.data_dir)}",
        f"Source name: {_table_cell(readiness.source_name)}",
        "Checks:",
    ]
    for check in readiness.checks:
        command = check.command or "-"
        path = check.path or "-"
        hint = check.install_hint or "-"
        lines.append(
            f"- {_table_cell(check.name)}: {check.status} | command={_table_cell(command)} | "
            f"path={_table_cell(path)} | detail={_table_cell(check.detail)} | "
            f"install_hint={_table_cell(hint)}"
        )
    lines.append(f"Steps: {readiness.step_count}")
    lines.append("Order | Step | Suggested Effect | Purpose | Command")
    for step in readiness.steps:
        lines.append(
            f"{step.order} | {_table_cell(step.name)} | {step.suggested_effect} | "
            f"{_table_cell(step.purpose)} | {_table_cell(step.command)}"
        )
    lines.append("Boundaries:")
    for boundary in readiness.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines


def _upstream_command_check(
    adapter_id: str,
    *,
    which: Callable[[str], str | None],
) -> ExternalToolReadinessCheck:
    command, install_hint, detail = _COMMAND_METADATA[adapter_id]
    if command is None:
        return ExternalToolReadinessCheck(
            name="upstream_command",
            status="not_applicable",
            command=None,
            path=None,
            detail=detail,
            install_hint=install_hint,
        )
    path = which(command)
    if path:
        return ExternalToolReadinessCheck(
            name="upstream_command",
            status="found",
            command=command,
            path=path,
            detail=detail,
            install_hint=install_hint,
        )
    return ExternalToolReadinessCheck(
        name="upstream_command",
        status="missing",
        command=command,
        path=None,
        detail=detail,
        install_hint=install_hint,
    )


def _readiness_steps(
    *,
    adapter_id: str,
    directory_text: str,
    config_text: str,
    data_text: str,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of_text: str,
    source_name: str,
) -> list[ExternalToolReadinessStep]:
    return [
        ExternalToolReadinessStep(
            order=1,
            name="inspect_adapter_registry",
            purpose="Print adapter defaults and boundaries.",
            command=_shell_command(
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
            ),
            suggested_effect="print_only",
        ),
        ExternalToolReadinessStep(
            order=2,
            name="print_adapter_template_json",
            purpose="Print sanitized example rows for the selected adapter.",
            command=_shell_command(
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
            ),
            suggested_effect="print_only",
        ),
        ExternalToolReadinessStep(
            order=3,
            name="print_external_tool_workflow",
            purpose="Print the full local handoff workflow metadata.",
            command=_shell_command(
                "fashion-radar",
                "external-tool-workflow",
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
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--format",
                "json",
            ),
            suggested_effect="print_only",
        ),
        ExternalToolReadinessStep(
            order=4,
            name="print_signal_profile",
            purpose="Print the accepted community signal row fields.",
            command=_shell_command("fashion-radar", "community-signal-profile", "--format", "json"),
            suggested_effect="print_only",
        ),
        ExternalToolReadinessStep(
            order=5,
            name="lint_export_directory",
            purpose="Read matched local export files and lint sanitized rows when the user is ready.",
            command=_shell_command(
                "fashion-radar",
                "community-signal-lint-dir",
                directory_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--strict",
            ),
            suggested_effect="read_only",
        ),
        ExternalToolReadinessStep(
            order=6,
            name="review_handoff_readiness",
            purpose="Read matched local export files and print handoff readiness when the user is ready.",
            command=_shell_command(
                "fashion-radar",
                "community-handoff-check-dir",
                directory_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_text,
                "--source-name",
                source_name,
                "--as-of",
                as_of_text,
                "--strict",
            ),
            suggested_effect="read_only",
        ),
        ExternalToolReadinessStep(
            order=7,
            name="dry_run_directory_import",
            purpose="Dry-run import matched local export files when the user is ready.",
            command=_shell_command(
                "fashion-radar",
                "import-signals-dir",
                directory_text,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--data-dir",
                data_text,
                "--imported-at",
                as_of_text,
                "--dry-run",
            ),
            suggested_effect="read_only",
        ),
    ]


def _shell_command(*parts: object) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def _table_cell(value: str) -> str:
    return " ".join(value.replace("|", "/").split())
```

- [ ] **Step 4: Verify first test passes**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py::test_readiness_has_stable_instaloader_contract_and_keys -q
```

Expected: pass.

- [ ] **Step 5: Add behavior tests**

Append to `tests/test_external_tool_readiness.py`:

```python
def test_readiness_reports_missing_and_not_applicable_commands(monkeypatch) -> None:
    monkeypatch.setattr(readiness_module.shutil, "which", lambda command: None)

    instaloader = build_external_tool_readiness(
        adapter_id="instaloader",
        as_of="2026-06-13T12:00:00Z",
    )
    generic = build_external_tool_readiness(
        adapter_id="generic_community_export",
        as_of="2026-06-13T12:00:00Z",
    )
    tiktok = build_external_tool_readiness(
        adapter_id="tiktok_api",
        as_of="2026-06-13T12:00:00Z",
    )

    assert instaloader.checks[0].status == "missing"
    assert instaloader.checks[0].command == "instaloader"
    assert instaloader.checks[0].path is None
    assert "pypi.tuna.tsinghua.edu.cn" in (instaloader.checks[0].install_hint or "")
    assert generic.checks[0].status == "not_applicable"
    assert generic.checks[0].command is None
    assert tiktok.checks[0].status == "not_applicable"
    assert "TikTokApi" in (tiktok.checks[0].install_hint or "")


def test_readiness_defaults_to_generic_adapter_and_accepts_overrides(monkeypatch) -> None:
    monkeypatch.setattr(readiness_module.shutil, "which", lambda command: None)

    readiness = build_external_tool_readiness(
        adapter_id=None,
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
        input_format="json",
        pattern="*.handoff.json",
        source_name="Local Desk Export",
    )

    assert readiness.adapter_id == "generic_community_export"
    assert readiness.directory == "exports ? # & %"
    assert readiness.input_format == "json"
    assert readiness.pattern == "*.handoff.json"
    assert readiness.source_name == "Local Desk Export"
    commands = {step.name: step.command for step in readiness.steps}
    assert "'exports ? # & %'" in commands["print_external_tool_workflow"]
    assert "--source-name 'Local Desk Export'" in commands["review_handoff_readiness"]
    assert "--pattern '*.handoff.json'" in commands["dry_run_directory_import"]


def test_readiness_rejects_unknown_adapter_and_invalid_as_of() -> None:
    with pytest.raises(ValueError, match="Unknown external tool adapter: missing"):
        build_external_tool_readiness(
            adapter_id="missing",
            as_of="2026-06-13T12:00:00Z",
        )

    with pytest.raises(ValueError):
        build_external_tool_readiness(
            adapter_id="instaloader",
            as_of="not-a-date",
        )


def test_readiness_table_renderer_sanitizes_cells_and_prints_boundaries(monkeypatch) -> None:
    monkeypatch.setattr(readiness_module.shutil, "which", lambda command: "/bin/tool|one")

    readiness = build_external_tool_readiness(
        adapter_id="instaloader",
        directory=Path("exports|one"),
        config_dir=Path("config|one"),
        data_dir=Path("data|one"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Source | One",
    )
    lines = render_external_tool_readiness_table(readiness)

    assert lines[0] == "External tool readiness."
    assert "Execution mode: local_read_only" in lines
    assert "Commands were not executed." in lines
    assert "Directory: exports/one" in lines
    assert any("path=/bin/tool/one" in line for line in lines)
    assert "Source name: Source / One" in lines
    assert any("No platform collection" in line for line in lines)


def test_readiness_boundaries_include_no_scope_terms() -> None:
    boundary_text = " ".join(EXTERNAL_TOOL_READINESS_BOUNDARIES)

    for term in (
        "Checks local command availability only",
        "Does not run adapters",
        "Does not inspect directories",
        "No platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no account/session/cookie/token behavior",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    ):
        assert term in boundary_text


def test_readiness_model_rejects_extra_fields(monkeypatch) -> None:
    monkeypatch.setattr(readiness_module.shutil, "which", lambda command: None)
    payload = build_external_tool_readiness(
        adapter_id="instaloader",
        as_of="2026-06-13T12:00:00Z",
    ).model_dump(mode="json")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExternalToolReadiness.model_validate({**payload, "unexpected": "value"})
```

- [ ] **Step 6: Run focused core tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q
```

Expected: pass.

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add near the existing external-tool CLI tests in `tests/test_cli.py`:

```python
def test_external_tool_readiness_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["external-tool-readiness", "--help"],
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
    assert "generic_community_export" in result.output
    assert "Print local external tool readiness guidance" in result.output


def test_external_tool_readiness_command_prints_json_with_stable_keys(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)
    directory = tmp_path / "exports ? # & %"
    config_dir = tmp_path / "config ? # & %"
    data_dir = tmp_path / "data ? # & %"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
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
        "checks",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert payload["contract_version"] == "external-tool-readiness/v1"
    assert payload["execution_mode"] == "local_read_only"
    assert payload["adapter_id"] == "instaloader"
    assert payload["checks"][0]["status"] in {"missing", "found"}
    assert payload["step_count"] == 7
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()


def test_external_tool_readiness_command_prints_table_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)
    directory = tmp_path / "missing exports"
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
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
    assert "External tool readiness." in result.output
    assert "Contract version: external-tool-readiness/v1" in result.output
    assert "Commands were not executed." in result.output
    assert "upstream_command" in result.output
    assert "rednote-mcp" in result.output
    assert "npmmirror.com" in result.output
    assert "No platform collection" in result.output
    assert not directory.exists()
    assert not config_dir.exists()
    assert not data_dir.exists()
```

- [ ] **Step 2: Run CLI tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_readiness"
```

Expected: fail because the command does not exist and imports are missing.

- [ ] **Step 3: Wire CLI imports, alias, and command**

In `src/fashion_radar/cli.py`, add imports:

```python
import fashion_radar.external_tool_readiness as external_tool_readiness_module
from fashion_radar.external_tool_readiness import (
    DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID,
    build_external_tool_readiness,
    render_external_tool_readiness_table,
)
```

Add alias near other output formats:

```python
ExternalToolReadinessOutputFormat = Literal["table", "json"]
```

Add option constant:

```python
EXTERNAL_TOOL_READINESS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add command after `external_tool_workflow_command`:

```python
@app.command(name="external-tool-readiness")
def external_tool_readiness_command(
    adapter: str = typer.Option(
        DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID,
        "--adapter",
        help="Adapter id to check.",
    ),
    directory: str = EXTERNAL_TOOL_WORKFLOW_DIRECTORY_OPTION,
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = EXTERNAL_TOOL_WORKFLOW_AS_OF_OPTION,
    input_format: ManualSignalInputFormat | None = EXTERNAL_TOOL_WORKFLOW_INPUT_FORMAT_OPTION,
    pattern: str | None = EXTERNAL_TOOL_WORKFLOW_PATTERN_OPTION,
    source_name: str | None = EXTERNAL_TOOL_WORKFLOW_SOURCE_NAME_OPTION,
    output_format: ExternalToolReadinessOutputFormat = EXTERNAL_TOOL_READINESS_FORMAT_OPTION,
) -> None:
    """Print local external tool readiness guidance without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build external tool readiness: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        readiness = build_external_tool_readiness(
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
        typer.echo(f"Could not build external tool readiness: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(readiness.model_dump_json(indent=2))
        return
    for line in render_external_tool_readiness_table(readiness):
        typer.echo(line)
```

Also expose `external_tool_readiness_shutil = external_tool_readiness_module.shutil`
near module scope so CLI tests can monkeypatch command lookup without patching
global `shutil`.

- [ ] **Step 4: Add CLI error and no-side-effect tests**

Append to `tests/test_cli.py`:

```python
def test_external_tool_readiness_command_defaults_to_generic_adapter(monkeypatch) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)

    result = CliRunner().invoke(app, ["external-tool-readiness", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "generic_community_export"
    assert payload["checks"][0]["status"] == "not_applicable"


def test_external_tool_readiness_command_applies_overrides(monkeypatch) -> None:
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
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


def test_external_tool_readiness_command_rejects_unknown_adapter() -> None:
    result = CliRunner().invoke(app, ["external-tool-readiness", "--adapter", "missing"])

    assert result.exit_code == 1
    assert (
        "Could not build external tool readiness: Unknown external tool adapter: missing"
        in result.output
    )


def test_external_tool_readiness_command_rejects_invalid_as_of_without_builder(monkeypatch) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_readiness",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_readiness should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(app, ["external-tool-readiness", "--as-of", "not-a-date"])

    assert result.exit_code == 1
    assert "Could not build external tool readiness: invalid --as-of" in result.output
    assert "build_external_tool_readiness should not be called" not in result.output
    assert "Traceback" not in result.output


def test_external_tool_readiness_command_rejects_invalid_format_without_builder(monkeypatch) -> None:
    monkeypatch.setattr(
        cli_module,
        "build_external_tool_readiness",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("build_external_tool_readiness should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(app, ["external-tool-readiness", "--format", "xml"])

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "build_external_tool_readiness should not be called" not in result.output
    assert "Traceback" not in result.output


def test_external_tool_readiness_command_does_not_read_directory_or_run_side_effects(
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

    for path_method in (
        "exists",
        "is_file",
        "is_dir",
        "iterdir",
        "glob",
        "rglob",
        "stat",
        "lstat",
    ):
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
    monkeypatch.setattr(cli_module.external_tool_readiness_shutil, "which", lambda command: None)

    result = CliRunner().invoke(
        app,
        [
            "external-tool-readiness",
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

- [ ] **Step 5: Run focused CLI tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_readiness"
```

Expected: pass.

## Task 3: First-Run Smoke And Docs Drift

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `tests/test_cli_docs.py`
- Modify docs listed in File Map.

- [ ] **Step 1: Add smoke validator and tests**

In `docs/github-upload-checklist.md`, add installed-wheel smoke commands for:

```bash
fashion-radar external-tool-readiness --help
fashion-radar external-tool-readiness --adapter instaloader --format json
```

In `scripts/check_first_run_smoke.py`, add a validator similar to external tool
workflow and call it from `run_first_run_flow` immediately after the existing
`external-tool-workflow` validation:

```python
def validate_external_tool_readiness(command: str, payload: dict[str, object]) -> None:
    if payload.get("contract_version") != "external-tool-readiness/v1":
        raise SmokeError(f"{command} contract_version mismatch")
    if payload.get("execution_mode") != "local_read_only":
        raise SmokeError(f"{command} execution_mode mismatch")
    if payload.get("adapter_id") != "rednote_mcp":
        raise SmokeError(f"{command} adapter_id mismatch")
    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise SmokeError(f"{command} missing readiness checks")
    first_check = checks[0]
    if not isinstance(first_check, dict):
        raise SmokeError(f"{command} invalid readiness check")
    if first_check.get("name") != "upstream_command":
        raise SmokeError(f"{command} first check mismatch")
    if first_check.get("status") not in {"found", "missing"}:
        raise SmokeError(f"{command} unexpected command status")
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command} missing steps")
    step_names = [step.get("name") for step in steps if isinstance(step, dict)]
    if "print_external_tool_workflow" not in step_names:
        raise SmokeError(f"{command} missing workflow next step")
```

The flow call must execute:

```bash
fashion-radar external-tool-readiness --adapter rednote_mcp --directory "$exports_dir" --config-dir "$config_dir" --data-dir "$data_dir" --as-of "$AS_OF" --format json
```

Update `tests/test_first_run_smoke.py` with an `external_tool_readiness_payload`
helper generated from `build_external_tool_readiness`, plus validator tests and
an assertion that `run_first_run_flow` invokes `external-tool-readiness`.

- [ ] **Step 2: Add docs drift checks**

In `tests/test_cli_docs.py`, add an `EXTERNAL_TOOL_READINESS_DOCS` tuple that
mirrors `EXTERNAL_TOOL_WORKFLOW_DOCS` and add a docs test requiring each listed
doc to mention:

- `external-tool-readiness`
- `external tool readiness`
- `local read-only`
- `command availability`
- `mirror-friendly install`
- `user-controlled external/community tools`
- `sanitized CSV/JSON local file handoff`
- `does not run adapters`
- `does not run upstream tools`
- `does not inspect directories`
- `does not read handoff files`
- `no scraping`
- `no browser automation`
- `no platform APIs`
- `no account/session/cookie/token behavior`
- `no monitoring`
- `no scheduling`
- `no source acquisition`
- `no demand proof`
- `no ranking`
- `no coverage verification`

Assert the upload checklist help loop and installed smoke include:

```text
external-tool-readiness
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help
"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter instaloader --format json
```

- [ ] **Step 3: Update docs**

Update the docs listed in File Map with the same boundary language. Add CLI
examples:

```bash
uv run fashion-radar external-tool-readiness --adapter instaloader
uv run fashion-radar external-tool-readiness --adapter rednote_mcp --format json
```

In `docs/github-upload-checklist.md`, add the command to the installed-wheel help
loop and smoke commands.

- [ ] **Step 4: Run docs/smoke focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_first_run_smoke.py -q
```

Expected: pass.

## Task 4: Review, Full Verification, Commit, Push

**Files:**
- Create review prompt/result docs.

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_readiness"
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
```

- [ ] **Step 2: Run full verification**

Run:

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

- [ ] **Step 3: Run local opencode code review**

Create `docs/reviews/opencode-stage-66-code-review-prompt.md`, then run:

```bash
opencode run --dir /home/ubuntu/fashion-radar --model zhipuai-coding-plan/glm-5.2 --variant max --dangerously-skip-permissions "$(cat docs/reviews/opencode-stage-66-code-review-prompt.md)" | tee docs/reviews/opencode-stage-66-code-review.md
```

Fix Critical and Important findings.

- [ ] **Step 4: Final verification, commit, push**

Run full verification again after review fixes. Then:

```bash
git add ...
git diff --cached --check
git diff --cached -- . ':!uv.lock' | rg -n 'gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY' || true
git commit -m "Add external tool readiness guidance"
git push origin HEAD:main
```

If ordinary push lacks credentials, use the existing ephemeral `http.extraheader`
pattern only; do not write the GitHub token to remote URLs, config files, shell
profiles, docs, or committed files.
