# Stage 190 Source Liveness Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only `source-liveness` CLI command that probes configured RSS/RSSHub and GDELT sources without collecting, storing, scoring, or writing artifacts.

**Architecture:** Introduce a focused `fashion_radar.source_liveness` module with Pydantic contracts, injected HTTP-client seams, RSS/GDELT probe helpers, table rendering, and exit-code helper. Wire a flat Typer command next to `source-pack-lint`, then document it as live network diagnostics while preserving `source-pack-lint` as offline YAML linting.

**Tech Stack:** Python 3.11, Pydantic, Typer, feedparser, existing `FashionHttpClient`, existing source config loader, pytest with fake clients, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Create: `src/fashion_radar/source_liveness.py`
- Create: `tests/test_source_liveness.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-packs.md`
- Modify: `docs/source-pack-quality.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_source_packs_docs.py`
- Modify: `tests/test_source_pack_quality_docs.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`
- Add: `docs/superpowers/specs/2026-06-24-stage-190-source-liveness-diagnostics-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md`
- Add: `docs/reviews/opencode-stage-190-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-190-plan-review.md`
- Add after plan fix: `docs/reviews/opencode-stage-190-plan-rereview-prompt.md`
- Add after plan fix: `docs/reviews/opencode-stage-190-plan-rereview.md`
- Add after subagent plan audit: `docs/reviews/opencode-stage-190-plan-rereview-2-prompt.md`
- Add after subagent plan audit: `docs/reviews/opencode-stage-190-plan-rereview-2.md`
- Add after implementation: `docs/reviews/opencode-stage-190-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-190-code-review.md`
- Add after code review fixes: `docs/reviews/opencode-stage-190-code-rereview-prompt.md`
- Add after code review fixes: `docs/reviews/opencode-stage-190-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-190-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-190-release-review.md`
- Add after release review fixes: `docs/reviews/opencode-stage-190-release-rereview-prompt.md`
- Add after release review fixes: `docs/reviews/opencode-stage-190-release-rereview.md`

## Task 1: Core Contracts, Counts, And Renderer

**Files:**

- Create: `src/fashion_radar/source_liveness.py`
- Create: `tests/test_source_liveness.py`

- [ ] **Step 1: Add RED tests for stable JSON shape, counts, valid disabled skips, invalid config, renderer, and exit helper**

Create `tests/test_source_liveness.py` with this initial test scaffold:

```python
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

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
    def __init__(self, *, text: str = "", payload: object | None = None, error: Exception | None = None):
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

    monkeypatch.setattr(
        source_liveness_module,
        "FashionHttpClient",
        NetworkGuardHttpClient,
        raising=False,
    )


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


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
    assert payload["findings"] == []
    assert payload["boundaries"] == [
        "Performs bounded network probes for configured RSS/RSSHub feeds and GDELT Doc API queries only.",
        "Does not collect, store, score, match, report, open SQLite, update source health, fetch article pages, or prove demand/coverage.",
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


def test_invalid_disabled_source_returns_invalid_config_instead_of_skipped_row(tmp_path: Path) -> None:
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
```

The test references `build_source_liveness_report_from_results(...)`; the first
implementation step should expose this helper from `source_liveness.py` for
deterministic renderer tests.

- [ ] **Step 2: Verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_liveness.py -q
```

Expected: import failure because `fashion_radar.source_liveness` does not exist.

- [ ] **Step 3: Implement contracts and non-network report assembly**

Create `src/fashion_radar/source_liveness.py` with:

```python
from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.lint_formatting import format_finding_counts
from fashion_radar.models.source import HttpSourceSettings, SourceDefinition, SourceType
from fashion_radar.settings import ConfigError, load_source_config

SOURCE_LIVENESS_CONTRACT_VERSION = "source-liveness/v1"
SOURCE_LIVENESS_EXECUTION_MODE = "network_read_only"
SOURCE_LIVENESS_BOUNDARIES = [
    "Performs bounded network probes for configured RSS/RSSHub feeds and GDELT Doc API queries only.",
    "Does not collect, store, score, match, report, open SQLite, update source health, fetch article pages, or prove demand/coverage.",
]


class SourceLivenessStatus(StrEnum):
    LIVE = "live"
    DEGRADED = "degraded"
    EMPTY = "empty"
    FAILED = "failed"
    SKIPPED = "skipped"


class SourceLivenessSeverity(StrEnum):
    OK = "ok"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SourceLivenessFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SourceLivenessFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: SourceLivenessFindingSeverity
    code: str
    message: str


class SourceLivenessResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    source_type: SourceType
    enabled: bool
    target_type: Literal["url", "gdelt_query"]
    target: str
    status: SourceLivenessStatus
    severity: SourceLivenessSeverity
    code: str | None = None
    message: str
    checked_at: datetime
    elapsed_ms: int
    records_seen: int | None = None
    error_type: str | None = None


class SourceLivenessReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = SOURCE_LIVENESS_CONTRACT_VERSION
    execution_mode: Literal["network_read_only"] = SOURCE_LIVENESS_EXECUTION_MODE
    path: str
    checked_at: datetime
    source_count: int = 0
    enabled_count: int = 0
    disabled_count: int = 0
    probed_count: int = 0
    live_count: int = 0
    degraded_count: int = 0
    empty_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    type_counts: dict[str, int] = Field(default_factory=dict)
    tag_counts: dict[str, int] = Field(default_factory=dict)
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    results: list[SourceLivenessResult] = Field(default_factory=list)
    findings: list[SourceLivenessFinding] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=lambda: list(SOURCE_LIVENESS_BOUNDARIES))


class HttpProbeClient(Protocol):
    def get_text(self, url: str, *, params: dict[str, str | int] | None = None) -> str: ...
    def get_json(self, url: str, *, params: dict[str, str | int] | None = None) -> Any: ...
    def close(self) -> None: ...


SourceHttpClientFactory = Callable[[SourceDefinition, HttpSourceSettings], HttpProbeClient]


def build_source_liveness_report(
    path: Path,
    *,
    client_factory: SourceHttpClientFactory | None = None,
    clock: Callable[[], datetime] | None = None,
    monotonic: Callable[[], float] | None = None,
) -> SourceLivenessReport:
    checked_at = _checked_at(clock)
    try:
        config = load_source_config(path)
    except ConfigError as exc:
        return build_source_liveness_report_from_results(
            path=str(path),
            checked_at=checked_at,
            source_count=0,
            enabled_count=0,
            disabled_count=0,
            type_counts={},
            tag_counts={},
            results=[],
            findings=[
                SourceLivenessFinding(
                    severity=SourceLivenessFindingSeverity.ERROR,
                    code="invalid_config",
                    message=str(exc),
                )
            ],
        )

    results = [_skipped_result(source, checked_at) for source in config.sources if not source.enabled]
    return build_source_liveness_report_from_results(
        path=str(path),
        checked_at=checked_at,
        source_count=len(config.sources),
        enabled_count=sum(1 for source in config.sources if source.enabled),
        disabled_count=sum(1 for source in config.sources if not source.enabled),
        type_counts=Counter(source.type.value for source in config.sources),
        tag_counts=Counter(tag for source in config.sources for tag in source.tags),
        results=results,
        findings=[],
    )


def build_source_liveness_report_from_results(
    *,
    path: str,
    checked_at: datetime,
    source_count: int,
    enabled_count: int,
    disabled_count: int,
    type_counts: dict[str, int] | Counter[str],
    tag_counts: dict[str, int] | Counter[str],
    results: Sequence[SourceLivenessResult],
    findings: Sequence[SourceLivenessFinding],
) -> SourceLivenessReport:
    result_list = list(results)
    finding_list = list(findings)
    return SourceLivenessReport(
        path=path,
        checked_at=checked_at,
        source_count=source_count,
        enabled_count=enabled_count,
        disabled_count=disabled_count,
        probed_count=sum(1 for result in result_list if result.enabled),
        live_count=_count_status(result_list, SourceLivenessStatus.LIVE),
        degraded_count=_count_status(result_list, SourceLivenessStatus.DEGRADED),
        empty_count=_count_status(result_list, SourceLivenessStatus.EMPTY),
        failed_count=_count_status(result_list, SourceLivenessStatus.FAILED),
        skipped_count=_count_status(result_list, SourceLivenessStatus.SKIPPED),
        type_counts=dict(sorted(type_counts.items())),
        tag_counts=dict(sorted(tag_counts.items())),
        error_count=_count_severity(result_list, SourceLivenessSeverity.ERROR)
        + _count_findings(finding_list, SourceLivenessFindingSeverity.ERROR),
        warning_count=_count_severity(result_list, SourceLivenessSeverity.WARNING)
        + _count_findings(finding_list, SourceLivenessFindingSeverity.WARNING),
        info_count=_count_severity(result_list, SourceLivenessSeverity.INFO)
        + _count_findings(finding_list, SourceLivenessFindingSeverity.INFO),
        results=result_list,
        findings=finding_list,
    )
