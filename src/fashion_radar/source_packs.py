from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.settings import ConfigError, load_source_config


class SourcePackFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SourcePackFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: SourcePackFindingSeverity
    code: str
    message: str
    source_name: str | None = None
    field: str | None = None


class SourcePackLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    source_count: int = 0
    enabled_count: int = 0
    disabled_count: int = 0
    type_counts: dict[str, int] = Field(default_factory=dict)
    tag_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[SourcePackFinding] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return _count_findings(self.findings, SourcePackFindingSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return _count_findings(self.findings, SourcePackFindingSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return _count_findings(self.findings, SourcePackFindingSeverity.INFO)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


def lint_source_pack(path: Path) -> SourcePackLintResult:
    """Read and lint one local source YAML file."""
    # Raw YAML is read before typed validation so omitted fields can be linted.
    raw_data, raw_error = _read_raw_source_config(path)
    if raw_error is not None:
        return SourcePackLintResult(path=str(path), findings=[raw_error])

    raw_sources = _raw_sources(raw_data)
    try:
        source_config = load_source_config(path)
    except ConfigError as exc:
        return SourcePackLintResult(
            path=str(path),
            source_count=len(raw_sources),
            findings=[
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.ERROR,
                    code="invalid_config",
                    message=str(exc),
                )
            ],
        )

    sources = source_config.sources
    findings = _lint_sources(sources, raw_sources)
    type_counts = Counter(source.type.value for source in sources)
    tag_counts = Counter(tag for source in sources for tag in source.tags)
    return SourcePackLintResult(
        path=str(path),
        source_count=len(sources),
        enabled_count=sum(1 for source in sources if source.enabled),
        disabled_count=sum(1 for source in sources if not source.enabled),
        type_counts=dict(sorted(type_counts.items())),
        tag_counts=dict(sorted(tag_counts.items())),
        findings=_sort_findings(findings),
    )


def render_source_pack_lint_table(result: SourcePackLintResult) -> list[str]:
    """Render a deterministic human-readable lint summary."""
    lines = [
        f"Source pack: {result.path}",
        (
            f"Sources: {result.source_count} total, {result.enabled_count} enabled, "
            f"{result.disabled_count} disabled"
        ),
        f"Types: {_format_counts(result.type_counts)}",
        (
            f"Findings: {result.error_count} errors, {result.warning_count} warnings, "
            f"{result.info_count} info"
        ),
    ]
    if not result.findings:
        lines.append("No source-pack quality findings.")
        return lines

    lines.append("Severity | Code | Source | Field | Message")
    for finding in result.findings:
        lines.append(
            f"{finding.severity.value} | {finding.code} | "
            f"{finding.source_name or 'n/a'} | {finding.field or 'n/a'} | "
            f"{finding.message}"
        )
    return lines


def normalize_source_name(value: str) -> str:
    """Lowercase and collapse whitespace in a source name."""
    return " ".join(value.lower().split())


def normalize_source_target(value: str) -> str:
    """Normalize RSS/RSSHub URL strings for duplicate detection."""
    parsed = urlsplit(value.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def normalize_gdelt_query(value: str) -> str:
    """Lowercase and collapse whitespace in a GDELT query."""
    return " ".join(value.lower().split())


def _read_raw_source_config(path: Path) -> tuple[Mapping[str, Any], SourcePackFinding | None]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        return {}, _invalid_config_finding(f"Could not read config {path}: {exc}")
    except yaml.YAMLError as exc:
        return {}, _invalid_config_finding(f"Invalid YAML in {path}: {exc}")

    if not isinstance(data, Mapping):
        return {}, _invalid_config_finding(f"Config {path} must contain a YAML mapping")
    return data, None


def _raw_sources(raw_data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw_sources = raw_data.get("sources", [])
    if not isinstance(raw_sources, list):
        return []
    return [source for source in raw_sources if isinstance(source, Mapping)]


def _lint_sources(
    sources: Sequence[SourceDefinition],
    raw_sources: Sequence[Mapping[str, Any]],
) -> list[SourcePackFinding]:
    findings: list[SourcePackFinding] = []
    enabled_count = sum(1 for source in sources if source.enabled)
    if enabled_count == 0:
        findings.append(
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="empty_enabled_pack",
                message="Source pack has no enabled sources.",
            )
        )

    findings.extend(_duplicate_source_name_findings(sources))
    findings.extend(_duplicate_target_findings(sources))
    findings.extend(_duplicate_gdelt_query_findings(sources))

    for index, source in enumerate(sources):
        raw_source = raw_sources[index] if index < len(raw_sources) else {}
        if not source.tags:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.WARNING,
                    code="missing_tags",
                    message="Source has no tags.",
                    source_name=source.name,
                    field="tags",
                )
            )
        if "weight" not in raw_source:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.INFO,
                    code="implicit_weight",
                    message="Source omits weight, so scoring uses the default weight.",
                    source_name=source.name,
                    field="weight",
                )
            )
        if not source.enabled:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.INFO,
                    code="disabled_source",
                    message="Source is disabled and will not be collected.",
                    source_name=source.name,
                    field="enabled",
                )
            )
        if source.type in {SourceType.RSS, SourceType.RSSHUB} and source.article.enabled:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.INFO,
                    code="article_extraction_enabled",
                    message=(
                        "Article extraction is enabled for this RSS/RSSHub source; "
                        "review whether this local-pack setting is intended."
                    ),
                    source_name=source.name,
                    field="article.enabled",
                )
            )
    return findings


