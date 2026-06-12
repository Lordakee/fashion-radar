# Stage 20 Imported Signals Review Design

## Goal

Add a local read-only review command for rows that have already been imported
from user-provided files:

```bash
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z
```

The command helps users inspect retained `manual_import` rows after
`import-signals` or `import-signals-dir` and before running `match`,
`candidates`, `trends`, reports, or the dashboard.

Stage 20 stays local-first. It reads only the existing local SQLite database.
It does not add collection, source acquisition, platform search, scraping,
crawling, browser automation, account automation, platform APIs, watch folders,
schedulers, background import, dashboard writes, report generation, matching,
scoring, schema migration, or product-facing approval/audit/policy workflows.

## Recommended Command

Add:

```bash
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --lookback-days 1
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --limit 10
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --source-name "Community Tool Export"
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --unmatched-only
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --format json
```

`imported-signals` is intentionally separate from `import-signals` and
`import-signals-dir`: the existing commands validate/import local files, and
the new command reviews rows already stored with
`items.source_type == "manual_import"`.

`--as-of` is required to match the existing read-only `candidates` and `trends`
style. It makes output reproducible and avoids treating the command runtime as
a hidden filter.

## Behavior

- The command reads `fashion-radar.sqlite` under `--data-dir`.
- If the database does not exist, it prints an empty review result and exits
  zero without creating `--data-dir`.
- It validates `--as-of` before opening SQLite or touching `--data-dir`.
- It opens existing SQLite databases in read-only URI mode.
- It verifies `schema_metadata`, `items`, and `item_entities` are present.
- It verifies `schema_metadata.version` is present.
- It verifies `schema_metadata.version == SCHEMA_VERSION`.
- It verifies the `items` and `item_entities` columns used by the command are
  present before querying.
- It only returns rows where `items.source_type == "manual_import"`.
- It filters by `collected_at` window:
  `window_start < collected_at <= as_of`.
- `--lookback-days N` defaults to `7` and has minimum `1`.
- `--limit N` defaults to `50` and accepts `0`.
- Direct Python helper calls reject negative `limit` values with `ValueError`;
  the CLI also enforces `min=0`.
- `--source-name TEXT` optionally filters by exact stored source name after
  stripping surrounding whitespace. Blank values are treated as no filter.
- `--unmatched-only` limits the effective result set to rows with no current
  `item_entities` matches.
- Counts are computed after source/window/unmatched filters and before
  `--limit`.
- Displayed rows are ordered by `collected_at` descending, then `id`
  descending.
- Match status is read from existing `item_entities` rows only. It can be
  stale if `match` has not been rerun since import or since entity config
  changes.
- It prints table or JSON output controlled by `--format table|json`.
- JSON output is emitted with `model_dump_json(indent=2)`, and model fields
  intentionally stay JSON primitives/strings/lists/dicts.
- Table output replaces carriage returns/newlines with spaces and replaces pipe
  characters with `/` inside cell values before rendering rows.
- It does not run matching, scoring, candidate discovery, trend comparison,
  report generation, digest packaging, collection, import, or migration.

## Output Contract

Table output:

```text
Imported manual signals from local SQLite.
Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00
Rows: 2 shown, 3 total
Matches: 1 matched, 2 unmatched
Sources: Community Tool Export=2, Manual Import=1
ID | Collected At | Match | Source | Weight | Title | URL
3 | 2026-06-12T12:00:00+00:00 | matched:The Row | Community Tool Export | 1.40 | Margaux interest | https://example.com/margaux
2 | 2026-06-12T11:00:00+00:00 | unmatched | Manual Import | 1.00 | Le Teckel bag rises | https://example.com/le-teckel
```

When no rows match:

```text
Imported manual signals from local SQLite.
Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00
Rows: 0 shown, 0 total
Matches: 0 matched, 0 unmatched
Sources: none
No imported manual signals found.
```

JSON output uses stable top-level key order:

