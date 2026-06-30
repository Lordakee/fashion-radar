from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.youtube import YouTubeCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def _completed(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _video(
    vid: str,
    title: str = "The Row runway show",
    upload_date: str = "20260611",
    description: str = "Spring collection",
):
    return {
        "id": vid,
        "title": title,
        "upload_date": upload_date,
        "description": description,
        "webpage_url": f"https://www.youtube.com/watch?v={vid}",
    }


def _yt_source(**overrides):
    payload = {
        "name": "YT",
        "type": SourceType.YOUTUBE,
        "query": "fashion week",
        "youtube": {"ytdlp_path": "/fake/yt-dlp"},
    }
    payload.update(overrides)
    return SourceDefinition(**payload)


def test_youtube_collector_parses_json_lines_into_items():
    video_a = json.dumps(_video("abc", "The Row runway", "20260611", "Spring show"))
    video_b = json.dumps(_video("def", "Ballet flats", "20260610", "Flat review"))
    stdout = f"{video_a}\n{video_b}"
    captured = {}

    def runner(argv):
        captured["argv"] = argv
        return _completed(stdout=stdout)

    result = YouTubeCollector().collect(
        _yt_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert "ytsearch20:fashion week" in captured["argv"]
    assert result.items[0].url == "https://www.youtube.com/watch?v=abc"
    assert result.items[0].title == "The Row runway"
    assert result.items[0].published_at == datetime(2026, 6, 11, 0, 0, tzinfo=UTC)


def test_youtube_collector_uses_search_prefix_and_max():
    captured = {}

    def runner(argv):
        captured["argv"] = argv
        return _completed(stdout=json.dumps(_video("1")))

    YouTubeCollector().collect(
        _yt_source(
            youtube={
                "ytdlp_path": "/fake/yt-dlp",
                "max_videos_per_run": 5,
                "search_prefix": "ytsearchdate",
            }
        ),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
        runner=runner,
    )

    assert "ytsearchdate5:fashion week" in captured["argv"]


def test_youtube_collector_skips_malformed_json_lines():
    stdout = f"{json.dumps(_video('abc'))}\nnot-json-garbage\n{json.dumps(_video('def'))}"

    def runner(_argv):
        return _completed(stdout=stdout)

    result = YouTubeCollector().collect(
        _yt_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.items_seen == 2
    assert [item.url for item in result.items] == [
        "https://www.youtube.com/watch?v=abc",
        "https://www.youtube.com/watch?v=def",
    ]


def test_youtube_collector_skips_when_ytdlp_missing(monkeypatch):
    monkeypatch.setattr("fashion_radar.collectors.youtube.shutil.which", lambda _name: None)

    result = YouTubeCollector().collect(
        _yt_source(youtube={"ytdlp_path": None}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "ytdlp_unavailable"


def test_youtube_collector_skips_on_nonzero_exit():
    def runner(_argv):
        return _completed(stdout="", stderr="error", returncode=1)

    result = YouTubeCollector().collect(
        _yt_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "ytdlp_unavailable"


def test_youtube_collector_skips_when_runner_raises():
    def runner(_argv):
        raise FileNotFoundError("yt-dlp not found")

    result = YouTubeCollector().collect(
        _yt_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "ytdlp_unavailable"


def test_youtube_collector_upload_date_malformed_falls_back_to_started_at():
    started = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)

    for bad_date in ("20241399", "", None):
        video = {"id": "x", "upload_date": bad_date, "title": "T"}

        def runner(_argv, v=video):
            return _completed(stdout=json.dumps(v))

        result = YouTubeCollector().collect(_yt_source(), started_at=started, runner=runner)
        assert result.items[0].published_at == started, f"failed for upload_date={bad_date!r}"


def test_youtube_collector_report_safe_snippet_truncates_long_description():
    long_desc = "lead. " + ("detail " * 120) + "TAIL_MARKER"

    def runner(_argv):
        return _completed(stdout=json.dumps({"id": "z", "description": long_desc}))

    result = YouTubeCollector().collect(
        _yt_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert "TAIL_MARKER" not in result.items[0].summary
    assert result.items[0].summary.endswith("...")
