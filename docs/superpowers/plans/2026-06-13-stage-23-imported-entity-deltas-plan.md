# Stage 23 Imported Entity Deltas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar imported-entity-deltas`, a local read-only command that compares stored matched entities on retained `manual_import` rows across current and baseline collected-at windows.

**Architecture:** Add a focused `src/fashion_radar/imported_entity_deltas.py` module with Pydantic result models, a read-only query helper, deterministic Python aggregation, and a table renderer. Add a thin Typer command in `src/fashion_radar/cli.py`; it parses `--as-of`, delegates to the query helper, and prints table or JSON. The command never initializes, migrates, imports, matches, scores, reports, schedules, monitors, collects, or writes artifacts.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, SQLite read-only URI mode, pytest, ruff, uv.

---

## Process Gate

Implementation may start only after Claude Code approves this Stage 23 plan
review and every Critical or Important plan-review finding is resolved. After
implementation, Stage 23 code must be submitted to Claude Code for code review
before commit and push.

## File Structure

- Create `src/fashion_radar/imported_entity_deltas.py`
  - Models: `ImportedEntityDelta`, `ImportedEntityDeltas`
  - Helpers: `query_imported_entity_deltas()`, `_query_imported_entity_deltas()`, `render_imported_entity_deltas_table()`
  - Internal aggregation helpers for item-level counts and stable ordering
- Modify `src/fashion_radar/cli.py`
  - Import query/render helpers
  - Add `ImportedEntityDeltasOutputFormat`
  - Add `IMPORTED_ENTITY_DELTAS_*` option constants
  - Add `imported-entity-deltas` command
- Create `tests/test_imported_entity_deltas.py`
  - Unit tests for missing DB, aggregation, filters, limit, read-only engine use, and rendering
- Modify `tests/test_cli.py`
  - CLI tests for help, JSON/table output, invalid input, missing DB, invalid schema, special paths, and no mutation
- Modify docs and changelog with local-only command examples
- Create Claude Code Stage 23 plan/code review prompt/result files

## Task 1: Query Models And Read-Only Aggregation

**Files:**
- Create: `src/fashion_radar/imported_entity_deltas.py`
- Create: `tests/test_imported_entity_deltas.py`

- [ ] **Step 1: Write failing model and missing-DB tests**

Create `tests/test_imported_entity_deltas.py` with imports:

```python
from datetime import UTC, datetime
from pathlib import Path

import pytest

import fashion_radar.imported_entity_deltas as imported_entity_deltas_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_entity_deltas import (
    ImportedEntityDelta,
    ImportedEntityDeltas,
    query_imported_entity_deltas,
    render_imported_entity_deltas_table,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
```

Add:

```python
def test_query_imported_entity_deltas_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
    )

    assert result.database == str(db_path)
    assert result.as_of == "2026-06-13T12:00:00+00:00"
    assert result.current_window_start == "2026-06-06T12:00:00+00:00"
    assert result.baseline_window_start == "2026-05-30T12:00:00+00:00"
    assert result.current_days == 7
    assert result.baseline_days == 7
    assert result.entity_type is None
    assert result.source_name is None
    assert result.limit == 50
    assert result.row_count == 0
    assert result.total_count == 0
    assert result.current_matched_item_count == 0
    assert result.baseline_matched_item_count == 0
    assert result.entities == []
    assert not db_path.parent.exists()
```

- [ ] **Step 2: Write failing aggregation test**

Add a helper:

```python
def _store_item(
    repository: ItemRepository,
    *,
    source_name: str,
    url: str,
    title: str,
    published_at: datetime,
    collected_at: datetime,
    source_type: SourceType = SourceType.MANUAL_IMPORT,
) -> int:
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=published_at,
        ),
        source_weight=1.0,
        collected_at=collected_at,
    )


def _match(entity_name: str, entity_type: str) -> dict[str, object]:
    return {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "alias": entity_name,
        "confidence": 1.0,
        "reason": "context",
        "context_terms": ["local"],
    }
```

Add:

