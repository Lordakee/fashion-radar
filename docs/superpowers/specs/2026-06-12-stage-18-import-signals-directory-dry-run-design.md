# Stage 18 Import Signals Directory Dry Run Design

## Goal

Add a local, read-only directory dry-run command for batches of already
sanitized community signal CSV/JSON handoff files. This gives users a bridge
between `community-signal-lint-dir` and single-file `import-signals --dry-run`
without writing SQLite state or importing rows.

Stage 18 improves local batch handoff confidence. It does not add collection,
platform connectors, platform search, scraping, browser automation, account
automation, platform APIs, source acquisition, bulk import, background
monitoring, ranking claims, authorization verification, or policy workflow
features.

## Recommended Command

Add a flat command:

```bash
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run
fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --dry-run
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run --output-format json
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --dry-run
```

The command uses the `import-signals-dir` naming family because it exercises
the same importer model as `import-signals --dry-run`. Stage 18 requires
`--dry-run`; without it, the command exits non-zero before reading files. A
future stage can add deliberate batch import behavior after this dry-run result
shape is stable.

## Behavior

- `DIRECTORY` is a local directory path supplied by the user.
- `--format csv|json` is required, matching existing `import-signals`. The
  command does not infer format from file names.
- `--pattern TEXT` is required. Examples are `*.csv` and `*.json`.
- `--dry-run` is required in Stage 18. Without it, the command prints a stable
  message and exits non-zero without reading files or creating artifacts.
- `--output-format table|json` controls diagnostics output. It is separate from
  `--format`, which remains the input file format.
- matching is non-recursive.
- only regular files directly under `DIRECTORY` are dry-run validated.
- enumeration uses `directory.iterdir()` plus `fnmatch.fnmatch(path.name,
  pattern)`, not `Path.glob()` or `rglob()`, so `**/*.csv` cannot recurse.
- matched paths are sorted deterministically by path string.
- every matched file is passed to `load_manual_signal_rows()` using the same
  fallback source-name behavior as `import-signals --dry-run`.
- a bad file does not hide clean file results.
- invalid or unreadable directories produce a stable directory-level
  `invalid_directory` error.
- zero matched regular direct-child files produce a directory-level
  `no_matching_files` error.
- per-file parse/validation failures produce file-level `invalid_file` errors.
- successful files report row counts, source-name counts, and platform counts.
- output is printed before exit handling.
- errors exit non-zero.
- success exits zero.
- the command has no `--data-dir`, `--config-dir`, `--reports-dir`, or
  `--imported-at` option in Stage 18 because it is read-only validation only.
- the command does not create config/data/report directories, open SQLite,
  import rows, collect sources, fetch URLs, match entities, score, generate
  reports, package digests, touch dashboard state, or run platform tooling.

## Result Shape

JSON output should be stable:

```json
{
  "directory": "exports",
  "input_format": "csv",
  "pattern": "*.csv",
  "file_count": 2,
  "valid_file_count": 1,
  "row_count": 2,
  "error_count": 1,
  "source_name_counts": {
    "Community Tool Export": 2
  },
  "platform_counts": {
    "community": 2
  },
  "files": [
    {
      "path": "exports/a.csv",
      "row_count": 2,
      "error_count": 0,
      "source_name_counts": {
        "Community Tool Export": 2
      },
      "platform_counts": {
        "community": 2
      },
      "findings": []
    },
    {
      "path": "exports/b.csv",
      "row_count": 0,
      "error_count": 1,
      "source_name_counts": {},
      "platform_counts": {},
      "findings": [
        {
          "severity": "error",
          "code": "invalid_file",
          "message": "Could not dry-run import file: row 2: ...",
          "path": "exports/b.csv"
        }
      ]
    }
  ],
  "findings": []
}
```

Top-level `findings` are reserved for directory-level errors such as
`invalid_directory` and `no_matching_files`. Per-file parse/validation failures
remain inside the corresponding file result.

