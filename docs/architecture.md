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
  -> optionally copy sanitized CSV/JSON external tool handoff template files
     for a local external tool
  -> optionally use checked-in external community tool export directory
     examples for a local external tool
  -> optionally print the external social/community tool adapter registry
     as a local producer-discovery registry
  -> optionally print adapter-specific template rows for sanitized CSV/JSON
     local file handoff examples
  -> optionally check local command availability guidance for external/community tools
     without running adapters or upstream tools
  -> optionally print the community signal producer profile before a local tool writes files
     with static directory_example_paths pointers
  -> optionally print a community directory handoff checklist without executing it
  -> optionally run a local-only community directory handoff readiness report
  -> optionally lint one community signal CSV/JSON file or a local directory batch before import
  -> optionally dry-run matched local signal files in one directory before import
  -> optionally import user-provided local CSV/JSON signals from one file or one directory
  -> store items in SQLite
  -> optionally print a post-import review command checklist without executing it
  -> optionally review retained manual_import rows from local SQLite
  -> optionally summarize retained manual_import rows by stored source-name label
  -> match configured entities
  -> optionally compare stored manual_import entity counts across collected-at windows
  -> optionally inspect privacy-safe retained manual_import rows behind one matched entity
  -> optionally review candidate phrases from retained manual_import rows
  -> optionally inspect retained manual_import rows behind one candidate phrase
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
  The external tool handoff templates are sanitized CSV/JSON local file
  handoff templates for user-controlled external/community tools.
  This is not platform collection and does not add connectors, scraping,
  browser automation, platform APIs, monitoring, scheduling, source acquisition,
  demand proof, ranking, or coverage verification.
  The external community tool export directory examples are sanitized CSV/JSON
  local directory samples for user-controlled external/community tools. They
  are exposed as static `directory_example_paths` pointers and are not platform
  collection. They do not add connectors, scraping, browser automation,
  platform APIs, monitoring, scheduling, source acquisition, demand proof,
  ranking, or coverage verification.
  `external-tool-adapters` prints the external social/community tool adapter
  registry as a local producer-discovery registry for user-controlled
  external/community tools that need sanitized CSV/JSON local file handoff
  targets. It is local and print-only: it does not run adapters, inspect
  directories, read handoff files, validate files, import rows, open SQLite,
  or create artifacts. It is not platform collection and has no connectors, no
  scraping, no browser automation, no platform APIs, no monitoring, no
  scheduling, no source acquisition, no demand proof, no ranking, and no
  coverage verification. Each adapter command list includes
  `external-tool-readiness` as an optional local read-only preflight command,
  while `external-tool-adapters` itself remains print-only and does not run
  readiness or perform PATH lookup.
  `external-tool-template` prints adapter-specific template rows for
  user-controlled external/community tools that need sanitized CSV/JSON local
  file handoff examples. It is local and print-only: JSON and CSV output
  contain importable community handoff rows only, table output may include
  local metadata and copyable commands, and the command does not write files,
  run adapters, inspect directories, read handoff files, validate files,
  import rows, open SQLite, or create artifacts. It is not platform collection
  and has no connectors, no scraping, no browser automation, no platform APIs,
  no monitoring, no scheduling, no source acquisition, no demand proof, no
  ranking, and no coverage verification. The JSON/CSV handoff rows remain
  importable row output only, while table/model guidance can include the same
  adapter recommended command list.
  `external-tool-workflow` prints workflow metadata as a local producer
  handoff wrapper only. It is for user-controlled external/community tools
  that need a producer-facing wrapper around existing local commands before
  writing sanitized CSV/JSON local file handoff rows. It is local and
  print-only: JSON output is workflow metadata, not importable handoff rows,
  table output may include local metadata and copyable commands, and the
  printed steps include `check_external_tool_readiness`, an optional preflight
  command that points to `external-tool-readiness` for local command
  availability guidance before sanitized handoff rows are prepared. The command
  does not run generated commands, adapters, or upstream tools,
  inspect the supplied directory, read handoff files, validate rows, import
  rows, open SQLite, or create artifacts. It is not platform collection and
  has no connectors, no scraping, no browser automation, no platform APIs, no
  monitoring, no scheduling, no source acquisition, no demand proof, no
  ranking, and no coverage verification.
  `external-tool-readiness` reports external tool readiness and local command
  readiness guidance only. It is local read-only, not print-only, because it
  checks command availability only with local PATH lookup (`shutil.which`) for
  known free
  external/community tools such as Rednote MCP, Xiaohongshu crawler,
  Instaloader, TikTok-Api, yt-dlp, and X/search exports. It prints
  mirror-friendly install hints and Fashion Radar next-step handoff commands
  for user-controlled external/community tools producing sanitized CSV/JSON
  local file handoff rows. It does not install dependencies automatically, does
  not run adapters, does not run upstream tools, does not inspect directories,
  does not read handoff files, import rows, open or write SQLite, or create
  config/data/report/dashboard/workflow/handoff artifacts. It is not a
  scraper/connector and has no scraping, no browser automation, no platform
  APIs, no account/session/cookie/token behavior, no monitoring, no scheduling,
  no source acquisition, no demand proof, no ranking, no coverage verification,
  and no compliance-review product feature.
  `community-signal-profile` prints that local producer contract for
  user-controlled tools without reading handoff files, creating artifacts,
  acquiring sources, monitoring platforms, or performing compliance review.
  `community-handoff-manifest` copies those `directory_example_paths` into its
  JSON manifest for external/local tool discovery without reading the supplied
  directory.
  `community-candidates` is an in-memory pre-import preview over one local
  handoff file. It sits before manual import and does not write database,
  report, config, or dashboard state.
  `community-handoff-check-dir` is a local-only handoff readiness report for
  user-controlled community signal directories. It reads only matched local
  regular files and local config. It does not import rows, uses no SQLite,
  creates no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
  APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
  acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
  authorization/safety-review features.
  `community-handoff-workflow` is a print-only helper over the local directory
  handoff sequence. It prints copyable commands for `community-signal-lint-dir`,
  `community-candidates-dir`, `community-handoff-check-dir`,
  `import-signals-dir --dry-run`, `import-signals-dir`, and
  `imported-review-workflow` as `lint_handoff_directory`,
  `preview_candidate_phrases`, `review_handoff_readiness`,
  `dry_run_directory_import`, `import_directory_signals`, and
  `print_post_import_review`. The `review_handoff_readiness` step is the
  `community-handoff-check-dir` local-only handoff readiness report before
  importing rows. The workflow does not execute commands, read the supplied
  directory, validate files, import rows, open or write SQLite, fetch URLs, or
  create workflow artifacts.
  `import-signals-dir --dry-run` validates matched regular files directly under
  one local directory through the same importer model without opening SQLite,
  importing rows, or creating workflow artifacts. `import-signals-dir` without
  `--dry-run` imports only after every matched local file validates.
