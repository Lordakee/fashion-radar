# Community Signal Quality

`community-signal-lint` checks one local community signal CSV/JSON file before
`import-signals --dry-run` or import. `community-signal-lint-dir` applies the
same checks to matched regular files directly under one local directory. These
commands are useful when another local tool writes sanitized handoff rows for
Fashion Radar.

The commands are read-only. They do not import rows, open SQLite, create
config/data/report directories, collect sources, fetch URLs, search platforms,
monitor communities, package digests, run matching/scoring, or create dashboard
state.

## Commands

Lint CSV:

```bash
uv run fashion-radar community-signal-lint ./community-signals.csv --input-format csv
```

Lint JSON:

```bash
uv run fashion-radar community-signal-lint ./community-signals.json --input-format json
```

Print JSON diagnostics:

```bash
uv run fashion-radar community-signal-lint ./community-signals.json --input-format json --format json
```

Lint all matched CSV handoff files directly under one local directory:

```bash
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv"
```

Lint matched JSON handoff files and print aggregate JSON diagnostics:

```bash
uv run fashion-radar community-signal-lint-dir ./exports --input-format json --pattern "*.json" --format json
```

Use the same fallback source name you plan to use during dry run/import:

```bash
uv run fashion-radar community-signal-lint ./community-signals.csv --input-format csv --source-name "Community Tool Export"
```

Fail on warnings as well as errors:

```bash
uv run fashion-radar community-signal-lint ./community-signals.csv --input-format csv --strict
```

Recommended order:

```bash
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Community Tool Export" --strict
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --dry-run
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export" --unmatched-only
uv run fashion-radar community-signal-lint ./community-signals.csv --input-format csv --source-name "Community Tool Export" --strict
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export" --dry-run
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export"
```

Use `community-signal-lint-dir` first for strict community handoff quality.
Use `import-signals-dir --dry-run` next when you want the broader manual
importer model to validate matched local files without writing rows. Then use
`import-signals-dir` without `--dry-run` to import the same local files only
after the full matched set validates.
Use `imported-review-workflow` when you want a printed, copyable local sequence
for existing post-import review commands without executing anything.
Use `imported-signals-summary` after import to inspect retained row counts by
stored `source_name`. Use `imported-entity-deltas` after matching to compare
stored matched entities across collected-at windows. Use
`imported-signals --unmatched-only` for row-level review of retained local rows
without stored matches.

Directory linting is non-recursive in this version. A pattern such as `*.csv`
matches regular files directly under the supplied directory only. Nested files
are ignored, and `**/*.csv` does not recurse.

## Output

Single-file table output:

```text
Community signal file: examples/community-signals.example.csv
Input format: csv
Rows: 2 total, 2 import-ready
Fields: collected_at=2, platform=2, published_at=2, source_name=2, source_weight=2, summary=2, title=2, url=2
Sources: Community Tool Export=2
Platforms: community=2
Findings: 0 errors, 0 warnings, 0 info
No community-signal quality findings.
```

JSON output has stable top-level keys:

```json
{
  "path": "examples/community-signals.example.csv",
  "input_format": "csv",
  "row_count": 2,
  "valid_row_count": 2,
  "field_counts": {
    "collected_at": 2,
    "platform": 2,
    "published_at": 2,
    "source_name": 2,
    "source_weight": 2,
    "summary": 2,
    "title": 2,
    "url": 2
  },
  "source_name_counts": {
    "Community Tool Export": 2
  },
  "platform_counts": {
    "community": 2
  },
  "findings": []
}
```

Directory table output starts with aggregate counts, then one line per matched
file, then a finding table that includes directory-level and per-file findings:

```text
Community signal directory: exports
Input format: csv
Pattern: *.csv
Files: 2
Rows: 3 total, 2 import-ready
Fields: platform=2, published_at=3, source_name=2, title=3, url=3
Sources: Community Tool Export=2
Platforms: community=2
Findings: 1 errors, 3 warnings, 2 info
Files:
- exports/a.csv: 2 rows, 2 import-ready, 0 errors, 0 warnings, 0 info
- exports/b.csv: 1 rows, 0 import-ready, 1 errors, 3 warnings, 2 info
Severity | File | Code | Row | Field | Message
error | exports/b.csv | invalid_row | 2 | row | Row is not import-ready: ...
```

