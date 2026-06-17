from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import fashion_radar.imported_entity_evidence as imported_entity_evidence_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_entity_evidence import (
    ImportedEntityEvidenceReview,
    ImportedEntityEvidenceRow,
    query_imported_entity_evidence,
    render_imported_entity_evidence_table,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType

AS_OF = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)


def test_query_imported_entity_evidence_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert result.database == str(db_path)
    assert result.as_of == "2026-06-13T12:00:00+00:00"
    assert result.entity_name == "The Row"
    assert result.entity_type == "brand"
    assert result.current_window_start == "2026-06-06T12:00:00+00:00"
    assert result.baseline_window_start == "2026-05-30T12:00:00+00:00"
    assert result.current_days == 7
    assert result.baseline_days == 7
    assert result.source_type == "manual_import"
    assert result.source_name is None
    assert result.limit == 20
    assert result.row_count == 0
    assert result.total_count == 0
    assert result.current_mentions == 0
    assert result.baseline_mentions == 0
    assert result.distinct_sources == 0
    assert result.evidence == []
    assert not db_path.parent.exists()


def test_query_imported_entity_evidence_filters_manual_rows_entity_source_and_windows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_item(
        repository,
        title="The Row current mention",
        url="https://example.com/current",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    baseline_id = _store_item(
        repository,
        title="The Row baseline mention",
        url="https://example.com/baseline",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=10),
    )
    other_source_id = _store_item(
        repository,
        title="The Row other manual mention",
        url="https://example.com/manual",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    other_entity_id = _store_item(
        repository,
        title="Alaia mention",
        url="https://example.com/alaia",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=3),
    )
    product_id = _store_item(
        repository,
        title="The Row product mention",
        url="https://example.com/product",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=4),
    )
    rss_id = _store_item(
        repository,
        title="The Row RSS mention",
        url="https://example.com/rss",
        source_name="RSS Source",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=5),
    )
    future_id = _store_item(
        repository,
        title="The Row future mention",
        url="https://example.com/future",
        source_name="Community Tool Export",
        collected_at=AS_OF + timedelta(hours=1),
    )
    old_id = _store_item(
        repository,
        title="The Row old mention",
        url="https://example.com/old",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=30),
    )
    repository.replace_item_matches(current_id, [_match("The Row", "brand")])
    repository.replace_item_matches(baseline_id, [_match("The Row", "brand")])
    repository.replace_item_matches(other_source_id, [_match("The Row", "brand")])
    repository.replace_item_matches(other_entity_id, [_match("Alaia", "brand")])
    repository.replace_item_matches(product_id, [_match("The Row", "product")])
    repository.replace_item_matches(rss_id, [_match("The Row", "brand")])
    repository.replace_item_matches(future_id, [_match("The Row", "brand")])
    repository.replace_item_matches(old_id, [_match("The Row", "brand")])
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        source_name="Community Tool Export",
    )

    assert result.source_name == "Community Tool Export"
    assert result.total_count == 2
    assert result.row_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.distinct_sources == 1
    assert [row.id for row in result.evidence] == [current_id, baseline_id]
    assert [row.window for row in result.evidence] == ["current", "baseline"]


def test_query_imported_entity_evidence_blank_source_name_is_no_filter(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_id = _store_matched_item(
        repository,
        "The Row",
        source_name="Community Tool Export",
        url="https://example.com/community",
        collected_at=AS_OF - timedelta(hours=1),
    )
    second_id = _store_matched_item(
        repository,
        "The Row",
        source_name="Manual Export",
        url="https://example.com/manual",
        collected_at=AS_OF - timedelta(hours=2),
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        source_name="   ",
    )

    assert result.source_name is None
    assert result.total_count == 2
    assert result.current_mentions == 2
    assert [row.id for row in result.evidence] == [first_id, second_id]


def test_query_imported_entity_evidence_deduplicates_duplicate_entity_matches(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = _store_item(
        repository,
        title="The Row duplicate stored match",
        url="https://example.com/duplicate",
        collected_at=AS_OF - timedelta(hours=1),
    )
    repository.replace_item_matches(
        item_id,
        [
            _match("The Row", "brand"),
            _match("The Row", "brand", alias="The Row duplicate"),
        ],
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert result.total_count == 1
    assert result.current_mentions == 1
    assert [row.id for row in result.evidence] == [item_id]


def test_query_imported_entity_evidence_classifies_window_boundaries(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/baseline-start",
        collected_at=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
    )
    current_start_id = _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/current-start",
        collected_at=datetime(2026, 6, 6, 12, 0, tzinfo=UTC),
    )
    as_of_id = _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/as-of",
        collected_at=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
    )
    _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/future",
        collected_at=datetime(2026, 6, 13, 12, 1, tzinfo=UTC),
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert result.total_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert [(row.id, row.window) for row in result.evidence] == [
        (as_of_id, "current"),
        (current_start_id, "baseline"),
    ]


def test_query_imported_entity_evidence_limit_zero_preserves_counts(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/current",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/baseline",
        collected_at=AS_OF - timedelta(days=10),
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        limit=0,
    )

    assert result.row_count == 0
    assert result.total_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.evidence == []


def test_query_imported_entity_evidence_limit_applies_after_sorting(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    older_current_id = _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/older-current",
        collected_at=AS_OF - timedelta(hours=1),
    )
    newest_id = _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/newest",
        collected_at=AS_OF - timedelta(minutes=5),
    )
    _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/baseline",
        collected_at=AS_OF - timedelta(days=10),
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        limit=1,
    )

    assert result.row_count == 1
    assert result.total_count == 3
    assert result.current_mentions == 2
    assert result.baseline_mentions == 1
    assert older_current_id < newest_id
    assert [row.id for row in result.evidence] == [newest_id]


