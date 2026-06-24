# Changelog

All notable changes to Fashion Radar will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Stage 173 docs/test parity for XPOZ MCP / Social Data API
  `external-tool-readiness` discoverability for sanitized CSV/JSON local file
  handoff rows from user-controlled external/community tools. This is
  docs/test-only and adds no XPOZ API calls, MCP execution, API keys,
  connectors, scraping, browser automation, platform APIs, login/cookie/token
  behavior, source acquisition, demand proof, ranking, coverage verification,
  or compliance-review product feature.
- Stage 80 external tool import onboarding docs for the local route from a
  user-controlled external export directory to sanitized CSV/JSON handoff,
  directory lint, candidate preview, readiness review, import, and post-import
  review. This is docs/test-only and adds no upstream tool execution, platform
  search, scraping, platform APIs, connectors, demand proof, ranking, or
  platform coverage verification.
- Python package foundation with Typer CLI.
- YAML source, entity, and scoring configuration.
- RSS/Atom, RSSHub-compatible, and GDELT collector support.
- SQLite persistence with schema versioning and migrations through schema v5.
- Deterministic entity matching with context gates for broad/common aliases.
- Transparent heat scoring with current/baseline windows, source weights,
  source diversity, growth, high-weight source bonuses, labels, and stable
  first-seen tracking.
- Markdown and JSON daily report generation.
- Optional local Streamlit dashboard.
- CodeGraph project setup for Claude Code/Codex navigation.
- Source-boundary, scoring, retention, dashboard, mirror, and GitHub-readiness
  documentation.
- CI for locked install, lint, format check, tests, wheel build, installed CLI
  smoke, packaged template smoke, and dashboard extra smoke.
- Safe `schedule-example` CLI output for cron, systemd user timers, and GitHub
  Actions.
- Public RSS/GDELT fashion source-pack example.
- Scheduling and source-pack documentation.
- Stage 8 candidate discovery documentation for observed phrases, review
  windows, CLI usage, report/dashboard behavior, and source boundaries.
- Manual signal import documentation for local user-provided CSV/JSON files,
  dry runs, follow-up review commands, and privacy/source boundaries.
- Report and dashboard wording for candidate signals from configured sources and
  imported local signals that need review.
- Read-only `trends` CLI command for local observed entity and candidate signal
  deltas between scoring snapshots.
- Dashboard Trend Deltas view using local SQLite state and forwarded
  `--config-dir` settings.
- Trend delta documentation covering local-only scope, baseline windows,
  read-only behavior, and source-coverage limits.
- Optional local digest packaging for generated daily reports, including latest
  report artifacts, a report index, a local `.eml` handoff file, and stdout
  summary output.
- Local read-only `source-pack-lint` command for source YAML quality diagnostics
  and documentation for expanded public-pack RSS/GDELT categories.
- Community signal import contract documentation, examples, and JSON schema for
  sanitized local CSV/JSON handoff into the existing manual import command.
- Local read-only `community-signal-lint` command for community CSV/JSON handoff
  contract diagnostics before import, without fetching URLs, opening SQLite,
  importing rows, or creating artifacts.
- Local read-only `community-signal-lint-dir` command for non-recursive
  directory-level community CSV/JSON handoff diagnostics before import.
- Local read-only `import-signals-dir --dry-run` command for non-recursive
  importer-model validation of matched local signal files without SQLite writes.
- Validated local `import-signals-dir` execution for non-recursive directory
  import after every matched file passes importer-model validation.
- Local read-only `imported-signals` command for reviewing retained
  `manual_import` rows and stored match presence after local file imports.
- Local read-only `imported-signals-summary` command for grouping retained
  `manual_import` rows by stored source-name label and item-level stored match
  presence.
- Local read-only `imported-entity-deltas` command for comparing stored matched
  entities on retained `manual_import` rows across collected-at windows.
- Local read-only imported-only `imported-entity-evidence` command for
  reviewing privacy-safe retained local rows behind one `manual_import` stored
  matched entity, plus the print-only `review_imported_entity_evidence`
  workflow step. It adds no scraping, browser automation, platform APIs, or
  account or cookie behavior.

- Local read-only `imported-candidates` command for reviewing candidate phrases
  from retained `manual_import` rows only.
- Local read-only `imported-candidate-evidence` command for reviewing retained
  `manual_import` rows behind one imported candidate phrase.
- Added `community-candidates` for local pre-import candidate phrase previews
  from one supplied community signal CSV/JSON handoff file.
- Added `community-candidates-dir` for local non-recursive aggregate-only
  pre-import candidate phrase previews from matched community signal handoff
  files in one directory.
