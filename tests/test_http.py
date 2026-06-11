import httpx
import pytest

from fashion_radar.models.source import HttpSourceSettings
from fashion_radar.utils.http import FashionHttpClient, HttpFetchError


def test_http_client_sends_user_agent_and_parses_json() -> None:
    seen_headers: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.append(request.headers["user-agent"])
        return httpx.Response(200, json={"ok": True})

    client = FashionHttpClient(
        HttpSourceSettings(user_agent="FashionRadar/Test", per_domain_delay_seconds=0),
        transport=httpx.MockTransport(handler),
    )

    assert client.get_json("https://example.com/data.json") == {"ok": True}
    assert seen_headers == ["FashionRadar/Test"]


def test_http_client_retries_server_errors_with_bound() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, text="temporary")
        return httpx.Response(200, text="ok")

    client = FashionHttpClient(
        HttpSourceSettings(max_retries=1, per_domain_delay_seconds=0),
        transport=httpx.MockTransport(handler),
        sleep_func=lambda _seconds: None,
    )

    assert client.get_text("https://example.com/feed.xml") == "ok"
    assert attempts == 2


def test_http_client_applies_per_domain_politeness_delay() -> None:
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="ok")

    client = FashionHttpClient(
        HttpSourceSettings(per_domain_delay_seconds=1.0),
        transport=httpx.MockTransport(handler),
        sleep_func=sleeps.append,
        clock=lambda: 100.0,
    )

    client.get_text("https://example.com/one")
    client.get_text("https://example.com/two")

    assert sleeps == [1.0]


def test_http_client_raises_after_retry_budget_is_exhausted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="temporary")

    client = FashionHttpClient(
        HttpSourceSettings(max_retries=1, per_domain_delay_seconds=0),
        transport=httpx.MockTransport(handler),
        sleep_func=lambda _seconds: None,
    )

    with pytest.raises(HttpFetchError, match="GET https://example.com/feed.xml failed"):
        client.get_text("https://example.com/feed.xml")


def test_http_client_does_not_retry_client_errors() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(404, text="missing")

    client = FashionHttpClient(
        HttpSourceSettings(max_retries=2, per_domain_delay_seconds=0),
        transport=httpx.MockTransport(handler),
        sleep_func=lambda _seconds: None,
    )

    with pytest.raises(HttpFetchError):
        client.get_text("https://example.com/missing")
    assert attempts == 1
