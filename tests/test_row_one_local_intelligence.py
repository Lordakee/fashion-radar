from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.local_intelligence import build_row_one_local_article_intelligence
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 5, 4, 0, tzinfo=UTC)


def _story(
    story_id: str,
    headline: str,
    *,
    detail_path: str,
    source_name: str = "Vogue Business",
    story_type: str = "tracked_entity",
    heat_delta: int | None = None,
    entity_refs: list[RowOneReference] | None = None,
    product_refs: list[RowOneReference] | None = None,
    designer_refs: list[RowOneReference] | None = None,
    tags: list[str] | None = None,
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type=story_type,
        headline=headline,
        summary=LocalizedText(zh=f"{headline} 摘要", en=f"{headline} summary"),
        why_it_matters=LocalizedText(zh="为什么重要", en="Why it matters"),
        editorial_takeaway=LocalizedText(zh="编辑判断", en="Editorial takeaway"),
        signal_context=LocalizedText(zh="本地信号背景", en="Local signal context"),
        reader_path=LocalizedText(zh="先读本地正文", en="Read the local article first"),
        source_name=source_name,
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=detail_path,
        tags=tags or [],
        evidence=[
            RowOneLink(
                title="Evidence",
                url="https://example.com/evidence",
                source_name=source_name,
            )
        ],
        entity_refs=entity_refs or [],
        product_refs=product_refs or [],
        designer_refs=designer_refs or [],
        heat_delta=heat_delta,
    )


def _edition(stories: list[RowOneStory]) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="今日本地时尚情报", en="Today local fashion intelligence"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的内容", en="Read first"),
            )
        ],
        stories=stories,
    )


def _article(story_id: str, *, source_name: str, paragraphs: list[str]) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        url="https://example.com/article",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs,
        paragraphs_zh=[f"中文 {index + 1}" for index, _paragraph in enumerate(paragraphs)],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                        body=LocalizedText(zh="中文重点 1", en=paragraphs[0]),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )


def test_build_row_one_local_article_intelligence_uses_only_current_saved_articles() -> None:
    the_row = RowOneReference(name="The Row", type="brand", label="tracked")
    margaux = RowOneReference(name="Margaux", type="bag", label="product")
    stories = [
        _story(
            "the-row-1234567890",
            "The Row demand moves",
            detail_path="details/the-row-1234567890.html",
            heat_delta=9,
            entity_refs=[the_row],
            product_refs=[margaux],
            tags=["brand", "bag"],
        )
    ]

    sections = build_row_one_local_article_intelligence(
        _edition(stories),
        {
            "the-row-1234567890": _article(
                "the-row-1234567890",
                source_name="Vogue Business",
                paragraphs=["The Row and Margaux are the saved local source signal."],
            ),
            "stale-story": _article(
                "stale-story",
                source_name="Old Source",
                paragraphs=["This stale article must not appear."],
            ),
        },
    )

    assert [section.key for section in sections] == [
        "strongest_reads",
        "brand_watch",
        "product_watch",
        "heat_movers",
    ]
    assert sections[0].items[0].title.en == "The Row demand moves"
    assert sections[0].items[0].detail_path == "details/the-row-1234567890.html#local-article"
    assert sections[0].items[0].source_name == "Vogue Business"
    assert sections[0].items[0].source_names == ["Vogue Business"]
    assert sections[1].items[0].title.en == "The Row"
    assert sections[2].items[0].title.en == "Margaux"
    assert sections[3].items[0].heat_delta == 9
    assert "stale" not in sections[0].items[0].body.en


def test_build_row_one_local_article_intelligence_aggregates_references_by_name() -> None:
    the_row_brand = RowOneReference(name="The Row", type="brand", label="tracked")
    the_row_label = RowOneReference(name="the row", type="brand", label="candidate")
    margaux = RowOneReference(name="Margaux", type="bag", label="product")
    sandal = RowOneReference(name="Bare Sandal", type="shoe", label="product")
    stories = [
        _story(
            "story-a-1234567890",
            "The Row opens the day",
            detail_path="details/story-a-1234567890.html",
            heat_delta=4,
            entity_refs=[the_row_brand],
            product_refs=[margaux],
        ),
        _story(
            "story-b-1234567890",
            "The Row product context",
            detail_path="details/story-b-1234567890.html",
            heat_delta=8,
            entity_refs=[the_row_label],
            product_refs=[sandal],
        ),
    ]

    sections = build_row_one_local_article_intelligence(
        _edition(stories),
        {
            "story-a-1234567890": _article(
                "story-a-1234567890",
                source_name="Vogue Business",
                paragraphs=["The Row appears with Margaux in a saved article."],
            ),
            "story-b-1234567890": _article(
                "story-b-1234567890",
                source_name="WWD",
                paragraphs=["The Row appears again with Bare Sandal context."],
            ),
        },
    )

    brand_watch = next(section for section in sections if section.key == "brand_watch")
    assert brand_watch.items[0].title.en == "The Row"
    assert brand_watch.items[0].story_count == 2
    assert brand_watch.items[0].article_count == 2
    assert brand_watch.items[0].heat_delta == 8
    assert brand_watch.items[0].source_names == ["Vogue Business", "WWD"]
    assert brand_watch.items[0].references[0].name == "The Row"
    assert brand_watch.items[0].body.en == (
        "The Row appears with Margaux in a saved article. Sources: Vogue Business, WWD."
    )

    product_watch = next(section for section in sections if section.key == "product_watch")
    assert [item.title.en for item in product_watch.items] == ["Bare Sandal", "Margaux"]


def test_build_row_one_local_article_intelligence_falls_back_to_paragraphs_and_omits_empty() -> (
    None
):
    story = _story(
        "story-a-1234567890",
        "Saved article without structured sections",
        detail_path="details/story-a-1234567890.html",
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {
            "story-a-1234567890": RowOneLocalArticle(
                story_id="story-a-1234567890",
                url="https://example.com/article",
                source_name="Source",
                extracted_at=AS_OF,
                paragraphs=["Fallback paragraph is still publishable locally."],
            )
        },
    )

    assert [section.key for section in sections] == ["strongest_reads"]
    assert sections[0].items[0].body.en == "Fallback paragraph is still publishable locally."

    assert build_row_one_local_article_intelligence(_edition([story]), {}) == []
