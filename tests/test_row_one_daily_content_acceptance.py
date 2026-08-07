from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from fashion_radar.collectors.base import (
    CollectorResult,
    CollectorRunStatus,
    CollectorRunSummary,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.row_one.daily_content_acceptance import (
    DailyContentAcceptanceVerdict,
    evaluate_daily_content_acceptance,
)
from fashion_radar.settings import DailyContentAcceptanceSettings

AS_OF = datetime(2026, 8, 7, 4, 0, tzinfo=UTC)
STARTED_AT = datetime(2026, 8, 7, 3, 0, tzinfo=UTC)
FINISHED_AT = datetime(2026, 8, 7, 3, 1, tzinfo=UTC)


def _source(name: str) -> SourceDefinition:
    return SourceDefinition(
        name=name,
        type=SourceType.RSS,
        url=f"https://example.com/{name.lower().replace(' ', '-')}.xml",
    )


def _item(source: SourceDefinition, *, published_at: datetime) -> CollectedItem:
    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=f"https://example.com/{source.name.lower().replace(' ', '-')}/story",
        title=f"{source.name} story",
        published_at=published_at,
        summary="A collected fashion signal.",
    )


def _result(
    source: SourceDefinition,
    status: CollectorRunStatus,
    *,
    items: list[CollectedItem] | None = None,
) -> CollectorResult:
    collected_items = [] if items is None else items
    return CollectorResult(
        status=CollectorRunSummary(
            source_name=source.name,
            source_type=source.type,
            status=status,
            started_at=STARTED_AT,
            finished_at=FINISHED_AT,
            items_seen=len(collected_items),
            items_collected=len(collected_items),
        ),
        items=collected_items,
    )


def test_accepts_healthy_successful_collector_with_one_fresh_item() -> None:
    source = _source("Healthy Feed")
    results = [
        _result(
            source,
            CollectorRunStatus.SUCCESS,
            items=[_item(source, published_at=AS_OF - timedelta(hours=48))],
        )
    ]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict == DailyContentAcceptanceVerdict(
        accepted=True,
        successful_collector_count=1,
        fresh_item_count=1,
        min_successful_collectors=1,
        min_fresh_items=1,
        max_fresh_item_age_hours=48,
        reasons=(),
    )
    with pytest.raises(FrozenInstanceError):
        verdict.accepted = False


def test_rejects_empty_result_list_with_insufficient_success_and_fresh_reasons() -> None:
    verdict = evaluate_daily_content_acceptance(
        results=[],
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 0
    assert verdict.fresh_item_count == 0
    assert verdict.reasons == (
        "insufficient successful collectors: found 0, minimum 1",
        "insufficient fresh items: found 0, minimum 1",
    )


def test_rejects_all_failed_collectors_with_the_same_insufficient_counts() -> None:
    results = [
        _result(_source("Failed Feed One"), CollectorRunStatus.FAILED),
        _result(_source("Failed Feed Two"), CollectorRunStatus.FAILED),
    ]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 0
    assert verdict.fresh_item_count == 0
    assert verdict.reasons == (
        "insufficient successful collectors: found 0, minimum 1",
        "insufficient fresh items: found 0, minimum 1",
    )


def test_rejects_skipped_only_collectors_with_no_successful_source() -> None:
    results = [
        _result(_source("Skipped Feed One"), CollectorRunStatus.SKIPPED),
        _result(_source("Skipped Feed Two"), CollectorRunStatus.SKIPPED),
    ]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 0
    assert verdict.fresh_item_count == 0
    assert verdict.reasons == (
        "insufficient successful collectors: found 0, minimum 1",
        "insufficient fresh items: found 0, minimum 1",
    )


def test_rejects_successful_collector_with_zero_items_for_insufficient_fresh_items() -> None:
    results = [_result(_source("Empty Success Feed"), CollectorRunStatus.SUCCESS)]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 1
    assert verdict.fresh_item_count == 0
    assert verdict.reasons == ("insufficient fresh items: found 0, minimum 1",)


def test_rejects_explicitly_stale_item_for_insufficient_fresh_items() -> None:
    source = _source("Stale Feed")
    results = [
        _result(
            source,
            CollectorRunStatus.SUCCESS,
            items=[_item(source, published_at=AS_OF - timedelta(hours=48, seconds=1))],
        )
    ]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 1
    assert verdict.fresh_item_count == 0
    assert verdict.reasons == ("insufficient fresh items: found 0, minimum 1",)


def test_rejects_future_dated_item_as_not_fresh() -> None:
    source = _source("Future Feed")
    results = [
        _result(
            source,
            CollectorRunStatus.SUCCESS,
            items=[_item(source, published_at=AS_OF + timedelta(seconds=1))],
        )
    ]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 1
    assert verdict.fresh_item_count == 0
    assert verdict.reasons == ("insufficient fresh items: found 0, minimum 1",)


def test_orders_reasons_counts_only_successes_and_does_not_mutate_inputs() -> None:
    successful_source = _source("Successful Feed")
    failed_source = _source("Failed Feed")
    skipped_source = _source("Skipped Feed")
    results = [
        _result(
            successful_source,
            CollectorRunStatus.SUCCESS,
            items=[_item(successful_source, published_at=AS_OF)],
        ),
        _result(failed_source, CollectorRunStatus.FAILED),
        _result(skipped_source, CollectorRunStatus.SKIPPED),
    ]
    before = [result.model_dump(mode="json") for result in results]

    verdict = evaluate_daily_content_acceptance(
        results=results,
        settings=DailyContentAcceptanceSettings(
            min_successful_collectors=2,
            min_fresh_items=2,
            max_fresh_item_age_hours=48,
        ),
        as_of=AS_OF,
    )

    assert verdict.accepted is False
    assert verdict.successful_collector_count == 1
    assert verdict.fresh_item_count == 1
    assert verdict.reasons == (
        "insufficient successful collectors: found 1, minimum 2",
        "insufficient fresh items: found 1, minimum 2",
    )
    assert [result.model_dump(mode="json") for result in results] == before
