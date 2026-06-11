from __future__ import annotations

from datetime import UTC, datetime

from dateutil import parser


def parse_datetime_utc(value: str | datetime) -> datetime:
    """Parse a date/datetime value and return a UTC-aware datetime."""
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = parser.parse(value)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
