from __future__ import annotations

import csv
import fnmatch
import json
from collections import Counter
from collections.abc import Iterable, Mapping
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from fashion_radar.importers.manual_signals import ManualSignalFormat, ManualSignalRow
from fashion_radar.lint_formatting import format_finding_counts

ALLOWED_COMMUNITY_SIGNAL_FIELDS = {
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at",
}
PROHIBITED_COMMUNITY_SIGNAL_FIELDS = {
    "author_handle",
    "raw_comment",
    "account_id",
    "follower_count",
    "image_url",
    "video_url",
    "profile_url",
    "full_post_body",
    "direct_message",
    "cookie",
    "session",
    "token",
}


class CommunitySignalFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class CommunitySignalFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: CommunitySignalFindingSeverity
    code: str
    message: str
    row: int | None = None
    field: str | None = None


class CommunitySignalLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    input_format: ManualSignalFormat
    row_count: int = 0
    valid_row_count: int = 0
    field_counts: dict[str, int] = Field(default_factory=dict)
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[CommunitySignalFinding] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return _count_findings(self.findings, CommunitySignalFindingSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return _count_findings(self.findings, CommunitySignalFindingSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return _count_findings(self.findings, CommunitySignalFindingSeverity.INFO)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


class CommunitySignalDirectoryLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    file_count: int = 0
    row_count: int = 0
    valid_row_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    field_counts: dict[str, int] = Field(default_factory=dict)
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    files: list[CommunitySignalLintResult] = Field(default_factory=list)
    findings: list[CommunitySignalFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


def lint_community_signal_file(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str = "Community Signal Import",
) -> CommunitySignalLintResult:
    raw_rows, read_error = _read_raw_signal_rows(path, input_format=input_format)
    if read_error is not None:
        return CommunitySignalLintResult(
            path=str(path),
            input_format=input_format,
            findings=[read_error],
        )

    findings: list[CommunitySignalFinding] = []
    if not raw_rows:
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="empty_signal_file",
                message="Community signal file contains no rows.",
            )
        )

    valid_rows: list[ManualSignalRow] = []
    field_counts: Counter[str] = Counter()
    url_rows: dict[str, list[int]] = {}
    for row_number, raw in raw_rows:
        if None in raw:
            findings.append(
                CommunitySignalFinding(
                    severity=CommunitySignalFindingSeverity.ERROR,
                    code="csv_extra_cells",
                    message="CSV row has more cells than headers.",
                    row=row_number,
                    field="row",
                )
            )
            raw = {field: value for field, value in raw.items() if field is not None}
        findings.extend(_raw_field_findings(raw, row_number=row_number))
        for field, value in raw.items():
            if value is not None and str(value).strip():
                field_counts[str(field)] += 1
        row, row_findings = _validate_import_ready_row(
            raw,
            row_number=row_number,
            default_source_name=default_source_name,
        )
        findings.extend(row_findings)
        if row is None:
            continue
        valid_rows.append(row)
        url_rows.setdefault(row.url, []).append(row_number)
        findings.extend(_quality_findings(raw, row, row_number=row_number))

    findings.extend(_duplicate_url_findings(url_rows))
    return CommunitySignalLintResult(
        path=str(path),
        input_format=input_format,
        row_count=len(raw_rows),
        valid_row_count=len(valid_rows),
        field_counts=dict(sorted(field_counts.items())),
        source_name_counts=dict(sorted(Counter(row.source_name for row in valid_rows).items())),
        platform_counts=dict(
            sorted(Counter(row.platform for row in valid_rows if row.platform).items())
        ),
        findings=_sort_findings(findings),
    )


def lint_community_signal_directory(
    directory: Path,
    *,
    input_format: ManualSignalFormat,
    pattern: str,
    default_source_name: str = "Community Signal Import",
) -> CommunitySignalDirectoryLintResult:
    findings: list[CommunitySignalFinding] = []
    try:
        if not directory.is_dir():
            return CommunitySignalDirectoryLintResult(
                directory=str(directory),
                input_format=input_format,
                pattern=pattern,
                error_count=1,
                findings=[
                    CommunitySignalFinding(
                        severity=CommunitySignalFindingSeverity.ERROR,
                        code="invalid_directory",
                        message=(
                            "Community signal directory does not exist or is not a directory."
                        ),
                    )
                ],
            )
        children = list(directory.iterdir())
    except OSError:
        return CommunitySignalDirectoryLintResult(
            directory=str(directory),
            input_format=input_format,
            pattern=pattern,
            error_count=1,
            findings=[
                CommunitySignalFinding(
                    severity=CommunitySignalFindingSeverity.ERROR,
                    code="invalid_directory",
                    message="Could not read community signal directory.",
                )
            ],
        )

    paths: list[Path] = []
    for path in children:
        try:
            is_regular_file = path.is_file()
        except OSError:
            continue
        if is_regular_file and fnmatch.fnmatch(path.name, pattern):
            paths.append(path)
    paths = sorted(paths, key=lambda path: str(path))

    if not paths:
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="no_matching_files",
                message="No regular files matched the pattern in the directory.",
            )
        )

    file_results = [
        lint_community_signal_file(
            path,
            input_format=input_format,
            default_source_name=default_source_name,
        )
        for path in paths
    ]
    error_count = _count_findings(findings, CommunitySignalFindingSeverity.ERROR) + sum(
        file.error_count for file in file_results
    )
    warning_count = _count_findings(
        findings,
        CommunitySignalFindingSeverity.WARNING,
    ) + sum(file.warning_count for file in file_results)
    info_count = _count_findings(findings, CommunitySignalFindingSeverity.INFO) + sum(
        file.info_count for file in file_results
    )

    return CommunitySignalDirectoryLintResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        file_count=len(file_results),
        row_count=sum(file.row_count for file in file_results),
        valid_row_count=sum(file.valid_row_count for file in file_results),
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        field_counts=_merge_count_dicts(file.field_counts for file in file_results),
        source_name_counts=_merge_count_dicts(file.source_name_counts for file in file_results),
        platform_counts=_merge_count_dicts(file.platform_counts for file in file_results),
        files=file_results,
        findings=_sort_findings(findings),
    )


