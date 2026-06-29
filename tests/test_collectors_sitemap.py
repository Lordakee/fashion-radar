from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from fashion_radar.collectors.article import ArticleExtractionResult
from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.sitemap import MAX_SITEMAP_URLS_PER_RUN, SitemapCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def _sitemap_source(**overrides: object) -> SourceDefinition:
    payload = {
        "name": "Fashion News Daily",
        "type": SourceType.SITEMAP,
        "url": "https://fnd.example/sitemap.xml",
    }
    payload.update(overrides)
    return SourceDefinition(**payload)


def _result(url: str) -> ArticleExtractionResult:
    return ArticleExtractionResult(
        url=url,
        title="Brand X News",
        text="Summary text.",
        published_at="2026-06-11T08:00:00Z",
        skipped=False,
    )


def _patch_discovery(monkeypatch, discovered: list[str]) -> None:
    monkeypatch.setattr("fashion_radar.collectors.sitemap.extractor_available", lambda: True)
    monkeypatch.setattr(
        "fashion_radar.collectors.sitemap.trafilatura",
        SimpleNamespace(sitemaps=SimpleNamespace(sitemap_search=lambda _target: discovered)),
    )


def _patch_extraction(monkeypatch) -> list[str]:
    extracted: list[str] = []

    def fake_extract(url, *, source, html_fetcher, robots_checker):
        extracted.append(url)
        return _result(url)

    monkeypatch.setattr("fashion_radar.collectors.html.extract_article_with_metadata", fake_extract)
    return extracted


def test_sitemap_collector_discovers_and_extracts_urls(monkeypatch) -> None:
    _patch_discovery(monkeypatch, ["https://fnd.example/a", "https://fnd.example/b"])
    extracted = _patch_extraction(monkeypatch)

    result = SitemapCollector().collect(
        _sitemap_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert extracted == ["https://fnd.example/a", "https://fnd.example/b"]
    assert [item.url for item in result.items] == ["https://fnd.example/a", "https://fnd.example/b"]


def test_sitemap_collector_discovery_failure_returns_success_zero_items(monkeypatch) -> None:
    monkeypatch.setattr("fashion_radar.collectors.sitemap.extractor_available", lambda: True)

    def raising(_target):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "fashion_radar.collectors.sitemap.trafilatura",
        SimpleNamespace(sitemaps=SimpleNamespace(sitemap_search=raising)),
    )

    result = SitemapCollector().collect(
        _sitemap_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.items == []
    assert result.status.items_seen == 0


def test_sitemap_collector_skipped_when_extractor_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("fashion_radar.collectors.sitemap.extractor_available", lambda: False)

    result = SitemapCollector().collect(
        _sitemap_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "extractor_unavailable"
    assert result.items == []


def test_sitemap_collector_bounds_discovered_urls_to_run_cap(monkeypatch) -> None:
    many = [f"https://fnd.example/{i}" for i in range(MAX_SITEMAP_URLS_PER_RUN + 5)]
    _patch_discovery(monkeypatch, many)
    _patch_extraction(monkeypatch)

    result = SitemapCollector().collect(
        _sitemap_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.items_seen == MAX_SITEMAP_URLS_PER_RUN
    assert len(result.items) == MAX_SITEMAP_URLS_PER_RUN


def test_discover_sitemap_urls_returns_empty_for_none_target() -> None:
    from fashion_radar.collectors.sitemap import _discover_sitemap_urls

    assert _discover_sitemap_urls(None) == []
