from __future__ import annotations

from typing import Any

from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.row_one.article_readiness import (
    build_row_one_article_readiness,
    row_one_article_readiness_payload,
)
from fashion_radar.row_one.site_metrics import RowOneLocalArticleSiteMetrics


def _rss_source(name: str, *, row_one_enabled: bool = False) -> SourceDefinition:
    slug = name.casefold().replace(" ", "-")
    return SourceDefinition(
        name=name,
        type=SourceType.RSS,
        url=f"https://{slug}.example/feed.xml",
        article={"enabled": False},
        row_one_article={"enabled": row_one_enabled, "max_chars": 2400},
    )


def _edition_payload(source_names: list[str]) -> dict[str, Any]:
    return {
        "contract_version": "row-one-app/v7",
        "story_count": len(source_names),
        "stories": [
            {
                "id": f"story-{index}-1234567890",
                "source_name": source_name,
                "source_url": (
                    f"https://{source_name.casefold().replace(' ', '-')}.example/{index}"
                ),
            }
            for index, source_name in enumerate(source_names)
        ],
    }


def test_article_readiness_counts_article_enabled_sources_and_story_coverage() -> None:
    readiness = build_row_one_article_readiness(
        sources=[
            _rss_source("Fashionista", row_one_enabled=True),
            _rss_source("Legacy Fashion", row_one_enabled=False),
        ],
        edition_payload=_edition_payload(["Fashionista", "Legacy Fashion", "Unknown"]),
        local_article_metrics=RowOneLocalArticleSiteMetrics(
            article_count=1,
            paragraph_count=4,
            organized_section_count=2,
            source_count=1,
        ),
    )

    assert readiness.source_summary.total_sources == 2
    assert readiness.source_summary.enabled_sources == 2
    assert readiness.source_summary.article_enabled_sources == 1
    assert readiness.story_coverage.story_count == 3
    assert readiness.story_coverage.eligible_story_count == 1
    assert readiness.story_coverage.disabled_source_count == 1
    assert readiness.story_coverage.missing_source_count == 1
    assert not readiness.recommendations


def test_article_readiness_recommends_row_one_article_when_no_stories_are_eligible() -> None:
    readiness = build_row_one_article_readiness(
        sources=[_rss_source("Legacy Fashion", row_one_enabled=False)],
        edition_payload=_edition_payload(["Legacy Fashion"]),
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert readiness.story_coverage.eligible_story_count == 0
    assert any("row_one_article.enabled: true" in item for item in readiness.recommendations)


def test_article_readiness_matches_enabled_source_by_story_url_host_when_name_differs() -> None:
    readiness = build_row_one_article_readiness(
        sources=[
            SourceDefinition(
                name="Fashionista",
                type=SourceType.RSS,
                url="https://shared.example/feed.xml",
                article={"enabled": False},
                row_one_article={"enabled": True, "max_chars": 2400},
            )
        ],
        edition_payload={
            "contract_version": "row-one-app/v7",
            "story_count": 1,
            "stories": [
                {
                    "id": "story-host-fallback-1234567890",
                    "source_name": "Historical Source",
                    "source_url": "https://shared.example/articles/the-row",
                }
            ],
        },
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert readiness.story_coverage.story_count == 1
    assert readiness.story_coverage.eligible_story_count == 1
    assert readiness.story_coverage.disabled_source_count == 0
    assert readiness.story_coverage.missing_source_count == 0
    assert not readiness.recommendations


def test_article_readiness_counts_host_matched_article_disabled_source_as_disabled() -> None:
    readiness = build_row_one_article_readiness(
        sources=[
            SourceDefinition(
                name="Legacy Fashion",
                type=SourceType.RSS,
                url="https://legacy.example/feed.xml",
                article={"enabled": False},
                row_one_article={"enabled": False, "max_chars": 2400},
            )
        ],
        edition_payload={
            "contract_version": "row-one-app/v7",
            "story_count": 1,
            "stories": [
                {
                    "id": "story-host-disabled-1234567890",
                    "source_name": "Historical Source",
                    "source_url": "https://legacy.example/articles/the-row",
                }
            ],
        },
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert readiness.story_coverage.story_count == 1
    assert readiness.story_coverage.eligible_story_count == 0
    assert readiness.story_coverage.disabled_source_count == 1
    assert readiness.story_coverage.missing_source_count == 0
    assert any("row_one_article.enabled: true" in item for item in readiness.recommendations)


def test_article_readiness_payload_is_machine_readable() -> None:
    readiness = build_row_one_article_readiness(
        sources=[_rss_source("Fashionista", row_one_enabled=True)],
        edition_payload=None,
        local_article_metrics=RowOneLocalArticleSiteMetrics(),
    )

    assert row_one_article_readiness_payload(readiness) == {
        "source_summary": {
            "total_sources": 1,
            "enabled_sources": 1,
            "article_enabled_sources": 1,
        },
        "story_coverage": {
            "story_count": 0,
            "eligible_story_count": 0,
            "disabled_source_count": 0,
            "missing_source_count": 0,
        },
        "local_articles": {
            "article_count": 0,
            "paragraph_count": 0,
            "organized_section_count": 0,
            "source_count": 0,
        },
        "recommendations": [
            "Build or refresh ROW ONE before evaluating current story source coverage.",
        ],
    }
