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


def _create_v2_schema_with_item(engine) -> None:
    _create_v1_schema_with_item(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            create table collector_runs (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                status varchar(32) not null,
                started_at varchar(64) not null,
                finished_at varchar(64),
                items_seen integer not null default 0,
                items_stored integer not null default 0,
                error_message text,
                error_type varchar(128)
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table source_health (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                consecutive_failures integer not null default 0,
                last_success_at varchar(64),
                last_failure_at varchar(64),
                unhealthy_until varchar(64),
                last_error_message text,
                constraint uq_source_health_source unique (source_name, source_type)
            )
            """
        )
        connection.exec_driver_sql("update schema_metadata set version = 2")


def _create_v3_schema_with_item_and_match(engine) -> None:
    _create_v2_schema_with_item(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "alter table items add column source_weight float not null default 1.0"
        )
        connection.exec_driver_sql("alter table items add column collected_at varchar(64)")
        connection.exec_driver_sql("update items set collected_at = '2026-06-01T10:00:00+00:00'")
        connection.exec_driver_sql("update schema_metadata set version = 3")
        connection.exec_driver_sql(
            """
            insert into item_entities (
                item_id, entity_name, entity_type, alias, confidence, reason, context_terms
            )
            values (1, 'The Row', 'brand', 'The Row', 1.0, 'context', '[]')
            """
        )


def test_schema_initializes_metadata_and_tables(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")

    initialize_schema(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {
        "schema_metadata",
        "items",
        "item_entities",
        "collector_runs",
        "source_health",
        "entity_first_seen",
    } <= table_names
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
    assert version == SCHEMA_VERSION
    columns = {column["name"] for column in inspect(engine).get_columns("items")}
    assert {"source_weight", "collected_at"} <= columns
    assert version == SCHEMA_VERSION
    assert SCHEMA_VERSION == 4


def test_schema_migrates_v1_to_v4_preserving_items(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    _create_v1_schema_with_item(engine)

    initialize_schema(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {"collector_runs", "source_health"} <= table_names
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
        item_count = connection.execute(text("select count(*) from items")).scalar_one()
        row = (
            connection.execute(
                text(
                    """
                    select title, source_weight, collected_at, published_at
                    from items
                    where id = 1
                    """
                )
            )
            .mappings()
            .one()
        )
    assert version == 4
    assert item_count == 1
    assert row["title"] == "The Row Margaux handbag"
    assert row["source_weight"] == 1.0
    assert row["collected_at"] == row["published_at"]


def test_schema_migrates_v2_to_v4_adding_source_weight_collected_at_and_first_seen(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    _create_v2_schema_with_item(engine)

    initialize_schema(engine)

    columns = {column["name"] for column in inspect(engine).get_columns("items")}
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
        row = (
            connection.execute(
                text(
                    """
                    select source_weight, collected_at, published_at
                    from items
                    where id = 1
                    """
                )
            )
            .mappings()
            .one()
        )
    assert {"source_weight", "collected_at"} <= columns
    assert version == 4
    assert row["source_weight"] == 1.0
    assert row["collected_at"] == row["published_at"]


def test_schema_migrates_v3_to_v4_adding_entity_first_seen_without_deleting_data(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    _create_v3_schema_with_item_and_match(engine)

    initialize_schema(engine)

    table_names = set(inspect(engine).get_table_names())
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
        item_count = connection.execute(text("select count(*) from items")).scalar_one()
        match_count = connection.execute(text("select count(*) from item_entities")).scalar_one()
    columns = {column["name"] for column in inspect(engine).get_columns("entity_first_seen")}
    assert "entity_first_seen" in table_names
    assert {"entity_name", "entity_type", "first_seen_at", "last_seen_at"} <= columns
    assert version == 4
    assert item_count == 1
    assert match_count == 1


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


def test_item_repository_stores_source_weight_and_preserves_first_collected_at(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_seen = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    later_seen = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)

    first_id = repository.upsert_item(
        _item("https://example.com/article?id=1&utm_source=ig"),
        source_weight=1.7,
        collected_at=first_seen,
    )
    second_id = repository.upsert_item(
        _item("https://example.com/article?id=1", "Updated title"),
        source_weight=1.9,
        collected_at=later_seen,
    )

    stored = repository.get_item(first_id)
    assert second_id == first_id
    assert stored["title"] == "Updated title"
    assert stored["source_weight"] == 1.9
    assert stored["collected_at"] == "2026-06-11T12:00:00+00:00"


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


def test_item_repository_tracks_entity_first_seen_and_last_seen_from_matches(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    later_item_id = repository.upsert_item(
        _item("https://example.com/later"),
        collected_at=datetime(2026, 6, 10, 12, 0, tzinfo=UTC),
    )
    earlier_item_id = repository.upsert_item(
        _item("https://example.com/earlier"),
        collected_at=datetime(2026, 6, 1, 12, 0, tzinfo=UTC),
    )
    latest_item_id = repository.upsert_item(
        _item("https://example.com/latest"),
        collected_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )
    matches = [
        {
            "entity_name": "The Row",
            "entity_type": "brand",
            "alias": "The Row",
            "confidence": 1.0,
            "reason": "context",
            "context_terms": ["margaux"],
        }
    ]

    repository.replace_item_matches(later_item_id, matches)
    repository.replace_item_matches(earlier_item_id, matches)
    repository.replace_item_matches(latest_item_id, matches)

    seen = repository.get_entity_first_seen("The Row", "brand")
    assert seen == {
        "entity_name": "The Row",
        "entity_type": "brand",
        "first_seen_at": "2026-06-01T12:00:00+00:00",
        "last_seen_at": "2026-06-12T12:00:00+00:00",
    }


def test_item_repository_prunes_old_items_and_match_rows_without_fk_cascade(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    old_item_id = repository.upsert_item(
        _item("https://example.com/old"),
        collected_at=datetime(2026, 5, 1, 12, 0, tzinfo=UTC),
    )
    kept_item_id = repository.upsert_item(
        _item("https://example.com/kept"),
        collected_at=datetime(2026, 6, 10, 12, 0, tzinfo=UTC),
    )
    for item_id in (old_item_id, kept_item_id):
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

    dry_run = repository.prune_items_older_than(datetime(2026, 6, 1, tzinfo=UTC), dry_run=True)
    pruned = repository.prune_items_older_than(datetime(2026, 6, 1, tzinfo=UTC))

    with engine.connect() as connection:
        item_ids = [
            row[0] for row in connection.execute(text("select id from items order by id")).all()
        ]
        orphan_count = connection.execute(
            text(
                """
                select count(*)
                from item_entities
                left join items on items.id = item_entities.item_id
                where items.id is null
                """
            )
        ).scalar_one()
        match_count = connection.execute(text("select count(*) from item_entities")).scalar_one()
    assert dry_run.items_deleted == 1
    assert dry_run.item_entities_deleted == 1
    assert dry_run.dry_run is True
    assert pruned.items_deleted == 1
    assert pruned.item_entities_deleted == 1
    assert item_ids == [kept_item_id]
    assert match_count == 1
    assert orphan_count == 0


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
