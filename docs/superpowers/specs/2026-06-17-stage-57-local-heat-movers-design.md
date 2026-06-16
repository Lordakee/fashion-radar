# Stage 57 Local Heat Movers Design

## Goal

Add a local-only "heat movers" review view that answers: which tracked entities
and candidate phrases are new or rising inside the configured local source set?

The feature must help the user review local heat movement for brands, products,
bags, shoes, designers, celebrities, categories, and candidate phrases without
adding any new source acquisition capability.

## Context

Fashion Radar already has the core primitives:

- `trends` compares local observed entity heat scores and candidate discovery
  snapshots across two timestamps.
- The dashboard already renders raw trend delta rows from existing SQLite state.
- Reports and candidate discovery already frame candidates as observed phrases
  that need review.

The gap is presentation. `trends` exposes a flat delta table, which is useful
for debugging but not optimized for the daily question "what moved up today?"

## Options Considered

### Option 1: Add `heat-movers` Over Existing Trend Deltas

Create a small grouping layer over `TrendComparison`, add a public
`fashion-radar heat-movers` CLI command, and add a dashboard heat-movers view.

Pros:

- Directly answers the user's heat-movement question.
- Reuses existing scoring, candidate discovery, schema validation, and
  read-only SQLite behavior.
- Does not add dependencies, schema changes, data writes, source acquisition, or
  platform integration.
- Keeps the existing lower-level `trends` command unchanged.

Cons:

- Adds one new public command and dashboard surface.
- Requires careful copy so "heat movers" is understood as local observed
  movement, not market-wide popularity.

This is the recommended option.

### Option 2: Add Heat Movement Into Daily Reports

Embed a heat-change section into generated Markdown/JSON reports.

Pros:

- Useful for report-first users.
- Makes reports more self-contained.

Cons:

- Larger blast radius: report schema, templates, digest examples, and first-run
  output gates may need updates.
- Report generation writes files by design, while Stage 57 can stay read-only.

This is deferred.

### Option 3: Imported-Only Heat Review

Combine imported entity deltas and imported candidates into a new imported-only
review command.

Pros:

- Fits the recent community handoff/import work.
- Narrow and safe.

Cons:

- Ignores configured-source rows, so it is less useful for broader local heat
  movement.
- Risks adding another imported review command beside existing imported review
  commands.

This is not the next best node.

## Proposed Design

Create `src/fashion_radar/heat_movers.py` with pure grouping and rendering
logic over an existing `TrendComparison`.

The module will define strict Pydantic models:

- `HeatMover`: one projected trend row with status, signal kind, signal type,
  name, score movement, mention movement, label fields, distinct-source movement,
  and first-seen timestamp.
- `HeatMoverGroup`: a named section with a display label and rows.
- `HeatMoversReport`: the read-only report envelope with `as_of`,
  `baseline_as_of`, `execution_mode`, `limit_per_group`, `include_cooling`,
  `group_count`, `row_count`, and `groups`.

The grouping function will accept a `TrendComparison` and return:

- `new_tracked_entities`: `entity` deltas with status `new`.
- `rising_tracked_entities`: `entity` deltas with status `rising`.
- `new_candidate_phrases`: `candidate` deltas with status `new`.
- `rising_candidate_phrases`: `candidate` deltas with status `rising`.
- `cooling_watchlist`: optional `cooling` deltas when `include_cooling=True`.

Rows keep the ordering already provided by `TrendComparison` inside each group.
`limit_per_group` applies after grouping. A `None` limit means no group cap; a
zero limit keeps group headers and returns no rows.

## CLI

Add:

```bash
fashion-radar heat-movers
```

Options:

- `--config-dir`
- `--data-dir`
- `--as-of`
- `--baseline-as-of`
- `--limit`
- `--include-cooling`
- `--format table|json`

The CLI will mirror `trends` validation:

- Parse `--as-of` before touching config/data.
- Load `scoring.yaml` and optional `entities.yaml`.
- Default `baseline_as_of` to `as_of - scoring.current_window_days`.
- Reject baseline timestamps at or after `as_of`.
- If the local database is missing, print an empty heat movers report without
  creating the data directory or SQLite file.
- Open existing SQLite only through the existing read-only trend path.

The CLI will call `build_trend_comparison(..., include_dropped=False,
limit=None)` and then group the resulting comparison with the new heat-movers
helper. This keeps `--limit` as a per-group display cap rather than a global raw
delta cap.

## Dashboard

Add a dashboard heat-movers view without creating new query behavior.

The dashboard will reuse `load_trend_comparison(...)` and the same
`build_heat_movers(...)` helper. It will add a "Heat Movers" tab before the raw
"Trend Deltas" tab so users can scan grouped new/rising signals first and still
inspect raw deltas separately.

Dashboard copy must say "local observed heat movement" and "configured source
set"; it must not imply market-wide popularity or platform coverage.

## Boundaries

Stage 57 must not add:

- Platform connectors, platform APIs, scraping, crawling, browser automation,
  account login, cookies, sessions, proxies, or media downloading.
- Background monitoring, watch loops, scheduling, notification sending, or
  webhooks.
- New database schema, migrations, writes, report artifacts, dashboard artifacts,
  config generation, or entity generation.
- New scoring formulas or claims of verified demand, platform coverage,
  source ranking, market-wide trend proof, or "hottest" social trends.
- Compliance, legal, approval, policy, authorization, or safety-review features.

The feature is a local review aid over retained local data only.

## Documentation

Update:

- `README.md`
- `docs/trend-deltas.md`
- `docs/dashboard.md`
- `docs/cli-reference.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`

Documentation should use phrases like:

- "local observed heat movement"
- "configured source set"
- "configured sources and imported local signals"
- "candidate phrases need review"

Documentation should avoid or explicitly negate:

- "hottest"
- "viral"
- "market-wide"
- "platform-wide"
- "verified demand"
- "top social trend"
- "coverage verification"
- "demand proof"
- "source ranking"

## Tests

Add focused coverage for:

- Pure grouping: new/rising entity and candidate groups, optional cooling,
  group limits, empty state, deterministic JSON key order, and table
  sanitization.
- CLI: help flags, JSON output, table output, missing database read-only
  behavior, invalid dates, invalid config, baseline validation, negative limit,
  and no runtime artifacts.
- Dashboard: heat mover row serialization, empty state, config/query warnings,
  and no data-dir creation for missing config.
- Docs: new command appears in public docs; boundary wording is present; raw
  `trends` command remains documented; no unsupported source/platform or demand
  claims are introduced.

Verification should include targeted tests, full tests, ruff, format, lock
checks, mirror sync check, release hygiene, first-run smoke, and installed-wheel
smoke for `fashion-radar heat-movers --help`.
