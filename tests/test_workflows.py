from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.sitemap import SitemapCollector
from fashion_radar.collectors.xiaohongshu import XiaohongshuCollector
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.settings import ScoringSettings
from fashion_radar.workflows import (
    _default_collectors,
    clean_old_data,
    collect_configured_sources,
    default_database_path,
    match_stored_items,
    write_daily_report_files,
)


class FakeCollector:
    def collect(self, source: SourceDefinition, *, started_at: datetime):
        from fashion_radar.collectors.base import CollectorResult

        return CollectorResult.success(
            source,
            items=[
                CollectedItem(
                    source_name=source.name,
                    source_type=source.type,
                    url="https://example.com/story",
                    title="The Row Margaux handbag gains momentum",
                    published_at="2026-06-11T10:00:00Z",
                    summary="The Row handbag coverage.",
                )
            ],
            started_at=started_at,
            finished_at=started_at,
            items_seen=1,
        )


def _store_item(data_dir: Path) -> int:
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    return ItemRepository(engine).upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/the-row",
            title="The Row Margaux handbag gains momentum",
            published_at="2026-06-11T10:00:00Z",
            summary="The Row handbag coverage.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )


def test_collect_configured_sources_uses_injected_collectors(tmp_path: Path) -> None:
    source = SourceDefinition(
        name="Fixture Feed",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        weight=1.7,
        article={"enabled": False},
    )

    results = collect_configured_sources(
        data_dir=tmp_path / "data",
        sources=[source],
        collectors={SourceType.RSS: FakeCollector()},
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    engine = create_sqlite_engine(default_database_path(tmp_path / "data"))
    stored = ItemRepository(engine).get_item(1)
    assert results[0].status.status == "success"
    assert stored["source_weight"] == 1.7
    assert stored["collected_at"] == "2026-06-11T12:00:00+00:00"


def test_collect_configured_sources_with_injected_collectors_ignores_proxy_env(
    tmp_path: Path, monkeypatch
) -> None:
    for key in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "http_proxy"):
        monkeypatch.setenv(key, "socks5h://127.0.0.1:9")

    source = SourceDefinition(
        name="Fixture Feed",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        weight=1.7,
        article={"enabled": False},
    )

    results = collect_configured_sources(
        data_dir=tmp_path / "data",
        sources=[source],
        collectors={SourceType.RSS: FakeCollector()},
        now=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    engine = create_sqlite_engine(default_database_path(tmp_path / "data"))
    stored = ItemRepository(engine).get_item(1)
    assert results[0].status.status == "success"
    assert stored["source_weight"] == 1.7
    assert stored["collected_at"] == "2026-06-11T12:00:00+00:00"


def test_manual_import_is_not_a_default_collector() -> None:
    collectors = _default_collectors()

    assert SourceType.MANUAL_IMPORT not in collectors
    assert SourceType.MANUAL_IMPORT.value not in collectors


def test_match_stored_items_matches_title_and_summary_and_updates_first_seen(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    item_id = _store_item(data_dir)
    entity = EntityDefinition(
        name="The Row",
        type=EntityType.BRAND,
        aliases=["The Row"],
        context_terms=["handbag"],
    )

    summary = match_stored_items(data_dir=data_dir, entities=[entity])

    repository = ItemRepository(create_sqlite_engine(default_database_path(data_dir)))
    assert summary.items_processed == 1
    assert summary.matches_stored == 1
    assert repository.list_item_matches(item_id)[0]["entity_name"] == "The Row"
    assert repository.get_entity_first_seen("The Row", "brand")["first_seen_at"] == (
        "2026-06-11T11:00:00+00:00"
    )


def test_write_daily_report_files_caps_stored_summaries(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/the-row-long",
            title="The Row long signal",
            published_at="2026-06-11T10:00:00Z",
            summary="Lead text. " + ("detail " * 120) + "TAIL_MARKER",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    markdown_path, json_path = write_daily_report_files(
        data_dir=data_dir,
        reports_dir=reports_dir,
        scoring=ScoringSettings(),
        as_of=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert "TAIL_MARKER" not in markdown_path.read_text(encoding="utf-8")
    assert "TAIL_MARKER" not in json_path.read_text(encoding="utf-8")


def test_clean_old_data_prunes_by_collected_at(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    old_id = repository.upsert_item(
        CollectedItem(
            source_name="Old Source",
            source_type=SourceType.RSS,
            url="https://example.com/old",
            title="Old signal",
            published_at="2026-05-01T10:00:00Z",
            summary="old",
        ),
        collected_at=datetime(2026, 5, 1, tzinfo=UTC),
    )
    repository.replace_item_matches(
        old_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    result = clean_old_data(
        data_dir=data_dir,
        as_of=datetime(2026, 6, 11, tzinfo=UTC),
        retention_days=14,
    )

    assert result.items_deleted == 1
    assert result.item_entities_deleted == 1
    assert repository.count_items() == 0


def test_default_collectors_register_html_sitemap_and_xiaohongshu() -> None:
    collectors = _default_collectors()

    assert isinstance(collectors[SourceType.HTML], HtmlCollector)
    assert isinstance(collectors[SourceType.SITEMAP], SitemapCollector)
    assert isinstance(collectors[SourceType.XIAOHONGSHU], XiaohongshuCollector)
    assert isinstance(collectors[SourceType.RSS], RssCollector)
    assert isinstance(collectors[SourceType.RSSHUB], RssCollector)
    assert isinstance(collectors[SourceType.GDELT], GdeltCollector)
