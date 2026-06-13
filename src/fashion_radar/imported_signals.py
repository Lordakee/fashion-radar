from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, inspect, select
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import SCHEMA_VERSION, item_entities, items, schema_metadata
from fashion_radar.models.source import SourceType
from fashion_radar.trends import create_readonly_sqlite_engine
from fashion_radar.utils.dates import parse_datetime_utc


class ImportedSignalMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: str
    entity_type: str
    alias: str
    confidence: float


class ImportedSignalItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    source_name: str
    url: str
    title: str
    published_at: str
    collected_at: str
    source_weight: float
    summary: str | None = None
    match_status: Literal["matched", "unmatched"]
    matches: list[ImportedSignalMatch] = Field(default_factory=list)


class ImportedSignalsReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    window_start: str
    lookback_days: int = 7
    source_name: str | None = None
    unmatched_only: bool = False
    limit: int | None = 50
    row_count: int = 0
    total_count: int = 0
    matched_count: int = 0
    unmatched_count: int = 0
    source_name_counts: dict[str, int] = Field(default_factory=dict)
    latest_collected_at: str | None = None
    items: list[ImportedSignalItem] = Field(default_factory=list)


REQUIRED_SCHEMA_METADATA_COLUMNS = {"version"}
REQUIRED_ITEMS_COLUMNS = {
    "id",
    "source_name",
    "source_type",
    "url",
    "title",
    "published_at",
    "collected_at",
    "source_weight",
    "summary",
}
REQUIRED_ITEM_ENTITIES_COLUMNS = {
    "id",
    "item_id",
    "entity_name",
    "entity_type",
    "alias",
    "confidence",
}


