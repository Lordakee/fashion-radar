# Stage 65 Imported Entity Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local read-only `imported-entity-evidence` command that shows retained `manual_import` rows behind one matched imported entity.

**Architecture:** Implement a focused query/render module modeled on `imported_candidate_evidence`, then wire it into the CLI, imported review workflow, first-run smoke, docs, and package checks. The query reads only local SQLite, joins `items` to `item_entities`, dedupes by item id, and emits privacy-safe evidence rows.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic models, SQLAlchemy Core, pytest, ruff, uv.

---

## File Map

- Create `src/fashion_radar/imported_entity_evidence.py`
  - Owns Pydantic evidence models, read-only query, and table renderer.
- Create `tests/test_imported_entity_evidence.py`
  - Covers query semantics, dedupe, windows, output shape, and rendering.
- Modify `src/fashion_radar/cli.py`
  - Adds output format alias, options, imports, and `imported-entity-evidence` command.
- Modify `src/fashion_radar/imported_review_workflow.py`
  - Adds `review_imported_entity_evidence` step after entity deltas.
- Modify `tests/test_cli.py`
  - Adds command help/output/error coverage.
- Modify `tests/test_imported_review_workflow.py`
  - Updates expected step count/order and command assertions.
- Modify `scripts/check_first_run_smoke.py`
  - Updates imported review workflow expected steps validator.
- Modify `tests/test_first_run_smoke.py`
  - Updates fake workflow payload and deterministic first-run assertions.
- Modify docs:
  - `README.md`
  - `docs/cli-reference.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/dashboard.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Modify `tests/test_cli_docs.py`
  - Adds docs drift checks for the new command.

## Task 1: Core Evidence Query And Renderer

**Files:**
- Create: `src/fashion_radar/imported_entity_evidence.py`
- Create: `tests/test_imported_entity_evidence.py`

- [ ] **Step 1: Write missing database test**

Add to `tests/test_imported_entity_evidence.py`:

```python
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import fashion_radar.imported_entity_evidence as imported_entity_evidence_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_entity_evidence import (
    ImportedEntityEvidenceReview,
    ImportedEntityEvidenceRow,
    query_imported_entity_evidence,
    render_imported_entity_evidence_table,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType

AS_OF = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)


def test_query_imported_entity_evidence_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert result.database == str(db_path)
    assert result.as_of == "2026-06-13T12:00:00+00:00"
    assert result.entity_name == "The Row"
    assert result.entity_type == "brand"
    assert result.current_window_start == "2026-06-06T12:00:00+00:00"
    assert result.baseline_window_start == "2026-05-30T12:00:00+00:00"
    assert result.current_days == 7
    assert result.baseline_days == 7
    assert result.source_type == "manual_import"
    assert result.source_name is None
    assert result.limit == 20
    assert result.row_count == 0
    assert result.total_count == 0
    assert result.current_mentions == 0
    assert result.baseline_mentions == 0
    assert result.distinct_sources == 0
    assert result.evidence == []
    assert not db_path.parent.exists()
```

- [ ] **Step 2: Run the new test and verify it fails**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py::test_query_imported_entity_evidence_missing_database_returns_empty_without_creating_dir -q
```

Expected: fail because `fashion_radar.imported_entity_evidence` does not exist.

- [ ] **Step 3: Create minimal models and missing DB behavior**

Create `src/fashion_radar/imported_entity_evidence.py`:

```python
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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
    return ImportedEntityEvidenceReview(**review_base)
```

- [ ] **Step 4: Verify missing DB test passes**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py::test_query_imported_entity_evidence_missing_database_returns_empty_without_creating_dir -q
```

Expected: pass.

- [ ] **Step 5: Add query behavior tests**

Append these tests and helpers to `tests/test_imported_entity_evidence.py`:

```python
def _store_item(
    repository: ItemRepository,
    *,
    title: str,
    url: str,
    source_name: str = "Community Tool Export",
    source_type: SourceType = SourceType.MANUAL_IMPORT,
    collected_at: datetime | None = None,
    summary: str = "",
) -> int:
    collected = collected_at or AS_OF
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=collected,
            summary=summary,
        ),
        collected_at=collected,
    )


