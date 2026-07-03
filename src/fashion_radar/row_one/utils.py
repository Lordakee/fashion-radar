from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlsplit


def safe_external_url(url: str | None) -> str | None:
    if not url:
        return None
    if "\\" in url or any(
        character.isspace() or ord(character) < 32 or ord(character) == 127 for character in url
    ):
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        return None
    return url


def isoformat_z(value: datetime) -> str:
    return utc_datetime(value).isoformat().replace("+00:00", "Z")


def utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
