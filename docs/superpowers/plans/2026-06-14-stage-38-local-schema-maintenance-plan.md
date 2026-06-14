# Stage 38 Local Schema Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local `migrate-db` command and read-only `doctor` schema status so users can inspect and upgrade the SQLite schema explicitly.

**Architecture:** Keep maintenance local and explicit. `migrate-db` is the only new write-capable path and only calls the existing schema initializer. `doctor` reads schema state without mutating the database, and read-only review errors point users to `migrate-db` instead of silently migrating.

**Tech Stack:** Python, Typer CLI, SQLAlchemy Core, SQLite, pytest, ruff, uv. No dependency, connector, scraping, platform automation, scheduler, watcher, or external API changes.

---

## Boundaries

In scope:

- `src/fashion_radar/cli.py`
- `src/fashion_radar/db/schema_messages.py`
- `src/fashion_radar/imported_signals.py`
- `src/fashion_radar/trends.py`
- `tests/test_cli.py`
- `tests/test_stage1_hardening.py`
- `README.md`
- `docs/architecture.md`
- `CHANGELOG.md`
- Stage 38 review artifacts.

Out of scope:

- Schema version changes.
- Source connectors, scraping, crawling, browser automation, login/cookie flow,
  account automation, proxy/CAPTCHA handling, source acquisition, source
  ranking, demand proof, watcher, scheduler, or external platform API work.
- Collecting feeds, importing signal rows, matching, scoring, reporting,
  dashboard startup, or digest packaging from `doctor` or `migrate-db`.
- Dependency or `uv.lock` changes.

## Task -1: Claude Code Plan Review Gate

This is a user-required audit artifact, not implementation work. The main
coordinating agent must complete it before Task 1 starts, commit the prompt and
review output as Stage 38 artifacts, and not ask implementation workers to rerun
the review once the approval phrase is present.

**Files:**

- Add: `docs/reviews/claude-code-stage-38-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-38-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create `docs/reviews/claude-code-stage-38-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 38 Plan Review Prompt

You are reviewing the Stage 38 local schema maintenance plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add a local `migrate-db` command and read-only `doctor` schema status so users
can inspect and upgrade the SQLite schema explicitly.

## Proposed Technical Approach

- Add `migrate-db --data-dir ...` that calls `create_sqlite_engine()` and
  `initialize_schema()` for the local SQLite database, then prints the resulting
  schema version.
- Extend `doctor` with a read-only database schema status line. Missing database
  is OK; current schema is OK; old/future/invalid schema exits non-zero with a
  user-facing message.
- Add read-only schema mismatch hints that point to
  `fashion-radar migrate-db --data-dir ...` for older/missing schemas.
- Keep future schema errors distinct so they do not imply `migrate-db` can
  downgrade a newer database.
- Add focused tests proving `doctor` is non-mutating and `migrate-db` does not
  collect, import, match, score, report, package digests, schedule, watch, or
  touch external sources.
