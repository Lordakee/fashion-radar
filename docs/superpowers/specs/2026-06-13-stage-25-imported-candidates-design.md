# Stage 25 Imported Candidates Design

## Goal

Add `fashion-radar imported-candidates`, a local read-only command that surfaces
candidate phrases from retained `manual_import` rows only.

This helps review locally imported community/manual signals for possible new
brands, designer brands, bags, shoes, categories, or other phrases before they
are promoted into `entities.yaml`.

## Why This Stage

The project already has:

- `imported-signals`: row-level retained manual import review.
- `imported-signals-summary`: imported source-name count summary.
- `imported-entity-deltas`: stored matched entity movement on imported rows.
- `candidates`: untracked phrase discovery across all retained local items.

There is still a useful gap: a reviewer cannot ask for candidate phrases from
imported rows only. Stage 25 fills that gap without adding a source connector,
external integration, scheduler, platform search, crawler, scraper, account
workflow, or browser automation.

## Non-Goals

- No source acquisition, platform/API integration, scraping, crawling, browser
  automation, account automation, scheduling, watch folders, or external
  service calls.
- No database writes, schema migrations, report writes, dashboard writes,
  matching, scoring algorithm changes, or persistent candidate tables.
- No claims about market-wide demand, platform-wide popularity, source quality,
  source coverage, source ranking, or verified trends.
- No new dependencies.

## Command

```bash
fashion-radar imported-candidates \
  --config-dir ./configs \
  --data-dir ./data \
  --as-of 2026-06-13T12:00:00Z
```

Options:

- `--config-dir PATH`: loads local `scoring.yaml` and optional `entities.yaml`.
- `--data-dir PATH`: points to the existing local SQLite database.
- `--as-of TEXT`: required UTC review timestamp.
- `--source-name TEXT`: optional exact stored imported `source_name` filter.
- `--limit INTEGER`: maximum candidate rows to print, default `50`, minimum
  `0`.
- `--format [table|json]`: output format, default `table`.

`--as-of` is parsed with `parse_datetime_utc()` and normalized in output.
Blank `--source-name` is treated as no source-name filter.

## Data Flow

1. CLI parses `--as-of` and validates CLI option types before opening data.
2. CLI loads local scoring config and optional local entities config.
3. `query_imported_candidates()` receives:
   - database path,
   - scoring settings,
   - candidate discovery settings,
   - optional entity config,
   - normalized `as_of`,
   - optional `source_name`,
   - `limit`.
4. Missing database returns an empty result and creates no directory or file.
5. Existing database is opened with the existing read-only SQLite engine.
6. Existing imported-review schema verification is reused.
7. Existing candidate discovery is reused with two new optional filters:
   - `source_type="manual_import"`,
   - optional exact `source_name`.
8. Results are converted into stable Pydantic output and rendered as table or
   JSON.

## Candidate Discovery Filter Change

`discover_candidates()` gets optional filter arguments:

```python
source_type: SourceType | str | None = None
source_name: str | None = None
```

Default behavior stays unchanged. Existing callers such as reports, dashboard,
`candidates`, and `trends` continue passing no filters and therefore continue
reading all eligible retained local items.

`_candidate_mentions()` applies source filters before Python date-window
classification. Date-window behavior remains unchanged.

Known configured entities and stored entity matches continue to suppress
candidate phrases in the same way as the existing `candidates` command.

## Output Model

Top-level JSON fields, in order:

```text
database
as_of
current_window_start
baseline_window_start
current_days
baseline_days
source_type
source_name
limit
candidate_count
candidates
```

`source_type` is always `manual_import`.

Each candidate uses an imported-candidate-specific aggregate shape:

```text
phrase
candidate_type
label
score
current_mentions
baseline_mentions
distinct_sources
growth_ratio
first_seen_at
```

The command does not expose candidate `contexts`, normalized keys, item IDs,
representative item URLs, titles, summaries, match reasons, match confidence,
aliases, import paths, source files, account fields, cookies, sessions, raw
comments, or private fields.

## Table Output

Table output starts with:

```text
Imported manual candidate signals from local SQLite.
Candidate signals are observed phrases from retained manual_import rows and need review.
Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00
Baseline window: 2026-05-07T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00
Source name: none
Candidates: 0
```

If candidates exist, rows use:

```text
Phrase | Type | Label | Score | Current Mentions | Baseline Mentions | Distinct Sources | First Seen At
```

Table cells are sanitized for pipes/newlines/carriage returns. JSON is the
stable machine-readable form.

## Errors

- Invalid `--as-of` prints `Could not review imported candidates: invalid
  --as-of: ...` and exits `1`.
- Invalid `--format` is rejected by Typer before query execution.
- Invalid `--limit` is rejected by Typer before query execution.
- Invalid scoring/entity config prints `Invalid imported candidates config:
  ...` and exits `1`.
- Invalid SQLite schema prints `Could not review imported candidates: ...` and
  exits `1` without traceback.

## Tests

Add tests for:

- default `discover_candidates()` behavior remains unchanged;
- `discover_candidates()` can filter by source type and source name;
- imported candidates missing database returns empty result without creating a
  directory;
- imported candidates call the read-only SQLite engine through
  `query_imported_candidates()`;
- imported candidates filter to `manual_import` and optional `source_name`;
- configured/stored entity filtering still suppresses known entities;
- baseline/current windows and labels match existing candidate discovery;
- stable JSON field order;
- JSON omits `representative_items`, `source_url`, `title`, `summary`,
  `contexts`, item IDs, and match internals;
- table rendering sanitizes non-machine-readable cells;
- CLI help, JSON, table, invalid `--as-of`, invalid `--format`, invalid
  `--limit`, missing database no-artifact behavior, invalid schema without
  traceback, and no database mutation.

## Documentation

Document the command near existing imported review and candidate-discovery
examples. Wording must say imported candidates are local observed phrases from
retained manual imports and need review. It must not describe them as verified
entities, market trends, platform coverage, source quality, source ranking, or
demand proof.
