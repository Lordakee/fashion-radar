# Architecture

Fashion Radar is a local Python application. It uses deterministic collectors,
matching, scoring, and reporting so a user can understand why a fashion signal
appeared in a report.

## Flow

```text
YAML config
  -> optionally lint source-pack quality before collection
  -> optionally lint entity-pack quality before matching
  -> collect public sources
  -> optionally import user-provided local CSV/JSON signals
  -> store items in SQLite
  -> match configured entities
  -> score current vs baseline windows
  -> discover candidate signals from retained local items
  -> write Markdown/JSON reports
  -> optionally package local digest artifacts
  -> compare local trend deltas on demand
  -> inspect read-only dashboard
```

## Components

- **CLI:** Typer commands in `fashion_radar.cli`.
- **Config:** Pydantic models load `sources.yaml`, `entities.yaml`, and
  `scoring.yaml`. Optional entity packs are static `entities.yaml` templates
  users can copy and edit; they do not add runtime behavior.
- **Entity-Pack Quality:** Local read-only diagnostics lint one entity YAML or
  entity-pack YAML file for invalid config, empty packs, aliases that cannot
  match, matcher-context surprises, product parent-brand precision issues,
  metadata-list hygiene, missing tags, and omitted scoring defaults. The linter
  does not match items, score entities, open SQLite, collect sources, or create
  config/data/report directories.
- **Source-Pack Quality:** Local read-only diagnostics lint one source YAML or
  source-pack YAML file for duplicate names, duplicate targets, duplicate GDELT
  queries, missing tags, disabled sources, implicit weights, empty enabled
  source sets, invalid config, and article extraction settings before
  collection. The linter does not fetch sources, open SQLite, collect items, or
  create config/data/report directories.
- **Collectors:** RSS/RSSHub-compatible feeds and GDELT Doc API metadata.
  Collectors return normalized items and do not write directly to SQLite.
- **Manual Import:** Local CSV/JSON user-provided signal files are parsed as an
  input path only. They are not connectors or platform collection workflows.
  Community signal import is a documented contract and example set for external
  tools that produce sanitized local files for this same importer.
- **Storage:** SQLite tables store collected items, source health, collector
  runs, entity matches, and stable entity first/last seen timestamps.
- **Matching:** Deterministic alias matching with context gates for common or
  broad aliases.
- **Scoring:** Local heat metrics over configured time windows, based on
  matched entities and item `collected_at` timestamps.
- **Candidate Discovery:** Deterministic observed-phrase review over retained
  local item titles and summaries from configured sources and imported local
  signals.
- **Trend Deltas:** Read-only comparison of entity scoring and candidate
  discovery snapshots from existing local SQLite state. It does not create
  schema migrations, persistent trend tables, or database writes.
- **Reports:** Markdown and JSON daily reports rendered from packaged
  templates.
- **Local Digest:** Optional post-report packaging that writes local
  `latest.md`, `latest.json`, `report-index.json`, `.eml`, or stdout summary
  artifacts from already-generated reports. It does not collect sources or send
  anything.
- **Dashboard:** Optional Streamlit UI that reads local SQLite/report state.

## Default Paths

The CLI accepts explicit paths and environment variables:

```text
FASHION_RADAR_CONFIG_DIR
FASHION_RADAR_DATA_DIR
FASHION_RADAR_REPORTS_DIR
```

If unset, platformdirs chooses user-level config/data/document directories. The
database file is:

```text
<data-dir>/fashion-radar.sqlite
```

Daily reports are:

```text
<reports-dir>/fashion-radar-YYYY-MM-DD.md
<reports-dir>/fashion-radar-YYYY-MM-DD.json
```

Optional local digest artifacts are:

```text
<reports-dir>/latest.md
<reports-dir>/latest.json
<reports-dir>/report-index.json
<reports-dir>/fashion-radar-YYYY-MM-DD.eml
```

## Command Flow

```bash
fashion-radar init
fashion-radar doctor
fashion-radar source-pack-lint ./configs/sources.yaml
fashion-radar entity-pack-lint ./configs/entities.yaml
fashion-radar collect
fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
fashion-radar match
fashion-radar report --as-of 2026-06-11T12:00:00Z
fashion-radar report --as-of 2026-06-11T12:00:00Z --digest-latest copy --digest-index
fashion-radar candidates --as-of 2026-06-11T12:00:00Z
fashion-radar trends --as-of 2026-06-11T12:00:00Z --config-dir ./configs
```

`run` executes `collect -> match -> report` serially in one local process:

```bash
fashion-radar run --as-of 2026-06-11T12:00:00Z
```

There are no parallel database writers in the MVP workflow.

## Source-Pack Quality Boundary

`source-pack-lint` is a pre-collection diagnostics command for local YAML files.
It reads raw YAML for omitted-field checks, validates the same source schema used
by collection, and prints table or JSON findings. It does not check live source
availability, run collectors, open the local database, or create workflow
artifacts.

## Entity-Pack Quality Boundary

`entity-pack-lint` is a pre-matching diagnostics command for local YAML files.
It reads raw YAML for omitted-field checks, validates the same entity schema used
by matching, and prints table or JSON findings. It does not run matching,
scoring, collection, source acquisition, platform search, report generation,
digest packaging, or dashboard workflows.

## Candidate Discovery Boundary

Candidate discovery does not add collectors or source types. It reads retained
local SQLite rows, filters configured and already matched tracked entities, and
surfaces candidate signals as observed phrases from configured sources and
imported local signals that need review.

The read-only `candidates` command computes the same review-oriented signals
without writing report files.

## Source Boundary

The core collector set is RSS, RSSHub-compatible feeds, and GDELT. Manual signal
import is a local input path for user-provided CSV/JSON files, not a connector
or platform collector. Non-core platform collection is not part of v0.1.0. See
[source-boundaries.md](source-boundaries.md).

## Dashboard Boundary

The dashboard is optional and imports Streamlit only when the dashboard command
or app is used. Refreshing the dashboard reads local SQLite/report state only; it
does not call collectors, run matching, write reports, or perform network
fetches.

The dashboard defaults to `127.0.0.1:8501` and has no authentication layer.
The candidate signal view reads the latest report JSON and may be stale until a
new report is generated. The trend tab computes local observed deltas from
SQLite using the same config directory as the CLI.

## Package Extras

- Core install: CLI, config, SQLite, RSS/GDELT collection, matching, scoring,
  reports.
- `article`: optional article text extraction dependency.
- `dashboard`: optional Streamlit and pandas dashboard dependencies.

The core CLI must work without optional extras.