def render_community_signal_lint_table(result: CommunitySignalLintResult) -> list[str]:
    lines = [
        f"Community signal file: {result.path}",
        f"Input format: {result.input_format}",
        f"Rows: {result.row_count} total, {result.valid_row_count} import-ready",
        f"Fields: {_format_counts(result.field_counts)}",
        f"Sources: {_format_counts(result.source_name_counts)}",
        f"Platforms: {_format_counts(result.platform_counts)}",
        (
            "Findings: "
            f"{format_finding_counts(result.error_count, result.warning_count, result.info_count)}"
        ),
    ]
    if not result.findings:
        lines.append("No community-signal quality findings.")
        return lines

    lines.append("Severity | Code | Row | Field | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | {finding.code} | {finding.row or 'n/a'} | "
            f"{finding.field or 'n/a'} | {finding.message}"
        )
    return lines


def render_community_signal_directory_lint_table(
    result: CommunitySignalDirectoryLintResult,
) -> list[str]:
    lines = [
        f"Community signal directory: {result.directory}",
        f"Input format: {result.input_format}",
        f"Pattern: {result.pattern}",
        f"Files: {result.file_count}",
        f"Rows: {result.row_count} total, {result.valid_row_count} import-ready",
        f"Fields: {_format_counts(result.field_counts)}",
        f"Sources: {_format_counts(result.source_name_counts)}",
        f"Platforms: {_format_counts(result.platform_counts)}",
        (
            "Findings: "
            f"{format_finding_counts(result.error_count, result.warning_count, result.info_count)}"
        ),
    ]
    if result.files:
        lines.append("Files:")
        for file in result.files:
            lines.append(
                f"- {file.path}: {file.row_count} rows, "
                f"{file.valid_row_count} import-ready, "
                f"{format_finding_counts(file.error_count, file.warning_count, file.info_count)}"
            )
    if not result.findings and all(not file.findings for file in result.files):
        lines.append("No community-signal directory findings.")
        return lines

    lines.append("Severity | File | Code | Row | Field | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | n/a | {finding.code} | "
            f"{finding.row or 'n/a'} | {finding.field or 'n/a'} | {finding.message}"
        )
    for file in result.files:
        for finding in file.findings:
            lines.append(
                f"{finding.severity.value} | {file.path} | {finding.code} | "
                f"{finding.row or 'n/a'} | {finding.field or 'n/a'} | "
                f"{finding.message}"
            )
    return lines


def _read_raw_signal_rows(
    path: Path,
    *,
    input_format: ManualSignalFormat,
) -> tuple[list[tuple[int, dict[Any, Any]]], CommunitySignalFinding | None]:
    try:
        if input_format == "csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    return [], _invalid_file("CSV file must contain headers.")
                if any(field is None or not str(field).strip() for field in reader.fieldnames):
                    return [], _invalid_file("CSV headers must be non-empty.")
                return [
                    (row_number, dict(raw)) for row_number, raw in enumerate(reader, start=2)
                ], None

        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [], _invalid_file(f"Could not read community signal file {path}: {exc}")
    except json.JSONDecodeError as exc:
        return [], _invalid_file(f"Invalid JSON in {path}: {exc}")

    if isinstance(payload, list):
        items = payload
    elif (
        isinstance(payload, dict)
        and set(payload) == {"items"}
        and isinstance(
            payload.get("items"),
            list,
        )
    ):
        items = payload["items"]
    else:
        return [], _invalid_file(
            "JSON community signal file must be a list or an object with only an items list."
        )

    raw_rows: list[tuple[int, dict[Any, Any]]] = []
    for row_number, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return [], _invalid_file(f"row {row_number}: row must be an object.")
        raw_rows.append((row_number, dict(item)))
    return raw_rows, None


