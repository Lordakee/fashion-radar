# Stage 214 Code Review
**Verdict:** APPROVE_WITH_NITS

## Critical
*(none)*

## Important

**`_discover_sitemap_urls`: list comprehension is outside the `try` block**

```python
try:
    raw = trafilatura.sitemaps.sitemap_search(target)
except Exception:
    return []
return [str(url) for url in raw]# ← outside try
```

If `sitemap_search` returns `None` instead of raising (unusual but not contractually excluded), `for url in raw` raises `TypeError` that escapes `_discover_sitemap_urls` and propagates through `collect()` uncaught. The fix is trivial — move the comprehension inside the `try` or add `or []`:

```python
    raw = trafilatura.sitemaps.sitemap_search(target) or []
```

or guard with `if raw is None: return []`. In practice trafilatura returns a list, so this hasn't fired, but the current tests mock the return value and would never catch it.

## Nits

**Empty-seeds behavioral delta in `HtmlCollector.collect`**
The old path returned `CollectorResult.success(…, items=[])` without `items_seen` when seeds was empty; the new path passes `items_seen=len(seeds)` (i.e. `items_seen=0`) explicitly. Functionally identical assuming the default is0, but it's a silent contract change worth noting if `CollectorResult` ever distinguishes `None` from `0`.

**Removed explanatory comment**
`# Bind started_at up front so published_at can never be None (mirrors runner.py).` was dropped from `HtmlCollector.collect`. That sentence captured a non-obvious invariant; worth re-adding as a one-liner above the `collect_html_items` docstring or at the `started_at` binding site in `SitemapCollector.collect` too.

## Résumé

The refactor is clean and well-scoped. `collect_html_items` is correctly extracted with the `if not urls: return []` short-circuit, `HtmlCollector.collect` preserves all Stage 213 behaviour, and `SitemapCollector` follows the same `started_at`/`extractor_available`/`_discover`/`bounded`/`collect_html_items` pattern faithfully. All five test scenarios (happy path, discovery failure, extractor-unavailable, cap enforcement, None-target) are present and correct. Docs and CHANGELOG are accurate. The one actionable item is the None-return edge case on `sitemap_search`; fix it before merge.
