from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.sitemap import SitemapCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def test_sitemap_collector_no_op_returns_success_with_no_items() -> None:
    source = SourceDefinition(
        name="Fashion News Daily",
        type=SourceType.SITEMAP,
        url="https://fashionnewsdaily.com/sitemap.xml",
    )
    collector = SitemapCollector()
    started_at = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = collector.collect(source, started_at=started_at)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.source_name == "Fashion News Daily"
    assert result.status.source_type == SourceType.SITEMAP
    assert result.items == []
