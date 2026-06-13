from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.discovery.candidates import CandidateMetric, discover_candidates
from fashion_radar.imported_signals import verify_imported_signals_schema
from fashion_radar.models.source import SourceType
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.trends import create_readonly_sqlite_engine
from fashion_radar.utils.dates import parse_datetime_utc


class ImportedCandidateRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: str
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: str


class ImportedCandidatesReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_type: Literal["manual_import"] = "manual_import"
    source_name: str | None = None
    limit: int | None = 50
    candidate_count: int = 0
    candidates: list[ImportedCandidateRow] = Field(default_factory=list)


def query_imported_candidates(
    db_path: Path,
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    source_name: str | None = None,
    limit: int | None = 50,
) -> ImportedCandidatesReview:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")
    as_of_value = parse_datetime_utc(as_of)
    current_window_start = as_of_value - timedelta(days=scoring.current_window_days)
    baseline_window_start = current_window_start - timedelta(days=scoring.baseline_window_days)
    source_filter = (source_name or "").strip() or None
    review_base = {
        "database": str(db_path),
        "as_of": as_of_value.isoformat(),
        "current_window_start": current_window_start.isoformat(),
        "baseline_window_start": baseline_window_start.isoformat(),
        "current_days": scoring.current_window_days,
        "baseline_days": scoring.baseline_window_days,
        "source_name": source_filter,
        "limit": limit,
    }
    if not db_path.exists():
        return ImportedCandidatesReview(**review_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        metrics = discover_candidates(
            engine,
            scoring=scoring,
            settings=settings,
            entity_config=entity_config,
            as_of=as_of_value,
            limit=limit,
            source_type=SourceType.MANUAL_IMPORT,
            source_name=source_filter,
        )
    finally:
        engine.dispose()
    candidates = [_candidate_report(metric) for metric in metrics]
    return ImportedCandidatesReview(
        **review_base,
        candidate_count=len(candidates),
        candidates=candidates,
    )


def render_imported_candidates_table(review: ImportedCandidatesReview) -> list[str]:
    lines = [
        "Imported manual candidate signals from local SQLite.",
        "Candidate signals are observed phrases from retained manual_import rows and need review.",
        f"Current window: {review.current_window_start} < collected_at <= {review.as_of}",
        (
            f"Baseline window: {review.baseline_window_start} < collected_at <= "
            f"{review.current_window_start}"
        ),
        f"Source name: {_table_cell(review.source_name or 'none')}",
        f"Candidates: {review.candidate_count}",
    ]
    if not review.candidates:
        lines.append("No imported manual candidate signals found.")
        return lines

    lines.append(
        "Phrase | Type | Label | Score | Current Mentions | Baseline Mentions | "
        "Distinct Sources | First Seen At"
    )
    for candidate in review.candidates:
        lines.append(
            f"{_table_cell(candidate.phrase)} | {_table_cell(candidate.candidate_type)} | "
            f"{_table_cell(candidate.label)} | {candidate.score:.2f} | "
            f"{candidate.current_mentions} | {candidate.baseline_mentions} | "
            f"{candidate.distinct_sources} | {candidate.first_seen_at}"
        )
    return lines


def _candidate_report(metric: CandidateMetric) -> ImportedCandidateRow:
    return ImportedCandidateRow(
        phrase=metric.phrase,
        candidate_type=metric.candidate_type,
        label=metric.label,
        score=metric.score,
        current_mentions=metric.current_mentions,
        baseline_mentions=metric.baseline_mentions,
        distinct_sources=metric.distinct_sources,
        growth_ratio=metric.growth_ratio,
        first_seen_at=parse_datetime_utc(metric.first_seen_at).isoformat(),
    )


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
