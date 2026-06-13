from datetime import UTC, datetime, timedelta

import pytest

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.discovery.candidates import (
    candidate_key,
    discover_candidates,
    stored_entity_candidate_keys,
)
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.settings import (
    CandidateDiscoverySettings,
    EntityConfig,
    ScoringSettings,
)

AS_OF = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)


def _store(
    engine,
    *,
    title: str,
    url: str,
    source_name: str = "Fashionista",
    source_type: SourceType = SourceType.RSS,
    source_weight: float = 1.0,
    collected_at=None,
    summary: str = "",
) -> int:
    return ItemRepository(engine).upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=collected_at or AS_OF,
            summary=summary,
        ),
        source_weight=source_weight,
        collected_at=collected_at or AS_OF,
    )


def test_discovers_new_candidate_from_current_window(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Le Teckel bag gains momentum",
        url="https://example.com/a",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Le Teckel bag appears again",
        url="https://example.com/b",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "le teckel bag")
    assert candidate.label == "new_candidate"
    assert candidate.current_mentions == 2
    assert candidate.baseline_mentions == 0
    assert candidate.distinct_sources == 2
    assert candidate.representative_items[0].title == "Le Teckel bag gains momentum"


def test_labels_rising_candidate_when_baseline_exists_and_growth_threshold_is_met(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Pierced mule appears earlier",
        url="https://example.com/baseline",
        collected_at=AS_OF - timedelta(days=10),
    )
    _store(
        engine,
        title="Pierced mule gains momentum",
        url="https://example.com/current-a",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Pierced mule appears again",
        url="https://example.com/current-b",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(current_window_days=7, baseline_window_days=30),
        settings=CandidateDiscoverySettings(rising_growth_ratio=2.0),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "pierced mule")
    assert candidate.label == "rising_candidate"
    assert candidate.baseline_mentions == 1
    assert candidate.current_mentions == 2
    assert candidate.growth_ratio == pytest.approx((2 / 7) / (1 / 30))


def test_labels_review_when_candidate_meets_review_floor_but_not_new_or_rising(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Slim sneaker appears earlier",
        url="https://example.com/baseline-a",
        collected_at=AS_OF - timedelta(days=10),
    )
    _store(
        engine,
        title="Slim sneaker appears earlier again",
        url="https://example.com/baseline-b",
        collected_at=AS_OF - timedelta(days=11),
    )
    _store(
        engine,
        title="Slim sneaker current mention",
        url="https://example.com/current-a",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Slim sneaker current mention again",
        url="https://example.com/current-b",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(current_window_days=7, baseline_window_days=30),
        settings=CandidateDiscoverySettings(rising_growth_ratio=10.0),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "slim sneaker")
    assert candidate.label == "review"
    assert candidate.current_mentions == 2
    assert candidate.distinct_sources == 2


