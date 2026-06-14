# Stage 39 Shared Read-only Schema Inspection Design

## Goal

Consolidate the read-only SQLite schema inspection logic introduced in Stage 38
so `doctor`, `trends`, imported-signal review, and candidate review use one
shared implementation for schema version parsing, future-schema precedence,
missing-schema hints, and required table/column validation.

## Scope

In scope:

- Add a focused `fashion_radar.db.schema_inspection` module for read-only schema
  inspection helpers.
- Move the read-only SQLite engine helper into `fashion_radar.db.engine` while
  keeping existing imports working.
- Replace duplicated schema version parsing and required-column helpers in:
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/imported_signals.py`
  - `src/fashion_radar/trends.py`
- Add unit coverage for the shared helper.
- Keep existing Stage 38 CLI behavior and tests green.

Out of scope:

- Schema version changes or migrations.
- New commands or user-facing workflow changes.
- Source connectors, scraping, crawling, browser automation, login/cookie
  flows, account automation, proxy/CAPTCHA handling, source acquisition,
  schedulers, watchers, monitors, or external platform API integrations.
- Dependency or `uv.lock` changes.
- Changing report, dashboard, scoring, matching, import, or collection behavior.

## Design

### Shared Helper Module

Create `src/fashion_radar/db/schema_inspection.py` with small, reusable
read-only helpers:

- `SchemaVersionParser = Callable[[object], int | None]`
- `parse_schema_version_value(value: object) -> int | None`
- `parse_signed_schema_version_value(value: object) -> int | None`
- `read_schema_version_if_available(engine, inspector, table_names, *, version_parser) -> int | None`
- `verify_required_columns(inspector, table_name, required_columns) -> None`
- `verify_readonly_schema(engine, *, required_tables, required_columns_by_table, version_parser) -> None`
- `inspect_database_schema_status(db_path, *, required_columns_by_table, version_parser) -> DatabaseSchemaStatus`

The shared helper preserves Stage 38 semantics:

- read `schema_metadata.version` before required data-table checks when possible;
- report future versions before missing table/column compatibility checks;
- old versions receive the `migrate-db` hint;
- future versions receive the newer-version hint and no `migrate-db` hint;
- missing required tables receive the missing-schema `migrate-db` hint;
- missing columns, duplicate version rows, non-integer versions, and corrupt
  SQLite files remain invalid without implying that `migrate-db` can fix them;
- missing database files are reported as `missing` and do not create files.
- the default schema version parser accepts Python `int` values and unsigned
  integer strings only; booleans, signed strings, decimals, floats, blanks, and
  labels remain invalid.
- CLI status and candidate verification pass a signed-string parser because
  Stage 38 CLI code already accepted `+1` and `-1` strings via
  `_parse_schema_version_value()`. Imported-signal and trend verification keep
  the stricter default unsigned parser.
- required column inputs use ordered sequences of `(table_name, columns)` pairs
  so table/column validation order remains explicit. Missing table names still
  appear sorted in error text.
- verifier-style commands report empty `schema_metadata.version` only after
  required tables and columns have been validated; `doctor` status inspection
  keeps its Stage 38 behavior and reports the empty version before broader
  table/column status checks.
- missing `schema_metadata.version` column remains the raw missing-column error
  for verifier-style commands and the existing `schema_metadata.version is
  missing` status detail for `doctor`.

### Read-only Engine Location

Move the read-only SQLite engine helper to `src/fashion_radar/db/engine.py`:

```python
def create_readonly_sqlite_engine(db_path: Path) -> Engine:
    quoted_path = quote(db_path.as_posix(), safe="/")
    return create_engine(
        f"sqlite:///file:{quoted_path}?mode=ro&uri=true",
        future=True,
    )
```

`trends.py` may continue importing and re-exporting it so existing internal and
external imports do not break.

### Callers

- `doctor` should call `inspect_database_schema_status()` and keep formatting in
  `cli.py`, passing the signed CLI parser and the same sorted table order used
  by Stage 38.
- `_verify_candidate_database_schema()` should call `verify_readonly_schema()`
  with `schema_metadata`, `items`, and `item_entities`, passing the signed CLI
  parser.
- `verify_imported_signals_schema()` should call `verify_readonly_schema()` with
  the imported-signal required table and column set and the default unsigned
  parser.
- `verify_readonly_trend_schema()` should call `verify_readonly_schema()` with
  `schema_metadata`, `items`, `item_entities`, and `entity_first_seen` and the
  default unsigned parser.

## Verification

Focused verification:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py -q -k "schema or doctor or migrate_db or invalid_schema or future_schema_before_missing_table_validation or incompatible_database_without_schema_mutation"
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/db/engine.py src/fashion_radar/db/schema_inspection.py src/fashion_radar/cli.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/db/engine.py src/fashion_radar/db/schema_inspection.py src/fashion_radar/cli.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_schema_inspection.py tests/test_cli.py tests/test_imported_signals.py
```

Release verification:

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
