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

### Opt-In

These connectors may be useful but must require explicit user enablement:

- Google News RSS.
- Google Trends official API when the user has access.
- Reddit API with user-provided credentials and accepted API terms.
- Static webpage monitoring for user-provided URL lists.

Opt-in connectors must document their limits and should fail closed when credentials or access are missing.

Google News RSS is not included in `v0.1.0`. If added later, it must be disabled by default and documented as use-at-your-own-risk because it is not a formal Google News API and programmatic use may violate Google terms.

### Experimental

These connectors are not part of the default MVP and should be disabled by default:

- Xiaohongshu/RedNote MCP or crawlers.
- MediaCrawler.
- Instaloader.
- TikTok-Api.
- TikTok Creative Center page monitoring.
- Pinterest Trends page monitoring.
- twscrape.
- yt-dlp metadata extraction for user-provided URLs.
- XPOZ or other third-party SaaS free tiers.

Experimental connectors must not block core collection, scoring, reports, or dashboards.

### Out Of Scope

The project should not include:

- Login-cookie harvesting.
- CAPTCHA bypass.
- Paywall bypass.
- Residential proxy rotation.
- Account pools.
- Hidden scraping workarounds.
- Bulk media download as a default workflow.
- Tutorials for evading platform controls.

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

Avoid wording that implies complete market truth:

- "This is the hottest brand"
- "This product is definitely viral"
- "This celebrity caused the trend"

## Quality Boundaries

Heat scores are local metrics based on configured sources. They are not global platform rankings.

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
- The default workflow avoids logged-in scraping and paywall bypass.
- Experimental connectors may stop working and are not production guarantees.