- Keep all changes local: no connectors, scraping, crawling, browser
  automation, login/cookie/account/proxy/CAPTCHA/source-acquisition/platform
  API functionality.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-38-local-schema-maintenance-design.md`
- `docs/superpowers/plans/2026-06-14-stage-38-local-schema-maintenance-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 38 LOCAL SCHEMA MAINTENANCE
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-38-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-38-plan-review.md
```

Expected: approval phrase appears, or the plan is revised and rereviewed before
Task 1.

## Task 1: CLI Tests For `migrate-db`

**Files:**

- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add missing database initialization test**

Also add a help smoke near existing CLI help tests:

```python
def test_cli_help_lists_migrate_db() -> None:
    result = CliRunner().invoke(app, ["--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "migrate-db" in result.output
```

Add:

```python
def test_migrate_db_command_initializes_missing_database(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "migrate-db",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Database path:" in result.output
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output
    assert (data_dir / "fashion-radar.sqlite").exists()
```

- [ ] **Step 2: Add v4 upgrade test**

Add a small raw-SQL helper in `tests/test_cli.py`:

```python
def _create_v4_database(path: Path) -> None:
    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (4)")
        connection.exec_driver_sql(
            """
            create table items (
                id integer primary key,
                source_name varchar(255) not null,
                source_type varchar(64) not null,
                url text not null,
                normalized_url text not null,
                title text not null,
                published_at varchar(64) not null,
                source_weight float not null default 1.0,
                collected_at varchar(64) not null,
                summary text,
                content_hash varchar(64) not null,
                constraint uq_items_normalized_url unique (normalized_url)
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table item_entities (
                id integer primary key,
                item_id integer not null,
                entity_name varchar(255) not null,
                entity_type varchar(64) not null,
                alias varchar(255) not null,
                confidence float not null,
                reason varchar(64) not null,
                context_terms text not null default '[]'
            )
            """
        )
        connection.exec_driver_sql(
            """
            create table entity_first_seen (
                id integer primary key,
                entity_name varchar(255) not null,
                entity_type varchar(64) not null,
                first_seen_at varchar(64) not null,
                last_seen_at varchar(64) not null,
                constraint uq_entity_first_seen_entity unique (entity_name, entity_type)
            )
            """
        )
    engine.dispose()
```

Then add:

```python
def test_migrate_db_command_upgrades_v4_database(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    db_path = data_dir / "fashion-radar.sqlite"
    _create_v4_database(db_path)

    result = CliRunner().invoke(app, ["migrate-db", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output
    with create_sqlite_engine(db_path).connect() as connection:
        version = connection.execute(select(schema_metadata.c.version)).scalar_one()
    assert version == SCHEMA_VERSION
```

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q -k "migrate_db"
```

Expected before implementation: failures because `migrate-db` does not exist.

- [ ] **Step 4: Add future schema rejection test**

Add:

```python
def test_migrate_db_rejects_future_schema_without_traceback(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("update schema_metadata set version = 999")
    engine.dispose()

    result = CliRunner().invoke(app, ["migrate-db", "--data-dir", str(data_dir)])

    assert result.exit_code == 1
    assert "Could not migrate database schema" in result.output
    assert "Unsupported database schema version 999" in result.output
    assert "Traceback" not in result.output
```

- [ ] **Step 5: Add local-only hardening test**

Add a test that proves `migrate-db` only touches the local schema path:

```python
def test_migrate_db_does_not_run_collection_or_review_workflows(
    tmp_path: Path,
    monkeypatch,
) -> None:
    forbidden = [
        "_package_digest_or_exit",
        "collect_configured_sources",
        "dashboard",
        "discover_candidates",
        "match_stored_items",
        "package_daily_digest",
        "write_daily_report_files",
        "load_source_config",
        "load_entity_config",
        "load_scoring_config",
        "load_manual_signal_rows",
        "load_manual_signal_directory_rows",
        "store_manual_signal_rows",
        "build_trend_comparison",
        "query_imported_candidate_evidence",
        "query_imported_candidates",
        "query_imported_entity_deltas",
        "query_imported_signals",
        "query_imported_signals_summary",
    ]

    def fail(name: str):
        def inner(*_args, **_kwargs):
            raise AssertionError(f"{name} should not be called")

        return inner

    for name in forbidden:
        monkeypatch.setattr(cli_module, name, fail(name))

    result = CliRunner().invoke(
        app,
        [
            "migrate-db",
            "--data-dir",
            str(tmp_path / "data"),
        ],
    )

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output
```

## Task 2: Implement Shared Schema Messages And `migrate-db`

**Files:**

- Create: `src/fashion_radar/db/schema_messages.py`
- Modify: `src/fashion_radar/cli.py`

- [ ] **Step 1: Add shared schema guidance messages**

Create `src/fashion_radar/db/schema_messages.py`:

```python
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
```

- [ ] **Step 2: Add doctor status helpers**

In `src/fashion_radar/cli.py`, import:

```python
import re
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

from fashion_radar.db.schema import (
    SCHEMA_VERSION,
    SchemaVersionError,
    initialize_schema,
    metadata as db_metadata,
    schema_metadata,
)
from fashion_radar.db.schema_messages import (
    FUTURE_SCHEMA_HINT,
    MIGRATE_DB_HINT,
    invalid_schema_message,
    missing_schema_message,
    unsupported_schema_message,
)
```

Add:

```python
@dataclass(frozen=True)
class _DatabaseSchemaStatus:
    state: Literal["missing", "current", "old", "future", "invalid"]
    version: int | None = None
    detail: str | None = None
    missing_schema: bool = False
```

Add:

```python
def _inspect_database_schema_status(db_path: Path) -> _DatabaseSchemaStatus:
    if not db_path.exists():
        return _DatabaseSchemaStatus(state="missing")

    engine = create_readonly_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        if "schema_metadata" not in table_names:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="missing schema_metadata table",
                missing_schema=True,
            )

        metadata_columns = {
            column["name"] for column in inspector.get_columns("schema_metadata")
        }
        if "version" not in metadata_columns:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is missing",
            )

        try:
            with engine.connect() as connection:
                raw_version = connection.execute(
                    select(schema_metadata.c.version)
                ).scalar_one_or_none()
        except MultipleResultsFound:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version has multiple rows",
            )
        if raw_version is None:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is empty",
                missing_schema=True,
            )
        version = _parse_schema_version_value(raw_version)
        if version is None:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is not an integer",
            )

        if version < SCHEMA_VERSION:
            return _DatabaseSchemaStatus(state="old", version=version)
        if version > SCHEMA_VERSION:
            return _DatabaseSchemaStatus(state="future", version=version)

        missing_tables = sorted(set(db_metadata.tables) - table_names)
        if missing_tables:
            return _DatabaseSchemaStatus(
                state="invalid",
                version=version,
                detail=f"missing tables: {', '.join(missing_tables)}",
            )
        for table_name, table in sorted(db_metadata.tables.items()):
            actual_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            expected_columns = {column.name for column in table.columns}
            missing_columns = sorted(expected_columns - actual_columns)
            if missing_columns:
                return _DatabaseSchemaStatus(
                    state="invalid",
                    version=version,
                    detail=(
                        f"table {table_name} missing columns: "
                        f"{', '.join(missing_columns)}"
                    ),
                )
        return _DatabaseSchemaStatus(state="current", version=version)
    except SQLAlchemyError as exc:
        return _DatabaseSchemaStatus(state="invalid", detail=str(exc))
    finally:
        engine.dispose()
```

Add:

```python
def _format_database_schema_status(status: _DatabaseSchemaStatus) -> str:
    if status.state == "missing":
        return "Database schema: not initialized"
    if status.state == "current":
        return f"Database schema: v{status.version} (current)"
    if status.state == "old":
        return (
            f"Database schema: v{status.version} (upgrade available; "
            f"{MIGRATE_DB_HINT})"
        )
    if status.state == "future":
        return (
            f"Database schema: v{status.version} "
            f"(unsupported; expected v{SCHEMA_VERSION}). {FUTURE_SCHEMA_HINT}"
        )
    detail = status.detail or "unknown schema problem"
    if status.missing_schema:
        return f"Database schema: invalid: {missing_schema_message(detail)}"
    return f"Database schema: {invalid_schema_message(detail)}"
```

- [ ] **Step 3: Add the command**

Add near `doctor`:

```python
@app.command(name="migrate-db")
def migrate_db(data_dir: Path = DATA_DIR_OPTION) -> None:
    """Initialize or upgrade the local SQLite database schema."""
    db_path = default_database_path(data_dir)
    try:
        engine = create_sqlite_engine(db_path)
        initialize_schema(engine)
        status = _inspect_database_schema_status(db_path)
    except SchemaVersionError as exc:
        message = str(exc)
        version = _parse_schema_version_from_error(message)
        if version is not None:
            message = unsupported_schema_message(version)
        typer.echo(f"Could not migrate database schema: {message}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Could not migrate database schema: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        if "engine" in locals():
            engine.dispose()

    typer.echo(f"Database path: {db_path}")
    typer.echo(_format_database_schema_status(status))
    if status.state != "current":
        raise typer.Exit(1)
```

Add:

```python
def _parse_schema_version_from_error(message: str) -> int | None:
    match = re.search(r"Unsupported schema version ([0-9]+)", message)
    if match is None:
        return None
    return int(match.group(1))
```

Add strict version parsing:

```python
def _parse_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+", value.strip()):
        return int(value)
    return None
```

Then replace the permissive raw version conversion in
`_inspect_database_schema_status()` with:

```python
        version = _parse_schema_version_value(raw_version)
        if version is None:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is not an integer",
            )
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py -q -k "migrate_db"
```

Expected: migrate-db tests pass.

## Task 3: Doctor Schema Status Tests

**Files:**

- Modify: `tests/test_cli.py`
- Modify: `tests/test_stage1_hardening.py`

- [ ] **Step 1: Add current schema status test**

Add:

```python
def test_doctor_reports_current_database_schema(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert f"Database schema: v{SCHEMA_VERSION} (current)" in result.output
```

- [ ] **Step 2: Add missing database non-mutating test**

Add:

```python
def test_doctor_reports_missing_database_without_creating_it(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Database schema: not initialized" in result.output
    assert not db_path.exists()
```

- [ ] **Step 3: Add old schema hint test**

Add:

```python
def test_doctor_reports_old_database_schema_with_migration_hint(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    _create_v4_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: v4 (upgrade available" in result.output
    assert "fashion-radar migrate-db --data-dir" in result.output
```

- [ ] **Step 4: Add future schema status test**

Add:

```python
def test_doctor_reports_future_database_schema_without_migrate_hint(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("update schema_metadata set version = 999")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Database schema: v999 (unsupported; expected v{SCHEMA_VERSION})" in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output
```

Add a future-schema-priority test that proves version comparison happens before
table and column compatibility validation:

```python
def test_doctor_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (999)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Database schema: v999 (unsupported; expected v{SCHEMA_VERSION})" in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output
```

- [ ] **Step 5: Add hardening guard**

In `tests/test_stage1_hardening.py`, add:

```python
def test_doctor_reports_missing_database_without_initializing_sqlite(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    init_result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    assert init_result.exit_code == 0

    def fail(*_args, **_kwargs):
        raise AssertionError("doctor should not initialize or migrate SQLite")

    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail)
    monkeypatch.setattr(cli_module, "initialize_schema", fail)

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Database schema: not initialized" in result.output
    assert "Traceback" not in result.output
    assert not (data_dir / "fashion-radar.sqlite").exists()
```

Also add a `tests/test_cli.py` invalid current-version database test:

```python
def test_doctor_rejects_current_version_database_missing_required_tables(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql(
            f"insert into schema_metadata (version) values ({SCHEMA_VERSION})"
        )
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "missing tables" in result.output
    assert "Traceback" not in result.output
```

Add a current-version missing-column test:

```python
def test_doctor_rejects_current_version_database_missing_required_columns(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    _create_v4_database(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            f"update schema_metadata set version = {SCHEMA_VERSION}"
        )
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "missing columns" in result.output
    assert "platform" in result.output
    assert "Traceback" not in result.output
```

Add existing SQLite missing-schema hint tests:

```python
def test_doctor_reports_existing_sqlite_without_schema_metadata_with_migrate_hint(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table unrelated (id integer primary key)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "missing schema_metadata table" in result.output
    assert "fashion-radar migrate-db --data-dir" in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_schema_metadata_without_version_without_migrate_hint(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (id integer primary key)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is missing" in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output
```

Add an empty-version missing-schema hint test:

```python
def test_doctor_reports_empty_schema_metadata_version_with_migrate_hint(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is empty" in result.output
    assert "fashion-radar migrate-db --data-dir" in result.output
    assert "Traceback" not in result.output
```

And a non-SQLite file test:

```python
def test_doctor_rejects_unreadable_database_without_traceback(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    (data_dir / "fashion-radar.sqlite").write_text("not sqlite", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "Traceback" not in result.output
```

Add malformed version tests:

```python
def test_doctor_rejects_non_integer_database_schema_version(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version text)")
        connection.exec_driver_sql("insert into schema_metadata (version) values ('latest')")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is not an integer" in result.output
    assert "Traceback" not in result.output


def test_doctor_rejects_duplicate_database_schema_versions(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version has multiple rows" in result.output
    assert "Traceback" not in result.output
```

Add a numeric-but-non-integer version test so validation does not silently
truncate malformed values:

```python
def test_doctor_rejects_decimal_database_schema_version(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    db_path = data_dir / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version real)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5.7)")
    engine.dispose()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Database schema: invalid" in result.output
    assert "schema_metadata.version is not an integer" in result.output
    assert "Traceback" not in result.output
```

- [ ] **Step 6: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_stage1_hardening.py -q -k "doctor"
```

Expected before implementation: failures because doctor does not print schema
status or old-schema hints.

## Task 4: Implement Doctor Status And Read-only Hints

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/imported_signals.py`
- Modify: `src/fashion_radar/trends.py`

- [ ] **Step 1: Print schema status from doctor**

After config loading succeeds in `doctor`, add:

```python
    db_path = default_database_path(data_dir)
    status = _inspect_database_schema_status(db_path)
    typer.echo(_format_database_schema_status(status))
    if status.state in {"old", "future", "invalid"}:
        raise typer.Exit(1)
```

- [ ] **Step 2: Improve read-only schema mismatch hints**

In `imported_signals.py`, `trends.py`, and `_verify_candidate_database_schema`
in `cli.py`, import `MIGRATE_DB_HINT`, `missing_schema_message`, and
`unsupported_schema_message` from `fashion_radar.db.schema_messages`.

Use this order in each read-only verifier:

1. Inspect table names.
2. If `schema_metadata` and `schema_metadata.version` can be read, read
   `schema_metadata.version` before required data-table or column checks.
3. If the version is greater than `SCHEMA_VERSION`, raise
   `unsupported_schema_message(version)` immediately.
4. If the version is older than `SCHEMA_VERSION`, raise
   `unsupported_schema_message(version)`.
5. Then validate required tables and columns for current-version databases.

Old or missing schema mismatch errors must include:

```python
MIGRATE_DB_HINT
```

Keep these commands read-only. Do not call `initialize_schema()` from read-only
query paths.

Future-version errors should say:

```text
This database may require a newer Fashion Radar version.
```

Do not add a `migrate-db` hint to future-version errors.

When `schema_metadata.version` can be read, read and compare it before table or
column compatibility checks. If `version > SCHEMA_VERSION`, raise the future
message immediately.

- [ ] **Step 3: Update existing read-only schema tests**

Update existing tests in `tests/test_cli.py`:

- `test_trends_command_rejects_incompatible_database_without_schema_mutation`
  should assert the `migrate-db` guidance remains present and no schema
  mutation happens;
- `test_candidates_command_rejects_incompatible_database_without_schema_mutation`
  should assert the same;
- imported read-only invalid-schema tests for `imported-signals`,
  `imported-signals-summary`, and imported candidates/candidate evidence paths
  should assert no traceback and the same guidance for old/missing schemas.

Add a helper near the other raw schema helpers:

```python
def _create_future_metadata_only_database(path: Path) -> None:
    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer primary key)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (999)")
    engine.dispose()
```

Add read-only future-priority tests for each modified verifier:

```python
def test_trends_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "trends",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_candidates_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_imported_signals_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-01-15T00:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output


def test_imported_signals_summary_command_reports_future_schema_before_missing_table_validation(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    _create_future_metadata_only_database(data_dir / "fashion-radar.sqlite")

    result = CliRunner().invoke(
        app,
        [
            "imported-signals-summary",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in result.output
    assert "This database may require a newer Fashion Radar version." in result.output
    assert "missing tables" not in result.output
    assert "migrate-db" not in result.output
    assert "Traceback" not in result.output
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_stage1_hardening.py -q -k "doctor or migrate_db or invalid_schema"
```

Expected: focused CLI/hardening tests pass.

## Task 5: Docs, Verification, And Release Review

**Files:**

- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`
- Add: `docs/reviews/claude-code-stage-38-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-38-release-review.md`

- [ ] **Step 1: Update docs**

Document:

- `uv run fashion-radar migrate-db --data-dir "$PWD/data"` as a local schema
  initialization/upgrade command;
- `doctor` reports database schema status read-only;
- `migrate-db` does not collect, import, match, score, report, monitor, watch,
  schedule, or touch external platforms.

- [ ] **Step 2: Add changelog entry**

Add:

```markdown
- Added a local `migrate-db` command and read-only `doctor` schema status for
  explicit SQLite schema maintenance.
```

- [ ] **Step 3: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_stage1_hardening.py -q -k "doctor or migrate_db or invalid_schema"
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/cli.py src/fashion_radar/db/schema_messages.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_cli.py tests/test_stage1_hardening.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/cli.py src/fashion_radar/db/schema_messages.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_cli.py tests/test_stage1_hardening.py
```

- [ ] **Step 4: Full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 5: Boundary scans**

Run diff-scoped scans to confirm no dependency, connector, scraping, crawling,
browser automation, login/cookie, account automation, proxy/CAPTCHA, source
acquisition, source ranking, demand proof, watcher, scheduler, generated data,
generated reports, or token changes were introduced.

- [ ] **Step 6: Claude Code release review**

Create release review prompt with the diff, RED/GREEN evidence, verification
evidence, boundary scan evidence, and next phase plan. Required approval phrase:

```text
APPROVED FOR STAGE 38 COMMIT AND PUSH
```

Fix Critical/Important findings before commit.

## Task 6: Commit, Push, And GitHub Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 38 files**

Confirm only Stage 38 files are staged. `uv.lock`, dependency metadata,
generated data, generated reports, generated build artifacts, and unrelated
source files must not be staged.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Add local database schema maintenance" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Push with a one-shot HTTP extraheader. Do not persist the GitHub token.

- [ ] **Step 3: Confirm GitHub Actions**

Poll the latest GitHub Actions run for the pushed commit until it completes.
If it fails, debug with job logs and do not proceed to the next stage.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- GitHub Actions result;
- uncommitted files;
- next step.
