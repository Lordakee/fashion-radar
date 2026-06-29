# Phase 1 — Web Collectors (Official Sites & News) Design

- **Date:** 2026-06-29
- **Status:** Draft (pending Claude Code review → opencode revision per project iron rules)
- **Track:** New mainline — direct acquisition (boundaries overturned by project owner)
- **Predecessor:** v0.1.x stage track ended at Stage 209 (`e8567fc`). Stage 210 (markdown report snippet hygiene) plan exists but is paused while this new mainline is active.
- **Spec author workflow:** This spec is the brainstorming artifact. After user approval, `writing-plans` produces the implementation plan; that plan is reviewed by local Claude Code, revised by opencode (`glm-5.2 --variant max`), then implemented with TDD; the resulting code is reviewed by Claude Code before the next phase.

## 1. Context & Complete Mainline Roadmap

The project owner overturned the prior "no direct scraping" boundaries. Fashion Radar will now acquire fashion signals directly from social platforms and web sources by **wrapping mature external tools** (Architecture Approach A), not by reinventing reverse-engineered signing or login flows.

The complete acquisition target set (all must ship, none dropped):

| Phase | Target | Wrapped tool | Login? | Status |
|---|---|---|---|---|
| **1** | **Official sites & news (RSS + HTML + sitemap)** | feedparser + trafilatura + self-hosted RSSHub | No | **This spec** |
| 2 | Xiaohongshu (小红书) | `xiaohongshu-mcp` (Go MCP, headless browser) | Yes (QR) | Planned |
| 3 | Instagram | `instaloader` | Yes | Planned |
| 4 | X / Twitter | `twitter-cli` (cookie, free) | Yes (cookie) | Deferred (committed) |
| 5 | YouTube | `yt-dlp` | No | Deferred (committed) |

Phase 2 also introduces the **login/credential storage model** (a new gitignored credentials directory + changes to `scripts/check_release_hygiene.py` and storage boundaries). Phase 1 deliberately avoids that complexity so the new collector architecture and the boundary/doc reversal land in isolation.

## 2. Phase 1 Goal

Add direct acquisition of fashion official-site and news content via three complementary, robots-respecting mechanisms, reusing existing collector infrastructure and mature libraries with minimal new code:

1. **RSS / RSSHub expansion** — broaden feed coverage via source-pack data + documentation of self-hosted RSSHub. Zero new collector code.
2. **HTML page collector** — fetch a configured list of seed page URLs, extract main article text, store as items. `SourceType.HTML`.
3. **Sitemap discovery collector** — discover article URLs from a site's sitemap, then fetch+extract each. `SourceType.SITEMAP`.

**Core product gap closed:** the current pipeline can only ingest RSS/Atom, RSSHub-compatible feeds, and GDELT metadata. Sites that publish via plain HTML pages or sitemaps (but no feed) are invisible. Phase 1 closes that acquisition gap on the `collect` side of `collect -> match -> report`.

## 3. Non-Goals (Phase 1)

- No link-following crawler (seed-URL-only; bounded crawl deferred to a later phase).
- No social platform collectors (Xiaohongshu / Instagram / X / YouTube = Phases 2–5).
- No login/cookie/credential storage model (Phase 2).
- No overturn of the **social-platform scraping ban** in docs — Phase 1 only adds HTML/sitemap as allowed robots-respecting web acquisition and keeps the social ban until Phase 2.
- No change to matching, scoring, candidate discovery, reports, dashboard, DB schema (the `items` table is reused as-is), or dependency core set.
- No Jina Reader / cloud extraction path (kept as a documented future alternative; Phase 1 is local-first via trafilatura).

## 4. Tool Selection (wrap mature projects; avoid secondary development)

