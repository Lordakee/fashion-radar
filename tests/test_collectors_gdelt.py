import json
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.gdelt import GDELT_DOC_API, GdeltCollector, gdelt_http_settings
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.source import SourceDefinition, SourceType


class FakeHttpClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[tuple[str, dict[str, str | int]]] = []

    def get_json(self, url: str, *, params: dict[str, str | int] | None = None) -> dict:
        self.calls.append((url, params or {}))
        return self.payload


def _payload() -> dict:
    return json.loads(Path("tests/fixtures/gdelt/sample_response.json").read_text(encoding="utf-8"))


def _source() -> SourceDefinition:
    return SourceDefinition(
        name="GDELT Luxury Fashion",
        type=SourceType.GDELT,
        query='luxury fashion OR "fashion week"',
        gdelt={
            "lookback_hours": 48,
            "max_records": 75,
            "rate_limit_per_second": 0.5,
        },
        http={"per_domain_delay_seconds": 0},
    )


def test_gdelt_collector_uses_source_query_and_settings() -> None:
    http_client = FakeHttpClient(_payload())
    collector = GdeltCollector(http_client=http_client)
    source = _source()

    result = collector.collect(
        source,
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
        finished_at=datetime(2026, 6, 11, 12, 1, tzinfo=UTC),
    )

    assert http_client.calls == [
        (
            GDELT_DOC_API,
            {
                "query": 'luxury fashion OR "fashion week"',
                "mode": "artlist",
                "format": "json",
                "timespan": "48h",
                "maxrecords": 75,
            },
        )
    ]
    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert [item.title for item in result.items] == [
        "The Row Margaux becomes a luxury resale signal",
        "Miu Miu ballet flats return to street style coverage",
    ]
    assert result.items[0].source_name == "GDELT Luxury Fashion"
    assert result.items[0].source_type == SourceType.GDELT
    assert result.items[0].published_at.isoformat() == "2026-06-11T10:15:00+00:00"
    assert result.items[0].summary == "A short GDELT article-list snippet about the Margaux bag."


def test_gdelt_items_use_repository_upsert_path(tmp_path) -> None:
    result = GdeltCollector(http_client=FakeHttpClient(_payload())).collect(_source())
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)

    item_id = repository.upsert_item(result.items[0])

    assert repository.count_items() == 1
    assert (
        repository.get_item(item_id)["normalized_url"]
        == "https://example.com/gdelt/the-row-margaux"
    )


def test_gdelt_http_settings_enforce_rate_limit_delay() -> None:
    settings = gdelt_http_settings(_source())

    assert settings.per_domain_delay_seconds == 2.0
