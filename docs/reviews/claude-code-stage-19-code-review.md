## Critical

None found.

## Important

### 1. `--output-format json` is not JSON-only for invalid `--imported-at`

**File:** `src/fashion_radar/cli.py:383-388`

For `import-signals-dir --output-format json --imported-at not-a-date`, the command emits a plain-text error:

```python
typer.echo(
    f"Could not import signals directory: invalid --imported-at: {exc}",
    err=True,
)
```

This happens before the normal directory diagnostics path, so it bypasses `_print_manual_signal_directory_diagnostics(...)`, which correctly emits JSON for other validation failures.

This violates the review requirement that CLI output be JSON-only when `--output-format json` is used. It also means the currently added invalid-`--imported-at` tests only assert the text path, not the JSON output contract.

**Why this matters:** automation consuming JSON output will fail on this specific validation error, including the explicitly required `--dry-run --imported-at` failure path.

**Suggested fix:** when `output_format == "json"`, emit a structured JSON diagnostic/error payload for invalid `--imported-at` instead of plain text. Add tests for both normal and `--dry-run` invalid `--imported-at` with `--output-format json`, asserting valid JSON and no non-JSON text.

## Minor

### 1. Import-time database failures are not batch-transaction atomic

**File:** `src/fashion_radar/importers/manual_signals.py:416-438`
**Related:** `src/fashion_radar/db/repositories.py:29-65`

`store_manual_signal_rows(...)` calls `ItemRepository.upsert_item(...)` once per row, and each `upsert_item(...)` opens its own `engine.begin()` transaction. If a database/write error occurs after some rows have been upserted, earlier rows remain committed.

I’m listing this as **Minor**, not Important, because Stage 19 explicitly asks to reuse existing `store_manual_signal_rows(...)` semantics, and the main atomicity requirement appears focused on validation-before-import: no SQLite/data-dir creation or partial import when directory/file/timestamp validation fails. That requirement is satisfied by the current flow because all matched files are loaded and validated before `create_sqlite_engine(...)`.

If stronger all-or-nothing database write semantics are desired later, `store_manual_signal_rows(...)` would need a batch transaction or repository helper that accepts an existing connection.

## Positive checks

- Stage 18 dry-run table/JSON shape appears preserved through the existing `ManualSignalDirectoryDryRunResult`/file result models and renderers.
- `--imported-at` is parsed before directory reads, including dry-run.
- Directory matching uses direct children via `iterdir()`, filters `is_file()`, and applies `fnmatch` non-recursively.
- Matched files are all loaded/validated before SQLite engine creation and `data_dir` creation.
- `load_manual_signal_directory_rows(...)` retains validated `ManualSignalRow` instances and returns them for import instead of requiring a second read.
- Unknown/private input fields remain ignored through `ManualSignalRow.model_config = ConfigDict(extra="ignore")`.
- Successful imports reuse `store_manual_signal_rows(...)`, preserving `manual_import` source type and normalized URL upsert behavior.
- Deterministic ordering is maintained for matched paths and count maps.
- Docs review found no high-confidence boundary violations around scraping, platform acquisition/coverage, authorization verification, approval/audit/policy workflows, or market-wide ranking claims.

Not approved