```python
def test_query_imported_entity_deltas_groups_entities_and_counts_item_level_windows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/current",
        title="The Row Margaux current",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    baseline_id = _store_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/baseline",
        title="The Row baseline",
        published_at=datetime(2026, 6, 3, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 3, 9, 0, tzinfo=UTC),
    )
    new_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/new",
        title="Alaia flats",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 9, 0, tzinfo=UTC),
    )
    rss_id = _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS Alaia",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        current_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["margaux"],
            },
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 0.95,
                "reason": "context",
                "context_terms": ["bag"],
            },
        ],
    )
    repository.replace_item_matches(
        baseline_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["baseline"],
            }
        ],
    )
    repository.replace_item_matches(
        new_id,
        [
            {
                "entity_name": "Alaia",
                "entity_type": "brand",
                "alias": "Alaia",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["flats"],
            }
        ],
    )
    repository.replace_item_matches(
        rss_id,
        [
            {
                "entity_name": "Alaia",
                "entity_type": "brand",
                "alias": "Alaia",
                "confidence": 1.0,
                "reason": "context",
                "context_terms": ["rss"],
            }
        ],
    )
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
    )

    assert result.total_count == 2
    assert result.row_count == 2
    assert result.current_matched_item_count == 2
    assert result.baseline_matched_item_count == 1
    assert [row.entity_name for row in result.entities] == ["Alaia", "The Row"]
    assert result.entities[0].change_label == "new_in_current"
    assert result.entities[0].current_count == 1
    assert result.entities[0].baseline_count == 0
    assert result.entities[0].delta == 1
    assert result.entities[1].current_count == 1
    assert result.entities[1].baseline_count == 1
    assert result.entities[1].delta == 0
    assert result.entities[1].change_label == "unchanged"
```

The RED failure should be `ModuleNotFoundError` or a missing symbol.

- [ ] **Step 3: Write failing label, ordering, boundary, and source-count tests**

Add:

```python
def test_query_imported_entity_deltas_labels_and_orders_all_change_states(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    # Build entities so the final sorted labels are:
    # new_in_current, increased, dropped_from_current, decreased, unchanged.
    # Use two current items and one baseline item for "Increased Brand".
    # Use one baseline item only for "Dropped Brand".
    # Use one current item and two baseline items for "Decreased Brand".
    # Use one current and one baseline item for "Unchanged Brand".
    # Store all rows as manual_import and all matches as entity_type="brand".
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
    )

    assert [row.change_label for row in result.entities] == [
        "new_in_current",
        "increased",
        "dropped_from_current",
        "decreased",
        "unchanged",
    ]
    assert [row.entity_name for row in result.entities] == [
        "New Brand",
        "Increased Brand",
        "Dropped Brand",
        "Decreased Brand",
        "Unchanged Brand",
    ]
```

When implementing this test, create the rows explicitly with `_store_item()` and
`repository.replace_item_matches()` calls. Do not leave the explanatory
comments in the committed test body.

Add:

```python
def test_query_imported_entity_deltas_orders_ties_deterministically(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    # Use only increased entities so the primary change-label order is tied.
    # Increased Move 3: current=4, baseline=1, abs(delta)=3.
    # Increased Move 2: current=3, baseline=1, abs(delta)=2.
    # Increased Current Count: current=3, baseline=2, abs(delta)=1.
    # Product Tie: current=2, baseline=1, entity_type="product".
    # Brand Tie A/B: current=2, baseline=1, entity_type="brand".
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
    )

    assert [(row.entity_type, row.entity_name) for row in result.entities] == [
        ("brand", "Increased Move 3"),
        ("brand", "Increased Move 2"),
        ("brand", "Increased Current Count"),
        ("brand", "Brand Tie A"),
        ("brand", "Brand Tie B"),
        ("product", "Product Tie"),
    ]
```

When implementing this test, create concrete current/baseline items to produce
exactly the counts named in the comments. The expected order proves absolute
movement first, then current count, then entity type, then entity name.

Add:

```python
def test_query_imported_entity_deltas_classifies_window_boundaries_in_python(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    # as_of = 2026-06-13T12:00:00Z, current_start = 2026-06-06T12:00:00Z,
    # baseline_start = 2026-05-30T12:00:00Z.
    # Store one row exactly at baseline_start and assert it is excluded.
    # Store one row exactly at current_start and assert it is baseline.
    # Store one row exactly at as_of and assert it is current.
    # Store one future row and assert it is excluded.
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
    )

    by_name = {row.entity_name: row for row in result.entities}
    assert "Baseline Start Brand" not in by_name
    assert by_name["Current Start Brand"].baseline_count == 1
    assert by_name["Current Start Brand"].current_count == 0
    assert by_name["As Of Brand"].current_count == 1
    assert "Future Brand" not in by_name
```