```

Then add private helpers `_checked_at`, `_skipped_result`, `_count_status`,
`_count_severity`, `_count_findings`, `_format_counts`, `_sanitize_cell`,
`render_source_liveness_table(...)`, and
`source_liveness_should_exit_nonzero(...)` following the renderer expectations
from the tests.

- [ ] **Step 4: Verify GREEN for Task 1**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_liveness.py -q
uv --no-config run --frozen ruff check src/fashion_radar/source_liveness.py tests/test_source_liveness.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_liveness.py tests/test_source_liveness.py
```

Expected: all Task 1 tests and checks pass.

## Task 2: RSS And GDELT Probe Behavior

**Files:**

- Modify: `src/fashion_radar/source_liveness.py`
- Modify: `tests/test_source_liveness.py`

- [ ] **Step 1: Add RED probe tests**

Append tests covering:

```python
def test_rss_liveness_live_feed_counts_entries_from_fixture(tmp_path: Path) -> None:
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
        text=\"\"\"<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item><item><title>B</title><link>https://example.com/b</link></item></channel></rss>\"\"\"
    )

    report = build_source_liveness_report(
        path,
        client_factory=lambda _source, _settings: client,
        clock=fixed_clock,
        monotonic=monotonic_sequence([10.0, 10.025]),
    )

    assert client.closed is True
    assert report.live_count == 1
    assert report.results[0].elapsed_ms == 25
    assert report.results[0].records_seen == 2
    assert report.results[0].message == "Feed returned 2 entries."


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
    assert report.results[0].status == SourceLivenessStatus.EMPTY
    assert report.results[0].code == "empty_feed"


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
    client = FakeClient(text="<rss><channel><item><title>A</title><link>https://example.com/a</link></item>")

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.results[0].status == SourceLivenessStatus.DEGRADED
    assert report.results[0].severity == SourceLivenessSeverity.WARNING
    assert report.results[0].records_seen == 1


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
```

Add RSS/RSSHub settings and parity tests:

```python
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
            text=\"\"\"<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item></channel></rss>\"\"\"
        )

    report = build_source_liveness_report(path, client_factory=client_factory, clock=fixed_clock)

    assert report.live_count == 1
    assert seen_settings[0].per_domain_delay_seconds == 0.25


def test_rsshub_liveness_is_probed_like_rss(tmp_path: Path) -> None:
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
        text=\"\"\"<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item></channel></rss>\"\"\"
    )

    report = build_source_liveness_report(path, client_factory=lambda *_: client, clock=fixed_clock)

    assert report.live_count == 1
    assert report.results[0].source_type == SourceType.RSSHUB
    assert report.results[0].target_type == "url"
```

Add GDELT tests:

```python
def test_gdelt_liveness_uses_query_timespan_format_and_maxrecords_one(tmp_path: Path) -> None:
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
    assert report.results[0].target_type == "gdelt_query"


def test_gdelt_liveness_passes_gdelt_http_settings_to_client_factory(tmp_path: Path) -> None:
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
    assert report.results[0].status == SourceLivenessStatus.EMPTY
    assert report.results[0].code == "empty_gdelt_results"


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
    assert report.results[0].status == SourceLivenessStatus.FAILED
    assert report.results[0].code == "invalid_gdelt_payload"


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
            text=\"\"\"<?xml version="1.0"?><rss version="2.0"><channel><item><title>A</title><link>https://example.com/a</link></item></channel></rss>\"\"\"
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
```

- [ ] **Step 2: Verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_liveness.py -q
```

Expected: probe tests fail because enabled sources are not probed yet.

- [ ] **Step 3: Implement RSS/GDELT probes**

Update `source_liveness.py`:

- Import `feedparser`, `GDELT_DOC_API`, `gdelt_http_settings`, and
  `FashionHttpClient`.
- Add `_default_client_factory(...)`.
- In `build_source_liveness_report(...)`, for each source:
  - disabled -> `_skipped_result(...)`;
  - enabled RSS/RSSHUB -> `_probe_rss_source(...)`;
  - enabled GDELT -> `_probe_gdelt_source(...)`.
- Preserve result order from the source config and continue probing later
  sources after one source fails.
- Only schema-valid disabled sources can become skipped rows because
  `load_source_config(...)` validates the entire file before per-source
  iteration.
- Use `monotonic` to compute `elapsed_ms`; default to `time.monotonic`.
- Always close clients in `finally`.
- Convert exceptions to `failed` rows with `error_type=type(exc).__name__`.
- For RSS/RSSHub, pass `source.http` to `client_factory(...)`.
- For GDELT, pass `gdelt_http_settings(source)` to `client_factory(...)`. This
  intentionally mirrors existing per-source collector client behavior and does
  not implement command-global GDELT pacing in v1.

Implement `_gdelt_liveness_params(source)` with `maxrecords: 1`.

- [ ] **Step 4: Verify GREEN for Task 2**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest tests/test_source_liveness.py -q
uv --no-config run --frozen ruff check src/fashion_radar/source_liveness.py tests/test_source_liveness.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_liveness.py tests/test_source_liveness.py
```

