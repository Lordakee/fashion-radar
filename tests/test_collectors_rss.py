from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.source import SourceDefinition, SourceType


def test_rss_collector_parses_fixture_items() -> None:
    fixture = Path("tests/fixtures/rss/sample_feed.xml")
    source = SourceDefinition(
        name="Fixture RSS",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )
    collector = RssCollector(feed_fetcher=lambda _url: fixture.read_text(encoding="utf-8"))

    result = collector.collect(
        source,
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
        finished_at=datetime(2026, 6, 11, 12, 1, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert [item.title for item in result.items] == [
        "The Row Margaux handbag gains momentum",
        "Zendaya red carpet styling highlights archival couture",
    ]
    assert result.items[0].source_name == "Fixture RSS"
    assert result.items[0].source_type == SourceType.RSS
    assert result.items[0].published_at.isoformat() == "2026-06-11T10:00:00+00:00"
    assert result.items[0].summary == "A short signal about a handbag."


def test_rss_collector_items_use_repository_upsert_path(tmp_path) -> None:
    fixture = Path("tests/fixtures/rss/sample_feed.xml")
    source = SourceDefinition(
        name="Fixture RSS",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )
    collector = RssCollector(feed_fetcher=lambda _url: fixture.read_text(encoding="utf-8"))
    result = collector.collect(source)
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)

    first_id = repository.upsert_item(result.items[0])
    second_id = repository.upsert_item(result.items[0])

    assert second_id == first_id
    assert repository.count_items() == 1
    assert repository.get_item(first_id)["normalized_url"] == "https://example.com/articles/margaux"
