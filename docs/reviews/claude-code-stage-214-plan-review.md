# Stage 214Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical
*(none)*

## Important

**`trafilatura.sitemaps` submodule may not be auto-accessible via `import trafilatura`**

The plan's `sitemap.py` does:
```python
try:
    import trafilatura
except ImportError:
    trafilatura = None
...
raw = trafilatura.sitemaps.sitemap_search(target)
```

In Python, `import trafilatura` only makes `trafilatura.sitemaps` accessible via attribute access if trafilatura's `__init__.py` explicitly imports it. If it doesn't, `trafilatura.sitemaps` raises `AttributeError`, which the `except Exception` in `_discover_sitemap_urls` silently swallows → returns `[]` → collector runs successfully with zero items, feature is dead in production, tests pass (they mock `fashion_radar.collectors.sitemap.trafilatura` with a MagicMock whose `.sitemaps.sitemap_search` attribute works fine).

Fix: be explicit in the import block:
```python
try:
    import trafilatura
    import trafilatura.sitemaps  # ensure submodule is loaded
except ImportError:
    trafilatura = None
```
Then `trafilatura.sitemaps.sitemap_search(target)` is safe. No test or mock changes required.

## Nits

1. **Redundant `trafilatura is None` guard in `_discover_sitemap_urls`:** `SitemapCollector.collect` already gates on `extractor_available()` before calling `_discover_sitemap_urls`, so `trafilatura` is guaranteed non-None at that point. The inner check is dead code. Harmless, but clutters the contract. Either remove it or make `_discover_sitemap_urls` a private method that asserts its precondition via a comment.

2. **Empty seeds path creates unused HTTP client in refactored `HtmlCollector`:** Post-refactor, `HtmlCollector.collect` with no seeds calls `collect_html_items(source, [], started_at)`, which allocates and immediately closes a `FashionHttpClient` + `RobotsPolicyChecker`. The existing code short-circuits with an early return. A simple `if not urls: return []` guard at the top of `collect_html_items` restores the short-circuit and keeps it clean.

3. **Missing `source.url = None` test for `SitemapCollector`:** The model validator guards against it at config time, so it's not a reachable path from valid sources. But since `_discover_sitemap_urls` explicitly accepts `str | None`, a single `test_sitemap_collector_with_none_url_returns_empty_success` would document the contract and protect against a future validator relaxation.

## Résumé

Architecture is sound. Monkeypatching safety is confirmed: `collect_html_items` references `extract_article_with_metadata` and `extractor_available` in the `html` module namespace, so existing `fashion_radar.collectors.html.*` patches continue to intercept them after the refactor — all213 html tests stay valid regression guards. The sitemap mocking strategy (patch `sitemap.trafilatura`, `html.extract_article_with_metadata`, `sitemap.extractor_available`) correctly isolates `SitemapCollector` from the network. Fail-closed, bound, and exception-safe discovery all match `CollectorResult` contracts. The one Important item (explicit `import trafilatura.sitemaps`) is a one-line fix before Task 2.
