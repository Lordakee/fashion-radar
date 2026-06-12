## Critical

None found.

## Important

None found.

## Minor

None found.

## Rereview notes

1. **Important JSON-only finding is fixed.**
   In `src/fashion_radar/cli.py:380-398`, invalid `--imported-at` is caught before the directory load path. When `--output-format json` is selected, the command now emits:

   - `ManualSignalDirectoryDryRunResult.model_dump_json(indent=2)`
   - with finding code `invalid_imported_at`
   - and exits with status `1`

   The table/text path is preserved for non-JSON output via `typer.echo(message, err=True)`.

2. **JSON diagnostic shape is compatible with dry-run result shape and does not leak import fields.**
   `_invalid_imported_at_directory_result(...)` in `src/fashion_radar/cli.py:451-470` returns a `ManualSignalDirectoryDryRunResult`.

   That model’s fields in `src/fashion_radar/importers/manual_signals.py:119-132` are dry-run diagnostic fields only:

   - `directory`
   - `input_format`
   - `pattern`
   - `file_count`
   - `valid_file_count`
   - `row_count`
   - `error_count`
   - `source_name_counts`
   - `platform_counts`
   - `files`
   - `findings`

   The import-summary fields are only on `ManualSignalDirectoryImportResult` in `src/fashion_radar/importers/manual_signals.py:146-157`, and that object is constructed only after successful directory loading and SQLite import. I do not see a path where `rows`, `rows_imported`, or `items_added` can leak into the invalid timestamp JSON diagnostic.

3. **Invalid timestamp still avoids directory reads, SQLite opening, and artifact creation.**
   The order in `import_signals_dir_command` is correct:

   - `--imported-at` parsed first: `src/fashion_radar/cli.py:380-384`
   - invalid timestamp exits in the `except` block: `src/fashion_radar/cli.py:385-398`
   - directory loading starts only afterward: `src/fashion_radar/cli.py:400-405`
   - SQLite opening/import starts only after successful load and validation: `src/fashion_radar/cli.py:414-420`

   Because the invalid timestamp path exits before `load_manual_signal_directory_rows(...)`, it also avoids the missing-directory/`invalid_directory` diagnostic and file reads. The added tests in `tests/test_cli.py:1553-1648` cover JSON output for both normal and `--dry-run` invalid timestamp paths and assert no community lint artifacts are created.

4. **No new Critical or Important issues introduced.**
   I found no high-confidence regressions in the changed CLI flow, JSON shape, dry-run compatibility, artifact avoidance, or text-output preservation.

Approved for Stage 19 release
