from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_briefs import (
    build_row_one_saved_article_briefs,
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
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"{story_id} article",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh or [],
        content_sections=content_sections or [],
    )


def _content_item(
    label: str,
    *,
    body: str | None = None,
    body_zh: str | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=LocalizedText(zh=label, en=label),
        body=(
            LocalizedText(
                zh=body_zh if body_zh is not None else body or "",
                en=body or "",
            )
            if body is not None
            else None
        ),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    key: str,
    title: str,
    *,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,
        title=LocalizedText(zh=title, en=title),
        items=items or [],
    )


def test_saved_article_briefs_use_takeaway_and_reference_chips() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    coverage = build_row_one_saved_article_briefs(
        _edition(story),
        {
            story.id: _article(
                story.id,
                content_sections=[
                    _section(
                        "takeaways",
                        "Takeaways",
                        items=[
                            _content_item(
                                "Lead",
                                body="The Row pushed a quiet luxury merchandising signal.",
                                body_zh="The Row 释放安静奢华陈列信号。",
                                paragraph_indices=[0],
                            )
                        ],
                    ),
                    _section(
                        "entities",
                        "Entities",
                        items=[
                            _content_item(
                                "Brands",
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    ),
                                    RowOneReference(
                                        name="Mary-Kate Olsen",
                                        type="person",
                                        label="designer",
                                    ),
                                ],
                            )
                        ],
                    ),
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _content_item(
                                "Products",
                                references=[
                                    RowOneReference(name="Margaux", type="bag", label="product"),
                                    RowOneReference(name="Margaux", type="bag", label="product"),
                                ],
                            )
                        ],
                    ),
                ],
            )
        },
    )

    assert coverage is not None
    assert coverage.article_count == 1
    assert len(coverage.items) == 1
    item = coverage.items[0]
    assert item.title.en == "The Row coverage"
    assert item.section_title.en == "Top Stories"
    assert item.source_name == "Vogue Business"
    assert item.lead.en == "The Row pushed a quiet luxury merchandising signal."
    assert item.lead.zh == "The Row 释放安静奢华陈列信号。"
    assert item.detail_path == "details/the-row-a-1234567890.html#local-article-digest"
    assert [(ref.name, ref.type, ref.label) for ref in item.people_brands] == [
        ("The Row", "brand", "tracked"),
        ("Mary-Kate Olsen", "person", "designer"),
    ]
    assert [(ref.name, ref.type, ref.label) for ref in item.products] == [
        ("Margaux", "bag", "product"),
    ]


def test_saved_article_briefs_filter_invalid_articles_and_cap_cards() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}") for index in range(1, 7)]
    bad_path_story = _story("bad-path-1234567890", "Bad Path").model_copy(
        update={"detail_path": "../private.html"}
    )
    bad_id_story = _story("bad id", "Bad ID").model_copy(
        update={"detail_path": "details/bad-id-1234567890.html"}
    )
    mismatched_article_story = _story("mismatch-1234567890", "Mismatched Article")
    coverage = build_row_one_saved_article_briefs(
        _edition(*stories, bad_path_story, bad_id_story, mismatched_article_story),
        {
            **{
                story.id: _article(
                    story.id,
                    paragraphs=["   ", f"Paragraph {index}."],
                    paragraphs_zh=["   ", f"段落 {index}。"],
                )
                for index, story in enumerate(stories, start=1)
            },
            bad_path_story.id: _article(bad_path_story.id),
            bad_id_story.id: _article(bad_id_story.id),
            mismatched_article_story.id: _article("other-story-1234567890"),
            "not-in-edition-1234567890": _article("not-in-edition-1234567890"),
            "bad id": _article("bad id"),
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
    assert coverage.items[0].lead.en == "Paragraph 1."
    assert coverage.items[0].lead.zh == "段落 1。"


def test_saved_article_briefs_omit_without_publishable_articles() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")

    assert build_row_one_saved_article_briefs(_edition(story), {}) is None
    assert (
        build_row_one_saved_article_briefs(
            _edition(story),
            {story.id: _article(story.id, paragraphs=["   "])},
        )
        is None
    )
