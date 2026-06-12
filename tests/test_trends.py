from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import fashion_radar.trends as trends_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.discovery.candidates import CandidateMetric
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.models.trend import TrendComparison, TrendSignalKind, TrendStatus
from fashion_radar.scoring import EntityHeatMetric
from fashion_radar.settings import CandidateDiscoverySettings, ScoringSettings
from fashion_radar.trends import compare_trends

AS_OF = datetime(2026, 6, 12, tzinfo=UTC)
BASELINE_AS_OF = datetime(2026, 6, 5, tzinfo=UTC)


def store_observed_item(
    engine,
    *,
    title: str,
    url: str,
    source_name: str,
    collected_at: datetime,
) -> int:
    return ItemRepository(engine).upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=SourceType.RSS,
            url=url,
            title=title,
            published_at=collected_at,
            summary=title,
        ),
        collected_at=collected_at,
    )


def entity_metric(
    name: str,
    *,
    entity_type: str = "brand",
    label: str = "stable",
    score: float = 1.0,
    current_mentions: int = 1,
    baseline_mentions: int = 0,
    distinct_sources: int = 1,
    growth_ratio: float | None = None,
    first_seen_at: datetime = BASELINE_AS_OF,
) -> EntityHeatMetric:
    return EntityHeatMetric(
        entity_name=name,
        entity_type=entity_type,
        label=label,
        heat_score=score,
        current_mentions=current_mentions,
        baseline_mentions=baseline_mentions,
        weighted_mention_sum=float(current_mentions),
        distinct_sources=distinct_sources,
        growth_ratio=growth_ratio,
        first_seen_at=first_seen_at,
        weighted_mention_component=score,
        growth_component=0.0,
        source_diversity_component=0.0,
        high_weight_component=0.0,
    )


def candidate_metric(
    phrase: str,
    *,
    candidate_type: str = "brand",
    label: str = "review",
    score: float = 1.0,
    current_mentions: int = 1,
    baseline_mentions: int = 0,
    distinct_sources: int = 1,
    growth_ratio: float | None = None,
    first_seen_at: datetime = BASELINE_AS_OF,
) -> CandidateMetric:
    return CandidateMetric(
        phrase=phrase,
        normalized_key=phrase.casefold(),
        candidate_type=candidate_type,
        label=label,
        score=score,
        current_mentions=current_mentions,
        baseline_mentions=baseline_mentions,
        distinct_sources=distinct_sources,
        growth_ratio=growth_ratio,
        first_seen_at=first_seen_at,
        contexts=(),
        representative_items=(),
    )


