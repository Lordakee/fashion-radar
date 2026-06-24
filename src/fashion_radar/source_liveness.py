from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from io import BytesIO
from pathlib import Path
from typing import Any, Literal, Protocol

import feedparser
from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.collectors.gdelt import GDELT_DOC_API, gdelt_http_settings
from fashion_radar.lint_formatting import format_count_label, format_finding_counts
from fashion_radar.models.source import HttpSourceSettings, SourceDefinition, SourceType
from fashion_radar.settings import ConfigError, load_source_config
from fashion_radar.utils.http import FashionHttpClient

SOURCE_LIVENESS_CONTRACT_VERSION = "source-liveness/v1"
SOURCE_LIVENESS_EXECUTION_MODE = "network_read_only"
SOURCE_LIVENESS_BOUNDARIES = [
    (
        "Performs bounded network probes for configured RSS/RSSHub feeds and GDELT "
        "Doc API queries only."
    ),
    (
        "Does not collect, store, score, match, report, open SQLite, update source "
        "health, fetch article pages, or prove demand/coverage."
    ),
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

    factory = client_factory or _default_client_factory
    monotonic_clock = monotonic or time.monotonic
    results: list[SourceLivenessResult] = []
    for source in config.sources:
        if not source.enabled:
            results.append(_skipped_result(source, checked_at))
        elif source.type in {SourceType.RSS, SourceType.RSSHUB}:
            results.append(_probe_rss_source(source, factory, checked_at, monotonic_clock))
        elif source.type == SourceType.GDELT:
            results.append(_probe_gdelt_source(source, factory, checked_at, monotonic_clock))

    type_counts = Counter(source.type.value for source in config.sources)
    tag_counts = Counter(tag for source in config.sources for tag in source.tags)
    return build_source_liveness_report_from_results(
        path=str(path),
        checked_at=checked_at,
        source_count=len(config.sources),
        enabled_count=sum(1 for source in config.sources if source.enabled),
        disabled_count=sum(1 for source in config.sources if not source.enabled),
        type_counts=dict(type_counts),
        tag_counts=dict(tag_counts),
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
    type_counts: Mapping[str, int],
    tag_counts: Mapping[str, int],
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


def render_source_liveness_table(report: SourceLivenessReport) -> list[str]:
    lines = [
        f"Source liveness: {report.path}",
        f"Contract version: {report.contract_version}",
        f"Execution mode: {report.execution_mode}",
        f"Checked at: {report.checked_at.isoformat()}",
        (
            f"Sources: {report.source_count} total, {report.enabled_count} enabled, "
            f"{report.disabled_count} disabled, {report.probed_count} probed"
        ),
        (
            f"Results: {report.live_count} live, {report.degraded_count} degraded, "
            f"{report.empty_count} empty, {report.failed_count} failed, "
            f"{report.skipped_count} skipped"
        ),
        f"Types: {_format_counts(report.type_counts)}",
        f"Tags: {_format_counts(report.tag_counts)}",
        (
            "Findings: "
            f"{format_finding_counts(report.error_count, report.warning_count, report.info_count)}"
        ),
    ]
    if report.results:
        lines.append("Source | Type | Status | Severity | Records | Target | Message")
        for result in report.results:
            records = "n/a" if result.records_seen is None else str(result.records_seen)
            lines.append(
                " | ".join(
                    [
                        _sanitize_cell(result.source_name),
                        result.source_type.value,
                        result.status.value,
                        result.severity.value,
                        records,
                        _sanitize_cell(result.target),
                        _sanitize_cell(result.message),
                    ]
                )
            )
    else:
        lines.append("No source-liveness result rows.")

    if report.findings:
        lines.append("Finding Severity | Code | Message")
        for finding in report.findings:
            lines.append(
                " | ".join(
                    [
                        finding.severity.value,
                        finding.code,
                        _sanitize_cell(finding.message),
                    ]
                )
            )

    lines.append("Boundaries:")
    lines.extend(f"- {boundary}" for boundary in report.boundaries)
    return lines


def source_liveness_should_exit_nonzero(
    report: SourceLivenessReport,
    *,
    strict: bool,
) -> bool:
    if report.error_count > 0:
        return True
    return strict and report.warning_count > 0


def _default_client_factory(
    _source: SourceDefinition,
    settings: HttpSourceSettings,
) -> HttpProbeClient:
    return FashionHttpClient(settings)


def _probe_rss_source(
    source: SourceDefinition,
    client_factory: SourceHttpClientFactory,
    checked_at: datetime,
    monotonic: Callable[[], float],
) -> SourceLivenessResult:
    started_at = monotonic()
    client: HttpProbeClient | None = None
    try:
        client = client_factory(source, source.http)
        parsed = feedparser.parse(BytesIO(client.get_text(source.url or "").encode("utf-8")))
        elapsed_ms = _elapsed_ms(started_at, monotonic)
        entries = list(parsed.entries)
        records_seen = len(entries)
        bozo = bool(parsed.get("bozo", False))
        if records_seen > 0 and bozo:
            return _result(
                source,
                checked_at=checked_at,
                elapsed_ms=elapsed_ms,
                status=SourceLivenessStatus.DEGRADED,
                severity=SourceLivenessSeverity.WARNING,
                code="malformed_feed",
                message=(
                    f"Feed returned {_record_label(records_seen, 'entry', 'entries')} "
                    "with parser warnings."
                ),
                records_seen=records_seen,
            )
        if records_seen > 0:
            return _result(
                source,
                checked_at=checked_at,
                elapsed_ms=elapsed_ms,
                status=SourceLivenessStatus.LIVE,
                severity=SourceLivenessSeverity.OK,
                code=None,
                message=f"Feed returned {_record_label(records_seen, 'entry', 'entries')}.",
                records_seen=records_seen,
            )
        if bozo:
            return _result(
                source,
                checked_at=checked_at,
                elapsed_ms=elapsed_ms,
                status=SourceLivenessStatus.FAILED,
                severity=SourceLivenessSeverity.ERROR,
                code="malformed_feed",
                message=_malformed_feed_message(parsed),
                records_seen=0,
                error_type=_bozo_error_type(parsed),
            )
        return _result(
            source,
            checked_at=checked_at,
            elapsed_ms=elapsed_ms,
            status=SourceLivenessStatus.EMPTY,
            severity=SourceLivenessSeverity.WARNING,
            code="empty_feed",
            message="Feed returned no entries.",
            records_seen=0,
        )
    except Exception as exc:
        return _exception_result(source, checked_at, _elapsed_ms(started_at, monotonic), exc)
    finally:
        if client is not None:
            client.close()


def _probe_gdelt_source(
    source: SourceDefinition,
    client_factory: SourceHttpClientFactory,
    checked_at: datetime,
    monotonic: Callable[[], float],
) -> SourceLivenessResult:
    started_at = monotonic()
    client: HttpProbeClient | None = None
    try:
        client = client_factory(source, gdelt_http_settings(source))
        payload = client.get_json(GDELT_DOC_API, params=_gdelt_liveness_params(source))
        elapsed_ms = _elapsed_ms(started_at, monotonic)
        articles = payload.get("articles") if isinstance(payload, Mapping) else None
        if not isinstance(articles, list):
            return _result(
                source,
                checked_at=checked_at,
                elapsed_ms=elapsed_ms,
                status=SourceLivenessStatus.FAILED,
                severity=SourceLivenessSeverity.ERROR,
                code="invalid_gdelt_payload",
                message="GDELT response did not contain an articles list.",
                records_seen=None,
                error_type=type(payload).__name__,
            )
        records_seen = len(articles)
        if records_seen == 0:
            return _result(
                source,
                checked_at=checked_at,
                elapsed_ms=elapsed_ms,
                status=SourceLivenessStatus.EMPTY,
                severity=SourceLivenessSeverity.WARNING,
                code="empty_gdelt_results",
                message="GDELT returned no articles.",
                records_seen=0,
            )
        return _result(
            source,
            checked_at=checked_at,
            elapsed_ms=elapsed_ms,
            status=SourceLivenessStatus.LIVE,
            severity=SourceLivenessSeverity.OK,
            code=None,
            message=f"GDELT returned {_record_label(records_seen, 'article', 'articles')}.",
            records_seen=records_seen,
        )
    except Exception as exc:
        return _exception_result(source, checked_at, _elapsed_ms(started_at, monotonic), exc)
    finally:
        if client is not None:
            client.close()


def _gdelt_liveness_params(source: SourceDefinition) -> dict[str, str | int]:
    return {
        "query": source.query or "",
        "mode": "artlist",
        "format": "json",
        "timespan": f"{source.gdelt.lookback_hours}h",
        "maxrecords": 1,
    }


def _skipped_result(source: SourceDefinition, checked_at: datetime) -> SourceLivenessResult:
    target_type, target = _target(source)
    return SourceLivenessResult(
        source_name=source.name,
        source_type=source.type,
        enabled=False,
        target_type=target_type,
        target=target,
        status=SourceLivenessStatus.SKIPPED,
        severity=SourceLivenessSeverity.INFO,
        code="source_disabled",
        message="Source is disabled; no liveness probe was run.",
        checked_at=checked_at,
        elapsed_ms=0,
        records_seen=None,
        error_type=None,
    )


def _exception_result(
    source: SourceDefinition,
    checked_at: datetime,
    elapsed_ms: int,
    exc: Exception,
) -> SourceLivenessResult:
    return _result(
        source,
        checked_at=checked_at,
        elapsed_ms=elapsed_ms,
        status=SourceLivenessStatus.FAILED,
        severity=SourceLivenessSeverity.ERROR,
        code="fetch_failed",
        message=f"Probe failed: {exc}",
        records_seen=None,
        error_type=type(exc).__name__,
    )


def _result(
    source: SourceDefinition,
    *,
    checked_at: datetime,
    elapsed_ms: int,
    status: SourceLivenessStatus,
    severity: SourceLivenessSeverity,
    code: str | None,
    message: str,
    records_seen: int | None,
    error_type: str | None = None,
) -> SourceLivenessResult:
    target_type, target = _target(source)
    return SourceLivenessResult(
        source_name=source.name,
        source_type=source.type,
        enabled=source.enabled,
        target_type=target_type,
        target=target,
        status=status,
        severity=severity,
        code=code,
        message=message,
        checked_at=checked_at,
        elapsed_ms=elapsed_ms,
        records_seen=records_seen,
        error_type=error_type,
    )


def _target(source: SourceDefinition) -> tuple[Literal["url", "gdelt_query"], str]:
    if source.type == SourceType.GDELT:
        return "gdelt_query", source.query or ""
    return "url", source.url or ""


def _checked_at(clock: Callable[[], datetime] | None) -> datetime:
    value = clock() if clock is not None else datetime.now(tz=UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _elapsed_ms(started_at: float, monotonic: Callable[[], float]) -> int:
    return max(0, round((monotonic() - started_at) * 1000))


def _count_status(
    results: Sequence[SourceLivenessResult],
    status: SourceLivenessStatus,
) -> int:
    return sum(1 for result in results if result.status == status)


def _count_severity(
    results: Sequence[SourceLivenessResult],
    severity: SourceLivenessSeverity,
) -> int:
    return sum(1 for result in results if result.severity == severity)


def _count_findings(
    findings: Sequence[SourceLivenessFinding],
    severity: SourceLivenessFindingSeverity,
) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _sanitize_cell(value: object) -> str:
    return " ".join(str(value).replace("|", "/").split())


def _record_label(count: int, singular: str, plural: str) -> str:
    return format_count_label(count, singular, plural)


def _malformed_feed_message(parsed: feedparser.FeedParserDict) -> str:
    bozo_exception = parsed.get("bozo_exception")
    if bozo_exception is None:
        return "Feed could not be parsed."
    return f"Feed could not be parsed: {bozo_exception}"


def _bozo_error_type(parsed: feedparser.FeedParserDict) -> str | None:
    bozo_exception = parsed.get("bozo_exception")
    if bozo_exception is None:
        return None
    return type(bozo_exception).__name__
