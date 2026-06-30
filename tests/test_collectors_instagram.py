from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.instagram import InstagramCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def _post(shortcode: str, caption: str | None = None, date_utc: datetime | None = None):
    return SimpleNamespace(shortcode=shortcode, caption=caption, date_utc=date_utc, date=date_utc)


def _iter_or_raise(posts, raises):
    if raises is not None:

        def _gen():
            raise raises
            yield  # makes _gen a generator

        return _gen()
    return iter(posts or [])


def _patch(
    monkeypatch,
    *,
    hashtag_posts=None,
    profile_posts=None,
    session_raises=False,
    hashtag_raises=None,
    profile_raises=None,
):
    loader = SimpleNamespace(context=object(), session_raises=session_raises, loaded=None)

    def load_session(user):
        if loader.session_raises:
            raise RuntimeError("login required")
        loader.loaded = user

    loader.load_session_from_config = load_session
    loader.close = lambda: None

    hashtag_obj = SimpleNamespace(
        get_all_posts=lambda: _iter_or_raise(hashtag_posts, hashtag_raises)
    )
    profile_obj = SimpleNamespace(get_posts=lambda: _iter_or_raise(profile_posts, profile_raises))
    hashtag_type = type(
        "Hashtag", (), {"from_name": classmethod(lambda cls, ctx, name: hashtag_obj)}
    )
    profile_type = type(
        "Profile", (), {"from_username": classmethod(lambda cls, ctx, name: profile_obj)}
    )
    monkeypatch.setattr(
        "fashion_radar.collectors.instagram.instaloader",
        SimpleNamespace(Instaloader=lambda: loader, Hashtag=hashtag_type, Profile=profile_type),
    )
    return loader


def _ig_source(**overrides):
    payload = {"name": "IG", "type": SourceType.INSTAGRAM, "query": "therow"}
    payload.update(overrides)
    return SourceDefinition(**payload)


def test_instagram_collector_maps_hashtag_posts_into_items(monkeypatch):
    posts = [
        _post("abc", "The Row Margaux bag\nNew drop.", datetime(2026, 6, 11, 8, 0, tzinfo=UTC)),
        _post("def", "Ballet flats season", datetime(2026, 6, 11, 9, 0, tzinfo=UTC)),
    ]
    _patch(monkeypatch, hashtag_posts=posts)

    result = InstagramCollector().collect(
        _ig_source(instagram={"login_user": "buyer1"}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert [item.url for item in result.items] == [
        "https://www.instagram.com/p/abc/",
        "https://www.instagram.com/p/def/",
    ]
    assert result.items[0].title == "The Row Margaux bag"
    assert result.items[0].summary == "The Row Margaux bag New drop."
    assert result.items[0].published_at == datetime(2026, 6, 11, 8, 0, tzinfo=UTC)


def test_instagram_collector_maps_profile_posts(monkeypatch):
    _patch(
        monkeypatch,
        profile_posts=[_post("abc", "Profile post", datetime(2026, 6, 11, 8, 0, tzinfo=UTC))],
    )

    result = InstagramCollector().collect(
        _ig_source(query="therow", instagram={"target_type": "profile"}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert [item.url for item in result.items] == ["https://www.instagram.com/p/abc/"]


def test_instagram_collector_bounds_posts_to_max_per_run(monkeypatch):
    posts = [_post(f"id{n}", f"caption {n}") for n in range(5)]
    _patch(monkeypatch, hashtag_posts=posts)

    result = InstagramCollector().collect(
        _ig_source(instagram={"max_posts_per_run": 2}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.items_seen == 2
    assert len(result.items) == 2


def test_instagram_collector_skips_when_instaloader_missing(monkeypatch):
    monkeypatch.setattr("fashion_radar.collectors.instagram.instaloader", None)

    result = InstagramCollector().collect(
        _ig_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "instaloader_unavailable"


def test_instagram_collector_skips_login_required_at_session_load(monkeypatch):
    _patch(monkeypatch, session_raises=True)

    result = InstagramCollector().collect(
        _ig_source(instagram={"login_user": "buyer1"}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "login_required"


def test_instagram_collector_skips_login_required_surfaced_during_iteration(monkeypatch):
    class LoginRequiredException(Exception):
        pass

    _patch(monkeypatch, hashtag_raises=LoginRequiredException("login required"))

    result = InstagramCollector().collect(
        _ig_source(instagram={"login_user": "buyer1"}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "login_required"


def test_instagram_collector_skips_unavailable_when_connection_error_during_iteration(monkeypatch):
    _patch(monkeypatch, hashtag_raises=ConnectionError("connection reset"))

    result = InstagramCollector().collect(
        _ig_source(instagram={"login_user": "buyer1"}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "instaloader_unavailable"


def test_instagram_collector_falls_back_to_started_at_when_no_date(monkeypatch):
    _patch(monkeypatch, hashtag_posts=[_post("abc", "caption")])
    started = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    result = InstagramCollector().collect(_ig_source(), started_at=started)

    assert result.items[0].published_at == started
    assert result.items[0].title == "caption"


def test_instagram_collector_report_safe_snippet_truncates_long_caption(monkeypatch):
    long_caption = "lead. " + ("detail " * 120) + "TAIL_MARKER"
    _patch(monkeypatch, hashtag_posts=[_post("abc", long_caption)])

    result = InstagramCollector().collect(
        _ig_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
    )

    assert "TAIL_MARKER" not in result.items[0].summary
    assert result.items[0].summary.endswith("...")
