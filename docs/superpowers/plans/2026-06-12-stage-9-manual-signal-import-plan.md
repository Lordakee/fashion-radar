# Stage 9 Manual Signal Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe local CSV/JSON import command for user-provided fashion signal rows so local files the user already has permission to process can enter the existing matching, candidate discovery, report, and dashboard workflows.

**Architecture:** Add a focused importer module with two explicit phases: `load_manual_signal_rows()` parses and validates normalized CSV/JSON files without opening any database path, then `store_manual_signal_rows()` persists already validated rows with the existing item repository upsert semantics. The importer adds a provenance-only `manual_import` source type that is rejected in source configuration, with no schema migration, no collector, and no network behavior.

**Tech Stack:** Python 3.11+, standard library `csv`/`json`, Pydantic validation, Typer CLI, SQLAlchemy-backed existing repository, pytest, ruff, uv.

---

## Scope Guard

Stage 9 must not add platform search, crawlers, scrapers, browser automation,
Playwright, MCP scraping servers, account automation, login cookies,
account/session files, proxy pools, fingerprint evasion, CAPTCHA bypass,
access-control bypass, paywall bypass, private data collection, paid API
requirements, LLM calls, embeddings, vector databases, image recognition, or
media download workflows.

The importer only reads a local user-provided CSV/JSON file and writes
sanitized item metadata into the local SQLite database.

`manual_import` is import-only. It must not be accepted in `sources.yaml`, added
to source packs, included in source health, or wired into collector execution.

Atomicity in Stage 9 means validation atomicity: malformed files fail before any
database write path opens. `store_manual_signal_rows()` may still use existing
per-row `ItemRepository.upsert_item()` transactions after validation succeeds;
full runtime batch rollback is out of scope for this stage.

Stage 9 atomicity means validation atomicity: validation errors are detected
before any database path is opened, so malformed files write nothing and do not
create `data_dir`. Full transaction rollback for mid-write database/runtime
failures is out of scope for this stage.

Codex subagents must use `reasoning_effort: "xhigh"`. Claude Code review must
use `--effort max`.

## Files

- Create: `src/fashion_radar/importers/__init__.py`
- Create: `src/fashion_radar/importers/manual_signals.py`
- Modify: `src/fashion_radar/models/source.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Create: `tests/test_manual_signal_import.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_dashboard.py`
- Create: `docs/manual-signal-import.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/dashboard.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
- Create after implementation: `docs/reviews/claude-code-stage-9-code-review-prompt.md`
- Create after code review: `docs/reviews/claude-code-stage-9-code-review.md`

## Public Interfaces

New source type:

```python
class SourceType(StrEnum):
    RSS = "rss"
    RSSHUB = "rsshub"
    GDELT = "gdelt"
    MANUAL_IMPORT = "manual_import"
```

New CLI:

```bash
fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
fashion-radar import-signals ./signals.json --format json --source-name "Manual Export"
fashion-radar import-signals ./signals.csv --dry-run
```

Input fields:

- Required: `url`, `title`, `published_at`
- Optional: `summary`, `source_name`, `platform`, `source_weight`, `collected_at`

`platform` is a short provenance label only. It is not stored separately and
must not imply complete platform coverage. It is accepted to tolerate varied
local files and discarded after validation.

The command-level `--source-name` is stripped before use. An empty or
all-whitespace value falls back to `Manual Import`.

The local item table has one row per normalized URL. Stage 9 intentionally keeps
the existing upsert behavior: importing a row with an existing URL updates that
item and does not create a duplicate. CLI output reports rows imported and new
items added separately. The new-item count is a local single-process CLI count
intended for normal local use.

## Task 1: Claude Code Plan Gate

- [ ] Create `docs/reviews/claude-code-stage-9-plan-review-prompt.md` with the Stage 9 goal, architecture, tech stack, implementation method, tests, docs, explicit read-only review instruction, and explicit out-of-scope boundaries.
- [ ] Run:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-9-plan-review-prompt.md
```

- [ ] Save the review to `docs/reviews/claude-code-stage-9-plan-review.md`.
- [ ] Fix every Critical and Important finding before Task 2.

## Task 2: Manual Import Source Type

**Files:**

- Modify: `src/fashion_radar/models/source.py`
- Modify: `tests/test_models.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_workflows.py`

- [ ] Add failing model tests:

```python
import pytest
from pydantic import ValidationError

