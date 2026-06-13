# Stage 25 Imported Candidates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar imported-candidates`, a local read-only command that surfaces candidate phrases from retained `manual_import` rows only.

**Architecture:** Extend existing candidate discovery with optional source filters that default to no filtering, preserving reports, trends, dashboard, and the existing `candidates` command. Add a focused `src/fashion_radar/imported_candidates.py` wrapper that opens SQLite read-only, reuses imported schema verification, calls filtered candidate discovery, and renders stable table/JSON output. Add a thin Typer command in `src/fashion_radar/cli.py` plus docs and release checks.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, pytest, ruff, uv.

---

## Process Gate

Implementation may start only after Claude Code approves this Stage 25 plan
review and every Critical or Important plan-review finding is resolved. After
implementation, Stage 25 code must be submitted to Claude Code for code review
before commit and push.

Do not include the existing uncommitted `uv.lock` mirror-url change in any
Stage 25 commit.

## File Structure

- Modify `src/fashion_radar/discovery/candidates.py`
  - Add optional `source_type` and `source_name` filters to `discover_candidates()`.
  - Add the same optional filters to `_candidate_mentions()`.
- Create `src/fashion_radar/imported_candidates.py`
  - Models: `ImportedCandidatesReview`
  - Helpers: `query_imported_candidates()`, `render_imported_candidates_table()`
  - Internal helpers: `_candidate_report()`, `_table_cell()`
- Modify `src/fashion_radar/cli.py`
  - Import query/renderer.
  - Add `ImportedCandidatesOutputFormat`.
  - Add `imported-candidates` command.
- Modify `tests/test_candidate_scoring.py`
  - Filter regressions for `discover_candidates()`.
- Create `tests/test_imported_candidates.py`
  - Unit tests for imported-only query and renderer.
- Modify `tests/test_cli.py`
  - CLI tests for help, JSON/table, invalid inputs, no artifacts, and no mutation.
- Modify docs/changelog/checklist:
  - `README.md`
  - `docs/candidate-discovery.md`
  - `docs/manual-signal-import.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/architecture.md`
  - `docs/source-boundaries.md`
  - `docs/github-upload-checklist.md`
  - `CHANGELOG.md`
- Create Claude Code Stage 25 code review prompt/result files.

## Task 1: Candidate Discovery Source Filters

**Files:**
- Modify: `src/fashion_radar/discovery/candidates.py`
- Modify: `tests/test_candidate_scoring.py`

- [ ] **Step 1: Write failing filter tests**

In `tests/test_candidate_scoring.py`, modify helper `_store()` to accept
`source_type: SourceType = SourceType.RSS` and pass it into `CollectedItem`.

Add:

```python
def test_discover_candidates_filters_source_type_and_source_name(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Le Teckel bag appears in imported row",
        url="https://example.com/imported-a",
        source_name="Community Tool Export",
        source_type=SourceType.MANUAL_IMPORT,
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Le Teckel bag appears in another imported row",
        url="https://example.com/imported-b",
        source_name="Manual Export",
        source_type=SourceType.MANUAL_IMPORT,
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store(
        engine,
        title="Le Teckel bag appears in RSS row",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=3),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        source_type=SourceType.MANUAL_IMPORT,
        source_name="Community Tool Export",
    )

    candidate = next(item for item in candidates if item.normalized_key == "le teckel bag")
    assert candidate.current_mentions == 1
    assert candidate.distinct_sources == 1
    assert [item.source_name for item in candidate.representative_items] == [
        "Community Tool Export"
    ]
```

Add:

```python
def test_discover_candidates_default_keeps_all_source_types(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(
        engine,
        title="Slim sneaker current imported mention",
        url="https://example.com/imported",
        source_name="Community Tool Export",
        source_type=SourceType.MANUAL_IMPORT,
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store(
        engine,
        title="Slim sneaker current RSS mention",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=2),
    )

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "slim sneaker")
    assert candidate.current_mentions == 2
    assert candidate.distinct_sources == 2
```

