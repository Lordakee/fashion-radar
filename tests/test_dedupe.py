from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.utils.hashing import content_hash, normalize_url


def test_normalize_url_strips_tracking_params_and_keeps_real_query() -> None:
    url = (
        "HTTPS://Example.com/Article?"
        "utm_source=instagram&b=2&a=1&fbclid=abc&empty=&ref_src=tw#section"
    )

    assert normalize_url(url) == "https://example.com/Article?a=1&b=2"


def test_normalize_url_keeps_non_tracking_query_params() -> None:
    url = "https://example.com/search?q=the+row&sort=new&utm_campaign=summer"

    assert normalize_url(url) == "https://example.com/search?q=the+row&sort=new"


def test_content_hash_normalizes_core_attribution_fields() -> None:
    published_at = datetime(2026, 6, 11, 10, 0, tzinfo=UTC)

    first = content_hash(
        title="  The   Row Margaux ",
        published_at=published_at,
        source_name="Vogue Business",
        summary="A concise signal about the bag.",
    )
    second = content_hash(
        title="the row margaux",
        published_at="2026-06-11T10:00:00Z",
        source_name="vogue business",
        summary="a concise signal about the bag.",
    )

    assert first == second


def test_content_hash_folds_stage_196_latin_overrides() -> None:
    published_at = datetime(2026, 6, 11, 10, 0, tzinfo=UTC)

    first = content_hash(
        title="Søster Studio MØ bag",
        published_at=published_at,
        source_name="Fashion Wire",
        summary="Søster launches the MØ tote.",
    )
    second = content_hash(
        title="Soster Studio MO bag",
        published_at="2026-06-11T10:00:00Z",
        source_name="Fashion Wire",
        summary="Soster launches the MO tote.",
    )

    assert first == second
