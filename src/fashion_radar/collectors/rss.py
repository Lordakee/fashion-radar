from __future__ import annotations

import calendar
from collections.abc import Callable
from datetime import UTC, datetime
from html import unescape
from time import struct_time

import feedparser

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.utils.http import FashionHttpClient


class RssCollector:
    def __init__(self, feed_fetcher: Callable[[str], str] | None = None) -> None:
        self._feed_fetcher = feed_fetcher

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> CollectorResult:
        if source.type not in {SourceType.RSS, SourceType.RSSHUB}:
            raise ValueError("RssCollector requires an rss or rsshub source")
        if source.url is None:
            raise ValueError("RSS source requires url")

        feed_text = self._fetch(source)
        parsed = feedparser.parse(feed_text)
        fallback_time = finished_at or datetime.now(tz=UTC)
        items = [
            item
            for entry in parsed.entries
            if (item := _entry_to_item(source, entry, fallback_time)) is not None
        ]
        return CollectorResult.success(
            source,
            items=items,
            started_at=started_at,
            finished_at=finished_at,
            items_seen=len(parsed.entries),
        )

    def _fetch(self, source: SourceDefinition) -> str:
        if self._feed_fetcher is not None:
            return self._feed_fetcher(source.url or "")
        client = FashionHttpClient(source.http)
        try:
            return client.get_text(source.url or "")
        finally:
            client.close()


def _entry_to_item(
    source: SourceDefinition,
    entry: feedparser.FeedParserDict,
    fallback_time: datetime,
) -> CollectedItem | None:
    title = _text(entry.get("title"))
    url = _text(entry.get("link") or entry.get("id"))
    if not title or not url:
        return None

    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=url,
        title=title,
        published_at=_entry_datetime(entry, fallback_time),
        summary=_text(entry.get("summary") or entry.get("description")),
    )


def _entry_datetime(entry: feedparser.FeedParserDict, fallback_time: datetime) -> datetime:
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if isinstance(published, struct_time):
        return datetime.fromtimestamp(calendar.timegm(published), tz=UTC)
    return fallback_time


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = unescape(str(value)).strip()
    return text or None
