from __future__ import annotations

from datetime import datetime

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.source import SourceDefinition


class InstagramCollector:
    """Collector for ``instagram`` sources.

    Stage 231 is plumbing-only: ``collect`` is a no-op stub so the collector can
    be registered and exercised end-to-end. Real instaloader subprocess
    integration lands in Stage 232.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        return CollectorResult.success(source, items=[], started_at=started_at)
