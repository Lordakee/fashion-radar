from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from fashion_radar.models.source import SourceDefinition
from fashion_radar.row_one.site_metrics import (
    RowOneLocalArticleSiteMetrics,
    row_one_local_article_site_metrics_payload,
)
from fashion_radar.row_one.utils import safe_external_url


@dataclass(frozen=True)
class RowOneArticleReadinessSourceSummary:
    total_sources: int = 0
    enabled_sources: int = 0
    article_enabled_sources: int = 0


@dataclass(frozen=True)
class RowOneArticleReadinessStoryCoverage:
    story_count: int = 0
    eligible_story_count: int = 0
    disabled_source_count: int = 0
    missing_source_count: int = 0


@dataclass(frozen=True)
class RowOneArticleReadiness:
    source_summary: RowOneArticleReadinessSourceSummary
    story_coverage: RowOneArticleReadinessStoryCoverage
    local_article_metrics: RowOneLocalArticleSiteMetrics
    recommendations: tuple[str, ...] = ()


def build_row_one_article_readiness(
    *,
    sources: Sequence[SourceDefinition],
    edition_payload: Mapping[str, Any] | None,
    local_article_metrics: RowOneLocalArticleSiteMetrics,
) -> RowOneArticleReadiness:
    source_summary = _source_summary(sources)
    story_coverage = _story_coverage(sources, edition_payload)
    return RowOneArticleReadiness(
        source_summary=source_summary,
        story_coverage=story_coverage,
        local_article_metrics=local_article_metrics,
        recommendations=_recommendations(source_summary, story_coverage),
    )


def row_one_article_readiness_payload(
    readiness: RowOneArticleReadiness,
) -> dict[str, object]:
    return {
        "source_summary": {
            "total_sources": readiness.source_summary.total_sources,
            "enabled_sources": readiness.source_summary.enabled_sources,
            "article_enabled_sources": readiness.source_summary.article_enabled_sources,
        },
        "story_coverage": {
            "story_count": readiness.story_coverage.story_count,
            "eligible_story_count": readiness.story_coverage.eligible_story_count,
            "disabled_source_count": readiness.story_coverage.disabled_source_count,
            "missing_source_count": readiness.story_coverage.missing_source_count,
        },
        "local_articles": row_one_local_article_site_metrics_payload(
            readiness.local_article_metrics
        ),
        "recommendations": list(readiness.recommendations),
    }


def _source_summary(
    sources: Sequence[SourceDefinition],
) -> RowOneArticleReadinessSourceSummary:
    enabled_sources = [source for source in sources if source.enabled]
    return RowOneArticleReadinessSourceSummary(
        total_sources=len(sources),
        enabled_sources=len(enabled_sources),
        article_enabled_sources=sum(
            1 for source in enabled_sources if source.row_one_article.enabled
        ),
    )


def _story_coverage(
    sources: Sequence[SourceDefinition],
    edition_payload: Mapping[str, Any] | None,
) -> RowOneArticleReadinessStoryCoverage:
    if edition_payload is None:
        return RowOneArticleReadinessStoryCoverage()
    raw_stories = edition_payload.get("stories")
    if not isinstance(raw_stories, list):
        return RowOneArticleReadinessStoryCoverage()
    source_by_name = {source.name: source for source in sources if source.enabled}
    eligible_story_count = 0
    disabled_source_count = 0
    missing_source_count = 0
    story_count = 0
    for story in raw_stories:
        if not isinstance(story, Mapping):
            continue
        story_count += 1
        source_name = story.get("source_name")
        if not isinstance(source_name, str) or not source_name.strip():
            missing_source_count += 1
            continue
        source = source_by_name.get(source_name)
        if source is None:
            source = _source_by_story_url_host(story, sources)
        if source is None:
            missing_source_count += 1
            continue
        if source.row_one_article.enabled:
            eligible_story_count += 1
        else:
            disabled_source_count += 1
    return RowOneArticleReadinessStoryCoverage(
        story_count=story_count,
        eligible_story_count=eligible_story_count,
        disabled_source_count=disabled_source_count,
        missing_source_count=missing_source_count,
    )


def _source_by_story_url_host(
    story: Mapping[str, Any],
    sources: Sequence[SourceDefinition],
) -> SourceDefinition | None:
    story_url = story.get("source_url")
    story_host = _hostname(safe_external_url(story_url if isinstance(story_url, str) else None))
    if story_host is None:
        return None
    for source in sources:
        if not source.enabled:
            continue
        source_hosts = {_hostname(url) for url in [source.url, *source.seed_urls] if url}
        if story_host in source_hosts:
            return source
    return None


def _hostname(url: str | None) -> str | None:
    if url is None:
        return None
    parsed = urlsplit(url)
    return parsed.hostname.casefold() if parsed.hostname else None


def _recommendations(
    source_summary: RowOneArticleReadinessSourceSummary,
    story_coverage: RowOneArticleReadinessStoryCoverage,
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if story_coverage.story_count == 0:
        recommendations.append(
            "Build or refresh ROW ONE before evaluating current story source coverage."
        )
    if source_summary.article_enabled_sources == 0:
        recommendations.append(
            "Enable row_one_article.enabled: true in sources.yaml on sources that should "
            "produce ROW ONE local article sidecars."
        )
    elif story_coverage.story_count > 0 and story_coverage.eligible_story_count == 0:
        recommendations.append(
            "Current ROW ONE stories come from sources without row_one_article.enabled: "
            "true in sources.yaml."
        )
    return tuple(recommendations)