def test_query_imported_entity_evidence_sorts_same_timestamp_by_higher_id(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    collected_at = AS_OF - timedelta(hours=1)
    lower_id = _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/lower",
        collected_at=collected_at,
    )
    higher_id = _store_matched_item(
        repository,
        "The Row",
        url="https://example.com/higher",
        collected_at=collected_at,
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert higher_id > lower_id
    assert [row.id for row in result.evidence] == [higher_id, lower_id]


def test_query_imported_entity_evidence_rejects_invalid_options(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"

    with pytest.raises(ValueError, match="current_days must be at least 1"):
        query_imported_entity_evidence(
            db_path,
            as_of=AS_OF,
            entity_name="The Row",
            entity_type="brand",
            current_days=0,
        )
    with pytest.raises(ValueError, match="baseline_days must be at least 1"):
        query_imported_entity_evidence(
            db_path,
            as_of=AS_OF,
            entity_name="The Row",
            entity_type="brand",
            baseline_days=0,
        )
    with pytest.raises(ValueError, match="limit must be at least 0"):
        query_imported_entity_evidence(
            db_path,
            as_of=AS_OF,
            entity_name="The Row",
            entity_type="brand",
            limit=-1,
        )
    with pytest.raises(ValueError, match="entity name must not be blank"):
        query_imported_entity_evidence(
            db_path,
            as_of=AS_OF,
            entity_name=" ",
            entity_type="brand",
        )
    with pytest.raises(ValueError, match="entity type must not be blank"):
        query_imported_entity_evidence(
            db_path,
            as_of=AS_OF,
            entity_name="The Row",
            entity_type=" ",
        )


def test_query_imported_entity_evidence_uses_readonly_engine(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(repository, "The Row", collected_at=AS_OF - timedelta(hours=1))
    engine.dispose()
    observed = {}
    original = imported_entity_evidence_module.create_readonly_sqlite_engine

    def _spy(path: Path):
        observed["path"] = path
        return original(path)

    imported_entity_evidence_module.create_readonly_sqlite_engine = _spy
    try:
        query_imported_entity_evidence(
            db_path,
            as_of=AS_OF,
            entity_name="The Row",
            entity_type="brand",
        )
    finally:
        imported_entity_evidence_module.create_readonly_sqlite_engine = original

    assert observed["path"] == db_path


def test_imported_entity_evidence_json_shape_omits_match_and_raw_fields(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = _store_item(
        repository,
        title="The Row retained evidence title",
        url="https://example.com/private",
        summary="raw comment body and handle should not appear",
        collected_at=AS_OF - timedelta(hours=1),
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "Secret Alias",
                "confidence": 0.99,
                "reason": "keyword",
                "context_terms": ["private_context"],
            }
        ],
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    payload = result.model_dump()
    assert list(payload) == [
        "database",
        "as_of",
        "entity_name",
        "entity_type",
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
    serialized = result.model_dump_json()
    assert '"summary"' not in serialized
    for forbidden in (
        "raw comment body",
        "handle",
        "Secret Alias",
        "confidence",
        "reason",
        "context_terms",
        "private_context",
    ):
        assert forbidden not in serialized


def test_render_imported_entity_evidence_table_sanitizes_display_cells() -> None:
    review = ImportedEntityEvidenceReview(
        database="/tmp/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        entity_name="The | Row\nBrand",
        entity_type="brand | type",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
        source_name="Community | Tool\nExport",
        row_count=1,
        total_count=1,
        current_mentions=1,
        baseline_mentions=0,
        distinct_sources=1,
        evidence=[
            ImportedEntityEvidenceRow(
                id=7,
                window="current",
                source_name="Community | Tool\nExport",
                title="The Row | mention\nwith spaces",
                url="https://example.com/a|b\nc",
                published_at="2026-06-13T11:00:00+00:00",
                collected_at="2026-06-13T12:00:00+00:00",
            )
        ],
    )

    assert render_imported_entity_evidence_table(review) == [
        "Imported manual entity evidence from local SQLite.",
        (
            "Evidence rows are retained manual_import rows whose stored matched entity "
            "equals the requested entity."
        ),
        "Entity: The / Row Brand",
        "Entity type: brand / type",
        ("Baseline window: 2026-05-30T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00"),
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Source name: Community / Tool Export",
        "Rows: 1 shown, 1 total evidence rows",
        "Mentions: 1 current, 0 baseline",
        "Distinct current sources: 1",
        "Window | ID | Collected At | Source | Title | URL",
        (
            "current | 7 | 2026-06-13T12:00:00+00:00 | Community / Tool Export | "
            "The Row / mention with spaces | https://example.com/a/b c"
        ),
    ]


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


def _store_matched_item(
    repository: ItemRepository,
    entity_name: str,
    *,
    entity_type: str = "brand",
    source_name: str = "Community Tool Export",
    url: str = "https://example.com/item",
    collected_at: datetime | None = None,
) -> int:
    item_id = _store_item(
        repository,
        title=f"{entity_name} mention",
        url=url,
        source_name=source_name,
        collected_at=collected_at,
    )
    repository.replace_item_matches(item_id, [_match(entity_name, entity_type)])
    return item_id


def _match(entity_name: str, entity_type: str = "brand", *, alias: str | None = None):
    return {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "alias": alias or entity_name,
        "confidence": 1.0,
        "reason": "keyword",
        "context_terms": [],
    }
