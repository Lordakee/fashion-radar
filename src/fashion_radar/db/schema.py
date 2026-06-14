from __future__ import annotations

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    inspect,
    select,
    update,
)
from sqlalchemy.engine import Engine

SCHEMA_VERSION = 5

metadata = MetaData()

schema_metadata = Table(
    "schema_metadata",
    metadata,
    Column("version", Integer, primary_key=True),
)

items = Table(
    "items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("source_name", String(255), nullable=False),
    Column("source_type", String(64), nullable=False),
    Column("url", Text, nullable=False),
    Column("normalized_url", Text, nullable=False),
    Column("title", Text, nullable=False),
    Column("published_at", String(64), nullable=False),
    Column("source_weight", Float, nullable=False, default=1.0),
    Column("collected_at", String(64), nullable=False),
    Column("summary", Text),
    Column("platform", String(64)),
    Column("content_hash", String(64), nullable=False),
    UniqueConstraint("normalized_url", name="uq_items_normalized_url"),
)

item_entities = Table(
    "item_entities",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
    Column("entity_name", String(255), nullable=False),
    Column("entity_type", String(64), nullable=False),
    Column("alias", String(255), nullable=False),
    Column("confidence", Float, nullable=False),
    Column("reason", String(64), nullable=False),
    Column("context_terms", Text, nullable=False, default="[]"),
)

entity_first_seen = Table(
    "entity_first_seen",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("entity_name", String(255), nullable=False),
    Column("entity_type", String(64), nullable=False),
    Column("first_seen_at", String(64), nullable=False),
    Column("last_seen_at", String(64), nullable=False),
    UniqueConstraint("entity_name", "entity_type", name="uq_entity_first_seen_entity"),
)

collector_runs = Table(
    "collector_runs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("source_name", String(255), nullable=False),
    Column("source_type", String(64), nullable=False),
    Column("status", String(32), nullable=False),
    Column("started_at", String(64), nullable=False),
    Column("finished_at", String(64)),
    Column("items_seen", Integer, nullable=False, default=0),
    Column("items_stored", Integer, nullable=False, default=0),
    Column("error_message", Text),
    Column("error_type", String(128)),
)

source_health = Table(
    "source_health",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("source_name", String(255), nullable=False),
    Column("source_type", String(64), nullable=False),
    Column("consecutive_failures", Integer, nullable=False, default=0),
    Column("last_success_at", String(64)),
    Column("last_failure_at", String(64)),
    Column("unhealthy_until", String(64)),
    Column("last_error_message", Text),
    UniqueConstraint("source_name", "source_type", name="uq_source_health_source"),
)


class SchemaVersionError(RuntimeError):
    """Raised when an existing database schema is incompatible."""


def initialize_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "schema_metadata" in table_names:
        existing_version = _read_schema_version(engine)
        if existing_version == 1:
            _migrate_v1_to_v2(engine)
            existing_version = 2
        if existing_version == 2:
            _migrate_v2_to_v3(engine)
            existing_version = 3
        if existing_version == 3:
            _migrate_v3_to_v4(engine)
            existing_version = 4
        if existing_version == 4:
            _migrate_v4_to_v5(engine)
            existing_version = 5
        if existing_version is not None and existing_version != SCHEMA_VERSION:
            raise SchemaVersionError(
                f"Unsupported schema version {existing_version}; expected {SCHEMA_VERSION}"
            )

    metadata.create_all(engine)
    with engine.begin() as connection:
        existing_version = connection.execute(
            select(schema_metadata.c.version)
        ).scalar_one_or_none()
        if existing_version is None:
            connection.execute(schema_metadata.insert().values(version=SCHEMA_VERSION))


def _read_schema_version(engine: Engine) -> int | None:
    with engine.connect() as connection:
        return connection.execute(select(schema_metadata.c.version)).scalar_one_or_none()


def _migrate_v1_to_v2(engine: Engine) -> None:
    with engine.begin() as connection:
        collector_runs.create(connection, checkfirst=True)
        source_health.create(connection, checkfirst=True)
        connection.execute(update(schema_metadata).values(version=2))


def _migrate_v2_to_v3(engine: Engine) -> None:
    existing_columns = {column["name"] for column in inspect(engine).get_columns("items")}
    with engine.begin() as connection:
        if "source_weight" not in existing_columns:
            connection.exec_driver_sql(
                "alter table items add column source_weight float not null default 1.0"
            )
        if "collected_at" not in existing_columns:
            connection.exec_driver_sql("alter table items add column collected_at varchar(64)")
            connection.exec_driver_sql(
                "update items set collected_at = published_at where collected_at is null"
            )
        connection.execute(update(schema_metadata).values(version=3))


def _migrate_v3_to_v4(engine: Engine) -> None:
    with engine.begin() as connection:
        entity_first_seen.create(connection, checkfirst=True)
        connection.execute(update(schema_metadata).values(version=4))


def _migrate_v4_to_v5(engine: Engine) -> None:
    existing_columns = {column["name"] for column in inspect(engine).get_columns("items")}
    with engine.begin() as connection:
        if "platform" not in existing_columns:
            connection.exec_driver_sql("alter table items add column platform varchar(64)")
        connection.execute(update(schema_metadata).values(version=SCHEMA_VERSION))
