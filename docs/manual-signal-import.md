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
- `platform`: short provenance label for varied local files. It is not stored as
  platform coverage and does not imply complete platform visibility.
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
      "source_weight": 1.2
    }
  ]
}
```

## Dry Run

Use `--dry-run` to validate the local file before writing rows:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --dry-run
```

A dry run is intended to check parsing and validation. It does not import rows
into the local database.

## Import And Review

Import a CSV file:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
```

Import a JSON file:

```bash
uv run fashion-radar import-signals ./signals.json --format json --source-name "Manual Export"
```

After import, run the same local review commands used for collected sources:

```bash
uv run fashion-radar match
uv run fashion-radar report --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

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