- Local `imported-review-workflow` command for printing a copyable post-import
  review sequence without executing it.
- Local print-only `community-handoff-workflow` command for printing the
  directory community handoff sequence without reading the supplied directory or
  executing generated commands, intentionally including supplied
  directory/config/data paths inside copyable local commands. Stage 61 adds the
  `review_handoff_readiness` step for the `community-handoff-check-dir`
  local-only handoff readiness report before importing rows; the workflow does
  not execute commands.
- Local print-only `community-handoff-manifest` command for printing a
  directory producer manifest with handoff pattern, suggested filename,
  producer contract fields, storage guidance, and workflow commands without
  reading the supplied directory or executing generated commands.
- Local-only handoff readiness report `community-handoff-check-dir` for
  matched local community signal directory files and local config, without
  importing rows, using SQLite, creating config/data/report/dashboard/digest
  artifacts, fetching URLs, logging in, calling platform APIs, downloading
  media, browser automation, scrape/crawl/monitor/watch/schedule/connectors,
  source acquisition, demand proof, ranking, coverage verification, entity
  generation, or compliance/policy/authorization/safety-review features.
- Stage 57 `heat-movers` docs for read-only local observed heat movement over
  one configured source set, comparing configured sources and imported local
  signals where output needs review, with no demand proof and no platform
  coverage verification.
- Stage 58 `imported-review-workflow` docs for a final read-only `heat-movers`
  handoff over local observed heat movement from configured sources and imported
  local signals, with no demand proof and no platform coverage verification.
- Stage 60 `imported-review-workflow` docs for a read-only imported-candidates
  step for candidate phrase review before the final read-only heat-movers step
  over local observed heat movement from configured sources and imported local
  signals, with no demand proof and no platform coverage verification.
- Stage 65 docs for the `imported-entity-evidence` local read-only imported-only
  drilldown over retained local rows, with privacy-safe fields only and no
  scraping, browser automation, platform APIs, account or cookie work.
- Print-only `community-signal-profile` command and example JSON producer
  contract for external tools that generate sanitized community signal handoff
  files.
- Stage 54 external tool handoff templates documented at
  `examples/community-tool-handoff.example.csv` and
  `examples/community-tool-handoff.example.json` as sanitized CSV/JSON local
  file handoff templates for user-controlled external/community tools.
- Stage 55 external community tool export directory examples documented at
  `examples/community-tool-handoff-directory.example/README.md`,
  `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`,
  `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`,
  `examples/community-tool-handoff-directory.example/json/community-tool-a.json`,
  and
  `examples/community-tool-handoff-directory.example/json/community-tool-b.json`
  as sanitized CSV/JSON local directory samples for user-controlled
  external/community tools. `community-signal-profile --format json` and
  `community-handoff-manifest --format json` expose those same pointers as
  `directory_example_paths`; this is not platform collection, connectors,
  scraping, browser automation, platform APIs, monitoring, scheduling, source
  acquisition, demand proof, ranking, or coverage verification.
- Stage 62 docs for the print-only `external-tool-adapters` external
  social/community tool adapter registry and local producer-discovery registry
  for sanitized CSV/JSON local file handoff by user-controlled
  external/community tools. This is local and print-only, not platform
  collection, with no connectors, no scraping, no browser automation, no
  platform APIs, no monitoring, no scheduling, no source acquisition, no demand
  proof, no ranking, and no coverage verification. Each adapter command list
  includes `external-tool-readiness` as an optional local read-only preflight
  command, while `external-tool-adapters` itself remains print-only and does
  not run readiness or perform PATH lookup.
- Stage 63 `external-tool-template` command for local, print-only
  adapter-specific template rows for user-controlled external/community tools
  that need sanitized CSV/JSON local file handoff examples. JSON and CSV output
  contain importable community handoff rows only; table output can include local
  metadata and copyable commands. JSON/CSV handoff rows remain importable row
  output only, while table/model guidance can include the same adapter
  recommended command list. This is not platform collection, with no
  connectors, no scraping, no browser automation, no platform APIs, no
  monitoring, no scheduling, no source acquisition, no demand proof, no
  ranking, and no coverage verification.
- Stage 64 `external-tool-workflow` command for local, print-only workflow
  metadata over a producer-facing wrapper around existing local commands for
  user-controlled external/community tools that need sanitized CSV/JSON local
  file handoff rows. JSON output is workflow metadata, not importable handoff
  rows; table output can include local metadata and copyable commands. It does
  not inspect directories, read handoff files, import rows, open SQLite, or
  create artifacts. This is not platform collection, with no connectors, no
  scraping, no browser automation, no platform APIs, no monitoring, no
  scheduling, no source acquisition, no demand proof, no ranking, and no
  coverage verification.
