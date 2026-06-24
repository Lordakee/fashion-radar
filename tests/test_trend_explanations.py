from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.trend_explanations import (
    TrendExplanationReport,
    build_trend_explanations,
    render_trend_explanations_table,
)

AS_OF = datetime(2026, 6, 24, 12, 0, tzinfo=UTC)
BASELINE_AS_OF = datetime(2026, 6, 17, 12, 0, tzinfo=UTC)


def delta(
    name: str,
    *,
    signal_kind: TrendSignalKind = TrendSignalKind.ENTITY,
    status: TrendStatus = TrendStatus.RISING,
    signal_type: str = "brand",
    current_score: float = 5.0,
    baseline_score: float = 2.0,
    current_mentions: int = 5,
    baseline_mentions: int = 2,
    current_distinct_sources: int = 3,
    baseline_distinct_sources: int = 1,
    current_label: str | None = "rising",
    baseline_label: str | None = "stable",
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


def test_build_trend_explanations_preserves_delta_order_and_derives_reasons() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta("The Row", status=TrendStatus.NEW, current_label="new", baseline_label=None),
                delta(
                    "Mesh flats",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    signal_type="phrase",
                    status=TrendStatus.RISING,
                ),
            ]
        )
    )

    assert [item.name for item in report.items] == ["The Row", "Mesh flats"]
    assert report.items[0].headline == "Local observed new tracked entity signal needs review."
    assert report.items[0].reason_codes == [
        "status_new",
        "score_increase_observed",
        "mention_increase_observed",
        "source_diversity_increase_observed",
        "label_changed_observed",
    ]
    assert report.items[1].headline == "Local observed rising candidate phrase signal needs review."
    assert "candidate_signal_needs_review" in report.items[1].reason_codes
    assert "configured sources and imported local signals" in report.items[1].summary


def test_build_trend_explanations_handles_stable_and_dropped_statuses() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta(
                    "Mixed Brand",
                    status=TrendStatus.STABLE,
                    current_score=4.0,
                    baseline_score=1.0,
                    current_mentions=1,
                    baseline_mentions=4,
                    current_distinct_sources=2,
                    baseline_distinct_sources=2,
                ),
                delta(
                    "Old Brand",
                    status=TrendStatus.DROPPED,
                    current_score=0.0,
                    baseline_score=3.0,
                    current_mentions=0,
                    baseline_mentions=3,
                    current_distinct_sources=0,
                    baseline_distinct_sources=2,
                    current_label=None,
                    baseline_label="watch",
                ),
            ]
        )
    )

    assert report.items[0].headline == "Local observed stable tracked entity signal needs review."
    assert "status_stable" in report.items[0].reason_codes
    assert report.items[1].headline == "Local observed dropped tracked entity signal needs review."
    assert "status_dropped" in report.items[1].reason_codes
    assert (
        "Signal was present in the baseline snapshot but not in the current snapshot."
        in report.items[1].summary
    )


def test_build_trend_explanations_status_clauses_allow_flat_dimensions() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta(
                    "Flat mentions",
                    status=TrendStatus.RISING,
                    current_score=3.0,
                    baseline_score=1.0,
                    current_mentions=2,
                    baseline_mentions=2,
                ),
                delta(
                    "Flat score",
                    status=TrendStatus.COOLING,
                    current_score=2.0,
                    baseline_score=2.0,
                    current_mentions=1,
                    baseline_mentions=3,
                ),
            ]
        )
    )

    assert "Score and/or mention movement increased" in report.items[0].summary
    assert "mention_increase_observed" not in report.items[0].reason_codes
    assert "Score and/or mention movement decreased" in report.items[1].summary
    assert "score_decrease_observed" not in report.items[1].reason_codes


def test_trend_explanations_json_top_level_key_order_is_stable() -> None:
    report = build_trend_explanations(comparison([]))
    payload = json.loads(report.model_dump_json())

    assert isinstance(report, TrendExplanationReport)
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "as_of",
        "baseline_as_of",
        "item_count",
        "items",
        "boundaries",
    ]


def test_trend_explanations_table_states_boundaries_and_empty_report() -> None:
    report = build_trend_explanations(comparison([]))

    rendered = "\n".join(render_trend_explanations_table(report))

    assert "Local observed trend explanations need review." in rendered
    assert "configured sources and imported local signals" in rendered.lower()
    assert "no demand proof" in rendered.lower()
    assert "No platform coverage verification is performed." in rendered
    assert "No local observed trend explanations in this comparison." in rendered


def test_trend_explanations_table_sanitizes_dynamic_cells() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta(
                    "The|Row\nDrop",
                    signal_type="brand|\nline",
                    current_label="now|\nlabel",
                    baseline_label="base|\nlabel",
                )
            ]
        )
    )

    row = render_trend_explanations_table(report)[-1]

    assert "The / Row Drop" in row
    assert "brand / line" in row
    assert "now / label" in row
    assert "\n" not in row


def test_trend_explanations_limit_truncates_existing_order() -> None:
    report = build_trend_explanations(
        comparison([delta("A"), delta("B"), delta("C")]),
        limit=2,
    )

    assert [item.name for item in report.items] == ["A", "B"]
    assert report.item_count == 2

    zero = build_trend_explanations(comparison([delta("A")]), limit=0)
    assert zero.items == []
    assert zero.item_count == 0


def test_trend_explanations_rejects_negative_limit() -> None:
    with pytest.raises(ValueError, match="limit must be at least 0"):
        build_trend_explanations(comparison([]), limit=-1)
