"""Evaluate whether a ROW ONE refresh has enough current collector output.

Collectors synthesize ``CollectedItem.published_at`` when a source does not
provide a date. This evaluator treats that normalized timestamp like any other
published timestamp.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from fashion_radar.collectors.base import CollectorResult, CollectorRunStatus
from fashion_radar.settings import DailyContentAcceptanceSettings
from fashion_radar.utils.dates import parse_datetime_utc


@dataclass(frozen=True)
class DailyContentAcceptanceVerdict:
    accepted: bool
    successful_collector_count: int
    fresh_item_count: int
    min_successful_collectors: int
    min_fresh_items: int
    max_fresh_item_age_hours: int
    reasons: tuple[str, ...]


def evaluate_daily_content_acceptance(
    *,
    results: Sequence[CollectorResult],
    settings: DailyContentAcceptanceSettings,
    as_of: str | datetime,
) -> DailyContentAcceptanceVerdict:
    """Return a pure acceptance verdict for the current collector run."""
    as_of_utc = parse_datetime_utc(as_of)
    max_fresh_item_age = timedelta(hours=settings.max_fresh_item_age_hours)
    successful_collector_count = 0
    fresh_item_count = 0

    for result in results:
        if result.status.status != CollectorRunStatus.SUCCESS:
            continue

        successful_collector_count += 1
        for item in result.items:
            item_age = as_of_utc - parse_datetime_utc(item.published_at)
            if timedelta() <= item_age <= max_fresh_item_age:
                fresh_item_count += 1

    reasons: list[str] = []
    if successful_collector_count < settings.min_successful_collectors:
        reasons.append(
            "insufficient successful collectors: "
            f"found {successful_collector_count}, "
            f"minimum {settings.min_successful_collectors}"
        )
    if fresh_item_count < settings.min_fresh_items:
        reasons.append(
            f"insufficient fresh items: found {fresh_item_count}, "
            f"minimum {settings.min_fresh_items}"
        )

    return DailyContentAcceptanceVerdict(
        accepted=not reasons,
        successful_collector_count=successful_collector_count,
        fresh_item_count=fresh_item_count,
        min_successful_collectors=settings.min_successful_collectors,
        min_fresh_items=settings.min_fresh_items,
        max_fresh_item_age_hours=settings.max_fresh_item_age_hours,
        reasons=tuple(reasons),
    )
