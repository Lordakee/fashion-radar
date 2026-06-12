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

Community signal import is the same local input pattern with repository
examples and a JSON schema for tools that produce sanitized local rows. It is
not a connector, source pack, platform collector, remote community ingestion
workflow, or source-acquisition guide.

Community signal lint is local contract validation for one CSV/JSON file or a
non-recursive batch of matched regular files directly under one local directory.
It is not a connector, source pack, platform collector, remote community
ingestion workflow, source-acquisition guide, authorization verifier, policy
workflow, or platform coverage check.

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

- Store source URLs, titles, publication timestamps, source names, short summaries, entity matches, tags, counts, and scores.
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

Avoid wording that implies complete market truth:

- "This is the hottest brand"
- "This source-set signal proves external demand"
- "This celebrity caused the trend"
- "Market-wide trend"
- "Platform-wide popularity"
- "Verified demand"
- "Top social trend"

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
- Community signal lint validates local file structure and allowed fields only,
  including optional non-recursive directory batches; it is not source
  acquisition, platform coverage verification, authorization verification, or a
  policy workflow feature.
- Trend deltas are local observed comparisons, not verified demand or complete
  source coverage.
- Experimental connectors may stop working and are not production guarantees.
- Broad non-core platform collection is excluded from `v0.1.0`.
- Account artifacts, access-control bypasses, and private data are not part of
  the project.
