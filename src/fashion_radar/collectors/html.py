from __future__ import annotations

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
    """Collector for ``html`` sources.

    Fetches configured seed URLs and extracts main article text plus title and
    publication date via trafilatura (through ``extract_article_with_metadata``),
    respecting robots.txt and configured paywalled-domain skips. Requires the
    optional ``article`` extra; when trafilatura is unavailable the run is
    recorded as skipped with reason ``extractor_unavailable`` so the core CLI
    still works without the extra.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        # Bind started_at up front so published_at can never be None (mirrors runner.py).
        started_at = started_at or datetime.now(tz=UTC)
        if not extractor_available():
            return CollectorResult.skipped(
                source, reason="extractor_unavailable", started_at=started_at
            )
        seeds = list(source.seed_urls) if source.seed_urls else ([source.url] if source.url else [])
        if not seeds:
            return CollectorResult.success(source, items=[], started_at=started_at)
        client = FashionHttpClient(source.http)
        robots = RobotsPolicyChecker(lambda url: client.get_response(url))
        items: list[CollectedItem] = []
        try:
            for url in seeds:
                result = extract_article_with_metadata(
                    url,
                    source=source,
                    html_fetcher=client.get_text,
                    robots_checker=robots,
                )
                if result.skipped or not result.text:
                    continue
                items.append(
                    CollectedItem(
                        source_name=source.name,
                        source_type=source.type,
                        url=url,
                        title=result.title or _fallback_title(url),
                        published_at=_published_at(result.published_at, started_at),
                        summary=result.text,
                    )
                )
        finally:
            client.close()
        return CollectorResult.success(
            source, items=items, started_at=started_at, items_seen=len(seeds)
        )


def _fallback_title(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path.rstrip("/")
    if path:
        last = path.rsplit("/", 1)[-1]
        if last:
            return last
    return parsed.netloc or "Untitled"


def _published_at(raw: str | None, fallback: datetime) -> datetime:
    if raw:
        try:
            return parse_datetime_utc(raw)
        except Exception:
            return fallback
    return fallback
