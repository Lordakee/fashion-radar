# Stage 26 Imported Candidate Evidence Design

## Goal

Add `fashion-radar imported-candidate-evidence`, a local read-only command that
shows which retained `manual_import` rows caused one imported candidate phrase
to appear.

Stage 25 added the aggregate imported-candidates view. Stage 26 adds a
phrase-scoped drilldown so a reviewer can answer: "Why did this candidate phrase
show up?"

## Why This Stage

The aggregate `imported-candidates` command intentionally omits representative
items, URLs, titles, summaries, contexts, item IDs, and match internals. That is
the right shape for a broad list, but the reviewer still needs a local way to
inspect evidence for one selected phrase before deciding whether it is noise,
worth watching, or ready for a later draft/export workflow.

This stage stays narrow:

- one phrase in;
- local retained `manual_import` rows out;
- no config mutation;
- no persistent candidate tables;
- no report/dashboard writes;
- no source acquisition or external integrations.

## Non-Goals

- No source acquisition, platform/API integration, scraping, crawling, browser
  automation, account automation, scheduling, watch folders, or external
  service calls.
- No database writes, schema migrations, config writes, report writes,
  dashboard writes, matching execution, persistent evidence tables, candidate
  approval state, or entity YAML draft generation.
- No claims about verified entities, demand proof, external coverage, source
  quality, source ranking, or platform/community coverage.
- No new dependencies.

## Command

```bash
fashion-radar imported-candidate-evidence \
  --config-dir ./configs \
  --data-dir ./data \
  --as-of 2026-06-13T12:00:00Z \
  --phrase "Le Teckel bag"
```

Options:

- `--config-dir PATH`: loads local `scoring.yaml` and optional `entities.yaml`.
- `--data-dir PATH`: points to the existing local SQLite database.
- `--as-of TEXT`: required UTC review timestamp.
- `--phrase TEXT`: required candidate phrase to inspect.
- `--source-name TEXT`: optional exact stored imported `source_name` filter.
- `--limit INTEGER`: maximum evidence rows to print, default `20`, minimum `0`.
- `--format [table|json]`: output format, default `table`.

`--as-of` is parsed with `parse_datetime_utc()` and normalized in output.
Blank `--source-name` is treated as no source-name filter. Blank `--phrase` is
rejected before query execution.

## Data Flow

1. CLI parses `--as-of`, validates nonblank `--phrase`, and validates option
   types before opening data.
2. CLI loads local scoring config and optional local entities config.
3. `query_imported_candidate_evidence()` receives:
   - database path,
   - scoring settings,
   - candidate discovery settings,
   - optional entity config,
   - parsed `as_of`,
   - phrase,
   - optional `source_name`,
   - `limit`.
4. Missing database returns an empty result and creates no directory or file.
5. Existing database is opened with the existing read-only SQLite engine.
6. Existing imported-review schema verification is reused.
7. Evidence rows are read from retained `manual_import` items only, with optional
   exact `source_name`.
8. In the current schema, "retained" means the row still exists in `items`.
   Stage 26 also applies the same review-window boundary as Stage 25 candidate
   discovery: `baseline_window_start < collected_at <= as_of`. Older
   out-of-window rows and future rows are excluded.
9. Candidate extraction uses the same candidate phrase extraction and candidate
   key normalization as candidate discovery. It must not use naive substring
   matching.
10. Configured entities and stored entity matches continue to suppress known
   entities in the same way as candidate discovery.
11. Evidence is classified into current or baseline windows using
    `items.collected_at`.
12. Results are converted into stable Pydantic output and rendered as table or
    JSON.

## Candidate Discovery Helper Change

Expose two small public helpers from `fashion_radar.discovery.candidates`:

```python
def candidate_key(value: str) -> str:
    ...

def stored_entity_candidate_keys(
    engine: Engine,
    *,
    min_match_confidence: float,
    as_of: datetime,
) -> set[str]:
    ...
```

They delegate to the existing private candidate-key and stored-entity-key
implementations. Existing behavior stays unchanged.

The evidence command uses:

