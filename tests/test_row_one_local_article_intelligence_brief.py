from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.local_article_intelligence_brief import (
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE,
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_EVIDENCE_LINKS,
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES,
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTE_LINKS,
    build_row_one_local_article_intelligence_brief,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 9, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=f"Headline {story_id}",
        summary=_lt("Summary", "摘要"),
        why_it_matters=_lt("Story why it matters", "故事重要性"),
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


def _reference(
    name: str,
    *,
    ref_type: str = "brand",
    label: str = "brand",
) -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _brief(
    key: str = "why_it_matters",
    *,
    body: LocalizedText | None = None,
) -> RowOneLocalArticleBriefSection:
    return RowOneLocalArticleBriefSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(key.replace("_", " ").title()),
        body=body or _lt("Local article explains the market signal.", "本地文章解释市场信号。"),
    )


def _item(
    label: str,
    *,
    body: LocalizedText | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=body if body is not None else _lt(f"{label} support", f"{label} 支撑"),
        references=references or [],
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


def _article(
    story_id: str = "the-row-signal-1234567890",
    *,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    brief_sections: list[RowOneLocalArticleBriefSection] | None = None,
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
            "The Row reset its restraint signal for the season.",
            "The Margaux bag kept showing up as the commercial anchor.",
            "Alaia shoes gained fresh editor attention.",
            "Mary-Kate Olsen framed the silhouette shift.",
        ],
        paragraphs_zh=paragraphs_zh
        or [
            "The Row 重塑了克制信号。",
            "Margaux 包继续成为商业锚点。",
            "Alaia 鞋履获得编辑关注。",
            "Mary-Kate Olsen 定义了廓形变化。",
        ],
        brief_sections=brief_sections or [],
        content_sections=content_sections or [],
    )


def test_build_local_article_intelligence_brief_summarizes_article_structure() -> None:
    brief = build_row_one_local_article_intelligence_brief(
        story=_story(),
        local_article=_article(
            brief_sections=[
                _brief(
                    body=_lt(
                        "Local signal explains why this matters.",
                        "本地信号解释重要性。",
                    )
                )
            ],
            content_sections=[
                _section(
                    "Brand Signals",
                    key="brand_signals",
                    items=[
                        _item(
                            "The Row",
                            body=_lt("The Row remains the brand anchor.", "The Row 仍是品牌锚点。"),
                            references=[
                                _reference("The Row", ref_type="brand", label="brand"),
                                _reference("the row", ref_type="brand", label="tracked"),
                                _reference("Margaux", ref_type="accessory", label="product"),
                                _reference("Mary-Kate Olsen", ref_type="person", label="designer"),
                            ],
                            paragraph_indices=[0, 1],
                        )
                    ],
                ),
                _section(
                    "Quiet luxury reset",
                    key="takeaways",
                    items=[
                        _item(
                            "Alaia flats",
                            references=[
                                _reference("Alaia flats", ref_type="shoe", label="product")
                            ],
                            paragraph_indices=[2],
                        )
                    ],
                ),
            ],
        ),
    )

    assert brief is not None
    assert brief.title.en == "Local Article Intelligence Brief"
    assert brief.title.zh == "本地文章情报摘要"
    assert brief.source_name == "Vogue Business"
    assert brief.opening_signal.en == "Local signal explains why this matters."
    assert brief.opening_signal.zh == "本地信号解释重要性。"
    assert [lane.key for lane in brief.lanes] == ["brands", "products", "people", "themes"]
    by_key = {lane.key: lane for lane in brief.lanes}
    assert [chip.label.en for chip in by_key["brands"].chips] == ["The Row"]
    assert [chip.label.en for chip in by_key["products"].chips] == ["Margaux", "Alaia flats"]
    assert [chip.label.en for chip in by_key["people"].chips] == ["Mary-Kate Olsen"]
    assert [chip.label.en for chip in by_key["themes"].chips] == [
        "Brand Signals",
        "Quiet luxury reset",
    ]
    assert [evidence.href for evidence in brief.evidence] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-2",
        "#local-article-paragraph-3",
    ]
    assert brief.evidence[0].excerpt.zh == "The Row 重塑了克制信号。"
    assert [route.href for route in brief.routes] == [
        "#local-article-content-section-1",
        "#local-article-content-section-2",
    ]


