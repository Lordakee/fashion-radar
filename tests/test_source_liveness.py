from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent
from time import struct_time

import pytest

from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.source_liveness import (
    SourceLivenessFinding,
    SourceLivenessFindingSeverity,
    SourceLivenessResult,
    SourceLivenessSeverity,
    SourceLivenessStatus,
    build_source_liveness_report,
    build_source_liveness_report_from_results,
    render_source_liveness_table,
    source_liveness_should_exit_nonzero,
)

FIXED_NOW = datetime(2026, 6, 24, 2, 0, tzinfo=UTC)


class FakeClient:
    def __init__(
        self,
        *,
        text: str = "",
        payload: object | None = None,
        error: Exception | None = None,
    ) -> None:
        self.text = text
        self.payload = payload if payload is not None else {}
        self.error = error
        self.calls: list[tuple[str, dict[str, str | int] | None]] = []
        self.closed = False

    def get_text(self, url: str, *, params: dict[str, str | int] | None = None) -> str:
        self.calls.append((url, params))
        if self.error is not None:
            raise self.error
        return self.text

    def get_json(self, url: str, *, params: dict[str, str | int] | None = None):
        self.calls.append((url, params))
        if self.error is not None:
            raise self.error
        return self.payload

    def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def forbid_default_network_client(monkeypatch: pytest.MonkeyPatch) -> None:
    from fashion_radar import source_liveness as source_liveness_module

    class NetworkGuardHttpClient:
        def __init__(self, *_args, **_kwargs) -> None:
            raise AssertionError("source-liveness tests must inject fake clients")

    monkeypatch.setattr(source_liveness_module, "FashionHttpClient", NetworkGuardHttpClient)


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def rss_item(
    title: str,
    *,
    published: str | None = None,
) -> str:
    published_xml = f"<pubDate>{published}</pubDate>" if published else ""
    slug = title.casefold().replace(" ", "-")
    return (
        f"<item><title>{title}</title><link>https://example.com/{slug}</link>{published_xml}</item>"
    )


def rss_feed(*items: str) -> str:
    return '<?xml version="1.0"?><rss version="2.0"><channel>' + "".join(items) + "</channel></rss>"


def atom_feed(
    *,
    published: str | None = None,
    updated: str | None = None,
) -> str:
    published_xml = f"<published>{published}</published>" if published else ""
    updated_xml = f"<updated>{updated}</updated>" if updated else ""
    feed_updated = updated or published or "2026-06-24T00:00:00Z"
    return (
        '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">'
        "<title>Test Feed</title><id>urn:test-feed</id>"
        f"<updated>{feed_updated}</updated>"
        "<entry><title>Atom Entry</title><id>urn:test-entry</id>"
        '<link href="https://example.com/atom-entry"/>'
        f"{published_xml}{updated_xml}"
        "</entry></feed>"
    )


def fixed_clock() -> datetime:
    return FIXED_NOW


def monotonic_sequence(values: list[float]):
    iterator = iter(values)
    return lambda: next(iterator)