- [ ] **Step 2: Run filter tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py -q -k "source_type or default_keeps_all_source_types"
```

Expected: at least `source_type` test fails because `discover_candidates()`
does not yet accept `source_type` or `source_name`.

- [ ] **Step 3: Implement optional filters**

In `src/fashion_radar/discovery/candidates.py`, import `SourceType`:

```python
from fashion_radar.models.source import SourceType
```

Update `discover_candidates()` signature:

```python
def discover_candidates(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: datetime,
    limit: int | None = None,
    source_type: SourceType | str | None = None,
    source_name: str | None = None,
) -> list[CandidateMetric]:
```

Before calling `_candidate_mentions()`, normalize filters:

```python
source_type_filter = source_type.value if isinstance(source_type, SourceType) else source_type
source_name_filter = (source_name or "").strip() or None
```

Pass filters:

```python
mentions = _candidate_mentions(
    engine,
    known_keys=known_keys,
    settings=settings,
    baseline_start=baseline_start,
    as_of=as_of_utc,
    source_type=source_type_filter,
    source_name=source_name_filter,
)
```

Update `_candidate_mentions()` signature:

```python
def _candidate_mentions(
    engine: Engine,
    *,
    known_keys: set[str],
    settings: CandidateDiscoverySettings,
    baseline_start: datetime,
    as_of: datetime,
    source_type: str | None = None,
    source_name: str | None = None,
) -> list[_CandidateMention]:
```

Apply SQL filters before executing:

```python
query = select(
    items.c.id,
    items.c.source_name,
    items.c.source_weight,
    items.c.url,
    items.c.published_at,
    items.c.title,
    items.c.summary,
    items.c.collected_at,
)
conditions = []
if source_type is not None:
    conditions.append(items.c.source_type == source_type)
if source_name is not None:
    conditions.append(items.c.source_name == source_name)
if conditions:
    query = query.where(*conditions)
rows = list(connection.execute(query).mappings())
```

- [ ] **Step 4: Run filter tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py -q -k "source_type or default_keeps_all_source_types"
```

Expected: filter tests pass.

## Task 2: Imported Candidates Query And Renderer

**Files:**
- Create: `src/fashion_radar/imported_candidates.py`
- Create: `tests/test_imported_candidates.py`

- [ ] **Step 1: Write failing imported candidate tests**

Create `tests/test_imported_candidates.py` with imports:

```python
from datetime import UTC, datetime, timedelta
from pathlib import Path

import fashion_radar.imported_candidates as imported_candidates_module
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.imported_candidates import (
    ImportedCandidatesReview,
    query_imported_candidates,
    render_imported_candidates_table,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.settings import CandidateDiscoverySettings, ScoringSettings
```

Add helper:

```python
AS_OF = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)


def _store_item(
    repository: ItemRepository,
    *,
    title: str,
    url: str,
    source_name: str = "Community Tool Export",
    source_type: SourceType = SourceType.MANUAL_IMPORT,
    collected_at: datetime | None = None,
) -> int:
    collected = collected_at or AS_OF
    return repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=source_type,
            url=url,
            title=title,
            published_at=collected,
            summary=title,
        ),
        collected_at=collected,
    )
```

Add:

```python
def test_query_imported_candidates_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    assert result.database == str(db_path)
    assert result.as_of == "2026-06-13T12:00:00+00:00"
    assert result.source_type == "manual_import"
    assert result.source_name is None
    assert result.limit == 50
    assert result.candidate_count == 0
    assert result.candidates == []
    assert not db_path.parent.exists()
```

Add:

```python
def test_query_imported_candidates_filters_manual_rows_and_source_name(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/imported-a",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag current manual mention",
        url="https://example.com/imported-b",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store_item(
        repository,
        title="Le Teckel bag current RSS mention",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=3),
    )
    engine.dispose()

    result = query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        source_name="Community Tool Export",
    )

    assert result.candidate_count == 1
    candidate = result.candidates[0]
    assert candidate.phrase == "Le Teckel bag"
    assert candidate.current_mentions == 1
    assert candidate.distinct_sources == 1
    assert not hasattr(candidate, "representative_items")
```

Add:

```python
def test_query_imported_candidates_uses_readonly_engine(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()
    calls: list[Path] = []
    original = imported_candidates_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_candidates_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_candidates(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    assert calls == [db_path]
```

Add renderer test:

