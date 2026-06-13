# Stage 23 Imported Entity Deltas Design

## Goal

Add `fashion-radar imported-entity-deltas`, a local read-only command that
summarizes stored matched entities on retained `manual_import` rows across a
current collected-at window and an immediately preceding baseline window.

The command helps users inspect local changes in already-imported and
already-matched fashion entities such as brands, designers, products, people,
places, or materials. It does not fetch, import, match, score, report, schedule,
or write anything.

The command compares the current stored match state on rows whose
`collected_at` falls in the baseline or current window. It does not reconstruct
historical match state as it existed at the baseline time. If matching is rerun,
both windows reflect the latest stored `item_entities` rows.

## Non-Goals

- No new collectors, browser automation, platform APIs, account login, watch
  folders, or background jobs.
- No new matching, scoring, report generation, dashboard writes, database
  migrations, or dependencies.
- No source-name quality, source-name ranking, or external coverage claims.
- No titles, URLs, summaries, imported file paths, raw item rows, match reasons,
  or match context terms in output.

## Command

```bash
fashion-radar imported-entity-deltas --data-dir ./data --as-of 2026-06-13T12:00:00Z
fashion-radar imported-entity-deltas --data-dir ./data --as-of 2026-06-13T12:00:00Z --format json
```

Options:

- `--data-dir PATH`: existing project data directory.
- `--as-of TEXT`: UTC boundary for the current window.
- `--current-days INTEGER`: current window size, default `7`, minimum `1`.
- `--baseline-days INTEGER`: baseline window size, default `7`, minimum `1`.
- `--entity-type TEXT`: optional exact stored entity type filter.
- `--source-name TEXT`: optional exact stored source-name filter.
- `--limit INTEGER`: maximum entity rows to display, default `50`, minimum `0`.
- `--format [table|json]`: output format, default `table`.

Window semantics:

```text
baseline_start < collected_at <= current_start
current_start < collected_at <= as_of
current_start = as_of - current_days
baseline_start = current_start - baseline_days
```

## Data Model

Top-level JSON fields, in order:

```text
database
as_of
current_window_start
baseline_window_start
current_days
baseline_days
entity_type
source_name
limit
row_count
total_count
current_matched_item_count
baseline_matched_item_count
entities
```

Entity row fields, in order:

```text
entity_name
entity_type
current_count
baseline_count
delta
change_label
current_source_count
baseline_source_count
source_count_delta
first_collected_at
latest_collected_at
```

Counting rules:

- Only rows where `items.source_type == "manual_import"` are considered.
- Only stored `item_entities` matches are considered.
- Counts are item-level per entity. If one item has duplicate matches for the
  same stored entity name and type, that item contributes once to that entity.
- `current_matched_item_count` and `baseline_matched_item_count` count distinct
  manual-import items that have at least one stored match in the relevant
  window after optional source-name and entity-type filtering.
- All stored matches count regardless of confidence. This command follows the
  imported-signal review pattern, not scoring thresholds.
- `current_source_count` and `baseline_source_count` are distinct stored
  `source_name` label counts for that entity in each window.
- `source_count_delta` is `current_source_count - baseline_source_count`.
- `first_collected_at` and `latest_collected_at` are normalized UTC ISO strings
  from rows contributing to that entity across both windows.

`change_label` values:

- `new_in_current`: current count is positive and baseline count is zero.
- `increased`: current count is greater than baseline count.
- `dropped_from_current`: current count is zero and baseline count is positive.
- `decreased`: current count is less than baseline count and still positive.
- `unchanged`: counts are equal.

Ordering:

1. `new_in_current`
2. `increased`
3. `dropped_from_current`
4. `decreased`
5. `unchanged`
6. Higher absolute movement.
7. Higher `current_count`.
8. `entity_type` ascending.
9. `entity_name` ascending.

This ordering is a deterministic local presentation order, not an external
source ranking.

## Read-Only Behavior

The query helper mirrors `query_imported_signals_summary()`:

- If the database path does not exist, return an empty result and do not create
  directories or files.
- If the database exists, open it through `create_readonly_sqlite_engine()`.
- Reuse `verify_imported_signals_schema(engine)` before querying.
- Execute only `SELECT` statements and dispose the engine in `finally`.
- Parse stored `collected_at` values with `parse_datetime_utc()` in Python for
  window filtering and classification. The existing import path writes
  normalized UTC strings, but this command does not depend on lexical timestamp
  ordering.

## Table Output

Empty table output:

```text
Imported manual entity deltas from local SQLite.
Baseline window: <baseline_start> < collected_at <= <current_start>
Current window: <current_start> < collected_at <= <as_of>
Rows: 0 shown, 0 total entities
Matched items: 0 current, 0 baseline
No imported manual entity deltas found.
```

Populated table header:

```text
Entity | Type | Current | Baseline | Delta | Change | Current Sources | Baseline Sources | Source Delta | First Collected At | Latest Collected At
```

The table sanitizes entity names and types with the existing `_table_cell()`
behavior and does not print item-level fields.

## Errors

- Invalid `--as-of` prints `Could not compare imported entity deltas: invalid
  --as-of: ...` and exits `1`.
- Existing invalid database schema prints `Could not compare imported entity
  deltas: ...` and exits `1`.
- Typer validates enum and numeric option values before the query helper is
  called.

## Tests

Add focused tests for:

- missing database returns an empty model without creating directories;
- grouping by entity name/type and counting item-level current/baseline matches;
- duplicate matches on the same item do not inflate entity counts;
- all change labels and ordering tie-breakers;
- per-window stored `source_name` label counts and `source_count_delta`;
- manual-import filtering excludes RSS rows;
- optional `entity_type`, `source_name`, and `limit=0`;
- read-only engine use;
- table output and sanitization;
- CLI help, JSON key order, invalid format before query, invalid schema without
  traceback, special-character data directory, and no mutation of an existing
  database.

## Documentation

Document the command near imported signal review and summary commands. Wording
must stay local: retained manual-import rows, stored matches, collected-at
windows, and stored entity/source-name labels.
