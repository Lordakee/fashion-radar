from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from fashion_radar.heat_movers import (
    HeatMoverGroup,
    build_heat_movers,
    render_heat_movers_table,
)
from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus

AS_OF = datetime(2026, 6, 17, 9, 0, tzinfo=UTC)
BASELINE_AS_OF = datetime(2026, 6, 10, 9, 0, tzinfo=UTC)


def delta(
    name: str,
    *,
    signal_kind: TrendSignalKind = TrendSignalKind.ENTITY,
    status: TrendStatus = TrendStatus.NEW,
    signal_type: str = "brand",
    current_score: float = 5.0,
    baseline_score: float = 1.0,
    current_mentions: int = 5,
    baseline_mentions: int = 1,
    current_distinct_sources: int = 3,
    baseline_distinct_sources: int = 1,
    current_label: str | None = "watch",
    baseline_label: str | None = "baseline",
) -> TrendDelta:
    return TrendDelta(
        signal_kind=signal_kind,
        comparison_key=f"{signal_kind.value}:{signal_type}:{name.casefold()}",
        name=name,
        signal_type=signal_type,
        status=status,
        current_label=current_label,
        baseline_label=baseline_label,
        current_score=current_score,
        baseline_score=baseline_score,
        score_delta=current_score - baseline_score,
        current_mentions=current_mentions,
        baseline_mentions=baseline_mentions,
        mention_delta=current_mentions - baseline_mentions,
        current_internal_baseline_mentions=baseline_mentions,
        baseline_internal_baseline_mentions=baseline_mentions,
        current_growth_ratio=2.0,
        baseline_growth_ratio=1.0,
        current_distinct_sources=current_distinct_sources,
        baseline_distinct_sources=baseline_distinct_sources,
        distinct_source_delta=current_distinct_sources - baseline_distinct_sources,
        first_seen_at=BASELINE_AS_OF,
    )


def comparison(deltas: list[TrendDelta]) -> TrendComparison:
    return TrendComparison(as_of=AS_OF, baseline_as_of=BASELINE_AS_OF, deltas=deltas)


def group_rows(report, group_name: str):
    groups_by_name = {group.name: group for group in report.groups}
    return groups_by_name[group_name].rows


def group_names(report) -> list[str]:
    return [group.name for group in report.groups]


def test_entity_new_delta_goes_to_new_tracked_entities() -> None:
    report = build_heat_movers(
        comparison([delta("Alaia", signal_kind=TrendSignalKind.ENTITY, status=TrendStatus.NEW)])
    )

    rows = group_rows(report, "new_tracked_entities")

    assert [row.name for row in rows] == ["Alaia"]
    assert rows[0].signal_kind == TrendSignalKind.ENTITY
    assert rows[0].status == TrendStatus.NEW


def test_entity_rising_delta_goes_to_rising_tracked_entities() -> None:
    report = build_heat_movers(
        comparison(
            [delta("The Row", signal_kind=TrendSignalKind.ENTITY, status=TrendStatus.RISING)]
        )
    )

    rows = group_rows(report, "rising_tracked_entities")

    assert [row.name for row in rows] == ["The Row"]
    assert rows[0].signal_kind == TrendSignalKind.ENTITY
    assert rows[0].status == TrendStatus.RISING


def test_candidate_new_delta_goes_to_new_candidate_phrases() -> None:
    report = build_heat_movers(
        comparison(
            [
                delta(
                    "east-west bag",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    status=TrendStatus.NEW,
                    signal_type="phrase",
                )
            ]
        )
    )

    rows = group_rows(report, "new_candidate_phrases")

    assert [row.name for row in rows] == ["east-west bag"]
    assert rows[0].signal_kind == TrendSignalKind.CANDIDATE
    assert rows[0].status == TrendStatus.NEW


def test_candidate_rising_delta_goes_to_rising_candidate_phrases() -> None:
    report = build_heat_movers(
        comparison(
            [
                delta(
                    "mesh flats",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    status=TrendStatus.RISING,
                    signal_type="phrase",
                )
            ]
        )
    )

    rows = group_rows(report, "rising_candidate_phrases")

    assert [row.name for row in rows] == ["mesh flats"]
    assert rows[0].signal_kind == TrendSignalKind.CANDIDATE
    assert rows[0].status == TrendStatus.RISING


def test_cooling_watchlist_appears_only_when_requested() -> None:
    heat_delta = delta("Cooling Brand", status=TrendStatus.COOLING)

    default_report = build_heat_movers(comparison([heat_delta]))
    cooling_report = build_heat_movers(comparison([heat_delta]), include_cooling=True)

    assert "cooling_watchlist" not in group_names(default_report)
    assert default_report.row_count == 0
    assert group_names(cooling_report) == [
        "new_tracked_entities",
        "rising_tracked_entities",
        "new_candidate_phrases",
        "rising_candidate_phrases",
        "cooling_watchlist",
    ]
    assert [row.name for row in group_rows(cooling_report, "cooling_watchlist")] == [
        "Cooling Brand"
    ]


