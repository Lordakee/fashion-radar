from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fashion_radar.utils.dates import parse_datetime_utc

REPORT_SNIPPET_MAX_CHARS = 500


def report_safe_snippet(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    if len(normalized) <= REPORT_SNIPPET_MAX_CHARS:
        return normalized
    return normalized[: REPORT_SNIPPET_MAX_CHARS - 3].rstrip() + "..."


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

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: str | None) -> str | None:
        return report_safe_snippet(value)


class EntityMatchEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matched_items: int = 0
    accepted_without_context_items: int = 0
    context_supported_items: int = 0
    parent_brand_supported_items: int = 0
    safe_alias_supported_items: int = 0
    other_supported_items: int = 0
    min_confidence: float | None = None
    avg_confidence: float | None = None
    max_confidence: float | None = None


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
    weighted_mention_component: float = 0.0
    growth_component: float = 0.0
    source_diversity_component: float = 0.0
    high_weight_component: float = 0.0
    representative_items: list[RepresentativeItem] = Field(default_factory=list)
    match_evidence: EntityMatchEvidence = Field(default_factory=EntityMatchEvidence)


class CandidateReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: str
    score: float
    weighted_mention_component: float = 0.0
    growth_component: float = 0.0
    source_diversity_component: float = 0.0
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


DAILY_BRIEF_BOUNDARIES = (
    (
        "Daily Brief is derived from local report rows for configured sources "
        "and imported local signals."
    ),
    (
        "Daily Brief does not collect sources, search platforms, prove demand, "
        "or verify platform coverage."
    ),
)


class DailyBriefItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal[
        "tracked_entity",
        "candidate_phrase",
        "source_caveat",
        "collector_run_caveat",
    ]
    title: str
    summary: str
    reason_codes: list[str] = Field(default_factory=list)
    current_mentions: int | None = None
    baseline_mentions: int | None = None
    distinct_sources: int | None = None
    score: float | None = None
    needs_review: bool = False


class DailyBriefSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["tracked_signals", "candidate_signals", "source_caveats"]
    title: str
    items: list[DailyBriefItem] = Field(default_factory=list)


class DailyBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = "daily-brief/v1"
    execution_mode: Literal["local_report_derived"] = "local_report_derived"
    summary: str
    sections: list[DailyBriefSection] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=lambda: list(DAILY_BRIEF_BOUNDARIES))


def empty_daily_brief() -> DailyBrief:
    return DailyBrief(
        summary=(
            "Local observed brief from configured sources and imported local signals: "
            "0 tracked signals, 0 candidate signals needing review, 0 source caveats. "
            "It provides no demand proof and no platform coverage verification."
        ),
        sections=[
            DailyBriefSection(name="tracked_signals", title="Tracked Signals To Review"),
            DailyBriefSection(
                name="candidate_signals",
                title="Candidate Signals Needing Review",
            ),
            DailyBriefSection(name="source_caveats", title="Source Caveats"),
        ],
    )


class DailyReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: ReportMetadata
    brief: DailyBrief = Field(default_factory=empty_daily_brief)
    entities: list[EntityReport] = Field(default_factory=list)
    candidates: list[CandidateReport] = Field(default_factory=list)
    source_health: list[SourceHealthReport] = Field(default_factory=list)
    recent_runs: list[CollectorRunReport] = Field(default_factory=list)
