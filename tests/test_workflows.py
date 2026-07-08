from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.collectors.article import ArticleExtractionResult
from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.collectors.instagram import InstagramCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.sitemap import SitemapCollector
from fashion_radar.collectors.twitter import TwitterCollector
from fashion_radar.collectors.xiaohongshu import XiaohongshuCollector
from fashion_radar.collectors.youtube import YouTubeCollector
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
    prune_stale_daily_report_files,
    write_daily_report_files,
    write_row_one_site_files,
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


def test_write_daily_report_files_writes_html_with_recent_window_items(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    for title, source_name, url, collected_at, summary in [
        (
            "Future collected title",
            "Future Source",
            "https://example.com/future",
            datetime(2026, 6, 11, 13, 0, tzinfo=UTC),
            "Future summary.",
        ),
        (
            "Newest collected title",
            "Newest Source",
            "https://example.com/newest",
            datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
            "Lead text. " + ("detail " * 40) + "TAIL_MARKER",
        ),
        (
            "Older collected title",
            "Older Source",
            "https://example.com/older",
            datetime(2026, 6, 10, 11, 0, tzinfo=UTC),
            "Older summary.",
        ),
        (
            "Stale collected title",
            "Stale Source",
            "https://example.com/stale",
            datetime(2026, 6, 9, 11, 0, tzinfo=UTC),
            "Stale summary.",
        ),
    ]:
        repository.upsert_item(
            CollectedItem(
                source_name=source_name,
                source_type=SourceType.RSS,
                url=url,
                title=title,
                published_at=collected_at,
                summary=summary,
            ),
            collected_at=collected_at,
        )

    markdown_path, json_path = write_daily_report_files(
        data_dir=data_dir,
        reports_dir=reports_dir,
        scoring=ScoringSettings(current_window_days=2),
        as_of=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    html_path = reports_dir / "fashion-radar-2026-06-11.html"
    html = html_path.read_text(encoding="utf-8")
    assert markdown_path.name == "fashion-radar-2026-06-11.md"
    assert json_path.name == "fashion-radar-2026-06-11.json"
    assert html_path.exists()
    assert "<h2>Latest Collected News</h2>" in html
    assert "Newest collected title" in html
    assert "Older collected title" in html
    assert "Newest Source" in html
    assert "Older Source" in html
    assert "https://example.com/newest" in html
    assert html.index("Newest collected title") < html.index("Older collected title")
    assert "Future collected title" not in html
    assert "Stale collected title" not in html
    assert "TAIL_MARKER" not in html


def test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one"
    item_id = _store_item(data_dir)
    engine = create_sqlite_engine(default_database_path(data_dir))
    repository = ItemRepository(engine)
    second_item_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/the-row-ballet-flat",
            title="The Row ballet flat gains editorial traction",
            published_at="2026-06-11T09:30:00Z",
            summary="The Row ballet flat coverage.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 5, tzinfo=UTC),
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
    repository.replace_item_matches(
        second_item_id,
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
    stored_before = repository.get_item(item_id)
    matches_before = repository.list_item_matches(item_id)
    second_stored_before = repository.get_item(second_item_id)
    second_matches_before = repository.list_item_matches(second_item_id)
    item_count_before = repository.count_items()
    source = SourceDefinition(
        name="Vogue Business",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        article={"enabled": False},
        row_one_article={"enabled": True, "max_chars": 200},
    )

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="The Row local source article",
            text="Local article paragraph for the ROW ONE detail page.",
            skipped=False,
        )

    write_row_one_site_files(
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        scoring=ScoringSettings(),
        as_of=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
        sources=[source],
        local_article_extractor=extractor,
    )

    articles_dir = output_dir / "articles"
    assert not (output_dir / "saved-signal-index.html").exists()
    assert not (articles_dir / "saved-signal-index.html").exists()
    if articles_dir.exists():
        article_sidecar_stems = {
            path.stem for path in (output_dir / "data" / "articles").glob("*.json")
        }
        allowed_article_pages = {"index.html"} | {
            f"{story_id}.html" for story_id in article_sidecar_stems
        }
        assert {path.name for path in articles_dir.iterdir()} <= allowed_article_pages

    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    detail_pages = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted((output_dir / "details").glob("*.html"))
    }
    detail_html = next(
        html
        for html in detail_pages.values()
        if "Local article paragraph for the ROW ONE detail page." in html
    )
    article_pages = [
        path for path in (output_dir / "articles").glob("*.html") if path.name != "index.html"
    ]
    assert article_pages
    article_html = article_pages[0].read_text(encoding="utf-8")
    assert 'class="local-article-paragraph-context"' in article_html
    assert 'id="local-article-paragraph-1"' in article_html
    article_files = list((output_dir / "data" / "articles").glob("*.json"))
    assert article_files
    cached_articles = [article_file.read_text(encoding="utf-8") for article_file in article_files]
    edition_payload = json.loads((output_dir / "data" / "edition.json").read_text())
    manifest_payload = json.loads((output_dir / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((output_dir / "data" / "runtime.json").read_text())
    assert any(
        story.get("editorial_takeaway", {}).get("en") or story.get("summary", {}).get("en")
        for story in edition_payload["stories"]
    )
    stored = repository.get_item(item_id)
    matches_after = repository.list_item_matches(item_id)
    second_stored = repository.get_item(second_item_id)
    second_matches_after = repository.list_item_matches(second_item_id)
    item_count_after = repository.count_items()

    assert 'id="local-article"' in detail_html
    assert "Local article paragraph for the ROW ONE detail page." in detail_html
    assert "Read saved article" in detail_html
    assert "阅读本地正文" in detail_html
    assert "saved-article-content-organization-evidence-link" in index_html
    assert "local-read-path" in detail_html
    assert all(
        "Local article paragraph for the ROW ONE detail page." in cached_article
        for cached_article in cached_articles
    )
    assert (
        "daily-local-intelligence" in index_html
        or "saved-article-coverage" in index_html
        or "saved-article-briefs" in index_html
    )
    assert 'class="daily-edit"' in index_html
    assert "Daily Edit" in index_html
    assert "今日编辑简报" in index_html
    assert 'class="editorial-brief"' in index_html
    assert 'class="editorial-brief-trail"' in index_html
    assert "Editorial Brief" in index_html
    assert "编辑正文" in index_html
    assert "Saved Article Content Organization" in index_html
    assert "保存正文内容整理" in index_html
    assert "#local-article-content-section-" in index_html
    assert "local-article-content-previews" in detail_html
    assert "Saved Paragraph Evidence" in detail_html
    assert "本地段落线索" in detail_html
    assert 'id="local-article-paragraph-evidence"' in detail_html
    assert "Saved paragraph" in detail_html
    assert "保存段落" in detail_html
    assert 'class="detail-signal-briefing"' in detail_html
    assert "Signal Briefing" in detail_html
    assert "信号简报" in detail_html
    assert any('id="continue-reading"' in html for html in detail_pages.values())
    assert any(
        "The Row ballet flat gains editorial traction" in html for html in detail_pages.values()
    )
    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    generated_contract_payload = json.dumps(
        {
            "edition": edition_payload,
            "manifest": manifest_payload,
            "runtime": runtime_payload,
        },
        ensure_ascii=False,
    )
    assert '"local_articles"' not in generated_contract_payload
    assert '"saved_article_content_organization"' not in generated_contract_payload
    assert '"saved_paragraph_previews"' not in generated_contract_payload
    assert '"continue_reading"' not in generated_contract_payload
    assert '"related_stories"' not in generated_contract_payload
    assert '"detail_signal_briefing"' not in generated_contract_payload
    assert '"signal_briefing"' not in generated_contract_payload
    assert '"daily_edit"' not in generated_contract_payload
    assert '"editorial_brief"' not in generated_contract_payload
    assert '"editorial_source_trail"' not in generated_contract_payload
    assert '"source_trail"' not in generated_contract_payload
    assert '"daily_information_layer"' not in generated_contract_payload
    assert '"local_article_count"' not in generated_contract_payload
    assert '"local_article_paragraph_count"' not in generated_contract_payload
    assert '"local_first_read"' not in generated_contract_payload
    assert '"local_read_path"' not in generated_contract_payload
    assert '"saved_article_cta"' not in generated_contract_payload
    assert '"evidence_paragraph_trail"' not in generated_contract_payload
    assert '"paragraph_trail"' not in generated_contract_payload
    assert '"evidence_paragraph_chips"' not in generated_contract_payload
    assert '"saved_article_content_organization_evidence"' not in generated_contract_payload
    assert '"local_article_paragraph_evidence"' not in generated_contract_payload
    assert '"paragraph_evidence_index"' not in generated_contract_payload
    assert '"local_evidence_index"' not in generated_contract_payload
    assert '"evidence_paragraph_index"' not in generated_contract_payload
    assert '"saved_article_library"' not in generated_contract_payload
    assert '"daily_saved_article_library"' not in generated_contract_payload
    assert '"article_library"' not in generated_contract_payload
    assert '"saved_signal_index"' not in generated_contract_payload
    assert '"saved_signal_excerpt"' not in generated_contract_payload
    assert '"signal_index"' not in generated_contract_payload
    assert '"signal_excerpt"' not in generated_contract_payload
    assert '"ops_check"' not in generated_contract_payload
    assert '"deploy_status"' not in generated_contract_payload
    assert '"port_status"' not in generated_contract_payload
    assert '"entity_index"' not in generated_contract_payload
    assert '"brand_index"' not in generated_contract_payload
    assert '"product_index"' not in generated_contract_payload
    assert '"saved_article_entity_index"' not in generated_contract_payload
    assert '"saved_article_brand_index"' not in generated_contract_payload
    assert '"saved_article_product_index"' not in generated_contract_payload
    assert '"saved_article_evidence_board"' not in generated_contract_payload
    assert '"saved_article_paragraph_evidence_board"' not in generated_contract_payload
    assert '"paragraph_evidence_board"' not in generated_contract_payload
    assert '"saved_paragraph_evidence_board"' not in generated_contract_payload
    assert '"article_paragraph_evidence_board"' not in generated_contract_payload
    assert '"evidence_board"' not in generated_contract_payload
    assert '"saved_article_evidence_cards"' not in generated_contract_payload
    assert '"paragraph_evidence_cards"' not in generated_contract_payload
    assert '"local_article_pages"' not in generated_contract_payload
    assert '"local_article_page"' not in generated_contract_payload
    assert '"first_class_local_article"' not in generated_contract_payload
    assert '"saved_article_pages"' not in generated_contract_payload
    assert '"article_page_routes"' not in generated_contract_payload
    assert "saved-article-library" not in generated_contract_payload
    assert "saved-signal-index" not in generated_contract_payload
    assert "saved-article-evidence-board" not in generated_contract_payload
    assert "local-article-page" not in generated_contract_payload
    assert "Daily Saved Article Library" not in generated_contract_payload
    assert "Saved Signal Index" not in generated_contract_payload
    assert "Saved Article Paragraph Evidence Board" not in generated_contract_payload
    assert "每日本地文章库" not in generated_contract_payload
    assert "本地信号索引" not in generated_contract_payload
    assert "保存文章段落证据板" not in generated_contract_payload
    assert "saved-signal-index.json" not in generated_contract_payload
    assert "saved-signal-excerpts.json" not in generated_contract_payload
    assert "saved-signal-excerpt.html" not in generated_contract_payload
    assert "saved-article-evidence-board.json" not in generated_contract_payload
    assert "local-article-pages.json" not in generated_contract_payload
    assert "saved-article-pages.json" not in generated_contract_payload
    assert "saved-article-paragraph-quality-gate.json" not in generated_contract_payload
    assert "saved_article_paragraph_quality_gate" not in generated_contract_payload
    assert "paragraph_quality_gate" not in generated_contract_payload
    assert "saved_paragraph_quality_gate" not in generated_contract_payload
    assert "article_paragraph_quality_gate" not in generated_contract_payload
    assert "saved-article-paragraph-quality-gate" not in generated_contract_payload
    assert "paragraph-quality-gate" not in generated_contract_payload
    assert "Saved Article Paragraph Quality Gate" not in generated_contract_payload
    assert "local_article_reading_improvements" not in generated_contract_payload
    assert "local_article_reader_improvements" not in generated_contract_payload
    assert "article_reading_improvements" not in generated_contract_payload
    assert "reading_improvements" not in generated_contract_payload
    assert "local-article-reading-improvements" not in generated_contract_payload
    assert "article-reading-improvements" not in generated_contract_payload
    assert "Local Article Reading Improvements" not in generated_contract_payload
    assert "local-article-reading-improvements.json" not in generated_contract_payload
    assert "saved_paragraph_context_cues" not in generated_contract_payload
    assert "local_article_paragraph_contexts" not in generated_contract_payload
    assert "local_article_context_cues" not in generated_contract_payload
    assert "paragraph_context_cues" not in generated_contract_payload
    assert "saved_article_content_organization_summary" not in generated_contract_payload
    assert "content_organization_group_summary" not in generated_contract_payload
    assert "Saved Article Content Organization Group Summary" not in generated_contract_payload
    assert "saved-article-content-organization-summary" not in generated_contract_payload
    assert "content-organization-group-summary" not in generated_contract_payload
    assert "saved_article_organization_coverage" not in generated_contract_payload
    assert "organization_coverage_matrix" not in generated_contract_payload
    assert "Saved Article Organization Coverage Matrix" not in generated_contract_payload
    assert "saved-article-organization-coverage" not in generated_contract_payload
    assert "organization-coverage-matrix" not in generated_contract_payload
    assert "saved_article_daily_summary" not in generated_contract_payload
    assert "daily_saved_article_summary" not in generated_contract_payload
    assert "Saved Article Daily Summary" not in generated_contract_payload
    assert "saved-article-daily-summary" not in generated_contract_payload
    assert "daily-saved-article-summary" not in generated_contract_payload
    assert "saved_article_body_guide" not in generated_contract_payload
    assert "article_body_guide" not in generated_contract_payload
    assert "Saved Article Body Guide" not in generated_contract_payload
    assert "saved-article-body-guide" not in generated_contract_payload
    assert "article-body-guide" not in generated_contract_payload
    assert "saved_article_source_brief" not in generated_contract_payload
    assert "article_source_brief" not in generated_contract_payload
    assert "Source Brief" not in generated_contract_payload
    assert "source-brief" not in generated_contract_payload
    assert "saved-article-source-brief" not in generated_contract_payload
    assert "article-source-brief" not in generated_contract_payload
    assert "Saved Paragraph Context Cues" not in generated_contract_payload
    assert "saved-paragraph-context-cues" not in generated_contract_payload
    assert "local-article-paragraph-contexts" not in generated_contract_payload
    assert "local-article-context-cues" not in generated_contract_payload
    assert "paragraph-context-cues" not in generated_contract_payload
    assert "ROW ONE ops check" not in generated_contract_payload
    articles_html_path = output_dir / "articles" / "index.html"
    if articles_html_path.exists():
        articles_html = articles_html_path.read_text(encoding="utf-8")
        assert 'class="saved-article-content-organization-group"' in articles_html
        assert 'class="saved-article-content-organization-summary"' in articles_html
        assert 'class="saved-article-body-guide"' in articles_html
        assert 'class="saved-article-source-brief"' in articles_html
        if "saved-signal-index-support-row" in articles_html:
            assert "saved-signal-index-support-excerpt" in articles_html
    top_level_data_files = {path.name for path in (output_dir / "data").glob("*.json")}
    assert top_level_data_files <= {
        "edition.json",
        "manifest.json",
        "runtime.json",
        "local-intelligence.json",
    }
    assert not (output_dir / "data" / "local-article-metrics.json").exists()
    for artifact_path in (
        output_dir / "ops-check.html",
        output_dir / "saved-signal-excerpts.json",
        output_dir / "saved-signal-excerpt.html",
        output_dir / "articles" / "saved-signal-excerpts.json",
        output_dir / "articles" / "saved-signal-excerpt.html",
        output_dir / "data" / "ops-check.json",
        output_dir / "data" / "saved-signal-excerpts.json",
        output_dir / "saved-article-evidence-board.json",
        output_dir / "articles" / "saved-article-evidence-board.json",
        output_dir / "data" / "saved-article-evidence-board.json",
        output_dir / "local-article-pages.json",
        output_dir / "articles" / "local-article-pages.json",
        output_dir / "data" / "local-article-pages.json",
        output_dir / "saved-article-pages.json",
        output_dir / "articles" / "saved-article-pages.json",
        output_dir / "data" / "saved-article-pages.json",
        output_dir / "saved-article-paragraph-quality-gate.json",
        output_dir / "articles" / "saved-article-paragraph-quality-gate.json",
        output_dir / "data" / "saved-article-paragraph-quality-gate.json",
        output_dir / "saved-article-paragraph-quality-gate.html",
        output_dir / "articles" / "saved-article-paragraph-quality-gate.html",
        output_dir / "data" / "saved-article-paragraph-quality-gate.html",
        output_dir / "local-article-reading-improvements.json",
        output_dir / "articles" / "local-article-reading-improvements.json",
        output_dir / "data" / "local-article-reading-improvements.json",
        output_dir / "local-article-reading-improvements.html",
        output_dir / "articles" / "local-article-reading-improvements.html",
        output_dir / "data" / "local-article-reading-improvements.html",
        output_dir / "saved-paragraph-context-cues.json",
        output_dir / "articles" / "saved-paragraph-context-cues.json",
        output_dir / "data" / "saved-paragraph-context-cues.json",
        output_dir / "local-article-paragraph-contexts.json",
        output_dir / "articles" / "local-article-paragraph-contexts.json",
        output_dir / "data" / "local-article-paragraph-contexts.json",
        output_dir / "saved-paragraph-context-cues.html",
        output_dir / "articles" / "saved-paragraph-context-cues.html",
        output_dir / "data" / "saved-paragraph-context-cues.html",
        output_dir / "local-article-context-cues.json",
        output_dir / "articles" / "local-article-context-cues.json",
        output_dir / "data" / "local-article-context-cues.json",
        output_dir / "local-article-context-cues.html",
        output_dir / "articles" / "local-article-context-cues.html",
        output_dir / "data" / "local-article-context-cues.html",
        output_dir / "saved-article-content-organization-summary.json",
        output_dir / "articles" / "saved-article-content-organization-summary.json",
        output_dir / "data" / "saved-article-content-organization-summary.json",
        output_dir / "saved-article-content-organization-summary.html",
        output_dir / "articles" / "saved-article-content-organization-summary.html",
        output_dir / "data" / "saved-article-content-organization-summary.html",
        output_dir / "content-organization-group-summary.json",
        output_dir / "articles" / "content-organization-group-summary.json",
        output_dir / "data" / "content-organization-group-summary.json",
        output_dir / "content-organization-group-summary.html",
        output_dir / "articles" / "content-organization-group-summary.html",
        output_dir / "data" / "content-organization-group-summary.html",
        output_dir / "saved-article-organization-coverage.json",
        output_dir / "articles" / "saved-article-organization-coverage.json",
        output_dir / "data" / "saved-article-organization-coverage.json",
        output_dir / "saved-article-organization-coverage.html",
        output_dir / "articles" / "saved-article-organization-coverage.html",
        output_dir / "data" / "saved-article-organization-coverage.html",
        output_dir / "organization-coverage-matrix.json",
        output_dir / "articles" / "organization-coverage-matrix.json",
        output_dir / "data" / "organization-coverage-matrix.json",
        output_dir / "organization-coverage-matrix.html",
        output_dir / "articles" / "organization-coverage-matrix.html",
        output_dir / "data" / "organization-coverage-matrix.html",
        output_dir / "saved-article-daily-summary.json",
        output_dir / "articles" / "saved-article-daily-summary.json",
        output_dir / "data" / "saved-article-daily-summary.json",
        output_dir / "saved-article-daily-summary.html",
        output_dir / "articles" / "saved-article-daily-summary.html",
        output_dir / "data" / "saved-article-daily-summary.html",
        output_dir / "daily-saved-article-summary.json",
        output_dir / "articles" / "daily-saved-article-summary.json",
        output_dir / "data" / "daily-saved-article-summary.json",
        output_dir / "daily-saved-article-summary.html",
        output_dir / "articles" / "daily-saved-article-summary.html",
        output_dir / "data" / "daily-saved-article-summary.html",
        output_dir / "saved-article-body-guide.json",
        output_dir / "articles" / "saved-article-body-guide.json",
        output_dir / "data" / "saved-article-body-guide.json",
        output_dir / "saved-article-body-guide.html",
        output_dir / "articles" / "saved-article-body-guide.html",
        output_dir / "data" / "saved-article-body-guide.html",
        output_dir / "article-body-guide.json",
        output_dir / "articles" / "article-body-guide.json",
        output_dir / "data" / "article-body-guide.json",
        output_dir / "article-body-guide.html",
        output_dir / "articles" / "article-body-guide.html",
        output_dir / "data" / "article-body-guide.html",
        output_dir / "saved-article-source-brief.json",
        output_dir / "articles" / "saved-article-source-brief.json",
        output_dir / "data" / "saved-article-source-brief.json",
        output_dir / "saved-article-source-brief.html",
        output_dir / "articles" / "saved-article-source-brief.html",
        output_dir / "data" / "saved-article-source-brief.html",
        output_dir / "article-source-brief.json",
        output_dir / "articles" / "article-source-brief.json",
        output_dir / "data" / "article-source-brief.json",
        output_dir / "article-source-brief.html",
        output_dir / "articles" / "article-source-brief.html",
        output_dir / "data" / "article-source-brief.html",
    ):
        assert not artifact_path.exists()
    assert stored == stored_before
    assert matches_after == matches_before
    assert second_stored == second_stored_before
    assert second_matches_after == second_matches_before
    assert item_count_after == item_count_before
    assert stored["summary"] == "The Row handbag coverage."
    assert second_stored["summary"] == "The Row ballet flat coverage."


def test_prune_stale_daily_report_files_removes_old_dated_artifacts(
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    stale_names = [
        "fashion-radar-2026-07-01.md",
        "fashion-radar-2026-07-01.json",
        "fashion-radar-2026-07-01.html",
        "fashion-radar-2026-06-30.md",
    ]
    current_names = [
        "fashion-radar-2026-07-02.md",
        "fashion-radar-2026-07-02.json",
        "fashion-radar-2026-07-02.html",
    ]
    untouched_names = [
        "latest.md",
        "latest.json",
        "report-index.json",
        "fashion-radar-2026-07-01.eml",
        "fashion-radar-2026-07-01.txt",
        "fashion-radar-2026-07-03.md",
        "fashion-radar-not-a-date.md",
        "notes.md",
    ]
    for name in stale_names + current_names + untouched_names:
        (reports_dir / name).write_text(name, encoding="utf-8")

    result = prune_stale_daily_report_files(
        reports_dir=reports_dir,
        as_of=datetime(2026, 7, 2, 4, 0, tzinfo=UTC),
    )

    assert result.removed_count == len(stale_names)
    assert result.kept_current_count == len(current_names)
    assert result.current_date == "2026-07-02"
    assert [path.name for path in result.removed_paths] == sorted(stale_names)
    for name in stale_names:
        assert not (reports_dir / name).exists()
    for name in current_names + untouched_names:
        assert (reports_dir / name).exists()


def test_prune_stale_daily_report_files_missing_directory_is_noop(tmp_path: Path) -> None:
    reports_dir = tmp_path / "missing-reports"

    result = prune_stale_daily_report_files(
        reports_dir=reports_dir,
        as_of=datetime(2026, 7, 2, 4, 0, tzinfo=UTC),
    )

    assert result.removed_count == 0
    assert result.kept_current_count == 0
    assert result.current_date == "2026-07-02"
    assert result.removed_paths == []


def test_prune_stale_daily_report_files_tolerates_concurrent_removal(
    tmp_path: Path,
    monkeypatch,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    stale_path = reports_dir / "fashion-radar-2026-07-01.md"
    stale_path.write_text("stale", encoding="utf-8")
    original_unlink = Path.unlink

    def unlink_after_external_removal(path: Path, *args: object, **kwargs: object) -> None:
        original_unlink(path)
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", unlink_after_external_removal)

    result = prune_stale_daily_report_files(
        reports_dir=reports_dir,
        as_of=datetime(2026, 7, 2, 4, 0, tzinfo=UTC),
    )

    assert result.removed_count == 1
    assert result.removed_paths == [stale_path]
    assert not stale_path.exists()


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


def test_default_collectors_register_all_social_and_web_collectors() -> None:
    collectors = _default_collectors()

    assert isinstance(collectors[SourceType.HTML], HtmlCollector)
    assert isinstance(collectors[SourceType.SITEMAP], SitemapCollector)
    assert isinstance(collectors[SourceType.XIAOHONGSHU], XiaohongshuCollector)
    assert isinstance(collectors[SourceType.INSTAGRAM], InstagramCollector)
    assert isinstance(collectors[SourceType.TWITTER], TwitterCollector)
    assert isinstance(collectors[SourceType.YOUTUBE], YouTubeCollector)
    assert isinstance(collectors[SourceType.RSS], RssCollector)
    assert isinstance(collectors[SourceType.RSSHUB], RssCollector)
    assert isinstance(collectors[SourceType.GDELT], GdeltCollector)
