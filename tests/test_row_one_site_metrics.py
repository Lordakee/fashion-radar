from __future__ import annotations

import json
from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
)
from fashion_radar.row_one.site_metrics import (
    build_row_one_local_article_metrics,
    build_row_one_local_article_site_metrics,
    row_one_local_article_site_metrics_payload,
)

AS_OF = datetime(2026, 7, 6, 4, 0, tzinfo=UTC)


def test_local_article_site_metrics_are_zero_without_sidecars(tmp_path) -> None:
    metrics = build_row_one_local_article_site_metrics(tmp_path)

    assert metrics.article_count == 0
    assert metrics.paragraph_count == 0
    assert metrics.organized_section_count == 0
    assert metrics.source_count == 0
    assert row_one_local_article_site_metrics_payload(metrics) == {
        "article_count": 0,
        "paragraph_count": 0,
        "organized_section_count": 0,
        "source_count": 0,
    }


def test_local_article_site_metrics_count_publishable_sidecars(tmp_path) -> None:
    _write_article(
        tmp_path,
        "the-row-a-1234567890",
        source_name="Vogue Business",
        paragraphs=["One paragraph.", "   ", "Second paragraph."],
        organized_sections=2,
    )
    _write_article(
        tmp_path,
        "coach-b-1234567890",
        source_name="Vogue Business",
        paragraphs=["Coach paragraph."],
        organized_sections=1,
    )
    _write_article(
        tmp_path,
        "purse-c-1234567890",
        source_name="PurseBlog",
        paragraphs=["Bag paragraph."],
        organized_sections=0,
    )

    metrics = build_row_one_local_article_site_metrics(tmp_path)

    assert metrics.article_count == 3
    assert metrics.paragraph_count == 4
    assert metrics.organized_section_count == 3
    assert metrics.source_count == 2


def test_local_article_site_metrics_count_valid_empty_sidecars_separately_from_paragraphs(
    tmp_path,
) -> None:
    _write_article(
        tmp_path,
        "empty-body-1234567890",
        source_name="Local Desk",
        paragraphs=[],
        organized_sections=0,
    )
    (tmp_path / "data" / "articles" / "invalid.json").write_text(
        "{not json",
        encoding="utf-8",
    )

    metrics = build_row_one_local_article_site_metrics(tmp_path)

    assert metrics.article_count == 1
    assert metrics.paragraph_count == 0
    assert metrics.organized_section_count == 0
    assert metrics.source_count == 1


def test_local_article_metrics_count_current_render_articles_without_scanning_site(
    tmp_path,
) -> None:
    _write_article(
        tmp_path,
        "stale-sidecar-1234567890",
        source_name="Old Source",
        paragraphs=["Stale paragraph."],
        organized_sections=0,
    )
    current_article = RowOneLocalArticle(
        story_id="current-story-1234567890",
        title="Current article",
        url="https://example.com/current",
        source_name="Current Source",
        extracted_at=AS_OF,
        paragraphs=["Current paragraph.", "   "],
    )

    metrics = build_row_one_local_article_metrics([current_article])

    assert metrics.article_count == 1
    assert metrics.paragraph_count == 1
    assert metrics.organized_section_count == 0
    assert metrics.source_count == 1


def _write_article(
    site_dir,
    story_id: str,
    *,
    source_name: str,
    paragraphs: list[str],
    organized_sections: int,
) -> None:
    articles_dir = site_dir / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    article = RowOneLocalArticle(
        story_id=story_id,
        title=f"{story_id} article",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs,
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="要点", en="Takeaways"),
                items=[],
            )
            for _ in range(organized_sections)
        ],
    )
    (articles_dir / f"{story_id}.json").write_text(
        json.dumps(article.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )
