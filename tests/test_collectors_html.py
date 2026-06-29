from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.article import ArticleExtractionResult
from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def _html_source(**overrides: object) -> SourceDefinition:
    payload = {"name": "Brand X", "type": SourceType.HTML, "url": "https://brandx.com/news"}
    payload.update(overrides)
    return SourceDefinition(**payload)


def _result(
    url: str,
    *,
    title: str | None = "Brand X News",
    text: str | None = "Summary text.",
    published_at: str | None = "2026-06-11T08:00:00Z",
    skipped: bool = False,
    reason: str | None = None,
) -> ArticleExtractionResult:
    return ArticleExtractionResult(
        url=url,
        title=title,
        text=text,
        published_at=published_at,
        skipped=skipped,
        reason=reason,
    )


def _patch_extraction(monkeypatch, per_url: dict[str, ArticleExtractionResult]) -> list[str]:
    called: list[str] = []

    def fake_extract(url, *, source, html_fetcher, robots_checker):
        called.append(url)
        return per_url.get(url, _result(url, skipped=True, reason="no_extractable_text"))

    monkeypatch.setattr("fashion_radar.collectors.html.extract_article_with_metadata", fake_extract)
    monkeypatch.setattr("fashion_radar.collectors.html.extractor_available", lambda: True)
    return called


def test_html_collector_extracts_seed_into_collected_item(monkeypatch) -> None:
    called = _patch_extraction(
        monkeypatch, {"https://brandx.com/news": _result("https://brandx.com/news")}
    )
    started = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = HtmlCollector().collect(_html_source(), started_at=started)

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert called == ["https://brandx.com/news"]
    assert len(result.items) == 1
    item = result.items[0]
    assert item.source_name == "Brand X"
    assert item.source_type == SourceType.HTML
    assert item.url == "https://brandx.com/news"
    assert item.title == "Brand X News"
    assert item.summary == "Summary text."
    assert item.published_at == datetime(2026, 6, 11, 8, 0, tzinfo=UTC)
    assert result.status.items_seen == 1


def test_html_collector_skips_skipped_seed_but_counts_it_in_items_seen(monkeypatch) -> None:
    _patch_extraction(
        monkeypatch,
        {
            "https://brandx.com/news": _result(
                "https://brandx.com/news", skipped=True, reason="robots_disallowed", text=None
            )
        },
    )

    result = HtmlCollector().collect(
        _html_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.items == []
    assert result.status.items_seen == 1


def test_html_collector_prefers_seed_urls_over_url(monkeypatch) -> None:
    called = _patch_extraction(
        monkeypatch,
        {
            "https://brandx.com/press": _result("https://brandx.com/press"),
            "https://brandx.com/collections": _result("https://brandx.com/collections"),
        },
    )
    source = _html_source(
        url="https://brandx.com/news",
        seed_urls=["https://brandx.com/press", "https://brandx.com/collections"],
    )

    HtmlCollector().collect(source, started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC))

    assert called == ["https://brandx.com/press", "https://brandx.com/collections"]


def test_html_collector_falls_back_to_url_when_seed_urls_empty(monkeypatch) -> None:
    called = _patch_extraction(
        monkeypatch, {"https://brandx.com/news": _result("https://brandx.com/news")}
    )

    HtmlCollector().collect(_html_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC))

    assert called == ["https://brandx.com/news"]


def test_html_collector_returns_skipped_when_extractor_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("fashion_radar.collectors.html.extractor_available", lambda: False)

    result = HtmlCollector().collect(
        _html_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "extractor_unavailable"
    assert result.items == []


def test_html_collector_uses_fallback_title_when_extraction_has_none(monkeypatch) -> None:
    _patch_extraction(
        monkeypatch,
        {
            "https://brandx.com/news/spring-collection": _result(
                "https://brandx.com/news/spring-collection", title=None
            )
        },
    )
    source = _html_source(url="https://brandx.com/news/spring-collection")

    result = HtmlCollector().collect(source, started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC))

    assert result.items[0].title == "spring-collection"


def test_html_collector_falls_back_to_started_at_when_date_unparseable(monkeypatch) -> None:
    _patch_extraction(
        monkeypatch,
        {"https://brandx.com/news": _result("https://brandx.com/news", published_at="not-a-date")},
    )
    started = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = HtmlCollector().collect(_html_source(), started_at=started)

    assert result.items[0].published_at == started


def test_html_collector_reports_items_seen_across_mixed_seeds(monkeypatch) -> None:
    _patch_extraction(
        monkeypatch,
        {
            "https://brandx.com/press": _result("https://brandx.com/press"),
            "https://brandx.com/paywalled": _result(
                "https://brandx.com/paywalled", skipped=True, reason="paywalled_domain", text=None
            ),
        },
    )
    source = _html_source(seed_urls=["https://brandx.com/press", "https://brandx.com/paywalled"])

    result = HtmlCollector().collect(source, started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC))

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert [item.url for item in result.items] == ["https://brandx.com/press"]