def _raw_field_findings(
    raw: Mapping[Any, Any],
    *,
    row_number: int,
) -> list[CommunitySignalFinding]:
    findings: list[CommunitySignalFinding] = []
    for field in sorted(str(field) for field in raw):
        if field in ALLOWED_COMMUNITY_SIGNAL_FIELDS:
            continue
        if field in PROHIBITED_COMMUNITY_SIGNAL_FIELDS:
            findings.append(
                CommunitySignalFinding(
                    severity=CommunitySignalFindingSeverity.ERROR,
                    code="prohibited_field",
                    message="Field is excluded from the community signal contract.",
                    row=row_number,
                    field=field,
                )
            )
            continue
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="unknown_field",
                message="Field is not part of the community signal contract.",
                row=row_number,
                field=field,
            )
        )
    return findings


def _validate_import_ready_row(
    raw: Mapping[Any, Any],
    *,
    row_number: int,
    default_source_name: str,
) -> tuple[ManualSignalRow | None, list[CommunitySignalFinding]]:
    candidate = {str(key): value for key, value in raw.items()}
    if not str(candidate.get("source_name") or "").strip():
        candidate["source_name"] = default_source_name.strip() or "Manual Import"
    try:
        return ManualSignalRow.model_validate(candidate), []
    except (ValidationError, ValueError) as exc:
        return None, [
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="invalid_row",
                message=f"Row is not import-ready: {exc}",
                row=row_number,
                field="row",
            )
        ]


def _quality_findings(
    raw: Mapping[Any, Any],
    row: ManualSignalRow,
    *,
    row_number: int,
) -> list[CommunitySignalFinding]:
    findings: list[CommunitySignalFinding] = []
    if not str(raw.get("source_name") or "").strip():
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="missing_source_name",
                message="Row omits source_name; import will use the fallback source name.",
                row=row_number,
                field="source_name",
            )
        )
    if not str(raw.get("platform") or "").strip():
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="missing_platform",
                message="Row omits platform provenance.",
                row=row_number,
                field="platform",
            )
        )
    if not str(raw.get("summary") or "").strip():
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="missing_summary",
                message="Row omits a short sanitized summary.",
                row=row_number,
                field="summary",
            )
        )
    if not str(raw.get("source_weight") or "").strip():
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.INFO,
                code="implicit_source_weight",
                message="Row omits source_weight; import validation uses the default weight.",
                row=row_number,
                field="source_weight",
            )
        )
    if not str(raw.get("collected_at") or "").strip():
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.INFO,
                code="implicit_collected_at",
                message="Row omits collected_at; import time will be used.",
                row=row_number,
                field="collected_at",
            )
        )
    if row.collected_at is not None and row.collected_at < row.published_at:
        findings.append(
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="collected_before_published",
                message="collected_at is earlier than published_at.",
                row=row_number,
                field="collected_at",
            )
        )
    return findings


def _duplicate_url_findings(url_rows: Mapping[str, list[int]]) -> list[CommunitySignalFinding]:
    findings: list[CommunitySignalFinding] = []
    for _url, rows in sorted(url_rows.items()):
        if len(rows) < 2:
            continue
        row_list = ", ".join(str(row) for row in rows)
        for row_number in rows:
            findings.append(
                CommunitySignalFinding(
                    severity=CommunitySignalFindingSeverity.WARNING,
                    code="duplicate_url",
                    message=f"URL is duplicated in rows {row_list}.",
                    row=row_number,
                    field="url",
                )
            )
    return findings


def _sort_findings(
    findings: list[CommunitySignalFinding],
) -> list[CommunitySignalFinding]:
    severity_order = {
        CommunitySignalFindingSeverity.ERROR: 0,
        CommunitySignalFindingSeverity.WARNING: 1,
        CommunitySignalFindingSeverity.INFO: 2,
    }
    return sorted(
        findings,
        key=lambda finding: (
            severity_order[finding.severity],
            finding.row if finding.row is not None else -1,
            finding.field or "",
            finding.code,
            finding.message,
        ),
    )


def _count_findings(
    findings: list[CommunitySignalFinding],
    severity: CommunitySignalFindingSeverity,
) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _merge_count_dicts(counts: Iterable[Mapping[str, int]]) -> dict[str, int]:
    merged: Counter[str] = Counter()
    for count_map in counts:
        merged.update(count_map)
    return dict(sorted(merged.items()))


def _invalid_file(message: str) -> CommunitySignalFinding:
    return CommunitySignalFinding(
        severity=CommunitySignalFindingSeverity.ERROR,
        code="invalid_file",
        message=message,
    )
