# Stage 39 Shared Read-only Schema Inspection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate Stage 38 read-only SQLite schema inspection into one shared helper while preserving existing CLI behavior.

**Architecture:** Add `fashion_radar.db.schema_inspection` as the single source for schema version parsing, read-only version reads, required table/column verification, and database schema status inspection. The shared verifier accepts an ordered `(table_name, columns)` sequence and an injectable schema-version parser so imported/trend verification keeps unsigned parsing while CLI status and candidate verification keep signed-string parsing. Move the quoted read-only SQLite engine helper into `fashion_radar.db.engine` and keep `trends.create_readonly_sqlite_engine` available as an imported alias.

**Tech Stack:** Python, Typer CLI, SQLAlchemy Core, SQLite, pytest, ruff, uv. No dependency, connector, scraping, crawling, platform automation, scheduler, watcher, monitor, or external API changes.

---

## Boundaries

In scope:

- `src/fashion_radar/db/engine.py`
- `src/fashion_radar/db/schema_inspection.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/imported_signals.py`
- `src/fashion_radar/trends.py`
- `tests/test_schema_inspection.py`
- focused updates to `tests/test_cli.py` or `tests/test_imported_signals.py` only if behavior coverage gaps are found
- Stage 39 plan/review artifacts

Out of scope:

- Schema version or migration changes.
- New commands or user-facing behavior changes.
- Source connectors, scraping, crawling, browser automation, login/cookie flow,
  account automation, proxy/CAPTCHA handling, source acquisition, source
  ranking, demand proof, watcher, scheduler, monitor, or external platform API
  work.
- Collecting feeds, importing signal rows, matching, scoring, reporting,
  dashboard startup, or digest packaging from any schema helper.
- Dependency or `uv.lock` changes.

## Task -1: Claude Code Plan Review Gate

This is a user-required audit artifact, not implementation work. The main
coordinating agent must complete it before Task 1 starts, commit the prompt and
review output as Stage 39 artifacts, and not ask implementation workers to rerun
the review once the approval phrase is present.

**Files:**

- Add: `docs/reviews/claude-code-stage-39-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-39-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create `docs/reviews/claude-code-stage-39-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 39 Plan Review Prompt

You are reviewing the Stage 39 shared read-only schema inspection plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Consolidate Stage 38 read-only SQLite schema inspection into one shared helper
while preserving existing CLI behavior.

## Proposed Technical Approach

- Add `src/fashion_radar/db/schema_inspection.py` with shared helpers for strict
  schema version parsing, signed CLI schema version parsing, read-only schema
  version reads, required table/column verification, and
  `DatabaseSchemaStatus` inspection.
- Move `create_readonly_sqlite_engine()` into `src/fashion_radar/db/engine.py`
  and keep `fashion_radar.trends.create_readonly_sqlite_engine` available.
- Replace duplicated schema verification helpers in `cli.py`,
  `imported_signals.py`, and `trends.py`.
- Preserve Stage 38 behavior: missing DB is OK for `doctor`, future schemas are
  reported before compatibility checks, future schemas do not get a `migrate-db`
  hint, old/missing schemas keep the explicit `migrate-db` hint, and read-only
  commands do not mutate SQLite.
- Preserve Stage 38 parser differences: imported-signal and trend verification
  reject signed strings, while CLI database status and candidate verification
  accept signed integer strings.
- Use ordered required-column inputs so table validation order is explicit while
  missing-table names remain sorted in error text.
- Keep all changes local: no connectors, scraping, crawling, browser
  automation, login/cookie/account/proxy/CAPTCHA/source-acquisition/platform
  API functionality, schedulers, watchers, monitors, dependency changes, or
  schema version changes.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-39-shared-readonly-schema-inspection-design.md`
- `docs/superpowers/plans/2026-06-14-stage-39-shared-readonly-schema-inspection-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 39 SHARED READONLY SCHEMA INSPECTION
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-39-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-39-plan-review.md
```

Expected: approval phrase appears, or the plan is revised and rereviewed before
Task 1.

## Task 1: Shared Helper Unit Tests

**Files:**

- Create: `tests/test_schema_inspection.py`

- [ ] **Step 1: Add tests for strict version parsing**

Create `tests/test_schema_inspection.py` with:

```python
from pathlib import Path

