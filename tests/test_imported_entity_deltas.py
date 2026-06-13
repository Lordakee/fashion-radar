from datetime import UTC, datetime
from pathlib import Path

import pytest

import fashion_radar.imported_entity_deltas as imported_entity_deltas_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_entity_deltas import (
    ImportedEntityDelta,
    ImportedEntityDeltas,
    query_imported_entity_deltas,
    render_imported_entity_deltas_table,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType

AS_OF = "2026-06-13T12:00:00Z"


def test_query_imported_entity_deltas_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_entity_deltas(db_path, as_of=AS_OF)

    assert result.database == str(db_path)
    assert result.as_of == "2026-06-13T12:00:00+00:00"
    assert result.current_window_start == "2026-06-06T12:00:00+00:00"
    assert result.baseline_window_start == "2026-05-30T12:00:00+00:00"
    assert result.current_days == 7
    assert result.baseline_days == 7
    assert result.entity_type is None
    assert result.source_name is None
    assert result.limit == 50
    assert result.row_count == 0
    assert result.total_count == 0
    assert result.current_matched_item_count == 0
    assert result.baseline_matched_item_count == 0
    assert result.entities == []
    assert not db_path.parent.exists()


def test_query_imported_entity_deltas_groups_entities_and_counts_item_level_windows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/current",
        title="The Row Margaux current",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    baseline_id = _store_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/baseline",
        title="The Row baseline",
        published_at=datetime(2026, 6, 3, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 3, 9, 0, tzinfo=UTC),
    )
    new_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/new",
        title="Alaia flats",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 9, 0, tzinfo=UTC),
    )
    rss_id = _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS Alaia",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        current_id,
        [_match("The Row", "brand"), _match("The Row", "brand", alias="The Row duplicate")],
    )
    repository.replace_item_matches(baseline_id, [_match("The Row", "brand")])
    repository.replace_item_matches(new_id, [_match("Alaia", "brand")])
    repository.replace_item_matches(rss_id, [_match("Alaia", "brand")])
    engine.dispose()

    result = query_imported_entity_deltas(db_path, as_of=AS_OF)

    assert result.total_count == 2
    assert result.row_count == 2
    assert result.current_matched_item_count == 2
    assert result.baseline_matched_item_count == 1
    assert [row.entity_name for row in result.entities] == ["Alaia", "The Row"]
    assert result.entities[0].change_label == "new_in_current"
    assert result.entities[0].current_count == 1
    assert result.entities[0].baseline_count == 0
    assert result.entities[0].delta == 1
    assert result.entities[0].current_source_count == 1
    assert result.entities[0].baseline_source_count == 0
    assert result.entities[0].source_count_delta == 1
    assert result.entities[1].current_count == 1
    assert result.entities[1].baseline_count == 1
    assert result.entities[1].delta == 0
    assert result.entities[1].change_label == "unchanged"
    assert result.entities[1].current_source_count == 1
    assert result.entities[1].baseline_source_count == 1
    assert result.entities[1].source_count_delta == 0