- **Imported Signal Review:** Local read-only review of retained
  `manual_import` rows from existing SQLite state. It verifies schema before
  querying. The row-level and summary commands do not import rows, collect
  sources, fetch URLs, run matching, score signals, generate reports, or create
  dashboard/report artifacts. The summary command uses the same existing SQLite
  read boundary and groups retained rows by stored `source_name`. The
  entity-deltas command uses stored
  matches on retained rows to compare aggregate entity counts across
  collected-at windows. The imported-entity-evidence command shows a
  privacy-safe drilldown over retained local `manual_import` rows behind one
  stored matched entity and does not expose summaries, candidate contexts, match
  internals, import file paths, or platform labels. The imported-candidates command computes observed
  candidate phrases from retained rows only and does not expose item URLs,
  titles, summaries, candidate contexts, or match internals. The
  imported-candidate-evidence command shows phrase-scoped retained rows with
  titles and URLs, while omitting summaries, candidate contexts, and match
  internals. `imported-review-workflow` remains print-only and includes
  `review_imported_entity_evidence` after entity deltas, a read-only
  imported-candidates step for candidate phrase review, and the final read-only
  heat-movers step for local observed heat movement from
  configured sources and imported local signals. Those review outputs need
  review and provide no demand proof and no platform coverage verification. The
  review workflow command only prints a copyable sequence for existing local
  commands and does not execute them.
- **Community Signal Quality:** Local read-only diagnostics lint one community
  signal CSV/JSON file or a non-recursive batch of matched regular files in one
  local directory before dry-run/import. The linters check strict handoff fields
  and import-readiness but do not import rows, open SQLite, collect sources,
  fetch URLs, run matching/scoring, or create config/data/report directories.
- **Storage:** SQLite tables store collected items, source health, collector
  runs, entity matches, and stable entity first/last seen timestamps. The
  explicit `migrate-db` command initializes or upgrades the local SQLite schema
  for a configured data directory.
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
- **Heat Movers:** Read-only local observed heat movement review for one
  configured source set. It compares configured sources and imported local
  signals, and the output needs review. It provides no demand proof or platform
  coverage verification.
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

## Heat Movers

The `heat-movers` command and dashboard view are local observed heat movement
surfaces for one configured source set. They compare configured sources and
imported local signals, and the output needs review. They provide no demand proof
and no platform coverage verification.

## Command Flow