from fashion_radar.models.source import SourceDefinition, SourceType


def test_manual_import_source_type_exists() -> None:
    assert SourceType.MANUAL_IMPORT.value == "manual_import"


def test_manual_import_is_rejected_in_source_config() -> None:
    with pytest.raises(ValidationError, match="manual_import is import-only"):
        SourceDefinition(name="Manual Export", type=SourceType.MANUAL_IMPORT)
```

- [ ] Add failing config-loader test in `tests/test_config.py`:

```python
def test_source_config_rejects_manual_import_source_type(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Manual Export
            type: manual_import
        """,
    )

    with pytest.raises(ConfigError, match="manual_import is import-only"):
        load_source_config(path)
```

- [ ] Add collector-dispatch guard test in `tests/test_workflows.py`:

```python
from fashion_radar.models.source import SourceType
from fashion_radar.workflows import _default_collectors


def test_manual_import_is_not_a_default_collector() -> None:
    collectors = _default_collectors()

    assert SourceType.MANUAL_IMPORT not in collectors
    assert SourceType.MANUAL_IMPORT.value not in collectors
```

- [ ] Run:

```bash
.venv/bin/python -m pytest \
  tests/test_models.py::test_manual_import_source_type_exists \
  tests/test_models.py::test_manual_import_is_rejected_in_source_config \
  tests/test_config.py::test_source_config_rejects_manual_import_source_type \
  tests/test_workflows.py::test_manual_import_is_not_a_default_collector \
  -q
```

Expected: fails because `MANUAL_IMPORT` does not exist.

- [ ] Add `MANUAL_IMPORT = "manual_import"` to `SourceType`.
- [ ] Add this branch to `SourceDefinition.validate_source_target()` before the
  RSS/RSSHUB/GDELT checks:

```python
if self.type == SourceType.MANUAL_IMPORT:
    raise ValueError("manual_import is import-only; use fashion-radar import-signals")
```
- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_models.py tests/test_config.py tests/test_workflows.py -q
.venv/bin/python -m ruff check src/fashion_radar/models/source.py tests/test_models.py tests/test_config.py tests/test_workflows.py
```

Expected: passes.

## Task 3: Parser And Validator

**Files:**

- Create: `src/fashion_radar/importers/__init__.py`
- Create: `src/fashion_radar/importers/manual_signals.py`
- Create: `tests/test_manual_signal_import.py`

- [ ] Add parser tests:

```python
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fashion_radar.importers.manual_signals import (
    ManualSignalImportError,
    load_manual_signal_rows,
)


def test_loads_manual_signal_csv_rows(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,platform,source_weight\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,Short note,Manual Export,manual,1.4\n",
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Fallback")

    assert len(rows) == 1
    assert rows[0].url == "https://example.com/a"
    assert rows[0].title == "Le Teckel bag"
    assert rows[0].summary == "Short note"
    assert rows[0].source_name == "Manual Export"
    assert rows[0].source_weight == 1.4
    assert rows[0].published_at == datetime(2026, 6, 12, 8, 0, tzinfo=UTC)


def test_loads_manual_signal_json_items_object(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "url": "https://example.com/b",
                        "title": "Mary Jane flats",
                        "published_at": "2026-06-12T09:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert rows[0].source_name == "Manual Import"
    assert rows[0].summary is None


def test_loads_manual_signal_json_top_level_list(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/list",
                    "title": "East-west tote",
                    "published_at": "2026-06-12T09:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert len(rows) == 1
    assert rows[0].url == "https://example.com/list"


def test_manual_signal_import_normalizes_collected_at_to_utc(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/d",
                    "title": "Suede sneakers",
                    "published_at": "2026-06-12T09:00:00+02:00",
                    "collected_at": "2026-06-12T13:30:00+02:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert rows[0].published_at == datetime(2026, 6, 12, 7, 0, tzinfo=UTC)
    assert rows[0].collected_at == datetime(2026, 6, 12, 11, 30, tzinfo=UTC)


def test_manual_signal_import_rejects_invalid_rows_atomically(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Valid,2026-06-12T08:00:00Z\n"
        ",Missing URL,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 3"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_manual_signal_import_ignores_private_extra_fields(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/c",
                    "title": "Mesh flats",
                    "published_at": "2026-06-12T09:00:00Z",
                    "author_handle": "@private",
                    "raw_comment": "do not store",
                    "account_id": "secret",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert rows[0].model_dump() == {
        "url": "https://example.com/c",
        "title": "Mesh flats",
        "published_at": rows[0].published_at,
        "summary": None,
        "source_name": "Manual Import",
        "platform": None,
        "source_weight": 1.0,
        "collected_at": None,
    }


def test_manual_signal_import_ignores_unknown_csv_columns(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,author_handle,raw_comment,account_id\n"
        "https://example.com/e,Mesh flats,2026-06-12T09:00:00Z,@private,do not store,secret\n",
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    assert rows[0].model_dump().keys() == {
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    }


def test_manual_signal_import_normalizes_blank_optional_csv_values(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,platform,source_name,source_weight,collected_at\n"
        'https://example.com/f,Boat shoes,2026-06-12T09:00:00Z," "," "," "," "," "\n',
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    assert rows[0].summary is None
    assert rows[0].platform is None
    assert rows[0].source_name == "Manual Import"
    assert rows[0].source_weight == 1.0
    assert rows[0].collected_at is None


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ({}, "JSON import must be a list or an object with an items list"),
        ({"items": {}}, "JSON import must be a list or an object with an items list"),
        ([1], "row 1"),
    ],
)
def test_manual_signal_import_rejects_invalid_json_shapes(
    tmp_path: Path,
    payload: object,
    match: str,
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match=match):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


def test_manual_signal_import_rejects_empty_csv_without_headers(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match="CSV file must contain headers"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_manual_signal_import_allows_empty_csv_with_headers(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("url,title,published_at\n", encoding="utf-8")

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    assert rows == []


def test_manual_signal_import_rejects_csv_rows_with_extra_cells(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Valid,2026-06-12T08:00:00Z,unexpected\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 2"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_manual_signal_import_normalizes_blank_default_source_name(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Valid,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name=" ")

    assert rows[0].source_name == "Manual Import"


@pytest.mark.parametrize(
    "row",
    [
        {"url": "https://example.com/g", "published_at": "2026-06-12T09:00:00Z"},
        {"url": "https://example.com/g", "title": "", "published_at": "2026-06-12T09:00:00Z"},
        {"url": "https://example.com/g", "title": "No date"},
        {"url": "https://example.com/g", "title": "Blank date", "published_at": " "},
    ],
)
def test_manual_signal_import_rejects_missing_or_blank_required_fields(
    tmp_path: Path,
    row: dict[str, str],
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(json.dumps([row]), encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match="row 1"):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


@pytest.mark.parametrize(
    "row",
    [
        {
            "url": "https://example.com/h",
            "title": "Bad published date",
            "published_at": "not-a-date",
        },
        {
            "url": "https://example.com/h",
            "title": "Bad collected date",
            "published_at": "2026-06-12T09:00:00Z",
            "collected_at": "not-a-date",
        },
    ],
)
def test_manual_signal_import_rejects_invalid_dates(
    tmp_path: Path,
    row: dict[str, str],
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(json.dumps([row]), encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match="row 1"):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


@pytest.mark.parametrize("source_weight", ["0", "-0.1", "5.1", "not-a-number"])
def test_manual_signal_import_rejects_invalid_source_weight(
    tmp_path: Path,
    source_weight: str,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,source_weight\n"
        f"https://example.com/i,Invalid weight,2026-06-12T09:00:00Z,{source_weight}\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 2"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q
```

Expected: fails because importer module does not exist.

- [ ] Implement `src/fashion_radar/importers/__init__.py`:

```python
"""Local importers for user-provided Fashion Radar data."""
```

- [ ] Implement `src/fashion_radar/importers/manual_signals.py`:

```python
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from fashion_radar.utils.dates import parse_datetime_utc

ManualSignalFormat = Literal["csv", "json"]


class ManualSignalImportError(ValueError):
    """Raised when a manual signal import file cannot be parsed or validated."""


class ManualSignalRow(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: str
    title: str
    published_at: datetime
    summary: str | None = None
    source_name: str
    platform: str | None = None
    source_weight: float = Field(default=1.0, gt=0, le=5)
    collected_at: datetime | None = None

    @field_validator("url", "title", "source_name")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not str(value).strip():
            raise ValueError("field cannot be empty")
        return str(value).strip()

    @field_validator("summary", "platform", mode="before")
    @classmethod
    def blank_optional_to_none(cls, value: object) -> object | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("source_weight", mode="before")
    @classmethod
    def blank_source_weight_to_default(cls, value: object) -> object:
        if value is None or not str(value).strip():
            return 1.0
        return value

    @field_validator("published_at", mode="before")
    @classmethod
    def normalize_published_at(cls, value: object) -> datetime:
        return parse_datetime_utc(value)

    @field_validator("collected_at", mode="before")
    @classmethod
    def normalize_collected_at(cls, value: object | None) -> datetime | None:
        if value is None or not str(value).strip():
            return None
        return parse_datetime_utc(value)


def load_manual_signal_rows(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    default_source_name: str,
) -> list[ManualSignalRow]:
    raw_rows = _read_raw_rows(path, input_format=input_format)
    fallback_source_name = default_source_name.strip() or "Manual Import"
    rows = []
    for index, raw in enumerate(raw_rows, start=2 if input_format == "csv" else 1):
        if not isinstance(raw, dict):
            raise ManualSignalImportError(f"row {index}: row must be an object")
        if None in raw:
            raise ManualSignalImportError(f"row {index}: CSV row has more cells than headers")
        candidate = {**raw}
        if not str(candidate.get("source_name") or "").strip():
            candidate["source_name"] = fallback_source_name
        try:
            rows.append(ManualSignalRow.model_validate(candidate))
        except (ValidationError, ValueError) as exc:
            raise ManualSignalImportError(f"row {index}: {exc}") from exc
    return rows


def _read_raw_rows(path: Path, *, input_format: ManualSignalFormat) -> list[dict[str, object]]:
    try:
        if input_format == "csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    raise ManualSignalImportError("CSV file must contain headers")
                return [dict(row) for row in reader]
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManualSignalImportError(f"Could not read import file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ManualSignalImportError(f"Invalid JSON in {path}: {exc}") from exc

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ManualSignalImportError("JSON import must be a list or an object with an items list")
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q
.venv/bin/python -m ruff check src/fashion_radar/importers tests/test_manual_signal_import.py
```

Expected: passes.

## Task 4: Store Validated Manual Signal Rows

**Files:**

- Modify: `src/fashion_radar/importers/manual_signals.py`
- Modify: `tests/test_manual_signal_import.py`

- [ ] Add workflow tests:

```python
from datetime import UTC, datetime

from sqlalchemy import func, select

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import collector_runs, initialize_schema, source_health
from fashion_radar.importers.manual_signals import (
    load_manual_signal_rows,
    store_manual_signal_rows,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType


def test_store_manual_signal_rows_writes_sanitized_items(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,source_weight,collected_at,"
        "platform,author_handle,raw_comment,account_id\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,Short note,"
        "Manual Export,1.4,2026-06-12T10:00:00Z,manual,@private,do not store,secret\n"
        "https://example.com/b,Mary Jane flats,2026-06-12T09:00:00Z,, , , ,"
        "manual,@private,do not store,secret\n",
        encoding="utf-8",
    )
    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Fallback Export")

    result = store_manual_signal_rows(
        engine,
        rows=rows,
        imported_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert result.rows_seen == 2
    assert result.rows_imported == 2
    assert result.items_added == 2

    repository = ItemRepository(engine)
    first = repository.get_item(1)
    second = repository.get_item(2)
    assert first["source_type"] == "manual_import"
    assert first["source_name"] == "Manual Export"
    assert first["source_weight"] == 1.4
    assert first["summary"] == "Short note"
    assert first["collected_at"] == "2026-06-12T10:00:00+00:00"
    assert second["source_type"] == "manual_import"
    assert second["source_name"] == "Fallback Export"
    assert second["source_weight"] == 1.0
    assert second["summary"] is None
    assert second["collected_at"] == "2026-06-12T12:00:00+00:00"
    assert "platform" not in first
    assert "author_handle" not in first
    assert "raw_comment" not in first
    assert "account_id" not in first
    with engine.connect() as connection:
        collector_run_count = connection.execute(
            select(func.count()).select_from(collector_runs)
        ).scalar_one()
        source_health_count = connection.execute(
            select(func.count()).select_from(source_health)
        ).scalar_one()
    assert collector_run_count == 0
    assert source_health_count == 0


def test_store_manual_signal_rows_preserves_existing_normalized_url_upsert(
    tmp_path: Path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    existing_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue",
            source_type=SourceType.RSS,
            url="https://example.com/a?utm_source=newsletter",
            title="Original coverage",
            published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
            summary="Original summary",
        ),
        source_weight=1.2,
        collected_at=datetime(2026, 6, 11, 9, 0, tzinfo=UTC),
    )
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,source_weight\n"
        "https://example.com/a,Manual update,2026-06-12T08:00:00Z,Manual summary,Manual Export,1.4\n",
        encoding="utf-8",
    )
    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    result = store_manual_signal_rows(
        engine,
        rows=rows,
        imported_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert result.rows_seen == 1
    assert result.rows_imported == 1
    assert result.items_added == 0
    assert repository.count_items() == 1
    item = repository.get_item(existing_id)
    assert item["source_type"] == "manual_import"
    assert item["source_name"] == "Manual Export"
    assert item["title"] == "Manual update"
```

- [ ] Implement:

```python
from datetime import datetime

from sqlalchemy.engine import Engine

from fashion_radar.db.repositories import ItemRepository
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType


class ManualSignalImportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rows_seen: int
    rows_imported: int
    items_added: int


def store_manual_signal_rows(
    engine: Engine,
    *,
    rows: list[ManualSignalRow],
    imported_at: datetime,
) -> ManualSignalImportResult:
    repository = ItemRepository(engine)
    before_count = repository.count_items()
    imported_at_utc = parse_datetime_utc(imported_at)
    for row in rows:
        repository.upsert_item(
            CollectedItem(
                source_name=row.source_name,
                source_type=SourceType.MANUAL_IMPORT,
                url=row.url,
                title=row.title,
                published_at=row.published_at,
                summary=row.summary,
            ),
            source_weight=row.source_weight,
            collected_at=row.collected_at or imported_at_utc,
        )
    after_count = repository.count_items()
    return ManualSignalImportResult(
        rows_seen=len(rows),
        rows_imported=len(rows),
        items_added=max(0, after_count - before_count),
    )
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q
.venv/bin/python -m ruff check src/fashion_radar/importers tests/test_manual_signal_import.py
```

Expected: passes.

## Task 5: CLI Command

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] Add CLI tests:

```python
def test_import_signals_command_imports_csv(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,platform,author_handle,raw_comment,account_id\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,Short note,"
        "manual,@private,do not store,secret\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Manual Export",
            "--imported-at",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Validated 1 manual signal rows" in result.output
    assert "Imported 1 manual signal rows" in result.output
    database_path = data_dir / "fashion-radar.sqlite"
    assert database_path.exists()
    engine = create_sqlite_engine(database_path)
    item = ItemRepository(engine).get_item(1)
    assert item["source_type"] == "manual_import"
    assert item["source_name"] == "Manual Export"
    assert item["summary"] == "Short note"
    assert "platform" not in item
    assert "author_handle" not in item
    assert "raw_comment" not in item
    assert "account_id" not in item


def test_import_signals_command_imports_json(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/json",
                    "title": "East-west tote",
                    "published_at": "2026-06-12T08:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "json",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Manual JSON Export",
        ],
    )

    assert result.exit_code == 0
    assert "Imported 1 manual signal rows" in result.output
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    item = ItemRepository(engine).get_item(1)
    assert item["source_type"] == "manual_import"
    assert item["source_name"] == "Manual JSON Export"


def test_import_signals_command_dry_run_writes_nothing(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Dry run: no rows imported" in result.output
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_import_signals_command_rejects_invalid_file_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Valid,2026-06-12T08:00:00Z\n"
        ",Missing URL,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Could not import signals: row 3" in result.output
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_import_signals_command_rejects_invalid_imported_at(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--imported-at",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not import signals: invalid --imported-at" in result.output
    assert not data_dir.exists()


def test_import_signals_command_rejects_unsupported_format_before_data_dir_creation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    path = tmp_path / "signals.xml"
    path.write_text("<signals />", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            "xml",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code != 0
    assert not data_dir.exists()
```

- [ ] Implement command:

```python
from datetime import UTC, datetime

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import initialize_schema
from fashion_radar.importers.manual_signals import (
    ManualSignalImportError,
    load_manual_signal_rows,
    store_manual_signal_rows,
)
from fashion_radar.utils.dates import parse_datetime_utc

ManualSignalInputFormat = Literal["csv", "json"]


@app.command(name="import-signals")
def import_signals_command(
    path: Path,
    data_dir: Path = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = typer.Option("csv", "--format"),
    source_name: str = typer.Option("Manual Import", help="Fallback source name."),
    imported_at: str | None = typer.Option(None, help="UTC import timestamp override."),
    dry_run: bool = typer.Option(False, help="Validate without writing rows."),
) -> None:
    """Import user-provided local signal rows from CSV or JSON."""
    source_name_value = source_name.strip() or "Manual Import"
    try:
        try:
            if imported_at is not None:
                imported_at_value = parse_datetime_utc(imported_at)
            else:
                imported_at_value = datetime.now(UTC)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not import signals: invalid --imported-at: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc

        rows = load_manual_signal_rows(
            path,
            input_format=input_format,
            default_source_name=source_name_value,
        )

        if dry_run:
            typer.echo(f"Validated {len(rows)} manual signal rows")
            typer.echo("Dry run: no rows imported")
            return

        engine = create_sqlite_engine(default_database_path(data_dir))
        initialize_schema(engine)
        result = store_manual_signal_rows(
            engine,
            rows=rows,
            imported_at=imported_at_value,
        )
    except ManualSignalImportError as exc:
        typer.echo(f"Could not import signals: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Validated {result.rows_seen} manual signal rows")
    typer.echo(f"Imported {result.rows_imported} manual signal rows")
    typer.echo(f"Items added: {result.items_added}")
```

Implementation requirements:

- Normalize `source_name` with `source_name.strip() or "Manual Import"`.
- Parse `imported_at` before creating the engine; use it if provided, otherwise
  current UTC time. Dry-run validates this option too, so
  `--dry-run --imported-at not-a-date` exits non-zero without creating
  `data_dir`.
- Call `load_manual_signal_rows()` before creating the engine, initializing
  schema, or creating `data_dir`.
- If `dry_run` is true, print the validation count and
  `Dry run: no rows imported`, then return without creating the engine,
  initializing schema, or creating `data_dir`.
- For real imports after validation succeeds, create engine with
  `create_sqlite_engine(default_database_path(data_dir))`.
- For real imports after validation succeeds, call `initialize_schema(engine)`
  because this is an explicit write command.
- Catch `ManualSignalImportError` and print `Could not import signals: ...`.
- Do not load source config or call collectors.
- Do not call network code.

- [ ] Run:

```bash
.venv/bin/python -m pytest \
  tests/test_cli.py::test_import_signals_command_imports_csv \
  tests/test_cli.py::test_import_signals_command_imports_json \
  tests/test_cli.py::test_import_signals_command_dry_run_writes_nothing \
  tests/test_cli.py::test_import_signals_command_rejects_invalid_file_before_data_dir_creation \
  tests/test_cli.py::test_import_signals_command_rejects_invalid_imported_at \
  tests/test_cli.py::test_import_signals_command_rejects_unsupported_format_before_data_dir_creation \
  -q
.venv/bin/python -m ruff check src/fashion_radar/cli.py tests/test_cli.py
```

Expected: passes.

## Task 6: Report, Dashboard, And Docs Wording

**Files:**

- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_dashboard.py`
- Create: `docs/manual-signal-import.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/scoring.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

- [ ] Update report candidate wording in `src/fashion_radar/reports.py`:

```python
"This candidate signal is an observed phrase from configured sources and "
"imported local signals and needs review."
```

- [ ] Update `tests/test_reports.py` candidate assertion:

```python
assert "from configured sources and imported local signals" in markdown.lower()
```

- [ ] Add a dashboard caption constant and use it in `src/fashion_radar/dashboard/app.py`:

```python
CANDIDATE_SIGNAL_CAPTION = (
    "Candidate signals are observed phrases from configured sources and "
    "imported local signals and need review."
)
```

Replace the candidate-tab `st.caption(...)` call with:

```python
st.caption(CANDIDATE_SIGNAL_CAPTION)
```

- [ ] Update `tests/test_dashboard.py` import and assertion:

```python
from fashion_radar.dashboard.app import CANDIDATE_SIGNAL_CAPTION, parse_args


def test_dashboard_candidate_caption_mentions_imported_local_signals() -> None:
    assert "configured sources and imported local signals" in CANDIDATE_SIGNAL_CAPTION
    assert "complete platform coverage" not in CANDIDATE_SIGNAL_CAPTION.lower()
```

- [ ] Create `docs/manual-signal-import.md` covering:
  - The feature imports user-provided local CSV/JSON files.
  - The tool does not collect from platforms.
  - Required and optional fields.
  - CSV and JSON examples.
  - `--dry-run`.
  - Follow-up commands: `match`, `report`, `candidates`.
  - Fashion Radar does not provide instructions for obtaining exports from
    social platforms; users are responsible for using only data they are
    authorized to process.
  - Privacy boundary: do not import private comments, account IDs, cookies,
    author profiles, follower lists, images, or videos.
- [ ] Update README quickstart with a short import example:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
```

- [ ] Update source-boundary docs to call manual import a local input path, not
  a connector or platform collector.
- [ ] Update README, `docs/dashboard.md`, `docs/candidate-discovery.md`,
  `docs/scoring.md`, and `docs/architecture.md` so candidate signals are framed
  as observed phrases from configured sources and imported local signals, not
  complete platform coverage.
- [ ] Run claim/safety grep:

```bash
rg -n "(scrape|crawler|cookie|proxy|CAPTCHA|fingerprint|bypass|account pool|login automation|full platform|viral|globally trending|market-wide trend|confirmed brand|confirmed product)" \
  README.md docs/manual-signal-import.md docs/architecture.md docs/source-boundaries.md docs/dashboard.md docs/candidate-discovery.md docs/scoring.md CHANGELOG.md src/fashion_radar/cli.py src/fashion_radar/reports.py src/fashion_radar/dashboard/app.py
```

Expected: manually classify every match. Allowed matches must be negative
boundary wording that explicitly says the tool does not do the behavior.
Unsafe claims or instructions must be removed before continuing.

## Task 7: Full Verification And Claude Code Code Review

- [ ] Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check
uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

- [ ] Run package smoke:

```bash
rm -rf /tmp/fashion-radar-dist-stage9
uv build --out-dir /tmp/fashion-radar-dist-stage9
tmpdir="$(mktemp -d)"
uv venv "$tmpdir/venv"
wheel="$(find /tmp/fashion-radar-dist-stage9 -maxdepth 1 -name 'fashion_radar-*.whl' | sort | tail -n 1)"
test -n "$wheel"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmpdir/venv/bin/python" "$wheel"
"$tmpdir/venv/bin/fashion-radar" import-signals --help
printf 'url,title,published_at\nhttps://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z\n' > "$tmpdir/signals.csv"
"$tmpdir/venv/bin/fashion-radar" import-signals "$tmpdir/signals.csv" --format csv --dry-run --data-dir "$tmpdir/data"
test ! -e "$tmpdir/data"
printf 'url,title,published_at\n,Missing URL,2026-06-12T08:00:00Z\n' > "$tmpdir/invalid-signals.csv"
if "$tmpdir/venv/bin/fashion-radar" import-signals "$tmpdir/invalid-signals.csv" --format csv --data-dir "$tmpdir/invalid-data"; then
  exit 1
fi
test ! -e "$tmpdir/invalid-data"
```

- [ ] Check CodeGraph:

```bash
# MCP tool: codegraph_status(projectPath="/home/ubuntu/fashion-radar")
```

- [ ] Create `docs/reviews/claude-code-stage-9-code-review-prompt.md`.
- [ ] Run:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-9-code-review-prompt.md
```

- [ ] Save to `docs/reviews/claude-code-stage-9-code-review.md`.
- [ ] Fix every Critical and Important finding.
- [ ] Commit with explicit file list.
- [ ] Sync to GitHub. If Git smart HTTP still fails, use the GitHub Git
  Database API only after verifying it can preserve remote `main` safely.

## Acceptance Criteria

- `fashion-radar import-signals` imports valid local CSV/JSON rows into SQLite.
- Invalid import files fail atomically without partial writes.
- `--dry-run` validates without writing rows.
- Imported rows use `source_type = "manual_import"`.
- Imported rows can be matched, reported, surfaced as candidates, and viewed in
  dashboard summaries through existing workflows.
- No scraping, crawler, browser automation, account automation, cookie, proxy,
  CAPTCHA/access-control bypass, private data collection, paid API, LLM,
  embedding, vector database, image/video storage, or media download behavior is
  added.
- Public docs frame imported data as user-provided local signals, not complete
  platform coverage.
- Full verification passes.
- Final Claude Code review has no unfixed Critical or Important findings.
