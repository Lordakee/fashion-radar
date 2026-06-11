# Fashion Radar Design

## Objective

Create a free-first open source fashion trend radar that runs locally and produces daily intelligence about fashion media, brands, designers, celebrities, bags, shoes, and trend terms.

The MVP must be useful before any fragile social-media crawler is added. It should rely on public, stable, mostly free sources, then allow experimental connectors later.

## System Shape

Fashion Radar is a local Python application with three entry points:

- CLI commands for collection, scoring, and report generation.
- A Streamlit dashboard for browsing recent items and rankings.
- YAML configuration files for sources, tracked entities, and scoring weights.

The system stores data in SQLite and generates Markdown/JSON report artifacts that can be committed, shared, emailed, or pasted into a team chat.

## Data Flow

```text
YAML config
  -> collectors
  -> normalized raw items
  -> SQLite storage
  -> entity matcher
  -> daily mention metrics
  -> heat scorer
  -> Markdown/JSON report
  -> Streamlit dashboard
```

## Core Sources

The MVP core should include only sources that are reasonable for unattended local use:

- RSS feeds.
- RSSHub-compatible feeds.
- GDELT Doc API keyword searches.
- Official brand/newsroom RSS or sitemap pages where allowed.
- Public article extraction through trafilatura when a collected item has a URL and extraction is allowed.

Google News RSS is excluded from the `v0.1.0` implementation. It may return later only as a disabled-by-default experimental connector with explicit use-at-your-own-risk documentation because it is not a formal Google News API and programmatic use may violate Google terms.

Source configuration must support:

- Source name.
- Source type.
- URL or query.
- Source weight.
- Enabled/disabled state.
- Tags such as `fashion_media`, `brand_newsroom`, `trend_source`, or `news_search`.

## Experimental Sources

The design must leave room for later connectors but not depend on them:

- RedNote/Xiaohongshu MCP and crawlers.
- MediaCrawler.
- Instaloader.
- TikTok-Api.
- TikTok Creative Center page monitoring.
- Pinterest Trends page monitoring.
- Google News RSS.
- Google Trends unless the user has official API access.
- Reddit unless the user provides API credentials and accepts Reddit API terms.
- twscrape.
- yt-dlp for given URL metadata.
- XPOZ MCP free-tier checks.

Experimental connector failures should be logged and skipped. They must not stop RSS, GDELT, scoring, reports, or the dashboard.

## Entity Model

The first version tracks six entity types:

- `brand`: The Row, Miu Miu, Khaite, Loewe.
- `designer`: Jonathan Anderson, Miuccia Prada.
- `celebrity`: Zendaya, Jennie, Bella Hadid.
- `product`: The Row Margaux, Miu Miu Arcadie, Alaia Le Teckel.
- `category`: ballet flats, east-west bag, suede jacket.
- `trend`: quiet luxury, office siren, boho chic.

Each entity should have:

- Canonical name.
- Type.
- Aliases.
- Optional parent brand.
- Optional category tags.
- Optional initial weight.
- Alias quality settings where needed.

Matching in MVP is deterministic alias matching with case-insensitive normalization, word boundaries, and a match confidence field. The matcher should prefer transparent behavior over complex NLP.

Alias rules:

- Do not match aliases as arbitrary substrings.
- Require word boundaries for Latin-script aliases.
- Treat common single-word aliases as invalid unless explicitly marked as safe.
- Allow short product aliases only when a parent brand or contextual token is present.
- Validate duplicate aliases across entities at config load time.
- Store match confidence even if the first implementation uses simple confidence constants.

## Storage

SQLite tables:

- `sources`: configured source records and weights copied from YAML for run traceability.
- `items`: normalized collected items.
- `item_entities`: matched entities for each item.
- `entity_daily_metrics`: daily mention counts and weighted source counts.
- `reports`: generated report paths and metadata.
- `collector_runs`: source run status, item count, errors, and timestamps.

The schema should be small and documented. Use SQLAlchemy 2.x table definitions and a repository layer. Alembic can be deferred until schema changes become frequent, but the table definitions should not depend on SQLite-only behavior.

All timestamps must be stored in UTC. Dashboard display can convert to local time.

## Heat Scoring

The first heat score is deterministic:

```text
heat_score =
  weighted_mentions_7d
+ growth_bonus_7d_vs_30d
+ source_diversity_bonus
+ high_weight_source_bonus
```

Recommended status labels:

- `new`: entity appears recently but had little or no previous history.
- `rising`: recent score is materially above baseline.
- `hot`: score and source diversity are both high.
- `stable`: mentions continue without strong growth.
- `cooling`: recent mentions are below baseline.

The exact constants should live in YAML so they can be tuned without code changes.

Fixture tests must prove score behavior for:

- A new entity with one weak mention.
- A stable entity with many mentions.
- A rising entity with recent growth.
- A high-volume source that should not dominate after per-domain weighting.

## Report Output

The daily Markdown report should include:

- Top industry signals.
- Rising brands.
- New or rising bags/shoes/products.
- Celebrity styling mentions.
- Designer/creative-director news.
- Items needing human review.
- Source health summary.

The JSON report should contain the same structured data for future integrations.

Every report item must include source name, source URL, and publication time. Markdown reports should include an attribution footer and must not reproduce full articles.

## Dashboard

Streamlit MVP pages:

- Daily Brief.
- Brand Heat.
- Product Radar.
- Celebrity Style.
- Source Health.

The dashboard should read from SQLite and report files. It should not trigger network collection on page load.

## CLI

Target commands:

```text
fashion-radar init
fashion-radar doctor
fashion-radar collect
fashion-radar score
fashion-radar report
fashion-radar run
fashion-radar dashboard
```

`run` should execute collect -> score -> report.

## Error Handling

Collectors should isolate failures per source:

- A bad RSS feed or GDELT query should create a failed `collector_runs` row and continue.
- A network timeout should be recorded and skipped.
- A malformed item should be skipped with a reason.
- A database error should fail fast.
- HTTP clients must use a descriptive User-Agent.
- GDELT must use configurable request throttling, defaulting to roughly 1 request per second, and bounded exponential backoff.
- Article extraction must check robots.txt before fetching pages and cache robots rules per domain within a collector run.
- Known paywalled domains should be configurable and skipped for extraction.
- Repeated source failures should mark a source unhealthy after a configurable threshold.

## Testing Strategy

Tests must cover:

- Config loading.
- Entity alias matching.
- URL/title/date normalization.
- SQLite schema initialization.
- Item upsert/deduplication.
- Heat score calculation.
- Markdown report rendering.
- CLI smoke commands using temporary directories.

Network calls should be tested with fixtures or mocked HTTP responses. Core scoring and matching should use real local data structures.

## GitHub Readiness

Before first upload, repository should include:

- README with purpose, installation, quickstart, and limitations.
- LICENSE.
- `.gitignore`.
- `.env.example`.
- `.pre-commit-config.yaml`.
- `pyproject.toml`.
- `uv.lock` if dependency resolution is performed during implementation.
- `configs/*.example.yaml`.
- `data/README.md` and `reports/README.md` with generated outputs ignored.
- Tests.
- `docs/` with architecture and review workflow.
- `docs/source-boundaries.md` with connector risk tiers and storage/copyright boundaries.
- GitHub Actions CI for tests and ruff.

## Review Gates

Claude Code must review:

1. This plan before implementation.
2. Phase 1 code before Phase 2 starts.
3. Phase 2 code and next plan before Phase 3 starts.
4. Final repository state before GitHub upload.
