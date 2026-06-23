from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_candidates import (
    CommunityCandidateDirectoryPreview,
    preview_community_candidate_directory,
)
from fashion_radar.community_handoff_workflow import DEFAULT_COMMUNITY_SOURCE_NAME
from fashion_radar.community_signals import (
    CommunitySignalDirectoryLintResult,
    lint_community_signal_directory,
)
from fashion_radar.importers.manual_signals import (
    ManualSignalDirectoryDryRunResult,
    ManualSignalFormat,
    ManualSignalImportError,
    dry_run_manual_signal_directory,
)
from fashion_radar.lint_formatting import format_count_label
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc

CommunityHandoffCheckName = Literal[
    "community_signal_lint",
    "candidate_preview",
    "import_dry_run",
    "config",
    "as_of",
]
CommunityHandoffCheckFindingSeverity = Literal["error", "warning", "info"]
COMMUNITY_HANDOFF_CHECK_EXECUTION_MODE = "local_read_only"


class CommunityHandoffDirectoryCheckFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: CommunityHandoffCheckFindingSeverity
    code: str
    message: str
    check: CommunityHandoffCheckName


class CommunityHandoffDirectoryCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    as_of: str
    config_dir: str
    source_name: str
    execution_mode: Literal["local_read_only"] = COMMUNITY_HANDOFF_CHECK_EXECUTION_MODE
    strict: bool = False
    limit: int | None = 50
    ok: bool = False
    failed_check_count: int = 0
    warning_count: int = 0
    findings: list[CommunityHandoffDirectoryCheckFinding] = Field(default_factory=list)
    community_signal_lint: CommunitySignalDirectoryLintResult
    candidate_preview: CommunityCandidateDirectoryPreview | None = None
    import_dry_run: ManualSignalDirectoryDryRunResult


def check_community_handoff_directory(
    directory: Path,
    *,
    config_dir: Path,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of: str | datetime,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    source_name: str = DEFAULT_COMMUNITY_SOURCE_NAME,
    strict: bool = False,
    limit: int | None = 50,
) -> CommunityHandoffDirectoryCheckResult:
    as_of_value = parse_datetime_utc(as_of)
    source_text = source_name.strip() or DEFAULT_COMMUNITY_SOURCE_NAME
    lint_result = lint_community_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_text,
    )
    candidate_preview: CommunityCandidateDirectoryPreview | None = None
    findings: list[CommunityHandoffDirectoryCheckFinding] = []
    try:
        candidate_preview = preview_community_candidate_directory(
            directory,
            input_format=input_format,
            pattern=pattern,
            scoring=scoring,
            settings=settings,
            entity_config=entity_config,
            as_of=as_of_value,
            default_source_name=source_text,
            limit=limit,
        )
    except ManualSignalImportError:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="candidate_preview_unavailable",
                message="Candidate preview could not read or validate the handoff directory.",
                check="candidate_preview",
            )
        )
    dry_run_result = dry_run_manual_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_text,
    )
    if lint_result.error_count:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="community_signal_lint_failed",
                message="Community signal directory lint reported errors.",
                check="community_signal_lint",
            )
        )
    if strict and lint_result.warning_count:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="community_signal_lint_warnings",
                message=(
                    "Community signal directory lint reported warnings and strict mode is enabled."
                ),
                check="community_signal_lint",
            )
        )
    if dry_run_result.error_count:
        findings.append(
            CommunityHandoffDirectoryCheckFinding(
                severity="error",
                code="import_dry_run_failed",
                message="Import directory dry-run reported errors.",
                check="import_dry_run",
            )
        )
    failed_checks = {finding.check for finding in findings if finding.severity == "error"}
    return CommunityHandoffDirectoryCheckResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        as_of=as_of_value.isoformat(),
        config_dir=str(config_dir),
        source_name=source_text,
        strict=strict,
        limit=limit,
        ok=not failed_checks,
        failed_check_count=len(failed_checks),
        warning_count=lint_result.warning_count,
        findings=findings,
        community_signal_lint=lint_result,
        candidate_preview=candidate_preview,
        import_dry_run=dry_run_result,
    )


def render_community_handoff_directory_check_table(
    result: CommunityHandoffDirectoryCheckResult,
) -> list[str]:
    lint = result.community_signal_lint
    candidate_preview = result.candidate_preview
    import_dry_run = result.import_dry_run
    candidate_preview_text = "unavailable"
    if candidate_preview is not None:
        candidate_count_label = format_count_label(
            candidate_preview.candidate_count,
            "candidate",
            "candidates",
        )
        candidate_row_label = format_count_label(candidate_preview.row_count, "row", "rows")
        candidate_preview_text = f"{candidate_count_label} from {candidate_row_label}"
    lines = [
        "Community handoff directory check.",
        f"Execution mode: {result.execution_mode}",
        f"Directory: {_table_cell(result.directory)}",
        f"Input format: {result.input_format}",
        f"Pattern: {_table_cell(result.pattern)}",
        f"As of: {result.as_of}",
        f"Config dir: {_table_cell(result.config_dir)}",
        f"Source name: {_table_cell(result.source_name)}",
        f"Strict: {str(result.strict).lower()}",
        f"Limit: {result.limit if result.limit is not None else 'none'}",
        f"Overall: {'ok' if result.ok else 'failed'}",
        f"Failed checks: {result.failed_check_count}",
        f"Warnings: {result.warning_count}",
        (
            "Lint: "
            f"{format_count_label(lint.file_count, 'file', 'files')}, "
            f"{lint.valid_row_count}/"
            f"{format_count_label(lint.row_count, 'import-ready row', 'import-ready rows')}, "
            f"{format_count_label(lint.error_count, 'error', 'errors')}"
        ),
        f"Candidate preview: {candidate_preview_text}",
        (
            "Import dry-run: "
            f"{import_dry_run.valid_file_count}/"
            f"{format_count_label(import_dry_run.file_count, 'valid file', 'valid files')}, "
            f"{format_count_label(import_dry_run.row_count, 'row', 'rows')}, "
            f"{format_count_label(import_dry_run.error_count, 'error', 'errors')}"
        ),
        "Does not import rows or write SQLite.",
    ]
    if result.findings:
        lines.append("Severity | Check | Code | Message")
        for finding in result.findings:
            lines.append(
                f"{finding.severity} | {_table_cell(finding.check)} | "
                f"{_table_cell(finding.code)} | {_table_cell(finding.message)}"
            )
    else:
        lines.append("No community handoff check findings.")
    return lines


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
