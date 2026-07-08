from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_local_section_binder import (
    SAVED_ARTICLE_LOCAL_SECTION_BINDER_EXCERPT_CHARS,
    SAVED_ARTICLE_LOCAL_SECTION_BINDER_ITEM_LIMIT,
    SAVED_ARTICLE_LOCAL_SECTION_BINDER_PARAGRAPH_LIMIT,
    SAVED_ARTICLE_LOCAL_SECTION_BINDER_REFERENCE_LIMIT,
    SAVED_ARTICLE_LOCAL_SECTION_BINDER_SECTION_LIMIT,
    SAVED_ARTICLE_LOCAL_SECTION_BINDER_UNFILED_PARAGRAPH_LIMIT,
    build_row_one_saved_article_local_section_binder,
)

AS_OF = datetime(2026, 7, 8, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=f"Headline {story_id}",
        summary=_lt("Summary"),
        why_it_matters=_lt("Why it matters"),
        editorial_takeaway=_lt("Takeaway"),
        signal_context=_lt("Signal context"),
        reader_path=_lt("Reader path"),
        source_name="Vogue Business",
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=["brand"],
        evidence=[],
    )


def _reference(
    name: str = "The Row",
    *,
    ref_type: str = "brand",
    label: str = "tracked",
) -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _item(
    label: str,
    *,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=_lt(f"{label} body", f"{label} 正文"),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "entities",
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        body=_lt(f"{title} body", f"{title} 正文"),
        items=items or [],
    )


def _article(
    story_id: str = "the-row-signal-1234567890",
    *,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"Local article {story_id}",
        url="https://example.com/source",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=paragraphs
        or [
            "The Row reset its quiet luxury signal.",
            "The Margaux bag continued to anchor product demand.",
            "Alaia shoes gained fresh editor attention.",
            "This saved paragraph has not been filed into a section.",
        ],
        paragraphs_zh=paragraphs_zh
        or [
            "The Row 重塑了静奢信号。",
            "Margaux 包继续支撑产品需求。",
            "Alaia 鞋履获得编辑关注。",
            "这一段尚未被归入任何整理栏目。",
        ],
        content_sections=content_sections or [],
    )


def test_build_local_section_binder_preserves_section_order_and_original_anchors() -> None:
    binder = build_row_one_saved_article_local_section_binder(
        story=_story(),
        local_article=_article(
            content_sections=[
                _section(
                    "People & Brands",
                    key="entities",
                    items=[
                        _item(
                            "The Row",
                            references=[_reference("The Row"), _reference("Margaux", label="bag")],
                            paragraph_indices=[0, 1],
                        )
                    ],
                ),
                _section("Blank Product Signals", key="product_signals", items=[]),
                _section(
                    "Brand Signals",
                    key="brand_signals",
                    items=[
                        _item(
                            "Alaia shoes",
                            references=[_reference("Alaia", label="shoe")],
                            paragraph_indices=[2],
                        )
                    ],
                ),
            ]
        ),
    )

    assert binder is not None
    assert binder.title.en == "Local article the-row-signal-1234567890"
    assert binder.source_name == "Vogue Business"
    assert [row.title.en for row in binder.rows] == ["People & Brands", "Brand Signals"]
    assert [row.section_href for row in binder.rows] == [
        "#local-article-content-section-1",
        "#local-article-content-section-3",
    ]
    assert binder.rows[0].item_labels[0].en == "The Row"
    assert [reference.name for reference in binder.rows[0].references] == ["The Row", "Margaux"]
    assert [paragraph.href for paragraph in binder.rows[0].paragraphs] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-2",
    ]
    assert binder.rows[0].paragraphs[0].excerpt.en == "The Row reset its quiet luxury signal."
    assert binder.rows[0].paragraphs[0].excerpt.zh == "The Row 重塑了静奢信号。"
    assert [paragraph.href for paragraph in binder.rows[1].paragraphs] == [
        "#local-article-paragraph-3"
    ]
    assert [paragraph.href for paragraph in binder.unfiled_paragraphs] == [
        "#local-article-paragraph-4"
    ]


def test_build_local_section_binder_filters_invalid_paragraph_indices_and_dedupes() -> None:
    binder = build_row_one_saved_article_local_section_binder(
        story=_story(),
        local_article=_article(
            paragraphs=[
                "Usable first paragraph.",
                "   ",
                "Usable third paragraph.",
            ],
            paragraphs_zh=["可用第一段。"],
            content_sections=[
                _section(
                    "People & Brands",
                    items=[
                        _item(
                            "The Row",
                            references=[_reference("The Row"), _reference("The Row")],
                            paragraph_indices=[True, 0, 0, 1, -1, 99, 2],
                        )
                    ],
                )
            ],
        ),
    )

    assert binder is not None
    assert [reference.name for reference in binder.rows[0].references] == ["The Row"]
    assert [paragraph.href for paragraph in binder.rows[0].paragraphs] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-3",
    ]
    assert binder.rows[0].paragraphs[0].excerpt.zh == "Usable first paragraph."
    assert binder.rows[0].paragraphs[1].excerpt.zh == "Usable third paragraph."
    assert binder.unfiled_paragraphs == ()


