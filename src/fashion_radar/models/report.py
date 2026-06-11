from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fashion_radar.utils.dates import parse_datetime_utc


class ReportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: datetime
    report_date: datetime
    item_count: int = 0

    @field_validator("generated_at", "report_date", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


class RepresentativeItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    source_url: str
    published_at: datetime
    title: str
    summary: str | None = None

    @field_validator("published_at", mode="before")
    @classmethod
    def normalize_published_at(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


class EntityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: str
    entity_type: str
    label: str
    heat_score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    representative_items: list[RepresentativeItem] = Field(default_factory=list)


class CandidateReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: str
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: datetime
    representative_items: list[RepresentativeItem] = Field(default_factory=list)

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


class SourceHealthReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    source_type: str
    consecutive_failures: int
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    unhealthy_until: datetime | None = None
    last_error_message: str | None = None

    @field_validator("last_success_at", "last_failure_at", "unhealthy_until", mode="before")
    @classmethod
    def normalize_optional_datetime(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class CollectorRunReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    source_type: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    items_seen: int
    items_stored: int
    error_message: str | None = None
    error_type: str | None = None

    @field_validator("started_at", "finished_at", mode="before")
    @classmethod
    def normalize_run_datetime(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class DailyReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: ReportMetadata
    entities: list[EntityReport] = Field(default_factory=list)
    candidates: list[CandidateReport] = Field(default_factory=list)
    source_health: list[SourceHealthReport] = Field(default_factory=list)
    recent_runs: list[CollectorRunReport] = Field(default_factory=list)
