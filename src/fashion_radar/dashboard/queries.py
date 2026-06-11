from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import func, select

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import item_entities, items, source_health


def database_path(data_dir: Path) -> Path:
    return data_dir / "fashion-radar.sqlite"


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
