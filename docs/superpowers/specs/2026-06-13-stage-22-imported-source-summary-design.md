# Stage 22 Imported Signals Summary Design

## Goal

Add a local read-only command that summarizes the retained imported manual
signal rows currently stored in local SQLite:

```bash
fashion-radar imported-signals-summary --data-dir ./data
fashion-radar imported-signals-summary --data-dir ./data --format json
```

The command groups existing `items.source_type == "manual_import"` rows by the
stored `source_name` label. It helps users inspect local import volume and
item-level stored match presence per source-name label without exposing row
titles, URLs, summaries, imported source file paths, raw import rows, or
internal match details.

Stage 22 stays local-first. It reads only the existing local SQLite database. It
does not collect sources, fetch URLs, run matching, score signals, generate
reports, monitor directories, initialize or migrate databases, write dashboard
artifacts, rank sources, assess source quality, measure platform coverage, or
provide instructions for obtaining platform/community data.

## Behavior

- The command reads `fashion-radar.sqlite` under `--data-dir`.
- If the database does not exist, it prints an empty summary and exits zero
  without creating `--data-dir`.
- It opens existing SQLite databases in read-only URI mode.
- It reuses the existing imported-signals schema verification:
  `schema_metadata`, `items`, `item_entities`, required columns, and
  `schema_metadata.version == SCHEMA_VERSION`.
- It only summarizes rows where `items.source_type == "manual_import"`.
- It summarizes all currently retained matching rows in the local `items`
  table. It does not add an `--as-of` review window or a limit.
- Matching presence is item-level and derived from whether the item has at
  least one current `item_entities` row. Multiple entity rows for the same
  imported item must not inflate matched-row counts.
- Source summaries are ordered by the exact stored `source_name` text value in
  SQLite ascending order. The command does not normalize labels, merge labels,
  apply locale-aware collation, or rank sources.
- It prints table or JSON output controlled by `--format table|json`.
- Table output sanitizes source-name cell values by replacing carriage
  returns/newlines with spaces, replacing `|` with `/`, and collapsing
  whitespace.

## Output Contract

Table output:

```text
Imported manual signal source summary from local SQLite.
Rows: 3 retained manual rows across 2 sources
Matched rows: 1 matched, 2 unmatched
Collected at: 2026-06-10T09:00:00+00:00 first, 2026-06-12T10:00:00+00:00 latest
Source | Rows | Matched Rows | Unmatched Rows | First Collected At | Latest Collected At
Community Tool Export | 2 | 1 | 1 | 2026-06-12T09:00:00+00:00 | 2026-06-12T10:00:00+00:00
Manual Import | 1 | 0 | 1 | 2026-06-10T09:00:00+00:00 | 2026-06-10T09:00:00+00:00
```

When no rows match:

```text
Imported manual signal source summary from local SQLite.
Rows: 0 retained manual rows across 0 sources
Matched rows: 0 matched, 0 unmatched
Collected at: none
No imported manual signal sources found.
```

JSON output uses stable top-level key order:

```json
{
  "database": "data/fashion-radar.sqlite",
  "source_type": "manual_import",
  "source_count": 2,
  "row_count": 3,
  "matched_count": 1,
  "unmatched_count": 2,
  "first_collected_at": "2026-06-10T09:00:00+00:00",
  "latest_collected_at": "2026-06-12T10:00:00+00:00",
  "sources": [
    {
      "source_name": "Community Tool Export",
      "row_count": 2,
      "matched_count": 1,
      "unmatched_count": 1,
      "first_collected_at": "2026-06-12T09:00:00+00:00",
      "latest_collected_at": "2026-06-12T10:00:00+00:00"
    }
  ]
}
```

The command includes the local SQLite database path in the top-level
`database` field, matching existing read-only JSON outputs. It does not expose
URLs, titles, summaries, normalized URLs, content hashes, raw import rows,
imported source file paths, or internal match reasons/context terms. The rows
describe retained local records only. They are not platform coverage, source
quality, source health, market rankings, demand proof, real-time monitoring, or
source acquisition.

## Architecture And Tech Stack

- Python 3.11+
- Typer for CLI parsing and validation
- Pydantic v2 for structured output models
- SQLAlchemy Core and SQLite read-only URI mode
- pytest for tests
- ruff for lint and format checks
- uv for dependency, lockfile, and package verification

No new runtime or development dependencies are required.

## Files

Modify:

- `src/fashion_radar/imported_signals.py`
- `src/fashion_radar/cli.py`
- `tests/test_imported_signals.py`
- `tests/test_cli.py`
- `README.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

Create process artifacts:

- `docs/superpowers/specs/2026-06-13-stage-22-imported-source-summary-design.md`
- `docs/superpowers/plans/2026-06-13-stage-22-imported-source-summary-plan.md`
- `docs/reviews/claude-code-stage-22-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-22-plan-review.md`
- code review prompt/result files after implementation

## Testing Requirements

Module tests:

- missing database returns an empty source summary without creating directories;
- query summarizes only `manual_import` rows and excludes RSS/GDELT rows;
- query groups by exact stored `source_name`;
- matched-row counts are item-level and are not inflated by multiple
  `item_entities` rows for one imported item;
- aggregate first/latest collected timestamps are derived across all retained
  manual rows;
- source summaries are ordered by exact stored `source_name` text ascending
  without normalization or ranking;
- table rendering covers empty and populated outputs, including source-name cell
  sanitization.

CLI tests:

- help lists `--data-dir` and `--format`;
- missing database returns empty JSON and creates no artifacts;
- invalid `--format xml` fails before query/database access and without
  creating `--data-dir`;
- table output shows source counts, retained row counts, matched rows, and
  grouped source rows, while not exposing titles or URLs;
- JSON output has stable top-level and source keys;
- invalid schema exits non-zero without traceback;
- special-character `--data-dir` paths work;
- existing databases remain unchanged after the command runs.

## Scope Guard

Stage 22 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, platform APIs,
  account automation, login cookies, browser profiles, proxy pools, CAPTCHA
  bypass, rate-limit bypass, source acquisition, or platform export
  instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, import behavior changes, database migrations, matching
  changes, scoring changes, report generation changes, dashboard writes, or
  digest changes;
- source health, source quality, source coverage, source ranking, top-source,
  product-facing approval, audit, policy checklist, authorization verification,
  or legal-review workflows.

Wording must stay bounded to retained local rows, imported local signals, local
source-name labels, and stored match presence derived from `item_entities`. It
must not imply platform coverage, market-wide ranking, verified demand,
real-time monitoring, source quality, source health, or source acquisition.
