from __future__ import annotations

import csv
import fnmatch
import json
from collections import Counter
from collections.abc import Iterable
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy.engine import Engine

from fashion_radar.db.repositories import ItemRepository
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.utils.dates import parse_datetime_utc

ManualSignalFormat = Literal["csv", "json"]


class ManualSignalImportError(ValueError):
    """Raised when a manual signal import file cannot be parsed or validated."""


class ManualSignalRow(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: str
    title: str
    published_at: datetime
    summary: str | None = None
    source_name: str
    platform: str | None = None
    source_weight: float = Field(default=1.0, gt=0, le=5)
    collected_at: datetime | None = None

    @field_validator("url", "title", "source_name")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not str(value).strip():
            raise ValueError("field cannot be empty")
        return str(value).strip()

    @field_validator("summary", "platform", mode="before")
    @classmethod
    def blank_optional_to_none(cls, value: object) -> object | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("source_weight", mode="before")
    @classmethod
    def blank_source_weight_to_default(cls, value: object) -> object:
        if value is None or not str(value).strip():
            return 1.0
        return value

    @field_validator("published_at", mode="before")
    @classmethod
    def normalize_published_at(cls, value: object) -> datetime:
        if value is None or not str(value).strip():
            raise ValueError("field cannot be empty")
        try:
            return parse_datetime_utc(value)
        except TypeError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("collected_at", mode="before")
    @classmethod
    def normalize_collected_at(cls, value: object | None) -> datetime | None:
        if value is None or not str(value).strip():
            return None
        try:
            return parse_datetime_utc(value)
        except TypeError as exc:
            raise ValueError(str(exc)) from exc


class ManualSignalImportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rows_seen: int
    rows_imported: int
    items_added: int


class ManualSignalDryRunFindingSeverity(StrEnum):
    ERROR = "error"


class ManualSignalDirectoryDryRunFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: ManualSignalDryRunFindingSeverity
    code: str
    message: str
    path: str | None = None


class ManualSignalDirectoryDryRunFileResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    row_count: int = 0
    error_count: int = 0
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[ManualSignalDirectoryDryRunFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


class ManualSignalDirectoryDryRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directory: str
    input_format: ManualSignalFormat
    pattern: str
    file_count: int = 0
    valid_file_count: int = 0
    row_count: int = 0
    error_count: int = 0
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    files: list[ManualSignalDirectoryDryRunFileResult] = Field(default_factory=list)
    findings: list[ManualSignalDirectoryDryRunFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


def load_manual_signal_rows(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str,
) -> list[ManualSignalRow]:
    raw_rows = _read_raw_rows(path, input_format=input_format)
    fallback_source_name = default_source_name.strip() or "Manual Import"
    rows: list[ManualSignalRow] = []
    for index, raw in enumerate(raw_rows, start=2 if input_format == "csv" else 1):
        if not isinstance(raw, dict):
            raise ManualSignalImportError(f"row {index}: row must be an object")
        if None in raw:
            raise ManualSignalImportError(f"row {index}: CSV row has more cells than headers")
        candidate = {**raw}
        if not str(candidate.get("source_name") or "").strip():
            candidate["source_name"] = fallback_source_name
        try:
            rows.append(ManualSignalRow.model_validate(candidate))
        except (ValidationError, ValueError) as exc:
            raise ManualSignalImportError(f"row {index}: {exc}") from exc
    return rows


def _read_raw_rows(path: Path, *, input_format: ManualSignalFormat) -> list[object]:
    try:
        if input_format == "csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    raise ManualSignalImportError("CSV file must contain headers")
                return list(reader)
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManualSignalImportError(f"Could not read import file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ManualSignalImportError(f"Invalid JSON in {path}: {exc}") from exc

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ManualSignalImportError("JSON import must be a list or an object with an items list")


def dry_run_manual_signal_directory(
    directory: Path,
    *,
    input_format: ManualSignalFormat,
    pattern: str,
    default_source_name: str,
) -> ManualSignalDirectoryDryRunResult:
    findings: list[ManualSignalDirectoryDryRunFinding] = []
    try:
        if not directory.is_dir():
            return ManualSignalDirectoryDryRunResult(
                directory=str(directory),
                input_format=input_format,
                pattern=pattern,
                error_count=1,
                findings=[
                    ManualSignalDirectoryDryRunFinding(
                        severity=ManualSignalDryRunFindingSeverity.ERROR,
                        code="invalid_directory",
                        message=("Manual signal directory does not exist or is not a directory."),
                    )
                ],
            )
        children = list(directory.iterdir())
    except OSError:
        return ManualSignalDirectoryDryRunResult(
            directory=str(directory),
            input_format=input_format,
            pattern=pattern,
            error_count=1,
            findings=[
                ManualSignalDirectoryDryRunFinding(
                    severity=ManualSignalDryRunFindingSeverity.ERROR,
                    code="invalid_directory",
                    message="Could not read manual signal directory.",
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
            ManualSignalDirectoryDryRunFinding(
                severity=ManualSignalDryRunFindingSeverity.ERROR,
                code="no_matching_files",
                message="No regular files matched the pattern in the directory.",
            )
        )

    file_results = [
        _dry_run_manual_signal_file(
            path,
            input_format=input_format,
            default_source_name=default_source_name,
        )
        for path in paths
    ]
    return ManualSignalDirectoryDryRunResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        file_count=len(file_results),
        valid_file_count=sum(1 for file in file_results if file.ok),
        row_count=sum(file.row_count for file in file_results),
        error_count=len(findings) + sum(file.error_count for file in file_results),
        source_name_counts=_merge_count_dicts(file.source_name_counts for file in file_results),
        platform_counts=_merge_count_dicts(file.platform_counts for file in file_results),
        files=file_results,
        findings=findings,
    )


def render_manual_signal_directory_dry_run_table(
    result: ManualSignalDirectoryDryRunResult,
) -> list[str]:
    lines = [
        f"Import signals directory dry run: {result.directory}",
        f"Input format: {result.input_format}",
        f"Pattern: {result.pattern}",
        f"Files: {result.file_count} total, {result.valid_file_count} valid",
        f"Rows: {result.row_count} import-ready",
        f"Sources: {_format_counts(result.source_name_counts)}",
        f"Platforms: {_format_counts(result.platform_counts)}",
        f"Errors: {result.error_count}",
    ]
    if result.files:
        lines.append("Files:")
        for file in result.files:
            lines.append(f"- {file.path}: {file.row_count} rows, {file.error_count} errors")
    if not result.findings and all(not file.findings for file in result.files):
        lines.append("No manual signal directory dry-run errors.")
        return lines

    lines.append("Severity | File | Code | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | {finding.path or 'n/a'} | "
            f"{finding.code} | {finding.message}"
        )
    for file in result.files:
        for finding in file.findings:
            lines.append(
                f"{finding.severity.value} | {file.path} | {finding.code} | {finding.message}"
            )
    return lines


def _dry_run_manual_signal_file(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str,
) -> ManualSignalDirectoryDryRunFileResult:
    try:
        rows = load_manual_signal_rows(
            path,
            input_format=input_format,
            default_source_name=default_source_name,
        )
    except ManualSignalImportError as exc:
        return ManualSignalDirectoryDryRunFileResult(
            path=str(path),
            error_count=1,
            findings=[
                ManualSignalDirectoryDryRunFinding(
                    severity=ManualSignalDryRunFindingSeverity.ERROR,
                    code="invalid_file",
                    message=f"Could not dry-run import file: {exc}",
                    path=str(path),
                )
            ],
        )

    return ManualSignalDirectoryDryRunFileResult(
        path=str(path),
        row_count=len(rows),
        source_name_counts=dict(sorted(Counter(row.source_name for row in rows).items())),
        platform_counts=dict(sorted(Counter(row.platform for row in rows if row.platform).items())),
    )


def store_manual_signal_rows(
    engine: Engine,
    *,
    rows: list[ManualSignalRow],
    imported_at: datetime,
) -> ManualSignalImportResult:
    repository = ItemRepository(engine)
    before_count = repository.count_items()
    imported_at_utc = parse_datetime_utc(imported_at)
    for row in rows:
        repository.upsert_item(
            CollectedItem(
                source_name=row.source_name,
                source_type=SourceType.MANUAL_IMPORT,
                url=row.url,
                title=row.title,
                published_at=row.published_at,
                summary=row.summary,
            ),
            source_weight=row.source_weight,
            collected_at=row.collected_at or imported_at_utc,
        )
    after_count = repository.count_items()
    return ManualSignalImportResult(
        rows_seen=len(rows),
        rows_imported=len(rows),
        items_added=max(0, after_count - before_count),
    )


def _merge_count_dicts(counts: Iterable[dict[str, int]]) -> dict[str, int]:
    merged: Counter[str] = Counter()
    for count_map in counts:
        merged.update(count_map)
    return dict(sorted(merged.items()))


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
