from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorResult, CollectorRunStatus
from fashion_radar.collectors.runner import collect_sources
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType


class FailingCollector:
    def collect(self, source: SourceDefinition) -> CollectorResult:
        raise RuntimeError("feed timeout")


class SuccessfulCollector:
    def collect(self, source: SourceDefinition) -> CollectorResult:
        item = CollectedItem(
            source_name=source.name,
            source_type=source.type,
            url="https://example.com/story",
            title="The Row Margaux handbag gains momentum",
            published_at="2026-06-11T10:00:00Z",
            summary="Short attributed signal.",
        )
        return CollectorResult.success(
            source,
            items=[item],
            started_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
            finished_at=datetime(2026, 6, 11, 10, 1, tzinfo=UTC),
            items_seen=1,
        )


def _rss_source(name: str, **overrides: object) -> SourceDefinition:
    return SourceDefinition(
        name=name,
        type=SourceType.RSS,
        url=f"https://example.com/{name}.xml",
        **overrides,
    )


def test_collect_sources_records_failure_and_continues_to_next_source(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    sources = [
        _rss_source("Failing Feed", health={"max_failures": 2, "retention_hours": 24}),
        _rss_source("Working Feed"),
    ]

    results = collect_sources(
        sources,
        engine=engine,
        collectors={
            "Failing Feed": FailingCollector(),
            "Working Feed": SuccessfulCollector(),
        },
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert [result.status.status for result in results] == [
        CollectorRunStatus.FAILED,
        CollectorRunStatus.SUCCESS,
    ]
    assert ItemRepository(engine).count_items() == 1
    runs = CollectorRunRepository(engine).list_recent_runs()
    assert [run["status"] for run in runs] == ["success", "failed"]
    assert SourceHealthRepository(engine).get_health(sources[0])["consecutive_failures"] == 1


def test_collect_sources_skips_unhealthy_source_until_retention_expires(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    source = _rss_source("Failing Feed", health={"max_failures": 1, "retention_hours": 24})
    health_repository = SourceHealthRepository(engine)
    health_repository.record_failure(
        source,
        error_message="timeout",
        occurred_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
        max_failures=1,
        retention_hours=24,
    )

    results = collect_sources(
        [source],
        engine=engine,
        collectors={"Failing Feed": FailingCollector()},
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert len(results) == 1
    assert results[0].status.status == CollectorRunStatus.SKIPPED
    assert results[0].status.error_message == "source unhealthy"
    assert CollectorRunRepository(engine).list_recent_runs()[0]["status"] == "skipped"
