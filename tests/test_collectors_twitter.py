from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.twitter import TwitterCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def test_twitter_collector_no_op_returns_success_with_no_items() -> None:
    source = SourceDefinition(name="X", type=SourceType.TWITTER, query="therow")
    started_at = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = TwitterCollector().collect(source, started_at=started_at)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.source_type == SourceType.TWITTER
    assert result.items == []