def test_source_liveness_report_json_shape_is_stable(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Disabled Feed
            type: rss
            url: https://example.com/feed.xml
            enabled: false
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )

    report = build_source_liveness_report(path, clock=fixed_clock)
    payload = json.loads(report.model_dump_json())

    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "path",
        "checked_at",
        "source_count",
        "enabled_count",
        "disabled_count",
        "probed_count",
        "live_count",
        "degraded_count",
        "empty_count",
        "failed_count",
        "skipped_count",
        "type_counts",
        "tag_counts",
        "error_count",
        "warning_count",
        "info_count",
        "results",
        "findings",
        "boundaries",
    ]
    assert payload["contract_version"] == "source-liveness/v1"
    assert payload["execution_mode"] == "network_read_only"
    assert payload["path"] == str(path)
    assert payload["checked_at"] == "2026-06-24T02:00:00Z"
    assert payload["source_count"] == 1
    assert payload["enabled_count"] == 0
    assert payload["disabled_count"] == 1
    assert payload["probed_count"] == 0
    assert payload["skipped_count"] == 1
    assert payload["type_counts"] == {"rss": 1}
    assert payload["tag_counts"] == {"fashion_media": 1}
    assert list(payload["results"][0]) == [
        "source_name",
        "source_type",
        "enabled",
        "target_type",
        "target",
        "status",
        "severity",
        "code",
        "message",
        "checked_at",
        "elapsed_ms",
        "records_seen",
        "dated_records_seen",
        "latest_entry_at",
        "latest_entry_age_hours",
        "error_type",
    ]
    assert payload["results"][0]["dated_records_seen"] is None
    assert payload["results"][0]["latest_entry_at"] is None
    assert payload["results"][0]["latest_entry_age_hours"] is None
    assert payload["findings"] == []
    assert payload["boundaries"] == [
        (
            "Performs bounded network probes for configured RSS/RSSHub feeds and GDELT "
            "Doc API queries only."
        ),
        (
            "Does not collect, store, score, match, report, open SQLite, update source "
            "health, fetch article pages, or prove demand/coverage."
        ),
    ]


