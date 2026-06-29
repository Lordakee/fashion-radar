# Stage 213 HtmlCollector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Stage 212 no-op `HtmlCollector` stub with real seed-URL fetch + trafilatura extraction that produces `CollectedItem`s with title, summary, and published_at, reusing the existing robots/paywall/fail-closed discipline via a new additive `extract_article_with_metadata` helper.

**Architecture:** `src/fashion_radar/collectors/article.py` gains (additively, without changing `extract_article`) a `published_at` field on `ArticleExtractionResult`, an `extractor_available()` predicate, and `extract_article_with_metadata(url, *, source, html_fetcher, robots_checker)`, which uses `trafilatura.extract(html, output_format="json")` to capture title + date + text in one pass. `src/fashion_radar/collectors/html.py` `HtmlCollector.collect` builds one `FashionHttpClient` + `RobotsPolicyChecker` per run, resolves effective seeds (`seed_urls or [url]`), returns `CollectorResult.skipped(reason="extractor_unavailable")` up front when the optional `article` extra is absent, and otherwise maps each non-skipped `ArticleExtractionResult` to a `CollectedItem`. The runner integration (enrichment-skip guard + default registration) is already in place from Stage 212.

**Tech Stack:** Python 3.11, Pydantic, httpx, trafilatura (optional `article` extra, GPL-3.0+, kept optional), robotexclusionrulesparser, pytest, `uv --no-config run --frozen`, Claude Code + opencode (`glm-5.2 --variant max`) review.

## Core product gap closed

Sites that publish via plain HTML pages (brand newsrooms, fashion media without feeds) become first-class sources. This is the first half of the web-acquisition gap (sitemap discovery closes the other half in Stage 214).

## Scope

**In scope:**
- `ArticleExtractionResult`: add `published_at: str | None = None`.
- `article.py`: add `extractor_available()` and `extract_article_with_metadata(...)`. Leave `extract_article` unchanged.
- `html.py`: real `HtmlCollector` (seed resolution, per-run client/robots, fail-closed skipped on missing extra, CollectedItem mapping with title/published_at fallbacks).
- Tests: `tests/test_collectors_html.py` expanded; new metadata-extraction coverage in `tests/test_collectors_article.py`.
- Docs: `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `README.md`, `docs/source-packs.md` add the `html` source type (robots-respecting, optional `article` extra). Docs-guard tests updated.
- CHANGELOG entry (this stage ships user-facing capability).

**Out of scope:** sitemap discovery (214), RSS/RSSHub expansion (215), any change to `extract_article` behavior or RSS enrichment, DB schema, dependencies (trafilatura already declared), matching/scoring/reporting/dashboard, social platforms (Phase 2+), login/cookie model.

## File Map

- Modify `src/fashion_radar/collectors/article.py` — add field + 2 functions.
- Modify `src/fashion_radar/collectors/html.py` — replace no-op stub with real collector.
- Modify `tests/test_collectors_article.py` — add `extract_article_with_metadata` + `extractor_available` tests.
- Modify `tests/test_collectors_html.py` — real-behavior tests.
- Modify `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `README.md`, `docs/source-packs.md`.
- Modify docs-guard tests as needed (`tests/test_source_boundaries_docs.py`, `tests/test_cli_docs.py`).
- Modify `CHANGELOG.md`.
- Add review artifacts under `docs/reviews/`.

No `pyproject.toml` / `uv.lock` change.

## Key implementation contracts

`extract_article_with_metadata` (article.py) — same skip semantics as `extract_article` (disabled / paywalled_domain / extractor_unavailable / robots_disallowed|unavailable / extraction_failed / no_extractable_text) but uses JSON output:
```python
def extract_article_with_metadata(
    url: str,
    *,
    source: SourceDefinition,
    html_fetcher: HtmlFetcher,
    robots_checker: RobotsPolicyChecker,
) -> ArticleExtractionResult:
    if not source.article.enabled:
        return _skipped(url, "disabled")
    if _is_paywalled_domain(url, source.article.paywalled_domains):
        return _skipped(url, "paywalled_domain")
    # Kept for self-contained reuse by Stage 214 SitemapCollector; HtmlCollector gates via extractor_available() first.
    if trafilatura is None:
        return _skipped(url, "extractor_unavailable")
    if source.article.respect_robots_txt:
        check = robots_checker.check(url, source.http.user_agent)
        if not check.allowed:
            return _skipped(url, check.reason)
    try:
        html = html_fetcher(url)
        raw = trafilatura.extract(
            html, include_comments=False, include_tables=False, output_format="json"
        )
    except Exception:
        return _skipped(url, "extraction_failed")
    if not raw:
        return _skipped(url, "no_extractable_text")
    # trafilatura.extract(output_format="json") returns None when nothing is
    # extracted (handled above); the JSON string uses "date"/"title"/"text" keys.
    try:
        document = json.loads(raw)
    except (ValueError, TypeError):
        return _skipped(url, "no_extractable_text")
    text = document.get("text") or ""
    if not text.strip():
        return _skipped(url, "no_extractable_text")
    title = (document.get("title") or "").strip() or None
    date = (document.get("date") or "").strip() or None
    return ArticleExtractionResult(
        url=url,
        title=title,
        text=text[: source.article.max_summary_chars],
        published_at=date,
        skipped=False,
        reason=None,
    )


def extractor_available() -> bool:
    return trafilatura is not None
```
(`json` is imported at top of article.py; `HtmlFetcher`/`RobotsPolicyChecker`/`ArticleExtractionResult`/`_skipped`/`_is_paywalled_domain` already defined there.)

