from datetime import UTC, datetime, timedelta
from pathlib import Path

import fashion_radar.imported_candidates as imported_candidates_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_candidates import (
    ImportedCandidatesReview,
    query_imported_candidates,
    render_imported_candidates_table,
)
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings

AS_OF = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)


def _store_item(
    repository: ItemRepository,
    *,
    title: str,
    url: str,
    source_name: str = "Community Tool Export",
    source_type: SourceType = SourceType.MANUAL_IMPORT,
    collected_at: datetime | None = None,
    summary: str = "",
) -> int:
    collected = collected_at or AS_OF
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=collected,
            summary=summary,
        ),
        collected_at=collected,
    )


def test_query_imported_candidates_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    assert result.database == str(db_path)
    assert result.as_of == "2026-06-13T12:00:00+00:00"
    assert result.source_type == "manual_import"
    assert result.source_name is None
    assert result.limit == 50
    assert result.candidate_count == 0
    assert result.candidates == []
    assert not db_path.parent.exists()


def test_query_imported_candidates_filters_manual_rows_and_source_name(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/imported-a",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag current manual mention",
        url="https://example.com/imported-b",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store_item(
        repository,
        title="Le Teckel bag current RSS mention",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=3),
    )
    engine.dispose()

    result = query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        source_name="Community Tool Export",
    )

    assert result.candidate_count == 1
    candidate = result.candidates[0]
    assert candidate.phrase == "Le Teckel bag"
    assert candidate.current_mentions == 1
    assert candidate.distinct_sources == 1
    assert not hasattr(candidate, "representative_items")


def test_query_imported_candidates_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()
    calls: list[Path] = []
    original = imported_candidates_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_candidates_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    assert calls == [db_path]


def test_query_imported_candidates_suppresses_configured_and_stored_entities(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Margaux bag current mention",
        url="https://example.com/configured",
        collected_at=AS_OF - timedelta(hours=1),
    )
    stored_id = _store_item(
        repository,
        title="Ghost mule current mention",
        url="https://example.com/stored",
        collected_at=AS_OF - timedelta(hours=2),
    )
    repository.replace_item_matches(
        stored_id,
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
    engine.dispose()

    result = query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=EntityConfig(
            entities=[
                EntityDefinition(
                    name="Margaux",
                    type=EntityType.PRODUCT,
                    aliases=[{"value": "Margaux"}],
                    context_terms=["bag"],
                )
            ]
        ),
        as_of=AS_OF,
    )

    phrases = {candidate.phrase for candidate in result.candidates}
    assert "Margaux bag" not in phrases
    assert "Ghost mule" not in phrases


def test_imported_candidates_json_shape_omits_item_and_match_fields(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://private.example.com/local-path",
        collected_at=AS_OF - timedelta(hours=1),
        summary="raw private review note",
    )
    engine.dispose()

    result = query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )
    payload = result.model_dump(mode="json")

    assert list(payload) == [
        "database",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "candidate_count",
        "candidates",
    ]
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]
    forbidden = {
        "representative_items",
        "source_url",
        "title",
        "summary",
        "contexts",
        "normalized_key",
        "item_id",
        "matches",
        "match_status",
    }
    assert forbidden.isdisjoint(payload["candidates"][0])


def test_render_imported_candidates_table_sanitizes_display_cells() -> None:
    review = ImportedCandidatesReview(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-07T12:00:00+00:00",
        source_name="Community | Export",
    )

    assert render_imported_candidates_table(review) == [
        "Imported manual candidate signals from local SQLite.",
        "Candidate signals are observed phrases from retained manual_import rows and need review.",
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Baseline window: 2026-05-07T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00",
        "Source name: Community / Export",
        "Candidates: 0",
        "No imported manual candidate signals found.",
    ]