def _match(entity_name: str, entity_type: str = "brand", *, alias: str | None = None):
    return {
        "entity_name": entity_name,
        "entity_type": entity_type,
        "alias": alias or entity_name,
        "confidence": 1.0,
        "reason": "keyword",
        "context_terms": [],
    }


def test_query_imported_entity_evidence_filters_manual_rows_entity_source_and_windows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_item(
        repository,
        title="The Row Margaux current",
        url="https://example.com/current",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    baseline_id = _store_item(
        repository,
        title="The Row baseline",
        url="https://example.com/baseline",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=10),
    )
    other_source_id = _store_item(
        repository,
        title="The Row other source",
        url="https://example.com/other-source",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    other_entity_id = _store_item(
        repository,
        title="Alaia current",
        url="https://example.com/alaia",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=3),
    )
    rss_id = _store_item(
        repository,
        title="The Row RSS",
        url="https://example.com/rss",
        source_name="RSS",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=4),
    )
    future_id = _store_item(
        repository,
        title="The Row future",
        url="https://example.com/future",
        source_name="Community Tool Export",
        collected_at=AS_OF + timedelta(hours=1),
    )
    old_id = _store_item(
        repository,
        title="The Row old",
        url="https://example.com/old",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=30),
    )
    repository.replace_item_matches(current_id, [_match("The Row")])
    repository.replace_item_matches(baseline_id, [_match("The Row")])
    repository.replace_item_matches(other_source_id, [_match("The Row")])
    repository.replace_item_matches(other_entity_id, [_match("Alaia")])
    repository.replace_item_matches(rss_id, [_match("The Row")])
    repository.replace_item_matches(future_id, [_match("The Row")])
    repository.replace_item_matches(old_id, [_match("The Row")])
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        source_name="Community Tool Export",
    )

    assert result.total_count == 2
    assert result.row_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.distinct_sources == 1
    assert [row.id for row in result.evidence] == [current_id, baseline_id]
    assert [row.window for row in result.evidence] == ["current", "baseline"]


