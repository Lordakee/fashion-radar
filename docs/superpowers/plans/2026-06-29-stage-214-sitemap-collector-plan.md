# Stage 214 SitemapCollector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Stage 212 no-op `SitemapCollector` stub with real sitemap discovery (`trafilatura.sitemaps.sitemap_search`) that discovers article URLs from a configured sitemap/site-root URL and extracts each via the Stage 213 `extract_article_with_metadata` path, reusing a shared `collect_html_items` helper extracted from `HtmlCollector`.

**Architecture:** `src/fashion_radar/collectors/html.py` is refactored to expose a module-level `collect_html_items(source, urls, started_at) -> list[CollectedItem]` (build one `FashionHttpClient` + `RobotsPolicyChecker`, loop URLs, call `extract_article_with_metadata`, map non-skipped results to `CollectedItem`s with `_fallback_title`/`_published_at`). `HtmlCollector.collect` becomes: bind `started_at`, fail-closed via `extractor_available()`, resolve seeds, `return CollectorResult.success(items=collect_html_items(...), items_seen=len(seeds))`. The Stage 213 `test_collectors_html.py` tests keep passing because they monkeypatch `fashion_radar.collectors.html.extract_article_with_metadata` / `extractor_available`, which `collect_html_items` still references in the `html` module namespace. `src/fashion_radar/collectors/sitemap.py` `SitemapCollector.collect` binds `started_at`, fails closed via `extractor_available()`, discovers URLs via `trafilatura.sitemaps.sitemap_search(source.url)` (try/except, bounded by `MAX_SITEMAP_URLS_PER_RUN`), then returns `CollectorResult.success(items=collect_html_items(source, discovered, started_at), items_seen=len(discovered))`.

**Tech Stack:** Python 3.11, trafilatura `sitemaps.sitemap_search` (optional `article` extra), httpx, robotexclusionrulesparser, pytest, `uv --no-config run --frozen`, Claude Code + opencode (`glm-5.2 --variant max`) review.

## Core product gap closed

Large news/official sites that publish a sitemap but no usable feed become first-class sources. Combined with Stage 213 (HTML seeds) and 215 (RSS/RSSHub), this completes Phase 1 web acquisition.

## Scope

**In scope:**
- `html.py`: extract `collect_html_items(source, urls, started_at)` (module-level); simplify `HtmlCollector.collect` to use it. Behavior identical.
- `sitemap.py`: real `SitemapCollector` using `trafilatura.sitemaps.sitemap_search` + `collect_html_items` + `extractor_available` fail-closed + `MAX_SITEMAP_URLS_PER_RUN` bound.
- Tests: `tests/test_collectors_sitemap.py` (discovery success, discovery failure → success with 0 items, discovered URLs flow into items, extractor-unavailable run-level skipped, bound cap); confirm `tests/test_collectors_html.py` (213) still green after the refactor.
- Docs: `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `README.md` add the `sitemap` source type; docs-guard.
- CHANGELOG `### Added`.

**Out of scope:** RSS/RSSHub expansion data (215), any change to `extract_article`/`extract_article_with_metadata` semantics, DB schema, dependencies, matching/scoring/reporting/dashboard, social platforms (Phase 2+).

## File Map

- Modify `src/fashion_radar/collectors/html.py` — extract `collect_html_items`; simplify `HtmlCollector.collect`.
- Modify `src/fashion_radar/collectors/sitemap.py` — real collector.
- Add/expand `tests/test_collectors_sitemap.py`.
- Modify `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `README.md`.
- Modify `tests/test_source_boundaries_docs.py` (add sitemap guard).
- Modify `CHANGELOG.md`.
- Add review artifacts.

No `pyproject.toml` / `uv.lock` change.

## Key implementation contracts

`collect_html_items` (html.py, module-level — moved out of `HtmlCollector.collect`):
```python
def collect_html_items(
    source: SourceDefinition,
    urls: list[str],
    started_at: datetime,
) -> list[CollectedItem]:
    if not urls:
        return []
    client = FashionHttpClient(source.http)
    robots = RobotsPolicyChecker(lambda url: client.get_response(url))
    items: list[CollectedItem] = []
    try:
        for url in urls:
            result = extract_article_with_metadata(
                url, source=source, html_fetcher=client.get_text, robots_checker=robots,
            )
            if result.skipped or not result.text:
                continue
            items.append(CollectedItem(
                source_name=source.name, source_type=source.type, url=url,
                title=result.title or _fallback_title(url),
                published_at=_published_at(result.published_at, started_at),
                summary=result.text,
            ))
    finally:
        client.close()
    return items