Directory JSON output has stable aggregate keys:

```json
{
  "directory": "exports",
  "input_format": "csv",
  "pattern": "*.csv",
  "file_count": 2,
  "row_count": 3,
  "valid_row_count": 2,
  "error_count": 1,
  "warning_count": 3,
  "info_count": 2,
  "field_counts": {
    "platform": 2,
    "published_at": 3,
    "source_name": 2,
    "title": 3,
    "url": 3
  },
  "source_name_counts": {
    "Community Tool Export": 2
  },
  "platform_counts": {
    "community": 2
  },
  "files": [
    {
      "path": "exports/a.csv",
      "input_format": "csv",
      "row_count": 2,
      "valid_row_count": 2,
      "field_counts": {},
      "source_name_counts": {},
      "platform_counts": {},
      "findings": []
    },
    {
      "path": "exports/b.csv",
      "input_format": "csv",
      "row_count": 1,
      "valid_row_count": 0,
      "field_counts": {},
      "source_name_counts": {},
      "platform_counts": {},
      "findings": [
        {
          "severity": "error",
          "code": "invalid_row",
          "message": "Row is not import-ready: ...",
          "row": 2,
          "field": "row"
        }
      ]
    }
  ],
  "findings": []
}
```

Exit codes:

- `0`: no errors.
- `1`: one or more errors, including invalid directory or no matching files.
- `1` with `--strict`: one or more errors or warnings.

## Severity

- `error`: the file does not fit the community handoff contract or a row is not
  import-ready.
- `warning`: the file is import-ready but may lose useful local provenance or
  may upsert duplicate URLs.
- `info`: the file is import-ready and the importer will use a default value.

## Finding Codes

- `invalid_directory`: the supplied directory cannot be read or is not a
  directory.
- `no_matching_files`: a directory pattern matched zero regular direct-child
  files.
- `invalid_file`: the file cannot be read, parsed, or shaped as CSV rows, a JSON
  list, or a JSON object with only an `items` list.
- `csv_extra_cells`: a CSV row has more cells than headers.
- `unknown_field`: a field is outside the community signal contract.
- `prohibited_field`: a raw/private/account/media/session field is excluded
  from community signal files.
- `invalid_row`: a row fails the same required-field, timestamp, or
  `source_weight` validation used by `import-signals`.
- `empty_signal_file`: the file contains zero rows.
- `missing_source_name`: a row omits `source_name`, so import will use the
  fallback source name.
- `missing_platform`: a row omits a short provenance label.
- `missing_summary`: a row omits a short sanitized review note.
- `duplicate_url`: multiple rows share the same URL, so import upsert behavior
  may collapse them to one item.
- `collected_before_published`: `collected_at` is earlier than `published_at`.
- `implicit_source_weight`: a row omits `source_weight`, so the default local
  score weight is used.
- `implicit_collected_at`: a row omits `collected_at`, so import time is used.

## Allowed Fields

Community signal files should contain only:

- `url`
- `title`
- `published_at`
- `summary`
- `source_name`
- `platform`
- `source_weight`
- `collected_at`

Do not include raw comments, full post bodies, private messages, author handles,
account IDs, follower lists, profile URLs, images, videos, cookies, sessions,
tokens, or other account/private material. Keep `summary` short and sanitized.

## Limits

The linters check local file quality only. Directory linting reads matched
regular files directly under one local directory and does not recurse. These
commands are not connectors, source packs, platform search, social monitoring,
source-acquisition workflows, ranking systems, demand proof, platform coverage
metrics, audit workflows, compliance reviews, safety workflows, approval UIs,
or legal review.

`platform` and `source_name` are provenance labels for local review. They do not
claim complete visibility into a platform or community.
