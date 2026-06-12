# Claude Code Stage 19 Code Rereview Prompt

You are rereviewing Stage 19 implementation for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

The initial code review result is:

- `docs/reviews/claude-code-stage-19-code-review.md`

It found one Important issue:

- `import-signals-dir --output-format json --imported-at not-a-date` emitted
  plain text instead of JSON.

## Fix Implemented

The implementation now:

- emits a `ManualSignalDirectoryDryRunResult`-shaped JSON diagnostic for invalid
  `--imported-at` when `--output-format json` is supplied;
- uses finding code `invalid_imported_at`;
- applies this to both normal import and `--dry-run`;
- still validates `--imported-at` before reading the directory or creating
  artifacts;
- preserves the text error path when `--output-format table` is used.

New tests were added for:

- invalid `--imported-at` with JSON output;
- invalid `--dry-run --imported-at` with JSON output.

## Verification After Fix

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_cli.py -q -k "invalid_imported_at or invalid_dry_run_imported_at" -p no:cacheprovider
# 5 passed, 93 deselected

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_manual_signal_import.py tests/test_cli.py -q -k "directory_load or directory_import or directory_dry_run or import_signals_dir" -p no:cacheprovider
# 31 passed, 109 deselected

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
# 397 passed

.venv/bin/python -m ruff check . --no-cache
# All checks passed!

.venv/bin/python -m ruff format --check .
# 78 files already formatted

git diff --check
# exit 0
```

## Review Request

Please verify:

1. The Important JSON-only finding is fixed.
2. The new JSON diagnostic shape is compatible with the dry-run result shape and
   does not leak rows or import summary fields.
3. The invalid timestamp path still avoids directory reads, SQLite opening, and
   artifact creation.
4. No new Critical or Important issues were introduced.

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 19 release`
- `Not approved`

Do not modify files.