def test_build_local_section_binder_caps_rows_chips_references_and_paragraphs() -> None:
    references = [_reference(f"Reference {index}", label=f"label {index}") for index in range(12)]
    items = [
        _item(
            f"Item {index}",
            references=[references[index]],
            paragraph_indices=[index],
        )
        for index in range(12)
    ]
    binder = build_row_one_saved_article_local_section_binder(
        story=_story(),
        local_article=_article(
            paragraphs=[f"Paragraph {index}" for index in range(12)],
            content_sections=[_section("People & Brands", items=items)],
        ),
    )

    assert binder is not None
    assert len(binder.rows[0].item_labels) == SAVED_ARTICLE_LOCAL_SECTION_BINDER_ITEM_LIMIT
    assert len(binder.rows[0].references) == SAVED_ARTICLE_LOCAL_SECTION_BINDER_REFERENCE_LIMIT
    assert len(binder.rows[0].paragraphs) == SAVED_ARTICLE_LOCAL_SECTION_BINDER_PARAGRAPH_LIMIT


def test_build_local_section_binder_caps_section_rows_but_scans_all_cited_paragraphs() -> None:
    section_count = SAVED_ARTICLE_LOCAL_SECTION_BINDER_SECTION_LIMIT + 2
    paragraphs = [f"Paragraph {index}" for index in range(section_count + 3)]
    sections = [
        _section(
            f"Section {index}",
            items=[_item(f"Item {index}", paragraph_indices=[index])],
        )
        for index in range(section_count)
    ]

    binder = build_row_one_saved_article_local_section_binder(
        story=_story(),
        local_article=_article(
            paragraphs=paragraphs,
            content_sections=sections,
        ),
    )

    assert binder is not None
    assert len(binder.rows) == SAVED_ARTICLE_LOCAL_SECTION_BINDER_SECTION_LIMIT
    assert [row.section_position for row in binder.rows] == list(
        range(1, SAVED_ARTICLE_LOCAL_SECTION_BINDER_SECTION_LIMIT + 1)
    )
    assert "#local-article-paragraph-9" not in [
        paragraph.href for paragraph in binder.unfiled_paragraphs
    ]
    assert "#local-article-paragraph-10" not in [
        paragraph.href for paragraph in binder.unfiled_paragraphs
    ]
    assert [paragraph.href for paragraph in binder.unfiled_paragraphs] == [
        "#local-article-paragraph-11",
        "#local-article-paragraph-12",
        "#local-article-paragraph-13",
    ]


def test_build_local_section_binder_caps_unfiled_paragraphs_and_truncates_excerpts() -> None:
    long_paragraph = "Luxury signal " * 40
    unfiled_count = SAVED_ARTICLE_LOCAL_SECTION_BINDER_UNFILED_PARAGRAPH_LIMIT + 3
    binder = build_row_one_saved_article_local_section_binder(
        story=_story(),
        local_article=_article(
            paragraphs=[
                long_paragraph,
                *[f"Unfiled paragraph {index}" for index in range(unfiled_count)],
            ],
            content_sections=[
                _section(
                    "People & Brands",
                    items=[_item("The Row", paragraph_indices=[0])],
                )
            ],
        ),
    )

    assert binder is not None
    assert len(binder.unfiled_paragraphs) == (
        SAVED_ARTICLE_LOCAL_SECTION_BINDER_UNFILED_PARAGRAPH_LIMIT
    )
    excerpt = binder.rows[0].paragraphs[0].excerpt.en
    assert len(excerpt) <= SAVED_ARTICLE_LOCAL_SECTION_BINDER_EXCERPT_CHARS + 1
    assert excerpt.endswith("…")


def test_build_local_section_binder_returns_none_for_unsafe_or_empty_inputs() -> None:
    assert (
        build_row_one_saved_article_local_section_binder(
            story=_story("unsafe/story"),
            local_article=_article("unsafe/story", content_sections=[]),
        )
        is None
    )
    assert (
        build_row_one_saved_article_local_section_binder(
            story=_story("the-row-signal-1234567890"),
            local_article=_article("other-signal-1234567890", content_sections=[]),
        )
        is None
    )
    assert (
        build_row_one_saved_article_local_section_binder(
            story=_story(),
            local_article=_article(paragraphs=[" ", ""], content_sections=[]),
        )
        is None
    )