| Capability | Wrapped tool | Already in repo? | New code |
|---|---|---|---|
| RSS/Atom parsing | `feedparser` | Core dependency | None |
| RSSHub discovery breadth | self-hosted RSSHub (`diygod/rsshub` Docker) | Core source type `RSSHUB` already supported | Docs + source-pack data |
| HTML fetch + article extraction | `trafilatura` | Optional `article` extra (`collectors/article.py`) | Thin collector |
| Sitemap discovery | `trafilatura.sitemaps` | Same optional `article` extra | Thin collector |

**Why trafilatura for both HTML and sitemap:**
- Top-ranked in independent main-content-extraction benchmarks; actively maintained.
- Already integrated behind the optional `article` extra with a working fail-closed import (`trafilatura is None` → skipped).
- Ships `trafilatura.sitemaps` (sitemap + feed URL discovery), so one library covers two Phase-1 capabilities.

**Rejected alternative — `ultimate-sitemap-parser` (USP):** has an active **high-severity advisory (AIKIDO-2026-326865)**: parses untrusted remote XML via Expat without blocking DTDs / entity expansion → XXE / XML-bomb CPU+memory exhaustion. Unacceptable for a collector that fetches remote sitemaps. Using `trafilatura.sitemaps` sidesteps this entirely.

**License note:** `trafilatura` is GPL-3.0+. It stays an **optional** extra (not promoted to core deps), so the MIT-licensed core is unaffected. HTML/sitemap collectors require the `article` extra and fail closed without it. This matches the existing article-enrichment pattern.

## 5. Architecture

### 5.1 New source types

Add to `SourceType` (`src/fashion_radar/models/source.py`):

```python
class SourceType(StrEnum):
    RSS = "rss"
    RSSHUB = "rsshub"
    GDELT = "gdelt"
    HTML = "html"          # new
    SITEMAP = "sitemap"    # new
    MANUAL_IMPORT = "manual_import"
```

### 5.2 SourceDefinition changes

Add an optional seed-URL list and extend the target validator (`src/fashion_radar/models/source.py`):

```python
class SourceDefinition(BaseModel):
    ...
    url: str | None = None
    seed_urls: list[str] = Field(default_factory=list)   # new
    ...

    @model_validator(mode="after")
    def validate_source_target(self) -> SourceDefinition:
        ...
        if self.type == SourceType.HTML and not (self.url or self.seed_urls):
            raise ValueError("html source requires url or seed_urls")
        if self.type == SourceType.SITEMAP and not self.url:
            raise ValueError("sitemap source requires url (sitemap.xml or site root)")
        return self
```

- HTML source: effective seed list = `seed_urls` if non-empty else `[url]`.
- Sitemap source: `url` is the sitemap XML URL or a site root (trafilatura discovers `/sitemap.xml`).
- `HttpSourceSettings` (user_agent, timeout, `per_domain_delay_seconds`, retries, backoff) and `ArticleSourceSettings` (enabled, `respect_robots_txt`, `max_summary_chars`, `paywalled_domains`) are reused unchanged for politeness and extraction control.

### 5.3 New collectors

Two new modules under `src/fashion_radar/collectors/`, each implementing the existing `Collector` protocol (`collect(source, *, started_at) -> CollectorResult`):

- `html.py` → `HtmlCollector`
- `sitemap.py` → `SitemapCollector`

Both are registered in `_default_collectors()` (`src/fashion_radar/workflows.py`) by `SourceType`:

```python
def _default_collectors() -> dict[SourceType, object]:
    return {
        SourceType.RSS: RssCollector(),
        SourceType.RSSHUB: RssCollector(),
        SourceType.GDELT: GdeltCollector(),
        SourceType.HTML: HtmlCollector(),        # new
        SourceType.SITEMAP: SitemapCollector(),  # new
    }
```

### 5.4 Data flow

