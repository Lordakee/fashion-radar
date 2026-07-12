from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_saved_text_takeaways import (
    DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS,
    build_row_one_daily_local_saved_text_takeaways,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 12, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(story_id: str, headline: str = "The Row signal") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline,
        summary=_lt("Saved text summary."),
        why_it_matters=_lt("Saved local text adds context."),
        editorial_takeaway=_lt("The saved article adds a concrete daily signal."),
        signal_context=_lt("The signal context stays grounded in saved text."),
        reader_path=_lt("Read through the saved local article body."),
        source_name="Vogue Business",
        source_url="https://example.com/story",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _edition(stories: list[RowOneStory]) -> RowOneEdition:
    return RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=_lt("Daily ROW ONE summary."),
        stories=stories,
    )


def _article(
    story_id: str,
    *,
    title: str = "Saved source article",
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url="https://example.com/local",
        source_name=source_name,
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=paragraphs
        if paragraphs is not None
        else [
            "The saved article explains why the item is gaining attention in stores.",
            "A second saved paragraph shows what the reader should inspect next.",
        ],
        paragraphs_zh=paragraphs_zh
        if paragraphs_zh is not None
        else [
            "保存正文解释该单品为何在门店获得关注。",
            "第二段保存正文提示读者接下来要观察什么。",
        ],
        content_sections=content_sections
        if content_sections is not None
        else [
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(en="Products", zh="单品"),
                body=LocalizedText(
                    en="Product context from saved text.",
                    zh="保存正文中的单品语境。",
                ),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Margaux bag", zh="Margaux 手袋"),
                        body=LocalizedText(
                            en="Margaux bag evidence appears in saved local text.",
                            zh="Margaux 手袋证据出现在保存本地正文中。",
                        ),
                        references=[
                            RowOneReference(
                                name="Margaux bag",
                                type="bag",
                                label="product",
                            )
                        ],
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )


def test_build_daily_local_saved_text_takeaways_groups_existing_saved_text() -> None:
    first_id = "the-row-signal-1111111111"
    second_id = "alaia-flats-2222222222"
    takeaways = build_row_one_daily_local_saved_text_takeaways(
        _edition([_story(first_id), _story(second_id, headline="Alaia flats signal")]),
        {first_id: _article(first_id), second_id: _article(second_id, source_name="WWD")},
        {first_id: f"{first_id}.html", second_id: f"{second_id}.html"},
    )

    assert takeaways is not None
    assert takeaways.article_count == 2
    assert takeaways.source_count == 2
    assert [lane.key for lane in takeaways.lanes] == [
        "what_article_says",
        "brand_product_context",
        "inspect_next",
    ]
    assert takeaways.lanes[0].cards[0].href == (
        "articles/the-row-signal-1111111111.html#local-article-paragraph-1"
    )
    assert takeaways.lanes[1].cards[0].href == (
        "articles/the-row-signal-1111111111.html#local-article-content-section-1"
    )
    assert "gaining attention" in takeaways.lanes[0].cards[0].excerpt.en
    assert takeaways.lanes[1].cards[0].label.en == "Margaux bag"


def test_build_daily_local_saved_text_takeaways_requires_two_articles() -> None:
    story_id = "single-signal-1111111111"
    assert (
        build_row_one_daily_local_saved_text_takeaways(
            _edition([_story(story_id)]),
            {story_id: _article(story_id)},
            {story_id: f"{story_id}.html"},
        )
        is None
    )


def test_build_daily_local_saved_text_takeaways_caps_excerpts_and_filters_hrefs() -> None:
    first_id = "the-row-signal-1111111111"
    second_id = "alaia-flats-2222222222"
    long_text = "Lead sentence. " + ("detail " * 80) + "TAIL_MARKER"
    unsafe_takeaways = build_row_one_daily_local_saved_text_takeaways(
        _edition([_story(first_id), _story(second_id)]),
        {
            first_id: _article(first_id, paragraphs=[long_text], paragraphs_zh=[long_text]),
            second_id: _article(second_id),
        },
        {
            first_id: f"{first_id}.html",
            second_id: "https://example.com/unsafe.html",
        },
    )

    assert unsafe_takeaways is None

    safe_takeaways = build_row_one_daily_local_saved_text_takeaways(
        _edition([_story(first_id), _story(second_id)]),
        {
            first_id: _article(first_id, paragraphs=[long_text], paragraphs_zh=[long_text]),
            second_id: _article(second_id),
        },
        {first_id: f"{first_id}.html", second_id: f"{second_id}.html"},
    )

    assert safe_takeaways is not None
    excerpt = safe_takeaways.lanes[0].cards[0].excerpt.en
    assert len(excerpt) <= DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS
    assert excerpt.endswith("...")
    assert "TAIL_MARKER" not in excerpt


def test_build_daily_local_saved_text_takeaways_inspect_next_avoids_reused_evidence() -> None:
    first_id = "the-row-signal-1111111111"
    second_id = "alaia-flats-2222222222"
    takeaways = build_row_one_daily_local_saved_text_takeaways(
        _edition([_story(first_id), _story(second_id)]),
        {first_id: _article(first_id), second_id: _article(second_id)},
        {first_id: f"{first_id}.html", second_id: f"{second_id}.html"},
    )

    assert takeaways is not None
    first_article_hrefs = [
        lane.cards[0].href
        for lane in takeaways.lanes
        if lane.cards and "the-row-signal-1111111111" in lane.cards[0].href
    ]
    assert first_article_hrefs == [
        "articles/the-row-signal-1111111111.html#local-article-paragraph-1",
        "articles/the-row-signal-1111111111.html#local-article-content-section-1",
        "articles/the-row-signal-1111111111.html#local-article-paragraph-2",
    ]
    assert len(first_article_hrefs) == len(set(first_article_hrefs))
