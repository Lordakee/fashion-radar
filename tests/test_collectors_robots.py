from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.collectors.robots import RobotsPolicyChecker


@dataclass
class Response:
    status_code: int
    text: str


def test_can_fetch_respects_disallow_rules() -> None:
    checker = RobotsPolicyChecker(
        lambda _url: Response(200, "User-agent: *\nDisallow: /private\nAllow: /\n")
    )

    assert checker.can_fetch("https://example.com/public/story", "FashionRadarBot") is True
    assert checker.can_fetch("https://example.com/private/story", "FashionRadarBot") is False


def test_can_fetch_defaults_false_when_robots_unavailable() -> None:
    checker = RobotsPolicyChecker(lambda _url: Response(404, ""))

    assert checker.can_fetch("https://example.com/public/story", "FashionRadarBot") is False


def test_check_reports_robots_unavailable_separately_from_disallow() -> None:
    unavailable = RobotsPolicyChecker(lambda _url: Response(404, ""))
    disallowing = RobotsPolicyChecker(
        lambda _url: Response(200, "User-agent: *\nDisallow: /private\nAllow: /\n")
    )

    unavailable_result = unavailable.check("https://example.com/public/story", "FashionRadarBot")
    disallowed_result = disallowing.check("https://example.com/private/story", "FashionRadarBot")

    assert unavailable_result.allowed is False
    assert unavailable_result.reason == "robots_unavailable"
    assert disallowed_result.allowed is False
    assert disallowed_result.reason == "robots_disallowed"


def test_can_fetch_defaults_false_when_robots_malformed() -> None:
    checker = RobotsPolicyChecker(lambda _url: Response(200, "<html>not robots</html>"))

    assert checker.can_fetch("https://example.com/public/story", "FashionRadarBot") is False


def test_can_fetch_caches_rules_per_scheme_and_netloc() -> None:
    fetched_urls: list[str] = []

    def fetcher(url: str) -> Response:
        fetched_urls.append(url)
        return Response(200, "User-agent: *\nAllow: /\n")

    checker = RobotsPolicyChecker(fetcher)

    assert checker.can_fetch("https://example.com/first", "FashionRadarBot") is True
    assert checker.can_fetch("https://example.com/second", "FashionRadarBot") is True
    assert checker.can_fetch("http://example.com/third", "FashionRadarBot") is True

    assert fetched_urls == [
        "https://example.com/robots.txt",
        "http://example.com/robots.txt",
    ]