**HtmlCollector** (per seed URL):
1. Resolve effective seed list (`seed_urls or [url]`).
2. For each seed URL: reuse the new `collectors.article.extract_article_with_metadata(url, source=source, html_fetcher=<FashionHttpClient.get_text>, robots_checker=<RobotsPolicyChecker>)` (added in Stage 213; the older `extract_article` returns text only). It enforces `respect_robots_txt`, paywall skip, trafilatura title/date/text extraction via JSON output, and fail-closed (`extractor_unavailable`).
3. Map each successful `ArticleExtractionResult` to a `CollectedItem` (`source_name=source.name`, `url=url`, `title` from trafilatura metadata or a URL-derived fallback, `summary=text` already capped by `max_summary_chars`, `published_at` from trafilatura date metadata or fall back to run `started_at`).
4. Return `CollectorResult.success(source, items=..., items_seen=len(seeds))`. Skipped seeds (robots/paywall/no-text/extractor-unavailable) are counted in `items_seen` but not stored, and are reflected via the runner's existing run/health recording.

**SitemapCollector**:
1. `trafilatura.sitemaps.sitemap_search(source.url)` → discovered article URLs (optionally filtered by `lastmod` recency and a configurable URL regex; defaults: no filter, bounded max URLs per run).
2. For each discovered URL, reuse the **same** fetch+extract path as `HtmlCollector` (extract a shared helper, e.g. `_extract_url_to_item`, to avoid duplication).
3. Return `CollectorResult.success(...)`.

Both collectors rely on the existing `collect_sources` runner (`src/fashion_radar/collectors/runner.py`) for: enabled/unhealthy skip, health circuit-breaker (`record_success`/`record_failure`), `collector_runs` + `source_health` recording, and item upsert via `ItemRepository.upsert_item`. **No runner changes required** beyond registering the new collectors — except one interaction: the runner currently re-runs article enrichment on returned items when `source.article.enabled`. For HTML/SITEMAP the collector already returns extracted text, so enrichment must be skipped for these types (the plan pins the exact guard, e.g. skip enrichment when `source.type in {HTML, SITEMAP}`).

### 5.5 Storage & dedup

Reuse the existing `items` table verbatim:
- `source_type` ∈ `{"html", "sitemap"}`.
- `platform` left unset (web; not a social provenance label).
- `source_weight` from `source.weight`.
- Dedup via the existing `normalized_url` unique constraint (no schema migration, no `SCHEMA_VERSION` bump).

## 6. Error Handling & Politeness

- **Robots:** enforced by the reused `extract_article_with_metadata` path (`ArticleSourceSettings.respect_robots_txt`, default true). Disallowed URLs are skipped with a recorded reason, not stored.
- **Rate limiting:** per-domain delay via existing `HttpSourceSettings.per_domain_delay_seconds` (default 1.0s), enforced by `FashionHttpClient`.
- **Paywalls:** existing `paywalled_domains` skip reused.
- **Partial failure:** per-URL exceptions are swallowed into "skipped" reasons; a collector run succeeds if at least the run completed (mirrors RSS collector behavior). Run-level exceptions → `CollectorResult.failed`.
- **Optional-extra fail-closed:** if `trafilatura` is not installed, an HTML/SITEMAP collector detects this once before iterating seeds and returns `CollectorResult.skipped(source, reason="extractor_unavailable")` (the same run-level skip path used for disabled/unhealthy sources), so the missing-extra state is surfaced honestly in `collector_runs`. The core CLI still works without the extra; only HTML/SITEMAP sources skip.
- **Sitemap safety:** `trafilatura.sitemaps` is used instead of raw Expat over untrusted XML (avoids the USP XXE class of bug). A max-URLs-per-run bound prevents runaway discovery.

## 7. Configuration Examples

```yaml
# HTML page collector — a brand newsroom page with no feed
- name: "Brand X Newsroom"
  type: html
  url: "https://brandx.com/news"
  weight: 1.0
  article: { enabled: true, respect_robots_txt: true, max_summary_chars: 500 }

# HTML collector with multiple seed pages
- name: "Designer Y Press"
  type: html
  seed_urls:
    - "https://designery.com/press"
    - "https://designery.com/collections"
  weight: 1.2

# Sitemap discovery collector — large news site
- name: "Fashion News Daily"
  type: sitemap
  url: "https://fashionnewsdaily.com/sitemap.xml"
  weight: 1.0
```

