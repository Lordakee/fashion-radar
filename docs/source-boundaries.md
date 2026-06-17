# Source Boundaries

Fashion Radar is a free-first research tool. It must be honest about source coverage, authorization, and data rights.

## Connector Risk Tiers

### Core

These connectors are suitable for the default local MVP:

- GDELT Doc API metadata and URLs.
- Official RSS/Atom feeds.
- RSSHub-compatible routes when the user accepts the route's source terms.
- Official brand newsroom, press release, RSS, or sitemap pages where automated access is allowed.

Core connectors should store source URL, title, publication time, source name, short summary where provided by the feed/API, extracted entities, and aggregate metrics.

Repository source packs are examples built from these source types. They are not
automatic subscriptions, endorsements, or guarantees that a feed will remain
available.

Manual signal import is a local input path for user-provided CSV/JSON files the
user is authorized to process. It is not a connector, platform collector, source
pack, or source-acquisition guide.

Manual signal directory dry run validates matched regular files directly under
one local directory through the same importer model without importing rows,
opening SQLite, creating workflow artifacts, fetching URLs, or collecting
sources. Manual signal directory import uses the same non-recursive local file
matching and writes only after every matched file validates.
Imported review workflow prints a copyable local command sequence after manual
signal import. It does not execute those commands, open SQLite, read configs,
create artifacts, fetch URLs, or collect sources.
Imported signal summary reads existing `manual_import` rows from local SQLite,
groups row counts by stored `source_name` and local `platform` provenance
labels where present, and creates no config, data, report, or dashboard
artifacts.
Imported entity deltas read stored matches on existing `manual_import` rows from
local SQLite, compare aggregate entity counts across collected-at windows, and
create no config, data, report, or dashboard artifacts.
`imported-entity-evidence` is local read-only and imported-only. It reads
existing `manual_import` rows from local SQLite for one requested matched
entity, returns only privacy-safe retained local rows and drilldown fields
(`window`, `id`, `source_name`, `title`, `url`, `published_at`, and
`collected_at`), and creates no config, data, report, or dashboard artifacts.
It does no scraping, no browser automation, no platform APIs, and no account or
cookie work.
Imported candidates read existing `manual_import` rows from local SQLite,
surface aggregate observed candidate phrases for review, and create no config,
data, report, or dashboard artifacts.
Imported candidate evidence reads existing `manual_import` rows from local
SQLite for one requested candidate phrase and creates no config, data, report,
or dashboard artifacts.

Imported signal review reads retained `manual_import` rows from an existing
local SQLite database in read-only mode. It may display stored `platform` labels
from retained `manual_import` rows as local provenance metadata only. It is not
a connector, source pack, platform collector, remote community ingestion
workflow, source-acquisition guide, authorization verifier, policy workflow,
demand proof, or platform coverage check.

Community signal import is the same local input pattern with repository
examples and a JSON schema for tools that produce sanitized local rows. It is
not a connector, source pack, platform collector, remote community ingestion
workflow, or source-acquisition guide.

`imported-review-workflow` is print-only and includes a read-only
review_imported_entity_evidence step after entity deltas, then a read-only
imported-candidates step for candidate phrase review before the final
read-only heat-movers step after local matching. The final step reviews local
observed heat movement from configured sources and imported local signals.
Those review outputs need review and provide no demand proof and no platform
coverage verification.

The external tool handoff templates are sanitized CSV/JSON local file handoff
templates for user-controlled external/community tools.
This is not platform collection and does not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

The external community tool export directory examples are sanitized CSV/JSON
local directory samples for user-controlled external/community tools. They are
exposed as static `directory_example_paths` pointers for local/external tool
discovery. They are not platform collection and do not add connectors,
scraping, browser automation, platform APIs, monitoring, scheduling, source
acquisition, demand proof, ranking, or coverage verification.

`community-signal-profile` prints the community handoff producer contract only.
It does not read handoff files or directories, create config/data/report
artifacts, open SQLite, fetch URLs, search platforms, log in, store cookies,
automate browsers, call platform APIs, monitor communities, rank sources,
verify platform coverage, perform source acquisition, or provide a
compliance-review workflow. Its JSON output may include
`directory_example_paths` as static checked-in directory example pointers.

