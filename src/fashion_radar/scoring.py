from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import item_entities, items
from fashion_radar.settings import ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc


class EntityHeatMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: str
    entity_type: str
    label: str
    heat_score: float
    current_mentions: int
    baseline_mentions: int
    weighted_mention_sum: float
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: datetime
    weighted_mention_component: float
    growth_component: float
    source_diversity_component: float
    high_weight_component: float


@dataclass(frozen=True)
class _Mention:
    entity_name: str
    entity_type: str
    item_id: int
    source_name: str
    source_weight: float
    confidence: float
    collected_at: datetime


def score_entities(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    as_of: datetime,
) -> list[EntityHeatMetric]:
    as_of_utc = parse_datetime_utc(as_of)
    current_start = as_of_utc - timedelta(days=scoring.current_window_days)
    baseline_start = current_start - timedelta(days=scoring.baseline_window_days)
    mentions = _load_distinct_mentions(
        engine,
        min_match_confidence=scoring.min_match_confidence,
        as_of=as_of_utc,
    )
    by_entity: dict[str, list[_Mention]] = {}
    for mention in mentions:
        by_entity.setdefault(mention.entity_name, []).append(mention)

    metrics: list[EntityHeatMetric] = []
    for entity_name, entity_mentions in by_entity.items():
        current_mentions = [
            mention
            for mention in entity_mentions
            if current_start < mention.collected_at <= as_of_utc
        ]
        if not current_mentions:
            continue
        baseline_mentions = [
            mention
            for mention in entity_mentions
            if baseline_start < mention.collected_at <= current_start
        ]
        metrics.append(
            _score_entity(
                entity_name=entity_name,
                entity_type=current_mentions[0].entity_type,
                current_mentions=current_mentions,
                baseline_mentions=baseline_mentions,
                first_seen_at=min(mention.collected_at for mention in entity_mentions),
                scoring=scoring,
                as_of=as_of_utc,
            )
        )

    return sorted(
        metrics,
        key=lambda metric: (
            -metric.heat_score,
            -metric.current_mentions,
            -metric.distinct_sources,
            metric.entity_name,
        ),
    )


def _load_distinct_mentions(
    engine: Engine,
    *,
    min_match_confidence: float,
    as_of: datetime,
) -> list[_Mention]:
    rows = []
    with engine.connect() as connection:
        result = connection.execute(
            select(
                item_entities.c.item_id,
                item_entities.c.entity_name,
                item_entities.c.entity_type,
                item_entities.c.confidence,
                items.c.source_name,
                items.c.source_weight,
                items.c.collected_at,
            )
            .select_from(item_entities.join(items, item_entities.c.item_id == items.c.id))
            .where(item_entities.c.confidence >= min_match_confidence)
        ).mappings()
        rows = list(result)

    distinct: dict[tuple[str, int], _Mention] = {}
    for row in rows:
        collected_at = parse_datetime_utc(row["collected_at"])
        if collected_at > as_of:
            continue
        key = (row["entity_name"], int(row["item_id"]))
        mention = _Mention(
            entity_name=row["entity_name"],
            entity_type=row["entity_type"],
            item_id=int(row["item_id"]),
            source_name=row["source_name"],
            source_weight=float(row["source_weight"] or 1.0),
            confidence=float(row["confidence"]),
            collected_at=collected_at,
        )
        existing = distinct.get(key)
        if existing is None or mention.confidence > existing.confidence:
            distinct[key] = mention
    return list(distinct.values())


def _score_entity(
    *,
    entity_name: str,
    entity_type: str,
    current_mentions: list[_Mention],
    baseline_mentions: list[_Mention],
    first_seen_at: datetime,
    scoring: ScoringSettings,
    as_of: datetime,
) -> EntityHeatMetric:
    current_count = len(current_mentions)
    baseline_count = len(baseline_mentions)
    weighted_mention_sum = sum(
        mention.source_weight * mention.confidence for mention in current_mentions
    )
    distinct_sources = len({mention.source_name for mention in current_mentions})
    current_rate = current_count / scoring.current_window_days
    baseline_rate = baseline_count / scoring.baseline_window_days if baseline_count else 0
    growth_ratio = current_rate / baseline_rate if baseline_rate > 0 else None

    weighted_mention_component = weighted_mention_sum * scoring.weighted_mentions_7d
    growth_component = (
        max(0.0, growth_ratio - 1) * scoring.growth_bonus if growth_ratio is not None else 0.0
    )
    source_diversity_component = max(0, distinct_sources - 1) * scoring.source_diversity_bonus
    high_weight_component = (
        scoring.high_weight_source_bonus
        if any(
            mention.source_weight >= scoring.high_weight_source_threshold
            for mention in current_mentions
        )
        else 0.0
    )
    heat_score = (
        weighted_mention_component
        + growth_component
        + source_diversity_component
        + high_weight_component
    )

    return EntityHeatMetric(
        entity_name=entity_name,
        entity_type=entity_type,
        label=_label_entity(
            first_seen_at=first_seen_at,
            current_mentions=current_count,
            baseline_mentions=baseline_count,
            growth_ratio=growth_ratio,
            heat_score=heat_score,
            distinct_sources=distinct_sources,
            scoring=scoring,
            as_of=as_of,
        ),
        heat_score=heat_score,
        current_mentions=current_count,
        baseline_mentions=baseline_count,
        weighted_mention_sum=weighted_mention_sum,
        distinct_sources=distinct_sources,
        growth_ratio=growth_ratio,
        first_seen_at=first_seen_at,
        weighted_mention_component=weighted_mention_component,
        growth_component=growth_component,
        source_diversity_component=source_diversity_component,
        high_weight_component=high_weight_component,
    )


def _label_entity(
    *,
    first_seen_at: datetime,
    current_mentions: int,
    baseline_mentions: int,
    growth_ratio: float | None,
    heat_score: float,
    distinct_sources: int,
    scoring: ScoringSettings,
    as_of: datetime,
) -> str:
    if (
        first_seen_at > as_of - timedelta(days=scoring.new_entity_days)
        and current_mentions >= scoring.new_min_mentions
    ):
        return "new"
    if (
        heat_score >= scoring.hot_score_threshold
        and distinct_sources >= scoring.hot_min_distinct_sources
    ):
        return "hot"
    if (
        growth_ratio is not None
        and baseline_mentions > 0
        and current_mentions >= scoring.rising_min_mentions
        and growth_ratio >= scoring.rising_growth_ratio
    ):
        return "rising"
    if (
        growth_ratio is not None
        and baseline_mentions >= scoring.cooling_min_baseline_mentions
        and growth_ratio <= scoring.cooling_growth_ratio
    ):
        return "cooling"
    if current_mentions >= scoring.stable_min_mentions:
        return "stable"
    return "stable"
