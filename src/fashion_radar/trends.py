from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import MultipleResultsFound

from fashion_radar.db.schema import (
    SCHEMA_VERSION,
    entity_first_seen,
    item_entities,
    items,
    schema_metadata,
)
from fashion_radar.db.schema_messages import (
    missing_schema_message,
    unsupported_schema_message,
)
from fashion_radar.discovery.candidates import CandidateMetric, discover_candidates
from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.scoring import EntityHeatMetric, score_entities
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc

_TREND_CANDIDATE_SNAPSHOT_MAX = 2_147_483_647


@dataclass(frozen=True)
class _Comparable:
    signal_kind: TrendSignalKind
    comparison_key: str
    name: str
    signal_type: str
    label: str
    score: float
    current_mentions: int
    internal_baseline_mentions: int
    growth_ratio: float | None
    distinct_sources: int
    first_seen_at: datetime


def compare_trends(
    *,
    current_entities: Sequence[EntityHeatMetric],
    baseline_entities: Sequence[EntityHeatMetric],
    current_candidates: Sequence[CandidateMetric],
    baseline_candidates: Sequence[CandidateMetric],
    as_of: datetime,
    baseline_as_of: datetime,
    include_dropped: bool = False,
    limit: int | None = None,
) -> TrendComparison:
    current: dict[str, _Comparable] = {}
    baseline: dict[str, _Comparable] = {}

    for metric in current_entities:
        comparable = _entity_comparable(metric)
        current[comparable.comparison_key] = comparable
    for metric in current_candidates:
        comparable = _candidate_comparable(metric)
        current[comparable.comparison_key] = comparable
    for metric in baseline_entities:
        comparable = _entity_comparable(metric)
        baseline[comparable.comparison_key] = comparable
    for metric in baseline_candidates:
        comparable = _candidate_comparable(metric)
        baseline[comparable.comparison_key] = comparable

    deltas = [
        _to_delta(
            current=current.get(key),
            baseline=baseline.get(key),
            include_dropped=include_dropped,
        )
        for key in sorted(current.keys() | baseline.keys())
    ]
    ordered = sorted((delta for delta in deltas if delta is not None), key=_sort_key)
    if limit is not None:
        ordered = ordered[: max(0, limit)]
    return TrendComparison(
        as_of=parse_datetime_utc(as_of),
        baseline_as_of=parse_datetime_utc(baseline_as_of),
        deltas=ordered,
    )


def create_readonly_sqlite_engine(db_path: Path) -> Engine:
    quoted_path = quote(db_path.as_posix(), safe="/")
    return create_engine(
        f"sqlite:///file:{quoted_path}?mode=ro&uri=true",
        future=True,
    )


def verify_readonly_trend_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    version = _read_schema_version_if_available(engine, inspector, table_names)
    if version is not None and version != SCHEMA_VERSION:
        raise RuntimeError(unsupported_schema_message(version))

    required = {"schema_metadata", "items", "item_entities", "entity_first_seen"}
    missing = sorted(required - table_names)
    if missing:
        raise RuntimeError(
            missing_schema_message(
                f"Database schema is missing required tables: {', '.join(missing)}"
            )
        )
    for table in (schema_metadata, items, item_entities, entity_first_seen):
        _verify_columns(inspector, table.name, {column.name for column in table.columns})
    if version is None:
        raise RuntimeError(missing_schema_message("schema_metadata.version is empty"))


def _read_schema_version_if_available(
    engine: Engine,
    inspector,
    table_names: set[str],
) -> int | None:
    if "schema_metadata" not in table_names:
        return None
    metadata_columns = {column["name"] for column in inspector.get_columns("schema_metadata")}
    if "version" not in metadata_columns:
        raise RuntimeError(
            "Database schema table schema_metadata is missing required columns: version"
        )
    try:
        with engine.connect() as connection:
            raw_version = connection.execute(select(schema_metadata.c.version)).scalar_one_or_none()
    except MultipleResultsFound as exc:
        raise RuntimeError("schema_metadata.version has multiple rows") from exc
    if raw_version is None:
        return None
    version = _parse_schema_version_value(raw_version)
    if version is None:
        raise RuntimeError("schema_metadata.version is not an integer")
    return version


def _parse_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def _verify_columns(inspector, table_name: str, required_columns: set[str]) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing = sorted(required_columns - columns)
    if missing:
        raise RuntimeError(
            f"Database schema table {table_name} is missing required columns: {', '.join(missing)}"
        )


def build_trend_comparison(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    candidate_discovery: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: datetime,
    baseline_as_of: datetime,
    include_dropped: bool = False,
    limit: int | None = None,
) -> TrendComparison:
    as_of_utc = parse_datetime_utc(as_of)
    baseline_as_of_utc = parse_datetime_utc(baseline_as_of)
    candidate_snapshot_settings = _candidate_snapshot_settings(candidate_discovery)
    return compare_trends(
        current_entities=score_entities(engine, scoring=scoring, as_of=as_of_utc),
        baseline_entities=score_entities(engine, scoring=scoring, as_of=baseline_as_of_utc),
        current_candidates=discover_candidates(
            engine,
            scoring=scoring,
            settings=candidate_snapshot_settings,
            entity_config=entity_config,
            as_of=as_of_utc,
        ),
        baseline_candidates=discover_candidates(
            engine,
            scoring=scoring,
            settings=candidate_snapshot_settings,
            entity_config=entity_config,
            as_of=baseline_as_of_utc,
        ),
        as_of=as_of_utc,
        baseline_as_of=baseline_as_of_utc,
        include_dropped=include_dropped,
        limit=limit,
    )


def _candidate_snapshot_settings(
    settings: CandidateDiscoverySettings,
) -> CandidateDiscoverySettings:
    return settings.model_copy(update={"max_candidates": _TREND_CANDIDATE_SNAPSHOT_MAX})


def _entity_key(metric: EntityHeatMetric) -> str:
    return f"entity:{metric.entity_type}:{normalize_alias_key(metric.entity_name)}"


def _candidate_key(metric: CandidateMetric) -> str:
    return f"candidate:{metric.candidate_type}:{normalize_alias_key(metric.phrase)}"


def _entity_comparable(metric: EntityHeatMetric) -> _Comparable:
    return _Comparable(
        signal_kind=TrendSignalKind.ENTITY,
        comparison_key=_entity_key(metric),
        name=metric.entity_name,
        signal_type=metric.entity_type,
        label=metric.label,
        score=metric.heat_score,
        current_mentions=metric.current_mentions,
        internal_baseline_mentions=metric.baseline_mentions,
        growth_ratio=metric.growth_ratio,
        distinct_sources=metric.distinct_sources,
        first_seen_at=parse_datetime_utc(metric.first_seen_at),
    )


def _candidate_comparable(metric: CandidateMetric) -> _Comparable:
    return _Comparable(
        signal_kind=TrendSignalKind.CANDIDATE,
        comparison_key=_candidate_key(metric),
        name=metric.phrase,
        signal_type=metric.candidate_type,
        label=metric.label,
        score=metric.score,
        current_mentions=metric.current_mentions,
        internal_baseline_mentions=metric.baseline_mentions,
        growth_ratio=metric.growth_ratio,
        distinct_sources=metric.distinct_sources,
        first_seen_at=parse_datetime_utc(metric.first_seen_at),
    )


def _to_delta(
    *,
    current: _Comparable | None,
    baseline: _Comparable | None,
    include_dropped: bool,
) -> TrendDelta | None:
    if current is None and baseline is None:
        return None
    if current is None and not include_dropped:
        return None

    status = _status(current, baseline)
    source = current or baseline
    if source is None:
        return None

    current_score = current.score if current is not None else 0.0
    baseline_score = baseline.score if baseline is not None else 0.0
    current_mentions = current.current_mentions if current is not None else 0
    baseline_mentions = baseline.current_mentions if baseline is not None else 0
    current_distinct_sources = current.distinct_sources if current is not None else 0
    baseline_distinct_sources = baseline.distinct_sources if baseline is not None else 0

    return TrendDelta(
        signal_kind=source.signal_kind,
        comparison_key=source.comparison_key,
        name=source.name,
        signal_type=source.signal_type,
        status=status,
        current_label=current.label if current is not None else None,
        baseline_label=baseline.label if baseline is not None else None,
        current_score=current_score,
        baseline_score=baseline_score,
        score_delta=current_score - baseline_score,
        current_mentions=current_mentions,
        baseline_mentions=baseline_mentions,
        mention_delta=current_mentions - baseline_mentions,
        current_internal_baseline_mentions=(
            current.internal_baseline_mentions if current is not None else 0
        ),
        baseline_internal_baseline_mentions=(
            baseline.internal_baseline_mentions if baseline is not None else 0
        ),
        current_growth_ratio=current.growth_ratio if current is not None else None,
        baseline_growth_ratio=baseline.growth_ratio if baseline is not None else None,
        current_distinct_sources=current_distinct_sources,
        baseline_distinct_sources=baseline_distinct_sources,
        distinct_source_delta=current_distinct_sources - baseline_distinct_sources,
        first_seen_at=source.first_seen_at,
    )


def _status(current: _Comparable | None, baseline: _Comparable | None) -> TrendStatus:
    if current is not None and baseline is None:
        return TrendStatus.NEW
    if current is None and baseline is not None:
        return TrendStatus.DROPPED
    if current is None or baseline is None:
        return TrendStatus.STABLE

    score_delta = current.score - baseline.score
    mention_delta = current.current_mentions - baseline.current_mentions
    if score_delta > 0 and mention_delta >= 0:
        return TrendStatus.RISING
    if score_delta == 0 and mention_delta > 0:
        return TrendStatus.RISING
    if score_delta < 0 and mention_delta <= 0:
        return TrendStatus.COOLING
    if score_delta == 0 and mention_delta < 0:
        return TrendStatus.COOLING
    return TrendStatus.STABLE


def _sort_key(delta: TrendDelta) -> tuple[int, float, float, int, str, str, str, str]:
    status_order = {
        TrendStatus.NEW: 0,
        TrendStatus.RISING: 1,
        TrendStatus.COOLING: 2,
        TrendStatus.STABLE: 3,
        TrendStatus.DROPPED: 4,
    }
    return (
        status_order[delta.status],
        -abs(delta.score_delta),
        -delta.current_score,
        -delta.current_mentions,
        delta.name.casefold(),
        delta.signal_kind.value,
        delta.signal_type,
        delta.comparison_key,
    )
