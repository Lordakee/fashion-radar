from __future__ import annotations

import shlex
import shutil
from collections.abc import Callable
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

EXTERNAL_TOOL_READINESS_CONTRACT_VERSION = "external-tool-readiness/v1"
EXTERNAL_TOOL_READINESS_EXECUTION_MODE = "local_read_only"
DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID = "generic_community_export"

EXTERNAL_TOOL_READINESS_BOUNDARIES = [
    "Prints local read-only external/community tool readiness guidance only.",
    "Checks PATH availability only through shutil.which for mapped upstream commands.",
    "Commands were not executed.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not import upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review product feature.",
]

_UPSTREAM_COMMAND_SPECS: dict[str, dict[str, str | None]] = {
    "rednote_mcp": {
        "command": "rednote-mcp",
        "install_hint": (
            "npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp"
        ),
        "detail": "Checks whether the Rednote MCP command is discoverable locally.",
    },
    "xiaohongshu_crawler": {
        "command": "xiaohongshu-crawler",
        "install_hint": (
            "Follow the upstream xiaohongshu-crawler docs; when using pip, prefer "
            "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ..."
        ),
        "detail": "Checks whether the Xiaohongshu crawler command is discoverable locally.",
    },
    "instaloader": {
        "command": "instaloader",
        "install_hint": (
            "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple instaloader"
        ),
        "detail": "Checks whether the Instaloader command is discoverable locally.",
    },
    "tiktok_api": {
        "command": None,
        "install_hint": (
            "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple TikTokApi"
        ),
        "detail": "No upstream CLI command is required for this sanitized local export target.",
    },
    "yt_dlp": {
        "command": "yt-dlp",
        "install_hint": (
            "python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple yt-dlp"
        ),
        "detail": "Checks whether the yt-dlp command is discoverable locally.",
    },
    "x_search_export": {
        "command": None,
        "install_hint": (
            "Use an AnySearch/snscrape sanitized export or another local export you control."
        ),
        "detail": "No upstream CLI command is required for sanitized X/search handoff rows.",
    },
    "xpoz_mcp": {
        "command": None,
        "install_hint": (
            "Use XPOZ MCP / Social Data API docs to create a sanitized local JSON export."
        ),
        "detail": "No upstream CLI command is required for sanitized XPOZ handoff rows.",
    },
    "generic_community_export": {
        "command": None,
        "install_hint": "Provide a sanitized local export in the community signal row shape.",
        "detail": "No upstream CLI command is required for a generic sanitized local export.",
    },
}


class ExternalToolReadinessCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: Literal["found", "missing", "not_applicable"]
    command: str | None
    path: str | None
    detail: str
    install_hint: str


class ExternalToolReadinessStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    name: str
    purpose: str
    command: str
    suggested_effect: Literal["print_only", "read_only"]


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
    effective_which = which if which is not None else shutil.which
    checks = [
        _upstream_command_check(
            adapter_id=adapter.id,
            which=effective_which,
        )
    ]
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
        "Check | Status | Command | Resolved Path | Install Hint | Detail",
    ]
    for check in readiness.checks:
        lines.append(
            f"{_table_cell(check.name)} | {check.status} | "
            f"{_optional_table_cell(check.command)} | "
            f"{_optional_table_cell(check.path)} | "
            f"{_table_cell(check.install_hint)} | {_table_cell(check.detail)}"
        )
    lines.extend(
        [
            f"Steps: {readiness.step_count}",
            "Order | Step | Suggested Effect | Purpose | Command",
        ]
    )
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
    *,
    adapter_id: str,
    which: Callable[[str], str | None],
) -> ExternalToolReadinessCheck:
    try:
        spec = _UPSTREAM_COMMAND_SPECS[adapter_id]
    except KeyError as exc:
        raise ValueError(f"Missing readiness command spec for adapter: {adapter_id}") from exc
    command = spec["command"]
    install_hint = spec["install_hint"] or ""
    detail = spec["detail"] or ""
    if command is None:
        return ExternalToolReadinessCheck(
            name="upstream_command",
            status="not_applicable",
            command=None,
            path=None,
            install_hint=install_hint,
            detail=detail,
        )

    resolved_path = which(command)
    if resolved_path is None:
        return ExternalToolReadinessCheck(
            name="upstream_command",
            status="missing",
            command=command,
            path=None,
            install_hint=install_hint,
            detail=detail,
        )

    return ExternalToolReadinessCheck(
        name="upstream_command",
        status="found",
        command=command,
        path=resolved_path,
        install_hint=install_hint,
        detail=detail,
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
            purpose="Print adapter defaults and boundaries before reviewing readiness.",
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
            purpose="Print example sanitized local handoff rows for the selected adapter.",
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
            purpose="Print the broader handoff workflow for the selected adapter settings.",
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
                "table",
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
            purpose="Lint local external tool handoff files before import.",
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
            purpose="Review local handoff readiness before import.",
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
                "--as-of",
                as_of_text,
                "--source-name",
                source_name,
                "--strict",
            ),
            suggested_effect="read_only",
        ),
        ExternalToolReadinessStep(
            order=7,
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


def _shell_command(*parts: str) -> str:
    return shlex.join(str(part) for part in parts)


def _optional_table_cell(value: str | None) -> str:
    if value is None:
        return ""
    return _table_cell(value)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
