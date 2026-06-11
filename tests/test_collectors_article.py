from __future__ import annotations

from types import SimpleNamespace

from fashion_radar.collectors.article import extract_article
from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.models.source import SourceDefinition, SourceType


class AllowingRobots:
    def can_fetch(self, url: str, user_agent: str) -> bool:
        return True


class DenyingRobots:
    def can_fetch(self, url: str, user_agent: str) -> bool:
        return False


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


def test_extract_article_skips_when_robots_disallow() -> None:
    result = extract_article(
        "https://example.com/story",
        source=rss_source(),
        html_fetcher=lambda _url: "<html></html>",
        robots_checker=DenyingRobots(),
    )

    assert result.skipped is True
    assert result.reason == "robots_disallowed"
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