def test_compare_trends_marks_snapshot_new_and_rising_entities() -> None:
    comparison = compare_trends(
        current_entities=[
            entity_metric("The Row", score=4.0, current_mentions=4),
            entity_metric("Alaia", score=3.0, current_mentions=3),
        ],
        baseline_entities=[entity_metric("The Row", score=1.0, current_mentions=1)],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    by_name = {delta.name: delta for delta in comparison.deltas}

    assert by_name["Alaia"].status == TrendStatus.NEW
    assert by_name["Alaia"].signal_kind == TrendSignalKind.ENTITY
    assert by_name["The Row"].status == TrendStatus.RISING
    assert by_name["The Row"].score_delta == 3.0
    assert by_name["The Row"].mention_delta == 3


def test_compare_trends_can_include_dropped_signals() -> None:
    comparison = compare_trends(
        current_entities=[],
        baseline_entities=[entity_metric("Phoebe Philo", entity_type="designer")],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
        include_dropped=True,
    )

    assert len(comparison.deltas) == 1
    assert comparison.deltas[0].name == "Phoebe Philo"
    assert comparison.deltas[0].status == TrendStatus.DROPPED
    assert comparison.deltas[0].signal_type == "designer"


def test_compare_trends_omits_dropped_signals_by_default() -> None:
    comparison = compare_trends(
        current_entities=[],
        baseline_entities=[entity_metric("Phoebe Philo", entity_type="designer")],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert comparison.deltas == []


def test_compare_trends_sorts_by_status_and_delta() -> None:
    comparison = compare_trends(
        current_entities=[
            entity_metric("Stable Brand", score=2.0, current_mentions=2),
            entity_metric("Rising Small", score=3.0, current_mentions=3),
            entity_metric("New Brand", score=1.0, current_mentions=1),
            entity_metric("Rising Large", score=8.0, current_mentions=8),
        ],
        baseline_entities=[
            entity_metric("Stable Brand", score=2.0, current_mentions=2),
            entity_metric("Rising Small", score=1.0, current_mentions=1),
            entity_metric("Rising Large", score=1.0, current_mentions=1),
        ],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert [delta.name for delta in comparison.deltas] == [
        "New Brand",
        "Rising Large",
        "Rising Small",
        "Stable Brand",
    ]


def test_compare_trends_handles_candidate_phrases() -> None:
    comparison = compare_trends(
        current_entities=[],
        baseline_entities=[],
        current_candidates=[candidate_metric("east-west bag", score=4.0, current_mentions=4)],
        baseline_candidates=[candidate_metric("east west bag", score=1.0, current_mentions=1)],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert len(comparison.deltas) == 1
    delta = comparison.deltas[0]
    assert delta.signal_kind == TrendSignalKind.CANDIDATE
    assert delta.name == "east-west bag"
    assert delta.status == TrendStatus.RISING
    assert delta.score_delta == 3.0


def test_compare_trends_treats_score_up_mentions_down_as_stable() -> None:
    comparison = compare_trends(
        current_entities=[entity_metric("Mixed Brand", score=4.0, current_mentions=1)],
        baseline_entities=[entity_metric("Mixed Brand", score=1.0, current_mentions=4)],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert comparison.deltas[0].status == TrendStatus.STABLE
    assert comparison.deltas[0].score_delta == 3.0
    assert comparison.deltas[0].mention_delta == -3


def test_compare_trends_treats_score_down_mentions_up_as_stable() -> None:
    comparison = compare_trends(
        current_entities=[entity_metric("Mixed Brand", score=1.0, current_mentions=4)],
        baseline_entities=[entity_metric("Mixed Brand", score=4.0, current_mentions=1)],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert comparison.deltas[0].status == TrendStatus.STABLE
    assert comparison.deltas[0].score_delta == -3.0
    assert comparison.deltas[0].mention_delta == 3


def test_compare_trends_status_boundaries_are_deterministic() -> None:
    cases = [
        (2.0, 1, TrendStatus.RISING),
        (-2.0, -1, TrendStatus.COOLING),
        (0.0, 2, TrendStatus.RISING),
        (0.0, -2, TrendStatus.COOLING),
        (0.0, 0, TrendStatus.STABLE),
    ]

    for score_delta, mention_delta, expected in cases:
        current_score = 3.0 + score_delta
        current_mentions = 3 + mention_delta
        comparison = compare_trends(
            current_entities=[
                entity_metric(
                    "Boundary Brand",
                    score=current_score,
                    current_mentions=current_mentions,
                )
            ],
            baseline_entities=[entity_metric("Boundary Brand", score=3.0, current_mentions=3)],
            current_candidates=[],
            baseline_candidates=[],
            as_of=AS_OF,
            baseline_as_of=BASELINE_AS_OF,
        )
        assert comparison.deltas[0].status == expected


def test_compare_trends_exposes_internal_baseline_mentions_with_explicit_names() -> None:
    comparison = compare_trends(
        current_entities=[
            entity_metric(
                "Margaux",
                entity_type="product",
                score=5.0,
                current_mentions=5,
                baseline_mentions=12,
            )
        ],
        baseline_entities=[
            entity_metric(
                "Margaux",
                entity_type="product",
                score=2.0,
                current_mentions=2,
                baseline_mentions=9,
            )
        ],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    delta = comparison.deltas[0]
    assert delta.current_mentions == 5
    assert delta.baseline_mentions == 2
    assert delta.mention_delta == 3
    assert delta.current_internal_baseline_mentions == 12
    assert delta.baseline_internal_baseline_mentions == 9


def test_compare_trends_uses_alias_key_normalization() -> None:
    comparison = compare_trends(
        current_entities=[entity_metric("The Row", score=3.0, current_mentions=3)],
        baseline_entities=[entity_metric("the-row", score=1.0, current_mentions=1)],
        current_candidates=[candidate_metric("Mary-Jane flats", score=3.0, current_mentions=3)],
        baseline_candidates=[candidate_metric("mary jane flats", score=1.0, current_mentions=1)],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert [delta.name for delta in comparison.deltas] == ["Mary-Jane flats", "The Row"]
    assert {delta.status for delta in comparison.deltas} == {TrendStatus.RISING}


def test_compare_trends_sorts_same_name_signals_deterministically() -> None:
    comparison = compare_trends(
        current_entities=[
            entity_metric("Mary Jane", entity_type="product", score=2.0, current_mentions=2),
            entity_metric("Mary Jane", entity_type="trend", score=2.0, current_mentions=2),
        ],
        baseline_entities=[
            entity_metric("Mary Jane", entity_type="product", score=1.0, current_mentions=1),
            entity_metric("Mary Jane", entity_type="trend", score=1.0, current_mentions=1),
        ],
        current_candidates=[candidate_metric("Mary Jane", score=2.0, current_mentions=2)],
        baseline_candidates=[candidate_metric("Mary Jane", score=1.0, current_mentions=1)],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
    )

    assert [(delta.signal_kind, delta.signal_type, delta.name) for delta in comparison.deltas] == [
        (TrendSignalKind.CANDIDATE, "brand", "Mary Jane"),
        (TrendSignalKind.ENTITY, "product", "Mary Jane"),
        (TrendSignalKind.ENTITY, "trend", "Mary Jane"),
    ]


def test_compare_trends_applies_limit_after_comparison() -> None:
    comparison = compare_trends(
        current_entities=[
            entity_metric("New Low", score=1.0, current_mentions=1),
            entity_metric("Rising High", score=10.0, current_mentions=10),
        ],
        baseline_entities=[entity_metric("Rising High", score=1.0, current_mentions=1)],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
        limit=1,
    )

    assert [delta.name for delta in comparison.deltas] == ["New Low"]


def test_compare_trends_limit_zero_returns_metadata_without_deltas() -> None:
    comparison = compare_trends(
        current_entities=[entity_metric("The Row")],
        baseline_entities=[],
        current_candidates=[],
        baseline_candidates=[],
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
        limit=0,
    )

    assert comparison == TrendComparison(as_of=AS_OF, baseline_as_of=BASELINE_AS_OF, deltas=[])


def test_build_trend_comparison_calls_snapshot_engines_twice_with_uncapped_discovery(
    monkeypatch,
) -> None:
    entity_current = [entity_metric("Current Entity")]
    entity_baseline = [entity_metric("Baseline Entity")]
    candidate_current = [candidate_metric("current candidate")]
    candidate_baseline = [candidate_metric("baseline candidate")]
    score_calls = []
    candidate_calls = []
    captured_compare_kwargs = {}

    def fake_score_entities(engine, *, scoring, as_of):
        score_calls.append((engine, scoring, as_of))
        return entity_current if as_of == AS_OF else entity_baseline

    def fake_discover_candidates(engine, *, scoring, settings, entity_config, as_of, **kwargs):
        candidate_calls.append((engine, scoring, settings, entity_config, as_of, kwargs))
        return candidate_current if as_of == AS_OF else candidate_baseline

    def fake_compare_trends(**kwargs):
        captured_compare_kwargs.update(kwargs)
        return TrendComparison(
            as_of=kwargs["as_of"],
            baseline_as_of=kwargs["baseline_as_of"],
            deltas=[],
        )

    monkeypatch.setattr(trends_module, "score_entities", fake_score_entities)
    monkeypatch.setattr(trends_module, "discover_candidates", fake_discover_candidates)
    monkeypatch.setattr(trends_module, "compare_trends", fake_compare_trends)

    engine = object()
    scoring = ScoringSettings()
    candidate_discovery = CandidateDiscoverySettings(max_candidates=7)

    comparison = trends_module.build_trend_comparison(
        engine,
        scoring=scoring,
        candidate_discovery=candidate_discovery,
        entity_config=None,
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
        include_dropped=True,
        limit=3,
    )

    assert comparison == TrendComparison(as_of=AS_OF, baseline_as_of=BASELINE_AS_OF, deltas=[])
    assert [call[2] for call in score_calls] == [AS_OF, BASELINE_AS_OF]
    assert [call[4] for call in candidate_calls] == [AS_OF, BASELINE_AS_OF]
    assert all("limit" not in call[5] for call in candidate_calls)
    assert all(call[2] is not candidate_discovery for call in candidate_calls)
    assert all(
        call[2].max_candidates > candidate_discovery.max_candidates for call in candidate_calls
    )
    assert all(call[2].enabled == candidate_discovery.enabled for call in candidate_calls)
    assert captured_compare_kwargs["current_entities"] == entity_current
    assert captured_compare_kwargs["baseline_entities"] == entity_baseline
    assert captured_compare_kwargs["current_candidates"] == candidate_current
    assert captured_compare_kwargs["baseline_candidates"] == candidate_baseline
    assert captured_compare_kwargs["include_dropped"] is True
    assert captured_compare_kwargs["limit"] == 3


def test_build_trend_comparison_compares_candidates_beyond_configured_max(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    for index, source_name in enumerate(("Source A", "Source B", "Source C"), start=1):
        store_observed_item(
            engine,
            title="Fading bag baseline mention",
            url=f"https://example.com/fading-baseline-{index}",
            source_name=source_name,
            collected_at=BASELINE_AS_OF - timedelta(hours=index),
        )
        store_observed_item(
            engine,
            title="Bright bag current mention",
            url=f"https://example.com/bright-current-{index}",
            source_name=source_name,
            collected_at=AS_OF - timedelta(hours=index),
        )
    store_observed_item(
        engine,
        title="Fading bag current mention",
        url="https://example.com/fading-current",
        source_name="Source A",
        collected_at=AS_OF - timedelta(hours=6),
    )

    comparison = trends_module.build_trend_comparison(
        engine,
        scoring=ScoringSettings(current_window_days=7, baseline_window_days=30),
        candidate_discovery=CandidateDiscoverySettings(
            max_candidates=1,
            min_current_mentions=1,
            review_min_current_mentions=1,
            min_single_token_mentions=99,
            min_single_token_distinct_sources=99,
        ),
        entity_config=None,
        as_of=AS_OF,
        baseline_as_of=BASELINE_AS_OF,
        include_dropped=True,
    )

    by_key = {delta.comparison_key: delta for delta in comparison.deltas}
    fading = by_key["candidate:bag:fading bag"]
    bright = by_key["candidate:bag:bright bag"]
    assert fading.status == TrendStatus.COOLING
    assert fading.current_mentions == 1
    assert fading.baseline_mentions == 3
    assert bright.status == TrendStatus.NEW


def test_create_readonly_sqlite_engine_rejects_writes(tmp_path) -> None:
    db_path = tmp_path / "fashion.db"
    writable_engine = create_sqlite_engine(db_path)
    initialize_schema(writable_engine)
    writable_engine.dispose()

    readonly_engine = trends_module.create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(OperationalError):
            with readonly_engine.begin() as connection:
                connection.execute(text("create table trend_write_probe (id integer)"))
    finally:
        readonly_engine.dispose()
