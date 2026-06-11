from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import HttpSourceSettings, SourceDefinition, SourceType
from fashion_radar.utils.http import FashionHttpClient

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


class GdeltCollector:
    def __init__(self, http_client: Any | None = None) -> None:
        self._http_client = http_client

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> CollectorResult:
        if source.type != SourceType.GDELT:
            raise ValueError("GdeltCollector requires a gdelt source")
        if source.query is None:
            raise ValueError("GDELT source requires query")

        client = self._http_client or FashionHttpClient(gdelt_http_settings(source))
        close_client = self._http_client is None
        try:
            payload = client.get_json(GDELT_DOC_API, params=_gdelt_params(source))
        finally:
            if close_client:
                client.close()

        articles = payload.get("articles", []) if isinstance(payload, dict) else []
        fallback_time = finished_at or datetime.now(tz=UTC)
        items = [
            item
            for article in articles
            if isinstance(article, dict)
            if (item := _article_to_item(source, article, fallback_time)) is not None
        ]
        return CollectorResult.success(
            source,
            items=items,
            started_at=started_at,
            finished_at=finished_at,
            items_seen=len(articles),
        )


def gdelt_http_settings(source: SourceDefinition) -> HttpSourceSettings:
    min_delay = 1.0 / source.gdelt.rate_limit_per_second
    return source.http.model_copy(
        update={
            "per_domain_delay_seconds": max(source.http.per_domain_delay_seconds, min_delay),
        }
    )


def _gdelt_params(source: SourceDefinition) -> dict[str, str | int]:
    return {
        "query": source.query or "",
        "mode": "artlist",
        "format": "json",
        "timespan": f"{source.gdelt.lookback_hours}h",
        "maxrecords": source.gdelt.max_records,
    }


def _article_to_item(
    source: SourceDefinition,
    article: dict[str, Any],
    fallback_time: datetime,
) -> CollectedItem | None:
    title = _string(article.get("title"))
    url = _string(article.get("url"))
    if not title or not url:
        return None
    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=url,
        title=title,
        published_at=_gdelt_datetime(article.get("seendate"), fallback_time),
        summary=_string(article.get("snippet") or article.get("description")),
    )


def _gdelt_datetime(value: object, fallback_time: datetime) -> datetime:
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        except ValueError:
            return fallback_time
    return fallback_time


def _string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