def test_excludes_configured_and_stored_entities(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    item_id = _store(
        engine,
        title="The Row Margaux bag gains momentum",
        url="https://example.com/row",
        collected_at=AS_OF - timedelta(hours=1),
    )
    ItemRepository(engine).replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    entity_config = EntityConfig(
        entities=[
            EntityDefinition(
                name="Margaux",
                type=EntityType.PRODUCT,
                aliases=[{"value": "Margaux"}],
                context_terms=["bag"],
            )
        ]
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(min_current_mentions=1),
        entity_config=entity_config,
        as_of=AS_OF,
    )

    keys = {candidate.normalized_key for candidate in candidates}
    assert "the row" not in keys
    assert "margaux" not in keys
    assert "the row margaux bag" not in keys
    assert "margaux bag" not in keys


def test_discover_candidates_filters_source_type_and_source_name(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Le Teckel bag appears in imported row",
        url="https://example.com/imported-a",
        source_name="Community Tool Export",
        source_type=SourceType.MANUAL_IMPORT,
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Le Teckel bag appears in another imported row",
        url="https://example.com/imported-b",
        source_name="Manual Export",
        source_type=SourceType.MANUAL_IMPORT,
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store(
        engine,
        title="Le Teckel bag appears in RSS row",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=3),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        source_type=SourceType.MANUAL_IMPORT,
        source_name="Community Tool Export",
    )

    candidate = next(item for item in candidates if item.normalized_key == "le teckel bag")
    assert candidate.current_mentions == 1
    assert candidate.distinct_sources == 1
    assert [item.source_name for item in candidate.representative_items] == [
        "Community Tool Export"
    ]


def test_discover_candidates_default_keeps_all_source_types(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Slim sneaker current imported mention",
        url="https://example.com/imported",
        source_name="Community Tool Export",
        source_type=SourceType.MANUAL_IMPORT,
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Slim sneaker current RSS mention",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=2),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "slim sneaker")
    assert candidate.current_mentions == 2
    assert candidate.distinct_sources == 2


def test_candidate_key_uses_candidate_discovery_normalization() -> None:
    assert candidate_key("Le Teckel's Bag") == "le teckel bag"


def test_stored_entity_candidate_keys_matches_existing_confidence_and_as_of_rules(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    accepted_id = _store(
        engine,
        title="Ghost mule current mention",
        url="https://example.com/accepted",
        collected_at=AS_OF - timedelta(hours=1),
    )
    future_id = _store(
        engine,
        title="Future bag current mention",
        url="https://example.com/future",
        collected_at=AS_OF + timedelta(days=1),
    )
    repository.replace_item_matches(
        accepted_id,
        [
            {
                "entity_name": "Ghost",
                "entity_type": "product",
                "alias": "Ghost",
                "confidence": 0.8,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    repository.replace_item_matches(
        future_id,
        [
            {
                "entity_name": "Future",
                "entity_type": "product",
                "alias": "Future",
                "confidence": 0.9,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    keys = stored_entity_candidate_keys(
        engine,
        min_match_confidence=0.5,
        as_of=AS_OF,
    )

    assert "ghost" in keys
    assert "future" not in keys


def test_stored_entity_filter_uses_min_match_confidence(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = _store(
        engine,
        title="Ghost bag gains momentum",
        url="https://example.com/ghost",
        collected_at=AS_OF - timedelta(hours=1),
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "Ghost",
                "entity_type": "product",
                "alias": "Ghost",
                "confidence": 0.2,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    low_confidence_candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(min_match_confidence=0.5),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )

    assert "ghost bag" in {candidate.normalized_key for candidate in low_confidence_candidates}

    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "Ghost",
                "entity_type": "product",
                "alias": "Ghost",
                "confidence": 0.8,
                "reason": "manual_review_sentinel_not_accepted",
                "context_terms": [],
            }
        ],
    )
    high_confidence_candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(min_match_confidence=0.5),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )

    assert "ghost bag" not in {candidate.normalized_key for candidate in high_confidence_candidates}


def test_future_stored_entity_match_does_not_filter_historical_candidate(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store(
        engine,
        title="Ghost bag gains momentum",
        url="https://example.com/current-ghost",
        collected_at=AS_OF - timedelta(hours=1),
    )
    future_item_id = _store(
        engine,
        title="Ghost appears later",
        url="https://example.com/future-ghost",
        collected_at=AS_OF + timedelta(days=1),
    )
    repository.replace_item_matches(
        future_item_id,
        [
            {
                "entity_name": "Ghost",
                "entity_type": "product",
                "alias": "Ghost",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(min_match_confidence=0.5),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )

    assert "ghost bag" in {candidate.normalized_key for candidate in candidates}


def test_uses_collected_at_windows_and_ignores_future_items(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Pierced mule demand grows",
        url="https://example.com/current",
        collected_at=AS_OF - timedelta(days=1),
    )
    _store(
        engine,
        title="Pierced mule earlier signal",
        url="https://example.com/baseline",
        collected_at=AS_OF - timedelta(days=10),
    )
    _store(
        engine,
        title="Pierced mule future signal",
        url="https://example.com/future",
        collected_at=AS_OF + timedelta(days=1),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(current_window_days=7, baseline_window_days=30),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "pierced mule")
    assert candidate.current_mentions == 1
    assert candidate.baseline_mentions == 1
    assert candidate.growth_ratio == pytest.approx((1 / 7) / (1 / 30))


def test_candidate_discovery_settings_control_output(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Khaite boot gains attention",
        url="https://example.com/a",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Khaite boot appears again",
        url="https://example.com/b",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
    )

    disabled = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(enabled=False),
        entity_config=None,
        as_of=AS_OF,
    )
    limited = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(max_candidates=1, representative_items_per_candidate=1),
        entity_config=None,
        as_of=AS_OF,
    )

    assert disabled == []
    assert len(limited) == 1
    assert len(limited[0].representative_items) == 1


def test_single_token_candidates_require_aggregate_thresholds(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Tabis return",
        url="https://example.com/tabis-a",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Tabis appear again",
        url="https://example.com/tabis-b",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store(
        engine,
        title="Skort returns",
        url="https://example.com/skort",
        source_name="Elle",
        collected_at=AS_OF - timedelta(hours=3),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    keys = {candidate.normalized_key for candidate in candidates}
    assert "tabis" in keys
    assert "skort" not in keys