```python
def test_render_imported_candidates_table_sanitizes_display_cells() -> None:
    review = ImportedCandidatesReview(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-07T12:00:00+00:00",
        source_name="Community | Export",
    )

    assert render_imported_candidates_table(review) == [
        "Imported manual candidate signals from local SQLite.",
        "Candidate signals are observed phrases from retained manual_import rows and need review.",
        "Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00",
        "Baseline window: 2026-05-07T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00",
        "Source name: Community / Export",
        "Candidates: 0",
        "No imported manual candidate signals found.",
    ]
```

- [ ] **Step 2: Run imported candidate tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_candidates.py -q
```

Expected: fail because `fashion_radar.imported_candidates` does not exist.

- [ ] **Step 3: Implement imported candidates module**

Create `src/fashion_radar/imported_candidates.py`:

```python
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.discovery.candidates import discover_candidates
from fashion_radar.imported_signals import verify_imported_signals_schema
from fashion_radar.models.source import SourceType
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.trends import create_readonly_sqlite_engine
from fashion_radar.utils.dates import parse_datetime_utc
```

Add models:

```python
class ImportedCandidateRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: str
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: str


class ImportedCandidatesReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_type: Literal["manual_import"] = "manual_import"
    source_name: str | None = None
    limit: int | None = 50
    candidate_count: int = 0
    candidates: list[ImportedCandidateRow] = Field(default_factory=list)
```

Add query:

```python
def query_imported_candidates(
    db_path: Path,
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    source_name: str | None = None,
    limit: int | None = 50,
) -> ImportedCandidatesReview:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")
    as_of_value = parse_datetime_utc(as_of)
    current_window_start = as_of_value - timedelta(days=scoring.current_window_days)
    baseline_window_start = current_window_start - timedelta(days=scoring.baseline_window_days)
    source_filter = (source_name or "").strip() or None
    review_base = {
        "database": str(db_path),
        "as_of": as_of_value.isoformat(),
        "current_window_start": current_window_start.isoformat(),
        "baseline_window_start": baseline_window_start.isoformat(),
        "current_days": scoring.current_window_days,
        "baseline_days": scoring.baseline_window_days,
        "source_name": source_filter,
        "limit": limit,
    }
    if not db_path.exists():
        return ImportedCandidatesReview(**review_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        metrics = discover_candidates(
            engine,
            scoring=scoring,
            settings=settings,
            entity_config=entity_config,
            as_of=as_of_value,
            limit=limit,
            source_type=SourceType.MANUAL_IMPORT,
            source_name=source_filter,
        )
    finally:
        engine.dispose()
    candidates = [_candidate_report(metric) for metric in metrics]
    return ImportedCandidatesReview(
        **review_base,
        candidate_count=len(candidates),
        candidates=candidates,
    )
```

Add renderer and helpers:

```python
def render_imported_candidates_table(review: ImportedCandidatesReview) -> list[str]:
    lines = [
        "Imported manual candidate signals from local SQLite.",
        "Candidate signals are observed phrases from retained manual_import rows and need review.",
        f"Current window: {review.current_window_start} < collected_at <= {review.as_of}",
        (
            f"Baseline window: {review.baseline_window_start} < collected_at <= "
            f"{review.current_window_start}"
        ),
        f"Source name: {_table_cell(review.source_name or 'none')}",
        f"Candidates: {review.candidate_count}",
    ]
    if not review.candidates:
        lines.append("No imported manual candidate signals found.")
        return lines

    lines.append(
        "Phrase | Type | Label | Score | Current Mentions | Baseline Mentions | "
        "Distinct Sources | First Seen At"
    )
    for candidate in review.candidates:
        lines.append(
            f"{_table_cell(candidate.phrase)} | {_table_cell(candidate.candidate_type)} | "
            f"{_table_cell(candidate.label)} | {candidate.score:.2f} | "
            f"{candidate.current_mentions} | {candidate.baseline_mentions} | "
            f"{candidate.distinct_sources} | {candidate.first_seen_at}"
        )
    return lines


def _candidate_report(metric) -> ImportedCandidateRow:
    return ImportedCandidateRow(
        phrase=metric.phrase,
        candidate_type=metric.candidate_type,
        label=metric.label,
        score=metric.score,
        current_mentions=metric.current_mentions,
        baseline_mentions=metric.baseline_mentions,
        distinct_sources=metric.distinct_sources,
        growth_ratio=metric.growth_ratio,
        first_seen_at=parse_datetime_utc(metric.first_seen_at).isoformat(),
    )


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 4: Run imported candidate tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_candidates.py -q
```

Expected: imported candidate tests pass.

## Task 3: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add CLI tests near existing `candidates`/`trends` tests:

```python
def test_imported_candidates_command_help_lists_options() -> None:
    result = CliRunner().invoke(app, ["imported-candidates", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "imported manual candidate" in result.output.lower()
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--source-name" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output
```

Add a fixture that creates scoring/entity config plus manual/RSS rows:

```python
def _prepare_imported_candidates_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        '''
version: 1
scoring:
  current_window_days: 7
  baseline_window_days: 30
candidate_discovery:
  min_current_mentions: 1
  review_min_current_mentions: 1
  min_single_token_mentions: 99
  min_single_token_distinct_sources: 99
  max_candidates: 10
'''.lstrip(),
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    as_of = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)
    for source_name, url in (
        ("Community Tool Export", "https://example.com/imported-a"),
        ("Manual Export", "https://example.com/imported-b"),
    ):
        repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.MANUAL_IMPORT,
                url=url,
                title="Le Teckel bag current mention",
                published_at=as_of - timedelta(hours=1),
                summary="Le Teckel bag current mention",
            ),
            collected_at=as_of - timedelta(hours=1),
        )
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/rss",
            title="Le Teckel bag RSS mention",
            published_at=as_of - timedelta(hours=2),
            summary="Le Teckel bag RSS mention",
        ),
        collected_at=as_of - timedelta(hours=2),
    )
    engine.dispose()
    return config_dir, data_dir
