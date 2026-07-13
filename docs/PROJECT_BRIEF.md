# Fashion Radar Project Brief

## Goal

Build **Fashion Radar**, a free-first open source tool that helps buyers, merchandisers, brand operators, content teams, and founders monitor fashion information every day.

The tool should discover and summarize:

- Fashion industry news.
- Celebrity styling and red carpet/street style signals.
- Luxury and designer brand movement.
- Emerging designer brands.
- New hot bags, shoes, and product lines.
- Trend terms and category signals.
- Brand and product heat changes over time.

The first GitHub-ready version should run locally, use mostly free public sources, and avoid depending on fragile logged-in social scraping for its core workflow.

## Product Positioning

Fashion Radar is not a generic scraper. It is a daily fashion intelligence workflow:

1. Collect public fashion signals from reliable free sources.
2. Normalize items into a shared data model.
3. Match brands, designers, celebrities, product lines, categories, and trend words.
4. Score local heat changes using mention volume, recent growth, source weight, and source diversity across configured sources and imported local signals.
5. Generate a daily Markdown/JSON/HTML report.
6. Show rankings and recent signals in a Streamlit dashboard.

## Core Users

- Buyer and merchandising teams: need trend and product signals for buying, assortment, and category decisions.
- Brand/content teams: need celebrity styling, social trend language, and daily content ideas.
- Founders/managers: need concise industry and competitor briefings.
- Individual fashion researchers: need searchable records and quick daily summaries.

## Free-First Boundary

Minimum core sources must work without paid social listening products and without personal account cookies:

- RSS/Atom feeds and RSSHub-compatible routes.
- GDELT Doc API.
- Official RSS feeds.

Optional article-extra collection is provided by the optional `article` extra and can use:

- Configured public HTML seed URLs.
- Allowed official newsroom/press-release HTML pages and sitemap discovery.

Optional sources may require user-provided credentials, approval, or explicit opt-in:

- Google News RSS, treated as post-MVP experimental and disabled because it is not a formal Google News API and programmatic use may violate Google terms.
- Google Trends official API, only when the user has approved access.
- Reddit API, only with user-provided credentials and clear usage boundaries.
- Public trend pages where legally and technically reasonable.

Experimental sources can be added later, but must not block the daily report:

- RedNote/Xiaohongshu — Phase 2 activates Xiaohongshu as an opt-in connector via xiaohongshu-mcp (login-required, use-at-your-own-risk).
- MediaCrawler.
- Instaloader.
- TikTok-Api.
- twscrape.
- yt-dlp for URL metadata/media extraction.
- XPOZ or other SaaS free tiers.

## Non-Goals For MVP

- No paid API requirement.
- No account pool.
- No proxy pool.
- No high-frequency scraping.
- No automated posting.
- No private user data collection.
- No claim that the tool provides full-platform Instagram, TikTok, X, or Xiaohongshu coverage.
- No LLM dependency in the first core pipeline. The first version should work with deterministic extraction and scoring. Optional LLM summarization can be added later.
- No login-cookie, proxy-pool, CAPTCHA-bypass, or paywall-bypass behavior in the default workflow; login-based social-platform collection is opt-in and use-at-your-own-risk (Phase 2 adds Xiaohongshu), provides no demand proof and no platform coverage verification, and users are responsible for each platform's terms.

## Recommended MVP

The first GitHub-ready MVP should include:

- Python package with CLI.
- YAML configuration for sources and tracked entities.
- SQLite database.
- RSS/GDELT collectors.
- No Google News RSS in v0.1.0 implementation.
- Optional public webpage extraction through trafilatura.
- Entity matcher with aliases.
- Daily heat scorer.
- Markdown, JSON, and companion HTML report generation.
- Streamlit dashboard.
- Tests for core logic.
- README, installation guide, sample config, license, and contribution notes.

## Review Workflow Required By The User

The project must be developed in review-gated stages.

Before implementation:

1. Write project goal, architecture, technical stack, implementation method, and phase plan.
2. Submit them to Claude Code for review.
3. Adjust the plan based on review findings.
4. Continue only after review is acceptable.

At every development node:

1. Finish the planned node.
2. Run tests and checks.
3. Ask Claude Code to review the newly added code.
4. Fix critical and important findings.
5. Submit the next phase plan to Claude Code for review.
6. Continue only after that review.

## Initial Technical Stack

- Python 3.11+.
- Typer for CLI commands.
- Pydantic for config and normalized models.
- SQLAlchemy 2.x with SQLite for persistence. Use a small repository layer and keep the schema portable enough for a future PostgreSQL option.
- feedparser for RSS/Atom feeds.
- httpx for HTTP requests.
- trafilatura for public article extraction.
- PyYAML for configuration.
- pandas for dashboard tables and report support.
- Streamlit for local dashboard.
- pytest for tests.
- ruff for linting and formatting.
- uv for dependency management.
- platformdirs for user config/data/report directories.
- python-dateutil for mixed date parsing.

## Repository Name

Recommended repository directory:

```text
fashion-radar
```

Recommended GitHub repository name:

```text
fashion-radar
```

## Recommended First Public Version

Version `v0.1.0` should promise only:

- RSS and GDELT ingestion with source attribution and rate limiting.
- SQLite storage.
- YAML source/entity/scoring configuration.
- Dictionary entity matching.
- Transparent heat scoring.
- Daily Markdown, JSON, and companion HTML reports.
- Basic Streamlit dashboard.
- Typer CLI.
- Tests and CI.
- Configured HTML seed URLs and sitemap discovery are current optional `article`-extra v0.1 capabilities.

Google News RSS, Google Trends, Reddit, and social-platform connectors should be opt-in post-MVP enhancements unless their authorization and access boundaries are clear.

## Current Review-Aligned Priorities

Before expanding any experimental or community handoff surface, roadmap work
should stay focused on the core collect/match/score/report path:

- keep using read-only source-liveness evidence as optional point-in-time
  diagnostics for a user's configured public sources and curated public-source
  coverage;
- maintain the broader public source pack while keeping the default starter
  config compact enough for first runs;
- continue improving deterministic matching quality after the default starter
  source expansion and common Latin diacritic alias matching added in Stage 195;
- keep further report summary or explanation refinements optional, local, and
  post-core.

The bundled source examples and source-liveness diagnostics do not prove demand,
source ranking, or platform-wide coverage.

Experimental/community handoff expansion remains frozen while these remaining
core gaps are addressed.

## Required Compliance Defaults

- Fetchers must use a descriptive User-Agent.
- Article extraction must check robots.txt before fetching eligible pages.
- Paywalled sources must be skipped unless a feed/API provides permitted metadata.
- Reports must show source name and source URL for every representative item.
- Reports must use short snippets and links, not republished full articles.
- GDELT requests must use configurable throttling, defaulting to a conservative request rate, and exponential backoff.
- Google News RSS must not ship as a default v0.1.0 source.