`community-handoff-manifest` prints a local producer-facing directory manifest
only. It does not execute commands, inspect or create the supplied directory,
read handoff files, validate files, import rows, open or write SQLite, create
config/data/report/dashboard artifacts, fetch URLs, log in, store cookies,
call platform APIs, monitor communities, schedule work, add source/platform
connectors, prove demand, verify platform coverage, rank sources, or provide a
compliance-review workflow. It may print supplied directory/config/data paths,
the matched file pattern, a suggested filename, profile/schema/example
pointers, `directory_example_paths`, producer profile field/rule summaries, a
manifest storage note, and workflow commands for local external producers.

`external-tool-adapters` prints the external social/community tool adapter
registry as a local producer-discovery registry only. It is for
user-controlled external/community tools that need sanitized CSV/JSON local
file handoff targets and copyable local commands. It does not run adapters,
inspect directories, read handoff files, validate files, import rows, open
SQLite, or create artifacts. It is not platform collection and has no
connectors, no scraping, no browser automation, no platform APIs, no
monitoring, no scheduling, no source acquisition, no demand proof, no ranking,
and no coverage verification. Each adapter command list includes
`external-tool-readiness` as an optional local read-only preflight command,
while `external-tool-adapters` itself remains print-only and does not run
readiness or perform PATH lookup.

`external-tool-template` prints adapter-specific template rows as a local
producer handoff aid only. It is for user-controlled external/community tools
that need sanitized CSV/JSON local file handoff examples. JSON and CSV output
contain importable community handoff rows only; table output may include local
metadata, field mappings, boundaries, and copyable commands. It does not write
files, run adapters, inspect directories, read handoff files, validate files,
import rows, open SQLite, or create artifacts. It is not platform collection
and has no connectors, no scraping, no browser automation, no platform APIs,
no monitoring, no scheduling, no source acquisition, no demand proof, no
ranking, and no coverage verification. The JSON/CSV handoff rows remain
importable row output only, while table/model guidance can include the same
adapter recommended command list.

`external-tool-workflow` prints workflow metadata as a local producer handoff
wrapper only. It is for user-controlled external/community tools that need a
producer-facing wrapper around existing local commands before writing sanitized
CSV/JSON local file handoff rows. JSON output is workflow metadata, not
importable handoff rows; table output may include local metadata and copyable
commands. The printed steps include `check_external_tool_readiness`, an
optional preflight command that points to `external-tool-readiness` for local
command availability guidance before sanitized handoff rows are prepared. It
does not run generated commands, adapters, or upstream tools, and it does not
inspect the supplied directory, read handoff files, validate rows, import rows,
open SQLite, or create artifacts. It is not platform collection and has no
connectors, no scraping, no browser automation, no platform APIs, no
monitoring, no scheduling, no source acquisition, no demand proof, no ranking,
and no coverage verification.

`external-tool-readiness` reports external tool readiness and local command
readiness guidance only. It is local read-only, not print-only, because it
performs command availability only with local PATH lookup (`shutil.which`) for
known free external/community tools such as Rednote MCP, Xiaohongshu crawler,
Instaloader, TikTok-Api, yt-dlp, and X/search exports. It prints
mirror-friendly install hints and Fashion Radar next-step handoff commands for
user-controlled external/community tools that produce sanitized CSV/JSON local
file handoff rows. It does not install
dependencies automatically, does not run adapters, does not run upstream tools,
does not inspect directories, does not read handoff files, validate files,
import rows, open or write SQLite, or create config/data/report/dashboard/
workflow/handoff artifacts. It is not a scraper/connector and has no scraping,
no browser automation, no platform APIs, no account/session/cookie/token
behavior, no monitoring, no scheduling, no source acquisition, no demand proof,
no ranking, no coverage verification, and no compliance-review product feature.

`community-handoff-check-dir` is a local-only handoff readiness report for
user-controlled community signal directories. It reads only matched local
regular files and local config. It does not import rows, uses no SQLite,
creates no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
authorization/safety-review features.

Community signal lint is local contract validation for one CSV/JSON file or a
non-recursive batch of matched regular files directly under one local directory.
It is not a connector, source pack, platform collector, remote community
ingestion workflow, source-acquisition guide, authorization verifier, policy
workflow, or platform coverage check.

`community-handoff-workflow` prints copyable local commands for
`community-signal-lint-dir`, `community-candidates-dir`,
`community-handoff-check-dir`, `import-signals-dir --dry-run`,
`import-signals-dir`, and `imported-review-workflow`. Its named steps are
`lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review`. The
`review_handoff_readiness` step is the `community-handoff-check-dir`
local-only handoff readiness report before importing rows. It does not execute
commands, read the supplied directory, validate files, import rows, open or
write SQLite, fetch URLs, log in, download media, automate browsers, scrape,
monitor, watch folders, schedule work, add source/platform connectors, prove
demand, verify platform coverage, rank sources, write reports, update
dashboards, generate configs, or generate entity files. It may intentionally
print the supplied directory/config/data paths inside copyable local commands;
this differs from aggregate candidate preview output, which suppresses paths
and row details.