Expected: all source-liveness tests pass under synthetic proxy because fake
clients are injected.

## Task 3: CLI Integration

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add RED CLI tests**

In `tests/test_cli.py`, near `source-pack-lint` tests, add:

```python
def test_source_liveness_help_lists_format_strict_and_network_read_only() -> None:
    result = CliRunner().invoke(app, ["source-liveness", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--strict" in result.output
    assert "bounded network probes" in result.output


def test_source_liveness_prints_json_from_builder(monkeypatch, tmp_path: Path) -> None:
    from fashion_radar import cli as cli_module
    from fashion_radar.source_liveness import build_source_liveness_report_from_results

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    report = build_source_liveness_report_from_results(
        path=str(path),
        checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC),
        source_count=0,
        enabled_count=0,
        disabled_count=0,
        type_counts={},
        tag_counts={},
        results=[],
        findings=[],
    )
    monkeypatch.setattr(cli_module, "build_source_liveness_report", lambda path: report)

    result = CliRunner().invoke(app, ["source-liveness", str(path), "--format", "json"])

    assert result.exit_code == 0
    assert json.loads(result.output)["contract_version"] == "source-liveness/v1"


def test_source_liveness_default_table_uses_renderer_output(monkeypatch, tmp_path: Path) -> None:
    from fashion_radar import cli as cli_module
    from fashion_radar.models.source import SourceType
    from fashion_radar.source_liveness import (
        SourceLivenessResult,
        SourceLivenessSeverity,
        SourceLivenessStatus,
        build_source_liveness_report_from_results,
    )

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    report = build_source_liveness_report_from_results(
        path=str(path),
        checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC),
        source_count=1,
        enabled_count=1,
        disabled_count=0,
        type_counts={"rss": 1},
        tag_counts={"fashion_media": 1},
        results=[
            SourceLivenessResult(
                source_name="Designer Feed",
                source_type=SourceType.RSS,
                enabled=True,
                target_type="url",
                target="https://example.com/feed.xml",
                status=SourceLivenessStatus.LIVE,
                severity=SourceLivenessSeverity.OK,
                message="Feed returned 1 entry.",
                checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC),
                elapsed_ms=20,
                records_seen=1,
            )
        ],
        findings=[],
    )
    monkeypatch.setattr(cli_module, "build_source_liveness_report", lambda path: report)

    result = CliRunner().invoke(app, ["source-liveness", str(path)])

    assert result.exit_code == 0
    assert "Sources: 1 total, 1 enabled, 0 disabled, 1 probed" in result.output
    assert "Designer Feed" in result.output
    assert "Boundaries:" in result.output
    assert "Does not collect, store" in result.output


def test_source_liveness_warning_only_exits_one_with_strict_but_prints_output(monkeypatch, tmp_path: Path) -> None:
    from fashion_radar import cli as cli_module
    from fashion_radar.source_liveness import SourceLivenessReport

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    report = SourceLivenessReport(
        path=str(path),
        checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC),
        warning_count=1,
    )
    monkeypatch.setattr(cli_module, "build_source_liveness_report", lambda path: report)

    result = CliRunner().invoke(app, ["source-liveness", str(path), "--strict"])

    assert result.exit_code == 1
    assert "Source liveness:" in result.output


def test_source_liveness_warning_only_exits_zero_without_strict(monkeypatch, tmp_path: Path) -> None:
    from fashion_radar import cli as cli_module
    from fashion_radar.source_liveness import SourceLivenessReport

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    report = SourceLivenessReport(
        path=str(path),
        checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC),
        warning_count=1,
    )
    monkeypatch.setattr(cli_module, "build_source_liveness_report", lambda path: report)

    result = CliRunner().invoke(app, ["source-liveness", str(path)])

    assert result.exit_code == 0
    assert "Source liveness:" in result.output


def test_source_liveness_error_exits_one_but_prints_output(monkeypatch, tmp_path: Path) -> None:
    from fashion_radar import cli as cli_module
    from fashion_radar.source_liveness import SourceLivenessReport

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    report = SourceLivenessReport(
        path=str(path),
        checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC),
        error_count=1,
    )
    monkeypatch.setattr(cli_module, "build_source_liveness_report", lambda path: report)

    result = CliRunner().invoke(app, ["source-liveness", str(path)])

    assert result.exit_code == 1
    assert "Source liveness:" in result.output


def test_source_liveness_invalid_format_does_not_call_builder(monkeypatch, tmp_path: Path) -> None:
    from fashion_radar import cli as cli_module

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    called = False

    def fail_if_called(path: Path):
        nonlocal called
        called = True
        raise AssertionError("builder should not be called")

    monkeypatch.setattr(cli_module, "build_source_liveness_report", fail_if_called)

    result = CliRunner().invoke(app, ["source-liveness", str(path), "--format", "xml"])

    assert result.exit_code != 0
    assert called is False


def test_source_liveness_does_not_create_config_data_report_or_workflow_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar import cli as cli_module
    from fashion_radar.source_liveness import SourceLivenessReport

    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    explicit_config = tmp_path / "explicit-config"
    explicit_data = tmp_path / "explicit-data"
    explicit_reports = tmp_path / "explicit-reports"
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(
        cli_module,
        "build_source_liveness_report",
        lambda path: SourceLivenessReport(path=str(path), checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC)),
    )

    result = CliRunner().invoke(
        app,
        ["source-liveness", str(path)],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(explicit_config),
            "FASHION_RADAR_DATA_DIR": str(explicit_data),
            "FASHION_RADAR_REPORTS_DIR": str(explicit_reports),
        },
    )

    assert result.exit_code == 0
    assert not (workdir / "config").exists()
    assert not (workdir / "configs").exists()
    assert not (workdir / "data").exists()
    assert not (workdir / "reports").exists()
    assert not explicit_config.exists()
    assert not explicit_data.exists()
    assert not explicit_reports.exists()
    artifact_names = {artifact.name for artifact in workdir.rglob("*")}
    assert "fashion-radar.sqlite" not in artifact_names
    assert not any(artifact.match("*.sqlite*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("collector-*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("collector_runs*") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("fashion-radar-*.md") for artifact in workdir.rglob("*"))
    assert not any(artifact.match("fashion-radar-*.json") for artifact in workdir.rglob("*"))
    assert not (workdir / "latest.md").exists()
    assert not (workdir / "latest.json").exists()
    assert not (workdir / "report-index.json").exists()
```

