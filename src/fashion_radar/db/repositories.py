from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import item_entities, items
from fashion_radar.models.item import CollectedItem
from fashion_radar.utils.hashing import content_hash, normalize_url


class ItemRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def upsert_item(self, item: CollectedItem) -> int:
        normalized = normalize_url(item.url)
        values = {
            "source_name": item.source_name,
            "source_type": item.source_type.value,
            "url": item.url,
            "normalized_url": normalized,
            "title": item.title,
            "published_at": item.published_at.isoformat(),
            "summary": item.summary,
            "content_hash": content_hash(
                title=item.title,
                published_at=item.published_at,
                source_name=item.source_name,
                summary=item.summary,
            ),
        }
        with self.engine.begin() as connection:
            existing_id = connection.execute(
                select(items.c.id).where(items.c.normalized_url == normalized)
            ).scalar_one_or_none()
            if existing_id is not None:
                connection.execute(update(items).where(items.c.id == existing_id).values(**values))
                return int(existing_id)
            result = connection.execute(items.insert().values(**values))
            return int(result.inserted_primary_key[0])

    def count_items(self) -> int:
        with self.engine.connect() as connection:
            return int(connection.execute(select(func.count()).select_from(items)).scalar_one())

    def get_item(self, item_id: int) -> dict[str, Any]:
        with self.engine.connect() as connection:
            row = connection.execute(select(items).where(items.c.id == item_id)).mappings().one()
        return dict(row)

    def replace_item_matches(
        self, item_id: int, matches: Iterable[Mapping[str, Any] | Any]
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(delete(item_entities).where(item_entities.c.item_id == item_id))
            for match in matches:
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


def _match_value(match: Mapping[str, Any] | Any, key: str) -> Any:
    if isinstance(match, Mapping):
        return match[key]
    return getattr(match, key)


def _entity_type_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)
