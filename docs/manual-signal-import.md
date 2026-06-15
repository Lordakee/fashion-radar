# Manual Signal Import

Manual signal import lets a user add local, user-provided CSV or JSON files to
the same SQLite item store used by the normal Fashion Radar workflow. Imported
rows are local signals only. They can be matched, reported, and reviewed as
candidate signals, but they do not turn Fashion Radar into a platform collector
or complete social-listening system.

Fashion Radar does not collect these rows from platforms, log in to accounts,
fetch private pages, download media, or provide instructions for obtaining
exports from social platforms. Users are responsible for importing only files
and rows they are authorized to process.

## Input Formats

CSV files must include a header row. JSON files may be an array of item objects
or an object with an `items` array.

Required fields:

- `url`: source URL or stable reference URL for the item.
- `title`: item title or short observed text.
- `published_at`: publication timestamp in an ISO 8601-compatible format.

Optional fields:

- `summary`: short item summary or note.
- `source_name`: display name for the local source. If omitted, the command's
  `--source-name` value is used.
- `platform`: short local provenance label for varied imported files. When
  present, it is preserved on retained `manual_import` rows in SQLite and may
  appear in imported-signal review output. It is not platform coverage, source
  acquisition, demand proof, or a claim of complete platform visibility.
- `source_weight`: numeric source weight for local scoring.
- `collected_at`: timestamp for when the item entered the local file.

CSV example:

```csv
url,title,published_at,summary,source_name,platform,source_weight
https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,Short note,Manual Export,manual,1.4
```

JSON example:

```json
{
  "items": [
    {
      "url": "https://example.com/b",
      "title": "Mary Jane flats",
      "published_at": "2026-06-12T09:00:00Z",
      "summary": "Local note from an authorized file",
      "source_name": "Manual Export",
      "platform": "manual",
      "source_weight": 1.2
    }
  ]
}
```

For external tools that need a stable sanitized handoff template, see
[community-signal-import.md](community-signal-import.md). That contract is a
template layer over this importer. It does not add platform collection or
instructions for obtaining platform/community data.

Manual import remains broader and backward-compatible: unknown columns may be
ignored by the importer. Use
[`community-signal-lint`](community-signal-quality.md) when a local external
tool should meet the stricter community handoff contract before dry-run/import.

## Dry Run

Use `--dry-run` to validate the local file before writing rows:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --data-dir "$PWD/data" --dry-run
```

A dry run is intended to check parsing and validation. It does not import rows
into the local database.

## Directory Dry Run And Import

Use `import-signals-dir --dry-run` to validate matched files directly under one
local directory through the same importer model:

```bash
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Manual Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --source-name "Manual Export" --data-dir "$PWD/data" --dry-run --output-format json
```

Directory matching is non-recursive. It validates regular files directly under
the supplied directory only, using the single input format selected by
`--format`. Run it separately for CSV and JSON folders or patterns.

Directory dry run does not open SQLite, create data/config/report directories,
import rows, fetch URLs, collect sources, verify platform coverage, or run
matching/scoring. It also does not estimate `items_added`, because that would
require reading the local database.

After a successful dry run, omit `--dry-run` to import the same local directory:

```bash
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Manual Export" --imported-at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --data-dir "$PWD/data"
uv run fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --source-name "Manual Export" --imported-at "2026-06-12T12:00:00Z" --data-dir "$PWD/data"
```

Actual directory import validates every matched file before opening SQLite. If
any matched file or the directory itself fails validation, no rows are imported
from otherwise-clean files and no data directory or SQLite database is created.
`--imported-at` is validated even during `--dry-run`; during dry run it is only a
command preflight and no rows are written.

## Import And Review

Import a CSV file:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --data-dir "$PWD/data"
```

Import a JSON file:

```bash
uv run fashion-radar import-signals ./signals.json --format json --source-name "Manual Export" --imported-at "2026-06-12T12:00:00Z" --data-dir "$PWD/data"
```

After import, run the same local review commands used for collected sources:

```bash
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Manual Export" --format json
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --phrase "Le Teckel bag"
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --phrase "Le Teckel bag" --source-name "Manual Export" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Manual Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --unmatched-only
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Retained-row review commands can be narrowed with `--source-name`,
`--lookback-days`, `--current-days`, `--baseline-days`, `--entity-type`, and
`--limit` where supported. Use `--format json` when you need machine-readable
output.

`imported-review-workflow` prints a copyable sequence for existing local review
commands. It does not execute those commands, open SQLite, read configs, import
rows, run matching, score signals, generate reports, or create artifacts.

`imported-signals-summary` groups retained `manual_import` rows by stored
`source_name` and, where shown, stored local `platform` provenance labels for a
local count overview before row-level review.

`imported-entity-deltas` compares stored matched entities on retained
`manual_import` rows across collected-at windows for an aggregate local
matched-entity review.

`imported-candidates` is local and read-only. It surfaces observed candidate
phrases from retained `manual_import` rows only. These phrases need review and
are not verified entities, demand proof, or platform coverage.

`imported-candidate-evidence` is local and read-only. It shows retained
`manual_import` rows whose extracted candidate phrases match one requested
phrase. Evidence rows are review aids and are not verified entities, demand
proof, or platform coverage.

`imported-signals` reviews retained `manual_import` rows already stored in the
local SQLite database, including stored `platform` provenance labels when
present. It is read-only and does not import rows, run matching, score signals,
generate reports, fetch URLs, monitor folders, infer platform coverage, or
create dashboard/report artifacts.

Reports and the dashboard frame candidate signals as observed phrases from
configured sources and imported local signals that need review.

Imported rows can affect trend deltas only after they are imported and matched.
This still does not imply platform coverage.

## Privacy Boundary

Do not import private comments, account IDs, cookies, author profiles, follower
lists, images, videos, or other private or sensitive material. Keep imported
rows limited to conservative metadata that you are allowed to process and review
locally.

Manual import is a local input path, not a connector, platform collector,
browser automation workflow, or source-acquisition guide.