def _duplicate_source_name_findings(
    sources: Sequence[SourceDefinition],
) -> list[SourcePackFinding]:
    groups: dict[str, list[SourceDefinition]] = defaultdict(list)
    for source in sources:
        groups[normalize_source_name(source.name)].append(source)
    findings: list[SourcePackFinding] = []
    for normalized, group in groups.items():
        if len(group) < 2:
            continue
        for source in group:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.ERROR,
                    code="duplicate_source_name",
                    message=f"Duplicate source name after normalization: {normalized}",
                    source_name=source.name,
                    field="name",
                )
            )
    return findings


def _duplicate_target_findings(sources: Sequence[SourceDefinition]) -> list[SourcePackFinding]:
    groups: dict[str, list[SourceDefinition]] = defaultdict(list)
    for source in sources:
        if source.type in {SourceType.RSS, SourceType.RSSHUB} and source.url:
            groups[normalize_source_target(source.url)].append(source)
    findings: list[SourcePackFinding] = []
    for normalized, group in groups.items():
        if len(group) < 2:
            continue
        for source in group:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.WARNING,
                    code="duplicate_source_target",
                    message=f"Duplicate RSS/RSSHub target after normalization: {normalized}",
                    source_name=source.name,
                    field="url",
                )
            )
    return findings


def _duplicate_gdelt_query_findings(
    sources: Sequence[SourceDefinition],
) -> list[SourcePackFinding]:
    groups: dict[str, list[SourceDefinition]] = defaultdict(list)
    for source in sources:
        if source.type == SourceType.GDELT and source.query:
            groups[normalize_gdelt_query(source.query)].append(source)
    findings: list[SourcePackFinding] = []
    for normalized, group in groups.items():
        if len(group) < 2:
            continue
        for source in group:
            findings.append(
                SourcePackFinding(
                    severity=SourcePackFindingSeverity.WARNING,
                    code="duplicate_gdelt_query",
                    message=f"Duplicate GDELT query after normalization: {normalized}",
                    source_name=source.name,
                    field="query",
                )
            )
    return findings


def _invalid_config_finding(message: str) -> SourcePackFinding:
    return SourcePackFinding(
        severity=SourcePackFindingSeverity.ERROR,
        code="invalid_config",
        message=message,
    )


def _sort_findings(findings: Sequence[SourcePackFinding]) -> list[SourcePackFinding]:
    severity_order = {
        SourcePackFindingSeverity.ERROR: 0,
        SourcePackFindingSeverity.WARNING: 1,
        SourcePackFindingSeverity.INFO: 2,
    }
    return sorted(
        findings,
        key=lambda finding: (
            severity_order[finding.severity],
            finding.code,
            finding.source_name or "",
            finding.field or "",
        ),
    )


def _count_findings(
    findings: Sequence[SourcePackFinding],
    severity: SourcePackFindingSeverity,
) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
