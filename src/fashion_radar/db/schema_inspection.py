from __future__ import annotations

import re
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

from fashion_radar.db.engine import create_readonly_sqlite_engine
from fashion_radar.db.schema import SCHEMA_VERSION, schema_metadata
from fashion_radar.db.schema_messages import missing_schema_message, unsupported_schema_message

SchemaVersionParser = Callable[[object], int | None]
RequiredColumnsByTable = Sequence[tuple[str, Collection[str]]]


@dataclass(frozen=True)
class DatabaseSchemaStatus:
    state: Literal["missing", "current", "old", "future", "invalid"]
    version: int | None = None
    detail: str | None = None
    missing_schema: bool = False


def parse_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value.strip()):
        return int(value)
    return None


def parse_signed_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+", value.strip()):
        return int(value)
    return None


def read_schema_version_if_available(
    engine: Engine,
    inspector: Any,
    table_names: set[str],
    *,
    version_parser: SchemaVersionParser = parse_schema_version_value,
) -> int | None:
    if "schema_metadata" not in table_names:
        return None
    metadata_columns = {column["name"] for column in inspector.get_columns("schema_metadata")}
    if "version" not in metadata_columns:
        raise RuntimeError(
            "Database schema table schema_metadata is missing required columns: version"
        )
    try:
        with engine.connect() as connection:
            raw_version = connection.execute(select(schema_metadata.c.version)).scalar_one_or_none()
    except MultipleResultsFound as exc:
        raise RuntimeError("schema_metadata.version has multiple rows") from exc
    if raw_version is None:
        return None
    version = version_parser(raw_version)
    if version is None:
        raise RuntimeError("schema_metadata.version is not an integer")
    return version


def verify_required_columns(
    inspector: Any,
    table_name: str,
    required_columns: Collection[str],
) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing = sorted(set(required_columns) - columns)
    if missing:
        raise RuntimeError(
            f"Database schema table {table_name} is missing required columns: {', '.join(missing)}"
        )


def verify_readonly_schema(
    engine: Engine,
    *,
    required_tables: Sequence[str],
    required_columns_by_table: RequiredColumnsByTable,
    version_parser: SchemaVersionParser = parse_schema_version_value,
) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    version = read_schema_version_if_available(
        engine,
        inspector,
        table_names,
        version_parser=version_parser,
    )
    if version is not None and version != SCHEMA_VERSION:
        raise RuntimeError(unsupported_schema_message(version))

    missing_tables = sorted(set(required_tables) - table_names)
    if missing_tables:
        raise RuntimeError(
            missing_schema_message(
                f"Database schema is missing required tables: {', '.join(missing_tables)}"
            )
        )

    for table_name, columns in required_columns_by_table:
        verify_required_columns(inspector, table_name, columns)
    if version is None:
        raise RuntimeError(missing_schema_message("schema_metadata.version is empty"))


def inspect_database_schema_status(
    db_path: Path,
    *,
    required_columns_by_table: RequiredColumnsByTable,
    version_parser: SchemaVersionParser = parse_schema_version_value,
) -> DatabaseSchemaStatus:
    if not db_path.exists():
        return DatabaseSchemaStatus(state="missing")

    engine = create_readonly_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        if "schema_metadata" not in table_names:
            return DatabaseSchemaStatus(
                state="invalid",
                detail="missing schema_metadata table",
                missing_schema=True,
            )

        metadata_columns = {column["name"] for column in inspector.get_columns("schema_metadata")}
        if "version" not in metadata_columns:
            return DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is missing",
            )

        try:
            version = read_schema_version_if_available(
                engine,
                inspector,
                table_names,
                version_parser=version_parser,
            )
        except RuntimeError as exc:
            return DatabaseSchemaStatus(state="invalid", detail=str(exc))
        if version is None:
            return DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is empty",
                missing_schema=True,
            )
        if version < SCHEMA_VERSION:
            return DatabaseSchemaStatus(state="old", version=version)
        if version > SCHEMA_VERSION:
            return DatabaseSchemaStatus(state="future", version=version)

        expected_tables = {table_name for table_name, _columns in required_columns_by_table}
        missing_tables = sorted(expected_tables - table_names)
        if missing_tables:
            return DatabaseSchemaStatus(
                state="invalid",
                version=version,
                detail=f"missing tables: {', '.join(missing_tables)}",
            )
        for table_name, columns in required_columns_by_table:
            actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
            missing_columns = sorted(set(columns) - actual_columns)
            if missing_columns:
                return DatabaseSchemaStatus(
                    state="invalid",
                    version=version,
                    detail=f"table {table_name} missing columns: {', '.join(missing_columns)}",
                )
        return DatabaseSchemaStatus(state="current", version=version)
    except SQLAlchemyError as exc:
        return DatabaseSchemaStatus(state="invalid", detail=str(exc))
    finally:
        engine.dispose()
