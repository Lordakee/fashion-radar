# Stage 19 Import Signals Directory Execution Design

## Goal

Enable `fashion-radar import-signals-dir` to import batches of user-provided
local CSV/JSON manual signal files after the Stage 18 directory dry-run result
shape has been stabilized.

Stage 19 keeps the project local-first. It does not add platform connectors,
platform search, scraping, crawling, browser automation, account automation,
platform APIs, source export acquisition, watch folders, schedulers, background
jobs, dashboard ingestion, ranking claims, or policy workflow features.

## Recommended Command

Keep the Stage 18 dry-run commands unchanged:

```bash
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run
fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --dry-run --output-format json
```

Add actual local directory import when `--dry-run` is omitted:

```bash
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --data-dir ./data
fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --data-dir ./data --imported-at 2026-06-12T12:00:00Z
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export"
```

The command remains an importer command. It reads only files already present on
the local filesystem and never attempts to discover, fetch, search, scrape, or
download exports from social platforms or websites.

## Behavior

- `DIRECTORY` is a local directory path supplied by the user.
- `--format csv|json` is required and describes the input file format.
- `--pattern TEXT` is required and is applied only to direct child file names.
- Matching remains non-recursive, deterministic, and based on:
  - `directory.iterdir()`
  - `path.is_file()`
  - `fnmatch.fnmatch(path.name, pattern)`
  - `sorted(paths, key=lambda path: str(path))`
- `--dry-run` keeps the exact Stage 18 behavior and output shape.
- If `--imported-at` is supplied, it is validated even during `--dry-run`.
  This catches bad production commands early. The parsed timestamp is unused
  while dry-running because no rows are written.
- Without `--dry-run`, the command validates every matched file before opening
  SQLite or creating `--data-dir`.
- If directory validation fails, no database is opened and no project artifacts
  are created.
- If any matched file fails importer-model validation, no database is opened
  and no rows are imported from otherwise-clean files.
- If validation succeeds, all loaded rows are passed to the existing
  `store_manual_signal_rows()` function and stored with source type
  `manual_import`.
- `--source-name` remains the fallback source name for rows that omit or blank
  `source_name`.
- `--imported-at` is optional for actual import and follows the same UTC parsing
  behavior as single-file `import-signals`.
- `--data-dir` is available only because actual import writes the existing
  `fashion-radar.sqlite` database.
- `--output-format table|json` remains diagnostics-oriented:
  - dry-run success or failure prints the Stage 18 dry-run result;
  - import validation failure prints the same dry-run-style diagnostics and
    exits non-zero;
  - import success prints a compact import summary in table or JSON form.
- Dry-run JSON must continue to serialize only
  `ManualSignalDirectoryDryRunResult` with the exact Stage 18 top-level fields.
  New Stage 19 loader state such as loaded rows must not appear in dry-run JSON.

## Success Output

Table output for a successful import:

```text
Validated 3 manual signal rows across 2 files
Imported 3 manual signal rows
Items added: 2
Sources: Community Tool Export=2, Manual Import=1
Platforms: instagram=2, x=1
```

JSON output for a successful import:

```json
{
  "directory": "exports",
  "input_format": "csv",
  "pattern": "*.csv",
  "file_count": 2,
  "row_count": 3,
  "rows_imported": 3,
  "items_added": 2,
  "source_name_counts": {
    "Community Tool Export": 2,
    "Manual Import": 1
  },
  "platform_counts": {
    "instagram": 2,
    "x": 1
  }
}
```

`items_added` may be lower than `rows_imported` because the existing repository
upserts by normalized URL. This matches single-file `import-signals` behavior.

## Failure Output

Directory and file validation failures reuse the Stage 18 dry-run diagnostics
shape. This keeps one stable validation contract for both dry-run and failed
import attempts.

Examples:

- missing or file path instead of directory: `invalid_directory`;
- unreadable directory: `invalid_directory`;
- zero matched direct-child regular files: `no_matching_files`;
- invalid CSV/JSON or invalid row: per-file `invalid_file`.

Invalid `--imported-at` is reported before reading files or creating `--data-dir`
with the existing single-file wording pattern:

```text
Could not import signals directory: invalid --imported-at: ...
```

## Files

Modify:

- `src/fashion_radar/importers/manual_signals.py`
- `src/fashion_radar/cli.py`
- `tests/test_manual_signal_import.py`
- `tests/test_cli.py`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `README.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

Process artifacts:

- `docs/reviews/claude-code-stage-19-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-19-plan-review.md`
- possible rereview and code-review prompt/result files, if Claude Code asks for
  changes or after implementation is ready for upload.

## Testing Requirements

Module tests:

- directory load helper returns rows and the Stage 18-compatible validation
  result for clean files;
- mixed clean plus invalid files returns validation errors and no rows for
  import execution;
- import summary model renders deterministic source/platform counts;
- static source guard continues to prevent `Path.glob()` and `rglob()` in the
  directory matching path.

CLI tests:

- help now lists `--data-dir` and `--imported-at`;
- dry-run output and JSON shape remain compatible with Stage 18;
- successful CSV directory import creates SQLite rows;
- successful JSON directory import supports `--output-format json`;
- duplicate URLs across files show `rows_imported` greater than or equal to
  `items_added`;
- invalid directory, unreadable directory, no matches, invalid file, invalid
  `--imported-at`, and invalid `--dry-run --imported-at` do not create
  data/config/report artifacts;
- validation failure with one clean file and one bad file imports nothing;
- validation failure uses a valid first sorted matched file and invalid later
  sorted matched file so tests prove import does not happen incrementally during
  validation;
- non-recursive matching remains covered.

Release checks:

- focused pytest for manual signal importer and CLI directory import tests;
- full pytest;
- `ruff check .`;
- `ruff format --check .`;
- `uv lock --check --default-index https://pypi.org/simple`;
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`;
- wheel build to `/tmp`;
- wheel install smoke test using the Tsinghua mirror;
- secret scan and artifact scan before commit.

## Open Decisions

Use the recommended approach:

- implement actual import for explicit local directories only;
- do not add recursive import, background import, watch folders, scheduler
  integration, platform acquisition, or collector adapters;
- do not introduce a new dependency or change the lockfile;
- keep validation and import summaries small and deterministic.
