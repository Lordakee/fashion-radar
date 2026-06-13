from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import items
from fashion_radar.discovery.candidates import (
    candidate_key,
    configured_entity_keys,
    extract_candidate_phrases,
    stored_entity_candidate_keys,
)
from fashion_radar.imported_signals import verify_imported_signals_schema
from fashion_radar.models.source import SourceType
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.trends import create_readonly_sqlite_engine
from fashion_radar.utils.dates import parse_datetime_utc


class ImportedCandidateEvidenceRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    window: Literal["current", "baseline"]
    source_name: str
    title: str
    url: str
    published_at: str
    collected_at: str


class ImportedCandidateEvidenceReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    phrase: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_type: Literal["manual_import"] = "manual_import"
    source_name: str | None = None
    limit: int | None = 20
    row_count: int = 0
    total_count: int = 0
    current_mentions: int = 0
    baseline_mentions: int = 0
    distinct_sources: int = 0
    evidence: list[ImportedCandidateEvidenceRow] = Field(default_factory=list)


def query_imported_candidate_evidence(
    db_path: Path,
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    phrase: str,
    source_name: str | None = None,
    limit: int | None = 20,
) -> ImportedCandidateEvidenceReview:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")
    phrase_filter = phrase.strip()
    if not phrase_filter:
        raise ValueError("phrase must not be blank")
    as_of_value = parse_datetime_utc(as_of)
    current_window_start = as_of_value - timedelta(days=scoring.current_window_days)
    baseline_window_start = current_window_start - timedelta(days=scoring.baseline_window_days)
    normalized_phrase = candidate_key(phrase_filter)
    source_filter = (source_name or "").strip() or None
    review_base = {
        "database": str(db_path),
        "as_of": as_of_value.isoformat(),
        "phrase": phrase_filter,
        "current_window_start": current_window_start.isoformat(),
        "baseline_window_start": baseline_window_start.isoformat(),
        "current_days": scoring.current_window_days,
        "baseline_days": scoring.baseline_window_days,
        "source_name": source_filter,
        "limit": limit,
    }
    if not db_path.exists():
        return ImportedCandidateEvidenceReview(**review_base)

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_imported_signals_schema(engine)
        evidence = _query_evidence_rows(
            engine,
            scoring=scoring,
            settings=settings,
            entity_config=entity_config,
            as_of=as_of_value,
            current_window_start=current_window_start,
            baseline_window_start=baseline_window_start,
            normalized_phrase=normalized_phrase,
            source_name=source_filter,
        )
    finally:
        engine.dispose()

    current_rows = [row for row in evidence if row.window == "current"]
    baseline_rows = [row for row in evidence if row.window == "baseline"]
    visible_evidence = evidence[:limit] if limit is not None else evidence
    return ImportedCandidateEvidenceReview(
        **review_base,
        row_count=len(visible_evidence),
        total_count=len(evidence),
        current_mentions=len(current_rows),
        baseline_mentions=len(baseline_rows),
        distinct_sources=len({row.source_name for row in current_rows}),
        evidence=visible_evidence,
    )


def render_imported_candidate_evidence_table(
    review: ImportedCandidateEvidenceReview,
) -> list[str]:
    lines = [
        "Imported manual candidate evidence from local SQLite.",
        (
            "Evidence rows are retained manual_import rows whose extracted candidate "
            "phrases match the requested phrase."
        ),
        f"Phrase: {_table_cell(review.phrase)}",
        f"Current window: {review.current_window_start} < collected_at <= {review.as_of}",
        (
            f"Baseline window: {review.baseline_window_start} < collected_at <= "
            f"{review.current_window_start}"
        ),
        f"Source name: {_table_cell(review.source_name or 'none')}",
        f"Rows: {review.row_count} shown, {review.total_count} total",
        f"Current mentions: {review.current_mentions}",
        f"Baseline mentions: {review.baseline_mentions}",
        f"Distinct current sources: {review.distinct_sources}",
    ]
    if not review.evidence:
        lines.append("No imported manual candidate evidence found.")
        return lines

    lines.append("Window | ID | Collected At | Source | Title | URL")
    for row in review.evidence:
        lines.append(
            f"{row.window} | {row.id} | {row.collected_at} | "
            f"{_table_cell(row.source_name)} | {_table_cell(row.title)} | "
            f"{_table_cell(row.url)}"
        )
    return lines


def _query_evidence_rows(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: datetime,
    current_window_start: datetime,
    baseline_window_start: datetime,
    normalized_phrase: str,
    source_name: str | None,
) -> list[ImportedCandidateEvidenceRow]:
    if not settings.enabled:
        return []

    known_keys = configured_entity_keys(entity_config, as_of=as_of) | stored_entity_candidate_keys(
        engine,
        min_match_confidence=scoring.min_match_confidence,
        as_of=as_of,
    )
    conditions = [items.c.source_type == SourceType.MANUAL_IMPORT.value]
    if source_name is not None:
        conditions.append(items.c.source_name == source_name)
    query = select(
        items.c.id,
        items.c.source_name,
        items.c.url,
        items.c.published_at,
        items.c.title,
        items.c.summary,
        items.c.collected_at,
    ).where(*conditions)

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    evidence: list[ImportedCandidateEvidenceRow] = []
    for row in rows:
        collected_at = parse_datetime_utc(row["collected_at"])
        if not (baseline_window_start < collected_at <= as_of):
            continue
        text = " ".join(value for value in (row["title"], row["summary"]) if isinstance(value, str))
        phrases = extract_candidate_phrases(
            text,
            source_name=row["source_name"],
            known_keys=known_keys,
            settings=settings,
        )
        if normalized_phrase not in {phrase.normalized_key for phrase in phrases}:
            continue
        evidence.append(
            _evidence_row(
                row,
                window=("current" if current_window_start < collected_at <= as_of else "baseline"),
                collected_at=collected_at,
            )
        )

    return sorted(
        evidence,
        key=lambda row: (
            0 if row.window == "current" else 1,
            -parse_datetime_utc(row.collected_at).timestamp(),
            -row.id,
        ),
    )


def _evidence_row(
    row,
    *,
    window: Literal["current", "baseline"],
    collected_at: datetime,
) -> ImportedCandidateEvidenceRow:
    return ImportedCandidateEvidenceRow(
        id=int(row["id"]),
        window=window,
        source_name=str(row["source_name"]),
        title=str(row["title"] or ""),
        url=str(row["url"] or ""),
        published_at=parse_datetime_utc(row["published_at"]).isoformat(),
        collected_at=collected_at.isoformat(),
    )


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