`HtmlCollector.collect` (html.py):
```python
from datetime import UTC, datetime
from urllib.parse import urlsplit

from fashion_radar.collectors.article import extract_article_with_metadata, extractor_available
from fashion_radar.collectors.base import CollectorResult
from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.utils.http import FashionHttpClient


class HtmlCollector:
    def collect(self, source, *, started_at=None):
        # Bind started_at up front so published_at can never be None: mirrors runner.py:48.
        started_at = started_at or datetime.now(tz=UTC)
        if not extractor_available():
            return CollectorResult.skipped(source, reason="extractor_unavailable", started_at=started_at)
        seeds = list(source.seed_urls) if source.seed_urls else ([source.url] if source.url else [])
        if not seeds:
            return CollectorResult.success(source, items=[], started_at=started_at)
        client = FashionHttpClient(source.http)
        robots = RobotsPolicyChecker(lambda url: client.get_response(url))
        items: list[CollectedItem] = []
        try:
            for url in seeds:
                result = extract_article_with_metadata(url, source=source, html_fetcher=client.get_text, robots_checker=robots)
                if result.skipped or not result.text:
                    continue
                items.append(CollectedItem(
                    source_name=source.name,
                    source_type=source.type,
                    url=url,
                    title=result.title or _fallback_title(url),
                    published_at=_published_at(result.published_at, started_at),
                    summary=result.text,
                ))
        finally:
            client.close()
        return CollectorResult.success(source, items=items, started_at=started_at, items_seen=len(seeds))
```
with helpers `_fallback_title(url)` (last non-empty path segment, else netloc, else "Untitled") and `_published_at(raw, started_at)` (try parse_datetime_utc(raw); on failure or falsy `raw`, fall back to `started_at`, which is always a real `datetime` because `collect` binds it via `datetime.now(tz=UTC)` at the top — so `CollectedItem.published_at` can never be `None`). Exact signatures/types to be filled in the plan with `SourceDefinition`/`datetime`/`CollectorResult` imports (note `CollectorResult.skipped` exists per `base.py:93`).

## Tasks (summary — full TDD steps in implementation)

- **Task 0 (plan review):** Claude Code reviews this plan; opencode revises per findings. Record `docs/reviews/claude-code-stage-213-plan-review.md` (+ opencode if needed).
- **Task 1 (article metadata helper, RED→GREEN):** add `published_at` field + `extract_article_with_metadata` + `extractor_available`; tests for success (title/date/text from JSON), each skip reason, and `extractor_available` reflecting the import guard.
- **Task 2 (HtmlCollector real, RED→GREEN):** replace stub; tests for success extraction (fake html_fetcher returning fixture HTML + fake robots allowing → one CollectedItem with extracted title/summary/published_at), robots-disallow skip, paywall skip, no-text skip, seed_urls precedence over url, url fallback when seed_urls empty, multiple seeds mixed skip/ok (items_seen counts all seeds), extractor-unavailable run-level `CollectorResult.skipped(reason="extractor_unavailable")` via monkeypatching `extractor_available`, **title fallback** (trafilatura JSON has no `"title"` key or empty string → `CollectedItem.title` is the `_fallback_title(url)` string, non-empty), and **published_at parse failure** (trafilatura returns an unparseable date string → `CollectedItem.published_at` equals `started_at`, no `ValidationError`).
- **Task 3 (docs + docs-guard + changelog):** add `html` source type to the 5 docs; pin wording in docs-guard; CHANGELOG `### Added`. Also update `docs/superpowers/specs/2026-06-29-phase1-web-collectors-design.md` Section 5.4 so it references `extract_article_with_metadata` (not `extract_article`) for the HtmlCollector path, matching the implementation that captures title + date + text.
- **Task 4 (focused + Claude Code code review + release verification + commit):** focused pytest, ruff, full gate (pytest, ruff, hygiene, lock, sync, smoke, git diff), `claude --effort max ...` code review, commit "Stage 213: HtmlCollector wraps trafilatura for seed-URL extraction", push.

## Verification

Focused: `uv --no-config run --frozen pytest tests/test_collectors_html.py tests/test_collectors_article.py tests/test_collectors_runner.py tests/test_source_model.py -q`. Full release gate as in Stage 212. `git diff --exit-code -- uv.lock pyproject.toml` must exit 0.

## Self-Review

- Reuses mature trafilatura + existing robots/paywall discipline; no new dependency.
- `extract_article` (RSS enrichment) untouched → zero regression risk there.
- Fail-closed preserved: missing `article` extra → run-level `skipped("extractor_unavailable")`, core CLI still works.
- CollectedItem contracts honored: title non-empty (fallback), published_at always set (fallback started_at).
- Forward-compatible with Stage 214 (SitemapCollector will reuse `extract_article_with_metadata` + the same fetch path).
