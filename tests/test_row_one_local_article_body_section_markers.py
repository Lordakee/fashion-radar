from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.local_article_body_section_markers import (
    LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS,
    LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS,
    LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS,
    LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES,
    build_row_one_local_article_body_section_markers,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 9, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _ref(name: str, ref_type: str, label: str) -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline="The Row signal",
        summary=_lt("The Row summary", "The Row 摘要"),
        why_it_matters=_lt("Why it matters", "重要性"),
        editorial_takeaway=_lt("Takeaway", "编辑判断"),
        signal_context=_lt("Signal context", "信号背景"),
        reader_path=_lt("Reader path", "阅读路径"),
        source_name="Vogue Business",
        source_url="https://example.com/the-row",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
    )


def _item(
    label: str,
    *,
    body: str | LocalizedText | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[object] | None = None,
) -> RowOneLocalArticleContentItem:
    localized_body = _lt(body) if isinstance(body, str) else body
    return RowOneLocalArticleContentItem.model_construct(
        label=_lt(label, f"{label} zh"),
        body=localized_body,
        references=list(references or []),
        paragraph_indices=list(paragraph_indices or []),
    )


def _section(
    key: str = "entities",
    *,
    title: LocalizedText | None = None,
    body: LocalizedText | None = None,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=title if title is not None else _lt("Section title", "分节标题"),
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
        source_name="Vogue Business",
        url="https://example.com/the-row",
        title="The Row local article",
        extracted_at=AS_OF,
        body_source="extracted",
        paragraphs=paragraphs
        if paragraphs is not None
        else [
            "The Row frames the season through restraint and proportion.",
            "The Margaux bag remains the commercial signal.",
        ],
        paragraphs_zh=paragraphs_zh or [],
        brief_sections=[],
        content_sections=content_sections or [],
    )


def test_build_local_article_body_section_markers_marks_section_starts() -> None:
    markers = build_row_one_local_article_body_section_markers(
        story=_story(),
        local_article=_article(
            content_sections=[
                _section(
                    "brand_signals",
                    title=_lt("Brand signal", "品牌信号"),
                    body=_lt("The Row section context.", "The Row 分节上下文。"),
                    items=[
                        _item(
                            "The Row",
                            body="Mary-Kate and Ashley Olsen's label frames the story.",
                            references=[_ref("The Row", "brand", "brand")],
                            paragraph_indices=[0, 1],
                        )
                    ],
                )
            ],
        ),
    )

    assert len(markers) == 1
    assert markers[0].paragraph_index == 0
    assert markers[0].paragraph_href == "#local-article-paragraph-1"
    assert markers[0].section_position == 1
    assert markers[0].section_href == "#local-article-content-section-1"
    assert markers[0].title.en == "Brand signal"
    assert markers[0].support.en == "The Row section context."
    assert [label.en for label in markers[0].item_labels] == ["The Row"]
    assert [ref.name for ref in markers[0].references] == ["The Row"]


def test_build_local_article_body_section_markers_filters_invalid_indices() -> None:
    markers = build_row_one_local_article_body_section_markers(
        story=_story(),
        local_article=_article(
            paragraphs=["   ", "Valid second paragraph."],
            content_sections=[
                _section(
                    items=[
                        _item(
                            "The Row",
                            paragraph_indices=[True, "0", -1, 0, 1, 1, 99],
                        )
                    ],
                )
            ],
        ),
    )

    assert len(markers) == 1
    assert markers[0].paragraph_index == 1
    assert markers[0].paragraph_href == "#local-article-paragraph-2"


def test_build_local_article_body_section_markers_dedupes_duplicate_paragraph_markers() -> None:
    markers = build_row_one_local_article_body_section_markers(
        story=_story(),
        local_article=_article(
            content_sections=[
                _section(
                    title=_lt("First section", "第一节"),
                    items=[_item("First", paragraph_indices=[0])],
                ),
                _section(
                    title=_lt("Second section", "第二节"),
                    items=[_item("Second", paragraph_indices=[0, 1])],
                ),
            ],
        ),
    )

    assert len(markers) == 1
    assert markers[0].paragraph_index == 0
    assert markers[0].section_position == 1
    assert markers[0].title.en == "First section"