def test_disabled_sources_are_skipped_without_network_call(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Disabled Feed
            type: rss
            url: https://example.com/feed.xml
            enabled: false
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    calls: list[SourceDefinition] = []

    def client_factory(source: SourceDefinition, _settings):
        calls.append(source)
        return FakeClient()

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert calls == []
    assert report.skipped_count == 1
    assert report.info_count == 1
    assert report.results[0].status == SourceLivenessStatus.SKIPPED
    assert report.results[0].severity == SourceLivenessSeverity.INFO
    assert report.results[0].code == "source_disabled"
    assert report.results[0].elapsed_ms == 0


def test_invalid_source_config_returns_error_report_without_network_call(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken Feed
            type: rss
        """,
    )
    called = False

    def client_factory(_source: SourceDefinition, _settings):
        nonlocal called
        called = True
        return FakeClient()

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert called is False
    assert report.error_count == 1
    assert report.findings[0].severity == SourceLivenessFindingSeverity.ERROR
    assert report.findings[0].code == "invalid_config"
    assert "requires url" in report.findings[0].message
    assert report.results == []


def test_invalid_disabled_source_returns_invalid_config_instead_of_skipped_row(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken Disabled Feed
            type: rss
            enabled: false
            weight: 1.0
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    called = False

    def client_factory(_source: SourceDefinition, _settings):
        nonlocal called
        called = True
        return FakeClient()

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert called is False
    assert report.error_count == 1
    assert report.findings[0].code == "invalid_config"
    assert "requires url" in report.findings[0].message
    assert report.results == []


def test_source_liveness_rejects_invalid_stale_threshold_before_config_or_network(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing-sources.yaml"

    with pytest.raises(ValueError, match="stale_after_hours must be at least 1"):
        build_source_liveness_report(missing_path, stale_after_hours=0)


def test_render_source_liveness_table_includes_summary_rows_and_boundaries() -> None:
    result = SourceLivenessResult(
        source_name="Pipe | Feed",
        source_type=SourceType.RSS,
        enabled=True,
        target_type="url",
        target="https://example.com/feed.xml",
        status=SourceLivenessStatus.LIVE,
        severity=SourceLivenessSeverity.OK,
        code=None,
        message="Feed returned 2 entries.\nSecond line",
        checked_at=FIXED_NOW,
        elapsed_ms=25,
        records_seen=2,
        dated_records_seen=2,
        latest_entry_at=datetime(2026, 6, 24, 0, 0, tzinfo=UTC),
        latest_entry_age_hours=2,
        error_type=None,
    )
    report = build_source_liveness_report_from_results(
        path="sources.yaml",
        checked_at=FIXED_NOW,
        source_count=1,
        enabled_count=1,
        disabled_count=0,
        type_counts={"rss": 1},
        tag_counts={"fashion_media": 1},
        results=[result],
        findings=[],
    )

    lines = render_source_liveness_table(report)

    assert lines[:9] == [
        "Source liveness: sources.yaml",
        "Contract version: source-liveness/v1",
        "Execution mode: network_read_only",
        "Checked at: 2026-06-24T02:00:00+00:00",
        "Sources: 1 total, 1 enabled, 0 disabled, 1 probed",
        "Results: 1 live, 0 degraded, 0 empty, 0 failed, 0 skipped",
        "Types: rss=1",
        "Tags: fashion_media=1",
        "Findings: 0 errors, 0 warnings, 0 info",
    ]
    assert lines[9] == (
        "Source | Type | Status | Severity | Records | Dated | Latest age | Target | Message"
    )
    assert " | 2 | 2 | 2h | " in lines[10]
    assert "Pipe / Feed" in lines[10]
    assert "Feed returned 2 entries. Second line" in lines[10]
    assert "Boundaries:" in lines
    assert any("Does not collect, store" in line for line in lines)


def test_report_from_results_counts_mixed_statuses_and_findings() -> None:
    results = [
        SourceLivenessResult(
            source_name="Live Feed",
            source_type=SourceType.RSS,
            enabled=True,
            target_type="url",
            target="https://example.com/live.xml",
            status=SourceLivenessStatus.LIVE,
            severity=SourceLivenessSeverity.OK,
            message="Feed returned 1 entry.",
            checked_at=FIXED_NOW,
            elapsed_ms=10,
            records_seen=1,
        ),
        SourceLivenessResult(
            source_name="Degraded Feed",
            source_type=SourceType.RSS,
            enabled=True,
            target_type="url",
            target="https://example.com/degraded.xml",
            status=SourceLivenessStatus.DEGRADED,
            severity=SourceLivenessSeverity.WARNING,
            code="malformed_feed",
            message="Feed returned 1 entry with parser warnings.",
            checked_at=FIXED_NOW,
            elapsed_ms=10,
            records_seen=1,
        ),
        SourceLivenessResult(
            source_name="Empty GDELT",
            source_type=SourceType.GDELT,
            enabled=True,
            target_type="gdelt_query",
            target="fashion",
            status=SourceLivenessStatus.EMPTY,
            severity=SourceLivenessSeverity.WARNING,
            code="empty_gdelt_results",
            message="GDELT returned no articles.",
            checked_at=FIXED_NOW,
            elapsed_ms=10,
            records_seen=0,
        ),
        SourceLivenessResult(
            source_name="Broken Feed",
            source_type=SourceType.RSSHUB,
            enabled=True,
            target_type="url",
            target="https://rsshub.example.com/fashion",
            status=SourceLivenessStatus.FAILED,
            severity=SourceLivenessSeverity.ERROR,
            code="fetch_failed",
            message="GET failed.",
            checked_at=FIXED_NOW,
            elapsed_ms=10,
            error_type="RuntimeError",
        ),
        SourceLivenessResult(
            source_name="Disabled Feed",
            source_type=SourceType.RSS,
            enabled=False,
            target_type="url",
            target="https://example.com/disabled.xml",
            status=SourceLivenessStatus.SKIPPED,
            severity=SourceLivenessSeverity.INFO,
            code="source_disabled",
            message="Source is disabled.",
            checked_at=FIXED_NOW,
            elapsed_ms=0,
        ),
    ]

    report = build_source_liveness_report_from_results(
        path="sources.yaml",
        checked_at=FIXED_NOW,
        source_count=5,
        enabled_count=4,
        disabled_count=1,
        type_counts={"gdelt": 1, "rss": 3, "rsshub": 1},
        tag_counts={"fashion_media": 4, "gdelt": 1},
        results=results,
        findings=[
            SourceLivenessFinding(
                severity=SourceLivenessFindingSeverity.WARNING,
                code="report_warning",
                message="Report-level warning.",
            )
        ],
    )

    assert report.probed_count == 4
    assert report.live_count == 1
    assert report.degraded_count == 1
    assert report.empty_count == 1
    assert report.failed_count == 1
    assert report.skipped_count == 1
    assert report.error_count == 1
    assert report.warning_count == 3
    assert report.info_count == 1


def test_source_liveness_should_exit_nonzero_only_for_errors_or_strict_warnings() -> None:
    live = build_source_liveness_report_from_results(
        path="sources.yaml",
        checked_at=FIXED_NOW,
        source_count=0,
        enabled_count=0,
        disabled_count=0,
        type_counts={},
        tag_counts={},
        results=[],
        findings=[],
    )
    warning = live.model_copy(update={"warning_count": 1})
    error = live.model_copy(update={"error_count": 1})

    assert source_liveness_should_exit_nonzero(live, strict=False) is False
    assert source_liveness_should_exit_nonzero(warning, strict=False) is False
    assert source_liveness_should_exit_nonzero(warning, strict=True) is True
    assert source_liveness_should_exit_nonzero(error, strict=False) is True


def test_rss_liveness_reports_fresh_newest_entry_evidence(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(
        text=rss_feed(
            rss_item("Older", published="Mon, 22 Jun 2026 00:00:00 GMT"),
            rss_item("Newest", published="Wed, 24 Jun 2026 00:00:00 GMT"),
        )
    )

    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.LIVE
    assert result.severity == SourceLivenessSeverity.OK
    assert result.code is None
    assert result.dated_records_seen == 2
    assert result.latest_entry_at == datetime(2026, 6, 24, 0, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 2
    assert result.message == "Feed returned 2 entries; newest dated entry is 2 hours old."
    assert client.calls == [("https://example.com/feed.xml", None)]


def test_rss_liveness_uses_updated_timestamp_when_atom_publication_is_absent(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Atom Feed
            type: rss
            url: https://example.com/atom.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text=atom_feed(updated="2026-06-24T00:30:00Z"))

    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.LIVE
    assert result.severity == SourceLivenessSeverity.OK
    assert result.code is None
    assert result.dated_records_seen == 1
    assert result.latest_entry_at == datetime(2026, 6, 24, 0, 30, tzinfo=UTC)
    assert result.latest_entry_age_hours == 2


def test_rss_liveness_prefers_atom_publication_over_update_timestamp(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Atom Feed
            type: rss
            url: https://example.com/atom.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(
        text=atom_feed(
            published="2026-06-20T00:00:00Z",
            updated="2026-06-24T01:00:00Z",
        )
    )

    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.DEGRADED
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "stale_feed"
    assert result.dated_records_seen == 1
    assert result.latest_entry_at == datetime(2026, 6, 20, 0, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 98


def test_rss_liveness_marks_feed_beyond_threshold_degraded(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text=rss_feed(rss_item("Stale", published="Sat, 20 Jun 2026 00:00:00 GMT")))

    report = build_source_liveness_report(
        path,
        stale_after_hours=72,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.DEGRADED
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "stale_feed"
    assert result.latest_entry_age_hours == 98
    assert report.warning_count == 1
    assert source_liveness_should_exit_nonzero(report, strict=False) is False
    assert source_liveness_should_exit_nonzero(report, strict=True) is True


def test_rss_liveness_freshness_exact_threshold_and_one_second_over() -> None:
    from fashion_radar.source_liveness import _rss_freshness_evidence

    exact = _rss_freshness_evidence(
        [{"published_parsed": datetime(2026, 6, 21, 2, 0, tzinfo=UTC).utctimetuple()}],
        checked_at=FIXED_NOW,
        stale_after_hours=72,
    )
    one_second_over = _rss_freshness_evidence(
        [{"published_parsed": datetime(2026, 6, 21, 1, 59, 59, tzinfo=UTC).utctimetuple()}],
        checked_at=FIXED_NOW,
        stale_after_hours=72,
    )

    assert exact.stale is False
    assert exact.latest_entry_age_hours == 72
    assert one_second_over.stale is True
    assert one_second_over.latest_entry_age_hours == 73


def test_rss_liveness_custom_threshold_changes_same_entry_classification(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    feed_text = rss_feed(rss_item("Threshold", published="Mon, 22 Jun 2026 01:00:00 GMT"))
    default_client = FakeClient(text=feed_text)
    custom_client = FakeClient(text=feed_text)

    default_report = build_source_liveness_report(
        path,
        stale_after_hours=72,
        client_factory=lambda *_: default_client,
        clock=fixed_clock,
    )
    custom_report = build_source_liveness_report(
        path,
        stale_after_hours=48,
        client_factory=lambda *_: custom_client,
        clock=fixed_clock,
    )

    default_result = default_report.results[0]
    custom_result = custom_report.results[0]
    assert default_result.status == SourceLivenessStatus.LIVE
    assert default_result.severity == SourceLivenessSeverity.OK
    assert default_result.code is None
    assert default_result.latest_entry_age_hours == 49
    assert custom_result.status == SourceLivenessStatus.DEGRADED
    assert custom_result.severity == SourceLivenessSeverity.WARNING
    assert custom_result.code == "stale_feed"
    assert custom_result.latest_entry_age_hours == 49


def test_rss_liveness_no_date_feed_is_freshness_unknown(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text=rss_feed(rss_item("A"), rss_item("B")))

    report = build_source_liveness_report(
        path,
        client_factory=lambda _source, _settings: client,
        clock=fixed_clock,
        monotonic=monotonic_sequence([10.0, 10.025]),
    )

    assert client.closed is True
    assert report.live_count == 1
    assert report.info_count == 1
    result = report.results[0]
    assert result.status == SourceLivenessStatus.LIVE
    assert result.severity == SourceLivenessSeverity.INFO
    assert result.code == "freshness_unknown"
    assert result.elapsed_ms == 25
    assert result.records_seen == 2
    assert result.dated_records_seen == 0
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None
    assert result.message == (
        "Feed returned 2 entries; no parseable entry timestamps were available."
    )


@pytest.mark.filterwarnings("ignore:To avoid breaking existing software.*:DeprecationWarning")
def test_rss_liveness_ignores_invalid_timestamp_when_another_entry_is_valid(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(
        text=rss_feed(
            rss_item("Invalid", published="not-a-timestamp"),
            rss_item("Valid", published="Wed, 24 Jun 2026 00:00:00 GMT"),
        )
    )

    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.LIVE
    assert result.severity == SourceLivenessSeverity.OK
    assert result.code is None
    assert result.records_seen == 2
    assert result.dated_records_seen == 1
    assert result.latest_entry_at == datetime(2026, 6, 24, 0, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 2


def test_rss_liveness_freshness_falls_back_after_publication_conversion_error() -> None:
    from fashion_radar.source_liveness import _rss_freshness_evidence

    invalid_publication = struct_time((10**9, 1, 1, 0, 0, 0, 0, 1, -1))
    valid_update = datetime(2026, 6, 24, 0, 0, tzinfo=UTC).utctimetuple()

    evidence = _rss_freshness_evidence(
        [
            {
                "published_parsed": invalid_publication,
                "updated_parsed": valid_update,
            }
        ],
        checked_at=FIXED_NOW,
        stale_after_hours=72,
    )

    assert evidence.dated_records_seen == 1
    assert evidence.latest_entry_at == datetime(2026, 6, 24, 0, 0, tzinfo=UTC)
    assert evidence.latest_entry_age_hours == 2
    assert evidence.stale is False


def test_rss_liveness_clamps_future_entry_age_to_zero(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(
        text=rss_feed(rss_item("Future", published="Thu, 25 Jun 2026 02:00:00 GMT"))
    )

    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.LIVE
    assert result.severity == SourceLivenessSeverity.OK
    assert result.code is None
    assert result.latest_entry_at == datetime(2026, 6, 25, 2, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 0


def test_rss_liveness_empty_feed_is_warning(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Empty Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text="<?xml version='1.0'?><rss version='2.0'><channel></channel></rss>")

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.warning_count == 1
    result = report.results[0]
    assert result.status == SourceLivenessStatus.EMPTY
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "empty_feed"
    assert result.dated_records_seen == 0
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None


def test_rss_liveness_malformed_feed_with_entries_is_degraded_warning(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Degraded Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(
        text=("<rss><channel>" + rss_item("A", published="Sat, 20 Jun 2026 00:00:00 GMT"))
    )

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    result = report.results[0]
    assert result.status == SourceLivenessStatus.DEGRADED
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "malformed_feed"
    assert result.records_seen == 1
    assert result.dated_records_seen == 1
    assert result.latest_entry_at == datetime(2026, 6, 20, 0, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 98


def test_rss_liveness_malformed_feed_without_dates_renders_latest_age_na(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Degraded Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text="<rss><channel>" + rss_item("A"))

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    result = report.results[0]
    assert result.status == SourceLivenessStatus.DEGRADED
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "malformed_feed"
    assert result.records_seen == 1
    assert result.dated_records_seen == 0

    lines = render_source_liveness_table(report)
    result_row = lines[10].split(" | ")
    assert result_row[6] == "n/a"
    assert "unknown" not in result_row


def test_rss_liveness_malformed_empty_feed_leaves_freshness_fields_unset(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Malformed Empty Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text="<rss><channel>")

    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.FAILED
    assert result.severity == SourceLivenessSeverity.ERROR
    assert result.code == "malformed_feed"
    assert result.records_seen == 0
    assert result.dated_records_seen is None
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None


def test_rss_liveness_http_fetch_error_is_failed_error_without_traceback(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(error=RuntimeError("feed timeout"))

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.error_count == 1
    assert client.closed is True
    assert report.results[0].status == SourceLivenessStatus.FAILED
    assert report.results[0].error_type == "RuntimeError"
    assert "feed timeout" in report.results[0].message
    assert "Traceback" not in report.results[0].message


def test_rss_liveness_parses_fetched_text_without_dereferencing_path_text(
    tmp_path: Path,
) -> None:
    fetched_path = tmp_path / "side-channel-feed.xml"
    fetched_path.write_text(
        """<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item></channel></rss>""",
        encoding="utf-8",
    )
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    client = FakeClient(text=str(fetched_path))

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.live_count == 0
    assert report.failed_count == 1
    assert report.results[0].status == SourceLivenessStatus.FAILED
    assert report.results[0].records_seen == 0


def test_rss_liveness_passes_source_http_settings_to_client_factory(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSS Feed
            type: rss
            url: https://example.com/feed.xml
            tags: [fashion_media]
            http:
              per_domain_delay_seconds: 0.25
            article:
              enabled: false
        """,
    )
    seen_settings = []

    def client_factory(_source: SourceDefinition, settings):
        seen_settings.append(settings)
        return FakeClient(
            text="""<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item></channel></rss>"""
        )

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert report.live_count == 1
    assert seen_settings[0].per_domain_delay_seconds == 0.25


def test_rsshub_liveness_uses_rss_freshness_classification(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: RSSHub Feed
            type: rsshub
            url: https://rsshub.example.com/fashion
            tags: [rsshub]
            article:
              enabled: false
        """,
    )
    client = FakeClient(
        text=rss_feed(rss_item("Stale RSSHub", published="Sat, 20 Jun 2026 00:00:00 GMT"))
    )

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    result = report.results[0]
    assert report.degraded_count == 1
    assert result.source_type == SourceType.RSSHUB
    assert result.target_type == "url"
    assert result.status == SourceLivenessStatus.DEGRADED
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "stale_feed"
    assert result.dated_records_seen == 1
    assert result.latest_entry_at == datetime(2026, 6, 20, 0, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 98


def test_gdelt_liveness_uses_query_timespan_format_and_maxrecords_one(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Luxury
            type: gdelt
            query: luxury fashion
            tags: [gdelt, luxury]
            gdelt:
              lookback_hours: 12
              max_records: 100
              rate_limit_per_second: 1.0
        """,
    )
    client = FakeClient(payload={"articles": [{"title": "A"}]})

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.live_count == 1
    assert client.calls[0][1] == {
        "query": "luxury fashion",
        "mode": "artlist",
        "format": "json",
        "timespan": "12h",
        "maxrecords": 1,
    }
    result = report.results[0]
    assert result.target_type == "gdelt_query"
    assert result.dated_records_seen is None
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None


def test_gdelt_liveness_passes_gdelt_http_settings_to_client_factory(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Luxury
            type: gdelt
            query: luxury fashion
            tags: [gdelt]
            http:
              per_domain_delay_seconds: 0
            gdelt:
              rate_limit_per_second: 0.5
              lookback_hours: 12
        """,
    )
    seen_settings = []

    def client_factory(_source: SourceDefinition, settings):
        seen_settings.append(settings)
        return FakeClient(payload={"articles": [{"title": "A"}]})

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert report.live_count == 1
    assert seen_settings[0].per_domain_delay_seconds == 2.0


def test_gdelt_liveness_empty_articles_is_warning(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Empty GDELT
            type: gdelt
            query: luxury fashion
            tags: [gdelt]
        """,
    )
    client = FakeClient(payload={"articles": []})

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.warning_count == 1
    result = report.results[0]
    assert result.status == SourceLivenessStatus.EMPTY
    assert result.code == "empty_gdelt_results"
    assert result.dated_records_seen is None
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None


def test_gdelt_liveness_invalid_payload_is_failed_error(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken GDELT
            type: gdelt
            query: luxury fashion
            tags: [gdelt]
        """,
    )
    client = FakeClient(payload={"unexpected": []})

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.error_count == 1
    result = report.results[0]
    assert result.status == SourceLivenessStatus.FAILED
    assert result.code == "invalid_gdelt_payload"
    assert result.dated_records_seen is None
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None


def test_gdelt_liveness_fetch_error_is_failed_error(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken GDELT
            type: gdelt
            query: luxury fashion
            tags: [gdelt]
        """,
    )
    client = FakeClient(error=RuntimeError("gdelt timeout"))

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.error_count == 1
    assert client.closed is True
    result = report.results[0]
    assert result.status == SourceLivenessStatus.FAILED
    assert result.error_type == "RuntimeError"
    assert result.dated_records_seen is None
    assert result.latest_entry_at is None
    assert result.latest_entry_age_hours is None
    assert "gdelt timeout" in result.message


def test_liveness_probe_order_matches_config_and_failures_do_not_abort_later_sources(
    tmp_path: Path,
) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Broken Feed
            type: rss
            url: https://example.com/broken.xml
            tags: [fashion_media]
            article:
              enabled: false
          - name: Disabled Feed
            type: rss
            url: https://example.com/disabled.xml
            enabled: false
            tags: [fashion_media]
            article:
              enabled: false
          - name: Live Feed
            type: rss
            url: https://example.com/live.xml
            tags: [fashion_media]
            article:
              enabled: false
        """,
    )
    clients = [
        FakeClient(error=RuntimeError("first source failed")),
        FakeClient(
            text="""<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item></channel></rss>"""
        ),
    ]
    requested_sources: list[str] = []

    def client_factory(source: SourceDefinition, _settings):
        requested_sources.append(source.name)
        return clients.pop(0)

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert requested_sources == ["Broken Feed", "Live Feed"]
    assert [result.source_name for result in report.results] == [
        "Broken Feed",
        "Disabled Feed",
        "Live Feed",
    ]
    assert report.results[0].status == SourceLivenessStatus.FAILED
    assert report.results[1].status == SourceLivenessStatus.SKIPPED
    assert report.results[2].status == SourceLivenessStatus.LIVE
