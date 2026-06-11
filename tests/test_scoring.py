from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.scoring import score_entities
from fashion_radar.settings import ScoringSettings

AS_OF = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)


def _store_item(
    engine,
    *,
    url: str,
    entity_name: str,
    entity_type: str = "brand",
    source_name: str = "Vogue Business",
    source_weight: float = 1.0,
    collected_at: datetime,
    published_at: datetime | None = None,
    matches: list[tuple[str, float]] | None = None,
) -> int:
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=SourceType.RSS,
            url=url,
            title=f"{entity_name} fashion signal",
            published_at=published_at or collected_at,
            summary=f"Short attributed summary for {entity_name}.",
        ),
        source_weight=source_weight,
        collected_at=collected_at,
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": entity_name,
                "entity_type": entity_type,
                "alias": alias,
                "confidence": confidence,
                "reason": "context",
                "context_terms": ["fashion"],
            }
            for alias, confidence in (matches or [(entity_name, 1.0)])
        ],
    )
    return item_id


def test_score_entities_counts_distinct_item_mentions_and_weights_max_confidence(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/the-row",
        entity_name="The Row",
        source_weight=2.0,
        collected_at=AS_OF - timedelta(hours=1),
        matches=[("The Row", 0.6), ("row", 0.8)],
    )
    _store_item(
        engine,
        url="https://example.com/miu-miu",
        entity_name="Miu Miu",
        source_weight=5.0,
        collected_at=AS_OF - timedelta(hours=2),
        matches=[("Miu Miu", 0.49)],
    )

    metrics = score_entities(
        engine,
        scoring=ScoringSettings(
            min_match_confidence=0.5,
            high_weight_source_threshold=3.0,
        ),
        as_of=AS_OF,
    )

    assert [metric.entity_name for metric in metrics] == ["The Row"]
    metric = metrics[0]
    assert metric.current_mentions == 1
    assert metric.baseline_mentions == 0
    assert metric.weighted_mention_sum == pytest.approx(1.6)
    assert metric.distinct_sources == 1
    assert metric.heat_score == pytest.approx(1.6)
    assert metric.label == "new"


