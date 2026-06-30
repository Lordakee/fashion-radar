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

SubprocessRunner = Callable[[list[str]], subprocess.CompletedProcess]


class YouTubeCollector:
    """Collector for ``youtube`` sources via the external ``yt-dlp`` CLI.

    Opt-in and use-at-your-own-risk. The user installs yt-dlp; Fashion Radar
    shells out to ``yt-dlp "ytsearch<N>:<query>" --dump-json`` and parses the
    per-line JSON metadata. Public data — no login/cookies needed. Fail-closed
    when yt-dlp is missing or errors. Provides no demand proof and no platform
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
        settings = source.youtube
        ytdlp_bin = settings.ytdlp_path or shutil.which("yt-dlp")
        if not ytdlp_bin:
            return _skipped(source, "ytdlp_unavailable", started_at)
        run = runner or _default_runner(source.http.timeout_seconds)
        search_target = f"{settings.search_prefix}{settings.max_videos_per_run}:{source.query}"
        argv = [ytdlp_bin, search_target, "--dump-json", "--no-warnings", "--skip-download"]
        try:
            completed = run(argv)
        except Exception:
            return _skipped(source, "ytdlp_unavailable", started_at)
        if completed.returncode != 0:
            return _skipped(source, "ytdlp_unavailable", started_at)
        videos = _parse_json_lines(completed.stdout)
        items: list[CollectedItem] = []
        for video in videos:
            mapped = _map_video(source, video, started_at)
            if mapped is not None:
                items.append(mapped)
        return CollectorResult.success(
            source, items=items, started_at=started_at, items_seen=len(videos)
        )


def _default_runner(timeout: float) -> SubprocessRunner:
    def _run(argv: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)

    return _run


def _skipped(source: SourceDefinition, reason: str, started_at: datetime) -> CollectorResult:
    return CollectorResult.skipped(source, reason=reason, started_at=started_at)


def _parse_json_lines(stdout: str | None) -> list[dict[str, Any]]:
    # yt-dlp --dump-json emits one JSON object per line; parse line-by-line,
    # skipping malformed lines (NOT a single json.loads blob like Twitter).
    if not stdout:
        return []
    videos: list[dict[str, Any]] = []
    for line in stdout.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            videos.append(parsed)
    return videos


def _map_video(
    source: SourceDefinition,
    video: dict[str, Any],
    started_at: datetime,
) -> CollectedItem | None:
    video_id = _first(video, ("id", "video_id"))
    if not video_id:
        return None
    title = _first(video, ("title",))
    url = (
        _first(video, ("webpage_url", "original_url"))
        or f"https://www.youtube.com/watch?v={video_id}"
    )
    description = _first(video, ("description", "description_text"))
    upload_date = _first(video, ("upload_date", "release_date", "timestamp"))
    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=url,
        title=title or f"YouTube video {video_id}",
        published_at=_upload_date(upload_date, started_at),
        summary=report_safe_snippet(description),
    )


def _first(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def _upload_date(raw: Any, fallback: datetime) -> datetime:
    # yt-dlp upload_date is a stable YYYYMMDD string; strptime first (not
    # parse_datetime_utc, which expects ISO8601 and fails on YYYYMMDD).
    if raw:
        try:
            return datetime.strptime(str(raw), "%Y%m%d").replace(tzinfo=UTC)
        except ValueError:
            pass
    return fallback
