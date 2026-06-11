from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import inspect, text

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.db.schema import SCHEMA_VERSION, SchemaVersionError, initialize_schema
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType


def _item(url: str, title: str = "The Row Margaux handbag") -> CollectedItem:
    return CollectedItem(
        source_name="Vogue Business",
        source_type=SourceType.RSS,
        url=url,
        title=title,
        published_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
        summary="A short attributed summary.",
    )


def _source() -> SourceDefinition:
    return SourceDefinition(
        name="Vogue Business",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )


def _create_v1_schema_with_item(engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (1)")
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                url text not null,
                normalized_url text not null,
                title text not null,
                published_at varchar(64) not null,
                summary text,
                content_hash varchar(64) not null,
                constraint uq_items_normalized_url unique (normalized_url)
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name varchar(255) not null,
                entity_type varchar(64) not null,
                alias varchar(255) not null,
                confidence float not null,
                reason varchar(64) not null,
                context_terms text not null default '[]'
            )
            """
        )
        connection.exec_driver_sql(
            """
            insert into items (
                id, source_name, source_type, url, normalized_url, title,
                published_at, summary, content_hash
            )
            values (
                1, 'Vogue Business', 'rss', 'https://example.com/article',
                'https://example.com/article', 'The Row Margaux handbag',
                '2026-06-11T10:00:00+00:00', 'A short attributed summary.', 'abc'
            )
            """
        )


def test_schema_initializes_metadata_and_tables(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")

    initialize_schema(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {"schema_metadata", "items", "item_entities", "collector_runs", "source_health"} <= (
        table_names
    )
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
    assert version == SCHEMA_VERSION
    assert SCHEMA_VERSION == 2


def test_schema_migrates_v1_to_v2_preserving_items(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    _create_v1_schema_with_item(engine)

    initialize_schema(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {"collector_runs", "source_health"} <= table_names
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
        item_count = connection.execute(text("select count(*) from items")).scalar_one()
        title = connection.execute(text("select title from items where id = 1")).scalar_one()
    assert version == 2
    assert item_count == 1
    assert title == "The Row Margaux handbag"


def test_schema_rejects_future_version(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer not null)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (999)")

    with pytest.raises(SchemaVersionError, match="Unsupported schema version"):
        initialize_schema(engine)


def test_item_repository_upserts_by_normalized_url(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)

    first_id = repository.upsert_item(
        _item("HTTPS://example.com/article?id=1&utm_source=ig#section")
    )
    second_id = repository.upsert_item(_item("https://example.com/article?id=1", "Updated title"))

    assert second_id == first_id
    assert repository.count_items() == 1
    stored = repository.get_item(first_id)
    assert stored["normalized_url"] == "https://example.com/article?id=1"
    assert stored["title"] == "Updated title"
    assert stored["summary"] == "A short attributed summary."


def test_item_repository_replaces_entity_matches(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(_item("https://example.com/article"))

    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["margaux"],
            }
        ],
    )

    matches = repository.list_item_matches(item_id)
    assert matches == [
        {
            "entity_name": "The Row",
            "entity_type": "brand",
            "alias": "The Row",
            "confidence": 1.0,
            "reason": "context",
            "context_terms": ["margaux"],
        }
    ]


def test_collector_run_repository_records_status(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = CollectorRunRepository(engine)
    started_at = datetime(2026, 6, 11, 10, 0, tzinfo=UTC)
    finished_at = datetime(2026, 6, 11, 10, 1, tzinfo=UTC)

    run_id = repository.record_run(
        _source(),
        status="success",
        started_at=started_at,
        finished_at=finished_at,
        items_seen=3,
        items_stored=2,
    )

    runs = repository.list_recent_runs()
    assert runs == [
        {
            "id": run_id,
            "source_name": "Vogue Business",
            "source_type": "rss",
            "status": "success",
            "started_at": "2026-06-11T10:00:00+00:00",
            "finished_at": "2026-06-11T10:01:00+00:00",
            "items_seen": 3,
            "items_stored": 2,
            "error_message": None,
            "error_type": None,
        }
    ]


def test_source_health_marks_unhealthy_after_repeated_failures_and_expires(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = SourceHealthRepository(engine)
    source = _source()

    repository.record_failure(
        source,
        error_message="timeout",
        occurred_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
        max_failures=2,
        retention_hours=24,
    )
    assert repository.is_unhealthy(source, now=datetime(2026, 6, 11, 10, 30, tzinfo=UTC)) is False

    repository.record_failure(
        source,
        error_message="still timeout",
        occurred_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
        max_failures=2,
        retention_hours=24,
    )

    health = repository.get_health(source)
    assert health is not None
    assert health["consecutive_failures"] == 2
    assert health["last_error_message"] == "still timeout"
    assert health["unhealthy_until"] == "2026-06-12T11:00:00+00:00"
    assert repository.is_unhealthy(source, now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)) is True
    assert repository.is_unhealthy(source, now=datetime(2026, 6, 12, 11, 1, tzinfo=UTC)) is False

    cleared = repository.clear_expired_unhealthy_sources(
        now=datetime(2026, 6, 12, 11, 1, tzinfo=UTC)
    )
    health = repository.get_health(source)
    assert cleared == 1
    assert health is not None
    assert health["consecutive_failures"] == 0
    assert health["unhealthy_until"] is None

    repository.record_success(source, occurred_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC))
    health = repository.get_health(source)
    assert health is not None
    assert health["consecutive_failures"] == 0
    assert health["last_success_at"] == "2026-06-12T12:00:00+00:00"
    assert health["unhealthy_until"] is None