def test_query_imported_entity_deltas_labels_and_orders_all_change_states(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_entity_count(repository, "New Brand", current=1, baseline=0)
    _store_entity_count(repository, "Increased Brand", current=2, baseline=1)
    _store_entity_count(repository, "Dropped Brand", current=0, baseline=1)
    _store_entity_count(repository, "Decreased Brand", current=1, baseline=2)
    _store_entity_count(repository, "Unchanged Brand", current=1, baseline=1)
    engine.dispose()

    result = query_imported_entity_deltas(db_path, as_of=AS_OF)

    assert [row.change_label for row in result.entities] == [
        "new_in_current",
        "increased",
        "dropped_from_current",
        "decreased",
        "unchanged",
    ]
    assert [row.entity_name for row in result.entities] == [
        "New Brand",
        "Increased Brand",
        "Dropped Brand",
        "Decreased Brand",
        "Unchanged Brand",
    ]


def test_query_imported_entity_deltas_orders_ties_deterministically(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_entity_count(repository, "Increased Move 3", current=4, baseline=1)
    _store_entity_count(repository, "Increased Move 2", current=3, baseline=1)
    _store_entity_count(repository, "Increased Current Count", current=3, baseline=2)
    _store_entity_count(repository, "Product Tie", "product", current=2, baseline=1)
    _store_entity_count(repository, "Brand Tie B", current=2, baseline=1)
    _store_entity_count(repository, "Brand Tie A", current=2, baseline=1)
    engine.dispose()

    result = query_imported_entity_deltas(db_path, as_of=AS_OF)

    assert [(row.entity_type, row.entity_name) for row in result.entities] == [
        ("brand", "Increased Move 3"),
        ("brand", "Increased Move 2"),
        ("brand", "Increased Current Count"),
        ("brand", "Brand Tie A"),
        ("brand", "Brand Tie B"),
        ("product", "Product Tie"),
    ]


def test_query_imported_entity_deltas_classifies_window_boundaries_in_python(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(
        repository,
        "Baseline Start Brand",
        collected_at=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
    )
    _store_matched_item(
        repository,
        "Current Start Brand",
        collected_at=datetime(2026, 6, 6, 12, 0, tzinfo=UTC),
    )
    _store_matched_item(
        repository,
        "As Of Brand",
        collected_at=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
    )
    _store_matched_item(
        repository,
        "Future Brand",
        collected_at=datetime(2026, 6, 13, 12, 1, tzinfo=UTC),
    )
    engine.dispose()

    result = query_imported_entity_deltas(db_path, as_of=AS_OF)

    by_name = {row.entity_name: row for row in result.entities}
    assert "Baseline Start Brand" not in by_name
    assert by_name["Current Start Brand"].baseline_count == 1
    assert by_name["Current Start Brand"].current_count == 0
    assert by_name["As Of Brand"].current_count == 1
    assert "Future Brand" not in by_name


def test_query_imported_entity_deltas_counts_distinct_source_labels_by_window(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_a = _store_matched_item(
        repository,
        "Multi Source Brand",
        source_name="Community Tool Export",
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        current_a,
        [
            _match("Multi Source Brand", "brand"),
            _match("Multi Source Brand", "brand", alias="Duplicate"),
        ],
    )
    _store_matched_item(
        repository,
        "Multi Source Brand",
        source_name="Manual Export",
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
    )
    _store_matched_item(
        repository,
        "Multi Source Brand",
        source_name="Manual Export",
        collected_at=datetime(2026, 6, 3, 9, 0, tzinfo=UTC),
    )
    engine.dispose()

    result = query_imported_entity_deltas(db_path, as_of=AS_OF)

    row = next(row for row in result.entities if row.entity_name == "Multi Source Brand")
    assert row.current_count == 2
    assert row.current_source_count == 2
    assert row.baseline_source_count == 1
    assert row.source_count_delta == 1

    filtered = query_imported_entity_deltas(
        db_path,
        as_of=AS_OF,
        source_name="Community Tool Export",
    )
    filtered_row = next(row for row in filtered.entities if row.entity_name == "Multi Source Brand")
    assert filtered_row.current_source_count == 1
    assert filtered_row.baseline_source_count == 0
    assert filtered_row.source_count_delta == 1


def test_query_imported_entity_deltas_filters_source_type_and_limit_zero(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(repository, "First Brand", url_suffix="first")
    _store_matched_item(repository, "Second Brand", url_suffix="second")
    _store_matched_item(
        repository,
        "RSS Brand",
        source_type=SourceType.RSS,
        url_suffix="rss-second",
    )
    engine.dispose()

    result = query_imported_entity_deltas(db_path, as_of=AS_OF, limit=0)

    assert result.total_count == 2
    assert result.row_count == 0
    assert result.entities == []


def test_query_imported_entity_deltas_filters_entity_type_and_source_name(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(
        repository,
        "Margaux",
        "product",
        source_name="Community Tool Export",
        url_suffix="product",
    )
    _store_matched_item(
        repository,
        "The Row",
        "brand",
        source_name="Manual Export",
        url_suffix="brand",
    )
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of=AS_OF,
        entity_type="product",
        source_name="Community Tool Export",
    )

    assert result.total_count == 1
    assert result.current_matched_item_count == 1
    assert result.baseline_matched_item_count == 0
    assert [row.entity_name for row in result.entities] == ["Margaux"]
    assert result.entities[0].entity_type == "product"


def test_query_imported_entity_deltas_blank_filters_are_no_filter(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_matched_item(repository, "The Row")
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of=AS_OF,
        entity_type=" ",
        source_name=" ",
    )

    assert result.total_count == 1
    assert result.entity_type is None
    assert result.source_name is None


def test_query_imported_entity_deltas_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()
    calls: list[Path] = []
    original = imported_entity_deltas_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_entity_deltas_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_entity_deltas(db_path, as_of=AS_OF)

    assert calls == [db_path]


def test_query_imported_entity_deltas_rejects_invalid_options(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"

    with pytest.raises(ValueError, match="current_days must be at least 1"):
        query_imported_entity_deltas(db_path, as_of=AS_OF, current_days=0)
    with pytest.raises(ValueError, match="baseline_days must be at least 1"):
        query_imported_entity_deltas(db_path, as_of=AS_OF, baseline_days=0)
    with pytest.raises(ValueError, match="limit must be at least 0"):
        query_imported_entity_deltas(db_path, as_of=AS_OF, limit=-1)


def test_render_imported_entity_deltas_table_empty() -> None:
    result = ImportedEntityDeltas(
        database="missing.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
    )

    assert render_imported_entity_deltas_table(result) == [
        "Imported manual entity deltas from local SQLite.",
        "Baseline window: 2026-05-30T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00",
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Rows: 0 shown, 0 total entities",
        "Matched items: 0 current, 0 baseline",
        "No imported manual entity deltas found.",
    ]


def test_render_imported_entity_deltas_table_populated_sanitizes_cells() -> None:
    result = ImportedEntityDeltas(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
        row_count=1,
        total_count=1,
        current_matched_item_count=2,
        baseline_matched_item_count=1,
        entities=[
            ImportedEntityDelta(
                entity_name="Alaia | Flats\nSignal",
                entity_type="product\rtype",
                current_count=2,
                baseline_count=1,
                delta=1,
                change_label="increased",
                current_source_count=2,
                baseline_source_count=1,
                source_count_delta=1,
                first_collected_at="2026-06-03T09:00:00+00:00",
                latest_collected_at="2026-06-12T09:00:00+00:00",
            )
        ],
    )

    assert render_imported_entity_deltas_table(result) == [
        "Imported manual entity deltas from local SQLite.",
        "Baseline window: 2026-05-30T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00",
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Rows: 1 shown, 1 total entities",
        "Matched items: 2 current, 1 baseline",
        "Entity | Type | Current | Baseline | Delta | Change | Current Sources | "
        "Baseline Sources | Source Delta | First Collected At | Latest Collected At",
        "Alaia / Flats Signal | product type | 2 | 1 | 1 | increased | 2 | 1 | 1 | "
        "2026-06-03T09:00:00+00:00 | 2026-06-12T09:00:00+00:00",
    ]


def _store_item(
    repository: ItemRepository,
    *,
    source_name: str,
    url: str,
    title: str,
    published_at: datetime,
    collected_at: datetime,
    source_type: SourceType = SourceType.MANUAL_IMPORT,
) -> int:
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=published_at,
        ),
        source_weight=1.0,
        collected_at=collected_at,
    )


def _store_matched_item(
    repository: ItemRepository,
    entity_name: str,
    entity_type: str = "brand",
    *,
    source_name: str = "Manual Export",
    source_type: SourceType = SourceType.MANUAL_IMPORT,
    collected_at: datetime = datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    url_suffix: str | None = None,
) -> int:
    slug = (url_suffix or f"{entity_name}-{collected_at.isoformat()}").replace(" ", "-")
    item_id = _store_item(
        repository,
        source_name=source_name,
        source_type=source_type,
        url=f"https://example.com/{slug}",
        title=entity_name,
        published_at=collected_at,
        collected_at=collected_at,
    )
    repository.replace_item_matches(item_id, [_match(entity_name, entity_type)])
    return item_id


def _store_entity_count(
    repository: ItemRepository,
    entity_name: str,
    entity_type: str = "brand",
    *,
    current: int,
    baseline: int,
) -> None:
    for index in range(current):
        _store_matched_item(
            repository,
            entity_name,
            entity_type,
            collected_at=datetime(2026, 6, 12, 9, index, tzinfo=UTC),
            url_suffix=f"{entity_name}-current-{index}",
        )
    for index in range(baseline):
        _store_matched_item(
            repository,
            entity_name,
            entity_type,
            collected_at=datetime(2026, 6, 3, 9, index, tzinfo=UTC),
            url_suffix=f"{entity_name}-baseline-{index}",
        )


def _match(entity_name: str, entity_type: str, *, alias: str | None = None) -> dict[str, object]:
    return {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "alias": alias or entity_name,
        "confidence": 1.0,
        "reason": "context",
        "context_terms": ["local"],
    }
