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
            f"{_table_cell(step.purpose)} | {_table_cell(step.command)}"
        )
    return lines


def _shell_command(*parts: str) -> str:
    return shlex.join(str(part) for part in parts)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