```json
{
  "database": "data/fashion-radar.sqlite",
  "as_of": "2026-06-12T12:00:00+00:00",
  "window_start": "2026-06-05T12:00:00+00:00",
  "lookback_days": 7,
  "source_name": null,
  "unmatched_only": false,
  "limit": 50,
  "row_count": 1,
  "total_count": 3,
  "matched_count": 1,
  "unmatched_count": 2,
  "source_name_counts": {
    "Community Tool Export": 2,
    "Manual Import": 1
  },
  "latest_collected_at": "2026-06-12T12:00:00+00:00",
  "items": [
    {
      "id": 3,
      "source_name": "Community Tool Export",
      "url": "https://example.com/margaux",
      "title": "Margaux interest",
      "published_at": "2026-06-12T09:00:00+00:00",
      "collected_at": "2026-06-12T12:00:00+00:00",
      "source_weight": 1.4,
      "summary": "Short local note.",
      "match_status": "matched",
      "matches": [
        {
          "entity_name": "The Row",
          "entity_type": "brand",
          "alias": "The Row",
          "confidence": 1.0
        }
      ]
    }
  ]
}
```

The command does not expose `normalized_url`, `content_hash`,
`item_entities.reason`, `item_entities.context_terms`, raw import rows, or file
paths. The counts describe retained local rows only. They are not platform
coverage, market rankings, demand proof, or real-time monitoring.

## Files

Create:

- `src/fashion_radar/imported_signals.py`
- `tests/test_imported_signals.py`

Modify:

- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `README.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/trend-deltas.md`
- `docs/dashboard.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

Process artifacts:

- `docs/reviews/claude-code-stage-20-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-20-plan-review.md`
- code-review prompt/result files after implementation is ready for upload.

## Testing Requirements

Module tests:

- missing database returns an empty review result without creating directories;
- invalid `as_of` is handled before database access when exercised through CLI;
- incompatible schema rejects databases missing `schema_metadata`, `items`, or
  `item_entities`;
- incompatible schema rejects databases missing `schema_metadata.version`;
- incompatible schema rejects unexpected `schema_metadata.version`;
- incompatible schema rejects databases missing command-required `items` or
  `item_entities` columns;
- query returns only `manual_import` rows and excludes RSS/GDELT rows;
- query respects `window_start < collected_at <= as_of`, including tests that
  exclude exactly `window_start`, include exactly `as_of`, and exclude future
  rows;
- ordering is `collected_at` descending then `id` descending;
- source-name filtering strips whitespace and treats blanks as no filter;
- `limit=0` returns no items while preserving aggregate counts;
- match status and match list are built from `item_entities` without inflating
  item counts when one item has multiple match rows;
- `--unmatched-only` equivalent filtering returns only rows with no matches;
- table rendering covers both populated and empty results, including row order,
  match-cell formatting, weight formatting, source counts, and cell
  sanitization.

CLI tests:

- help lists `--data-dir`, `--as-of`, `--lookback-days`, `--limit`,
  `--source-name`, `--unmatched-only`, and `--format`;
- invalid `--as-of` exits non-zero without traceback and without creating
  `--data-dir`;
- table output shows window, row counts, match counts, source counts, and item
  rows;
- JSON output has stable top-level keys and only imported rows;
- JSON output has stable item/match keys and excludes `normalized_url`,
  `content_hash`, `reason`, `context_terms`, raw rows, and file paths;
- missing database exits zero and creates no data/config/report artifacts;
- existing databases remain unchanged after the command reads them;
- module tests prove existing databases are opened through the read-only SQLite
  helper;
- invalid `--as-of` tests prove query/database access is skipped even if a
  database file already exists;
- source-name, lookback, limit, and unmatched-only behavior are covered;
- invalid schema exits non-zero without traceback.

Release checks:

- focused pytest for `tests/test_imported_signals.py` and
  `tests/test_cli.py -k imported_signals`;
- full pytest;
- `ruff check .`;
- `ruff format --check .`;
- `git diff --check`;
- `uv lock --check --default-index https://pypi.org/simple`;
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`;
- wheel build to `/tmp`;
- installed-wheel smoke using the Tsinghua mirror:
  - `fashion-radar imported-signals --help`;
  - import a tiny local directory into a temp `--data-dir`;
  - run `fashion-radar imported-signals --data-dir <temp> --as-of <timestamp> --format json`;
- secret scan and artifact scan before commit.

## Decisions

Use the recommended approach:

- add a read-only `imported-signals` command now;
- make `--as-of` required and use a deterministic lookback window;
- include match status from existing `item_entities` rows without running
  matching;
- include `--unmatched-only` to support post-import review before a matching
  run;
- keep the command focused on stored `manual_import` items only;
- do not add report files, dashboard writes, matching, scoring, source
  acquisition, recursive directory scanning, scheduled review, or external
  platform integration in this stage;
- do not add dependencies or change `uv.lock`.