```

Add JSON stable key test:

```python
def test_imported_candidates_command_prints_json_with_stable_keys(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_imported_candidates_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--source-name",
            "Community Tool Export",
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
        "source_type",
        "source_name",
        "limit",
        "candidate_count",
        "candidates",
    ]
    assert payload["source_type"] == "manual_import"
    assert payload["source_name"] == "Community Tool Export"
    assert payload["candidate_count"] == 1
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]
    forbidden = {
        "representative_items",
        "source_url",
        "title",
        "summary",
        "contexts",
        "normalized_key",
        "item_id",
        "matches",
        "match_status",
    }
    assert forbidden.isdisjoint(payload["candidates"][0])
    assert payload["candidates"][0]["current_mentions"] == 1
```

Add invalid input/no-artifact tests following existing imported command style:

```python
def _fail_imported_candidates_query(*args, **kwargs):
    raise AssertionError("query_imported_candidates should not be called")
```

Test invalid format and invalid limit by monkeypatching
`cli_module.query_imported_candidates`. Test invalid `--as-of` exits `1` with:

```text
Could not review imported candidates: invalid --as-of
```

Test missing database creates no config/data/report artifacts with
`assert_no_community_lint_artifacts()`.

- [ ] **Step 2: Run CLI tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_candidates"
```

Expected: fail because `imported-candidates` is not registered.

- [ ] **Step 3: Implement CLI command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.imported_candidates import (
    query_imported_candidates,
    render_imported_candidates_table,
)
```

Add:

```python
ImportedCandidatesOutputFormat = Literal["table", "json"]
```

Add option constants:

```python
IMPORTED_CANDIDATES_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC imported candidate review timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_CANDIDATES_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add command near `candidates`/imported review commands:

```python
@app.command(name="imported-candidates")
def imported_candidates_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_CANDIDATES_AS_OF_OPTION,
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    limit: int | None = typer.Option(50, min=0, help="Maximum imported candidates to print."),
    output_format: ImportedCandidatesOutputFormat = IMPORTED_CANDIDATES_FORMAT_OPTION,
) -> None:
    """Review candidate phrases from imported manual signals only."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(f"Could not review imported candidates: invalid --as-of: {exc}", err=True)
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid imported candidates config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        review = query_imported_candidates(
            default_database_path(data_dir),
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            source_name=source_name,
            limit=limit,
        )
    except Exception as exc:
        typer.echo(f"Could not review imported candidates: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_candidates_table(review):
        typer.echo(line)
```