```
`HtmlCollector.collect` becomes:
```python
    def collect(self, source, *, started_at=None):
        started_at = started_at or datetime.now(tz=UTC)
        if not extractor_available():
            return CollectorResult.skipped(source, reason="extractor_unavailable", started_at=started_at)
        seeds = list(source.seed_urls) if source.seed_urls else ([source.url] if source.url else [])
        items = collect_html_items(source, seeds, started_at)
        return CollectorResult.success(source, items=items, started_at=started_at, items_seen=len(seeds))
```

`SitemapCollector.collect` (sitemap.py):
```python
from __future__ import annotations
from datetime import UTC, datetime
try:
    import trafilatura
    import trafilatura.sitemaps  # ensure submodule is loaded
except ImportError:
    trafilatura = None  # type: ignore[assignment]
from fashion_radar.collectors.article import extractor_available
from fashion_radar.collectors.base import CollectorResult
from fashion_radar.collectors.html import collect_html_items
from fashion_radar.models.source import SourceDefinition

MAX_SITEMAP_URLS_PER_RUN = 50


class SitemapCollector:
    def collect(self, source: SourceDefinition, *, started_at: datetime | None = None) -> CollectorResult:
        started_at = started_at or datetime.now(tz=UTC)
        if not extractor_available():
            return CollectorResult.skipped(source, reason="extractor_unavailable", started_at=started_at)
        discovered = _discover_sitemap_urls(source.url)
        bounded = discovered[:MAX_SITEMAP_URLS_PER_RUN]
        items = collect_html_items(source, bounded, started_at)
        return CollectorResult.success(source, items=items, started_at=started_at, items_seen=len(bounded))


def _discover_sitemap_urls(target: str | None) -> list[str]:
    if not target:
        return []
    try:
        raw = trafilatura.sitemaps.sitemap_search(target)
    except Exception:
        return []
    return [str(url) for url in raw]
```

## Tasks (summary)

- **Task 0 (plan review):** Claude Code reviews; opencode revises. Record `docs/reviews/claude-code-stage-214-plan-review.md`.
- **Task 1 (refactor html.py, RED-preserve → GREEN):** extract `collect_html_items`; confirm `tests/test_collectors_html.py` still green (these are the regression guard for the refactor).
- **Task 2 (SitemapCollector, RED → GREEN):** replace stub; sitemap.py import block must `import trafilatura.sitemaps` explicitly (submodule auto-load via `import trafilatura` is not guaranteed in production, and mocking `fashion_radar.collectors.sitemap.trafilatura` masks the gap); tests for discovery success (fake `sitemap_search` returns URLs + fake extraction → items), discovery failure (sitemap_search raises → success 0 items), extractor-unavailable skipped, bound cap (`MAX_SITEMAP_URLS_PER_RUN`), discovered URLs passed through to items, and `test_sitemap_collector_with_none_url_returns_empty_success` (documents the `_discover_sitemap_urls(str | None)` contract, returns empty success).
- **Task 3 (docs + docs-guard + changelog):** add `sitemap` source type to the 4 docs; guard; CHANGELOG `### Added`.
- **Task 4 (focused + Claude Code code review + release verification + commit):** focused pytest, ruff, full gate, `claude --effort max ...` code review, commit "Stage 214: SitemapCollector discovers URLs via trafilatura sitemaps", push.

## Verification

Focused: `uv --no-config run --frozen pytest tests/test_collectors_sitemap.py tests/test_collectors_html.py tests/test_collectors_article.py tests/test_collectors_runner.py tests/test_source_boundaries_docs.py -q`. Full gate as in Stage 213. `git diff --exit-code -- uv.lock pyproject.toml` must exit 0.

## Self-Review

- Reuses the mature 213 extraction path; no new dependency; `extract_article` untouched.
- Refactor preserves HtmlCollector observable behavior (213 tests stay green) because `collect_html_items` still references `extract_article_with_metadata`/`extractor_available` in the `html` module namespace (the existing monkeypatch targets).
- Fail-closed preserved at run level for sitemap too.
- Discovery bounded + exception-safe (no crash on bad sitemap).
- `trafilatura.sitemaps.sitemap_search` is the documented discovery API; tests fake it since the `article` extra is not installed in the base env.
