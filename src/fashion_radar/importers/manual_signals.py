from __future__ import annotations

import csv
import json
from datetime import datetime
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
