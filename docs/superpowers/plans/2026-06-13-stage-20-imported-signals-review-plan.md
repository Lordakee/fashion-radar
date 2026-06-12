# Stage 20 Imported Signals Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar imported-signals`, a local read-only command for reviewing retained `manual_import` rows already stored in SQLite.

**Architecture:** Create a focused `fashion_radar.imported_signals` module that verifies the local database schema, opens SQLite through the existing read-only URI helper, and queries `items` plus existing `item_entities` match rows. Add a thin Typer command that validates `--as-of` before database access, prints deterministic table/JSON output, and never creates data/config/report artifacts for missing databases or invalid input.

**Tech Stack:** Python 3.11+, SQLAlchemy Core, SQLite read-only URI mode, Pydantic v2, Typer, pytest, ruff, uv. No new dependencies and no lockfile changes.

---

## Scope Guard

Stage 20 must not add or document:

- social/platform connectors, platform search, automated community ingestion, or source acquisition;
- scraping, crawler development, browser automation, Playwright, Selenium, MCP platform scraping servers, account automation, unofficial platform APIs, or export-acquisition instructions;
- login cookies, account/session files, browser profiles, tokens, credentials, proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall bypass;
- recursive scanning, watch folders, schedulers, background jobs, import execution changes, DB migrations, source-health changes, collector changes, dashboard writes, report generation, matcher behavior changes, scoring algorithm changes, persistent adapter tables, or network calls;
- product-facing approval, audit, policy checklist, authorization verification, or legal-review workflow features.

## File Structure

- Create `src/fashion_radar/imported_signals.py`: Pydantic output models, read-only schema verification, query function, and table renderer.
- Create `tests/test_imported_signals.py`: focused module tests for time windows, filtering, counts, matches, missing DB, and invalid schema.
- Modify `src/fashion_radar/cli.py`: add `ImportedSignalsOutputFormat`, output option, and `imported-signals` command.
- Modify `tests/test_cli.py`: add CLI help/output/no-artifact/invalid-input/invalid-schema tests.
- Modify documentation files listed in Task 4.

## Task 1: Add Module Tests

**Files:**

- Create: `tests/test_imported_signals.py`

- [ ] **Step 1: Write failing tests for query behavior**

Create `tests/test_imported_signals.py` with imports:

```python
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

import fashion_radar.imported_signals as imported_signals_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import SCHEMA_VERSION, initialize_schema
from fashion_radar.imported_signals import (
    ImportedSignalItem,
    ImportedSignalMatch,
    ImportedSignalsReview,
    query_imported_signals,
    render_imported_signals_table,
    verify_imported_signals_schema,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
```

Add this fixture helper:

```python
def _store_item(
    repository: ItemRepository,
    *,
    source_name: str,
    source_type: SourceType = SourceType.MANUAL_IMPORT,
    url: str,
    title: str,
    published_at: datetime,
    collected_at: datetime,
    source_weight: float = 1.0,
    summary: str | None = None,
) -> int:
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=published_at,
            summary=summary,
        ),
        source_weight=source_weight,
        collected_at=collected_at,
    )
```

Add the first failing test:

```python
def test_query_imported_signals_filters_window_and_manual_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS item",
        published_at=datetime(2026, 6, 12, 7, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/old",
        title="Old manual item",
        published_at=datetime(2026, 6, 10, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/in-window",
        title="In-window manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
        source_weight=1.4,
        summary="Short local note",
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
        limit=50,
    )

    assert review.database == str(db_path)
    assert review.as_of == "2026-06-12T12:00:00+00:00"
    assert review.window_start == "2026-06-11T12:00:00+00:00"
    assert review.lookback_days == 1
    assert review.total_count == 1
    assert review.row_count == 1
    assert review.matched_count == 0
    assert review.unmatched_count == 1
    assert review.source_name_counts == {"Manual Import": 1}
    assert review.latest_collected_at == "2026-06-12T09:00:00+00:00"
    assert review.items[0].title == "In-window manual item"
    assert review.items[0].source_weight == 1.4
    assert review.items[0].summary == "Short local note"
    assert review.items[0].match_status == "unmatched"
    assert review.items[0].matches == []
```

