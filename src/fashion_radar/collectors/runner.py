from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.engine import Engine

from fashion_radar.collectors.article import ArticleExtractionResult, extract_article
from fashion_radar.collectors.base import CollectorResult, CollectorRunStatus
from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.utils.http import FashionHttpClient


class Collector(Protocol):
    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult: ...


ArticleExtractor = Callable[[SourceDefinition, CollectedItem], ArticleExtractionResult]


def collect_sources(
    sources: Sequence[SourceDefinition],
    *,
    engine: Engine,
    collectors: Mapping[str | SourceType, Collector],
    article_extractor: ArticleExtractor | None = None,
    now: datetime | None = None,
) -> list[CollectorResult]:
    item_repository = ItemRepository(engine)
    run_repository = CollectorRunRepository(engine)
    health_repository = SourceHealthRepository(engine)
    results: list[CollectorResult] = []

    for source in sources:
        started_at = now or datetime.now(tz=UTC)
        if not source.enabled:
            result = CollectorResult.skipped(
                source,
                reason="source disabled",
                started_at=started_at,
                finished_at=started_at,
            )
            _record_run(run_repository, source, result, items_stored=0)
            results.append(result)
            continue

        if health_repository.is_unhealthy(source, now=started_at):
            result = CollectorResult.skipped(
                source,
                reason="source unhealthy",
                started_at=started_at,
                finished_at=started_at,
            )
            _record_run(run_repository, source, result, items_stored=0)
            results.append(result)
            continue

        source_article_extractor = article_extractor
        close_article_extractor: Callable[[], None] | None = None
        if (
            source_article_extractor is None
            and source.article.enabled
            and source.type not in {SourceType.HTML, SourceType.SITEMAP}
        ):
            source_article_extractor, close_article_extractor = _default_article_extractor(source)

        try:
            result = _collector_for(source, collectors).collect(source, started_at=started_at)
        except Exception as exc:
            result = CollectorResult.failed(
                source,
                error=exc,
                started_at=started_at,
                finished_at=datetime.now(tz=UTC),
            )
        finally:
            if close_article_extractor is not None and result.status.status != (
                CollectorRunStatus.SUCCESS
            ):
                close_article_extractor()

        items_stored = 0
        if result.status.status == CollectorRunStatus.SUCCESS:
            if source_article_extractor is not None and source.type not in {
                SourceType.HTML,
                SourceType.SITEMAP,
            }:
                result = result.model_copy(
                    update={
                        "items": _enrich_items_with_article_snippets(
                            source,
                            result.items,
                            source_article_extractor,
                        )
                    }
                )
            if close_article_extractor is not None:
                close_article_extractor()
            for item in result.items:
                item_repository.upsert_item(
                    item,
                    source_weight=source.weight,
                    collected_at=started_at,
                )
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


def _default_article_extractor(
    source: SourceDefinition,
) -> tuple[ArticleExtractor, Callable[[], None]]:
    client = FashionHttpClient(source.http)
    robots_checker = RobotsPolicyChecker(lambda url: client.get_response(url))

    def extractor(_source: SourceDefinition, item: CollectedItem) -> ArticleExtractionResult:
        return extract_article(
            item.url,
            source=source,
            html_fetcher=client.get_text,
            robots_checker=robots_checker,
        )

    return extractor, client.close


def _enrich_items_with_article_snippets(
    source: SourceDefinition,
    items: Sequence[CollectedItem],
    article_extractor: ArticleExtractor,
) -> list[CollectedItem]:
    enriched: list[CollectedItem] = []
    for item in items:
        try:
            extracted = article_extractor(source, item)
        except Exception:
            enriched.append(item)
            continue
        if not extracted.skipped and extracted.text:
            enriched.append(item.model_copy(update={"summary": extracted.text}))
        else:
            enriched.append(item)
    return enriched


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