def test_stable_and_dropped_deltas_are_omitted() -> None:
    report = build_heat_movers(
        comparison(
            [
                delta("Flat Brand", status=TrendStatus.STABLE),
                delta("Dropped Brand", status=TrendStatus.DROPPED),
            ]
        ),
        include_cooling=True,
    )

    assert report.row_count == 0
    assert all(group.rows == [] for group in report.groups)


def test_limit_per_group_limits_each_group_independently() -> None:
    report = build_heat_movers(
        comparison(
            [
                delta("New Entity 1", signal_kind=TrendSignalKind.ENTITY, status=TrendStatus.NEW),
                delta("New Entity 2", signal_kind=TrendSignalKind.ENTITY, status=TrendStatus.NEW),
                delta(
                    "Rising Entity 1",
                    signal_kind=TrendSignalKind.ENTITY,
                    status=TrendStatus.RISING,
                ),
                delta(
                    "Rising Entity 2",
                    signal_kind=TrendSignalKind.ENTITY,
                    status=TrendStatus.RISING,
                ),
                delta(
                    "new phrase 1",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    status=TrendStatus.NEW,
                ),
                delta(
                    "new phrase 2",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    status=TrendStatus.NEW,
                ),
                delta(
                    "rising phrase 1",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    status=TrendStatus.RISING,
                ),
                delta(
                    "rising phrase 2",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    status=TrendStatus.RISING,
                ),
            ]
        ),
        limit_per_group=1,
    )

    assert [row.name for row in group_rows(report, "new_tracked_entities")] == ["New Entity 1"]
    assert [row.name for row in group_rows(report, "rising_tracked_entities")] == [
        "Rising Entity 1"
    ]
    assert [row.name for row in group_rows(report, "new_candidate_phrases")] == ["new phrase 1"]
    assert [row.name for row in group_rows(report, "rising_candidate_phrases")] == [
        "rising phrase 1"
    ]
    assert report.row_count == 4


def test_limit_per_group_zero_returns_groups_with_no_rows() -> None:
    report = build_heat_movers(
        comparison(
            [
                delta("Alaia", status=TrendStatus.NEW),
                delta("Cooling Brand", status=TrendStatus.COOLING),
            ]
        ),
        limit_per_group=0,
        include_cooling=True,
    )

    assert group_names(report) == [
        "new_tracked_entities",
        "rising_tracked_entities",
        "new_candidate_phrases",
        "rising_candidate_phrases",
        "cooling_watchlist",
    ]
    assert report.group_count == 5
    assert report.row_count == 0
    assert all(group.rows == [] for group in report.groups)


def test_negative_limit_per_group_raises_value_error() -> None:
    with pytest.raises(ValueError, match="limit_per_group must be at least 0"):
        build_heat_movers(comparison([]), limit_per_group=-1)


def test_heat_mover_group_name_rejects_unknown_groups() -> None:
    with pytest.raises(ValidationError):
        HeatMoverGroup(name="unknown_group", label="Unknown", rows=[])


def test_json_top_level_key_order_is_stable() -> None:
    report = build_heat_movers(comparison([]), include_cooling=True)
    payload = json.loads(report.model_dump_json())

    assert list(payload) == [
        "as_of",
        "baseline_as_of",
        "execution_mode",
        "limit_per_group",
        "include_cooling",
        "group_count",
        "row_count",
        "groups",
    ]


def test_table_renderer_sanitizes_cells_and_states_local_boundaries() -> None:
    report = build_heat_movers(
        comparison(
            [
                delta(
                    "Pipe|Name\nNext",
                    status=TrendStatus.NEW,
                    signal_type="brand|type",
                    current_label="review|local\nonly",
                    baseline_label=None,
                )
            ]
        )
    )

    lines = render_heat_movers_table(report)
    rendered = "\n".join(lines)
    rendered_lower = rendered.lower()

    assert "Local observed heat movers need review." in rendered
    assert (
        "Configured source set only; no demand proof or platform coverage verification." in rendered
    )
    assert "local observed heat movement" in rendered_lower
    assert "configured source set" in rendered_lower
    assert "no demand proof" in rendered_lower
    assert "no platform coverage verification" in rendered_lower
    assert all("\n" not in line for line in lines)
    assert "Pipe|Name" not in rendered
    assert "brand|type" not in rendered
    assert "review|local" not in rendered
    assert "Pipe / Name Next" in rendered
    assert "brand / type" in rendered
    assert "review / local only" in rendered


def test_table_renderer_states_empty_comparison() -> None:
    report = build_heat_movers(comparison([]))

    lines = render_heat_movers_table(report)
    rendered = "\n".join(lines)

    assert "No local observed heat movers in this comparison." in rendered