Table output should show aggregate summary first, followed by one line per file
and finding details:

```text
Import signals directory dry run: exports
Input format: csv
Pattern: *.csv
Files: 2 total, 1 valid
Rows: 2 import-ready
Sources: Community Tool Export=2
Platforms: community=2
Errors: 1
Files:
- exports/a.csv: 2 rows, 0 errors
- exports/b.csv: 0 rows, 1 errors
Severity | File | Code | Message
error | exports/b.csv | invalid_file | Could not dry-run import file: row 2: ...
```

## Directory Findings

Errors:

- `invalid_directory`: directory cannot be read or is not a directory.
- `no_matching_files`: pattern matched zero regular files directly under the
  directory.
- `invalid_file`: a matched file cannot be parsed or validated by
  `load_manual_signal_rows()`.

Directory-level finding messages should be stable. File-level validation
messages may include the existing importer error details because the dry-run
command is meant to explain why an import dry-run would fail.

Stable directory-level messages:

| Code | Condition | Message |
| --- | --- | --- |
| `invalid_directory` | supplied path is missing or not a directory | `Manual signal directory does not exist or is not a directory.` |
| `invalid_directory` | directory existence check or direct-child enumeration raises `OSError` | `Could not read manual signal directory.` |
| `no_matching_files` | no regular direct-child files match `--pattern` | `No regular files matched the pattern in the directory.` |

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
- `CHANGELOG.md`

Process artifacts:

- `docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md`
- `docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md`
- Stage 18 Claude Code plan/code review prompts and results.

## Non-Goals

Stage 18 does not implement or document:

- social-platform connectors, platform search, remote community ingestion, or
  automated social collection;
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or source-acquisition
  workflows;
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA/rate-limit/access-control/paywall
  bypass;
- official or unofficial social platform APIs;
- instructions for obtaining platform/community exports;
- raw comments, full post bodies, private messages, author handles, account IDs,
  follower lists, profile URLs, images, videos, media downloading, reposting, or
  archive redistribution;
- recursive directory scanning, watch folders, background jobs, schedulers, or
  automatic imports;
- multi-file import, SQLite writes, DB migrations, collector changes,
  source-health changes, dashboard changes, report semantics changes, matcher
  behavior changes, persistent adapter tables, or scoring algorithm changes;
- product-facing compliance review, audit workflow, safety workflow, approval
  UI, authorization verification, policy checklist, or legal review feature.

## Testing

Focused tests should prove:

- directory dry-run enumerates matched regular files in deterministic sorted
  path order;
- matching is non-recursive and `**/*.csv` does not recurse;
- invalid directory and no matching files are stable directory-level errors;
- unreadable directory handling does not leak exception text or tracebacks;
- a bad file does not hide clean file results;
- aggregate counts include file count, valid file count, row count, errors,
  source counts, and platform counts;
- fallback source-name behavior matches single-file import dry-run behavior;
- table and JSON output shapes are stable;
- CLI help, table output, JSON output, failure exit behavior, success exit
  behavior, and no-artifact behavior are covered.

No test should call the network, run collectors, invoke platform/social tooling,
open SQLite, create config/data/report directories, or require external account
data.

## Documentation

Docs should say the command reads matched regular files directly under one local
directory, does not recurse, does not import rows, does not open SQLite, does
not create config/data/report directories, does not fetch URLs, and does not
verify authorization or platform coverage.

The public docs should position the workflow as:

```bash
community-signal-lint-dir
import-signals-dir --dry-run
import-signals --dry-run  # optional single-file final check
import-signals            # existing single-file import
```

No documentation should explain how to obtain platform/community files.

## Verification

Required before Stage 18 code review:

- focused manual-signal directory dry-run tests;
- focused CLI tests;
- full `pytest -q`;
- `ruff check .`;
- `ruff format --check .`;
- `git diff --check`;
- CodeGraph status;
- Claude Code code review with `--effort max`.
