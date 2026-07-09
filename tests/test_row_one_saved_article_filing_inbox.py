from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_filing_inbox import (
    _strict_valid_paragraph_indices,
    build_row_one_saved_article_filing_inbox,
)

AS_OF = datetime(2026, 7, 9, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(
    story_id: str = "the-row-signal-1234567890",
    headline: str = "The Row signal",
    *,
    section_key: str = "top_stories",
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        story_type="tracked_entity",
        headline=headline,
        summary=_lt(f"{headline} summary", f"{headline} 摘要"),
        why_it_matters=_lt("Why it matters", "重要性"),
        editorial_takeaway=_lt("Editorial read", "编辑判断"),
        signal_context=_lt("Signal context", "信号背景"),
        reader_path=_lt("Reader path", "阅读路径"),
        source_name="Vogue Business",
        source_url="https://example.com/source",
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
        summary=_lt("Daily summary", "今日摘要"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=_lt("Top Stories", "今日重点"),
                dek=_lt("Top reads", "重点阅读"),
            ),
            RowOneSection(
                key="hot_products",
                title=_lt("Hot Products", "热门单品"),
                dek=_lt("Product signals", "单品信号"),
            ),
        ],
        stories=list(stories),
    )


def _item(
    label: str = "Signal",
    *,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=_lt(f"{label} body", f"{label} 正文"),
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str = "People & Brands",
    *,
    key: str = "entities",
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        items=items or [],
    )


def _article(
    story_id: str = "the-row-signal-1234567890",
    *,
    title: str | None = "The Row saved article",
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
    body_source: str = "extracted",
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url="https://example.com/source",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs
        or [
            "The Row reset its quiet luxury signal.",
            "The Margaux bag continued to anchor product demand.",
            "Alaia shoes gained fresh editor attention.",
        ],
        paragraphs_zh=paragraphs_zh
        or [
            "The Row 重塑了静奢信号。",
            "Margaux 包继续支撑产品需求。",
            "Alaia 鞋履获得编辑关注。",
        ],
        content_sections=content_sections or [],
        body_source=body_source,  # type: ignore[arg-type]
    )


def test_build_saved_article_filing_inbox_collects_unfiled_paragraphs() -> None:
    story = _story()

    inbox = build_row_one_saved_article_filing_inbox(
        _edition(story),
        {
            story.id: _article(
                story.id,
                content_sections=[_section(items=[_item("The Row", paragraph_indices=[0])])],
            )
        },
        local_article_page_hrefs_by_detail_path={
            story.detail_path: "the-row-signal-1234567890.html"
        },
    )

    assert inbox is not None
    assert len(inbox.items) == 1
    item = inbox.items[0]
    assert item.title.en == "The Row saved article"
    assert item.source_name == "Vogue Business"
    assert item.body_source_label.en == "Extracted article text"
    assert item.saved_paragraph_count == 3
    assert item.organized_section_count == 1
    assert item.unfiled_paragraph_count == 2
    assert [paragraph.index for paragraph in item.paragraphs] == [1, 2]
    assert [paragraph.label.en for paragraph in item.paragraphs] == [
        "Paragraph 2",
        "Paragraph 3",
    ]
    assert [paragraph.href for paragraph in item.paragraphs] == [
        "the-row-signal-1234567890.html#local-article-paragraph-2",
        "the-row-signal-1234567890.html#local-article-paragraph-3",
    ]
    assert item.paragraphs[0].excerpt.zh == "Margaux 包继续支撑产品需求。"


def test_build_saved_article_filing_inbox_filters_invalid_indices_and_hrefs() -> None:
    assert _strict_valid_paragraph_indices(
        [True, "0", -1, 0, 0, 1, 99],
        {0, 2},
    ) == (0,)

    story = _story()
    inbox = build_row_one_saved_article_filing_inbox(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["First filed paragraph.", "   ", "Third unfiled paragraph."],
                content_sections=[
                    _section(items=[_item("Refs", paragraph_indices=[-1, 0, 0, 1, 99])])
                ],
            )
        },
        local_article_page_hrefs_by_detail_path={
            story.detail_path: "the-row-signal-1234567890.html"
        },
    )

    assert inbox is not None
    assert [paragraph.href for paragraph in inbox.items[0].paragraphs] == [
        "the-row-signal-1234567890.html#local-article-paragraph-3"
    ]

    for unsafe_href in (
        "javascript:alert(1)",
        "../secret.html",
        "nested/story.html",
        "https://example.com/story.html",
    ):
        assert (
            build_row_one_saved_article_filing_inbox(
                _edition(story),
                {story.id: _article(story.id)},
                local_article_page_hrefs_by_detail_path={story.detail_path: unsafe_href},
            )
            is None
        )


def test_build_saved_article_filing_inbox_caps_and_preserves_order() -> None:
    stories = [
        _story(
            f"story-{index}-1234567890",
            f"Story {index}",
            section_key="hot_products" if index % 2 else "top_stories",
        )
        for index in range(10)
    ]

    inbox = build_row_one_saved_article_filing_inbox(
        _edition(*stories),
        {
            story.id: _article(
                story.id,
                title=f"Local {index}",
                source_name=f"Source {index}",
                paragraphs=[f"Paragraph {index}-{paragraph}" for paragraph in range(6)],
                content_sections=[_section(items=[_item("Filed", paragraph_indices=[0])])],
            )
            for index, story in enumerate(stories)
        },
        local_article_page_hrefs_by_detail_path={
            story.detail_path: f"{story.id}.html" for story in stories
        },
    )

    assert inbox is not None
    assert [item.title.en for item in inbox.items] == [f"Local {index}" for index in range(8)]
    assert len(inbox.items[0].paragraphs) == 3
    assert [paragraph.label.en for paragraph in inbox.items[0].paragraphs] == [
        "Paragraph 2",
        "Paragraph 3",
        "Paragraph 4",
    ]


def test_build_saved_article_filing_inbox_returns_none_without_unfiled_paragraphs() -> None:
    story = _story()
    inbox = build_row_one_saved_article_filing_inbox(
        _edition(story),
        {
            story.id: _article(
                story.id,
                content_sections=[
                    _section(items=[_item("All filed", paragraph_indices=[0, 1, 2])])
                ],
            )
        },
        local_article_page_hrefs_by_detail_path={
            story.detail_path: "the-row-signal-1234567890.html"
        },
    )

    assert inbox is None
    assert (
        build_row_one_saved_article_filing_inbox(
            _edition(story),
            {},
            local_article_page_hrefs_by_detail_path={
                story.detail_path: "the-row-signal-1234567890.html"
            },
        )
        is None
    )
