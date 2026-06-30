from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.instagram import InstagramCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def test_instagram_collector_no_op_returns_success_with_no_items() -> None:
    source = SourceDefinition(name="IG", type=SourceType.INSTAGRAM, query="therow")
    started_at = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = InstagramCollector().collect(source, started_at=started_at)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.source_type == SourceType.INSTAGRAM
    assert result.items == []
