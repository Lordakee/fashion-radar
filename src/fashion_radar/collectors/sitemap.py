from __future__ import annotations

from datetime import datetime

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.source import SourceDefinition


class SitemapCollector:
    """Collector for ``sitemap`` sources.

    Stage 212 is plumbing-only: ``collect`` is a no-op stub that returns a
    successful result with no items so the collector can be registered in the
    default collector map and exercised end-to-end by ``collect_sources``.
    Real sitemap discovery + trafilatura extraction lands in Stage 214.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
    ) -> CollectorResult:
        return CollectorResult.success(source, items=[], started_at=started_at)