- Stage 66 `external-tool-readiness` external tool readiness documentation for
  a local read-only, command availability only readiness guide over known free
  external/community tools such as Rednote MCP, Xiaohongshu crawler,
  Instaloader, TikTok-Api, yt-dlp, and X/search exports. It prints
  mirror-friendly install hints and Fashion Radar next-step handoff commands
  for user-controlled external/community tools producing sanitized CSV/JSON
  local file handoff rows, but it does not install dependencies automatically,
  does not run adapters, does not run upstream tools, does not inspect
  directories, does not read handoff files, import rows, open/write SQLite, or
  create config/data/report/dashboard/workflow/handoff artifacts. This is not a
  scraper/connector and has no scraping, no browser automation, no platform
  APIs, no account/session/cookie/token behavior, no monitoring, no scheduling,
  no source acquisition, no demand proof, no ranking, no coverage verification,
  and no compliance-review product feature.
- Stage 67 `external-tool-workflow` now prints an early
  `check_external_tool_readiness` preflight step pointing to the local
  read-only `external-tool-readiness` command before sanitized CSV/JSON
  external/community handoff rows are prepared. The workflow itself remains
  local and print-only, does not execute generated commands or upstream tools,
  and adds no connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product feature.
- Stage 75 docs for the complete `external-tool-adapters` adapter matrix in
  `README.md` and `docs/cli-reference.md`, guarded by CLI docs tests. This is
  documentation/test-only and adds no runtime adapter or external-platform
  behavior.
- Stage 77 optional expanded watchlist community-signal sample for local
  `fashion-watchlist` import, match, report, and trend walkthroughs using
  synthetic checked-in rows. It does not fetch URLs, collect platform data,
  prove demand, rank brands, verify platform coverage, or add connectors.
- Stage 78 external/community adapter contract parity tests so adapter field
  mappings, template model metadata, workflow commands, readiness commands, and
  dry-run guidance stay aligned with the local community signal profile. This
  is test/docs-only and adds no scraping, platform APIs, connectors, source
  acquisition, demand proof, ranking, or platform coverage verification.
- Stage 79 onboarding docs for the recommended manual repo-local first run,
  automated source-checkout smoke, installed-wheel smoke, reset path, beginner
  CLI roadmap, and optional entity-pack local matching layer. This is docs-only
  and adds no live collection, platform automation, connectors, sources,
  ingestion, demand proof, ranking, or platform coverage verification.
- Stage 53 community handoff guardrail tests for prohibited-field lint
  coverage, producer-profile command order, docs drift, and parser rejection.
- Optional fashion entity watchlist pack for broader local matching coverage
  using the existing `entities.yaml` schema.
- Local read-only `entity-pack-lint` command for entity YAML quality diagnostics
  and documentation for matcher-context, product parent-brand, tag, and default
  weight/confidence review.
- Stage 38 local schema maintenance documentation for explicit `migrate-db`
  SQLite initialization/upgrades and read-only `doctor` schema status.

### Fixed

- Stage 188 isolates injected collector/workflow tests from proxy-configured
  host environments and corrects roadmap emphasis toward source coverage,
  source health, matching quality, and optional report summaries over further
  external/community handoff expansion.

### Changed

- Strengthened first-run sample smoke so the checked-in community sample must
  import, match starter entities, appear in reports, produce entity trend
  deltas, and keep untracked candidates empty under starter config.
- Clarified `imported-signals` table output by labeling stored match presence
  as matched rows, and added CLI/read-only SQLite regressions.
- Aligned CI, contribution docs, PR/issue templates, and upload smoke commands
  with release lockfile checks that ignore user-level uv mirror config.
- Adjusted CI and contributor verification so `uv sync --check` runs after a
  fresh locked environment install instead of before `.venv` exists.
- Stabilized GitHub Actions CLI help tests by disabling Typer forced terminal
  rendering in the pytest step.
- Added concrete GitHub security and conduct reporting paths for public launch.
- Preserved optional `platform` provenance from manual/community imports in
  local SQLite and imported-signal review outputs. These labels remain local
  metadata and do not add scraping, crawling, social connectors, source
  acquisition, platform coverage, or demand proof.

### Not Included In 0.1.0

- No default Google News RSS connector.
- No broad non-core platform connector in the default workflow.
- No paid external-service requirement for the core workflow.
- No account-based collection, access-control bypass, or private data
  collection.
