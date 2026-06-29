from __future__ import annotations

from types import SimpleNamespace

from fashion_radar.collectors.article import (
    extract_article,
    extract_article_with_metadata,
    extractor_available,
)
from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.models.source import SourceDefinition, SourceType


class AllowingRobots:
    def can_fetch(self, url: str, user_agent: str) -> bool:
        return True


class DenyingRobots:
    def can_fetch(self, url: str, user_agent: str) -> bool:
        return False


class UnavailableRobots:
    def check(self, url: str, user_agent: str) -> object:
        return SimpleNamespace(allowed=False, reason="robots_unavailable")


def rss_source(**article_overrides: object) -> SourceDefinition:
    article = {"max_summary_chars": 12, **article_overrides}
    return SourceDefinition(
        name="Fashion Feed",
        type=SourceType.RSS,
        url="https://source.example/feed.xml",
        article=article,
    )


def test_extract_article_skips_when_article_extraction_disabled() -> None:
    result = extract_article(
        "https://example.com/story",
        source=rss_source(enabled=False),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "disabled"
    assert result.text is None


def test_extract_article_skips_paywalled_domains_without_fetching_html() -> None:
    fetched_urls: list[str] = []

    result = extract_article(
        "https://www.paywall.example/story",
        source=rss_source(paywalled_domains=["paywall.example"]),
        html_fetcher=lambda url: fetched_urls.append(url) or "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "paywalled_domain"
    assert fetched_urls == []


def test_extract_article_skips_when_robots_disallow(monkeypatch) -> None:
    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=lambda *_args, **_kwargs: "unused"),
    )

    result = extract_article(
        "https://example.com/story",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=DenyingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "robots_disallowed"
    assert result.text is None


def test_extract_article_reports_robots_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=lambda *_args, **_kwargs: "unused"),
    )

    result = extract_article(
        "https://example.com/story",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=UnavailableRobots(),
    )

    assert result.skipped is True
    assert result.reason == "robots_unavailable"
    assert result.text is None


def test_extract_article_uses_trafilatura_and_truncates_to_summary(monkeypatch) -> None:
    def fake_extract(html: str, *, include_comments: bool, include_tables: bool) -> str:
        assert html == "<article>Long article</article>"
        assert include_comments is False
        assert include_tables is False
        return "This summary is longer than the configured maximum"

    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=fake_extract),
    )

    result = extract_article(
        "https://example.com/story",
        source=rss_source(max_summary_chars=20),
        html_fetcher=lambda _url: "<article>Long article</article>",
        robots_checker=RobotsPolicyChecker(
            lambda _url: type(
                "Response",
                (),
                {"status_code": 200, "text": "User-agent: *\nAllow: /\n"},
            )()
        ),
    )

    assert result.skipped is False
    assert result.reason is None
    assert result.url == "https://example.com/story"
    assert result.text == "This summary is long"


def test_extract_article_with_metadata_returns_title_date_text(monkeypatch) -> None:
    def fake_extract(
        html: str, *, include_comments: bool, include_tables: bool, output_format: str
    ) -> str:
        assert output_format == "json"
        return (
            '{"title": "Brand X News", "date": "2026-06-11T08:00:00Z", '
            '"text": "This is the article body text"}'
        )

    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=fake_extract),
    )

    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(max_summary_chars=15),
        html_fetcher=lambda _url: "<html><article>body</article></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is False
    assert result.title == "Brand X News"
    assert result.published_at == "2026-06-11T08:00:00Z"
    assert result.text == "This is the art"


def test_extract_article_with_metadata_returns_none_title_when_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=lambda *_a, **_k: '{"text": "Body only, no title or date"}'),
    )

    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is False
    assert result.title is None
    assert result.published_at is None
    assert result.text == "Body only, n"


def test_extract_article_with_metadata_skips_disabled() -> None:
    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(enabled=False),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "disabled"


def test_extract_article_with_metadata_skips_paywalled_domain() -> None:
    result = extract_article_with_metadata(
        "https://www.paywall.example/news",
        source=rss_source(paywalled_domains=["paywall.example"]),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "paywalled_domain"


def test_extract_article_with_metadata_skips_when_robots_disallow(monkeypatch) -> None:
    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=lambda *_a, **_k: '{"text": "unused"}'),
    )

    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=DenyingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "robots_disallowed"


def test_extract_article_with_metadata_skips_when_extractor_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("fashion_radar.collectors.article.trafilatura", None)

    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "extractor_unavailable"


def test_extract_article_with_metadata_skips_when_no_extractable_text(monkeypatch) -> None:
    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=lambda *_a, **_k: None),
    )

    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "no_extractable_text"


def test_extractor_available_reflects_trafilatura_import(monkeypatch) -> None:
    from fashion_radar.collectors import article as article_module

    monkeypatch.setattr(article_module, "trafilatura", SimpleNamespace())
    assert extractor_available() is True

    monkeypatch.setattr(article_module, "trafilatura", None)
    assert extractor_available() is False


def test_extract_article_with_metadata_skips_when_extraction_fails(monkeypatch) -> None:
    def raising_extract(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "fashion_radar.collectors.article.trafilatura",
        SimpleNamespace(extract=raising_extract),
    )

    result = extract_article_with_metadata(
        "https://example.com/news",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=AllowingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "extraction_failed"
