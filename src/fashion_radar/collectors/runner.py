from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.engine import Engine

from fashion_radar.collectors.base import CollectorResult, CollectorRunStatus
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.models.source import SourceDefinition, SourceType


class Collector(Protocol):
    def collect(self, source: SourceDefinition) -> CollectorResult: ...


def collect_sources(
    sources: Sequence[SourceDefinition],
    *,
    engine: Engine,
    collectors: Mapping[str | SourceType, Collector],
    now: datetime | None = None,
) -> list[CollectorResult]:
    item_repository = ItemRepository(engine)
    run_repository = CollectorRunRepository(engine)
    health_repository = SourceHealthRepository(engine)
    collected_at = now or datetime.now(tz=UTC)
    results: list[CollectorResult] = []

    for source in sources:
        if not source.enabled:
            result = CollectorResult.skipped(
                source,
                reason="source disabled",
                started_at=collected_at,
                finished_at=collected_at,
            )
            _record_run(run_repository, source, result, items_stored=0)
            results.append(result)
            continue

        if health_repository.is_unhealthy(source, now=collected_at):
            result = CollectorResult.skipped(
                source,
                reason="source unhealthy",
                started_at=collected_at,
                finished_at=collected_at,
            )
            _record_run(run_repository, source, result, items_stored=0)
            results.append(result)
            continue

        try:
            result = _collector_for(source, collectors).collect(source)
        except Exception as exc:
            result = CollectorResult.failed(
                source,
                error=exc,
                started_at=collected_at,
                finished_at=collected_at,
            )

        items_stored = 0
        if result.status.status == CollectorRunStatus.SUCCESS:
            for item in result.items:
                item_repository.upsert_item(item)
                items_stored += 1
            health_repository.record_success(source, occurred_at=result.status.finished_at)
        elif result.status.status == CollectorRunStatus.FAILED:
            health_repository.record_failure(
                source,
                error_message=result.status.error_message,
                occurred_at=result.status.finished_at,
                max_failures=source.health.max_failures,
                retention_hours=source.health.retention_hours,
            )

        _record_run(run_repository, source, result, items_stored=items_stored)
        results.append(result)

    return results


def _collector_for(
    source: SourceDefinition,
    collectors: Mapping[str | SourceType, Collector],
) -> Collector:
    for key in (source.name, source.type, source.type.value):
        if key in collectors:
            return collectors[key]
    raise KeyError(f"No collector configured for source {source.name!r}")


def _record_run(
    run_repository: CollectorRunRepository,
    source: SourceDefinition,
    result: CollectorResult,
    *,
    items_stored: int,
) -> None:
    run_repository.record_run(
        source,
        status=result.status.status.value,
        started_at=result.status.started_at,
        finished_at=result.status.finished_at,
        items_seen=result.status.items_seen,
        items_stored=items_stored,
        error_message=result.status.error_message,
        error_type=result.status.error_type,
    )
