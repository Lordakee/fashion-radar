from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_body_organizer import (
    LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ITEM_LABELS,
    LOCAL_ARTICLE_BODY_ORGANIZER_MAX_PARAGRAPHS_PER_ROW,
    LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ROUTE_LINKS,
    LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS,
    LOCAL_ARTICLE_BODY_ORGANIZER_MAX_UNFILED_PARAGRAPHS,
    build_row_one_saved_article_body_organizer,
)

AS_OF = datetime(2026, 7, 9, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=f"Headline {story_id}",
        summary=_lt("Summary", "摘要"),
        why_it_matters=_lt("Why it matters", "重要性"),
        editorial_takeaway=_lt("Takeaway", "编辑判断"),
        signal_context=_lt("Signal context", "信号背景"),
        reader_path=_lt("Reader path", "阅读路径"),
        source_name="Vogue Business",
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _item(
    label: str,
    *,
    body: LocalizedText | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=body if body is not None else _lt(f"{label} support", f"{label} 支撑"),
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "entities",
    body: LocalizedText | None = None,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        body=body,
        items=items or [],
    )


def _untitled_section(
    *,
    key: str = "entities",
    body: LocalizedText | None = None,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt("", ""),
        body=body,
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


def test_build_saved_article_body_organizer_groups_filed_and_unfiled_paragraphs() -> None:
    organizer = build_row_one_saved_article_body_organizer(
        story=_story(),
        local_article=_article(
            content_sections=[
                _section(
                    "People & Brands",
                    key="entities",
                    items=[_item("The Row", paragraph_indices=[0, 2])],
                ),
                _section(
                    "Products",
                    key="product_signals",
                    items=[_item("Margaux", paragraph_indices=[1])],
                ),
            ]
        ),
    )

    assert organizer is not None
    assert organizer.title.en == "Local article the-row-signal-1234567890"
    assert organizer.source_name == "Vogue Business"
    assert organizer.saved_paragraph_count == 4
    assert organizer.filed_paragraph_count == 3
    assert organizer.unfiled_paragraph_count == 1
    assert organizer.organized_section_count == 2
    assert [row.title.en for row in organizer.section_rows] == ["People & Brands", "Products"]
    assert [row.section_href for row in organizer.section_rows] == [
        "#local-article-content-section-1",
        "#local-article-content-section-2",
    ]
    assert [paragraph.href for paragraph in organizer.section_rows[0].paragraphs] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-3",
    ]
    assert [paragraph.href for paragraph in organizer.section_rows[1].paragraphs] == [
        "#local-article-paragraph-2"
    ]
    assert [paragraph.href for paragraph in organizer.unfiled_paragraphs] == [
        "#local-article-paragraph-4"
    ]
    assert [paragraph.href for paragraph in organizer.read_first_route] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-2",
        "#local-article-paragraph-3",
        "#local-article-paragraph-4",
    ]
    assert organizer.section_rows[0].paragraphs[0].excerpt.zh == "The Row 重塑了静奢信号。"


def test_build_saved_article_body_organizer_filters_invalid_indices_and_blank_paragraphs() -> None:
    organizer = build_row_one_saved_article_body_organizer(
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
                            paragraph_indices=[True, "0", -1, 0, 0, 1, 99],  # type: ignore[list-item]
                        )
                    ],
                )
            ],
        ),
    )

    assert organizer is not None
    assert organizer.saved_paragraph_count == 2
    assert organizer.filed_paragraph_count == 1
    assert organizer.unfiled_paragraph_count == 1
    assert [paragraph.href for paragraph in organizer.section_rows[0].paragraphs] == [
        "#local-article-paragraph-1"
    ]
    assert [paragraph.href for paragraph in organizer.unfiled_paragraphs] == [
        "#local-article-paragraph-3"
    ]
    emitted_hrefs = [
        paragraph.href for row in organizer.section_rows for paragraph in row.paragraphs
    ] + [paragraph.href for paragraph in organizer.unfiled_paragraphs]
    assert "#local-article-paragraph-0" not in emitted_hrefs
    assert "#local-article-paragraph-2" not in emitted_hrefs
    assert "#local-article-paragraph-100" not in emitted_hrefs
    assert organizer.section_rows[0].paragraphs[0].excerpt.zh == "Usable first paragraph."


def test_build_saved_article_body_organizer_handles_misaligned_zh() -> None:
    organizer = build_row_one_saved_article_body_organizer(
        story=_story(),
        local_article=_article(
            paragraphs=["First paragraph.", "Second paragraph."],
            paragraphs_zh=["第一段。"],
            content_sections=[
                _section("Takeaways", items=[_item("Signal", paragraph_indices=[0])])
            ],
        ),
    )

    assert organizer is not None
    assert organizer.section_rows[0].paragraphs[0].excerpt.zh == "First paragraph."
    assert organizer.unfiled_paragraphs[0].excerpt.zh == "Second paragraph."


