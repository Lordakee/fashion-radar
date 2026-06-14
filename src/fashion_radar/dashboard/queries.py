from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import func, select

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import item_entities, items, source_health
from fashion_radar.models.report import report_safe_snippet
from fashion_radar.models.trend import TrendComparison
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.trends import (
    build_trend_comparison,
    create_readonly_sqlite_engine,
    verify_readonly_trend_schema,
)
from fashion_radar.utils.dates import parse_datetime_utc


def database_path(data_dir: Path) -> Path:
    return data_dir / "fashion-radar.sqlite"


def latest_report_path(reports_dir: Path) -> Path | None:
    if not reports_dir.exists():
        return None
    # report_output_paths() writes fashion-radar-YYYY-MM-DD.json.
    candidates = sorted(reports_dir.glob("fashion-radar-*.json"))
    return candidates[-1] if candidates else None


def latest_candidate_rows(reports_dir: Path) -> list[dict[str, Any]]:
    return latest_candidate_report(reports_dir)["rows"]


def latest_candidate_report(reports_dir: Path) -> dict[str, Any]:
    path = latest_report_path(reports_dir)
    if path is None:
        return {"report_date": None, "candidate_count": 0, "rows": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "report_date": None,
            "candidate_count": 0,
            "rows": [],
            "error": f"Could not parse latest report JSON {path.name}: {exc}",
        }

    report_date = payload.get("metadata", {}).get("report_date")
    rows = []
    for candidate in payload.get("candidates", []):
        rows.append(
            {
                "phrase": candidate.get("phrase", ""),
                "candidate_type": candidate.get("candidate_type", ""),
                "label": candidate.get("label", ""),
                "score": candidate.get("score", 0.0),
                "current_mentions": candidate.get("current_mentions", 0),
                "baseline_mentions": candidate.get("baseline_mentions", 0),
                "distinct_sources": candidate.get("distinct_sources", 0),
                "report_date": report_date,
            }
        )
    return {"report_date": report_date, "candidate_count": len(rows), "rows": rows}


def dashboard_summary(data_dir: Path) -> dict[str, Any]:
    db_path = database_path(data_dir)
    if not db_path.exists():
        return {
            "database_exists": False,
            "item_count": 0,
            "match_count": 0,
            "latest_collected_at": None,
        }
    engine = create_sqlite_engine(db_path)
    try:
        with engine.connect() as connection:
            item_count = connection.execute(select(func.count()).select_from(items)).scalar_one()
            match_count = connection.execute(
                select(func.count()).select_from(item_entities)
            ).scalar_one()
            latest_collected_at = connection.execute(
                select(func.max(items.c.collected_at))
            ).scalar_one()
    finally:
        engine.dispose()
    return {
        "database_exists": True,
        "item_count": int(item_count),
        "match_count": int(match_count),
        "latest_collected_at": latest_collected_at,
    }


def recent_signals(data_dir: Path, limit: int = 20) -> list[dict[str, Any]]:
    db_path = database_path(data_dir)
    if not db_path.exists():
        return []
    engine = create_sqlite_engine(db_path)
    statement = (
        select(
            items.c.collected_at,
            items.c.published_at,
            items.c.source_name,
            items.c.source_type,
            items.c.title,
            items.c.url,
            items.c.summary,
        )
        .order_by(items.c.collected_at.desc(), items.c.id.desc())
        .limit(limit)
    )
    try:
        with engine.connect() as connection:
            rows = connection.execute(statement).mappings()
            return [
                {
                    "collected_at": row["collected_at"],
                    "published_at": row["published_at"],
                    "source_name": row["source_name"],
                    "source_type": row["source_type"],
                    "title": row["title"],
                    "url": row["url"],
                    "summary": report_safe_snippet(row["summary"]),
                }
                for row in rows
            ]
    finally:
        engine.dispose()


def top_entities(
    data_dir: Path,
    *,
    entity_type: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    db_path = database_path(data_dir)
    if not db_path.exists():
        return []
    engine = create_sqlite_engine(db_path)
    statement = (
        select(
            item_entities.c.entity_name,
            item_entities.c.entity_type,
            func.count(func.distinct(item_entities.c.item_id)).label("mentions"),
        )
        .select_from(item_entities)
        .group_by(item_entities.c.entity_name, item_entities.c.entity_type)
        .order_by(
            func.count(func.distinct(item_entities.c.item_id)).desc(),
            item_entities.c.entity_name.asc(),
        )
        .limit(limit)
    )
    if entity_type is not None:
        statement = statement.where(item_entities.c.entity_type == entity_type)
    try:
        with engine.connect() as connection:
            rows = connection.execute(statement).mappings()
            return [dict(row) for row in rows]
    finally:
        engine.dispose()


def source_health_rows(data_dir: Path) -> list[dict[str, Any]]:
    db_path = database_path(data_dir)
    if not db_path.exists():
        return []
    engine = create_sqlite_engine(db_path)
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                select(source_health).order_by(
                    source_health.c.consecutive_failures.desc(),
                    source_health.c.source_name.asc(),
                )
            ).mappings()
            return [dict(row) for row in rows]
    finally:
        engine.dispose()


def load_trend_comparison(
    *,
    data_dir: Path,
    scoring: ScoringSettings,
    candidate_discovery: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: Any,
    baseline_as_of: Any,
    include_dropped: bool = False,
    limit: int | None = 20,
) -> TrendComparison:
    as_of_value = parse_datetime_utc(as_of)
    baseline_as_of_value = parse_datetime_utc(baseline_as_of)
    if baseline_as_of_value >= as_of_value:
        raise ValueError("baseline_as_of must be before as_of")

    db_path = database_path(data_dir)
    if not db_path.exists():
        return TrendComparison(
            as_of=as_of_value,
            baseline_as_of=baseline_as_of_value,
            deltas=[],
        )

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_readonly_trend_schema(engine)
        return build_trend_comparison(
            engine,
            scoring=scoring,
            candidate_discovery=candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            baseline_as_of=baseline_as_of_value,
            include_dropped=include_dropped,
            limit=limit,
        )
    finally:
        engine.dispose()
