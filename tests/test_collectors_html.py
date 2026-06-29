from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def test_html_collector_no_op_returns_success_with_no_items() -> None:
    source = SourceDefinition(
        name="Brand X Newsroom",
        type=SourceType.HTML,
        url="https://brandx.com/news",
    )
    collector = HtmlCollector()
    started_at = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = collector.collect(source, started_at=started_at)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.source_name == "Brand X Newsroom"
    assert result.status.source_type == SourceType.HTML
    assert result.items == []
