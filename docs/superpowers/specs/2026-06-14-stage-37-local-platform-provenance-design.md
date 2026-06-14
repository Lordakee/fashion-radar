# Stage 37 Local Platform Provenance Design

## Goal

Preserve the sanitized `platform` provenance label from local manual/community
signal handoff files through SQLite storage and local review outputs.

## Scope

In scope:

- Add nullable `items.platform` storage with schema v5 migration.
- Add optional `platform` persistence to the item repository.
- Persist manual signal `row.platform` when storing local CSV/JSON handoff rows.
- Preserve `platform` on upsert updates without storing private/raw fields such
  as handles, comments, account IDs, browser profiles, cookies, or session data.
- Expose `platform` in local `imported-signals` review rows, counts, and table
  output.
- Expose local platform counts in `imported-signals-summary` output.
- Update manual/community signal docs to say `platform` is retained as local
  provenance only, not coverage proof.
- Add focused tests and Stage 37 review artifacts.

Out of scope:

- Source connectors, scraping, crawling, browser automation, login/cookie flows,
  account automation, proxy pools, CAPTCHA bypass, source acquisition, source
  ranking, demand proof, platform coverage verification, watchers, schedulers,
  or external platform API integrations.
- Changing heat-score formulas to use platform spread.
- Storing raw social handles, account IDs, comments, private exports, local
  paths, cookies, session files, browser profiles, or generated reports.
- Dependency or `uv.lock` changes.

## Design

### Storage

Add a nullable `platform` column to the `items` table and bump
`SCHEMA_VERSION` from 4 to 5. New databases get the column from metadata; v4
databases migrate with:

```sql
alter table items add column platform varchar(64)
```

The migration updates `schema_metadata.version` to 5.

### Repository

`ItemRepository.upsert_item()` gets an optional keyword-only
`platform: str | None = None` parameter. The repository trims whitespace,
collapses blank labels to `None`, and writes `platform` on insert and update.
Existing RSS/GDELT callers omit it, so stored platform remains `NULL` for
collector rows. The shared `CollectedItem` model stays generic and does not gain
a platform field.

### Manual Import

`store_manual_signal_rows()` passes `row.platform` into
`ItemRepository.upsert_item(platform=...)`. This preserves the already-parsed
and already-sanitized local label while continuing to drop `author_handle`,
`raw_comment`, `account_id`, and any unknown/private fields.

### Review Output

`ImportedSignalItem` gets `platform: str | None = None`. `query_imported_signals`
includes it in JSON/CLI object output, adds `platform_counts` excluding `NULL`
labels, and `render_imported_signals_table()` adds a `Platforms:` summary line
plus a `Platform` column.

`ImportedSignalsSourceSummary` gets top-level `platform_counts`, and
`render_imported_signals_summary_table()` adds a `Platforms:` summary line.
Source summary remains grouped by stored `source_name` for backward
compatibility.

## Verification

Focused verification:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py -q -k "schema or platform or imported_signals or import_signals"
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/db/schema.py src/fashion_radar/db/repositories.py src/fashion_radar/importers/manual_signals.py src/fashion_radar/imported_signals.py tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/db/schema.py src/fashion_radar/db/repositories.py src/fashion_radar/importers/manual_signals.py src/fashion_radar/imported_signals.py tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py
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