- [ ] **Step 2: Add failing tests for exact window boundaries**

Add:

```python
def test_query_imported_signals_window_excludes_start_includes_as_of_and_excludes_future(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/window-start",
        title="Window start item",
        published_at=datetime(2026, 6, 5, 12, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 5, 12, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/as-of",
        title="As-of item",
        published_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/future",
        title="Future item",
        published_at=datetime(2026, 6, 12, 12, 1, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 12, 1, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=7,
    )

    assert review.total_count == 1
    assert [item.title for item in review.items] == ["As-of item"]
```

- [ ] **Step 3: Add failing tests for ordering, source filter, limit, and missing DB**

Add:

```python
def test_query_imported_signals_orders_by_collected_at_then_id(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_id = _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/first",
        title="First item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    second_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/second",
        title="Second item",
        published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
    )

    assert [item.id for item in review.items] == [second_id, first_id]
```

```python
def test_query_imported_signals_source_filter_and_limit_zero(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    for index in range(2):
        _store_item(
            repository,
            source_name="Community Tool Export",
            url=f"https://example.com/community-{index}",
            title=f"Community item {index}",
            published_at=datetime(2026, 6, 12, 8 + index, 0, tzinfo=UTC),
            collected_at=datetime(2026, 6, 12, 9 + index, 0, tzinfo=UTC),
        )
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 11, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 13, 0, tzinfo=UTC),
        lookback_days=1,
        source_name=" Community Tool Export ",
        limit=0,
    )

    assert review.source_name == "Community Tool Export"
    assert review.limit == 0
    assert review.total_count == 2
    assert review.row_count == 0
    assert review.source_name_counts == {"Community Tool Export": 2}
    assert review.items == []
```

```python
def test_query_imported_signals_blank_source_filter_is_no_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        source_name="   ",
    )

    assert review.source_name is None
    assert review.total_count == 1
```

```python
def test_query_imported_signals_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert review.database == str(db_path)
    assert review.as_of == "2026-06-12T12:00:00+00:00"
    assert review.total_count == 0
    assert review.row_count == 0
    assert review.items == []
    assert not db_path.parent.exists()
```

```python
def test_query_imported_signals_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    _store_item(
        ItemRepository(engine),
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    engine.dispose()
    calls: list[Path] = []
    original = imported_signals_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_signals_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert calls == [db_path]
```

- [ ] **Step 4: Add failing tests for match status, match aggregation, and schema verification**

Add:

```python
def test_query_imported_signals_reads_match_status_and_unmatched_only(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    matched_id = _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/margaux",
        title="Margaux interest",
        published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="Community Tool Export",
        url="https://example.com/unmatched",
        title="Unmatched item",
        published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        matched_id,
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
                "entity_name": "Margaux",
                "entity_type": "product",
                "alias": "Margaux",
                "confidence": 0.9,
                "reason": "context",
                "context_terms": ["bag"],
            }
        ],
    )
    engine.dispose()

    full_review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
    )
    unmatched_review = query_imported_signals(
        db_path,
        as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
        lookback_days=1,
        unmatched_only=True,
    )

    assert full_review.total_count == 2
    assert full_review.matched_count == 1
    assert full_review.unmatched_count == 1
    matched = next(item for item in full_review.items if item.id == matched_id)
    assert matched.match_status == "matched"
    assert [match.model_dump() for match in matched.matches] == [
        {
            "entity_name": "The Row",
            "entity_type": "brand",
            "alias": "The Row",
            "confidence": 1.0,
        },
        {
            "entity_name": "Margaux",
            "entity_type": "product",
            "alias": "Margaux",
            "confidence": 0.9,
        }
    ]
    assert unmatched_review.total_count == 1
    assert unmatched_review.matched_count == 0
    assert unmatched_review.unmatched_count == 1
    assert unmatched_review.items[0].match_status == "unmatched"
```

```python
def test_query_imported_signals_rejects_negative_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    with pytest.raises(ValueError, match="limit must be at least 0"):
        query_imported_signals(
            db_path,
            as_of=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
            limit=-1,
        )

    assert not db_path.parent.exists()
```

