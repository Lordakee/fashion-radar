from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import report_safe_snippet
from fashion_radar.models.source import SourceDefinition
from fashion_radar.utils.dates import parse_datetime_utc

_TWEET_WRAPPER_KEYS = ("tweets", "data", "results", "statuses", "items")
_AUTH_KEYWORDS = (
    "login",
    "cookie",
    "auth",
    "401",
    "403",
    "unauthorized",
    "forbidden",
    "rate limit",
)

SubprocessRunner = Callable[[list[str]], subprocess.CompletedProcess]


class TwitterCollector:
    """Collector for ``twitter`` (X) sources via the external ``twitter-cli`` CLI.

    Opt-in and use-at-your-own-risk. The user installs twitter-cli and is logged
    into x.com in their browser (twitter-cli reads that cookie session); Fashion
    Radar only shells out to ``twitter search ... --json`` and parses the output
    — it never handles cookies/credentials. Fail-closed when the CLI is missing
    or reports an auth/connection error. Provides no demand proof and no platform
    coverage verification.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
        runner: SubprocessRunner | None = None,
    ) -> CollectorResult:
        started_at = started_at or datetime.now(tz=UTC)
        settings = source.twitter
        twitter_bin = settings.twitter_cli_path or shutil.which("twitter")
        if not twitter_bin:
            return _skipped(source, "twitter_cli_unavailable", started_at)
        run = runner or _default_runner(source.http.timeout_seconds)
        argv = [
            twitter_bin,
            "search",
            source.query,
            "-n",
            str(settings.max_tweets_per_run),
            "--json",
        ]
        try:
            completed = run(argv)
        except Exception:
            return _skipped(source, "twitter_cli_unavailable", started_at)
        if completed.returncode != 0:
            text = f"{completed.stdout or ''} {completed.stderr or ''}".lower()
            reason = (
                "login_required"
                if any(keyword in text for keyword in _AUTH_KEYWORDS)
                else "twitter_cli_unavailable"
            )
            return _skipped(source, reason, started_at)
        tweets = _coerce_tweets(completed.stdout)
        items: list[CollectedItem] = []
        for tweet in tweets:
            mapped = _map_tweet(source, tweet, started_at)
            if mapped is not None:
                items.append(mapped)
        return CollectorResult.success(
            source, items=items, started_at=started_at, items_seen=len(tweets)
        )


def _default_runner(timeout: float) -> SubprocessRunner:
    def _run(argv: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)

    return _run


def _skipped(source: SourceDefinition, reason: str, started_at: datetime) -> CollectorResult:
    return CollectorResult.skipped(source, reason=reason, started_at=started_at)


def _coerce_tweets(stdout: str | None) -> list[dict[str, Any]]:
    if not stdout or not stdout.strip():
        return []
    try:
        parsed = json.loads(stdout)
    except ValueError:
        return []
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if isinstance(parsed, dict):
        for key in _TWEET_WRAPPER_KEYS:
            value = parsed.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _map_tweet(
    source: SourceDefinition,
    tweet: dict[str, Any],
    started_at: datetime,
) -> CollectedItem | None:
    tweet_id = _first(tweet, ("id", "tweet_id", "status_id"))
    text = _first(tweet, ("text", "full_text", "content"))
    user = _user(tweet)
    if not tweet_id:
        return None
    url = _first(tweet, ("url", "link")) or (
        f"https://x.com/{user}/status/{tweet_id}" if user else f"https://x.com/i/status/{tweet_id}"
    )
    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=url,
        title=_title(text, tweet_id),
        published_at=_published_at(_first(tweet, ("created_at", "date", "time")), started_at),
        summary=report_safe_snippet(text),
    )


def _first(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def _user(tweet: dict[str, Any]) -> str | None:
    user = _first(tweet, ("user", "username", "screen_name"))
    if isinstance(user, dict):
        return _first(user, ("screen_name", "username", "handle")) or None  # type: ignore[arg-type]
    if isinstance(user, str):
        return user.lstrip("@")
    return None


def _title(text: Any, tweet_id: Any) -> str:
    if text:
        first = str(text).strip().splitlines()[0].strip()
        if first:
            return first[:200]
    return f"Tweet {tweet_id}"


def _published_at(raw: Any, fallback: datetime) -> datetime:
    if raw:
        try:
            dt = parse_datetime_utc(str(raw))
        except Exception:
            return fallback
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    return fallback
