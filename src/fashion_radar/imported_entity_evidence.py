from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import item_entities, items
from fashion_radar.imported_signals import verify_imported_signals_schema
from fashion_radar.models.source import SourceType
from fashion_radar.trends import create_readonly_sqlite_engine
from fashion_radar.utils.dates import parse_datetime_utc


class ImportedEntityEvidenceRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    window: Literal["current", "baseline"]
    source_name: str
    title: str
    url: str
    published_at: str
    collected_at: str


class ImportedEntityEvidenceReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    entity_name: str
    entity_type: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 7
    source_type: Literal["manual_import"] = "manual_import"
    source_name: str | None = None
    limit: int | None = 20
    row_count: int = 0
    total_count: int = 0
    current_mentions: int = 0
    baseline_mentions: int = 0
    distinct_sources: int = 0
    evidence: list[ImportedEntityEvidenceRow] = Field(default_factory=list)


def query_imported_entity_evidence(
    db_path: Path,
    *,
    as_of: str | datetime,
    entity_name: str,
    entity_type: str,
    current_days: int = 7,
    baseline_days: int = 7,
    source_name: str | None = None,
    limit: int | None = 20,
) -> ImportedEntityEvidenceReview:
    if current_days < 1:
        raise ValueError("current_days must be at least 1")
    if baseline_days < 1:
        raise ValueError("baseline_days must be at least 1")
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")
    entity_name_filter = entity_name.strip()
    if not entity_name_filter:
        raise ValueError("entity name must not be blank")
    entity_type_filter = entity_type.strip()
    if not entity_type_filter:
        raise ValueError("entity type must not be blank")

    as_of_value = parse_datetime_utc(as_of)
    current_window_start = as_of_value - timedelta(days=current_days)
    baseline_window_start = current_window_start - timedelta(days=baseline_days)
    source_filter = (source_name or "").strip() or None
    review_base = {
        "database": str(db_path),
        "as_of": as_of_value.isoformat(),
        "entity_name": entity_name_filter,
        "entity_type": entity_type_filter,
        "current_window_start": current_window_start.isoformat(),
        "baseline_window_start": baseline_window_start.isoformat(),
        "current_days": current_days,
        "baseline_days": baseline_days,
        "source_name": source_filter,
        "limit": limit,
    }
    if not db_path.exists():
        return ImportedEntityEvidenceReview(**review_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        evidence = _query_evidence_rows(
            engine,
            as_of=as_of_value,
            current_window_start=current_window_start,
            baseline_window_start=baseline_window_start,
            entity_name=entity_name_filter,
            entity_type=entity_type_filter,
            source_name=source_filter,
        )
    finally:
        engine.dispose()

    current_rows = [row for row in evidence if row.window == "current"]
    baseline_rows = [row for row in evidence if row.window == "baseline"]
    visible_evidence = evidence[:limit] if limit is not None else evidence
    return ImportedEntityEvidenceReview(
        **review_base,
        row_count=len(visible_evidence),
        total_count=len(evidence),
        current_mentions=len(current_rows),
        baseline_mentions=len(baseline_rows),
        distinct_sources=len({row.source_name for row in current_rows}),
        evidence=visible_evidence,
    )


def render_imported_entity_evidence_table(review: ImportedEntityEvidenceReview) -> list[str]:
    lines = [
        "Imported manual entity evidence from local SQLite.",
        (
            "Evidence rows are retained manual_import rows whose stored matched entity "
            "equals the requested entity."
        ),
        f"Entity: {_table_cell(review.entity_name)}",
        f"Entity type: {_table_cell(review.entity_type)}",
        (
            f"Baseline window: {review.baseline_window_start} < collected_at <= "
            f"{review.current_window_start}"
        ),
        f"Current window: {review.current_window_start} < collected_at <= {review.as_of}",
        f"Source name: {_table_cell(review.source_name or 'none')}",
        f"Rows: {review.row_count} shown, {review.total_count} total evidence rows",
        f"Mentions: {review.current_mentions} current, {review.baseline_mentions} baseline",
        f"Distinct current sources: {review.distinct_sources}",
    ]
    if not review.evidence:
        lines.append("No imported manual entity evidence found.")
        return lines

    lines.append("Window | ID | Collected At | Source | Title | URL")
    for row in review.evidence:
        lines.append(
            f"{row.window} | {row.id} | {row.collected_at} | "
            f"{_table_cell(row.source_name)} | {_table_cell(row.title)} | {_table_cell(row.url)}"
        )
    return lines


def _query_evidence_rows(
    engine: Engine,
    *,
    as_of: datetime,
    current_window_start: datetime,
    baseline_window_start: datetime,
    entity_name: str,
    entity_type: str,
    source_name: str | None,
) -> list[ImportedEntityEvidenceRow]:
    query = (
        select(
            items.c.id,
            items.c.source_name,
            items.c.url,
            items.c.published_at,
            items.c.title,
            items.c.collected_at,
        )
        .select_from(items.join(item_entities, item_entities.c.item_id == items.c.id))
        .where(
            items.c.source_type == SourceType.MANUAL_IMPORT.value,
            item_entities.c.entity_name == entity_name,
            item_entities.c.entity_type == entity_type,
        )
        .order_by(items.c.id)
    )
    if source_name is not None:
        query = query.where(items.c.source_name == source_name)

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    seen_item_ids: set[int] = set()
    evidence: list[ImportedEntityEvidenceRow] = []
    for row in rows:
        item_id = int(row["id"])
        if item_id in seen_item_ids:
            continue
        collected_at = parse_datetime_utc(row["collected_at"])
        if baseline_window_start < collected_at <= current_window_start:
            window: Literal["current", "baseline"] = "baseline"
        elif current_window_start < collected_at <= as_of:
            window = "current"
        else:
            continue
        seen_item_ids.add(item_id)
        evidence.append(_evidence_row(row, window=window, collected_at=collected_at))

    return sorted(
        evidence,
        key=lambda row: (
            0 if row.window == "current" else 1,
            -parse_datetime_utc(row.collected_at).timestamp(),
            -row.id,
        ),
    )


def _evidence_row(
    row,
    *,
    window: Literal["current", "baseline"],
    collected_at: datetime,
) -> ImportedEntityEvidenceRow:
    return ImportedEntityEvidenceRow(
        id=int(row["id"]),
        window=window,
        source_name=str(row["source_name"]),
        title=str(row["title"] or ""),
        url=str(row["url"] or ""),
        published_at=parse_datetime_utc(row["published_at"]).isoformat(),
        collected_at=collected_at.isoformat(),
    )


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