RSS/RSSHub expansion is data-only: new entries in `configs/source-packs/*.yaml` plus a docs section on self-hosting RSSHub (Docker) for sites without native feeds.

## 8. Documentation & Test Impact (Phase 1 scope only)

**Docs to update (additive; social ban untouched):**
- `docs/source-boundaries.md` — add HTML and sitemap as allowed, robots-respecting core acquisition; keep the social-platform ban and the "Robots And Fetching" etiquette rules.
- `docs/architecture.md` — document `HtmlCollector` / `SitemapCollector` and the new `SourceType` values.
- `docs/cli-reference.md`, `README.md` — note HTML/sitemap source types and the optional `article` extra requirement.
- `docs/source-packs.md` — HTML/sitemap source examples + self-hosted RSSHub guidance.

**Review protocol docs (project-owner iron rules):**
- `docs/REVIEW_PROTOCOL.md` and `AGENTS.md` — replace the opencode-primary review flow with: **plan → local Claude Code review (`claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash`) → opencode revision (`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`) → implement (TDD) → Claude Code code review → next phase**. Fallback: if Claude Code is unavailable, an independent opencode agent (`glm-5.2 --variant max`) reviews.

**Tests:**
- New `tests/test_collectors_html.py`, `tests/test_collectors_sitemap.py` (TDD: RED first) covering success, robots-skip, paywall-skip, no-text-skip, extractor-unavailable fail-closed, seed_urls resolution, sitemap URL filtering, dedup via normalized_url, and runner integration (health recording, enrichment-skip for HTML/SITEMAP).
- Update `tests/test_config.py` / source-config tests for the new `SourceType` values and `seed_urls` validator.
- Update/add docs-guard tests (`tests/test_source_boundaries_docs.py`, `tests/test_cli_docs.py`, etc.) to match new wording.
- Existing release-hygiene and first-run-smoke scripts: confirm HTML/SITEMAP sources work end-to-end in the smoke fixture (likely add a tiny HTML source to the sample).

## 9. Implementation Staging (sub-stages within Phase 1)

Each sub-stage is its own plan → Claude Code review → opencode revision → implement → Claude Code code review cycle:

1. **1a — Review-protocol docs update** (iron rules into `REVIEW_PROTOCOL.md` + `AGENTS.md`). Prerequisite for all later review gates.
2. **1b — Source model + plumbing**: `SourceType.HTML`/`SITEMAP`, `seed_urls`, validator, register no-op collectors, runner enrichment-skip guard. (Collectors can return empty until 1c/1d.)
3. **1c — HtmlCollector** + tests + docs.
4. **1d — SitemapCollector** + tests + docs (reuses 1c helper).
5. **1e — RSS/RSSHub expansion**: source-pack data + RSSHub self-host docs + docs-guard tests.
6. **1f — Phase 1 release verification** (full gate) + release review, then commit/push.

## 10. Open Questions (to resolve in the plan, not now)

- Exact `trafilatura.sitemaps` API surface + version pin (pin in the `article` extra).
- Sitemap default max-URLs-per-run bound and whether `lastmod` recency filtering is configurable per source or global.
- Whether to expose a URL-regex include filter on sitemap sources (default off).
- CollectedItem published_at fallback when trafilatura reports no date.
- Whether HTML/SITEMAP sources belong in the public source pack or a separate "web" pack.

## 11. Verification (per sub-stage and at Phase 1 release)

Focused tests during dev; at sub-stage release at least:
```
uv --no-config run --frozen pytest tests/test_collectors_html.py tests/test_collectors_sitemap.py tests/test_config.py
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
```
At Phase 1 final release, the full gate:
```
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```
`pyproject.toml`/`uv.lock` change only if the `article` extra version pin is touched (trafilatura is already declared); otherwise no dependency change.