import pytest

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import SCHEMA_VERSION, initialize_schema, schema_metadata
from fashion_radar.db.schema_inspection import (
    DatabaseSchemaStatus,
    inspect_database_schema_status,
    parse_schema_version_value,
    parse_signed_schema_version_value,
    verify_readonly_schema,
)
from fashion_radar.db.schema_messages import MIGRATE_DB_HINT, FUTURE_SCHEMA_HINT
from fashion_radar.trends import create_readonly_sqlite_engine


def test_parse_schema_version_value_accepts_int_and_integer_string() -> None:
    assert parse_schema_version_value(5) == 5
    assert parse_schema_version_value("5") == 5


@pytest.mark.parametrize("value", [True, 5.7, "5.7", "+5", "-1", "latest", "", None])
def test_parse_schema_version_value_rejects_non_integer_values(value: object) -> None:
    assert parse_schema_version_value(value) is None


def test_parse_signed_schema_version_value_preserves_cli_signed_strings() -> None:
    assert parse_signed_schema_version_value("+5") == 5
    assert parse_signed_schema_version_value("-1") == -1
    assert parse_signed_schema_version_value("5") == 5
    assert parse_signed_schema_version_value(True) is None
    assert parse_signed_schema_version_value("5.7") is None
```

- [ ] **Step 2: Add helpers for raw schema fixtures**

Add:

```python
def _create_metadata_only_database(path: Path, version: object) -> None:
    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version)")
        connection.exec_driver_sql(
            "insert into schema_metadata (version) values (?)",
            (version,),
        )
    engine.dispose()


def _required_imported_tables() -> tuple[str, ...]:
    return ("schema_metadata", "items", "item_entities")


def _required_imported_columns() -> tuple[tuple[str, set[str]], ...]:
    return (
        ("schema_metadata", {"version"}),
        (
            "items",
            {
                "id",
                "source_name",
                "source_type",
                "url",
                "title",
                "published_at",
                "collected_at",
                "source_weight",
                "summary",
                "platform",
            },
        ),
        (
            "item_entities",
            {
                "id",
                "item_id",
                "entity_name",
                "entity_type",
                "alias",
                "confidence",
            },
        ),
    )
```

- [ ] **Step 3: Add future-priority verifier test**

Add:

```python
def test_verify_readonly_schema_reports_future_before_missing_tables(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, 999)
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError) as exc_info:
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()

    message = str(exc_info.value)
    assert f"Unsupported database schema version 999; expected {SCHEMA_VERSION}" in message
    assert FUTURE_SCHEMA_HINT in message
    assert "missing required tables" not in message
    assert "migrate-db" not in message
```

- [ ] **Step 4: Add missing-table and malformed-version tests**

Add:

```python
def test_verify_readonly_schema_missing_tables_has_migrate_hint(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    db_path.touch()
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError) as exc_info:
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()

    message = str(exc_info.value)
    assert "Database schema is missing required tables" in message
    assert MIGRATE_DB_HINT in message


def test_verify_readonly_schema_rejects_duplicate_versions(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.exec_driver_sql("create table schema_metadata (version integer)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
        connection.exec_driver_sql("insert into schema_metadata (version) values (5)")
    engine.dispose()

    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError, match="schema_metadata.version has multiple rows"):
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()


def test_verify_readonly_schema_rejects_decimal_version(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, 5.7)
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError, match="schema_metadata.version is not an integer"):
            verify_readonly_schema(
                engine,
                required_tables=_required_imported_tables(),
                required_columns_by_table=_required_imported_columns(),
            )
    finally:
        engine.dispose()
