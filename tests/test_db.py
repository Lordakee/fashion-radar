from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import inspect, text

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import SCHEMA_VERSION, SchemaVersionError, initialize_schema
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType


def _item(url: str, title: str = "The Row Margaux handbag") -> CollectedItem:
    return CollectedItem(
        source_name="Vogue Business",
        source_type=SourceType.RSS,
        url=url,
        title=title,
        published_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
        summary="A short attributed summary.",
    )


def test_schema_initializes_metadata_and_tables(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")

    initialize_schema(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {"schema_metadata", "items", "item_entities"} <= table_names
    with engine.connect() as connection:
        version = connection.execute(text("select version from schema_metadata")).scalar_one()
    assert version == SCHEMA_VERSION


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
