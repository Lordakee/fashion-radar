from datetime import UTC, datetime

from fashion_radar.utils.dates import parse_datetime_utc


def test_parse_datetime_utc_converts_offset_to_utc() -> None:
    parsed = parse_datetime_utc("2026-06-11T10:30:00+08:00")

    assert parsed == datetime(2026, 6, 11, 2, 30, tzinfo=UTC)


def test_parse_datetime_utc_assumes_naive_input_is_utc() -> None:
    parsed = parse_datetime_utc("2026-06-11 02:30:00")

    assert parsed == datetime(2026, 6, 11, 2, 30, tzinfo=UTC)