- [ ] **Step 4: Run CLI tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_candidates"
```

Expected: CLI tests pass.

## Task 4: Documentation And Changelog

**Files:**
- Modify: `README.md`
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add bounded command examples**

Add examples near existing imported review/candidate docs:

```bash
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export" --format json
```

Use wording:

```markdown
`imported-candidates` is local and read-only. It surfaces observed candidate
phrases from retained `manual_import` rows only. These phrases need review and
are not verified entities, market-wide demand, or platform coverage.
```

- [ ] **Step 2: Update upload checklist**

Add installed-wheel smoke:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-candidates --help
```

- [ ] **Step 3: Update changelog**

Add under `### Added`:

```markdown
- Local read-only `imported-candidates` command for reviewing candidate phrases
  from retained `manual_import` rows only.
```

- [ ] **Step 4: Run docs boundary scan**

Run:

```bash
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

Expected: no new capability wording from Stage 25 product docs. Negative
boundary wording is acceptable only when it says the feature does not do those
things.

## Task 5: Review, Verification, And Release

**Files:**
- Create: `docs/reviews/claude-code-stage-25-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-25-code-review.md`
- Modify: any file needed to fix Critical or Important review findings

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py tests/test_imported_candidates.py tests/test_cli.py -q -k "imported_candidates or source_type or candidates_command or trends_command"
.venv/bin/python -m pytest tests/test_reports.py tests/test_trends.py tests/test_dashboard.py -q -k "candidate or trend or build_daily_report"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-25-code-review-prompt.md` asking Claude
Code to review the current working tree in read-only mode. Required review
focus:

- default candidate discovery behavior remains unchanged;
- imported candidates read only retained `manual_import` rows;
- no SQLite writes, config writes, report/dashboard writes, source acquisition,
  scraping, crawling, platform integration, scheduling, or account automation;
- invalid CLI inputs avoid query execution where appropriate;
- JSON/table contracts are stable and do not expose internal candidate contexts
  or match internals;
- docs remain local and do not imply verified entities, demand proof, market
  coverage, platform coverage, ranking, source quality, or source coverage.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-25-code-review-prompt.md | tee docs/reviews/claude-code-stage-25-code-review.md
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
git status --short
git diff -- uv.lock
rm -rf /tmp/fashion-radar-dist-stage25
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage25
```

Expected: all checks pass. If `uv.lock` still shows the pre-existing mirror-url
diff, it remains unstaged and excluded from the Stage 25 commit. Do not commit
any mirror-backed lockfile change.

- [ ] **Step 4: Run installed-wheel smoke**

Run:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv" --python 3.11
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage25/*.whl
mkdir -p "$tmp_env/config"
printf 'version: 1\nscoring: {}\ncandidate_discovery:\n  min_current_mentions: 1\n  review_min_current_mentions: 1\n' > "$tmp_env/config/scoring.yaml"
"$tmp_env/venv/bin/fashion-radar" imported-candidates --help
"$tmp_env/venv/bin/fashion-radar" imported-candidates --data-dir "$tmp_env/data" --config-dir "$tmp_env/config" --as-of "2026-06-13T12:00:00Z" --format json
```

Expected: both commands exit zero. The JSON command returns an empty imported
candidate review because the database is missing, and it does not create SQLite.

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
Important findings and all release checks pass.

Run:

```bash
current_branch="$(git branch --show-current)"
if [ "$current_branch" != "main" ]; then
  echo "Not on main; stop and adapt push target."
  exit 1
fi
git status --short --branch
git add src/fashion_radar/discovery/candidates.py src/fashion_radar/imported_candidates.py src/fashion_radar/cli.py tests/test_candidate_scoring.py tests/test_imported_candidates.py tests/test_cli.py README.md docs CHANGELOG.md
git commit -m "Add imported candidates command"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: branch is `main`, commit succeeds, and push updates `origin/main`.

Do not stage or commit `uv.lock` unless a later approved plan explicitly changes
dependencies or lockfile content.
