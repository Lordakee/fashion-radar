# Community Signal Quality

`community-signal-lint` checks one local community signal CSV/JSON file before
`import-signals --dry-run` or import. It is useful when another local tool writes
sanitized handoff rows for Fashion Radar.

The command is read-only. It does not import rows, open SQLite, create
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
uv run fashion-radar community-signal-lint ./community-signals.csv --input-format csv --source-name "Community Tool Export" --strict
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export" --dry-run
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export"
```

## Output

Table output:

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

Exit codes:

- `0`: no errors.
- `1`: one or more errors.
- `1` with `--strict`: one or more errors or warnings.

## Severity

- `error`: the file does not fit the community handoff contract or a row is not
  import-ready.
- `warning`: the file is import-ready but may lose useful local provenance or
  may upsert duplicate URLs.
- `info`: the file is import-ready and the importer will use a default value.

## Finding Codes

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

The linter checks local file quality only. It is not a connector, source pack,
platform search, social monitoring system, source-acquisition workflow,
ranking system, demand proof, platform coverage metric, audit workflow,
compliance review, safety workflow, approval UI, or legal review.

`platform` and `source_name` are provenance labels for local review. They do not
claim complete visibility into a platform or community.