```

- [ ] **Step 5: Add doctor status helper tests**

Add:

```python
def test_inspect_database_schema_status_missing_database_is_non_mutating(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing.sqlite"

    status = inspect_database_schema_status(
        db_path,
        required_columns_by_table=_required_imported_columns(),
    )

    assert status == DatabaseSchemaStatus(state="missing")
    assert not db_path.exists()


def test_inspect_database_schema_status_current_database(tmp_path: Path) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()

    status = inspect_database_schema_status(
        db_path,
        required_columns_by_table=(
            (schema_metadata.name, {column.name for column in schema_metadata.columns}),
        ),
    )

    assert status.state == "current"
    assert status.version == SCHEMA_VERSION


def test_inspect_database_schema_status_accepts_signed_cli_parser(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, f"+{SCHEMA_VERSION}")

    status = inspect_database_schema_status(
        db_path,
        required_columns_by_table=(("schema_metadata", {"version"}),),
        version_parser=parse_signed_schema_version_value,
    )

    assert status.state == "current"
    assert status.version == SCHEMA_VERSION


def test_verify_readonly_schema_rejects_signed_version_by_default(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    _create_metadata_only_database(db_path, f"+{SCHEMA_VERSION}")
    engine = create_readonly_sqlite_engine(db_path)
    try:
        with pytest.raises(RuntimeError, match="schema_metadata.version is not an integer"):
            verify_readonly_schema(
                engine,
                required_tables=("schema_metadata",),
                required_columns_by_table=(("schema_metadata", {"version"}),),
            )
    finally:
        engine.dispose()
```

- [ ] **Step 6: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py -q
```

Expected before implementation: import failure because
`fashion_radar.db.schema_inspection` does not exist.

## Task 2: Implement Shared Schema Inspection Module

**Files:**

- Modify: `src/fashion_radar/db/engine.py`
- Create: `src/fashion_radar/db/schema_inspection.py`

- [ ] **Step 1: Move read-only engine helper**

In `src/fashion_radar/db/engine.py`, add:

```python
from urllib.parse import quote
```

and:

```python
def create_readonly_sqlite_engine(path: Path) -> Engine:
    quoted_path = quote(path.as_posix(), safe="/")
    return create_engine(
        f"sqlite:///file:{quoted_path}?mode=ro&uri=true",
        future=True,
    )
```

Keep `create_sqlite_engine()` unchanged.

- [ ] **Step 2: Add shared module**

Create `src/fashion_radar/db/schema_inspection.py`:

```python
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Collection, Literal, Sequence

from sqlalchemy import inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

from fashion_radar.db.engine import create_readonly_sqlite_engine
from fashion_radar.db.schema import SCHEMA_VERSION, schema_metadata
from fashion_radar.db.schema_messages import (
    missing_schema_message,
    unsupported_schema_message,
)


SchemaVersionParser = Callable[[object], int | None]
RequiredColumnsByTable = Sequence[tuple[str, Collection[str]]]


@dataclass(frozen=True)
class DatabaseSchemaStatus:
    state: Literal["missing", "current", "old", "future", "invalid"]
    version: int | None = None
    detail: str | None = None
    missing_schema: bool = False


def parse_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value.strip()):
        return int(value)
    return None


def parse_signed_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+", value.strip()):
        return int(value)
    return None


def read_schema_version_if_available(
    engine: Engine,
    inspector,
    table_names: set[str],
    *,
    version_parser: SchemaVersionParser = parse_schema_version_value,
) -> int | None:
    if "schema_metadata" not in table_names:
        return None
    metadata_columns = {
        column["name"] for column in inspector.get_columns("schema_metadata")
    }
    if "version" not in metadata_columns:
        raise RuntimeError(
            "Database schema table schema_metadata is missing required columns: version"
        )
    try:
        with engine.connect() as connection:
            raw_version = connection.execute(
                select(schema_metadata.c.version)
            ).scalar_one_or_none()
    except MultipleResultsFound as exc:
        raise RuntimeError("schema_metadata.version has multiple rows") from exc
    if raw_version is None:
        return None
    version = version_parser(raw_version)
    if version is None:
        raise RuntimeError("schema_metadata.version is not an integer")
    return version


def verify_required_columns(
    inspector,
    table_name: str,
    required_columns: Collection[str],
) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing = sorted(set(required_columns) - columns)
    if missing:
        raise RuntimeError(
            f"Database schema table {table_name} is missing required columns: "
            f"{', '.join(missing)}"
        )


def verify_readonly_schema(
    engine: Engine,
    *,
    required_tables: Sequence[str],
    required_columns_by_table: RequiredColumnsByTable,
    version_parser: SchemaVersionParser = parse_schema_version_value,
) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    version = read_schema_version_if_available(
        engine,
        inspector,
        table_names,
        version_parser=version_parser,
    )
    if version is not None and version != SCHEMA_VERSION:
        raise RuntimeError(unsupported_schema_message(version))

    missing_tables = sorted(set(required_tables) - table_names)
    if missing_tables:
        raise RuntimeError(
            missing_schema_message(
                f"Database schema is missing required tables: "
                f"{', '.join(missing_tables)}"
            )
        )

    for table_name, columns in required_columns_by_table:
        verify_required_columns(inspector, table_name, columns)
    if version is None:
        raise RuntimeError(missing_schema_message("schema_metadata.version is empty"))


def inspect_database_schema_status(
    db_path: Path,
    *,
    required_columns_by_table: RequiredColumnsByTable,
    version_parser: SchemaVersionParser = parse_schema_version_value,
) -> DatabaseSchemaStatus:
    if not db_path.exists():
        return DatabaseSchemaStatus(state="missing")

    engine = create_readonly_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        if "schema_metadata" not in table_names:
            return DatabaseSchemaStatus(
                state="invalid",
                detail="missing schema_metadata table",
                missing_schema=True,
            )
        metadata_columns = {
            column["name"] for column in inspector.get_columns("schema_metadata")
        }
        if "version" not in metadata_columns:
            return DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is missing",
            )
        try:
            version = read_schema_version_if_available(
                engine,
                inspector,
                table_names,
                version_parser=version_parser,
            )
        except RuntimeError as exc:
            return DatabaseSchemaStatus(state="invalid", detail=str(exc))
        if version is None:
            return DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is empty",
                missing_schema=True,
            )
        if version < SCHEMA_VERSION:
            return DatabaseSchemaStatus(state="old", version=version)
        if version > SCHEMA_VERSION:
            return DatabaseSchemaStatus(state="future", version=version)

        expected_tables = {table_name for table_name, _columns in required_columns_by_table}
        missing_tables = sorted(expected_tables - table_names)
        if missing_tables:
            return DatabaseSchemaStatus(
                state="invalid",
                version=version,
                detail=f"missing tables: {', '.join(missing_tables)}",
            )
        for table_name, columns in required_columns_by_table:
            actual_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            missing_columns = sorted(set(columns) - actual_columns)
            if missing_columns:
                return DatabaseSchemaStatus(
                    state="invalid",
                    version=version,
                    detail=(
                        f"table {table_name} missing columns: "
                        f"{', '.join(missing_columns)}"
                    ),
                )
        return DatabaseSchemaStatus(state="current", version=version)
    except SQLAlchemyError as exc:
        return DatabaseSchemaStatus(state="invalid", detail=str(exc))
    finally:
        engine.dispose()
```

- [ ] **Step 3: Verify GREEN for helper tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py -q
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_trends.py -q -k "readonly or read_only or create_readonly_sqlite_engine or schema"
```

Expected: helper tests and existing read-only engine/trend schema tests pass.

## Task 3: Replace Duplicated Callers

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/imported_signals.py`
- Modify: `src/fashion_radar/trends.py`

- [ ] **Step 1: Update `trends.py`**

Import the read-only engine and shared verifier:

```python
from fashion_radar.db.engine import create_readonly_sqlite_engine
from fashion_radar.db.schema_inspection import verify_readonly_schema
```

Remove duplicated `_read_schema_version_if_available()`,
`_parse_schema_version_value()`, and `_verify_columns()` from `trends.py`.

Implement:

```python
def verify_readonly_trend_schema(engine: Engine) -> None:
    verify_readonly_schema(
        engine,
        required_tables=("schema_metadata", "items", "item_entities", "entity_first_seen"),
        required_columns_by_table=tuple(
            (table.name, {column.name for column in table.columns})
            for table in (schema_metadata, items, item_entities, entity_first_seen)
        ),
    )
```

- [ ] **Step 2: Update `imported_signals.py`**

Import:

```python
from fashion_radar.db.engine import create_readonly_sqlite_engine
from fashion_radar.db.schema_inspection import verify_readonly_schema
```

Remove duplicated `_read_schema_version_if_available()` and
`_parse_schema_version_value()`.

Implement `verify_imported_signals_schema()` with:

```python
def verify_imported_signals_schema(engine: Engine) -> None:
    verify_readonly_schema(
        engine,
        required_tables=("schema_metadata", "items", "item_entities"),
        required_columns_by_table=(
            ("schema_metadata", REQUIRED_SCHEMA_METADATA_COLUMNS),
            ("items", REQUIRED_ITEMS_COLUMNS),
            ("item_entities", REQUIRED_ITEM_ENTITIES_COLUMNS),
        ),
    )
```

Keep `_verify_columns()` only if still used elsewhere; otherwise remove it.

- [ ] **Step 3: Update `cli.py`**

Import:

```python
from fashion_radar.db.schema_inspection import (
    DatabaseSchemaStatus,
    inspect_database_schema_status,
    parse_signed_schema_version_value,
    verify_readonly_schema,
)
```

Remove local `_DatabaseSchemaStatus`, `_inspect_database_schema_status()`,
`_parse_schema_version_value()`, `_read_candidate_schema_version_if_available()`,
and `_verify_candidate_columns()`.

Update doctor:

```python
status = inspect_database_schema_status(
    default_database_path(data_dir),
    required_columns_by_table=tuple(
        (table_name, {column.name for column in table.columns})
        for table_name, table in sorted(db_metadata.tables.items())
    ),
    version_parser=parse_signed_schema_version_value,
)
```

Update candidate verifier:

```python
def _verify_candidate_database_schema(engine) -> None:
    verify_readonly_schema(
        engine,
        required_tables=("schema_metadata", "items", "item_entities"),
        required_columns_by_table=tuple(
            (
                table_name,
                {column.name for column in db_metadata.tables[table_name].columns},
            )
            for table_name in ("schema_metadata", "items", "item_entities")
        ),
        version_parser=parse_signed_schema_version_value,
    )
```

Keep `_format_database_schema_status()` in `cli.py`, but update its parameter
annotation from `_DatabaseSchemaStatus` to `DatabaseSchemaStatus`.

- [ ] **Step 4: Verify behavior preservation**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py -q -k "schema or doctor or migrate_db or invalid_schema or future_schema_before_missing_table_validation or incompatible_database_without_schema_mutation"
```

Expected: focused schema behavior tests pass.

## Task 4: Verification And Release Review

**Files:**

- Add: `docs/reviews/claude-code-stage-39-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-39-release-review.md`

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py -q -k "schema or doctor or migrate_db or invalid_schema or future_schema_before_missing_table_validation or incompatible_database_without_schema_mutation"
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_imported_signals.py tests/test_imported_candidates.py tests/test_imported_candidate_evidence.py tests/test_imported_entity_deltas.py tests/test_dashboard.py -q
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/db/engine.py src/fashion_radar/db/schema_inspection.py src/fashion_radar/cli.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/db/engine.py src/fashion_radar/db/schema_inspection.py src/fashion_radar/cli.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py
```

- [ ] **Step 2: Full release verification**

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

- [ ] **Step 3: Boundary scans**

Run diff-scoped scans to confirm no dependency, connector, scraping, crawling,
browser automation, login/cookie, account automation, proxy/CAPTCHA, source
acquisition, source ranking, demand proof, watcher, scheduler, monitor,
generated data, generated reports, or token changes were introduced.

- [ ] **Step 4: Claude Code release review**

Create release review prompt with the diff summary, RED/GREEN evidence,
verification evidence, boundary scan evidence, and next phase plan. Required
approval phrase:

```text
APPROVED FOR STAGE 39 COMMIT AND PUSH
```

Fix Critical/Important findings before commit.

## Task 5: Commit, Push, And GitHub Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 39 files**

Confirm only Stage 39 files are staged. `uv.lock`, dependency metadata,
generated data, generated reports, generated build artifacts, and unrelated
source files must not be staged.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Share read-only schema inspection" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Push with a one-shot HTTP extraheader. If git smart HTTP fails with the same
TLS transport issue seen in Stage 38, use the GitHub Git Database API fallback
only after verifying the local tree, parent, and remote branch head. Do not
persist the GitHub token.

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