def test_score_entities_uses_collected_at_windows_not_published_at(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    current_start = AS_OF - timedelta(days=7)
    _store_item(
        engine,
        url="https://example.com/stale-published-current-collection",
        entity_name="Miu Miu",
        collected_at=AS_OF - timedelta(days=1),
        published_at=datetime(2024, 1, 1, tzinfo=UTC),
    )
    _store_item(
        engine,
        url="https://example.com/current-published-stale-collection",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(days=40),
        published_at=AS_OF - timedelta(days=1),
    )
    _store_item(
        engine,
        url="https://example.com/current-boundary-excluded",
        entity_name="Boundary Brand",
        collected_at=current_start,
    )
    _store_item(
        engine,
        url="https://example.com/current-boundary-included",
        entity_name="Inside Brand",
        collected_at=current_start + timedelta(seconds=1),
    )

    metrics = score_entities(engine, scoring=ScoringSettings(), as_of=AS_OF)

    assert [metric.entity_name for metric in metrics] == ["Inside Brand", "Miu Miu"]


def test_score_entities_computes_formula_components(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/rising-baseline",
        entity_name="Rising Brand",
        collected_at=AS_OF - timedelta(days=20),
    )
    _store_item(
        engine,
        url="https://example.com/rising-current-a",
        entity_name="Rising Brand",
        source_name="Vogue Business",
        source_weight=1.0,
        collected_at=AS_OF - timedelta(days=1),
        matches=[("Rising Brand", 1.0)],
    )
    _store_item(
        engine,
        url="https://example.com/rising-current-b",
        entity_name="Rising Brand",
        source_name="Business of Fashion",
        source_weight=2.0,
        collected_at=AS_OF - timedelta(hours=1),
        matches=[("Rising", 0.5)],
    )
    scoring = ScoringSettings(
        weighted_mentions_7d=2.0,
        growth_bonus=3.0,
        source_diversity_bonus=1.25,
        high_weight_source_bonus=0.5,
        high_weight_source_threshold=1.5,
        hot_score_threshold=100.0,
    )

    metric = score_entities(engine, scoring=scoring, as_of=AS_OF)[0]

    expected_growth_ratio = (2 / 7) / (1 / 30)
    expected_heat_score = 2.0 * 2.0 + (expected_growth_ratio - 1) * 3.0 + (2 - 1) * 1.25 + 0.5
    assert metric.current_mentions == 2
    assert metric.baseline_mentions == 1
    assert metric.weighted_mention_sum == pytest.approx(2.0)
    assert metric.growth_ratio == pytest.approx(expected_growth_ratio)
    assert metric.source_diversity_component == pytest.approx(1.25)
    assert metric.high_weight_component == pytest.approx(0.5)
    assert metric.heat_score == pytest.approx(expected_heat_score)
    assert metric.label == "rising"


def test_score_entities_assigns_labels_and_ranks_deterministically(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/new-brand",
        entity_name="New Brand",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        engine,
        url="https://example.com/hot-baseline",
        entity_name="Hot Brand",
        collected_at=AS_OF - timedelta(days=20),
    )
    _store_item(
        engine,
        url="https://example.com/hot-current-a",
        entity_name="Hot Brand",
        source_name="Vogue Business",
        source_weight=2.0,
        collected_at=AS_OF - timedelta(days=1),
    )
    _store_item(
        engine,
        url="https://example.com/hot-current-b",
        entity_name="Hot Brand",
        source_name="Elle",
        source_weight=2.0,
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        engine,
        url="https://example.com/rising-baseline",
        entity_name="Rising Brand",
        collected_at=AS_OF - timedelta(days=20),
    )
    _store_item(
        engine,
        url="https://example.com/rising-current-a",
        entity_name="Rising Brand",
        source_name="Single Source",
        collected_at=AS_OF - timedelta(days=1),
    )
    _store_item(
        engine,
        url="https://example.com/rising-current-b",
        entity_name="Rising Brand",
        source_name="Single Source",
        collected_at=AS_OF - timedelta(hours=1),
    )
    for index in range(10):
        _store_item(
            engine,
            url=f"https://example.com/cooling-baseline-{index}",
            entity_name="Cooling Brand",
            collected_at=AS_OF - timedelta(days=10 + index),
        )
    _store_item(
        engine,
        url="https://example.com/cooling-current",
        entity_name="Cooling Brand",
        collected_at=AS_OF - timedelta(hours=3),
    )
    _store_item(
        engine,
        url="https://example.com/stable-baseline",
        entity_name="Stable Brand",
        collected_at=AS_OF - timedelta(days=20),
    )
    _store_item(
        engine,
        url="https://example.com/stable-current",
        entity_name="Stable Brand",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store_item(
        engine,
        url="https://example.com/aaa-tie",
        entity_name="Aaa Tie",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store_item(
        engine,
        url="https://example.com/zzz-tie",
        entity_name="Zzz Tie",
        collected_at=AS_OF - timedelta(hours=2),
    )

    metrics = score_entities(engine, scoring=ScoringSettings(), as_of=AS_OF)

    labels = {metric.entity_name: metric.label for metric in metrics}
    assert labels["New Brand"] == "new"
    assert labels["Hot Brand"] == "hot"
    assert labels["Rising Brand"] == "rising"
    assert labels["Cooling Brand"] == "cooling"
    assert labels["Stable Brand"] == "stable"
    assert metrics[0].entity_name == "Hot Brand"
    tie_names = [
        metric.entity_name for metric in metrics if metric.entity_name in {"Aaa Tie", "Zzz Tie"}
    ]
    assert tie_names == ["Aaa Tie", "Zzz Tie"]
