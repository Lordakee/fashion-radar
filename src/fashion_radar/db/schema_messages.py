from __future__ import annotations

from fashion_radar.db.schema import SCHEMA_VERSION

MIGRATE_DB_HINT = (
    "Run `fashion-radar migrate-db --data-dir ...` to initialize or upgrade "
    "the local SQLite database schema."
)
FUTURE_SCHEMA_HINT = "This database may require a newer Fashion Radar version."


def unsupported_schema_message(version: int | None) -> str:
    if version is not None and version > SCHEMA_VERSION:
        return (
            f"Unsupported database schema version {version}; expected {SCHEMA_VERSION}. "
            f"{FUTURE_SCHEMA_HINT}"
        )
    return (
        f"Unsupported database schema version {version}; expected {SCHEMA_VERSION}. "
        f"{MIGRATE_DB_HINT}"
    )


def missing_schema_message(message: str) -> str:
    return f"{message}. {MIGRATE_DB_HINT}"


def invalid_schema_message(message: str) -> str:
    return f"invalid: {message}"
