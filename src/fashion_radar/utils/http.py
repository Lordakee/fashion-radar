from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

import httpx

from fashion_radar.models.source import HttpSourceSettings


class HttpFetchError(RuntimeError):
    """Raised when an HTTP request fails after the configured retry budget."""


class FashionHttpClient:
    def __init__(
        self,
        settings: HttpSourceSettings,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep_func: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.settings = settings
        self._sleep = sleep_func
        self._clock = clock
        self._last_request_by_domain: dict[str, float] = {}
        self._client = httpx.Client(
            headers={"User-Agent": settings.user_agent},
            timeout=settings.timeout_seconds,
            transport=transport,
        )

    def get_text(self, url: str, *, params: dict[str, str | int] | None = None) -> str:
        return self._get(url, params=params).text

    def get_json(self, url: str, *, params: dict[str, str | int] | None = None) -> Any:
        return self._get(url, params=params).json()

    def get_response(
        self,
        url: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> httpx.Response:
        return self._get(url, params=params)

    def close(self) -> None:
        self._client.close()

    def _get(self, url: str, *, params: dict[str, str | int] | None = None) -> httpx.Response:
        last_error: Exception | None = None
        attempts = self.settings.max_retries + 1
        for attempt in range(attempts):
            self._apply_politeness_delay(url)
            try:
                response = self._client.get(url, params=params)
                if response.status_code >= 500 and attempt < attempts - 1:
                    self._sleep(self.settings.backoff_base_seconds * (2**attempt))
                    last_error = httpx.HTTPStatusError(
                        f"server error {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                    continue
                response.raise_for_status()
                self._record_request_time(url)
                return response
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code < 500:
                    break
                if attempt >= attempts - 1:
                    break
                self._sleep(self.settings.backoff_base_seconds * (2**attempt))
            except httpx.RequestError as exc:
                last_error = exc
                if attempt >= attempts - 1:
                    break
                self._sleep(self.settings.backoff_base_seconds * (2**attempt))
        raise HttpFetchError(f"GET {url} failed after {attempts} attempts") from last_error

    def _apply_politeness_delay(self, url: str) -> None:
        domain = _domain_key(url)
        if not domain:
            return
        last_request_at = self._last_request_by_domain.get(domain)
        if last_request_at is None:
            return
        elapsed = self._clock() - last_request_at
        remaining = self.settings.per_domain_delay_seconds - elapsed
        if remaining > 0:
            self._sleep(remaining)

    def _record_request_time(self, url: str) -> None:
        domain = _domain_key(url)
        if domain:
            self._last_request_by_domain[domain] = self._clock()


def _domain_key(url: str) -> str:
    parsed = urlsplit(url)
    return parsed.netloc.lower()