Add:

```python
def test_query_imported_entity_deltas_counts_distinct_source_labels_by_window(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    # Store "Multi Source Brand" in the current window from two stored
    # source_name labels and in the baseline window from one source_name label.
    # Store duplicate matches on one current item; the current_source_count must
    # remain 2 and the entity current_count must count that item once.
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
    )

    row = next(row for row in result.entities if row.entity_name == "Multi Source Brand")
    assert row.current_source_count == 2
    assert row.baseline_source_count == 1
    assert row.source_count_delta == 1

    filtered = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
        source_name="Community Tool Export",
    )
    filtered_row = next(
        row for row in filtered.entities if row.entity_name == "Multi Source Brand"
    )
    assert filtered_row.current_source_count == 1
    assert filtered_row.baseline_source_count == 0
    assert filtered_row.source_count_delta == 1
```

When implementing these tests, replace the comments with concrete helper calls
and keep the comments only if they clarify the boundary timestamp math.

- [ ] **Step 4: Write failing filter, limit, and read-only tests**

Add tests:

```python
def test_query_imported_entity_deltas_filters_source_type_and_limit_zero(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_id = _store_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/first",
        title="First brand",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    second_id = _store_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/second",
        title="Second brand",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 9, 0, tzinfo=UTC),
    )
    rss_id = _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss-second",
        title="Second brand RSS",
        published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(first_id, [_match("First Brand", "brand")])
    repository.replace_item_matches(second_id, [_match("Second Brand", "brand")])
    repository.replace_item_matches(rss_id, [_match("RSS Brand", "brand")])
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
        limit=0,
    )

    assert result.total_count == 2
    assert result.row_count == 0
    assert result.entities == []
```

```python
def test_query_imported_entity_deltas_filters_entity_type_and_source_name(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    product_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/product",
        title="Margaux",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    brand_id = _store_item(
        repository,
        source_name="Manual Export",
        url="https://example.com/brand",
        title="The Row",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(product_id, [_match("Margaux", "product")])
    repository.replace_item_matches(brand_id, [_match("The Row", "brand")])
    engine.dispose()

    result = query_imported_entity_deltas(
        db_path,
        as_of="2026-06-13T12:00:00Z",
        entity_type="product",
        source_name="Community Tool Export",
    )

    assert result.total_count == 1
    assert [row.entity_name for row in result.entities] == ["Margaux"]
    assert result.entities[0].entity_type == "product"
```

```python
def test_query_imported_entity_deltas_uses_readonly_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()
    calls: list[Path] = []
    original = imported_entity_deltas_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_entity_deltas_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_entity_deltas(db_path, as_of="2026-06-13T12:00:00Z")

    assert calls == [db_path]
```

- [ ] **Step 5: Run query tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_entity_deltas.py -q
```

Expected: fail because the module and symbols do not exist.

- [ ] **Step 6: Implement models and query helper**

Create `src/fashion_radar/imported_entity_deltas.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import item_entities, items
from fashion_radar.imported_signals import verify_imported_signals_schema
from fashion_radar.models.source import SourceType
from fashion_radar.trends import create_readonly_sqlite_engine
from fashion_radar.utils.dates import parse_datetime_utc
```

Add the public models:

```python
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
```

Add:

```python
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
```

- [ ] **Step 7: Implement aggregation internals**

Use a dataclass for aggregation:

```python
@dataclass
class _EntityAccumulator:
    entity_name: str
    entity_type: str
    current_item_ids: set[int] = field(default_factory=set)
    baseline_item_ids: set[int] = field(default_factory=set)
    current_source_names: set[str] = field(default_factory=set)
    baseline_source_names: set[str] = field(default_factory=set)
    collected_at_values: list[datetime] = field(default_factory=list)
```

Implement `_query_imported_entity_deltas()` by reading mappings:

```python
query = (
    select(
        items.c.id,
        items.c.source_name,
        items.c.collected_at,
        item_entities.c.entity_name,
        item_entities.c.entity_type,
    )
    .select_from(items.join(item_entities, item_entities.c.item_id == items.c.id))
    .where(
        items.c.source_type == SourceType.MANUAL_IMPORT.value,
    )
    .order_by(item_entities.c.entity_type, item_entities.c.entity_name, items.c.id)
)
```

Apply optional filters from `result_base["entity_type"]` and
`result_base["source_name"]` before execution. Do not filter by collected-at in
SQL; fetch the matched manual rows that satisfy the exact stored-label filters,
then parse `row["collected_at"]` with `parse_datetime_utc()` and classify each
row in Python:

```python
collected_at = parse_datetime_utc(row["collected_at"])
if baseline_start < collected_at <= current_start:
    window = "baseline"
elif current_start < collected_at <= as_of_value:
    window = "current"
else:
    continue
```

Aggregate rows in Python so duplicate item/entity matches collapse through
sets. The top-level matched item counts use the same stored source-name and
entity-type filters as the entity rows. Build rows with:

```python
current_count = len(accumulator.current_item_ids)
baseline_count = len(accumulator.baseline_item_ids)
delta = current_count - baseline_count
current_source_count = len(accumulator.current_source_names)
baseline_source_count = len(accumulator.baseline_source_names)
```

Skip entities with `current_count == 0 and baseline_count == 0`. Sort with:

```python
change_order = {
    "new_in_current": 0,
    "increased": 1,
    "dropped_from_current": 2,
    "decreased": 3,
    "unchanged": 4,
}
rows = sorted(
    rows,
    key=lambda row: (
        change_order[row.change_label],
        -abs(row.delta),
        -row.current_count,
        row.entity_type,
        row.entity_name,
    ),
)
```

Set `total_count=len(rows)`, `entities=rows[:limit]`, `row_count=len(entities)`,
and matched item counts from distinct item IDs observed in each window after
stored source-name and entity-type filters.

- [ ] **Step 8: Run query tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_entity_deltas.py -q -k "query_imported_entity_deltas"
```

Expected: query tests pass.

## Task 2: Table Rendering

**Files:**
- Modify: `src/fashion_radar/imported_entity_deltas.py`
- Test: `tests/test_imported_entity_deltas.py`

- [ ] **Step 1: Write failing renderer tests**

Add:

```python
def test_render_imported_entity_deltas_table_empty() -> None:
    result = ImportedEntityDeltas(
        database="missing.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
    )

    assert render_imported_entity_deltas_table(result) == [
        "Imported manual entity deltas from local SQLite.",
        "Baseline window: 2026-05-30T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00",
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Rows: 0 shown, 0 total entities",
        "Matched items: 0 current, 0 baseline",
        "No imported manual entity deltas found.",
    ]
```

Add:

```python
def test_render_imported_entity_deltas_table_populated_sanitizes_cells() -> None:
    result = ImportedEntityDeltas(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
        row_count=1,
        total_count=1,
        current_matched_item_count=2,
        baseline_matched_item_count=1,
        entities=[
            ImportedEntityDelta(
                entity_name="Alaia | Flats\nSignal",
                entity_type="product\rtype",
                current_count=2,
                baseline_count=1,
                delta=1,
                change_label="increased",
                current_source_count=2,
                baseline_source_count=1,
                source_count_delta=1,
                first_collected_at="2026-06-03T09:00:00+00:00",
                latest_collected_at="2026-06-12T09:00:00+00:00",
            )
        ],
    )

    assert render_imported_entity_deltas_table(result) == [
        "Imported manual entity deltas from local SQLite.",
        "Baseline window: 2026-05-30T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00",
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Rows: 1 shown, 1 total entities",
        "Matched items: 2 current, 1 baseline",
        "Entity | Type | Current | Baseline | Delta | Change | Current Sources | Baseline Sources | Source Delta | First Collected At | Latest Collected At",
        "Alaia / Flats Signal | product type | 2 | 1 | 1 | increased | 2 | 1 | 1 | 2026-06-03T09:00:00+00:00 | 2026-06-12T09:00:00+00:00",
    ]
```

