from __future__ import annotations

import shlex
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.utils.dates import parse_datetime_utc


class ImportedReviewWorkflowStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    name: str
    purpose: str
    command: str
    suggested_effect: Literal["read_only", "updates_local_matches"]


class ImportedReviewWorkflow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: str
    config_dir: str
    data_dir: str
    source_name: str | None = None
    lookback_days: int = 7
    current_days: int = 7
    baseline_days: int = 7
    execution_mode: Literal["print_only"] = "print_only"
    step_count: int = 0
    steps: list[ImportedReviewWorkflowStep] = Field(default_factory=list)


def build_imported_review_workflow(
    *,
    config_dir: Path,
    data_dir: Path,
    as_of: str | datetime,
    source_name: str | None = None,
    lookback_days: int = 7,
    current_days: int = 7,
    baseline_days: int = 7,
) -> ImportedReviewWorkflow:
    if lookback_days < 1:
        raise ValueError("lookback_days must be at least 1")
    if current_days < 1:
        raise ValueError("current_days must be at least 1")
    if baseline_days < 1:
        raise ValueError("baseline_days must be at least 1")

    as_of_value = parse_datetime_utc(as_of)
    as_of_text = as_of_value.isoformat()
    source_filter = (source_name or "").strip() or None
    config_text = str(config_dir)
    data_text = str(data_dir)
    source_args = _optional_source_args(source_filter)

    steps = [
        ImportedReviewWorkflowStep(
            order=1,
            name="summarize_imported_sources",
            purpose="Summarize retained imported source-name labels.",
            command=_shell_command(
                "fashion-radar",
                "imported-signals-summary",
                "--data-dir",
                data_text,
            ),
            suggested_effect="read_only",
        ),
        ImportedReviewWorkflowStep(
            order=2,
            name="refresh_stored_matches",
            purpose="Refresh stored local matches using configured entities.",
            command=_shell_command(
                "fashion-radar",
                "match",
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
            ),
            suggested_effect="updates_local_matches",
        ),
        ImportedReviewWorkflowStep(
            order=3,
            name="compare_imported_entities",
            purpose="Compare stored matched imported entities across collected-at windows.",
            command=_shell_command(
                "fashion-radar",
                "imported-entity-deltas",
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--current-days",
                str(current_days),
                "--baseline-days",
                str(baseline_days),
                *source_args,
            ),
            suggested_effect="read_only",
        ),
        ImportedReviewWorkflowStep(
            order=4,
            name="review_unmatched_imported_rows",
            purpose="Review retained imported rows without stored matches.",
            command=_shell_command(
                "fashion-radar",
                "imported-signals",
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--lookback-days",
                str(lookback_days),
                "--unmatched-only",
                *source_args,
            ),
            suggested_effect="read_only",
        ),
        ImportedReviewWorkflowStep(
            order=5,
            name="review_local_heat_movers",
            purpose="Review local observed heat movement after imported rows are matched.",
            command=_shell_command(
                "fashion-radar",
                "heat-movers",
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
            ),
            suggested_effect="read_only",
        ),
    ]
    return ImportedReviewWorkflow(
        as_of=as_of_text,
        config_dir=config_text,
        data_dir=data_text,
        source_name=source_filter,
        lookback_days=lookback_days,
        current_days=current_days,
        baseline_days=baseline_days,
        step_count=len(steps),
        steps=steps,
    )


def render_imported_review_workflow_table(workflow: ImportedReviewWorkflow) -> list[str]:
    lines = [
        "Imported manual signal review workflow.",
        f"Execution mode: {workflow.execution_mode}",
        "Commands were not executed.",
        f"As of: {workflow.as_of}",
        f"Data dir: {_table_cell(workflow.data_dir)}",
        f"Config dir: {_table_cell(workflow.config_dir)}",
        f"Source name: {_table_cell(workflow.source_name or 'none')}",
        f"Lookback days: {workflow.lookback_days}",
        f"Current days: {workflow.current_days}",
        f"Baseline days: {workflow.baseline_days}",
        f"Steps: {workflow.step_count}",
        "Order | Step | Suggested Effect | Purpose | Command",
    ]
    for step in workflow.steps:
        lines.append(
            f"{step.order} | {_table_cell(step.name)} | {step.suggested_effect} | "
            f"{_table_cell(step.purpose)} | {step.command}"
        )
    return lines


def _optional_source_args(source_name: str | None) -> list[str]:
    if source_name is None:
        return []
    return ["--source-name", source_name]


def _shell_command(*parts: str) -> str:
    return shlex.join(parts)


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