- [ ] **Step 2: Verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_liveness"
```

Expected: command is missing or imports fail.

- [ ] **Step 3: Wire CLI**

In `src/fashion_radar/cli.py`:

- import `build_source_liveness_report`,
  `render_source_liveness_table`, and
  `source_liveness_should_exit_nonzero`;
- add `SourceLivenessOutputFormat = Literal["table", "json"]`;
- add `SOURCE_LIVENESS_FORMAT_OPTION = typer.Option("table", "--format", help="Output format.")`;
- add:

```python
@app.command(name="source-liveness")
def source_liveness_command(
    path: Path,
    output_format: SourceLivenessOutputFormat = SOURCE_LIVENESS_FORMAT_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Check configured source liveness with bounded network probes and no writes."""
    report = build_source_liveness_report(path)
    if output_format == "json":
        typer.echo(report.model_dump_json(indent=2))
    else:
        for line in render_source_liveness_table(report):
            typer.echo(line)
    if source_liveness_should_exit_nonzero(report, strict=strict):
        raise typer.Exit(1)
```

- [ ] **Step 4: Verify GREEN for CLI**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_liveness or source_pack_lint"
uv --no-config run --frozen ruff check src/fashion_radar/cli.py tests/test_cli.py
uv --no-config run --frozen ruff format --check src/fashion_radar/cli.py tests/test_cli.py
```

Expected: CLI tests and checks pass.

## Task 4: Documentation

**Files:**

- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-packs.md`
- Modify: `docs/source-pack-quality.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_source_packs_docs.py`
- Modify: `tests/test_source_pack_quality_docs.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add RED docs tests**

Add focused phrase assertions:

- `tests/test_source_packs_docs.py`: require
  `uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml`
  and `--format json` in `docs/source-packs.md`.
- `tests/test_source_pack_quality_docs.py`: require the Limits section to say
  `source-pack-lint` does not fetch sources and that live checks belong to
  `source-liveness`.
- `tests/test_cli_docs.py`: require `docs/cli-reference.md` to list
  `source-liveness` with "bounded network probes" and "no writes".
- `tests/test_cli_docs.py`: require README to mention `source-liveness` and
  `configs/source-packs/fashion-public.example.yaml`.
- `tests/test_cli_docs.py`: require `docs/architecture.md` to mention
  `Source Liveness`, `RSS/RSSHub`, and `GDELT`.

- [ ] **Step 2: Verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q
```

Expected: the new source-liveness phrase tests fail.

- [ ] **Step 3: Update docs**

Add concise docs:

- README source-pack area: one command example for `source-liveness`.
- `docs/source-packs.md`: `## Check Source Liveness` section after pack lint.
- `docs/source-pack-quality.md`: keep lint offline wording and link live checks
  to `source-liveness`.
- `docs/architecture.md`: add `Source Liveness` component near
  `Source-Pack Quality`.
- `docs/cli-reference.md`: add `source-liveness PATH`.
- `CHANGELOG.md`: add Stage 190 under `### Added`.

Do not add long external/social boundary blocks.

- [ ] **Step 4: Verify docs GREEN**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q
```

Expected: docs tests pass.

## Task 5: Review, Release Gate, Commit, And Push

**Files:**

- Add review artifacts listed above.

- [ ] **Step 1: Focused verification**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest tests/test_source_liveness.py tests/test_cli.py -q -k "source_liveness or source_pack_lint"
uv --no-config run --frozen pytest tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/source_liveness.py src/fashion_radar/cli.py tests/test_source_liveness.py tests/test_cli.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_liveness.py src/fashion_radar/cli.py tests/test_source_liveness.py tests/test_cli.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Expected: all commands pass.

- [ ] **Step 2: Request code review**

Create and run `docs/reviews/opencode-stage-190-code-review-prompt.md`; require
the response to start with:

```text
# Stage 190 Code Review
```

Fix Critical or Important findings and request rereview if needed.

- [ ] **Step 3: Full release gate**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then exit 1; fi
```

Expected: test/check/lint/format/lock/diff commands pass. The token and
extraheader negative checks print no output and exit 0.

- [ ] **Step 4: Request release review**

Create and run `docs/reviews/opencode-stage-190-release-review-prompt.md`;
require the response to start with:

```text
# Stage 190 Release Review
```

Expected: no Critical or Important findings.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add \
  src/fashion_radar/source_liveness.py \
  src/fashion_radar/cli.py \
  tests/test_source_liveness.py \
  tests/test_cli.py \
  tests/test_source_packs_docs.py \
  tests/test_source_pack_quality_docs.py \
  tests/test_cli_docs.py \
  README.md \
  docs/architecture.md \
  docs/source-packs.md \
  docs/source-pack-quality.md \
  docs/cli-reference.md \
  docs/github-upload-checklist.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-24-stage-190-source-liveness-diagnostics-design.md \
  docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md \
  docs/reviews/opencode-stage-190-plan-review-prompt.md \
  docs/reviews/opencode-stage-190-plan-review.md \
  docs/reviews/opencode-stage-190-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-190-plan-rereview.md \
  docs/reviews/opencode-stage-190-plan-rereview-2-prompt.md \
  docs/reviews/opencode-stage-190-plan-rereview-2.md \
  docs/reviews/opencode-stage-190-plan-rereview-3-prompt.md \
  docs/reviews/opencode-stage-190-plan-rereview-3.md \
  docs/reviews/opencode-stage-190-code-review-prompt.md \
  docs/reviews/opencode-stage-190-code-review.md \
  docs/reviews/opencode-stage-190-code-rereview-prompt.md \
  docs/reviews/opencode-stage-190-code-rereview.md \
  docs/reviews/opencode-stage-190-release-review-prompt.md \
  docs/reviews/opencode-stage-190-release-review.md \
  docs/reviews/opencode-stage-190-release-rereview-prompt.md \
  docs/reviews/opencode-stage-190-release-rereview.md
git commit -m "feat: add source liveness diagnostics"
git push origin main
```

Expected: commit and push succeed.

## Self-Review

- Spec coverage: The plan covers contracts, probes, CLI, docs, review artifacts,
  release gate, commit, and push.
- Placeholder scan: No TBD/TODO/fill-in placeholders remain.
- Type consistency: Names match the Stage 190 design and intended imports.