`community-candidates` reads one local CSV/JSON handoff file plus local config
and prints aggregate candidate phrases. It does not import rows, open SQLite,
fetch URLs, recurse directories, log in, write reports, update dashboards, or
generate entity files. It does not output the supplied file path, row URLs,
row titles, summaries, raw text, normalized keys, candidate contexts, or
representative item details.

`community-candidates` is not proof of demand, not platform coverage, not source ranking, not a source connector, not an acquisition workflow, not a scraper, not a watcher, not a scheduler, not a report writer, not a dashboard updater, not a database import, and not an entity YAML generator.

`community-candidates-dir` reads matched regular CSV/JSON handoff files directly
under one local directory plus local config and prints aggregate candidate
phrase metrics. It does not recurse, import rows, open SQLite, fetch URLs, log
in, write reports, update dashboards, generate entity files, print the supplied
directory path, expose matched file paths, expose matched file names, or expose
row URLs, row titles, summaries, raw text, normalized keys, candidate contexts,
raw validation findings, account/private fields, or representative item details.

`community-candidates-dir` is not proof of demand, not platform coverage, not
source ranking, not a source connector, not an acquisition workflow, not a
scraper, not a watcher, not a scheduler, not a report writer, not a dashboard
updater, not a database import, and not an entity YAML generator.

Entity packs are local `entities.yaml` templates. They change only local entity
matching configuration and do not add sources, source setup, collection
workflows, platform/community ingestion, scraping, social monitoring, ranking
semantics, or source-acquisition guidance.

### Opt-In

These connectors may be useful but must require explicit user enablement:

- Google News RSS.
- Google Trends official API when the user has access.
- Reddit API with user-provided credentials and accepted API terms.
- Static webpage monitoring for user-provided URL lists.

Opt-in connectors must document their limits and should fail closed when credentials or access are missing.

Google News RSS is not included in `v0.1.0`. If added later, it must be disabled by default and documented as use-at-your-own-risk because it is not a formal Google News API and programmatic use may violate Google terms.

### Experimental

These connector categories are not part of `v0.1.0`, are not required for core
operation, and must not be treated as endorsed how-to instructions:

- Non-core platform collectors.
- User-account-dependent collectors.
- Media metadata utilities for user-provided URLs.
- Third-party source aggregation services.

Experimental connectors must not block core collection, scoring, reports, or
dashboards. Any future non-core connector must be an explicit opt-in with its
own terms, risk labels, and privacy review.

### Out Of Scope

The project should not include:

- Broad platform collection in the default workflow.
- Account-based collection artifacts.
- Access-control bypasses.
- Residential network-routing workarounds.
- Account pools.
- Hidden platform workarounds.
- Bulk media download as a default workflow.
- Tutorials for evading source controls.
- Private data collection.

## Storage Boundaries

Default storage should be conservative:

- Store source URLs, titles, publication timestamps, source names, optional local
  `platform` provenance labels for imported rows, short summaries, entity
  matches, tags, counts, and scores.
- Avoid storing full article text by default.
- Avoid storing original images or videos.
- Avoid storing user comments as redistributable assets.
- Preserve source links so users can read original content on the source site.
- Display source attribution beside representative items.
- Add attribution footer to generated reports.
- Skip extraction for known paywalled domains unless the source itself provides permitted metadata.

## Robots And Fetching

Before fetching an article page for extraction, collectors must check robots.txt.

Default fetch behavior:

- Use a descriptive User-Agent.
- Respect robots disallow rules.
- Use conservative timeouts.
- Use bounded retries.
- Use source-specific rate limits where configured.
- Record skipped URLs with reasons.
- Cache robots rules per domain within a collection run.

GDELT fetch behavior:

- Use configurable request throttling, with a conservative default near 1 request per second.
- Use bounded exponential backoff.
- Store GDELT-provided metadata and links, not republished article bodies.

## Output Boundaries

Reports and dashboards should describe signals, not assert certainty.

Preferred wording:

