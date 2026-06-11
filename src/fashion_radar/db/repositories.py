from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import (
    collector_runs,
    entity_first_seen,
    item_entities,
    items,
    source_health,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.utils.hashing import content_hash, normalize_url


class ItemRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def upsert_item(
        self,
        item: CollectedItem,
        *,
        source_weight: float = 1.0,
        collected_at: datetime | None = None,
    ) -> int:
        normalized = normalize_url(item.url)
        values = {
            "source_name": item.source_name,
            "source_type": item.source_type.value,
            "url": item.url,
            "normalized_url": normalized,
            "title": item.title,
            "published_at": item.published_at.isoformat(),
            "source_weight": float(source_weight),
            "summary": item.summary,
            "content_hash": content_hash(
                title=item.title,
                published_at=item.published_at,
                source_name=item.source_name,
                summary=item.summary,
            ),
        }
        insert_values = {
            **values,
            "collected_at": _utc_now_if_none(collected_at).isoformat(),
        }
        with self.engine.begin() as connection:
            existing_id = connection.execute(
                select(items.c.id).where(items.c.normalized_url == normalized)
            ).scalar_one_or_none()
            if existing_id is not None:
                connection.execute(update(items).where(items.c.id == existing_id).values(**values))
                return int(existing_id)
            result = connection.execute(items.insert().values(**insert_values))
            return int(result.inserted_primary_key[0])

    def count_items(self) -> int:
        with self.engine.connect() as connection:
            return int(connection.execute(select(func.count()).select_from(items)).scalar_one())

    def get_item(self, item_id: int) -> dict[str, Any]:
        with self.engine.connect() as connection:
            row = connection.execute(select(items).where(items.c.id == item_id)).mappings().one()
        return dict(row)

    def list_items_for_matching(self) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(
                    items.c.id,
                    items.c.title,
                    items.c.summary,
                    items.c.collected_at,
                ).order_by(items.c.id)
            ).mappings()
            return [dict(row) for row in rows]

    def replace_item_matches(
        self, item_id: int, matches: Iterable[Mapping[str, Any] | Any]
    ) -> None:
        match_rows = list(matches)
        with self.engine.begin() as connection:
            connection.execute(delete(item_entities).where(item_entities.c.item_id == item_id))
            for match in match_rows:
                connection.execute(
                    item_entities.insert().values(
                        item_id=item_id,
                        entity_name=_match_value(match, "entity_name"),
                        entity_type=_entity_type_value(_match_value(match, "entity_type")),
                        alias=_match_value(match, "alias"),
                        confidence=float(_match_value(match, "confidence")),
                        reason=_match_value(match, "reason"),
                        context_terms=json.dumps(
                            list(_match_value(match, "context_terms") or []),
                            ensure_ascii=True,
                        ),
                    )
                )
            self._upsert_entity_first_seen_from_matches(connection, item_id, match_rows)

    def list_item_matches(self, item_id: int) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(item_entities)
                .where(item_entities.c.item_id == item_id)
                .order_by(item_entities.c.id)
            ).mappings()
            return [
                {
                    "entity_name": row["entity_name"],
                    "entity_type": row["entity_type"],
                    "alias": row["alias"],
                    "confidence": row["confidence"],
                    "reason": row["reason"],
                    "context_terms": json.loads(row["context_terms"]),
                }
                for row in rows
            ]

    def upsert_entity_first_seen_from_item_matches(
        self, item_id: int, matches: Iterable[Mapping[str, Any] | Any]
    ) -> None:
        with self.engine.begin() as connection:
            self._upsert_entity_first_seen_from_matches(connection, item_id, list(matches))

    def get_entity_first_seen(
        self,
        entity_name: str,
        entity_type: str,
    ) -> dict[str, Any] | None:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    select(entity_first_seen).where(
                        entity_first_seen.c.entity_name == entity_name,
                        entity_first_seen.c.entity_type == _entity_type_value(entity_type),
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            return None
        return {
            "entity_name": row["entity_name"],
            "entity_type": row["entity_type"],
            "first_seen_at": row["first_seen_at"],
            "last_seen_at": row["last_seen_at"],
        }

    def prune_items_older_than(
        self,
        cutoff_collected_at: datetime,
        *,
        dry_run: bool = False,
    ) -> PruneResult:
        cutoff_value = parse_datetime_utc(cutoff_collected_at).isoformat()
        with self.engine.begin() as connection:
            item_ids = [
                int(row[0])
                for row in connection.execute(
                    select(items.c.id).where(items.c.collected_at < cutoff_value)
                ).all()
            ]
            if not item_ids:
                return PruneResult(items_deleted=0, item_entities_deleted=0, dry_run=dry_run)

            match_count = int(
                connection.execute(
                    select(func.count())
                    .select_from(item_entities)
                    .where(item_entities.c.item_id.in_(item_ids))
                ).scalar_one()
            )
            if dry_run:
                return PruneResult(
                    items_deleted=len(item_ids),
                    item_entities_deleted=match_count,
                    dry_run=True,
                )

            match_delete_result = connection.execute(
                delete(item_entities).where(item_entities.c.item_id.in_(item_ids))
            )
            item_delete_result = connection.execute(delete(items).where(items.c.id.in_(item_ids)))
            return PruneResult(
                items_deleted=_rowcount_or_expected(item_delete_result.rowcount, len(item_ids)),
                item_entities_deleted=_rowcount_or_expected(
                    match_delete_result.rowcount,
                    match_count,
                ),
                dry_run=False,
            )

    def _upsert_entity_first_seen_from_matches(
        self,
        connection: Any,
        item_id: int,
        matches: Iterable[Mapping[str, Any] | Any],
    ) -> None:
        if not matches:
            return
        collected_at_value = connection.execute(
            select(items.c.collected_at).where(items.c.id == item_id)
        ).scalar_one()
        seen_at = parse_datetime_utc(collected_at_value).isoformat()
        entity_keys = {
            (
                _match_value(match, "entity_name"),
                _entity_type_value(_match_value(match, "entity_type")),
            )
            for match in matches
        }
        for entity_name, entity_type in entity_keys:
            existing = (
                connection.execute(
                    select(entity_first_seen).where(
                        entity_first_seen.c.entity_name == entity_name,
                        entity_first_seen.c.entity_type == entity_type,
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is None:
                connection.execute(
                    entity_first_seen.insert().values(
                        entity_name=entity_name,
                        entity_type=entity_type,
                        first_seen_at=seen_at,
                        last_seen_at=seen_at,
                    )
                )
                continue
            first_seen_at = min(
                parse_datetime_utc(existing["first_seen_at"]),
                parse_datetime_utc(seen_at),
            )
            last_seen_at = max(
                parse_datetime_utc(existing["last_seen_at"]),
                parse_datetime_utc(seen_at),
            )
            connection.execute(
                update(entity_first_seen)
                .where(entity_first_seen.c.id == existing["id"])
                .values(
                    first_seen_at=first_seen_at.isoformat(),
                    last_seen_at=last_seen_at.isoformat(),
                )
            )


@dataclass(frozen=True)
class PruneResult:
    items_deleted: int
    item_entities_deleted: int
    dry_run: bool


class CollectorRunRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def record_run(
        self,
        source: SourceDefinition,
        *,
        status: str,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        items_seen: int = 0,
        items_stored: int = 0,
        error_message: str | None = None,
        error_type: str | None = None,
    ) -> int:
        values = {
            "source_name": source.name,
            "source_type": _source_type_value(source.type),
            "status": status,
            "started_at": _utc_now_if_none(started_at).isoformat(),
            "finished_at": _optional_datetime_value(finished_at),
            "items_seen": items_seen,
            "items_stored": items_stored,
            "error_message": error_message,
            "error_type": error_type,
        }
        with self.engine.begin() as connection:
            result = connection.execute(collector_runs.insert().values(**values))
            return int(result.inserted_primary_key[0])

    def list_recent_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(collector_runs).order_by(collector_runs.c.id.desc()).limit(limit)
            ).mappings()
            return [dict(row) for row in rows]


class SourceHealthRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def get_health(self, source: SourceDefinition) -> dict[str, Any] | None:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    select(source_health).where(
                        source_health.c.source_name == source.name,
                        source_health.c.source_type == _source_type_value(source.type),
                    )
                )
                .mappings()
                .one_or_none()
            )
        return dict(row) if row is not None else None

    def record_success(
        self,
        source: SourceDefinition,
        *,
        occurred_at: datetime | None = None,
    ) -> None:
        occurred_at_value = _utc_now_if_none(occurred_at).isoformat()
        existing = self.get_health(source)
        values = {
            "source_name": source.name,
            "source_type": _source_type_value(source.type),
            "consecutive_failures": 0,
            "last_success_at": occurred_at_value,
            "last_failure_at": existing["last_failure_at"] if existing else None,
            "unhealthy_until": None,
            "last_error_message": None,
        }
        self._upsert(source, values)

    def record_failure(
        self,
        source: SourceDefinition,
        *,
        error_message: str | None = None,
        occurred_at: datetime | None = None,
        max_failures: int,
        retention_hours: int,
    ) -> None:
        occurred = _utc_now_if_none(occurred_at)
        existing = self.get_health(source)
        consecutive_failures = int(existing["consecutive_failures"]) + 1 if existing else 1
        unhealthy_until = (
            (occurred + timedelta(hours=retention_hours)).isoformat()
            if consecutive_failures >= max_failures
            else None
        )
        values = {
            "source_name": source.name,
            "source_type": _source_type_value(source.type),
            "consecutive_failures": consecutive_failures,
            "last_success_at": existing["last_success_at"] if existing else None,
            "last_failure_at": occurred.isoformat(),
            "unhealthy_until": unhealthy_until,
            "last_error_message": error_message,
        }
        self._upsert(source, values)

    def is_unhealthy(self, source: SourceDefinition, *, now: datetime | None = None) -> bool:
        health = self.get_health(source)
        if health is None or health["unhealthy_until"] is None:
            return False
        until = parse_datetime_utc(health["unhealthy_until"])
        return _utc_now_if_none(now) <= until

    def clear_expired_unhealthy_sources(self, *, now: datetime | None = None) -> int:
        now_value = _utc_now_if_none(now)
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(source_health).where(source_health.c.unhealthy_until.is_not(None))
            ).mappings()
            expired_ids = [
                row["id"] for row in rows if parse_datetime_utc(row["unhealthy_until"]) < now_value
            ]
            if not expired_ids:
                return 0
            connection.execute(
                update(source_health)
                .where(source_health.c.id.in_(expired_ids))
                .values(consecutive_failures=0, unhealthy_until=None)
            )
            return len(expired_ids)

    def _upsert(self, source: SourceDefinition, values: dict[str, Any]) -> None:
        with self.engine.begin() as connection:
            existing_id = connection.execute(
                select(source_health.c.id).where(
                    source_health.c.source_name == source.name,
                    source_health.c.source_type == _source_type_value(source.type),
                )
            ).scalar_one_or_none()
            if existing_id is None:
                connection.execute(source_health.insert().values(**values))
            else:
                connection.execute(
                    update(source_health).where(source_health.c.id == existing_id).values(**values)
                )


def _match_value(match: Mapping[str, Any] | Any, key: str) -> Any:
    if isinstance(match, Mapping):
        return match[key]
    return getattr(match, key)


def _entity_type_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _source_type_value(value: SourceType | str) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _utc_now_if_none(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(tz=UTC)
    return parse_datetime_utc(value)


def _optional_datetime_value(value: datetime | None) -> str | None:
    return None if value is None else parse_datetime_utc(value).isoformat()


def _rowcount_or_expected(rowcount: int | None, expected: int) -> int:
    if rowcount is None or rowcount < 0:
        return expected
    return int(rowcount)
