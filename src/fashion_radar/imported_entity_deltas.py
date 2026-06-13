from __future__ import annotations

from dataclasses import dataclass, field
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


class ImportedEntityDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: str
    entity_type: str
    current_count: int
    baseline_count: int
    delta: int
    change_label: Literal[
        "new_in_current",
        "increased",
        "dropped_from_current",
        "decreased",
        "unchanged",
    ]
    current_source_count: int
    baseline_source_count: int
    source_count_delta: int
    first_collected_at: str
    latest_collected_at: str


class ImportedEntityDeltas(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 7
    entity_type: str | None = None
    source_name: str | None = None
    limit: int = 50
    row_count: int = 0
    total_count: int = 0
    current_matched_item_count: int = 0
    baseline_matched_item_count: int = 0
    entities: list[ImportedEntityDelta] = Field(default_factory=list)


@dataclass
class _EntityAccumulator:
    entity_name: str
    entity_type: str
    current_item_ids: set[int] = field(default_factory=set)
    baseline_item_ids: set[int] = field(default_factory=set)
    current_source_names: set[str] = field(default_factory=set)
    baseline_source_names: set[str] = field(default_factory=set)
    collected_at_values: list[datetime] = field(default_factory=list)


def query_imported_entity_deltas(
    db_path: Path,
    *,
    as_of: str | datetime,
    current_days: int = 7,
    baseline_days: int = 7,
    entity_type: str | None = None,
    source_name: str | None = None,
    limit: int = 50,
) -> ImportedEntityDeltas:
    if current_days < 1:
        raise ValueError("current_days must be at least 1")
    if baseline_days < 1:
        raise ValueError("baseline_days must be at least 1")
    if limit < 0:
        raise ValueError("limit must be at least 0")

    as_of_value = parse_datetime_utc(as_of)
    current_start = as_of_value - timedelta(days=current_days)
    baseline_start = current_start - timedelta(days=baseline_days)
    entity_type_filter = (entity_type or "").strip() or None
    source_name_filter = (source_name or "").strip() or None
    result_base = {
        "database": str(db_path),
        "as_of": as_of_value.isoformat(),
        "current_window_start": current_start.isoformat(),
        "baseline_window_start": baseline_start.isoformat(),
        "current_days": current_days,
        "baseline_days": baseline_days,
        "entity_type": entity_type_filter,
        "source_name": source_name_filter,
        "limit": limit,
    }
    if not db_path.exists():
        return ImportedEntityDeltas(**result_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        return _query_imported_entity_deltas(
            engine,
            as_of_value=as_of_value,
            current_start=current_start,
            baseline_start=baseline_start,
            result_base=result_base,
        )
    finally:
        engine.dispose()


def render_imported_entity_deltas_table(result: ImportedEntityDeltas) -> list[str]:
    lines = [
        "Imported manual entity deltas from local SQLite.",
        (
            f"Baseline window: {result.baseline_window_start} < collected_at <= "
            f"{result.current_window_start}"
        ),
        (f"Current window: {result.current_window_start} < collected_at <= {result.as_of}"),
        f"Rows: {result.row_count} shown, {result.total_count} total entities",
        (
            f"Matched items: {result.current_matched_item_count} current, "
            f"{result.baseline_matched_item_count} baseline"
        ),
    ]
    if not result.entities:
        lines.append("No imported manual entity deltas found.")
        return lines

    lines.append(
        "Entity | Type | Current | Baseline | Delta | Change | Current Sources | "
        "Baseline Sources | Source Delta | First Collected At | Latest Collected At"
    )
    for row in result.entities:
        lines.append(
            f"{_table_cell(row.entity_name)} | {_table_cell(row.entity_type)} | "
            f"{row.current_count} | {row.baseline_count} | {row.delta} | "
            f"{row.change_label} | {row.current_source_count} | "
            f"{row.baseline_source_count} | {row.source_count_delta} | "
            f"{row.first_collected_at} | {row.latest_collected_at}"
        )
    return lines


def _query_imported_entity_deltas(
    engine: Engine,
    *,
    as_of_value: datetime,
    current_start: datetime,
    baseline_start: datetime,
    result_base: dict[str, object],
) -> ImportedEntityDeltas:
    entity_type_filter = result_base["entity_type"]
    source_name_filter = result_base["source_name"]
    query = (
        select(
            items.c.id,
            items.c.source_name,
            items.c.collected_at,
            item_entities.c.entity_name,
            item_entities.c.entity_type,
        )
        .select_from(items.join(item_entities, item_entities.c.item_id == items.c.id))
        .where(items.c.source_type == SourceType.MANUAL_IMPORT.value)
        .order_by(item_entities.c.entity_type, item_entities.c.entity_name, items.c.id)
    )
    if isinstance(entity_type_filter, str):
        query = query.where(item_entities.c.entity_type == entity_type_filter)
    if isinstance(source_name_filter, str):
        query = query.where(items.c.source_name == source_name_filter)

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    current_matched_item_ids: set[int] = set()
    baseline_matched_item_ids: set[int] = set()
    accumulators: dict[tuple[str, str], _EntityAccumulator] = {}
    for row in rows:
        collected_at = parse_datetime_utc(row["collected_at"])
        if baseline_start < collected_at <= current_start:
            window = "baseline"
        elif current_start < collected_at <= as_of_value:
            window = "current"
        else:
            continue

        item_id = int(row["id"])
        source_name = str(row["source_name"])
        entity_name = str(row["entity_name"])
        entity_type = str(row["entity_type"])
        key = (entity_name, entity_type)
        accumulator = accumulators.setdefault(
            key,
            _EntityAccumulator(entity_name=entity_name, entity_type=entity_type),
        )
        accumulator.collected_at_values.append(collected_at)
        if window == "current":
            current_matched_item_ids.add(item_id)
            accumulator.current_item_ids.add(item_id)
            accumulator.current_source_names.add(source_name)
        else:
            baseline_matched_item_ids.add(item_id)
            accumulator.baseline_item_ids.add(item_id)
            accumulator.baseline_source_names.add(source_name)

    entity_rows = [_to_delta_row(accumulator) for accumulator in accumulators.values()]
    entity_rows = sorted(entity_rows, key=_sort_key)
    limit = int(result_base["limit"])
    shown_rows = entity_rows[:limit]
    return ImportedEntityDeltas(
        **result_base,
        row_count=len(shown_rows),
        total_count=len(entity_rows),
        current_matched_item_count=len(current_matched_item_ids),
        baseline_matched_item_count=len(baseline_matched_item_ids),
        entities=shown_rows,
    )


def _to_delta_row(accumulator: _EntityAccumulator) -> ImportedEntityDelta:
    current_count = len(accumulator.current_item_ids)
    baseline_count = len(accumulator.baseline_item_ids)
    delta = current_count - baseline_count
    current_source_count = len(accumulator.current_source_names)
    baseline_source_count = len(accumulator.baseline_source_names)
    collected_at_values = accumulator.collected_at_values
    return ImportedEntityDelta(
        entity_name=accumulator.entity_name,
        entity_type=accumulator.entity_type,
        current_count=current_count,
        baseline_count=baseline_count,
        delta=delta,
        change_label=_change_label(current_count, baseline_count),
        current_source_count=current_source_count,
        baseline_source_count=baseline_source_count,
        source_count_delta=current_source_count - baseline_source_count,
        first_collected_at=min(collected_at_values).isoformat(),
        latest_collected_at=max(collected_at_values).isoformat(),
    )


def _change_label(
    current_count: int,
    baseline_count: int,
) -> Literal["new_in_current", "increased", "dropped_from_current", "decreased", "unchanged"]:
    if current_count > 0 and baseline_count == 0:
        return "new_in_current"
    if current_count == 0 and baseline_count > 0:
        return "dropped_from_current"
    if current_count > baseline_count:
        return "increased"
    if current_count < baseline_count:
        return "decreased"
    return "unchanged"


def _sort_key(row: ImportedEntityDelta) -> tuple[int, int, int, str, str]:
    change_order = {
        "new_in_current": 0,
        "increased": 1,
        "dropped_from_current": 2,
        "decreased": 3,
        "unchanged": 4,
    }
    return (
        change_order[row.change_label],
        -abs(row.delta),
        -row.current_count,
        row.entity_type,
        row.entity_name,
    )


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
