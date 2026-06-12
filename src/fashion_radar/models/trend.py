from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

from fashion_radar.utils.dates import parse_datetime_utc


class TrendSignalKind(StrEnum):
    ENTITY = "entity"
    CANDIDATE = "candidate"


class TrendStatus(StrEnum):
    NEW = "new"
    RISING = "rising"
    COOLING = "cooling"
    STABLE = "stable"
    DROPPED = "dropped"


class TrendDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_kind: TrendSignalKind
    comparison_key: str
    name: str
    signal_type: str
    status: TrendStatus
    current_label: str | None = None
    baseline_label: str | None = None
    current_score: float = 0.0
    baseline_score: float = 0.0
    score_delta: float = 0.0
    current_mentions: int = 0
    baseline_mentions: int = 0
    mention_delta: int = 0
    current_internal_baseline_mentions: int = 0
    baseline_internal_baseline_mentions: int = 0
    current_growth_ratio: float | None = None
    baseline_growth_ratio: float | None = None
    current_distinct_sources: int = 0
    baseline_distinct_sources: int = 0
    distinct_source_delta: int = 0
    first_seen_at: datetime | None = None

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class TrendComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: datetime
    baseline_as_of: datetime
    deltas: list[TrendDelta]

    @field_validator("as_of", "baseline_as_of", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)
