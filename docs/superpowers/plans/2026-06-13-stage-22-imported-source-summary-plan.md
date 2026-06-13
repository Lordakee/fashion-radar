# Stage 22 Imported Signals Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar imported-signals-summary`, a local read-only command that summarizes currently retained `manual_import` rows by stored source-name label.

**Architecture:** Extend `src/fashion_radar/imported_signals.py` with source-summary Pydantic models, a read-only query helper that reuses existing imported-signals schema verification, and a table renderer. Add a thin Typer command that emits table or JSON and never initializes, migrates, imports, matches, scores, reports, schedules, monitors, collects, or writes artifacts. No `--as-of`, lookback window, or limit is added; the command summarizes the current local SQLite state.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, SQLite read-only URI mode, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/imported_signals.py`: add `ImportedSignalSourceSummaryRow`, `ImportedSignalsSourceSummary`, `query_imported_signals_summary()`, `_query_imported_signals_summary()`, and `render_imported_signals_summary_table()`.
- Modify `src/fashion_radar/cli.py`: import the new helper/renderer, add `ImportedSignalsSummaryOutputFormat`, option constant, and `imported-signals-summary` command.
- Modify `tests/test_imported_signals.py`: add helper/query/renderer tests for retained imported signal summaries.
- Modify `tests/test_cli.py`: add CLI tests for help, invalid format, table, JSON, invalid schema, missing DB, special-character path, and no mutation.
- Modify docs and changelog with bounded local-only examples.
- Create Stage 22 code review prompt/result files after implementation.

## Task 1: Source Summary Models And Query

**Files:**
- Modify: `src/fashion_radar/imported_signals.py`
- Test: `tests/test_imported_signals.py`

- [ ] **Step 1: Add failing imports and missing-database test**

In `tests/test_imported_signals.py`, extend the imported-signals import block:

```python
from fashion_radar.imported_signals import (
    ImportedSignalItem,
    ImportedSignalMatch,
    ImportedSignalSourceSummaryRow,
    ImportedSignalsReview,
    ImportedSignalsSourceSummary,
    query_imported_signals,
    query_imported_signals_summary,
    render_imported_signals_summary_table,
    render_imported_signals_table,
    verify_imported_signals_schema,
)
```

Add:

```python
def test_query_imported_signals_summary_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    summary = query_imported_signals_summary(db_path)

    assert summary.database == str(db_path)
    assert summary.source_type == "manual_import"
    assert summary.source_count == 0
    assert summary.row_count == 0
    assert summary.matched_count == 0
    assert summary.unmatched_count == 0
    assert summary.first_collected_at is None
    assert summary.latest_collected_at is None
    assert summary.sources == []
    assert not db_path.parent.exists()
```

- [ ] **Step 2: Add failing grouping/counting test**

Add:

```python
def test_query_imported_signals_summary_groups_manual_rows_and_match_presence(
    tmp_path: Path,
) -> None:
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
    _store_item(
        repository,
        source_name="Manual Import",
        url="https://example.com/manual",
        title="Manual item",
        published_at=datetime(2026, 6, 10, 7, 0, tzinfo=UTC),
        collected_at=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
    )
    _store_item(
        repository,
        source_name="RSS Source",
        source_type=SourceType.RSS,
        url="https://example.com/rss",
        title="RSS item",
        published_at=datetime(2026, 6, 12, 7, 0, tzinfo=UTC),
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
            },
            {
                "entity_name": "Margaux",
                "entity_type": "product",
                "alias": "Margaux",
                "confidence": 0.9,
                "reason": "context",
                "context_terms": ["bag"],
            },
        ],
    )
    engine.dispose()

    summary = query_imported_signals_summary(db_path)

    assert summary.source_count == 2
    assert summary.row_count == 3
    assert summary.matched_count == 1
    assert summary.unmatched_count == 2
    assert summary.first_collected_at == "2026-06-10T09:00:00+00:00"
    assert summary.latest_collected_at == "2026-06-12T10:00:00+00:00"
    assert [source.source_name for source in summary.sources] == [
        "Community Tool Export",
        "Manual Import",
    ]
    assert summary.sources[0].row_count == 2
    assert summary.sources[0].matched_count == 1
    assert summary.sources[0].unmatched_count == 1
    assert summary.sources[0].first_collected_at == "2026-06-12T09:00:00+00:00"
    assert summary.sources[0].latest_collected_at == "2026-06-12T10:00:00+00:00"
    assert summary.sources[1].row_count == 1
    assert summary.sources[1].matched_count == 0
    assert summary.sources[1].unmatched_count == 1
