# Stage 38 Local Schema Maintenance Design

## Goal

Add a local, explicit SQLite schema maintenance path so users can inspect and
upgrade the Fashion Radar database schema without collecting sources, importing
rows, running matching, or generating reports.

## Scope

In scope:

- Add a `migrate-db` CLI command that opens the configured local database with a
  write-capable SQLite engine, calls `initialize_schema(engine)`, and reports
  the resulting schema version.
- Add read-only database schema status output to `doctor`.
- Keep `doctor` non-mutating: it may inspect an existing database read-only, but
  must not create data directories, create SQLite files, or run migrations.
- Validate existing current-version databases read-only: `doctor` must reject a
  database that reports the current schema version but is missing required
  tables or columns.
- Distinguish missing databases from invalid existing databases.
- Improve read-only schema mismatch errors so users know to run
  `fashion-radar migrate-db --data-dir ...` for older/missing schemas.
- Keep future schema errors distinct: a newer Fashion Radar may be required,
  and `migrate-db` must not imply it can downgrade.
- Add focused CLI tests and docs.

Out of scope:

- Source connectors, scraping, crawling, browser automation, login/cookie flows,
  account automation, proxy/CAPTCHA handling, source acquisition, source
  ranking, demand proof, platform coverage checks, watchers, schedulers, or
  external platform API integrations.
- Running collect/match/report/import as part of `doctor` or `migrate-db`.
- Changing schema version, scoring formulas, imported platform provenance, or
  source configuration formats.
- Dependency or `uv.lock` changes.

## Design

### `migrate-db`

`migrate-db` uses the existing `--data-dir` option and derives the database path
with `default_database_path(data_dir)`. It calls:

```python
engine = create_sqlite_engine(default_database_path(data_dir))
initialize_schema(engine)
```

Then it reads `schema_metadata.version` and prints:

```text
Database path: <path>
Database schema: v5 (current)
```

The command is intentionally local. It does not load source configs, collect
feeds, import signal files, run matching/scoring, write reports, package
digests, or start dashboard code.

### `doctor`

After config validation succeeds, `doctor` checks the configured database path:

- missing database: print `Database schema: not initialized` and exit `0`;
- current schema: print `Database schema: v5 (current)` and exit `0`;
- older schema: print an upgrade hint and exit `1`;
- future schema: print `Database schema: vN (unsupported; expected v5)` and
  exit `1` without a `migrate-db` downgrade hint;
- invalid schema: print an invalid schema message and exit `1`.

The database check uses the existing read-only SQLite engine helper. It must not
call `create_sqlite_engine()` or `initialize_schema()`. It must distinguish:

- database file missing;
- existing DB with no `schema_metadata` table;
- existing DB with no `schema_metadata.version` column;
- unreadable/non-SQLite DB files;
- duplicate or non-integer version rows;
- old schema versions;
- future schema versions;
- current version but incomplete tables/columns.

Existing SQLite files with no `schema_metadata` table or with an empty
`schema_metadata.version` value are invalid, but they are also missing-schema
states that the existing `initialize_schema()` path can initialize or stamp.
Their doctor output should include the shared `migrate-db` hint. Existing
SQLite files where the `schema_metadata` table exists but lacks the `version`
column, corrupt/non-SQLite files, and malformed duplicate/non-integer versions
should remain invalid without implying that `migrate-db` can safely fix them.

When `schema_metadata.version` can be read and is greater than
`SCHEMA_VERSION`, `doctor` should classify the database as future before table
or column compatibility checks, so a newer database never receives a downgrade
hint.

### Read-only Commands

Read-only review commands that reject older/missing schemas should include a
short hint:

```text
Run `fashion-radar migrate-db --data-dir ...` to upgrade the local database schema.
```

This keeps read-only commands non-mutating while giving users a safe explicit
maintenance command.

Future schema errors should instead say a newer Fashion Radar version may be
required. No read-only command should auto-run the migration.

Schema guidance strings should be centralized so `trends`, imported-signal
review, candidate review, and doctor do not drift.

## Verification

Focused verification:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_stage1_hardening.py -q -k "doctor or migrate_db or invalid_schema or incompatible_database"
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/cli.py src/fashion_radar/db/schema_messages.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_cli.py tests/test_stage1_hardening.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/cli.py src/fashion_radar/db/schema_messages.py src/fashion_radar/imported_signals.py src/fashion_radar/trends.py tests/test_cli.py tests/test_stage1_hardening.py
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
