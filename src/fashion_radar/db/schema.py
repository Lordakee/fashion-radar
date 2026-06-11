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
)
from sqlalchemy.engine import Engine

SCHEMA_VERSION = 1

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
    Column("summary", Text),
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


class SchemaVersionError(RuntimeError):
    """Raised when an existing database schema is incompatible."""


def initialize_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "schema_metadata" in table_names:
        existing_version = _read_schema_version(engine)
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
