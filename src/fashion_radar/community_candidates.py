from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.discovery.candidates import configured_entity_keys, extract_candidate_phrases
from fashion_radar.importers.manual_signals import ManualSignalFormat, load_manual_signal_rows
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc


class CommunityCandidateRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: Literal["new", "rising", "observed"]
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: str


class CommunityCandidatePreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_format: ManualSignalFormat
    as_of: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_name: str = "Community Tool Export"
    row_count: int = 0
    candidate_count: int = 0
    limit: int | None = 50
    candidates: list[CommunityCandidateRow] = Field(default_factory=list)


@dataclass(frozen=True)
class _PreviewMention:
    normalized_key: str
    phrase: str
    candidate_type: str
    source_name: str
    source_weight: float
    collected_at: datetime


def preview_community_candidates(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    default_source_name: str = "Community Tool Export",
    limit: int | None = 50,
) -> CommunityCandidatePreview:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")
    as_of_value = parse_datetime_utc(as_of)
    current_window_start = as_of_value - timedelta(days=scoring.current_window_days)
    baseline_window_start = current_window_start - timedelta(days=scoring.baseline_window_days)
    source_name = default_source_name.strip() or "Community Tool Export"
    rows = load_manual_signal_rows(
        path,
        input_format=input_format,
        default_source_name=source_name,
    )
    preview_base = {
        "input_format": input_format,
        "as_of": as_of_value.isoformat(),
        "current_window_start": current_window_start.isoformat(),
        "baseline_window_start": baseline_window_start.isoformat(),
        "current_days": scoring.current_window_days,
        "baseline_days": scoring.baseline_window_days,
        "source_name": source_name,
        "row_count": len(rows),
        "limit": limit,
    }
    if not settings.enabled:
        return CommunityCandidatePreview(**preview_base)

    known_keys = configured_entity_keys(entity_config, as_of=as_of_value)
    mentions: list[_PreviewMention] = []
    for row in rows:
        collected_at = parse_datetime_utc(row.collected_at or as_of_value)
        if not (baseline_window_start < collected_at <= as_of_value):
            continue
        text = " ".join(value for value in (row.title, row.summary) if isinstance(value, str))
        seen_row_keys: set[str] = set()
        for phrase in extract_candidate_phrases(
            text,
            source_name=row.source_name,
            known_keys=known_keys,
            settings=settings,
        ):
            if phrase.normalized_key in seen_row_keys:
                continue
            seen_row_keys.add(phrase.normalized_key)
            mentions.append(
                _PreviewMention(
                    normalized_key=phrase.normalized_key,
                    phrase=phrase.phrase,
                    candidate_type=phrase.candidate_type,
                    source_name=row.source_name,
                    source_weight=row.source_weight,
                    collected_at=collected_at,
                )
            )

    candidates = _score_preview_mentions(
        mentions,
        scoring=scoring,
        settings=settings,
        current_window_start=current_window_start,
    )
    visible_candidates = candidates[:limit] if limit is not None else candidates
    return CommunityCandidatePreview(
        **preview_base,
        candidate_count=len(candidates),
        candidates=visible_candidates,
    )


def _score_preview_mentions(
    mentions: list[_PreviewMention],
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    current_window_start: datetime,
) -> list[CommunityCandidateRow]:
    by_key: dict[str, list[_PreviewMention]] = {}
    for mention in mentions:
        by_key.setdefault(mention.normalized_key, []).append(mention)

    candidates: list[CommunityCandidateRow] = []
    for candidate_mentions in by_key.values():
        current_mentions = [
            mention for mention in candidate_mentions if mention.collected_at > current_window_start
        ]
        if not current_mentions:
            continue
        baseline_mentions = [
            mention
            for mention in candidate_mentions
            if mention.collected_at <= current_window_start
        ]
        current_count = len(current_mentions)
        distinct_sources = len({mention.source_name for mention in current_mentions})
        if current_count < settings.review_min_current_mentions:
            continue
        if distinct_sources < settings.review_min_distinct_sources:
            continue
        key = current_mentions[0].normalized_key
        if len(key.split()) == 1 and (
            current_count < settings.min_single_token_mentions
            or distinct_sources < settings.min_single_token_distinct_sources
        ):
            continue
        baseline_count = len(baseline_mentions)
        current_rate = current_count / scoring.current_window_days
        baseline_rate = baseline_count / scoring.baseline_window_days if baseline_count else 0
        growth_ratio = current_rate / baseline_rate if baseline_rate > 0 else None
        weighted_current_mentions = sum(mention.source_weight for mention in current_mentions)
        score = (
            weighted_current_mentions * scoring.weighted_mentions_7d
            + max(0, distinct_sources - 1) * scoring.source_diversity_bonus
            + (max(0.0, growth_ratio - 1) * scoring.growth_bonus if growth_ratio else 0.0)
        )
        ordered_current = sorted(
            current_mentions,
            key=lambda mention: mention.collected_at,
            reverse=True,
        )
        all_mentions = [*current_mentions, *baseline_mentions]
        candidates.append(
            CommunityCandidateRow(
                phrase=ordered_current[0].phrase,
                candidate_type=ordered_current[0].candidate_type,
                label=_preview_label(
                    baseline_count=baseline_count,
                    growth_ratio=growth_ratio,
                    settings=settings,
                ),
                score=score,
                current_mentions=current_count,
                baseline_mentions=baseline_count,
                distinct_sources=distinct_sources,
                growth_ratio=growth_ratio,
                first_seen_at=min(mention.collected_at for mention in all_mentions).isoformat(),
            )
        )

    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate.score,
            -candidate.current_mentions,
            -candidate.distinct_sources,
            candidate.phrase.lower(),
        ),
    )


def _preview_label(
    *,
    baseline_count: int,
    growth_ratio: float | None,
    settings: CandidateDiscoverySettings,
) -> Literal["new", "rising", "observed"]:
    if baseline_count == 0:
        return "new"
    if growth_ratio is not None and growth_ratio >= settings.rising_growth_ratio:
        return "rising"
    return "observed"


def render_community_candidates_table(preview: CommunityCandidatePreview) -> list[str]:
    lines = [
        "Community candidate preview from one local handoff file.",
        "Candidate signals are aggregate observed phrases from the supplied file only.",
        f"Input format: {preview.input_format}",
        f"Current window: {preview.current_window_start} < collected_at <= {preview.as_of}",
        (
            f"Baseline window: {preview.baseline_window_start} < collected_at <= "
            f"{preview.current_window_start}"
        ),
        f"Source name: {_table_cell(preview.source_name)}",
        f"Rows: {preview.row_count}",
        f"Candidates: {len(preview.candidates)} shown, {preview.candidate_count} total",
    ]
    if not preview.candidates:
        lines.append("No community candidate signals found.")
        return lines
    lines.append(
        "Phrase | Type | Label | Score | Current Mentions | Baseline Mentions | "
        "Distinct Sources | First Seen At"
    )
    for candidate in preview.candidates:
        lines.append(
            f"{_table_cell(candidate.phrase)} | {_table_cell(candidate.candidate_type)} | "
            f"{candidate.label} | {candidate.score:.2f} | {candidate.current_mentions} | "
            f"{candidate.baseline_mentions} | {candidate.distinct_sources} | "
            f"{candidate.first_seen_at}"
        )
    return lines


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