```python
def test_verify_imported_signals_schema_rejects_empty_database(tmp_path: Path) -> None:
    db_path = tmp_path / "empty.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)

    with pytest.raises(RuntimeError, match="schema_metadata"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_requires_items_and_item_entities(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "broken.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )

    with pytest.raises(RuntimeError, match="item_entities, items|items, item_entities"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_missing_item_entities(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-matches.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name text not null,
                source_type text not null,
                url text not null,
                normalized_url text not null,
                title text not null,
                published_at text not null,
                source_weight real not null,
                collected_at text not null,
                summary text,
                content_hash text not null
            )
            """
        )

    with pytest.raises(RuntimeError, match="item_entities"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_missing_schema_metadata_version(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-version.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (label text)")
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name text not null,
                source_type text not null,
                url text not null,
                title text not null,
                published_at text not null,
                collected_at text not null,
                source_weight real not null,
                summary text
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name text not null,
                entity_type text not null,
                alias text not null,
                confidence real not null
            )
            """
        )

    with pytest.raises(RuntimeError, match="schema_metadata.*version"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_missing_required_item_columns(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-column.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name text not null,
                source_type text not null,
                url text not null,
                title text not null,
                published_at text not null,
                source_weight real not null,
                summary text
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name text not null,
                entity_type text not null,
                alias text not null,
                confidence real not null
            )
            """
        )

    with pytest.raises(RuntimeError, match="items.*collected_at"):
        verify_imported_signals_schema(engine)


def test_verify_imported_signals_schema_rejects_future_version(tmp_path: Path) -> None:
    db_path = tmp_path / "future.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.execute(text("update schema_metadata set version = 999"))

    with pytest.raises(RuntimeError, match="Unsupported database schema version 999"):
        verify_imported_signals_schema(engine)
```

- [ ] **Step 5: Add failing table renderer tests**

Add:

```python
def test_render_imported_signals_table_empty() -> None:
    review = ImportedSignalsReview(
        database="missing.sqlite",
        as_of="2026-06-12T12:00:00+00:00",
        window_start="2026-06-05T12:00:00+00:00",
        lookback_days=7,
    )

    assert render_imported_signals_table(review) == [
        "Imported manual signals from local SQLite.",
        "Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00",
        "Rows: 0 shown, 0 total",
        "Matches: 0 matched, 0 unmatched",
        "Sources: none",
        "No imported manual signals found.",
    ]
```

Add:

```python
def test_render_imported_signals_table_populated_sanitizes_cells() -> None:
    review = ImportedSignalsReview(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-12T12:00:00+00:00",
        window_start="2026-06-05T12:00:00+00:00",
        lookback_days=7,
        row_count=2,
        total_count=2,
        matched_count=1,
        unmatched_count=1,
        source_name_counts={"Community | Tool\nExport": 1, "Manual Import": 1},
        latest_collected_at="2026-06-12T12:00:00+00:00",
        items=[
            ImportedSignalItem(
                id=3,
                source_name="Community | Tool\nExport",
                url="https://example.com/margaux|row",
                title="Margaux |\ninterest",
                published_at="2026-06-12T09:00:00+00:00",
                collected_at="2026-06-12T12:00:00+00:00",
                source_weight=1.4,
                summary="Short local note.",
                match_status="matched",
                matches=[
                    ImportedSignalMatch(
                        entity_name="The | Row\n",
                        entity_type="brand",
                        alias="The Row",
                        confidence=1.0,
                    )
                ],
            ),
            ImportedSignalItem(
                id=2,
                source_name="Manual Import",
                url="https://example.com/le-teckel",
                title="Le Teckel bag rises",
                published_at="2026-06-12T08:00:00+00:00",
                collected_at="2026-06-12T11:00:00+00:00",
                source_weight=1.0,
                summary=None,
                match_status="unmatched",
                matches=[],
            ),
        ],
    )

    assert render_imported_signals_table(review) == [
        "Imported manual signals from local SQLite.",
        "Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00",
        "Rows: 2 shown, 2 total",
        "Matches: 1 matched, 1 unmatched",
        "Sources: Community / Tool Export=1, Manual Import=1",
        "ID | Collected At | Match | Source | Weight | Title | URL",
        "3 | 2026-06-12T12:00:00+00:00 | matched:The / Row | Community / Tool Export | 1.40 | Margaux / interest | https://example.com/margaux/row",
        "2 | 2026-06-12T11:00:00+00:00 | unmatched | Manual Import | 1.00 | Le Teckel bag rises | https://example.com/le-teckel",
    ]
```