```

- [ ] **Step 3: Add failing read-only engine test**

Add:

```python
def test_query_imported_signals_summary_uses_readonly_engine(
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

    query_imported_signals_summary(db_path)

    assert calls == [db_path]
```

- [ ] **Step 4: Run new query tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py -q -k "imported_signals_summary"
```

Expected: fail because the models and query helper do not exist yet.

- [ ] **Step 5: Implement models and query**

In `src/fashion_radar/imported_signals.py`, add after `ImportedSignalsReview`:

```python
class ImportedSignalSourceSummaryRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    row_count: int
    matched_count: int = 0
    unmatched_count: int = 0
    first_collected_at: str | None = None
    latest_collected_at: str | None = None


class ImportedSignalsSourceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    source_type: Literal["manual_import"] = "manual_import"
    source_count: int = 0
    row_count: int = 0
    matched_count: int = 0
    unmatched_count: int = 0
    first_collected_at: str | None = None
    latest_collected_at: str | None = None
    sources: list[ImportedSignalSourceSummaryRow] = Field(default_factory=list)
```

Add after `query_imported_signals()`:

```python
def query_imported_signals_summary(db_path: Path) -> ImportedSignalsSourceSummary:
    summary_base = {"database": str(db_path)}
    if not db_path.exists():
        return ImportedSignalsSourceSummary(**summary_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        return _query_imported_signals_summary(engine, summary_base=summary_base)
    finally:
        engine.dispose()
```

Add after `_query_imported_signals()`:

```python
def _query_imported_signals_summary(
    engine: Engine,
    *,
    summary_base: dict[str, object],
) -> ImportedSignalsSourceSummary:
    match_exists = select(item_entities.c.id).where(item_entities.c.item_id == items.c.id).exists()
    conditions = [items.c.source_type == SourceType.MANUAL_IMPORT.value]

    with engine.connect() as connection:
        source_rows = connection.execute(
            select(
                items.c.source_name,
                func.count(),
                func.min(items.c.collected_at),
                func.max(items.c.collected_at),
            )
            .where(*conditions)
            .group_by(items.c.source_name)
            .order_by(items.c.source_name)
        ).all()
        matched_rows = connection.execute(
            select(items.c.source_name, func.count())
            .where(*conditions, match_exists)
            .group_by(items.c.source_name)
        ).all()

    matched_by_source = {str(name): int(count) for name, count in matched_rows}
    sources: list[ImportedSignalSourceSummaryRow] = []
    for name, count, first_collected_at, latest_collected_at in source_rows:
        source_name = str(name)
        row_count = int(count)
        matched_count = matched_by_source.get(source_name, 0)
        sources.append(
            ImportedSignalSourceSummaryRow(
                source_name=source_name,
                row_count=row_count,
                matched_count=matched_count,
                unmatched_count=row_count - matched_count,
                first_collected_at=parse_datetime_utc(first_collected_at).isoformat(),
                latest_collected_at=parse_datetime_utc(latest_collected_at).isoformat(),
            )
        )

    total_rows = sum(source.row_count for source in sources)
    matched_total = sum(source.matched_count for source in sources)
    first_values = [source.first_collected_at for source in sources if source.first_collected_at]
    latest_values = [source.latest_collected_at for source in sources if source.latest_collected_at]
    return ImportedSignalsSourceSummary(
        **summary_base,
        source_count=len(sources),
        row_count=total_rows,
        matched_count=matched_total,
        unmatched_count=total_rows - matched_total,
        first_collected_at=min(first_values) if first_values else None,
        latest_collected_at=max(latest_values) if latest_values else None,
        sources=sources,
    )
```

- [ ] **Step 6: Run query tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py -q -k "imported_signals_summary"
```

Expected: new query tests pass.

## Task 2: Source Summary Table Rendering

**Files:**
- Modify: `src/fashion_radar/imported_signals.py`
- Test: `tests/test_imported_signals.py`

- [ ] **Step 1: Add failing renderer tests**

Add:

```python
def test_render_imported_signals_summary_table_empty() -> None:
    summary = ImportedSignalsSourceSummary(database="missing.sqlite")

    assert render_imported_signals_summary_table(summary) == [
        "Imported manual signal source summary from local SQLite.",
        "Rows: 0 retained manual rows across 0 sources",
        "Matched rows: 0 matched, 0 unmatched",
        "Collected at: none",
        "No imported manual signal sources found.",
    ]
```

Add:

```python
def test_render_imported_signals_summary_table_populated_sanitizes_cells() -> None:
    summary = ImportedSignalsSourceSummary(
        database="data/fashion-radar.sqlite",
        source_count=2,
        row_count=3,
        matched_count=1,
        unmatched_count=2,
        first_collected_at="2026-06-10T09:00:00+00:00",
        latest_collected_at="2026-06-12T10:00:00+00:00",
        sources=[
            ImportedSignalSourceSummaryRow(
                source_name="Community | Tool\nExport",
                row_count=2,
                matched_count=1,
                unmatched_count=1,
                first_collected_at="2026-06-12T09:00:00+00:00",
                latest_collected_at="2026-06-12T10:00:00+00:00",
            ),
            ImportedSignalSourceSummaryRow(
                source_name="Manual Import",
                row_count=1,
                matched_count=0,
                unmatched_count=1,
                first_collected_at="2026-06-10T09:00:00+00:00",
                latest_collected_at="2026-06-10T09:00:00+00:00",
            ),
        ],
    )

    assert render_imported_signals_summary_table(summary) == [
        "Imported manual signal source summary from local SQLite.",
        "Rows: 3 retained manual rows across 2 sources",
        "Matched rows: 1 matched, 2 unmatched",
        "Collected at: 2026-06-10T09:00:00+00:00 first, 2026-06-12T10:00:00+00:00 latest",
        "Source | Rows | Matched Rows | Unmatched Rows | First Collected At | Latest Collected At",
        "Community / Tool Export | 2 | 1 | 1 | 2026-06-12T09:00:00+00:00 | 2026-06-12T10:00:00+00:00",
        "Manual Import | 1 | 0 | 1 | 2026-06-10T09:00:00+00:00 | 2026-06-10T09:00:00+00:00",
    ]
```

- [ ] **Step 2: Run renderer tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py -q -k "render_imported_signals_summary_table"
```

Expected: fail because the renderer does not exist yet.

- [ ] **Step 3: Implement renderer**

In `src/fashion_radar/imported_signals.py`, add:

```python
def render_imported_signals_summary_table(
    summary: ImportedSignalsSourceSummary,
) -> list[str]:
    lines = [
        "Imported manual signal source summary from local SQLite.",
        (
            f"Rows: {summary.row_count} retained manual rows "
            f"across {summary.source_count} sources"
        ),
        f"Matched rows: {summary.matched_count} matched, {summary.unmatched_count} unmatched",
        _format_collected_at_range(summary.first_collected_at, summary.latest_collected_at),
    ]
    if not summary.sources:
        lines.append("No imported manual signal sources found.")
        return lines

    lines.append(
        "Source | Rows | Matched Rows | Unmatched Rows | First Collected At | Latest Collected At"
    )
    for source in summary.sources:
        lines.append(
            f"{_table_cell(source.source_name)} | {source.row_count} | "
            f"{source.matched_count} | {source.unmatched_count} | "
            f"{source.first_collected_at or ''} | {source.latest_collected_at or ''}"
        )
    return lines


def _format_collected_at_range(first: str | None, latest: str | None) -> str:
    if first is None or latest is None:
        return "Collected at: none"
    return f"Collected at: {first} first, {latest} latest"
```

- [ ] **Step 4: Run renderer tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py -q -k "render_imported_signals_summary_table"
```

Expected: renderer tests pass.

## Task 3: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

In `tests/test_cli.py`, add near the existing `imported-signals` tests:

```python
def test_imported_signals_summary_command_help_lists_options() -> None:
    result = CliRunner().invoke(
        app,
        ["imported-signals-summary", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--data-dir" in result.output
    assert "--format" in result.output
    assert "Summarize imported manual signal source labels" in result.output
```

Add:

```python
def test_imported_signals_summary_command_missing_database_is_read_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
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
    assert payload["row_count"] == 0
    assert payload["source_count"] == 0
    assert_no_community_lint_artifacts(
        tmp_path,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
    )
```

Add:

```python
def test_imported_signals_summary_command_prints_table(tmp_path: Path) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Imported manual signal source summary from local SQLite." in result.output
    assert "Rows: 3 retained manual rows across 2 sources" in result.output
    assert "Matched rows: 1 matched, 2 unmatched" in result.output
    assert "Community Tool Export | 2 | 1 | 1" in result.output
    assert "Manual Import | 1 | 0 | 1" in result.output
    assert "Margaux interest" not in result.output
    assert "https://example.com/margaux" not in result.output
    assert "RSS Source" not in result.output
```

Add:

```python
def test_imported_signals_summary_command_prints_json_with_stable_keys(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "database",
        "source_type",
        "source_count",
        "row_count",
        "matched_count",
        "unmatched_count",
        "first_collected_at",
        "latest_collected_at",
        "sources",
    ]
    assert payload["source_type"] == "manual_import"
    assert payload["source_count"] == 2
    assert payload["row_count"] == 3
    assert payload["matched_count"] == 1
    assert payload["unmatched_count"] == 2
    assert list(payload["sources"][0]) == [
        "source_name",
        "row_count",
        "matched_count",
        "unmatched_count",
        "first_collected_at",
        "latest_collected_at",
    ]
    assert "title" not in payload["sources"][0]
    assert "url" not in payload["sources"][0]
```

- [ ] **Step 2: Add failing CLI validation/path/schema/no-mutation tests**

Add:

```python
def _fail_imported_signals_summary_query(*args, **kwargs):
    raise AssertionError("query_imported_signals_summary should not be called")
```

Add invalid format test:

```python
def test_imported_signals_summary_command_rejects_invalid_format_without_query(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setattr(
        cli_module,
        "query_imported_signals_summary",
        _fail_imported_signals_summary_query,
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "--format" in result.output
    assert "query_imported_signals_summary should not be called" not in result.output
    assert "Traceback" not in result.output
    assert not data_dir.exists()
```

Add special-character path test:

```python
def test_imported_signals_summary_command_handles_special_character_data_dir(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(
        tmp_path,
        data_dir_name="data ? # & %",
    )

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["row_count"] == 3
    assert payload["database"] == str(data_dir / "fashion-radar.sqlite")
```

Add invalid schema test:

```python
def test_imported_signals_summary_command_invalid_schema_no_traceback(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with sqlite3.connect(data_dir / "fashion-radar.sqlite") as connection:
        connection.execute("create table schema_metadata (version integer primary key)")
        connection.execute(f"insert into schema_metadata (version) values ({SCHEMA_VERSION})")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Could not summarize imported signals" in result.output
    assert "Traceback" not in result.output
```

Add no-mutation test:

```python
def test_imported_signals_summary_command_does_not_mutate_existing_database(
    tmp_path: Path,
) -> None:
    data_dir = _prepare_imported_signals_cli_fixture(tmp_path)
    db_path = data_dir / "fashion-radar.sqlite"
    with sqlite3.connect(db_path) as connection:
        before_items = connection.execute("select count(*) from items").fetchone()[0]
        before_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        before_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        before_tables = {
            row[0]
            for row in connection.execute(
                "select name from sqlite_master where type = 'table'"
            )
        }

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(db_path) as connection:
        after_items = connection.execute("select count(*) from items").fetchone()[0]
        after_matches = connection.execute("select count(*) from item_entities").fetchone()[0]
        after_schema_version = connection.execute(
            "select version from schema_metadata"
        ).fetchone()[0]
        after_tables = {
            row[0]
            for row in connection.execute(
                "select name from sqlite_master where type = 'table'"
            )
        }
    assert after_items == before_items
    assert after_matches == before_matches
    assert after_schema_version == before_schema_version
    assert after_tables == before_tables
```

- [ ] **Step 3: Run CLI tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_signals_summary"
```

Expected: fail because the command does not exist.

- [ ] **Step 4: Implement CLI imports and command**

In `src/fashion_radar/cli.py`, extend the imported-signals import:

```python
from fashion_radar.imported_signals import (
    query_imported_signals,
    query_imported_signals_summary,
    render_imported_signals_summary_table,
    render_imported_signals_table,
)
```

Add near output format aliases:

```python
ImportedSignalsSummaryOutputFormat = Literal["table", "json"]
```

Add near imported-signals format option:

```python
IMPORTED_SIGNALS_SUMMARY_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Add before `imported_signals_command()`:

```python
@app.command(name="imported-signals-summary")
def imported_signals_summary_command(
    data_dir: Path = DATA_DIR_OPTION,
    output_format: ImportedSignalsSummaryOutputFormat = IMPORTED_SIGNALS_SUMMARY_FORMAT_OPTION,
) -> None:
    """Summarize imported manual signal source labels already stored in local SQLite."""
    try:
        summary = query_imported_signals_summary(default_database_path(data_dir))
    except Exception as exc:
        typer.echo(f"Could not summarize imported signals: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(summary.model_dump_json(indent=2))
        return
    for line in render_imported_signals_summary_table(summary):
        typer.echo(line)
```

- [ ] **Step 5: Run CLI tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_signals_summary"
```

Expected: all imported-signals-summary CLI tests pass.

## Task 4: Documentation And Changelog

**Files:**
- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update README command examples**

In `README.md`, near the imported-signals examples, add:

```bash
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
```

Add bounded prose:

```markdown
`imported-signals-summary` is local and read-only. It groups retained
`manual_import` rows by stored `source_name` so users can inspect local import
volume and item-level stored match presence without exposing row titles, URLs,
summaries, imported source file paths, or internal match details. `source_name`
is a stored local provenance label, not a statement about anything outside the
local database.
```

- [ ] **Step 2: Update manual/community import docs**

In `docs/manual-signal-import.md`, add `imported-signals-summary` to the
post-import review commands and state that it groups retained local rows by
stored source-name label.

In `docs/community-signal-import.md`, add the same command near Review After
Import and keep wording bounded to retained local rows.

In `docs/community-signal-quality.md`, add one sentence that after import,
`imported-signals-summary` can show source-name grouped counts before reviewing
individual rows with `imported-signals`.

- [ ] **Step 3: Update architecture/source-boundary/checklist docs**

In `docs/architecture.md`, add one line in the imported signal review area
showing optional review of imported source-name labels.

In `docs/source-boundaries.md`, add one sentence that imported signals summary
reads existing `manual_import` rows from local SQLite, groups row counts by
stored `source_name`, and creates no config, data, report, or dashboard
artifacts.

In `docs/github-upload-checklist.md`, add installed-wheel smoke command:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-signals-summary --help
```

- [ ] **Step 4: Update changelog**

In `CHANGELOG.md`, under `### Added`, add:

```markdown
- Local read-only `imported-signals-summary` command for grouping retained
  `manual_import` rows by stored source-name label and item-level stored match
  presence.
```

- [ ] **Step 5: Run docs boundary scan**

Run against only the staged or working diff so existing guardrail wording does
not make the scan unactionable:

```bash
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

Expected: no new problematic wording from Stage 22. Negative scope guard
wording may appear only as guardrails, not as capability claims.

## Task 5: Review, Verification, And Release

**Files:**
- Create: `docs/reviews/claude-code-stage-22-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-22-code-review.md`
- Modify: any file needed to fix Critical or Important review findings

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py tests/test_db.py -q -k "imported_signals_summary or imported_signals or readonly"
```

Expected: all selected tests pass.

- [ ] **Step 2: Run formatting and lint**

Run:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Write Claude Code review prompt**

Create `docs/reviews/claude-code-stage-22-code-review-prompt.md` with:

```markdown
# Claude Code Stage 22 Code Review Prompt

You are reviewing Stage 22 for `/home/ubuntu/fashion-radar` in read-only mode.
Do not edit files. Use maximum reasoning.

## Goal

Stage 22 adds `fashion-radar imported-signals-summary`, a local read-only
command that summarizes currently retained `manual_import` rows by stored
source-name label.

## Scope Guard

Do not recommend scraping, crawling, browser automation, platform APIs, account
automation, schedulers, watch folders, source acquisition, source-health,
source-quality, source-coverage, source-ranking, compliance/audit workflow
features, matching/scoring changes, report generation changes, dashboard
writes, database migrations, or new dependencies.

## Review Focus

Review the diff from `2214310` to `HEAD`.

Check:

1. The command reads only existing local SQLite and `manual_import` rows.
2. Missing DB and invalid CLI format do not create data/config/report artifacts.
3. Existing DBs are opened read-only and are not initialized, migrated, imported, matched, scored, reported, or otherwise mutated.
4. Source summaries count retained local rows by source-name label and item-level stored match presence; multiple entity matches for one item do not inflate matched-row counts.
5. Source rows are sorted by stored `source_name`, not by count/rank.
6. Table and JSON contracts are deterministic and do not expose URLs, titles, summaries, imported source file paths, raw rows, or internal match fields; the existing-style top-level `database` field is allowed.
7. Docs remain bounded to local source-name labels and do not imply platform coverage, source acquisition, source health, source quality, market-wide ranking, verified demand, or real-time monitoring.
8. Tests are focused and deterministic.

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

End with one of:

- `Approved for Stage 22 release checks`
- `Not approved`
```

- [ ] **Step 4: Request Claude Code code review**

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-22-code-review-prompt.md | tee docs/reviews/claude-code-stage-22-code-review.md
```

Expected: Claude Code returns either approval or findings. Fix every Critical
and Important finding before continuing.

- [ ] **Step 5: Run full release checks**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
rm -rf /tmp/fashion-radar-dist-stage22
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage22
```

Expected: all commands pass.

- [ ] **Step 6: Run installed wheel smoke**

Run:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv" --python 3.11
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage22/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/fashion-radar" imported-signals-summary --help
"$tmp_env/venv/bin/fashion-radar" imported-signals-summary --data-dir "$tmp_env/data ? # & %" --format json
```

Expected: help commands exit zero, missing database JSON exits zero, and no
traceback is printed.

- [ ] **Step 7: Run repository hygiene scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no secrets or generated artifacts that should be committed.

- [ ] **Step 8: Commit and push**

Run:

```bash
git status --short
current_branch="$(git branch --show-current)"
if [ "$current_branch" != "main" ]; then
  echo "Not on main; stop and adapt push target."
  exit 1
fi
git status --short --branch
git add src/fashion_radar/imported_signals.py src/fashion_radar/cli.py tests/test_imported_signals.py tests/test_cli.py README.md docs CHANGELOG.md
git commit -m "Add imported signals summary command"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: the branch is `main`, the worktree contains only Stage 22 changes
before commit, commit succeeds, and push updates `origin/main`. If the current
branch is not `main`, stop and adapt the push target to the current workflow
before pushing.