- `candidate_key(phrase)` for the requested phrase;
- `configured_entity_keys(entity_config, as_of=as_of)`;
- `stored_entity_candidate_keys(engine, min_match_confidence=..., as_of=as_of)`;
- `extract_candidate_phrases(...)`.

## Output Model

Top-level JSON fields, in order:

```text
database
as_of
phrase
current_window_start
baseline_window_start
current_days
baseline_days
source_type
source_name
limit
row_count
total_count
current_mentions
baseline_mentions
distinct_sources
evidence
```

`source_type` is always `manual_import`.

Each evidence row uses:

```text
id
window
source_name
title
url
published_at
collected_at
```

`window` is one of `current` or `baseline`.

This command intentionally exposes `title` and `url` for one requested phrase
because it is a local phrase-scoped evidence drilldown. It still omits summaries,
raw comments, candidate contexts, normalized candidate internals, match reasons,
match confidence, aliases, import paths, source files, account fields, cookies,
sessions, and private/raw fields.

`current_mentions` counts all matching current-window evidence rows before
`limit`. `baseline_mentions` counts all matching baseline-window evidence rows
before `limit`. `distinct_sources` counts distinct current-window source names.
`total_count` is all matching evidence rows before `limit`; `row_count` is the
number of rows in the returned `evidence` array after `limit`.

## Table Output

Table output starts with:

```text
Imported manual candidate evidence from local SQLite.
Evidence rows are retained manual_import rows whose extracted candidate phrases match the requested phrase.
Phrase: Le Teckel bag
Current window: 2026-06-06T12:00:00+00:00 < collected_at <= 2026-06-13T12:00:00+00:00
Baseline window: 2026-05-07T12:00:00+00:00 < collected_at <= 2026-06-06T12:00:00+00:00
Source name: none
Rows: 0 shown, 0 total
Current mentions: 0
Baseline mentions: 0
Distinct current sources: 0
```

If evidence exists, rows use:

```text
Window | ID | Collected At | Source | Title | URL
```

Table cells are sanitized for pipes/newlines/carriage returns. JSON is the
stable machine-readable form.

## Errors

- Missing required `--phrase` is rejected by Typer before query execution.
- Blank `--phrase` prints `Could not review imported candidate evidence:
  invalid --phrase: phrase must not be blank` and exits `1` before query
  execution.
- Invalid `--as-of` prints `Could not review imported candidate evidence:
  invalid --as-of: ...` and exits `1`.
- Invalid `--format` is rejected by Typer before query execution.
- Invalid `--limit` is rejected by Typer before query execution.
- Invalid scoring/entity config prints `Invalid imported candidate evidence
  config: ...` and exits `1`.
- Invalid SQLite schema prints `Could not review imported candidate evidence:
  ...` and exits `1` without traceback.

## Tests

Add tests for:

- public candidate key helper behavior;
- public stored-entity candidate key wrapper behavior;
- missing database returns empty evidence without creating a directory;
- query uses `create_readonly_sqlite_engine()` through a monkeypatch;
- query reads retained `manual_import` rows only and supports `source_name`;
- blank `source_name` behaves like no source-name filter;
- old out-of-window and future `manual_import` rows for the same phrase are
  excluded;
- current/baseline windows and counters are correct;
- `limit=0` returns no evidence rows while preserving pre-limit counters;
- evidence extraction uses candidate extraction instead of naive substring
  matching;
- configured and stored entity filtering suppress known entities;
- stable JSON field order;
- JSON omits summaries, raw fields, candidate contexts, match internals, source
  files, import paths, account fields, and private/raw fields;
- table rendering sanitizes non-machine-readable cells;
- CLI help, JSON, table, missing `--phrase`, blank `--phrase`, invalid
  `--as-of`, invalid `--format`, invalid `--limit`, missing database
  no-artifact behavior, invalid schema without traceback, and no database
  mutation.

## Documentation

Document the command near imported candidate and manual/community import review
examples. Wording must say evidence rows are local retained manual imports for a
requested phrase and need review. It must not describe them as verified
entities, demand proof, external coverage, source quality, source ranking, or
platform/community coverage.
