from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

import fashion_radar.imported_signals as imported_signals_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import SCHEMA_VERSION, initialize_schema
from fashion_radar.imported_signals import (
    ImportedSignalItem,
    ImportedSignalMatch,
    ImportedSignalSourceSummaryRow,
    ImportedSignalsReview,
    ImportedSignalsSourceSummary,
    query_imported_signals,
    query_imported_signals_summary,
    render_imported_signals_summary_table,
    render_imported_signals_table,
    verify_imported_signals_schema,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType


def test_query_imported_signals_filters_window_and_manual_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS item",
        published_at=datetime(2026, 6, 12, 7, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/old",
        title="Old manual item",
        published_at=datetime(2026, 6, 10, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/in-window",
        title="In-window manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
        source_weight=1.4,
        summary="Short local note",
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
        limit=50,
    )

    assert review.database == str(db_path)
    assert review.as_of == "2026-06-12T12:00:00+00:00"
    assert review.window_start == "2026-06-11T12:00:00+00:00"
    assert review.lookback_days == 1
    assert review.total_count == 1
    assert review.row_count == 1
    assert review.matched_count == 0
    assert review.unmatched_count == 1
    assert review.source_name_counts == {"Manual Import": 1}
    assert review.latest_collected_at == "2026-06-12T09:00:00+00:00"
    assert review.items[0].title == "In-window manual item"
    assert review.items[0].source_weight == 1.4
    assert review.items[0].summary == "Short local note"
    assert review.items[0].match_status == "unmatched"
    assert review.items[0].matches == []


def test_query_imported_signals_window_excludes_start_includes_as_of_and_excludes_future(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/window-start",
        title="Window start item",
        published_at=datetime(2026, 6, 5, 12, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 5, 12, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/as-of",
        title="As-of item",
        published_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/future",
        title="Future item",
        published_at=datetime(2026, 6, 12, 12, 1, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 12, 1, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=7,
    )

    assert review.total_count == 1
    assert [item.title for item in review.items] == ["As-of item"]


def test_query_imported_signals_orders_by_collected_at_then_id(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_id = _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/first",
        title="First item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    second_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/second",
        title="Second item",
        published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
    )

    assert [item.id for item in review.items] == [second_id, first_id]


def test_query_imported_signals_source_filter_and_limit_zero(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    for index in range(2):
        _store_item(
            repository,
            source_name="Community Tool Export",
            url=f"https://example.com/community-{index}",
            title=f"Community item {index}",
            published_at=datetime(2026, 6, 12, 8 + index, 0, tzinfo=UTC),
            collected_at=datetime(2026, 6, 12, 9 + index, 0, tzinfo=UTC),
        )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 11, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 13, 0, tzinfo=UTC),
        lookback_days=1,
        source_name=" Community Tool Export ",
        limit=0,
    )

    assert review.source_name == "Community Tool Export"
    assert review.limit == 0
    assert review.total_count == 2
    assert review.row_count == 0
    assert review.source_name_counts == {"Community Tool Export": 2}
    assert review.items == []


def test_query_imported_signals_blank_source_filter_is_no_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        source_name="   ",
    )

    assert review.source_name is None
    assert review.total_count == 1


def test_query_imported_signals_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert review.database == str(db_path)
    assert review.as_of == "2026-06-12T12:00:00+00:00"
    assert review.total_count == 0
    assert review.row_count == 0
    assert review.items == []
    assert not db_path.parent.exists()


def test_query_imported_signals_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    _store_item(
        ItemRepository(engine),
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()
    calls: list[Path] = []
    original = imported_signals_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_signals_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert calls == [db_path]


def test_query_imported_signals_handles_uri_special_characters_in_database_path(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "data ? # & %" / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    _store_item(
        ItemRepository(engine),
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert review.total_count == 1
    assert review.items[0].title == "Manual item"


def test_query_imported_signals_reads_match_status_and_unmatched_only(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    matched_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/margaux",
        title="Margaux interest",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/unmatched",
        title="Unmatched item",
        published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        matched_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["margaux"],
            },
            {
                "entity_name": "Margaux",
                "entity_type": "product",
                "alias": "Margaux",
                "confidence": 0.9,
                "reason": "context",
                "context_terms": ["bag"],
            },
        ],
    )
    engine.dispose()

    full_review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
    )
    unmatched_review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
        unmatched_only=True,
    )

    assert full_review.total_count == 2
    assert full_review.matched_count == 1
    assert full_review.unmatched_count == 1
    matched = next(item for item in full_review.items if item.id == matched_id)
    assert matched.match_status == "matched"
    assert [match.model_dump() for match in matched.matches] == [
        {
            "entity_name": "The Row",
            "entity_type": "brand",
            "alias": "The Row",
            "confidence": 1.0,
        },
        {
            "entity_name": "Margaux",
            "entity_type": "product",
            "alias": "Margaux",
            "confidence": 0.9,
        },
    ]
    assert unmatched_review.total_count == 1
    assert unmatched_review.matched_count == 0
    assert unmatched_review.unmatched_count == 1
    assert unmatched_review.items[0].match_status == "unmatched"


def test_query_imported_signals_rejects_negative_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    with pytest.raises(ValueError, match="limit must be at least 0"):
        query_imported_signals(
            db_path,
            as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
            limit=-1,
        )

    assert not db_path.parent.exists()


def test_verify_imported_signals_schema_rejects_empty_database(tmp_path: Path) -> None:
    db_path = tmp_path / "empty.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)

    with pytest.raises(RuntimeError, match="schema_metadata"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_requires_items_and_item_entities(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "broken.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )

    with pytest.raises(RuntimeError, match="item_entities, items|items, item_entities"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_missing_item_entities(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-matches.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name text not null,
                source_type text not null,
                url text not null,
                normalized_url text not null,
                title text not null,
                published_at text not null,
                source_weight real not null,
                collected_at text not null,
                summary text,
                content_hash text not null
            )
            """
        )

    with pytest.raises(RuntimeError, match="item_entities"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_missing_schema_metadata_version(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-version.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (label text)")
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name text not null,
                source_type text not null,
                url text not null,
                title text not null,
                published_at text not null,
                collected_at text not null,
                source_weight real not null,
                summary text
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name text not null,
                entity_type text not null,
                alias text not null,
                confidence real not null
            )
            """
        )

    with pytest.raises(RuntimeError, match="schema_metadata.*version"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_missing_required_item_columns(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-column.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name text not null,
                source_type text not null,
                url text not null,
                title text not null,
                published_at text not null,
                source_weight real not null,
                summary text
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name text not null,
                entity_type text not null,
                alias text not null,
                confidence real not null
            )
            """
        )

    with pytest.raises(RuntimeError, match="items.*collected_at"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_future_version(tmp_path: Path) -> None:
    db_path = tmp_path / "future.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.execute(text("update schema_metadata set version = 999"))

    with pytest.raises(RuntimeError, match="Unsupported database schema version 999"):
        verify_imported_signals_schema(engine)


def test_render_imported_signals_table_empty() -> None:
    review = ImportedSignalsReview(
        database="missing.sqlite",
        as_of="2026-06-12T12:00:00+00:00",
        window_start="2026-06-05T12:00:00+00:00",
        lookback_days=7,
    )

    assert render_imported_signals_table(review) == [
        "Imported manual signals from local SQLite.",
        "Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00",
        "Rows: 0 shown, 0 total",
        "Matched rows: 0 matched, 0 unmatched",
        "Sources: none",
        "No imported manual signals found.",
    ]
    assert all(not line.startswith("Matches:") for line in render_imported_signals_table(review))


def test_render_imported_signals_table_populated_sanitizes_cells() -> None:
    review = ImportedSignalsReview(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-12T12:00:00+00:00",
        window_start="2026-06-05T12:00:00+00:00",
        lookback_days=7,
        row_count=2,
        total_count=2,
        matched_count=1,
        unmatched_count=1,
        source_name_counts={"Community | Tool\nExport": 1, "Manual Import": 1},
        latest_collected_at="2026-06-12T12:00:00+00:00",
        items=[
            ImportedSignalItem(
                id=3,
                source_name="Community | Tool\nExport",
                url="https://example.com/margaux|row",
                title="Margaux |\ninterest",
                published_at="2026-06-12T09:00:00+00:00",
                collected_at="2026-06-12T12:00:00+00:00",
                source_weight=1.4,
                summary="Short local note.",
                match_status="matched",
                matches=[
                    ImportedSignalMatch(
                        entity_name="The | Row\n",
                        entity_type="brand",
                        alias="The Row",
                        confidence=1.0,
                    )
                ],
            ),
            ImportedSignalItem(
                id=2,
                source_name="Manual Import",
                url="https://example.com/le-teckel",
                title="Le Teckel bag rises",
                published_at="2026-06-12T08:00:00+00:00",
                collected_at="2026-06-12T11:00:00+00:00",
                source_weight=1.0,
                summary=None,
                match_status="unmatched",
                matches=[],
            ),
        ],
    )

    assert render_imported_signals_table(review) == [
        "Imported manual signals from local SQLite.",
        "Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00",
        "Rows: 2 shown, 2 total",
        "Matched rows: 1 matched, 1 unmatched",
        "Sources: Community / Tool Export=1, Manual Import=1",
        "ID | Collected At | Match | Source | Weight | Title | URL",
        "3 | 2026-06-12T12:00:00+00:00 | matched:The / Row | "
        "Community / Tool Export | 1.40 | Margaux / interest | "
        "https://example.com/margaux/row",
        "2 | 2026-06-12T11:00:00+00:00 | unmatched | Manual Import | 1.00 | Le Teckel bag rises | https://example.com/le-teckel",
    ]
    assert all(not line.startswith("Matches:") for line in render_imported_signals_table(review))


def test_query_imported_signals_summary_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    summary = query_imported_signals_summary(db_path)

    assert summary.database == str(db_path)
    assert summary.source_type == "manual_import"
    assert summary.source_count == 0
    assert summary.row_count == 0
    assert summary.matched_count == 0
    assert summary.unmatched_count == 0
    assert summary.first_collected_at is None
    assert summary.latest_collected_at is None
    assert summary.sources == []
    assert not db_path.parent.exists()


def test_query_imported_signals_summary_groups_manual_rows_and_match_presence(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    matched_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/margaux",
        title="Margaux interest",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/unmatched",
        title="Unmatched item",
        published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 10, 7, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS item",
        published_at=datetime(2026, 6, 12, 7, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 11, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        matched_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["margaux"],
            },
            {
                "entity_name": "Margaux",
                "entity_type": "product",
                "alias": "Margaux",
                "confidence": 0.9,
                "reason": "context",
                "context_terms": ["bag"],
            },
        ],
    )
    engine.dispose()

    summary = query_imported_signals_summary(db_path)

    assert summary.source_count == 2
    assert summary.row_count == 3
    assert summary.matched_count == 1
    assert summary.unmatched_count == 2
    assert summary.first_collected_at == "2026-06-10T09:00:00+00:00"
    assert summary.latest_collected_at == "2026-06-12T10:00:00+00:00"
    assert [source.source_name for source in summary.sources] == [
        "Community Tool Export",
        "Manual Import",
    ]
    assert summary.sources[0].row_count == 2
    assert summary.sources[0].matched_count == 1
    assert summary.sources[0].unmatched_count == 1
    assert summary.sources[0].first_collected_at == "2026-06-12T09:00:00+00:00"
    assert summary.sources[0].latest_collected_at == "2026-06-12T10:00:00+00:00"
    assert summary.sources[1].row_count == 1
    assert summary.sources[1].matched_count == 0
    assert summary.sources[1].unmatched_count == 1


def test_query_imported_signals_summary_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    _store_item(
        ItemRepository(engine),
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()
    calls: list[Path] = []
    original = imported_signals_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_signals_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_signals_summary(db_path)

    assert calls == [db_path]


def test_render_imported_signals_summary_table_empty() -> None:
    summary = ImportedSignalsSourceSummary(database="missing.sqlite")

    assert render_imported_signals_summary_table(summary) == [
        "Imported manual signal source summary from local SQLite.",
        "Rows: 0 retained manual rows across 0 sources",
        "Matched rows: 0 matched, 0 unmatched",
        "Collected at: none",
        "No imported manual signal sources found.",
    ]


def test_render_imported_signals_summary_table_populated_sanitizes_cells() -> None:
    summary = ImportedSignalsSourceSummary(
        database="data/fashion-radar.sqlite",
        source_count=2,
        row_count=3,
        matched_count=1,
        unmatched_count=2,
        first_collected_at="2026-06-10T09:00:00+00:00",
        latest_collected_at="2026-06-12T10:00:00+00:00",
        sources=[
            ImportedSignalSourceSummaryRow(
                source_name="Community | Tool\nExport",
                row_count=2,
                matched_count=1,
                unmatched_count=1,
                first_collected_at="2026-06-12T09:00:00+00:00",
                latest_collected_at="2026-06-12T10:00:00+00:00",
            ),
            ImportedSignalSourceSummaryRow(
                source_name="Manual Import",
                row_count=1,
                matched_count=0,
                unmatched_count=1,
                first_collected_at="2026-06-10T09:00:00+00:00",
                latest_collected_at="2026-06-10T09:00:00+00:00",
            ),
        ],
    )

    assert render_imported_signals_summary_table(summary) == [
        "Imported manual signal source summary from local SQLite.",
        "Rows: 3 retained manual rows across 2 sources",
        "Matched rows: 1 matched, 2 unmatched",
        "Collected at: 2026-06-10T09:00:00+00:00 first, 2026-06-12T10:00:00+00:00 latest",
        "Source | Rows | Matched Rows | Unmatched Rows | First Collected At | Latest Collected At",
        "Community / Tool Export | 2 | 1 | 1 | "
        "2026-06-12T09:00:00+00:00 | 2026-06-12T10:00:00+00:00",
        "Manual Import | 1 | 0 | 1 | 2026-06-10T09:00:00+00:00 | 2026-06-10T09:00:00+00:00",
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
    source_weight: float = 1.0,
    summary: str | None = None,
) -> int:
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=published_at,
            summary=summary,
        ),
        source_weight=source_weight,
        collected_at=collected_at,
    )
