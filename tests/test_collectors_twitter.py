from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.twitter import TwitterCollector
from fashion_radar.models.source import SourceDefinition, SourceType


def _completed(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _tweet(tid: str, text: str = "The Row Margaux on the runway", user: str = "fashionfeed"):
    return {
        "id": tid,
        "text": text,
        "created_at": "2026-06-11T08:00:00Z",
        "user": {"screen_name": user},
    }


def _x_source(**overrides):
    payload = {
        "name": "X",
        "type": SourceType.TWITTER,
        "query": "therow",
        "twitter": {"twitter_cli_path": "/fake/twitter"},
    }
    payload.update(overrides)
    return SourceDefinition(**payload)


def test_twitter_collector_parses_json_list_into_items():
    stdout = json.dumps(
        [_tweet("1", "The Row Margaux bag drops", "buyer1"), _tweet("2", "Ballet flats", "buyer2")]
    )
    captured = {}

    def runner(argv):
        captured["argv"] = argv
        return _completed(stdout=stdout)

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert "-n" in captured["argv"]
    assert captured["argv"][captured["argv"].index("-n") + 1] == "20"
    assert result.status.items_seen == 2
    assert result.items[0].url == "https://x.com/buyer1/status/1"
    assert result.items[0].title == "The Row Margaux bag drops"
    assert result.items[0].published_at == datetime(2026, 6, 11, 8, 0, tzinfo=UTC)


def test_twitter_collector_parses_tweets_wrapper_key():
    def runner(_argv):
        return _completed(stdout=json.dumps({"tweets": [_tweet("9", "wrapped", "u")]}))

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert [item.url for item in result.items] == ["https://x.com/u/status/9"]


def test_twitter_collector_skips_when_cli_missing(monkeypatch):
    monkeypatch.setattr("fashion_radar.collectors.twitter.shutil.which", lambda _name: None)

    result = TwitterCollector().collect(
        _x_source(twitter={"twitter_cli_path": None}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "twitter_cli_unavailable"


def test_twitter_collector_skips_login_required_on_auth_error_exit():
    def runner(_argv):
        return _completed(stdout="", stderr="error: login required (cookie expired)", returncode=1)

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "login_required"


def test_twitter_collector_skips_unavailable_on_other_error_exit():
    def runner(_argv):
        return _completed(stdout="", stderr="connection timeout", returncode=1)

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "twitter_cli_unavailable"


def test_twitter_collector_skips_unavailable_when_runner_raises():
    def runner(_argv):
        raise FileNotFoundError("twitter not executable")

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "twitter_cli_unavailable"


def test_twitter_collector_report_safe_snippet_and_fallbacks():
    long_text = "lead. " + ("detail " * 120) + "TAIL_MARKER"

    def runner(_argv):
        return _completed(
            stdout=json.dumps([{"id": "5", "text": long_text, "created_at": "not-a-date"}])
        )

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert "TAIL_MARKER" not in result.items[0].summary
    assert result.items[0].summary.endswith("...")
    assert result.items[0].published_at == datetime(2026, 6, 11, 12, 0, tzinfo=UTC)


def test_twitter_collector_uses_tweet_id_title_when_no_text():
    def runner(_argv):
        return _completed(stdout=json.dumps([{"id": "7"}]))

    result = TwitterCollector().collect(
        _x_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), runner=runner
    )

    assert result.items[0].title == "Tweet 7"
    assert result.items[0].url == "https://x.com/i/status/7"
