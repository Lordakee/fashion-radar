from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_coverage import (
    build_row_one_saved_article_coverage,
)

AS_OF = datetime(2026, 7, 6, 4, 0, tzinfo=UTC)


def _story(story_id: str, headline: str, *, section_key: str = "top_stories") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        story_type="tracked_entity",
        headline=headline,
        summary=LocalizedText(zh=f"{headline} 摘要", en=f"{headline} summary"),
        why_it_matters=LocalizedText(zh="重要。", en="Important."),
        editorial_takeaway=LocalizedText(zh="编辑判断。", en="Editorial read."),
        signal_context=LocalizedText(zh="信号背景。", en="Signal context."),
        reader_path=LocalizedText(zh="阅读路径。", en="Reader path."),
        source_name="Story Source",
        source_url="https://example.com/story",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="今日摘要。", en="Daily summary."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="重点。", en="Top reads."),
            ),
            RowOneSection(
                key="brand_moves",
                title=LocalizedText(zh="品牌动态", en="Brand Moves"),
                dek=LocalizedText(zh="品牌。", en="Brands."),
            ),
        ],
        stories=list(stories),
    )


def _article(
    story_id: str,
    *,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    organized_sections: int = 1,
) -> RowOneLocalArticle:
    sections = [
        RowOneLocalArticleContentSection(
            key="takeaways",
            title=LocalizedText(zh="要点", en="Takeaways"),
        )
        for _ in range(organized_sections)
    ]
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"{story_id} article",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        content_sections=sections,
    )


def test_saved_article_coverage_counts_only_current_publishable_articles() -> None:
    story_a = _story("the-row-a-1234567890", "The Row coverage")
    story_b = _story("coach-b-1234567890", "Coach coverage", section_key="brand_moves")
    coverage = build_row_one_saved_article_coverage(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                source_name="Vogue Business",
                paragraphs=["A paragraph.", "   ", "Another paragraph."],
                organized_sections=2,
            ),
            story_b.id: _article(
                story_b.id,
                source_name="Vogue Business",
                paragraphs=["Coach paragraph."],
                organized_sections=1,
            ),
            "not-in-edition-1234567890": _article("not-in-edition-1234567890"),
            "bad id": _article("bad id"),
        },
    )

    assert coverage is not None
    assert coverage.article_count == 2
    assert coverage.saved_paragraph_count == 3
    assert coverage.organized_section_count == 3
    assert coverage.source_count == 1
    assert [(source.name, source.article_count) for source in coverage.sources] == [
        ("Vogue Business", 2)
    ]
    assert [item.title.en for item in coverage.items] == [
        "The Row coverage",
        "Coach coverage",
    ]
    assert [item.section_title.en for item in coverage.items] == [
        "Top Stories",
        "Brand Moves",
    ]
    assert [item.saved_paragraph_count for item in coverage.items] == [2, 1]
    assert [item.organized_section_count for item in coverage.items] == [2, 1]
    assert coverage.items[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-digest"
    )


def test_saved_article_coverage_omits_when_no_publishable_articles() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")

    assert build_row_one_saved_article_coverage(_edition(story), {}) is None
    assert (
        build_row_one_saved_article_coverage(
            _edition(story),
            {story.id: _article(story.id, paragraphs=["   "])},
        )
        is None
    )


def test_saved_article_coverage_excludes_invalid_detail_paths() -> None:
    valid_story = _story("the-row-a-1234567890", "The Row coverage")
    invalid_story = _story("coach-b-1234567890", "Coach coverage").model_copy(
        update={"detail_path": "../private.html"}
    )

    coverage = build_row_one_saved_article_coverage(
        _edition(valid_story, invalid_story),
        {
            valid_story.id: _article(valid_story.id),
            invalid_story.id: _article(invalid_story.id),
        },
    )

    assert coverage is not None
    assert coverage.article_count == 1
    assert [item.title.en for item in coverage.items] == ["The Row coverage"]


def test_saved_article_coverage_limits_read_queue_to_four_in_edition_order() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}") for index in range(1, 7)]
    coverage = build_row_one_saved_article_coverage(
        _edition(*stories),
        {
            story.id: _article(
                story.id,
                source_name="Vogue" if index % 2 else "Business of Fashion",
            )
            for index, story in enumerate(stories, start=1)
        },
    )

    assert coverage is not None
    assert coverage.article_count == 6
    assert len(coverage.items) == 4
    assert [item.title.en for item in coverage.items] == [
        "Story 1",
        "Story 2",
        "Story 3",
        "Story 4",
    ]
    # Source chips preserve first-seen source order from the edition story order.
    assert [(source.name, source.article_count) for source in coverage.sources] == [
        ("Vogue", 3),
        ("Business of Fashion", 3),
    ]