- [ ] **Step 2: Run renderer tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_entity_deltas.py -q -k "render_imported_entity_deltas_table"
```

Expected: fail because the renderer does not exist yet.

- [ ] **Step 3: Implement renderer**

Add:

```python
def render_imported_entity_deltas_table(result: ImportedEntityDeltas) -> list[str]:
    lines = [
        "Imported manual entity deltas from local SQLite.",
        (
            f"Baseline window: {result.baseline_window_start} < collected_at <= "
            f"{result.current_window_start}"
        ),
        (
            f"Current window: {result.current_window_start} < collected_at <= "
            f"{result.as_of}"
        ),
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
```

Add `_table_cell()` matching existing imported-signal behavior.

- [ ] **Step 4: Run renderer tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_entity_deltas.py -q -k "render_imported_entity_deltas_table"
```

Expected: renderer tests pass.

## Task 3: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add tests near imported-signals CLI tests:

```python
def test_imported_entity_deltas_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-entity-deltas", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--current-days" in result.output
    assert "--baseline-days" in result.output
    assert "--entity-type" in result.output
    assert "--source-name" in result.output
    assert "--format" in result.output
    assert "Compare imported manual entity counts" in result.output
```

Add JSON/table tests using a fixture that creates matched current and baseline
manual-import rows:

```python
def _prepare_imported_entity_deltas_cli_fixture(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    # Store the same three manual rows used by
    # test_query_imported_entity_deltas_groups_entities_and_counts_item_level_windows:
    # current The Row, baseline The Row, and current Alaia.
    # Store one matched RSS row and assert later that it is not printed.
    # Use full match dictionaries with entity_name/entity_type/alias/confidence/
    # reason/context_terms, matching the query unit-test helper.
    engine.dispose()
    return data_dir
```

When implementing the fixture, write the full `repository.upsert_item()` and
`repository.replace_item_matches()` calls directly or extract small local test
helpers; do not leave comments as executable placeholders.

```python
def test_imported_entity_deltas_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_deltas_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "entity_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_matched_item_count",
        "baseline_matched_item_count",
        "entities",
    ]
    assert list(payload["entities"][0]) == [
        "entity_name",
        "entity_type",
        "current_count",
        "baseline_count",
        "delta",
        "change_label",
        "current_source_count",
        "baseline_source_count",
        "source_count_delta",
        "first_collected_at",
        "latest_collected_at",
    ]
    forbidden = {
        "id",
        "item_id",
        "title",
        "url",
        "summary",
        "reason",
        "context_terms",
        "confidence",
        "alias",
        "source_file",
        "source_path",
        "import_path",
    }
    assert forbidden.isdisjoint(payload)
    for entity in payload["entities"]:
        assert forbidden.isdisjoint(entity)
```

```python
def test_imported_entity_deltas_command_prints_table_without_item_fields(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_entity_deltas_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-deltas",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual entity deltas from local SQLite." in result.output
    assert "Alaia | brand | 1 | 0 | 1 | new_in_current" in result.output
    assert "The Row | brand | 1 | 1 | 0 | unchanged" in result.output
    assert "The Row Margaux current" not in result.output
    assert "https://example.com/current" not in result.output
    for forbidden in (
        "alias",
        "confidence",
        "reason",
        "context_terms",
        "margaux",
        "baseline",
        "flats",
        "rss",
        "source_file",
        "source_path",
        "import_path",
    ):
        assert forbidden not in result.output
```

- [ ] **Step 2: Write failing CLI guard tests**

Add:

```python
def _fail_imported_entity_deltas_query(*args, **kwargs):
    raise AssertionError("query_imported_entity_deltas should not be called")
```

Add tests for:

- invalid `--format xml` rejects before query and creates no data directory;
- invalid `--as-of` prints `Could not compare imported entity deltas`;
- missing database JSON returns zeros without artifacts;
- invalid schema exits `1` without traceback;
- special-character `--data-dir`;
- no mutation of `items`, `item_entities`, `schema_metadata.version`, and table set.

- [ ] **Step 3: Run CLI tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_entity_deltas"
```

Expected: fail because the command and CLI import do not exist.

- [ ] **Step 4: Implement CLI command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.imported_entity_deltas import (
    query_imported_entity_deltas,
    render_imported_entity_deltas_table,
)
```

Add:

```python
ImportedEntityDeltasOutputFormat = Literal["table", "json"]
```

Add option constants:

```python
IMPORTED_ENTITY_DELTAS_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC comparison timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_ENTITY_DELTAS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add command before `imported-signals-summary`:

```python
@app.command(name="imported-entity-deltas")
def imported_entity_deltas_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_ENTITY_DELTAS_AS_OF_OPTION,
    current_days: int = typer.Option(7, min=1, help="Current window in days."),
    baseline_days: int = typer.Option(7, min=1, help="Baseline window in days."),
    entity_type: str | None = typer.Option(None, help="Exact stored entity type filter."),
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    limit: int = typer.Option(50, min=0, help="Maximum entity delta rows to print."),
    output_format: ImportedEntityDeltasOutputFormat = IMPORTED_ENTITY_DELTAS_FORMAT_OPTION,
) -> None:
    """Compare imported manual entity counts across local collected-at windows."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not compare imported entity deltas: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        result = query_imported_entity_deltas(
            default_database_path(data_dir),
            as_of=as_of_value,
            current_days=current_days,
            baseline_days=baseline_days,
            entity_type=entity_type,
            source_name=source_name,
            limit=limit,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not compare imported entity deltas: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
        return
    for line in render_imported_entity_deltas_table(result):
        typer.echo(line)
```

- [ ] **Step 5: Run CLI tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_entity_deltas"
```

Expected: CLI tests pass.

## Task 4: Documentation And Changelog

**Files:**
- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add bounded command examples**

Add examples near imported signal review commands:

```bash
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

Use prose:

```markdown
`imported-entity-deltas` is local and read-only. It compares stored matched
entities on retained `manual_import` rows across collected-at windows and
prints aggregate entity counts only.
```

- [ ] **Step 2: Update upload checklist**

Add installed-wheel smoke command:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-entity-deltas --help
```

- [ ] **Step 3: Update changelog**

Add under `### Added`:

```markdown
- Local read-only `imported-entity-deltas` command for comparing stored matched
  entities on retained `manual_import` rows across collected-at windows.
```

- [ ] **Step 4: Run docs boundary scan**

Run:

```bash
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

Expected: no new capability wording from Stage 23 product docs.

## Task 5: Review, Verification, And Release

**Files:**
- Create: `docs/reviews/claude-code-stage-23-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-23-code-review.md`
- Modify: any file needed to fix Critical or Important review findings

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_entity_deltas.py tests/test_cli.py tests/test_db.py -q -k "imported_entity_deltas or imported_signals or readonly"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-23-code-review-prompt.md` asking Claude
Code to review the current working tree in read-only mode. Required review
focus:

- reads only existing local SQLite and `manual_import` rows;
- counts stored entities at item level across current/baseline windows;
- duplicate matches on one item do not inflate counts;
- missing DB and invalid format do not create artifacts;
- invalid schema produces a controlled CLI error;
- table/JSON outputs hide item-level fields;
- docs stay local.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-23-code-review-prompt.md | tee docs/reviews/claude-code-stage-23-code-review.md
```

Fix every Critical and Important finding before continuing.

- [ ] **Step 3: Run full release checks**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
rm -rf /tmp/fashion-radar-dist-stage23
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage23
```

Expected: all pass.

- [ ] **Step 4: Run installed-wheel smoke**

Run:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv" --python 3.11
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage23/*.whl
"$tmp_env/venv/bin/fashion-radar" imported-entity-deltas --help
"$tmp_env/venv/bin/fashion-radar" imported-entity-deltas --data-dir "$tmp_env/data ? # & %" --as-of "2026-06-13T12:00:00Z" --format json
```

Expected: both commands exit zero and print no traceback.

- [ ] **Step 5: Run repository hygiene scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no secrets or generated artifacts that should be committed.

- [ ] **Step 6: Commit and push**

This repository is currently using the user-authorized direct-main upload
workflow. Do this step only after Claude Code code review has no Critical or
Important findings and all release checks pass. If the workflow changes to a
branch/PR flow, stop and adapt this step before pushing.

Run:

```bash
current_branch="$(git branch --show-current)"
if [ "$current_branch" != "main" ]; then
  echo "Not on main; stop and adapt push target."
  exit 1
fi
git status --short --branch
git add src/fashion_radar/imported_entity_deltas.py src/fashion_radar/cli.py tests/test_imported_entity_deltas.py tests/test_cli.py README.md docs CHANGELOG.md
git commit -m "Add imported entity deltas command"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: branch is `main`, commit succeeds, and push updates `origin/main`.
