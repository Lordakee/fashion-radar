from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.utils.dates import parse_datetime_utc


class CollectorRunStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class CollectorRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    source_type: SourceType
    status: CollectorRunStatus
    started_at: datetime
    finished_at: datetime
    items_seen: int = 0
    items_collected: int = 0
    error_message: str | None = None
    error_type: str | None = None

    @field_validator("started_at", "finished_at", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


class CollectorResult(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    status: CollectorRunSummary
    items: list[CollectedItem]

    @classmethod
    def success(
        cls,
        source: SourceDefinition,
        *,
        items: list[CollectedItem],
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        items_seen: int | None = None,
    ) -> CollectorResult:
        now = datetime.now(tz=UTC)
        started = parse_datetime_utc(started_at or now)
        finished = parse_datetime_utc(finished_at or now)
        return cls(
            status=CollectorRunSummary(
                source_name=source.name,
                source_type=source.type,
                status=CollectorRunStatus.SUCCESS,
                started_at=started,
                finished_at=finished,
                items_seen=len(items) if items_seen is None else items_seen,
                items_collected=len(items),
            ),
            items=items,
        )

    @classmethod
    def failed(
        cls,
        source: SourceDefinition,
        *,
        error: Exception,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> CollectorResult:
        now = datetime.now(tz=UTC)
        return cls(
            status=CollectorRunSummary(
                source_name=source.name,
                source_type=source.type,
                status=CollectorRunStatus.FAILED,
                started_at=parse_datetime_utc(started_at or now),
                finished_at=parse_datetime_utc(finished_at or now),
                error_message=str(error),
                error_type=type(error).__name__,
            ),
            items=[],
        )

    @classmethod
    def skipped(
        cls,
        source: SourceDefinition,
        *,
        reason: str,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> CollectorResult:
        now = datetime.now(tz=UTC)
        return cls(
            status=CollectorRunSummary(
                source_name=source.name,
                source_type=source.type,
                status=CollectorRunStatus.SKIPPED,
                started_at=parse_datetime_utc(started_at or now),
                finished_at=parse_datetime_utc(finished_at or now),
                error_message=reason,
            ),
            items=[],
        )