def test_build_saved_article_body_organizer_caps_rows_deterministically() -> None:
    paragraphs = [f"Paragraph {index}" for index in range(20)]
    sections = [
        _section(
            f"Section {section_index}",
            key="entities" if section_index % 2 else "product_signals",
            items=[
                _item(
                    f"Item {section_index}-{item_index}",
                    paragraph_indices=list(range(section_index, section_index + 6)),
                )
                for item_index in range(5)
            ],
        )
        for section_index in range(7)
    ]

    organizer = build_row_one_saved_article_body_organizer(
        story=_story(),
        local_article=_article(paragraphs=paragraphs, paragraphs_zh=[], content_sections=sections),
    )

    assert organizer is not None
    assert len(organizer.section_rows) == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS
    assert all(
        len(row.item_labels) == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ITEM_LABELS
        for row in organizer.section_rows
    )
    assert all(
        len(row.paragraphs) == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_PARAGRAPHS_PER_ROW
        for row in organizer.section_rows
    )
    assert len(organizer.unfiled_paragraphs) == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_UNFILED_PARAGRAPHS
    assert len(organizer.read_first_route) == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ROUTE_LINKS
    assert [row.title.en for row in organizer.section_rows] == [
        f"Section {index}" for index in range(LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS)
    ]
    assert [paragraph.href for paragraph in organizer.read_first_route] == [
        f"#local-article-paragraph-{index}" for index in range(1, 6)
    ]


def test_build_saved_article_body_organizer_keeps_capped_section_paragraphs_unfiled() -> None:
    paragraphs = [f"Paragraph {index}" for index in range(7)]
    sections = [
        _section(
            f"Visible section {index}",
            key="entities" if index % 2 else "product_signals",
            items=[_item(f"Visible item {index}", paragraph_indices=[index])],
        )
        for index in range(LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS)
    ]
    sections.append(
        _section(
            "Capped section",
            items=[
                _item(
                    "Capped item",
                    paragraph_indices=[LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS],
                )
            ],
        )
    )

    organizer = build_row_one_saved_article_body_organizer(
        story=_story(),
        local_article=_article(paragraphs=paragraphs, paragraphs_zh=[], content_sections=sections),
    )

    assert organizer is not None
    assert len(organizer.section_rows) == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS
    assert organizer.filed_paragraph_count == LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS
    assert [paragraph.href for paragraph in organizer.unfiled_paragraphs] == [
        f"#local-article-paragraph-{LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS + 1}",
        f"#local-article-paragraph-{LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS + 2}",
    ]


def test_build_saved_article_body_organizer_counts_saved_body_anchors() -> None:
    organizer = build_row_one_saved_article_body_organizer(
        story=_story(),
        local_article=_article(
            paragraphs=[
                "Original source summary: ",
                "<p>Visible paragraph with HTML.</p>",
            ],
            paragraphs_zh=[],
        ),
    )

    assert organizer is not None
    assert organizer.saved_paragraph_count == 2
    assert [paragraph.href for paragraph in organizer.read_first_route] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-2",
    ]
    assert organizer.unfiled_paragraphs[0].excerpt.en == "Original source summary:"
    assert organizer.unfiled_paragraphs[1].excerpt.en == "Visible paragraph with HTML."


def test_build_saved_article_body_organizer_uses_bilingual_fallback_section_title() -> None:
    organizer = build_row_one_saved_article_body_organizer(
        story=_story(),
        local_article=_article(
            content_sections=[
                _untitled_section(
                    items=[_item("Signal", paragraph_indices=[0])],
                )
            ],
        ),
    )

    assert organizer is not None
    assert organizer.section_rows[0].title.en == "Section 1"
    assert organizer.section_rows[0].title.zh == "第 1 节"


def test_build_saved_article_body_organizer_returns_none_without_meaningful_body() -> None:
    story = _story()

    assert (
        build_row_one_saved_article_body_organizer(
            story=story,
            local_article=_article("other-story-1234567890"),
        )
        is None
    )
    assert (
        build_row_one_saved_article_body_organizer(
            story=_story("unsafe"),
            local_article=_article("unsafe"),
        )
        is None
    )
    assert (
        build_row_one_saved_article_body_organizer(
            story=story,
            local_article=_article(paragraphs=["   ", "\n"], paragraphs_zh=[]),
        )
        is None
    )
