from datetime import UTC, datetime, timedelta
from pathlib import Path

import fashion_radar.imported_candidate_evidence as imported_candidate_evidence_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_candidate_evidence import (
    ImportedCandidateEvidenceReview,
    ImportedCandidateEvidenceRow,
    query_imported_candidate_evidence,
    render_imported_candidate_evidence_table,
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


def test_query_imported_candidate_evidence_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )

    assert result.database == str(db_path)
    assert result.phrase == "Le Teckel bag"
    assert result.source_type == "manual_import"
    assert result.row_count == 0
    assert result.total_count == 0
    assert result.evidence == []
    assert not db_path.parent.exists()


def test_query_imported_candidate_evidence_filters_manual_rows_source_and_windows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/current",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    baseline_id = _store_item(
        repository,
        title="Le Teckel bag baseline mention",
        url="https://example.com/baseline",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=10),
    )
    _store_item(
        repository,
        title="Le Teckel bag other manual mention",
        url="https://example.com/manual",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store_item(
        repository,
        title="Le Teckel bag RSS mention",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=3),
    )
    _store_item(
        repository,
        title="Le Teckel bag future mention",
        url="https://example.com/future",
        source_name="Community Tool Export",
        collected_at=AS_OF + timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag old out-of-window mention",
        url="https://example.com/old",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=60),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
        source_name="Community Tool Export",
    )

    assert result.total_count == 2
    assert result.row_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.distinct_sources == 1
    assert [row.id for row in result.evidence] == [current_id, baseline_id]
    assert [row.window for row in result.evidence] == ["current", "baseline"]


def test_query_imported_candidate_evidence_blank_source_name_is_no_filter(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag community mention",
        url="https://example.com/community",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag manual mention",
        url="https://example.com/manual",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
        source_name="   ",
    )

    assert result.source_name is None
    assert result.total_count == 2
    assert result.current_mentions == 2


def test_query_imported_candidate_evidence_limit_zero_preserves_counts(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/current",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag baseline mention",
        url="https://example.com/baseline",
        collected_at=AS_OF - timedelta(days=10),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
        limit=0,
    )

    assert result.row_count == 0
    assert result.total_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.evidence == []


def test_query_imported_candidate_evidence_uses_candidate_extraction_not_substring(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Teckel shaped clasp appears",
        url="https://example.com/noise",
        collected_at=AS_OF - timedelta(hours=1),
    )
    expected_id = _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/match",
        collected_at=AS_OF - timedelta(hours=2),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )

    assert [row.id for row in result.evidence] == [expected_id]


def test_query_imported_candidate_evidence_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()
    calls: list[Path] = []
    original = imported_candidate_evidence_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_candidate_evidence_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )

    assert calls == [db_path]


def test_query_imported_candidate_evidence_suppresses_known_entities(
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
    for phrase in ("Margaux bag", "Ghost mule"):
        result = query_imported_candidate_evidence(
            db_path,
            scoring=ScoringSettings(),
            settings=CandidateDiscoverySettings(
                min_current_mentions=1,
                review_min_current_mentions=1,
            ),
            entity_config=entity_config,
            as_of=AS_OF,
            phrase=phrase,
        )
        assert result.evidence == []


def test_imported_candidate_evidence_json_shape_omits_summary_and_match_fields(
    tmp_path: Path,
) -> None:
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

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )
    payload = result.model_dump(mode="json")

    assert list(payload) == [
        "database",
        "as_of",
        "phrase",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "evidence",
    ]
    assert list(payload["evidence"][0]) == [
        "id",
        "window",
        "source_name",
        "title",
        "url",
        "published_at",
        "collected_at",
    ]
    forbidden = {
        "summary",
        "contexts",
        "normalized_phrase",
        "normalized_key",
        "normalized_url",
        "matches",
        "match_status",
        "source_file",
        "source_path",
        "import_path",
        "raw_comment",
        "account_id",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(payload["evidence"][0])


def test_render_imported_candidate_evidence_table_sanitizes_display_cells() -> None:
    review = ImportedCandidateEvidenceReview(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        phrase="Le Teckel | bag",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-07T12:00:00+00:00",
        row_count=1,
        total_count=1,
        current_mentions=1,
        baseline_mentions=0,
        distinct_sources=1,
        evidence=[
            ImportedCandidateEvidenceRow(
                id=7,
                window="current",
                source_name="Community | Export",
                title="Le Teckel\nbag",
                url="https://example.com/a|b",
                published_at="2026-06-13T10:00:00+00:00",
                collected_at="2026-06-13T11:00:00+00:00",
            )
        ],
    )

    lines = render_imported_candidate_evidence_table(review)

    assert "Phrase: Le Teckel / bag" in lines
    assert (
        "current | 7 | 2026-06-13T11:00:00+00:00 | Community / Export | "
        "Le Teckel bag | https://example.com/a/b"
    ) in lines