def query_imported_signals(
    db_path: Path,
    *,
    as_of: str | datetime,
    lookback_days: int = 7,
    limit: int | None = 50,
    source_name: str | None = None,
    unmatched_only: bool = False,
) -> ImportedSignalsReview:
    if lookback_days < 1:
        raise ValueError("lookback_days must be at least 1")
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")

    as_of_value = parse_datetime_utc(as_of)
    window_start_value = as_of_value - timedelta(days=lookback_days)
    source_filter = (source_name or "").strip() or None
    review_base = {
        "database": str(db_path),
        "as_of": as_of_value.isoformat(),
        "window_start": window_start_value.isoformat(),
        "lookback_days": lookback_days,
        "source_name": source_filter,
        "unmatched_only": unmatched_only,
        "limit": limit,
    }
    if not db_path.exists():
        return ImportedSignalsReview(**review_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        return _query_imported_signals(
            engine,
            as_of_value=as_of_value,
            window_start_value=window_start_value,
            review_base=review_base,
        )
    finally:
        engine.dispose()


def verify_imported_signals_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    required = {"schema_metadata", "items", "item_entities"}
    missing = sorted(required - table_names)
    if missing:
        raise RuntimeError(f"Database schema is missing required tables: {', '.join(missing)}")

    _verify_columns(inspector, "schema_metadata", REQUIRED_SCHEMA_METADATA_COLUMNS)
    _verify_columns(inspector, "items", REQUIRED_ITEMS_COLUMNS)
    _verify_columns(inspector, "item_entities", REQUIRED_ITEM_ENTITIES_COLUMNS)
    with engine.connect() as connection:
        version = connection.execute(select(schema_metadata.c.version)).scalar_one_or_none()
    if version != SCHEMA_VERSION:
        raise RuntimeError(
            f"Unsupported database schema version {version}; expected {SCHEMA_VERSION}"
        )


def render_imported_signals_table(review: ImportedSignalsReview) -> list[str]:
    lines = [
        "Imported manual signals from local SQLite.",
        f"Window: {review.window_start} < collected_at <= {review.as_of}",
        f"Rows: {review.row_count} shown, {review.total_count} total",
        f"Matched rows: {review.matched_count} matched, {review.unmatched_count} unmatched",
        f"Sources: {_format_counts(review.source_name_counts)}",
    ]
    if not review.items:
        lines.append("No imported manual signals found.")
        return lines

    lines.append("ID | Collected At | Match | Source | Weight | Title | URL")
    for item in review.items:
        lines.append(
            f"{item.id} | {item.collected_at} | {_format_match_cell(item)} | "
            f"{_table_cell(item.source_name)} | {item.source_weight:.2f} | "
            f"{_table_cell(item.title)} | {_table_cell(item.url)}"
        )
    return lines


def _query_imported_signals(
    engine: Engine,
    *,
    as_of_value: datetime,
    window_start_value: datetime,
    review_base: dict[str, object],
) -> ImportedSignalsReview:
    source_name = review_base["source_name"]
    unmatched_only = bool(review_base["unmatched_only"])
    limit = review_base["limit"]
    match_exists = select(item_entities.c.id).where(item_entities.c.item_id == items.c.id).exists()
    conditions = [
        items.c.source_type == SourceType.MANUAL_IMPORT.value,
        items.c.collected_at > window_start_value.isoformat(),
        items.c.collected_at <= as_of_value.isoformat(),
    ]
    if isinstance(source_name, str):
        conditions.append(items.c.source_name == source_name)
    if unmatched_only:
        conditions.append(~match_exists)

    item_query = (
        select(items)
        .where(*conditions)
        .order_by(
            items.c.collected_at.desc(),
            items.c.id.desc(),
        )
    )
    if limit is not None:
        item_query = item_query.limit(int(limit))

    with engine.connect() as connection:
        total_count = int(
            connection.execute(
                select(func.count()).select_from(items).where(*conditions)
            ).scalar_one()
        )
        matched_count = int(
            connection.execute(
                select(func.count()).select_from(items).where(*conditions, match_exists)
            ).scalar_one()
        )
        source_rows = connection.execute(
            select(items.c.source_name, func.count())
            .where(*conditions)
            .group_by(items.c.source_name)
            .order_by(items.c.source_name)
        ).all()
        latest_collected_at = connection.execute(
            select(func.max(items.c.collected_at)).select_from(items).where(*conditions)
        ).scalar_one_or_none()
        item_rows = connection.execute(item_query).mappings().all()

        item_ids = [int(row["id"]) for row in item_rows]
        matches_by_item_id = _fetch_matches_by_item_id(connection, item_ids)

    review_items = _build_review_items(item_rows, matches_by_item_id)
    return ImportedSignalsReview(
        **review_base,
        row_count=len(review_items),
        total_count=total_count,
        matched_count=matched_count,
        unmatched_count=total_count - matched_count,
        source_name_counts={str(name): int(count) for name, count in source_rows},
        latest_collected_at=(
            parse_datetime_utc(latest_collected_at).isoformat()
            if latest_collected_at is not None
            else None
        ),
        items=review_items,
    )


def _fetch_matches_by_item_id(
    connection: Any,
    item_ids: list[int],
) -> dict[int, list[ImportedSignalMatch]]:
    if not item_ids:
        return {}
    rows = connection.execute(
        select(
            item_entities.c.item_id,
            item_entities.c.entity_name,
            item_entities.c.entity_type,
            item_entities.c.alias,
            item_entities.c.confidence,
        )
        .where(item_entities.c.item_id.in_(item_ids))
        .order_by(item_entities.c.item_id, item_entities.c.id)
    ).mappings()
    matches: dict[int, list[ImportedSignalMatch]] = defaultdict(list)
    for row in rows:
        matches[int(row["item_id"])].append(
            ImportedSignalMatch(
                entity_name=str(row["entity_name"]),
                entity_type=str(row["entity_type"]),
                alias=str(row["alias"]),
                confidence=float(row["confidence"]),
            )
        )
    return dict(matches)


def _build_review_items(
    item_rows: list[Any],
    matches_by_item_id: dict[int, list[ImportedSignalMatch]],
) -> list[ImportedSignalItem]:
    review_items: list[ImportedSignalItem] = []
    for row in item_rows:
        item_id = int(row["id"])
        matches = matches_by_item_id.get(item_id, [])
        review_items.append(
            ImportedSignalItem(
                id=item_id,
                source_name=str(row["source_name"]),
                url=str(row["url"]),
                title=str(row["title"]),
                published_at=parse_datetime_utc(row["published_at"]).isoformat(),
                collected_at=parse_datetime_utc(row["collected_at"]).isoformat(),
                source_weight=float(row["source_weight"]),
                summary=row["summary"],
                match_status="matched" if matches else "unmatched",
                matches=matches,
            )
        )
    return review_items


def _verify_columns(inspector: Any, table_name: str, required_columns: set[str]) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing = sorted(required_columns - columns)
    if missing:
        raise RuntimeError(
            f"Database schema table {table_name} is missing required columns: {', '.join(missing)}"
        )


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{_table_cell(key)}={value}" for key, value in sorted(counts.items()))


def _format_match_cell(item: ImportedSignalItem) -> str:
    if not item.matches:
        return "unmatched"
    names = ", ".join(_table_cell(match.entity_name) for match in item.matches)
    return f"matched:{names}"


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
