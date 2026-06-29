from __future__ import annotations

from datetime import UTC, datetime

try:
    import trafilatura
    import trafilatura.sitemaps  # ensure submodule is loaded in production
except ImportError:  # pragma: no cover - optional extra
    trafilatura = None  # type: ignore[assignment]

from fashion_radar.collectors.article import extractor_available
from fashion_radar.collectors.base import CollectorResult
from fashion_radar.collectors.html import collect_html_items
from fashion_radar.models.source import SourceDefinition

MAX_SITEMAP_URLS_PER_RUN = 50


class SitemapCollector:
    """Collector for ``sitemap`` sources.

    Discovers article URLs from a configured sitemap or site-root URL via
    ``trafilatura.sitemaps.sitemap_search``, then extracts each via the shared
    html extraction path (``collect_html_items``). Requires the optional
    ``article`` extra; when trafilatura is unavailable the run is recorded as
    skipped with reason ``extractor_unavailable``.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        started_at = started_at or datetime.now(tz=UTC)
        if not extractor_available():
            return CollectorResult.skipped(
                source, reason="extractor_unavailable", started_at=started_at
            )
        discovered = _discover_sitemap_urls(source.url)
        bounded = discovered[:MAX_SITEMAP_URLS_PER_RUN]
        items = collect_html_items(source, bounded, started_at)
        return CollectorResult.success(
            source, items=items, started_at=started_at, items_seen=len(bounded)
        )


def _discover_sitemap_urls(target: str | None) -> list[str]:
    if not target:
        return []
    try:
        raw = trafilatura.sitemaps.sitemap_search(target)
    except Exception:
        return []
    if raw is None:
        return []
    return [str(url) for url in raw]
