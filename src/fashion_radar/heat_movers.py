from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.utils.dates import parse_datetime_utc

ExecutionMode = Literal["local_read_only"]
HeatMoverGroupName = Literal[
    "new_tracked_entities",
    "rising_tracked_entities",
    "new_candidate_phrases",
    "rising_candidate_phrases",
    "cooling_watchlist",
]


class HeatMover(BaseModel):
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
    current_distinct_sources: int = 0
    baseline_distinct_sources: int = 0
    distinct_source_delta: int = 0
    first_seen_at: datetime | None = None

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class HeatMoverGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: HeatMoverGroupName
    label: str
    rows: list[HeatMover]


class HeatMoversReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: datetime
    baseline_as_of: datetime
    execution_mode: ExecutionMode = "local_read_only"
    limit_per_group: int | None
    include_cooling: bool
    group_count: int
    row_count: int
    groups: list[HeatMoverGroup]

    @field_validator("as_of", "baseline_as_of", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


GroupMatcher = Callable[[TrendDelta], bool]


def build_heat_movers(
    comparison: TrendComparison,
    *,
    limit_per_group: int | None = 5,
    include_cooling: bool = False,
) -> HeatMoversReport:
    if limit_per_group is not None and limit_per_group < 0:
        raise ValueError("limit_per_group must be at least 0")

    specs = [
        (
            "new_tracked_entities",
            "New tracked entities",
            _matches(TrendSignalKind.ENTITY, TrendStatus.NEW),
        ),
        (
            "rising_tracked_entities",
            "Rising tracked entities",
            _matches(TrendSignalKind.ENTITY, TrendStatus.RISING),
        ),
        (
            "new_candidate_phrases",
            "New candidate phrases",
            _matches(TrendSignalKind.CANDIDATE, TrendStatus.NEW),
        ),
        (
            "rising_candidate_phrases",
            "Rising candidate phrases",
            _matches(TrendSignalKind.CANDIDATE, TrendStatus.RISING),
        ),
    ]
    if include_cooling:
        specs.append(
            ("cooling_watchlist", "Cooling watchlist", _matches_status(TrendStatus.COOLING))
        )

    groups = [
        HeatMoverGroup(
            name=name,
            label=label,
            rows=_limited(
                [_to_heat_mover(delta) for delta in comparison.deltas if matcher(delta)],
                limit_per_group,
            ),
        )
        for name, label, matcher in specs
    ]

    return HeatMoversReport(
        as_of=comparison.as_of,
        baseline_as_of=comparison.baseline_as_of,
        limit_per_group=limit_per_group,
        include_cooling=include_cooling,
        group_count=len(groups),
        row_count=sum(len(group.rows) for group in groups),
        groups=groups,
    )


def render_heat_movers_table(report: HeatMoversReport) -> list[str]:
    lines = [
        "# Heat Movers",
        "Local observed heat movers need review.",
        (
            "Local observed heat movement across the configured source set "
            f"from {_format_datetime(report.baseline_as_of)} to {_format_datetime(report.as_of)}."
        ),
        "Configured source set only; no demand proof or platform coverage verification.",
        "No platform coverage verification is performed.",
        (
            f"Execution mode: {_cell(report.execution_mode)}; "
            f"limit per group: {_format_limit(report.limit_per_group)}; rows: {report.row_count}."
        ),
        "",
    ]
    if report.row_count == 0:
        lines.extend(["No local observed heat movers in this comparison.", ""])

    for group in report.groups:
        lines.append(f"## {_cell(group.label)}")
        if not group.rows:
            lines.extend(["_No rows._", ""])
            continue

        lines.extend(
            [
                (
                    "| Name | Kind | Type | Status | Score delta | Mentions | "
                    "Sources | Label | First seen |"
                ),
                "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in group.rows:
            lines.append(
                " | ".join(
                    [
                        f"| {_cell(row.name)}",
                        _cell(row.signal_kind.value),
                        _cell(row.signal_type),
                        _cell(row.status.value),
                        _format_float_delta(row.score_delta),
                        _format_int_delta(row.mention_delta),
                        _format_int_delta(row.distinct_source_delta),
                        _cell(_format_label(row)),
                        f"{_cell(_format_datetime(row.first_seen_at))} |",
                    ]
                )
            )
        lines.append("")

    return lines


def _matches(signal_kind: TrendSignalKind, status: TrendStatus) -> GroupMatcher:
    return lambda delta: delta.signal_kind == signal_kind and delta.status == status


def _matches_status(status: TrendStatus) -> GroupMatcher:
    return lambda delta: delta.status == status


def _limited(rows: list[HeatMover], limit: int | None) -> list[HeatMover]:
    if limit is None:
        return rows
    return rows[:limit]


def _to_heat_mover(delta: TrendDelta) -> HeatMover:
    return HeatMover(
        signal_kind=delta.signal_kind,
        comparison_key=delta.comparison_key,
        name=delta.name,
        signal_type=delta.signal_type,
        status=delta.status,
        current_label=delta.current_label,
        baseline_label=delta.baseline_label,
        current_score=delta.current_score,
        baseline_score=delta.baseline_score,
        score_delta=delta.score_delta,
        current_mentions=delta.current_mentions,
        baseline_mentions=delta.baseline_mentions,
        mention_delta=delta.mention_delta,
        current_distinct_sources=delta.current_distinct_sources,
        baseline_distinct_sources=delta.baseline_distinct_sources,
        distinct_source_delta=delta.distinct_source_delta,
        first_seen_at=delta.first_seen_at,
    )


def _format_label(row: HeatMover) -> str:
    if row.current_label and row.baseline_label:
        return f"{row.current_label} (was {row.baseline_label})"
    if row.current_label:
        return row.current_label
    if row.baseline_label:
        return f"was {row.baseline_label}"
    return "-"


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.isoformat()


def _format_limit(limit: int | None) -> str:
    return "none" if limit is None else str(limit)


def _format_float_delta(value: float) -> str:
    return f"{value:+.2f}"


def _format_int_delta(value: int) -> str:
    return f"{value:+d}"


def _cell(value: object) -> str:
    text = "-" if value is None else str(value)
    text = text.replace("|", " / ")
    text = " ".join(text.splitlines())
    text = " ".join(text.split())
    return text or "-"