def test_build_local_article_body_section_markers_uses_support_fallbacks() -> None:
    section_body_marker, item_body_marker, paragraph_marker = (
        build_row_one_local_article_body_section_markers(
            story=_story(),
            local_article=_article(
                paragraphs=[
                    "Paragraph zero saved support.",
                    "Paragraph one saved support.",
                    "Paragraph two saved support.",
                ],
                paragraphs_zh=["段落零支撑。"],
                content_sections=[
                    _section(
                        title=_lt("", ""),
                        body=_lt("Section body support.", "分节正文支撑。"),
                        items=[_item("Section", body="Item body ignored.", paragraph_indices=[0])],
                    ),
                    _section(
                        title=_lt("Item fallback", "条目回退"),
                        body=None,
                        items=[
                            _item("Blank item", body=_lt("  ", " "), paragraph_indices=[]),
                            _item(
                                "Item",
                                body=_lt("First non-empty item body.", "第一个非空条目正文。"),
                                paragraph_indices=[1],
                            ),
                        ],
                    ),
                    _section(
                        title=_lt("Paragraph fallback", "段落回退"),
                        body=None,
                        items=[_item("Paragraph", body=None, paragraph_indices=[2])],
                    ),
                ],
            ),
        )
    )

    assert section_body_marker.title.en == "Section 1"
    assert section_body_marker.title.zh == "第 1 节"
    assert section_body_marker.support.en == "Section body support."
    assert section_body_marker.support.zh == "分节正文支撑。"
    assert item_body_marker.support.en == "First non-empty item body."
    assert item_body_marker.support.zh == "第一个非空条目正文。"
    assert paragraph_marker.support.en == "Paragraph two saved support."
    assert paragraph_marker.support.zh == "Paragraph two saved support."


def test_build_local_article_body_section_markers_caps_labels_references_and_markers() -> None:
    long_paragraph = " ".join(["Long saved paragraph support"] * 20)
    sections = [
        _section(
            title=_lt(f"Section {section_index}", f"第 {section_index} 节"),
            items=[
                _item(
                    "The Row",
                    references=[
                        _ref("The Row", "brand", "brand"),
                        _ref("the row", "BRAND", "Brand"),
                    ],
                    paragraph_indices=[section_index],
                ),
                _item(
                    "the row",
                    references=[_ref("Margaux", "product", "bag")],
                    paragraph_indices=[section_index],
                ),
                _item(
                    "Margaux",
                    references=[_ref("Alaia", "brand", "brand")],
                    paragraph_indices=[section_index],
                ),
                _item(
                    "Alaia",
                    references=[_ref("Olsen", "person", "designer")],
                    paragraph_indices=[section_index],
                ),
                _item(
                    "Fashion week",
                    references=[_ref("Runway", "event", "show")],
                    paragraph_indices=[section_index],
                ),
            ],
        )
        for section_index in range(LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS + 3)
    ]

    markers = build_row_one_local_article_body_section_markers(
        story=_story(),
        local_article=_article(
            paragraphs=[long_paragraph for _ in sections],
            content_sections=sections,
        ),
    )

    assert len(markers) == LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS
    assert [marker.paragraph_index for marker in markers] == list(
        range(LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS)
    )
    assert all(
        len(marker.item_labels) == LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS
        for marker in markers
    )
    assert all(
        len(marker.references) == LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES
        for marker in markers
    )
    assert [label.en for label in markers[0].item_labels] == [
        "The Row",
        "Margaux",
        "Alaia",
    ]
    assert [reference.name for reference in markers[0].references] == [
        "The Row",
        "Margaux",
        "Alaia",
        "Olsen",
    ]
    assert all(
        len(marker.support.en) <= LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS
        for marker in markers
    )
    assert markers[0].support.en.endswith("...")


def test_build_local_article_body_section_markers_returns_empty_without_markable_sections() -> None:
    assert (
        build_row_one_local_article_body_section_markers(
            story=_story(),
            local_article=_article(story_id="mismatched-story-1234567890"),
        )
        == ()
    )
    assert (
        build_row_one_local_article_body_section_markers(
            story=_story("unsafe/../story"),
            local_article=_article(story_id="unsafe/../story"),
        )
        == ()
    )
    assert (
        build_row_one_local_article_body_section_markers(
            story=_story(),
            local_article=_article(
                paragraphs=[" ", "\t"],
                content_sections=[_section(items=[_item("Blank", paragraph_indices=[0, 1])])],
            ),
        )
        == ()
    )
    assert (
        build_row_one_local_article_body_section_markers(
            story=_story(),
            local_article=_article(
                content_sections=[
                    _section(items=[_item("No indices", paragraph_indices=[])]),
                    _section(items=[_item("Invalid", paragraph_indices=[99])]),
                ],
            ),
        )
        == ()
    )