def test_build_local_article_intelligence_brief_filters_invalid_indices_and_blanks() -> None:
    brief = build_row_one_local_article_intelligence_brief(
        story=_story(),
        local_article=_article(
            paragraphs=[
                "Usable first paragraph.",
                "   ",
                "Usable third paragraph.",
            ],
            paragraphs_zh=["Only one zh paragraph."],
            content_sections=[
                _section(
                    "Brand Signals",
                    items=[
                        _item(
                            "The Row",
                            references=[_reference("The Row")],
                            paragraph_indices=[True, "0", -1, 0, 0, 1, 99, 2],  # type: ignore[list-item]
                        )
                    ],
                )
            ],
        ),
    )

    assert brief is not None
    assert [evidence.href for evidence in brief.evidence] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-3",
    ]
    emitted_hrefs = [evidence.href for evidence in brief.evidence]
    assert "#local-article-paragraph-0" not in emitted_hrefs
    assert "#local-article-paragraph-2" not in emitted_hrefs
    assert "#local-article-paragraph-100" not in emitted_hrefs
    assert brief.evidence[0].excerpt.zh == "Usable first paragraph."


def test_build_local_article_intelligence_brief_caps_outputs_deterministically() -> None:
    long_text = "Signal language " * 40
    brief = build_row_one_local_article_intelligence_brief(
        story=_story(),
        local_article=_article(
            paragraphs=[long_text, *[f"Paragraph {index}" for index in range(12)]],
            paragraphs_zh=[long_text, *[f"Paragraph zh {index}" for index in range(12)]],
            brief_sections=[_brief(body=_lt(long_text, long_text))],
            content_sections=[
                _section(
                    "Brand Signals",
                    key="brand_signals",
                    items=[
                        _item(
                            f"Theme {index}",
                            references=[
                                _reference(f"Brand {index}", ref_type="brand", label="brand"),
                                _reference(f"Product {index}", ref_type="shoe", label="product"),
                                _reference(f"Person {index}", ref_type="person", label="designer"),
                            ],
                            paragraph_indices=[index],
                        )
                        for index in range(12)
                    ],
                ),
                *[
                    _section(
                        f"Route Section {index}",
                        key="takeaways",
                        items=[_item(f"Route item {index}")],
                    )
                    for index in range(8)
                ],
            ],
        ),
    )

    assert brief is not None
    assert len(brief.lanes) == LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES
    assert all(
        len(lane.chips) <= LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE
        for lane in brief.lanes
    )
    assert len(brief.evidence) == LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_EVIDENCE_LINKS
    assert len(brief.routes) == LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTE_LINKS
    by_key = {lane.key: lane for lane in brief.lanes}
    assert [chip.label.en for chip in by_key["brands"].chips] == [
        f"Brand {index}" for index in range(LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE)
    ]
    assert [evidence.href for evidence in brief.evidence] == [
        f"#local-article-paragraph-{index}" for index in range(1, 5)
    ]
    assert brief.opening_signal.en.endswith("...")


def test_build_local_article_intelligence_brief_falls_back_without_brief_sections() -> None:
    story_fallback = build_row_one_local_article_intelligence_brief(
        story=_story(),
        local_article=_article(content_sections=[]),
    )
    assert story_fallback is not None
    assert story_fallback.opening_signal.en == "Story why it matters"

    section_fallback = build_row_one_local_article_intelligence_brief(
        story=_story().model_copy(update={"why_it_matters": _lt(" ", "")}),
        local_article=_article(
            brief_sections=[],
            content_sections=[
                _section(
                    "Brand Signals",
                    body=_lt("Section body explains the local article.", "栏目正文解释本地文章。"),
                    items=[],
                )
            ],
        ),
    )
    assert section_fallback is not None
    assert section_fallback.opening_signal.en == "Section body explains the local article."
    assert section_fallback.opening_signal.zh == "栏目正文解释本地文章。"


def test_build_local_article_intelligence_brief_returns_none_without_meaningful_body() -> None:
    assert (
        build_row_one_local_article_intelligence_brief(
            story=_story("unsafe/story"),
            local_article=_article("unsafe/story"),
        )
        is None
    )
    assert (
        build_row_one_local_article_intelligence_brief(
            story=_story(),
            local_article=_article("other-signal-1234567890"),
        )
        is None
    )
    assert (
        build_row_one_local_article_intelligence_brief(
            story=_story().model_copy(update={"why_it_matters": _lt(" ", "")}),
            local_article=_article(
                paragraphs=[" ", ""],
                paragraphs_zh=[],
                brief_sections=[],
                content_sections=[
                    RowOneLocalArticleContentSection(
                        key="entities",
                        title=_lt(" ", ""),
                        body=_lt(" ", ""),
                        items=[
                            RowOneLocalArticleContentItem(
                                label=_lt(" ", ""),
                                body=_lt(" ", ""),
                                references=[],
                                paragraph_indices=[0],
                            )
                        ],
                    )
                ],
            ),
        )
        is None
    )