- [ ] **Step 6: Run module tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py -q
```

Expected: fail because `fashion_radar.imported_signals` does not exist.

## Task 2: Implement Imported Signals Module

**Files:**

- Create: `src/fashion_radar/imported_signals.py`

- [ ] **Step 1: Implement Pydantic models**

Create `src/fashion_radar/imported_signals.py` with:

```python
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
```

- [ ] **Step 2: Implement schema verification**

Add:

```python
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


def _verify_columns(inspector: Any, table_name: str, required_columns: set[str]) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing = sorted(required_columns - columns)
    if missing:
        raise RuntimeError(
            f"Database schema table {table_name} is missing required columns: "
            f"{', '.join(missing)}"
        )
```

- [ ] **Step 3: Implement query entrypoint**

Add:

```python
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
```

- [ ] **Step 4: Implement SQL query helper and item builders**

Add:

```python
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
    match_exists = select(item_entities.c.id).where(
        item_entities.c.item_id == items.c.id
    ).exists()
    conditions = [
        items.c.source_type == SourceType.MANUAL_IMPORT.value,
        items.c.collected_at > window_start_value.isoformat(),
        items.c.collected_at <= as_of_value.isoformat(),
    ]
    if isinstance(source_name, str):
        conditions.append(items.c.source_name == source_name)
    if unmatched_only:
        conditions.append(~match_exists)

    item_query = select(items).where(*conditions).order_by(
        items.c.collected_at.desc(),
        items.c.id.desc(),
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


def _fetch_matches_by_item_id(connection: Any, item_ids: list[int]) -> dict[int, list[ImportedSignalMatch]]:
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
```

- [ ] **Step 5: Implement table renderer**

Add:

```python
def render_imported_signals_table(review: ImportedSignalsReview) -> list[str]:
    lines = [
        "Imported manual signals from local SQLite.",
        f"Window: {review.window_start} < collected_at <= {review.as_of}",
        f"Rows: {review.row_count} shown, {review.total_count} total",
        f"Matches: {review.matched_count} matched, {review.unmatched_count} unmatched",
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
```

Add:

```python
def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(
        f"{_table_cell(key)}={value}" for key, value in sorted(counts.items())
    )


def _format_match_cell(item: ImportedSignalItem) -> str:
    if not item.matches:
        return "unmatched"
    names = ", ".join(_table_cell(match.entity_name) for match in item.matches)
    return f"matched:{names}"


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 6: Run module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py -q
```

Expected: all module tests pass.

## Task 3: Add CLI Command

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Update the existing `tests/test_cli.py` schema import so it includes
`SCHEMA_VERSION`:

```python
from fashion_radar.db.schema import SCHEMA_VERSION, initialize_schema, item_entities, items
```

Add these tests to `tests/test_cli.py`:

```python
def test_imported_signals_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-signals", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--lookback-days" in result.output
    assert "--limit" in result.output
    assert "--source-name" in result.output
    assert "--unmatched-only" in result.output
    assert "--format" in result.output
```

```python
def test_imported_signals_command_requires_as_of(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        ["imported-signals", "--data-dir", str(data_dir)],
    )

    assert result.exit_code != 0
    assert "--as-of" in result.output
    assert not data_dir.exists()
```

```python
def test_imported_signals_command_invalid_as_of_creates_no_data_dir(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported signals: invalid --as-of" in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
```

```python
def test_imported_signals_command_invalid_as_of_skips_query_when_database_exists(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "fashion-radar.sqlite").touch()

    def fail_query(*args, **kwargs):
        raise AssertionError("query_imported_signals should not be called")

    monkeypatch.setattr(cli_module, "query_imported_signals", fail_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported signals: invalid --as-of" in result.output
    assert "query_imported_signals should not be called" not in result.output
    assert "Traceback" not in result.output
```

```python
def test_imported_signals_command_missing_database_is_read_only(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total_count"] == 0
    assert payload["row_count"] == 0
    assert not data_dir.exists()
    assert not config_dir.exists()
    assert not reports_dir.exists()
    assert not (reports_dir / "latest.md").exists()
    assert not (reports_dir / "index.json").exists()
    assert not (reports_dir / "fashion-radar-2026-06-12.eml").exists()
```

Add helper and coverage tests:

```python
def _prepare_imported_signals_cli_fixture(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    matched_id = repository.upsert_item(
        CollectedItem(
            source_name="Community Tool Export",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/margaux",
            title="Margaux interest",
            published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
            summary="Margaux appears in local notes.",
        ),
        source_weight=1.4,
        collected_at=datetime(2026, 6, 12, 9, 0, tzinfo=UTC),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Community Tool Export",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/unmatched",
            title="Unmatched local item",
            published_at=datetime(2026, 6, 12, 8, 30, tzinfo=UTC),
        ),
        collected_at=datetime(2026, 6, 12, 10, 0, tzinfo=UTC),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="Manual Import",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/old",
            title="Old local item",
            published_at=datetime(2026, 6, 10, 8, 0, tzinfo=UTC),
        ),
        collected_at=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="RSS Source",
            source_type=SourceType.RSS,
            url="https://example.com/rss",
            title="RSS item",
            published_at=datetime(2026, 6, 12, 8, 0, tzinfo=UTC),
        ),
        collected_at=datetime(2026, 6, 12, 11, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        matched_id,
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
    engine.dispose()
    return data_dir
```

```python
def test_imported_signals_command_prints_table(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual signals from local SQLite." in result.output
    assert "Window: 2026-06-11T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00" in result.output
    assert "Rows: 2 shown, 2 total" in result.output
    assert "Matches: 1 matched, 1 unmatched" in result.output
    assert "Sources: Community Tool Export=2" in result.output
    assert "Unmatched local item" in result.output
    assert "Margaux interest" in result.output
    assert "https://example.com/margaux" in result.output
    assert "Old local item" not in result.output
    assert "RSS item" not in result.output
```

```python
def test_imported_signals_command_prints_json_with_stable_keys(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--source-name",
            "Community Tool Export",
            "--limit",
            "1",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "as_of",
        "window_start",
        "lookback_days",
        "source_name",
        "unmatched_only",
        "limit",
        "row_count",
        "total_count",
        "matched_count",
        "unmatched_count",
        "source_name_counts",
        "latest_collected_at",
        "items",
    ]
    assert payload["source_name"] == "Community Tool Export"
    assert payload["limit"] == 1
    assert payload["row_count"] == 1
    assert payload["total_count"] == 2
    assert payload["matched_count"] == 1
    assert payload["unmatched_count"] == 1
    assert payload["source_name_counts"] == {"Community Tool Export": 2}
    assert payload["latest_collected_at"] == "2026-06-12T10:00:00+00:00"
    assert payload["items"][0]["title"] == "Unmatched local item"
    assert list(payload["items"][0]) == [
        "id",
        "source_name",
        "url",
        "title",
        "published_at",
        "collected_at",
        "source_weight",
        "summary",
        "match_status",
        "matches",
    ]
    assert "normalized_url" not in payload["items"][0]
    assert "content_hash" not in payload["items"][0]
```

```python
def test_imported_signals_command_json_match_keys_exclude_internal_fields(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--limit",
            "2",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    matched_item = next(
        item for item in payload["items"] if item["match_status"] == "matched"
    )
    assert list(matched_item["matches"][0]) == [
        "entity_name",
        "entity_type",
        "alias",
        "confidence",
    ]
    assert "reason" not in matched_item["matches"][0]
    assert "context_terms" not in matched_item["matches"][0]
```

```python
def test_imported_signals_command_unmatched_only(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--lookback-days",
            "1",
            "--unmatched-only",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["unmatched_only"] is True
    assert payload["total_count"] == 1
    assert payload["matched_count"] == 0
    assert payload["unmatched_count"] == 1
    assert payload["items"][0]["match_status"] == "unmatched"
    assert payload["items"][0]["matches"] == []
```

```python
def test_imported_signals_command_invalid_schema_no_traceback(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported signals" in result.output
    assert "Traceback" not in result.output
```

```python
def test_imported_signals_command_does_not_mutate_existing_database(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
    assert after_items == before_items
    assert after_matches == before_matches
```

- [ ] **Step 2: Run CLI tests and confirm failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k imported_signals
```

Expected: fail because the command does not exist.

- [ ] **Step 3: Implement CLI imports, type alias, and option**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.imported_signals import (
    query_imported_signals,
    render_imported_signals_table,
)
```

Add near the existing output format aliases:

```python
ImportedSignalsOutputFormat = Literal["table", "json"]
```

Add near the existing format options:

```python
IMPORTED_SIGNALS_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC review timestamp, for example 2026-06-12T12:00:00Z.",
)
IMPORTED_SIGNALS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

- [ ] **Step 4: Implement command**

Add:

```python
@app.command(name="imported-signals")
def imported_signals_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_SIGNALS_AS_OF_OPTION,
    lookback_days: int = typer.Option(7, min=1, help="Review window in days."),
    limit: int | None = typer.Option(50, min=0, help="Maximum imported rows to print."),
    source_name: str | None = typer.Option(None, help="Exact imported source name filter."),
    unmatched_only: bool = typer.Option(False, help="Only show rows without stored matches."),
    output_format: ImportedSignalsOutputFormat = IMPORTED_SIGNALS_FORMAT_OPTION,
) -> None:
    """Review manual imported signals already stored in local SQLite."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(f"Could not review imported signals: invalid --as-of: {exc}", err=True)
            raise typer.Exit(1) from exc

        review = query_imported_signals(
            default_database_path(data_dir),
            as_of=as_of_value,
            lookback_days=lookback_days,
            limit=limit,
            source_name=source_name,
            unmatched_only=unmatched_only,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not review imported signals: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_signals_table(review):
        typer.echo(line)
```

The JSON path intentionally uses `model_dump_json(indent=2)`. The
`ImportedSignalsReview`, `ImportedSignalItem`, and `ImportedSignalMatch` fields
remain JSON primitives, strings, dictionaries, and lists so the output contract
stays stable.

- [ ] **Step 5: Run focused CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py -q -k "imported_signals"
```

Expected: all imported-signals tests pass.

## Task 4: Update Documentation And Boundaries

**Files:**

- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Document the review command after import examples**

Keep documentation changes minimal: add command examples and explicit local
read-only boundaries only. Do not add new workflow claims, platform/community
coverage claims, ranking language, or approval/audit/legal process language.

Use examples in README, manual import docs, and community import docs:

```bash
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --unmatched-only
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

Describe the command as a read-only local SQLite review of retained
`manual_import` rows. Do not call it "last import" or imply it knows file path,
batch ID, platform, or export provenance.

- [ ] **Step 2: Update downstream workflow docs**

In `docs/candidate-discovery.md`, `docs/trend-deltas.md`, and
`docs/dashboard.md`, add one sentence that `imported-signals` can be run after
local imports to inspect retained imported rows before running candidates,
trends, reports, or dashboard review. Keep wording bounded to local retained
rows.

- [ ] **Step 3: Update architecture and boundaries**

In `docs/architecture.md` and `docs/source-boundaries.md`, state that
`imported-signals`:

- reads local SQLite only;
- verifies schema before querying existing databases;
- does not import, collect, match, score, generate reports, fetch URLs, monitor folders, or create dashboard/report artifacts;
- reports counts from retained local rows only.

- [ ] **Step 4: Update quality docs, upload checklist, and changelog**

In `docs/community-signal-quality.md`, add `imported-signals --unmatched-only`
as a post-import local review command for rows without stored matches.

In `docs/github-upload-checklist.md`, add installed-wheel smoke commands:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-signals --help
"$tmp_env/venv/bin/fashion-radar" imported-signals --data-dir "$tmp_run/data" --as-of "2026-06-12T12:00:00Z" --format json
```

In `CHANGELOG.md`, add:

```markdown
- Local read-only `imported-signals` command for reviewing retained
  `manual_import` rows and stored match status after local file imports.
```

- [ ] **Step 5: Run docs boundary scan**

Run:

```bash
rg -n "imported-signals|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|ranking|demand proof|authorization|audit|policy" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/trend-deltas.md docs/dashboard.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md CHANGELOG.md
```

Expected: hits are command examples or explicit negative boundary language.
If accidental product claims appear, remove or rewrite them before requesting
code review.

Then run the broader scope scan:

```bash
rg -n "scrap|crawl|crawler|browser|Playwright|Selenium|MCP|platform API|\\bAPI\\b|login|cookie|profile|proxy|CAPTCHA|rate-limit|bypass|watch folder|scheduler|background|approval|legal|legal-review|source export|export acquisition|coverage|monitoring" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/trend-deltas.md docs/dashboard.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md CHANGELOG.md
```

Expected: hits are existing explicit negative boundary language, local
development wording, or unrelated established docs. Any new Stage 20 wording
that suggests source acquisition, platform automation, platform coverage, or an
approval/legal workflow must be removed.

## Task 5: Claude Code Review And Release Checks

**Files:**

- Create: `docs/reviews/claude-code-stage-20-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-20-code-review.md`

- [ ] **Step 1: Create the code review prompt after implementation**

The prompt must include:

- user-visible scope;
- files changed;
- output contract;
- exact verification commands and results;
- statement that no dependencies or lockfile changed;
- statement that no source acquisition, scraping, crawling, browser automation,
  platform APIs, watch folders, schedulers, DB migrations, dashboard writes,
  reports, matching, scoring, or product-facing approval/audit/policy workflow
  features were added.

- [ ] **Step 2: Submit code review to Claude Code**

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-20-code-review-prompt.md | tee docs/reviews/claude-code-stage-20-code-review.md
```

Fix all Critical and Important findings. If fixes change code or docs, rerun
focused tests and submit a rereview prompt/result.

- [ ] **Step 3: Run release checks**

Run:

```bash
git diff --check
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py -q -k "imported_signals"
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
rm -rf /tmp/fashion-radar-dist-stage20
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage20
```

Then install the wheel into a temporary virtual environment with the Tsinghua
mirror and smoke-test:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-signals --help
"$tmp_env/venv/bin/fashion-radar" import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "2026-06-12T12:00:00Z"
"$tmp_env/venv/bin/fashion-radar" imported-signals --data-dir "$tmp_run/data" --as-of "2026-06-12T12:00:00Z" --format json
```

- [ ] **Step 4: Secret and artifact scan**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no tracked secrets and no artifact output outside ignored local
environments. Remove local caches before staging.

- [ ] **Step 5: Commit and push after approval**

Only after Claude Code code review approval, release checks, and the user's
existing authorization to upload this repository:

```bash
git add <stage-20-files>
git diff --cached --check
git commit -m "Add imported signals review command"
git push origin main
```

Keep the GitHub remote URL token-free. Use the existing repository remote. Use
a temporary `GIT_ASKPASS` only if normal push reaches authentication and fails.

## Self-Review Notes

- The plan covers every design requirement: read-only DB access, required
  `--as-of`, lookback filtering, manual-only filtering, source filtering,
  unmatched-only filtering, match-status display, deterministic JSON/table
  output, missing DB no-artifact behavior, invalid schema handling, docs, Claude
  Code review, release checks, and GitHub upload.
- The plan avoids source acquisition, scraping, crawling, browser automation,
  account automation, platform APIs, watch folders, schedulers, DB migrations,
  matching/scoring/report/dashboard writes, and product-facing approval/audit
  workflow features.
- The command reviews retained local rows. It does not claim last-import,
  platform counts, current popularity, market-wide rankings, or demand proof.