def test_query_imported_entity_evidence_blank_source_name_is_no_filter(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_id = _store_item(
        repository,
        title="The Row community",
        url="https://example.com/community",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    second_id = _store_item(
        repository,
        title="The Row manual",
        url="https://example.com/manual",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    repository.replace_item_matches(first_id, [_match("The Row")])
    repository.replace_item_matches(second_id, [_match("The Row")])
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        source_name="   ",
    )

    assert result.source_name is None
    assert result.total_count == 2
    assert result.current_mentions == 2


def test_query_imported_entity_evidence_deduplicates_duplicate_matches_per_item(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = _store_item(
        repository,
        title="The Row duplicated aliases",
        url="https://example.com/duplicate",
        collected_at=AS_OF - timedelta(hours=1),
    )
    repository.replace_item_matches(
        item_id,
        [_match("The Row"), _match("The Row", alias="The Row duplicate")],
    )
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert result.total_count == 1
    assert result.current_mentions == 1
    assert [row.id for row in result.evidence] == [item_id]


def test_query_imported_entity_evidence_classifies_window_boundaries(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    baseline_start_id = _store_item(
        repository,
        title="Baseline start excluded",
        url="https://example.com/baseline-start",
        collected_at=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
    )
    current_start_id = _store_item(
        repository,
        title="Current start baseline",
        url="https://example.com/current-start",
        collected_at=datetime(2026, 6, 6, 12, 0, tzinfo=UTC),
    )
    as_of_id = _store_item(
        repository,
        title="As of current",
        url="https://example.com/as-of",
        collected_at=AS_OF,
    )
    future_id = _store_item(
        repository,
        title="Future excluded",
        url="https://example.com/future",
        collected_at=AS_OF + timedelta(minutes=1),
    )
    for item_id in (baseline_start_id, current_start_id, as_of_id, future_id):
        repository.replace_item_matches(item_id, [_match("The Row")])
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
    )

    assert [row.id for row in result.evidence] == [as_of_id, current_start_id]
    assert [row.window for row in result.evidence] == ["current", "baseline"]
```

- [ ] **Step 6: Run query behavior tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py -q
```

Expected: failures because existing implementation does not query SQLite.

- [ ] **Step 7: Implement SQLite query, dedupe, sorting, and row conversion**

Replace `src/fashion_radar/imported_entity_evidence.py` with a full implementation:

```python
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
    conditions = [
        items.c.source_type == SourceType.MANUAL_IMPORT.value,
        item_entities.c.entity_name == entity_name,
        item_entities.c.entity_type == entity_type,
    ]
    if source_name is not None:
        conditions.append(items.c.source_name == source_name)
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
        .where(*conditions)
        .order_by(items.c.id)
    )

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    rows_by_id = {}
    for row in rows:
        rows_by_id.setdefault(int(row["id"]), row)

    evidence: list[ImportedEntityEvidenceRow] = []
    for row in rows_by_id.values():
        collected_at = parse_datetime_utc(row["collected_at"])
        if not (baseline_window_start < collected_at <= as_of):
            continue
        evidence.append(
            _evidence_row(
                row,
                window=(
                    "current"
                    if current_window_start < collected_at <= as_of
                    else "baseline"
                ),
                collected_at=collected_at,
            )
        )

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
```

- [ ] **Step 8: Verify query behavior tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py -q
```

Expected: tests added so far pass.

- [ ] **Step 9: Add validation, output shape, and rendering tests**

Append:

```python
def test_query_imported_entity_evidence_limit_zero_preserves_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = _store_item(
        repository,
        title="The Row current",
        url="https://example.com/current",
        collected_at=AS_OF - timedelta(hours=1),
    )
    repository.replace_item_matches(item_id, [_match("The Row")])
    engine.dispose()

    result = query_imported_entity_evidence(
        db_path,
        as_of=AS_OF,
        entity_name="The Row",
        entity_type="brand",
        limit=0,
    )

    assert result.row_count == 0
    assert result.total_count == 1
    assert result.current_mentions == 1
    assert result.evidence == []


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"entity_name": " ", "entity_type": "brand"}, "entity name must not be blank"),
        ({"entity_name": "The Row", "entity_type": " "}, "entity type must not be blank"),
        (
            {"entity_name": "The Row", "entity_type": "brand", "current_days": 0},
            "current_days must be at least 1",
        ),
        (
            {"entity_name": "The Row", "entity_type": "brand", "baseline_days": 0},
            "baseline_days must be at least 1",
        ),
        (
            {"entity_name": "The Row", "entity_type": "brand", "limit": -1},
            "limit must be at least 0",
        ),
    ],
)
def test_query_imported_entity_evidence_rejects_invalid_inputs(
    tmp_path: Path,
    kwargs: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        query_imported_entity_evidence(tmp_path / "db.sqlite", as_of=AS_OF, **kwargs)


def test_imported_entity_evidence_json_shape_omits_match_internals() -> None:
    review = ImportedEntityEvidenceReview(
        database="db.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        entity_name="The Row",
        entity_type="brand",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
        row_count=1,
        total_count=1,
        current_mentions=1,
        distinct_sources=1,
        evidence=[
            ImportedEntityEvidenceRow(
                id=1,
                window="current",
                source_name="Community Tool Export",
                title="The Row Margaux",
                url="https://example.com/current",
                published_at="2026-06-12T12:00:00+00:00",
                collected_at="2026-06-12T13:00:00+00:00",
            )
        ],
    )
    payload = review.model_dump()

    assert list(payload) == [
        "database",
        "as_of",
        "entity_name",
        "entity_type",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "evidence",
    ]
    assert list(payload["evidence"][0]) == [
        "id",
        "window",
        "source_name",
        "title",
        "url",
        "published_at",
        "collected_at",
    ]
    assert "summary" not in payload["evidence"][0]
    assert "alias" not in payload["evidence"][0]
    assert "confidence" not in payload["evidence"][0]
    assert "context_terms" not in payload["evidence"][0]


def test_render_imported_entity_evidence_table_sanitizes_cells() -> None:
    review = ImportedEntityEvidenceReview(
        database="db.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        entity_name="The | Row",
        entity_type="brand",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-30T12:00:00+00:00",
        row_count=1,
        total_count=1,
        current_mentions=1,
        distinct_sources=1,
        evidence=[
            ImportedEntityEvidenceRow(
                id=1,
                window="current",
                source_name="Community | Tool\nExport",
                title="The Row\nMargaux | tote",
                url="https://example.com/current|x",
                published_at="2026-06-12T12:00:00+00:00",
                collected_at="2026-06-12T13:00:00+00:00",
            )
        ],
    )

    lines = render_imported_entity_evidence_table(review)

    assert lines[0] == "Imported manual entity evidence from local SQLite."
    assert "Entity: The / Row" in lines
    assert "Window | ID | Collected At | Source | Title | URL" in lines
    assert (
        "current | 1 | 2026-06-12T13:00:00+00:00 | Community / Tool Export | "
        "The Row Margaux / tote | https://example.com/current / x"
    ) in lines
```

- [ ] **Step 10: Add renderer implementation**

Append to `src/fashion_radar/imported_entity_evidence.py`:

```python
def render_imported_entity_evidence_table(review: ImportedEntityEvidenceReview) -> list[str]:
    lines = [
        "Imported manual entity evidence from local SQLite.",
        (
            "Evidence rows are retained manual_import rows whose stored matched entity "
            "equals the requested entity."
        ),
        f"Entity: {_table_cell(review.entity_name)}",
        f"Entity type: {_table_cell(review.entity_type)}",
        f"Current window: {review.current_window_start} < collected_at <= {review.as_of}",
        (
            f"Baseline window: {review.baseline_window_start} < collected_at <= "
            f"{review.current_window_start}"
        ),
        f"Source name: {_table_cell(review.source_name or 'none')}",
        f"Rows: {review.row_count} shown, {review.total_count} total",
        f"Current mentions: {review.current_mentions}",
        f"Baseline mentions: {review.baseline_mentions}",
        f"Distinct current sources: {review.distinct_sources}",
    ]
    if not review.evidence:
        lines.append("No imported manual entity evidence found.")
        return lines

    lines.append("Window | ID | Collected At | Source | Title | URL")
    for row in review.evidence:
        lines.append(
            f"{row.window} | {row.id} | {row.collected_at} | "
            f"{_table_cell(row.source_name)} | {_table_cell(row.title)} | "
            f"{_table_cell(row.url)}"
        )
    return lines


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 11: Verify all core tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py -q
```

Expected: all tests pass.

- [ ] **Step 12: Commit core module**

Run:

```bash
git add src/fashion_radar/imported_entity_evidence.py tests/test_imported_entity_evidence.py
git commit -m "Add imported entity evidence query"
```

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI help/output tests**

Add tests near `imported-candidate-evidence` CLI tests in `tests/test_cli.py`:

```python
def test_imported_entity_evidence_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-entity-evidence", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--entity-name" in result.output
    assert "--entity-type" in result.output
    assert "--source-name" in result.output
    assert "--current-days" in result.output
    assert "--baseline-days" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output


def test_imported_entity_evidence_command_prints_json(monkeypatch, tmp_path: Path) -> None:
    captured = {}

    def fake_query(db_path, **kwargs):
        captured["db_path"] = db_path
        captured["kwargs"] = kwargs
        return ImportedEntityEvidenceReview(
            database=str(db_path),
            as_of="2026-06-13T12:00:00+00:00",
            entity_name="The Row",
            entity_type="brand",
            current_window_start="2026-06-06T12:00:00+00:00",
            baseline_window_start="2026-05-30T12:00:00+00:00",
            source_name="Community Tool Export",
            row_count=1,
            total_count=1,
            current_mentions=1,
            distinct_sources=1,
            evidence=[
                ImportedEntityEvidenceRow(
                    id=1,
                    window="current",
                    source_name="Community Tool Export",
                    title="The Row Margaux",
                    url="https://example.com/current",
                    published_at="2026-06-12T12:00:00+00:00",
                    collected_at="2026-06-12T13:00:00+00:00",
                )
            ],
        )

    monkeypatch.setattr(cli_module, "query_imported_entity_evidence", fake_query)
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
            "--source-name",
            "Community Tool Export",
            "--current-days",
            "7",
            "--baseline-days",
            "7",
            "--limit",
            "20",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["entity_name"] == "The Row"
    assert payload["evidence"][0]["title"] == "The Row Margaux"
    assert captured["db_path"] == data_dir / "fashion-radar.sqlite"
    assert captured["kwargs"]["entity_name"] == "The Row"
    assert captured["kwargs"]["entity_type"] == "brand"
    assert captured["kwargs"]["source_name"] == "Community Tool Export"
    assert captured["kwargs"]["current_days"] == 7
    assert captured["kwargs"]["baseline_days"] == 7
    assert captured["kwargs"]["limit"] == 20
```

Also import the new models at the top of `tests/test_cli.py`:

```python
from fashion_radar.imported_entity_evidence import (
    ImportedEntityEvidenceReview,
    ImportedEntityEvidenceRow,
)
```

- [ ] **Step 2: Run CLI tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "imported_entity_evidence"
```

Expected: fail because command/import wiring is missing.

- [ ] **Step 3: Wire CLI imports, type alias, options, and command**

In `src/fashion_radar/cli.py`:

Add import:

```python
from fashion_radar.imported_entity_evidence import (
    query_imported_entity_evidence,
    render_imported_entity_evidence_table,
)
```

Add type alias near imported output formats:

```python
ImportedEntityEvidenceOutputFormat = Literal["table", "json"]
```

Add format option near imported evidence options:

```python
IMPORTED_ENTITY_EVIDENCE_AS_OF_OPTION = typer.Option(
    DEFAULT_IMPORTED_AS_OF,
    "--as-of",
    help="UTC timestamp for review windows.",
)
IMPORTED_ENTITY_EVIDENCE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add command before `imported-candidates` or near `imported-candidate-evidence`:

```python
@app.command(name="imported-entity-evidence")
def imported_entity_evidence_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_ENTITY_EVIDENCE_AS_OF_OPTION,
    entity_name: str = typer.Option(..., "--entity-name", help="Exact stored entity name."),
    entity_type: str = typer.Option(..., "--entity-type", help="Exact stored entity type."),
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    current_days: int = typer.Option(7, min=1, help="Current window in days."),
    baseline_days: int = typer.Option(7, min=1, help="Baseline window in days."),
    limit: int | None = typer.Option(20, min=0, help="Maximum evidence rows to print."),
    output_format: ImportedEntityEvidenceOutputFormat = IMPORTED_ENTITY_EVIDENCE_FORMAT_OPTION,
) -> None:
    """Review retained imported rows behind one matched entity."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not review imported entity evidence: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        entity_name_value = entity_name.strip()
        if not entity_name_value:
            typer.echo(
                "Could not review imported entity evidence: invalid --entity-name: "
                "entity name must not be blank",
                err=True,
            )
            raise typer.Exit(1)
        entity_type_value = entity_type.strip()
        if not entity_type_value:
            typer.echo(
                "Could not review imported entity evidence: invalid --entity-type: "
                "entity type must not be blank",
                err=True,
            )
            raise typer.Exit(1)
        review = query_imported_entity_evidence(
            default_database_path(data_dir),
            as_of=as_of_value,
            entity_name=entity_name_value,
            entity_type=entity_type_value,
            current_days=current_days,
            baseline_days=baseline_days,
            source_name=source_name,
            limit=limit,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not review imported entity evidence: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_entity_evidence_table(review):
        typer.echo(line)
```

- [ ] **Step 4: Verify help/json tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "imported_entity_evidence"
```

Expected: help/json tests pass.

- [ ] **Step 5: Add CLI table and error tests**

Add:

```python
def test_imported_entity_evidence_command_prints_table(monkeypatch, tmp_path: Path) -> None:
    def fake_query(db_path, **kwargs):
        return ImportedEntityEvidenceReview(
            database=str(db_path),
            as_of="2026-06-13T12:00:00+00:00",
            entity_name="The Row",
            entity_type="brand",
            current_window_start="2026-06-06T12:00:00+00:00",
            baseline_window_start="2026-05-30T12:00:00+00:00",
            row_count=0,
            total_count=0,
        )

    monkeypatch.setattr(cli_module, "query_imported_entity_evidence", fake_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--data-dir",
            str(tmp_path),
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual entity evidence from local SQLite." in result.output
    assert "No imported manual entity evidence found." in result.output


def test_imported_entity_evidence_command_rejects_invalid_as_of_without_query(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("query_imported_entity_evidence should not be called")
        ),
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--as-of",
            "not-a-date",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported entity evidence: invalid --as-of" in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output


@pytest.mark.parametrize(
    ("option", "value", "message"),
    [
        ("--entity-name", " ", "entity name must not be blank"),
        ("--entity-type", " ", "entity type must not be blank"),
    ],
)
def test_imported_entity_evidence_command_rejects_blank_entity_inputs_without_query(
    monkeypatch,
    option: str,
    value: str,
    message: str,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "query_imported_entity_evidence",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("query_imported_entity_evidence should not be called")
        ),
        raising=False,
    )
    args = [
        "imported-entity-evidence",
        "--entity-name",
        "The Row",
        "--entity-type",
        "brand",
    ]
    index = args.index(option) + 1
    args[index] = value

    result = CliRunner().invoke(app, args)

    assert result.exit_code == 1
    assert message in result.output
    assert "query_imported_entity_evidence should not be called" not in result.output


def test_imported_entity_evidence_command_reports_query_errors(monkeypatch) -> None:
    def fail_query(*args, **kwargs):
        raise RuntimeError("schema missing")

    monkeypatch.setattr(cli_module, "query_imported_entity_evidence", fail_query)

    result = CliRunner().invoke(
        app,
        [
            "imported-entity-evidence",
            "--entity-name",
            "The Row",
            "--entity-type",
            "brand",
        ],
    )

    assert result.exit_code == 1
    assert "Could not review imported entity evidence: schema missing" in result.output
    assert "Traceback" not in result.output
```

- [ ] **Step 6: Verify CLI tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "imported_entity_evidence"
```

Expected: all imported entity evidence CLI tests pass.

- [ ] **Step 7: Commit CLI command**

Run:

```bash
git add src/fashion_radar/cli.py tests/test_cli.py
git commit -m "Expose imported entity evidence CLI"
```

## Task 3: Imported Review Workflow And First-Run Smoke

**Files:**
- Modify: `src/fashion_radar/imported_review_workflow.py`
- Modify: `tests/test_imported_review_workflow.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update workflow tests first**

In `tests/test_imported_review_workflow.py`, update expected step names to:

```python
[
    "summarize_imported_sources",
    "refresh_stored_matches",
    "compare_imported_entities",
    "review_imported_entity_evidence",
    "review_imported_candidate_phrases",
    "review_unmatched_imported_rows",
    "review_local_heat_movers",
]
```

Add assertions:

```python
entity_evidence_step = workflow.steps[3]
assert entity_evidence_step.suggested_effect == "read_only"
assert "fashion-radar imported-entity-evidence" in entity_evidence_step.command
assert "--entity-name 'The Row'" in entity_evidence_step.command
assert "--entity-type brand" in entity_evidence_step.command
```

If source filter tests exist, assert:

```python
assert "--source-name 'Community Tool Export'" in entity_evidence_step.command
```

- [ ] **Step 2: Run workflow tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_review_workflow.py -q
```

Expected: fail because the workflow does not include the new step.

- [ ] **Step 3: Add workflow step**

In `src/fashion_radar/imported_review_workflow.py`, insert after
`compare_imported_entities`:

```python
ImportedReviewWorkflowStep(
    order=4,
    name="review_imported_entity_evidence",
    purpose="Review retained imported rows behind one matched entity.",
    command=_shell_command(
        "fashion-radar",
        "imported-entity-evidence",
        "--data-dir",
        data_text,
        "--as-of",
        as_of_text,
        "--entity-name",
        "The Row",
        "--entity-type",
        "brand",
        "--current-days",
        str(current_days),
        "--baseline-days",
        str(baseline_days),
        *source_args,
    ),
    suggested_effect="read_only",
),
```

Renumber following step orders to 5, 6, and 7.

- [ ] **Step 4: Verify workflow tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_review_workflow.py -q
```

Expected: pass.

- [ ] **Step 5: Update first-run smoke validator and fixture tests**

In `scripts/check_first_run_smoke.py`, add
`review_imported_entity_evidence` to the imported review workflow expected
steps after `compare_imported_entities`.

In `tests/test_first_run_smoke.py`, update `imported_review_workflow_payload()`
with the new step and step count. Add the command:

```python
(
    "fashion-radar imported-entity-evidence --data-dir data "
    "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' "
    "--entity-type brand --current-days 7 --baseline-days 7"
)
```

When a source-filtered fixture is used, include `--source-name`.

- [ ] **Step 6: Verify first-run tests fail if fixture is stale, then pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or first_run_flow"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: both pass after fixture and validator update.

- [ ] **Step 7: Commit workflow/smoke changes**

Run:

```bash
git add src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Add imported entity evidence review step"
```

## Task 4: Documentation And Installed-Wheel Coverage

**Files:**
- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add docs drift tests**

In `tests/test_cli_docs.py`, add `imported-entity-evidence` to the appropriate
command docs checks and add a focused test:

```python
def test_imported_entity_evidence_docs_are_linked_and_bounded() -> None:
    docs = (
        README,
        CLI_REFERENCE,
        ROOT / "docs" / "community-signal-import.md",
        ROOT / "docs" / "community-signal-quality.md",
        ROOT / "docs" / "source-boundaries.md",
        ROOT / "docs" / "architecture.md",
        ROOT / "docs" / "dashboard.md",
        UPLOAD_CHECKLIST,
        ROOT / "AGENTS.md",
        ROOT / "CHANGELOG.md",
    )
    required = (
        "imported-entity-evidence",
        "local",
        "read-only",
        "manual_import",
        "retained imported rows",
        "matched entity",
        "not platform collection",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    )
    for path in docs:
        normalized = _normalized_text(_read(path)).casefold()
        for term in required:
            assert term.casefold() in normalized, f"{path.relative_to(ROOT)} missing {term!r}"
```

- [ ] **Step 2: Run docs test and verify it fails**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_imported_entity_evidence_docs_are_linked_and_bounded -q
```

Expected: fail until docs are updated.

- [ ] **Step 3: Update docs**

Add concise documentation:

- README command block:

```bash
uv run fashion-radar imported-entity-evidence --data-dir "$PWD/data" --as-of "$AS_OF" --entity-name "The Row" --entity-type brand
uv run fashion-radar imported-entity-evidence --data-dir "$PWD/data" --as-of "$AS_OF" --entity-name "The Row" --entity-type brand --source-name "Community Tool Export" --format json
```

- README description:

```markdown
`imported-entity-evidence` is local and read-only. It opens an existing SQLite
database in read-only mode and shows retained `manual_import` rows behind one
stored matched entity. It is imported-only evidence for review, not total heat
movement, demand proof, ranking, or platform coverage verification.
```

Mirror the same language into the listed docs. In `docs/dashboard.md`, say heat
movers stay aggregate and CLI `imported-entity-evidence` is the imported-row
drilldown for one matched entity.

- [ ] **Step 4: Update upload checklist installed-wheel commands**

In `docs/github-upload-checklist.md`, add:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --data-dir "$tmp_run/data" --as-of "2026-06-13T12:00:00Z" --entity-name "The Row" --entity-type brand --format json
```

- [ ] **Step 5: Verify docs tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

Expected: pass.

- [ ] **Step 6: Commit docs**

Run:

```bash
git add README.md docs/cli-reference.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md docs/dashboard.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md tests/test_cli_docs.py
git commit -m "Document imported entity evidence drilldown"
```

## Task 5: Final Validation, Review, Push

**Files:**
- Create: `docs/reviews/opencode-stage-65-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-65-plan-review.md`
- Create: `docs/reviews/opencode-stage-65-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-65-release-review.md`

- [ ] **Step 1: Run focused validation**

Run:

```bash
uv --no-config run --frozen pytest tests/test_imported_entity_evidence.py tests/test_cli.py tests/test_imported_review_workflow.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/imported_entity_evidence.py src/fashion_radar/cli.py src/fashion_radar/imported_review_workflow.py tests/test_imported_entity_evidence.py tests/test_cli.py tests/test_imported_review_workflow.py tests/test_first_run_smoke.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/imported_entity_evidence.py src/fashion_radar/cli.py src/fashion_radar/imported_review_workflow.py tests/test_imported_entity_evidence.py tests/test_cli.py tests/test_imported_review_workflow.py tests/test_first_run_smoke.py tests/test_cli_docs.py
```

- [ ] **Step 2: Run full local validation**

Run:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

- [ ] **Step 3: Run package validation**

Run:

```bash
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
python3 scripts/check_package_archives.py "$tmp_build"
uv --no-config venv "$tmp_env/venv"
uv --no-config pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-entity-evidence --data-dir "$tmp_env/data" --as-of 2026-06-13T12:00:00Z --entity-name "The Row" --entity-type brand --format json | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
```

- [ ] **Step 4: Run release scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]{20,}" .
rg -n "mirrors|tuna|aliyun|ustc|pypi.tuna|pypi.mirrors|index-url" uv.lock
git diff --check
```

Expected: token/mirror searches return no matches; `git diff --check` exits 0.

- [ ] **Step 5: Request local opencode release review**

Write a concise release-review prompt that asks local `opencode` with
`zhipuai-coding-plan/glm-5.2`, variant `max`, to review the current Stage 65
diff for Critical/Important issues only. The prompt must state:

- command is local/read-only/imported-only
- no platform collection/scraping/API/browser/cookie/media behavior
- no raw summaries, aliases, confidence, context terms, or source file paths in
  output
- duplicate matches dedupe by item id
- docs and first-run smoke updated

Run:

```bash
UV_NO_CONFIG=1 opencode run --dir /home/ubuntu/fashion-radar --model zhipuai-coding-plan/glm-5.2 --variant max "$(cat docs/reviews/opencode-stage-65-release-review-prompt.md)" | tee docs/reviews/opencode-stage-65-release-review.md
```

If opencode times out before a verdict, record the timeout honestly and fix any
concrete findings it emitted before timeout.

- [ ] **Step 6: Commit final Stage 65 changes**

Run:

```bash
git status -sb
git add .
git commit -m "Add imported entity evidence drilldown"
```

- [ ] **Step 7: Push and poll CI**

Try:

```bash
GIT_TERMINAL_PROMPT=0 git push origin main
```

If git transport fails, push with the GitHub Git Data API without writing the
token into remote URLs or files. Then fetch `origin/main`, align local branch if
the API-created commit SHA differs but the tree matches, and poll Actions for
the pushed head SHA.

End the node with a Handoff Summary containing repo status, verified commands,
uncommitted files, and next step.

## Self-Review Checklist

- Spec coverage: Tasks cover core query, CLI, workflow, first-run smoke, docs,
  review, validation, commit, push, and CI.
- Incomplete-work scan: No `TODO`, `TBD`, or unspecified implementation steps.
- Type consistency: Models, function names, and CLI command names consistently
  use `ImportedEntityEvidence*` and `imported-entity-evidence`.
- Scope check: No scraping, connector, browser automation, scheduling, ranking,
  demand proof, dashboard browser, schema migration, or compliance-review
  feature is included.
