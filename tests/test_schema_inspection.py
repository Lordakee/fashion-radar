from __future__ import annotations

from pathlib import Path

import pytest

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import SCHEMA_VERSION, initialize_schema, schema_metadata
from fashion_radar.db.schema_inspection import (
    DatabaseSchemaStatus,
    inspect_database_schema_status,
    parse_schema_version_value,
    parse_signed_schema_version_value,
    verify_readonly_schema,
)
from fashion_radar.db.schema_messages import FUTURE_SCHEMA_HINT, MIGRATE_DB_HINT
from fashion_radar.trends import create_readonly_sqlite_engine


def test_parse_schema_version_value_accepts_int_and_integer_string() -> None:
    assert parse_schema_version_value(5) == 5
    assert parse_schema_version_value("5") == 5


@pytest.mark.parametrize("value", [True, 5.7, "5.7", "+5", "-1", "latest", "", None])
def test_parse_schema_version_value_rejects_non_integer_values(value: object) -> None:
    assert parse_schema_version_value(value) is None


def test_parse_signed_schema_version_value_preserves_cli_signed_strings() -> None:
    assert parse_signed_schema_version_value("+5") == 5
    assert parse_signed_schema_version_value("-1") == -1
    assert parse_signed_schema_version_value("5") == 5
    assert parse_signed_schema_version_value(True) is None
    assert parse_signed_schema_version_value("5.7") is None


def _create_metadata_only_database(path: Path, version: object) -> None:
    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version)")
        connection.exec_driver_sql(
            "insert into schema_metadata (version) values (?)",
            (version,),
        )
    engine.dispose()


def _required_imported_tables() -> tuple[str, ...]:
    return ("schema_metadata", "items", "item_entities")


def _required_imported_columns() -> tuple[tuple[str, set[str]], ...]:
    return (
        ("schema_metadata", {"version"}),
        (
            "items",
            {
                "id",
                "source_name",
                "source_type",
                "url",
                "title",
                "published_at",
                "collected_at",
                "source_weight",
                "summary",
                "platform",
            },
        ),
        (
            "item_entities",
            {
                "id",
                "item_id",
                "entity_name",
                "entity_type",
                "alias",
                "confidence",
            },
        ),
    )


def test_verify_readonly_schema_reports_future_before_missing_tables(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, 999)
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError) as exc_info:
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()

    message = str(exc_info.value)
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in message
    assert FUTURE_SCHEMA_HINT in message
    assert "missing required tables" not in message
    assert "migrate-db" not in message


def test_verify_readonly_schema_missing_tables_has_migrate_hint(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    db_path.touch()
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError) as exc_info:
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()

    message = str(exc_info.value)
    assert "Database schema is missing required tables" in message
    assert MIGRATE_DB_HINT in message


def test_verify_readonly_schema_rejects_duplicate_versions(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
    engine.dispose()

    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError, match="schema_metadata.version has multiple rows"):
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()


def test_verify_readonly_schema_rejects_decimal_version(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, 5.7)
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError, match="schema_metadata.version is not an integer"):
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()


def test_inspect_database_schema_status_missing_database_is_non_mutating(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing.sqlite"

    status = inspect_database_schema_status(
        db_path,
        required_columns_by_table=_required_imported_columns(),
    )

    assert status == DatabaseSchemaStatus(state="missing")
    assert not db_path.exists()


def test_inspect_database_schema_status_current_database(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()

    status = inspect_database_schema_status(
        db_path,
        required_columns_by_table=(
            (schema_metadata.name, {column.name for column in schema_metadata.columns}),
        ),
    )

    assert status.state == "current"
    assert status.version == SCHEMA_VERSION


def test_inspect_database_schema_status_accepts_signed_cli_parser(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, f"+{SCHEMA_VERSION}")

    status = inspect_database_schema_status(
        db_path,
        required_columns_by_table=(("schema_metadata", {"version"}),),
        version_parser=parse_signed_schema_version_value,
    )

    assert status.state == "current"
    assert status.version == SCHEMA_VERSION


def test_verify_readonly_schema_rejects_signed_version_by_default(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, f"+{SCHEMA_VERSION}")
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError, match="schema_metadata.version is not an integer"):
            verify_readonly_schema(
                engine,
                required_tables=("schema_metadata",),
                required_columns_by_table=(("schema_metadata", {"version"}),),
            )
    finally:
        engine.dispose()


def test_verify_readonly_schema_accepts_signed_version_with_cli_parser(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, f"+{SCHEMA_VERSION}")
    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_readonly_schema(
            engine,
            required_tables=("schema_metadata",),
            required_columns_by_table=(("schema_metadata", {"version"}),),
            version_parser=parse_signed_schema_version_value,
        )
    finally:
        engine.dispose()
