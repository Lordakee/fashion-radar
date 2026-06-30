from __future__ import annotations

import itertools
from datetime import UTC, datetime
from typing import Any

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import report_safe_snippet
from fashion_radar.models.source import SourceDefinition
from fashion_radar.utils.dates import parse_datetime_utc

try:  # pragma: no cover - optional external dependency, user-installed
    import instaloader  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    instaloader = None  # type: ignore[assignment]


class InstagramCollector:
    """Collector for ``instagram`` sources via the user-installed ``instaloader`` library.

    Opt-in and use-at-your-own-risk. The user installs instaloader and creates a
    login session once (``instaloader --login=<user>``); Fashion Radar only
    reuses that session (``load_session_from_config``) and never handles
    passwords. Fail-closed when instaloader is missing, the session cannot be
    loaded, or a login/connection error surfaces during lazy post iteration
    (instaloader is lazy, so auth errors typically surface during iteration, not
    at session load). Provides no demand proof and no platform coverage
    verification.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        started_at = started_at or datetime.now(tz=UTC)
        if instaloader is None:
            return _skipped(source, "instaloader_unavailable", started_at)
        settings = source.instagram
        loader = instaloader.Instaloader()
        try:
            if settings.login_user:
                try:
                    loader.load_session_from_config(settings.login_user)
                except Exception:
                    return _skipped(source, "login_required", started_at)
            # instaloader is lazy: construction (from_name/from_username) and
            # iteration (get_all_posts/get_posts) can raise login/connection
            # errors. Force evaluation inside the try so they become skips.
            try:
                posts_iter = _iter_posts(loader, source)
                bounded = list(itertools.islice(posts_iter, settings.max_posts_per_run))
            except Exception as exc:
                return _skipped(source, _classify(exc), started_at)
            items: list[CollectedItem] = []
            for post in bounded:
                mapped = _map_post(source, post, started_at)
                if mapped is not None:
                    items.append(mapped)
            return CollectorResult.success(
                source,
                items=items,
                started_at=started_at,
                items_seen=len(bounded),
            )
        finally:
            close = getattr(loader, "close", None)
            if callable(close):
                close()


def _iter_posts(loader: Any, source: SourceDefinition):
    if source.instagram.target_type == "profile":
        profile = instaloader.Profile.from_username(loader.context, source.query)
        return profile.get_posts()
    tag_name = source.query.lstrip("#")
    hashtag = instaloader.Hashtag.from_name(loader.context, tag_name)
    # get_all_posts is the public iterator; fall back to get_posts on older APIs.
    if hasattr(hashtag, "get_all_posts"):
        return hashtag.get_all_posts()
    return hashtag.get_posts()


def _classify(exc: Exception) -> str:
    text = f"{type(exc).__name__} {exc}".lower()
    if any(
        keyword in text
        for keyword in ("login", "auth", "credential", "forbidden", "401", "private")
    ):
        return "login_required"
    return "instaloader_unavailable"


def _skipped(source: SourceDefinition, reason: str, started_at: datetime) -> CollectorResult:
    return CollectorResult.skipped(source, reason=reason, started_at=started_at)


def _map_post(
    source: SourceDefinition,
    post: Any,
    started_at: datetime,
) -> CollectedItem | None:
    shortcode = getattr(post, "shortcode", None)
    if not shortcode:
        return None
    caption = getattr(post, "caption", None)
    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=f"https://www.instagram.com/p/{shortcode}/",
        title=_title(caption, shortcode),
        published_at=_post_date(post, started_at),
        summary=report_safe_snippet(caption),
    )


def _title(caption: str | None, shortcode: str) -> str:
    if caption:
        first = caption.strip().splitlines()[0].strip()
        if first:
            return first[:200]
    return f"Instagram post {shortcode}"


def _post_date(post: Any, fallback: datetime) -> datetime:
    for attr in ("date_utc", "date"):
        value = getattr(post, attr, None)
        if value is not None:
            return _as_utc(value, fallback)
    return fallback


def _as_utc(value: Any, fallback: datetime) -> datetime:
    try:
        dt = value if isinstance(value, datetime) else parse_datetime_utc(str(value))
    except Exception:
        return fallback
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt
