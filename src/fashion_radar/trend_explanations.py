from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.utils.dates import parse_datetime_utc

TREND_EXPLANATION_BOUNDARIES = (
    "Configured sources and imported local signals only; no demand proof.",
    "No platform coverage verification is performed.",
)


class TrendExplanationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_kind: TrendSignalKind
    comparison_key: str
    name: str
    signal_type: str
    status: TrendStatus
    headline: str
    summary: str
    reason_codes: list[str] = Field(default_factory=list)
    current_score: float = 0.0
    baseline_score: float = 0.0
    score_delta: float = 0.0
    current_mentions: int = 0
    baseline_mentions: int = 0
    mention_delta: int = 0
    current_distinct_sources: int = 0
    baseline_distinct_sources: int = 0
    distinct_source_delta: int = 0
    current_label: str | None = None
    baseline_label: str | None = None
    first_seen_at: datetime | None = None

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class TrendExplanationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = "trend-explanations/v1"
    execution_mode: Literal["local_read_only"] = "local_read_only"
    as_of: datetime
    baseline_as_of: datetime
    item_count: int = 0
    items: list[TrendExplanationItem] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=lambda: list(TREND_EXPLANATION_BOUNDARIES))

    @field_validator("as_of", "baseline_as_of", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


def build_trend_explanations(
    comparison: TrendComparison,
    *,
    limit: int | None = None,
) -> TrendExplanationReport:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")

    items = [_to_explanation_item(delta) for delta in comparison.deltas]
    if limit is not None:
        items = items[:limit]
    return TrendExplanationReport(
        as_of=comparison.as_of,
        baseline_as_of=comparison.baseline_as_of,
        item_count=len(items),
        items=items,
    )


def render_trend_explanations_table(report: TrendExplanationReport) -> list[str]:
    lines = [
        "# Trend Explanations",
        "Local observed trend explanations need review.",
        f"As of: {report.as_of.isoformat()}",
        f"Baseline as of: {report.baseline_as_of.isoformat()}",
        *report.boundaries,
    ]
    if not report.items:
        lines.append("No local observed trend explanations in this comparison.")
        return lines
    lines.append("Status | Kind | Type | Name | Headline | Summary")
    for item in report.items:
        lines.append(
            f"{_cell(item.status.value)} | {_cell(item.signal_kind.value)} | "
            f"{_cell(item.signal_type)} | {_cell(item.name)} | {_cell(item.headline)} | "
            f"{_cell(item.summary)}"
        )
    return lines


def _to_explanation_item(delta: TrendDelta) -> TrendExplanationItem:
    return TrendExplanationItem(
        signal_kind=delta.signal_kind,
        comparison_key=delta.comparison_key,
        name=delta.name,
        signal_type=delta.signal_type,
        status=delta.status,
        headline=_headline(delta),
        summary=_summary(delta),
        reason_codes=_reason_codes(delta),
        current_score=delta.current_score,
        baseline_score=delta.baseline_score,
        score_delta=delta.score_delta,
        current_mentions=delta.current_mentions,
        baseline_mentions=delta.baseline_mentions,
        mention_delta=delta.mention_delta,
        current_distinct_sources=delta.current_distinct_sources,
        baseline_distinct_sources=delta.baseline_distinct_sources,
        distinct_source_delta=delta.distinct_source_delta,
        current_label=delta.current_label,
        baseline_label=delta.baseline_label,
        first_seen_at=delta.first_seen_at,
    )


def _headline(delta: TrendDelta) -> str:
    status_text = delta.status.value
    kind_text = _kind_text(delta.signal_kind)
    return f"Local observed {status_text} {kind_text} signal needs review."


def _summary(delta: TrendDelta) -> str:
    return (
        f"Local observed {_kind_text(delta.signal_kind)} signal from configured sources "
        f"and imported local signals: score {delta.score_delta:+.2f}, "
        f"mentions {delta.mention_delta:+d}, "
        f"distinct sources {delta.distinct_source_delta:+d}, {_label_text(delta)}. "
        f"{_status_clause(delta.status)}"
    )


def _reason_codes(delta: TrendDelta) -> list[str]:
    reasons = [f"status_{delta.status.value}"]
    if delta.score_delta > 0:
        reasons.append("score_increase_observed")
    elif delta.score_delta < 0:
        reasons.append("score_decrease_observed")
    if delta.mention_delta > 0:
        reasons.append("mention_increase_observed")
    elif delta.mention_delta < 0:
        reasons.append("mention_decrease_observed")
    if delta.distinct_source_delta > 0:
        reasons.append("source_diversity_increase_observed")
    elif delta.distinct_source_delta < 0:
        reasons.append("source_diversity_decrease_observed")
    if delta.current_label != delta.baseline_label:
        reasons.append("label_changed_observed")
    if delta.signal_kind == TrendSignalKind.CANDIDATE:
        reasons.append("candidate_signal_needs_review")
    return reasons


def _kind_text(signal_kind: TrendSignalKind) -> str:
    if signal_kind == TrendSignalKind.ENTITY:
        return "tracked entity"
    return "candidate phrase"


def _label_text(delta: TrendDelta) -> str:
    current = delta.current_label or "no current label"
    baseline = delta.baseline_label or "no baseline label"
    return f"label {current} from {baseline}"


def _status_clause(status: TrendStatus) -> str:
    mapping = {
        TrendStatus.NEW: "Signal was not present in the baseline snapshot.",
        TrendStatus.RISING: "Score and/or mention movement increased in the comparison window.",
        TrendStatus.COOLING: "Score and/or mention movement decreased in the comparison window.",
        TrendStatus.STABLE: "Score and mention movement did not agree on a rise or cooling signal.",
        TrendStatus.DROPPED: (
            "Signal was present in the baseline snapshot but not in the current snapshot."
        ),
    }
    return mapping[status]


def _cell(value: object) -> str:
    text = "-" if value is None else str(value)
    text = text.replace("|", " / ")
    text = " ".join(text.splitlines())
    return " ".join(text.split())