- "Rising signal"
- "Observed in 6 sources"
- "Mention count increased in this configured source set"
- "Needs human review"
- "Candidate signal from configured sources and imported local signals"
- "Observed phrase needs review"
- "Local observed trend delta"
- "Signal changed within this configured local source set"
- "Imported row platform provenance label"
- "Stored local provenance label, not platform coverage"

Avoid wording that implies complete market truth:

- "This is the hottest brand"
- "This source-set signal proves external demand"
- "This celebrity caused the trend"
- "Market-wide trend"
- "Platform-wide popularity"
- "Verified demand"
- "Top social trend"

### Heat Movers

The `heat-movers` command reports local observed heat movement for one
configured source set. It compares configured sources and imported local
signals, and the output needs review. It provides no demand proof and no
platform coverage verification.

## Quality Boundaries

Heat scores are local metrics based on configured sources and imported local
signals. They are not rankings outside that local source set.

Candidate signals are observed phrases from configured sources and imported
local signals and need review. They should not be presented as validated
entities.

The dashboard should show:

- Source count.
- Representative links.
- Time window.
- Failed source runs.
- Missing data warnings.
- Whether a source is core, opt-in, or experimental.

## README Requirements

The public README must explain:

- The project does not provide full social-platform coverage.
- Users are responsible for respecting source terms, robots rules, and API terms.
- The default workflow avoids account-based collection and access-control
  bypasses.
- Manual signal import is a local input path, not a platform connector or
  instructions for obtaining platform exports.
- Manual signal directory dry run and explicit directory import read matched
  local files only; they are not source acquisition, platform coverage
  verification, authorization verification, or policy workflow features.
- Imported signal review reads retained local SQLite rows only; it is not source
  acquisition, platform/community coverage verification, authorization
  verification, or a policy workflow feature.
- Imported `platform` labels are preserved only as local SQLite/review-output
  provenance; they are not scraping, crawling, social connectors, source
  acquisition, platform/community coverage verification, demand proof,
  authorization verification, or policy workflow features.
- Imported candidate review reads retained local SQLite rows only; it is not
  a source collector, platform/community coverage check, authorization check, or
  policy review feature.
- Imported candidate evidence reads retained local SQLite rows only for one
  requested phrase; it is not a source collector, platform/community coverage
  check, authorization check, or policy review feature.
- Community signal lint validates local file structure and allowed fields only,
  including optional non-recursive directory batches; it is not source
  acquisition, platform coverage verification, authorization verification, or a
  policy workflow feature.
- Community handoff manifest prints a local producer manifest only; it does not
  execute commands, inspect or create the supplied directory, read handoff
  files, validate files, import rows, open/write SQLite, add source/platform
  connectors, prove demand, verify platform coverage, rank sources, write
  reports, update dashboards, generate configs, or generate entity files. The
  README must warn that saved manifests belong outside the matched export
  directory or behind an excluded filename/pattern, especially JSON export
  directories using `--pattern "*.json"`.
- Community handoff workflow prints copyable local commands only; it does not
  execute commands, read the supplied directory, validate files, import rows,
  open/write SQLite, add source/platform connectors, prove demand, verify
  platform coverage, rank sources, write reports, update dashboards, generate
  configs, or generate entity files.
- Community handoff check directory reports are local-only handoff readiness
  reports. They read matched local regular files and local config, do not
  import rows, use no SQLite, create no config/data/report/dashboard/digest
  artifacts, and add no fetch URLs/login/platform APIs/download media/browser
  automation/scrape/crawl/monitor/watch/schedule/connectors/source acquisition/
  demand proof/ranking/coverage verification/entity generation/compliance/
  policy/authorization/safety-review features.
- External tool readiness reports are local read-only command availability only
  guidance for user-controlled external/community tools producing sanitized
  CSV/JSON local file handoff rows. They may use local PATH lookup but must not
  install dependencies, run adapters, run upstream tools, inspect directories,
  read handoff files, import rows, open/write SQLite, create artifacts, scrape,
  automate browsers, call platform APIs, use account/session/cookie/token
  behavior, monitor, schedule, acquire sources, prove demand, rank sources,
  verify coverage, or add compliance-review product features.
- Community candidate directory preview reads matched local files only and
  outputs aggregate candidate phrase metrics only; it is not source acquisition,
  platform/community coverage verification, authorization verification, or a
  policy workflow feature.
- Trend deltas are local observed comparisons, not verified demand or complete
  source coverage.
- Experimental connectors may stop working and are not production guarantees.
- Broad non-core platform collection is excluded from `v0.1.0`.
- Account artifacts, access-control bypasses, and private data are not part of
  the project.