```bash
fashion-radar init
fashion-radar doctor
fashion-radar migrate-db --data-dir ./data
fashion-radar source-pack-lint ./configs/sources.yaml --strict
fashion-radar entity-pack-lint ./configs/entities.yaml
fashion-radar collect --config-dir ./configs --data-dir ./data
fashion-radar external-tool-adapters --format json
fashion-radar external-tool-template --adapter instaloader --format json
fashion-radar external-tool-workflow --adapter instaloader --format json
fashion-radar external-tool-readiness --adapter instaloader --format json
fashion-radar community-handoff-workflow ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --data-dir ./data --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar community-handoff-check-dir ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar community-signal-lint ./signals.csv --input-format csv --source-name "Manual Export"
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Manual Export"
fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Manual Export" --data-dir ./data --dry-run
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Manual Export" --imported-at 2026-06-11T12:00:00Z --data-dir ./data
fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --data-dir ./data
fashion-radar imported-review-workflow --data-dir ./data --config-dir ./configs --as-of 2026-06-11T12:00:00Z
fashion-radar imported-signals-summary --data-dir ./data
fashion-radar imported-entity-deltas --data-dir ./data --as-of 2026-06-11T12:00:00Z
fashion-radar imported-candidates --data-dir ./data --config-dir ./configs --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar imported-candidate-evidence --data-dir ./data --config-dir ./configs --as-of 2026-06-11T12:00:00Z --phrase "Le Teckel bag" --source-name "Manual Export"
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar match --config-dir ./configs --data-dir ./data
fashion-radar report --config-dir ./configs --data-dir ./data --reports-dir ./reports --as-of 2026-06-11T12:00:00Z
fashion-radar report --config-dir ./configs --data-dir ./data --reports-dir ./reports --as-of 2026-06-11T12:00:00Z --digest-latest copy --digest-index
fashion-radar candidates --config-dir ./configs --data-dir ./data --as-of 2026-06-11T12:00:00Z
fashion-radar trends --config-dir ./configs --data-dir ./data --as-of 2026-06-11T12:00:00Z
```

`run` executes `collect -> match -> report` serially in one local process:

```bash
fashion-radar run --config-dir ./configs --data-dir ./data --reports-dir ./reports --as-of 2026-06-11T12:00:00Z
```

There are no parallel database writers in the MVP workflow.

`doctor` reports database schema status read-only. `migrate-db` is local schema
maintenance only: it initializes or upgrades SQLite state and does not collect,
import, match, score, report, monitor, watch, schedule, or touch external
platforms.

`community-candidates-dir` is an in-memory pre-import preview over matched
regular files directly under one local directory. It sits before manual
directory import and does not write database, report, config, entity, or
dashboard state.

`community-handoff-workflow` prints a copyable local directory sequence and does
not execute commands, read the supplied directory, validate files, import rows,
open or write SQLite, fetch URLs, log in, download media, automate browsers,
scrape, monitor, watch folders, schedule work, add source/platform connectors,
prove demand, verify platform coverage, rank sources, write reports, update
dashboards, generate configs, or generate entity files. It prints
`lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review`; the
`review_handoff_readiness` step is the `community-handoff-check-dir`
local-only handoff readiness report before importing rows. It intentionally
prints the supplied directory/config/data paths inside copyable local commands,
unlike aggregate candidate preview output.

`community-handoff-check-dir` prints a local-only handoff readiness report for
matched local regular files and local config. It does not import rows, uses no
SQLite, creates no config/data/report/dashboard/digest artifacts, and has no
fetch URLs/login/platform APIs/download media/browser automation/scrape/crawl/monitor/
watch/schedule/connectors/source acquisition/demand proof/ranking/coverage verification/entity
generation/compliance/policy/authorization/safety-review features.

`external-tool-readiness` prints external tool readiness guidance as local
read-only command availability only guidance. It may look up commands on PATH
with `shutil.which`, but it does not install dependencies, run adapters, run
upstream tools, inspect directories, read handoff files, import rows, open or
write SQLite, create
config/data/report/dashboard/workflow/handoff artifacts, scrape, automate
browsers, call platform APIs, use account/session/cookie/token behavior,
monitor, schedule, acquire sources, prove demand, rank sources, verify
coverage, or add a compliance-review product feature.

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

## Community Signal Quality Boundary

`community-signal-lint` is a pre-import diagnostics command for one local
CSV/JSON file. `community-signal-lint-dir` is a non-recursive directory wrapper
over the same single-file contract for matched regular files directly under one
local directory. Both validate strict community fields, check import-readiness
through the same manual signal row model, and print table or JSON findings. They
do not import rows, open the local database, fetch URLs, collect sources, run
matching/scoring, package digests, generate reports, perform platform search, or
create workflow artifacts.

## Candidate Discovery Boundary

Candidate discovery does not add collectors or source types. It reads retained
local SQLite rows, filters configured and already matched tracked entities, and
surfaces candidate signals as observed phrases from configured sources and
imported local signals that need review.

The read-only `candidates` command computes the same review-oriented signals
without writing report files.

The read-only `imported-candidates` command computes an imported-only aggregate
view from retained `manual_import` rows. It surfaces observed phrases for
review and does not create report files or dashboard artifacts.

The read-only `imported-candidate-evidence` command computes a phrase-scoped
view from retained `manual_import` rows. It helps inspect why one observed
candidate phrase appeared and does not create report files or dashboard
artifacts.

The read-only `imported-entity-evidence` command computes a matched-entity
drilldown from retained `manual_import` rows. It is local read-only and
imported-only, returns privacy-safe retained local rows for
`review_imported_entity_evidence`, and does not add scraping, browser
automation, platform APIs, report files, or dashboard artifacts. It has no
account or cookie work.

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
