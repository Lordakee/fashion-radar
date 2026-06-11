from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorResult, CollectorRunStatus
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType


def test_collector_result_returns_items_and_structured_status() -> None:
    source = SourceDefinition(
        name="Vogue Business",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )
    item = CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url="https://example.com/article",
        title="The Row Margaux handbag gains momentum",
        published_at="2026-06-11T10:00:00Z",
        summary="A short attributed summary.",
    )
    started_at = datetime(2026, 6, 11, 10, 0, tzinfo=UTC)
    finished_at = datetime(2026, 6, 11, 10, 1, tzinfo=UTC)

    result = CollectorResult.success(
        source,
        items=[item],
        started_at=started_at,
        finished_at=finished_at,
        items_seen=2,
    )

    assert result.items == [item]
    assert result.status.source_name == "Vogue Business"
    assert result.status.source_type == SourceType.RSS
    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert result.status.items_collected == 1
    assert result.status.started_at == started_at
    assert result.status.finished_at == finished_at
