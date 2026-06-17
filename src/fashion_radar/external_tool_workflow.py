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
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review workflow.",
]


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
    steps = _workflow_steps(
        adapter_id=adapter.id,
        directory_text=directory_text,
        config_text=config_text,
        data_text=data_text,
        input_format=input_format_value,
        pattern=pattern_text,
        as_of_text=as_of_text,
        source_name=source_text,
    )

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


def render_external_tool_workflow_table(workflow: ExternalToolWorkflow) -> list[str]:
    lines = [
        "External tool handoff workflow.",
        f"Contract version: {workflow.contract_version}",
        f"Execution mode: {workflow.execution_mode}",
        "Commands were not executed.",
        f"Adapter: {_table_cell(workflow.adapter_id)}",
        f"Display name: {_table_cell(workflow.display_name)}",
        f"Platform label: {_table_cell(workflow.platform_label)}",
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


def _workflow_steps(
    *,
    adapter_id: str,
    directory_text: str,
    config_text: str,
    data_text: str,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of_text: str,
    source_name: str,
) -> list[ExternalToolWorkflowStep]:
    return [
        ExternalToolWorkflowStep(
            order=1,
            name="inspect_adapter_registry",
            purpose="Print adapter defaults and boundaries before preparing local handoff files.",
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
        ExternalToolWorkflowStep(
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
        ExternalToolWorkflowStep(
            order=3,
            name="print_signal_profile",
            purpose="Print the accepted community signal row fields.",
            command=_shell_command("fashion-radar", "community-signal-profile", "--format", "json"),
            suggested_effect="print_only",
        ),
        ExternalToolWorkflowStep(
            order=4,
            name="print_handoff_manifest",
            purpose="Print a local handoff manifest for the selected export directory.",
            command=_shell_command(
                "fashion-radar",
                "community-handoff-manifest",
                directory_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--source-name",
                source_name,
                "--format",
                "json",
            ),
            suggested_effect="print_only",
        ),
        ExternalToolWorkflowStep(
            order=5,
            name="print_handoff_workflow",
            purpose="Print the local community handoff workflow for these adapter settings.",
            command=_shell_command(
                "fashion-radar",
                "community-handoff-workflow",
                directory_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--source-name",
                source_name,
            ),
            suggested_effect="print_only",
        ),
        ExternalToolWorkflowStep(
            order=6,
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
        ExternalToolWorkflowStep(
            order=7,
            name="preview_candidate_phrases",
            purpose="Preview aggregate candidate phrases before importing local handoff rows.",
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
                source_name,
            ),
            suggested_effect="read_only",
        ),
        ExternalToolWorkflowStep(
            order=8,
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
        ExternalToolWorkflowStep(
            order=9,
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
        ExternalToolWorkflowStep(
            order=10,
            name="import_directory_signals",
            purpose="Import validated local handoff rows into local SQLite.",
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
            ),
            suggested_effect="updates_local_imports",
        ),
        ExternalToolWorkflowStep(
            order=11,
            name="print_post_import_review",
            purpose="Print the local post-import review workflow.",
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
                source_name,
            ),
            suggested_effect="print_only",
        ),
    ]


def _shell_command(*parts: str) -> str:
    return shlex.join(str(part) for part in parts)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
