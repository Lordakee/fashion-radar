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


def test_build_row_one_local_article_intelligence_uses_curated_first_takeaway() -> None:
    story = _story(
        "the-row-1234567890",
        "The Row saved article",
        detail_path="details/the-row-1234567890.html",
        entity_refs=[RowOneReference(name="The Row", type="brand", label="tracked")],
        product_refs=[RowOneReference(name="Margaux", type="bag", label="product")],
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Opening source context without a named product signal.",
            "The Row and Margaux moved together in the saved local source.",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="The Row 和 Margaux 在本地来源中一起变化。",
                            en="The Row and Margaux moved together in the saved local source.",
                        ),
                        paragraph_indices=[1],
                    ),
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源要点 2", en="Source point 2"),
                        body=LocalizedText(
                            zh="没有明确产品信号的开头上下文。",
                            en="Opening source context without a named product signal.",
                        ),
                        paragraph_indices=[0],
                    ),
                ],
            )
        ],
    )

    sections = build_row_one_local_article_intelligence(_edition([story]), {story.id: article})

    strongest = next(section for section in sections if section.key == "strongest_reads")
    item = strongest.items[0]
    assert item.body.en == "The Row and Margaux moved together in the saved local source."
    assert item.paragraph_indices == [1]


def test_build_row_one_local_article_intelligence_preserves_article_content_segments() -> None:
    the_row = RowOneReference(name="The Row", type="brand", label="tracked")
    margaux = RowOneReference(name="Margaux", type="bag", label="product")
    story = _story(
        "the-row-1234567890",
        "The Row demand moves",
        detail_path="details/the-row-1234567890.html",
        entity_refs=[the_row],
        product_refs=[margaux],
        heat_delta=7,
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row opened with broader market context.",
            "Margaux demand was called out as a bag signal.",
        ],
        paragraphs_zh=["The Row 中文上下文。", "Margaux 中文产品信号。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                body=LocalizedText(
                    zh="本地保存正文首先指向这些要点。",
                    en="The saved source text points to these reads.",
                ),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="The Row 中文上下文。",
                            en="The Row opened with broader market context.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品信号", en="Product Signals"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Margaux", en="Margaux"),
                        body=LocalizedText(
                            zh="bag / product",
                            en="bag / product",
                        ),
                        references=[margaux],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {story.id: article},
    )

    strongest = next(section for section in sections if section.key == "strongest_reads")
    item = strongest.items[0]
    assert [segment.key for segment in item.segments] == ["takeaways", "product_signals"]
    assert item.segments[0].title.en == "Takeaways"
    assert item.segments[0].body is not None
    assert item.segments[0].body.en == "The saved source text points to these reads."
    assert item.segments[0].items[0].label.en == "Source lead"
    assert item.segments[0].items[0].body is not None
    assert item.segments[0].items[0].body.en == "The Row opened with broader market context."
    assert item.segments[0].items[0].paragraph_indices == [0]
    assert item.segments[1].items[0].references == [margaux]
    dumped = item.model_dump(mode="json")
    assert "paragraphs" not in dumped


def test_build_row_one_local_article_intelligence_uses_matching_reference_segments() -> None:
    the_row = RowOneReference(name="The Row", type="brand", label="tracked")
    story = _story(
        "the-row-1234567890",
        "The Row context",
        detail_path="details/the-row-1234567890.html",
        entity_refs=[the_row],
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Generic opening paragraph.",
            "The Row paragraph has the useful brand context.",
        ],
        paragraphs_zh=["通用开头。", "The Row 中文品牌上下文。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(zh="通用开头。", en="Generic opening paragraph."),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="相关对象", en="Entities"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="The Row", en="The Row"),
                        body=LocalizedText(
                            zh="brand / tracked",
                            en="brand / tracked",
                        ),
                        references=[the_row],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {story.id: article},
    )

    brand_watch = next(section for section in sections if section.key == "brand_watch")
    item = brand_watch.items[0]
    assert item.body.en == (
        "The Row paragraph has the useful brand context. Sources: Vogue Business."
    )
    assert item.paragraph_indices == [1]
    assert [segment.key for segment in item.segments] == ["entities"]
    assert item.segments[0].items[0].label.en == "The Row"
    assert item.segments[0].items[0].paragraph_indices == [1]


def test_reference_segments_can_upgrade_from_fallback_to_later_match() -> None:
    first_ref = RowOneReference(name="The Row", type="brand", label="tracked")
    later_ref = RowOneReference(name="the row", type="brand", label="tracked")
    first_story = _story(
        "story-a-1234567890",
        "Generic The Row mention",
        detail_path="details/story-a-1234567890.html",
        entity_refs=[first_ref],
    )
    later_story = _story(
        "story-b-1234567890",
        "Specific The Row context",
        detail_path="details/story-b-1234567890.html",
        source_name="WWD",
        entity_refs=[later_ref],
    )
    first_article = RowOneLocalArticle(
        story_id=first_story.id,
        title="Generic local source",
        url="https://example.com/a",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Generic opening with The Row but no structured reference segment."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="通用 The Row 开头。",
                            en="Generic opening with The Row but no structured reference segment.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )
    later_article = RowOneLocalArticle(
        story_id=later_story.id,
        title="Specific local source",
        url="https://example.com/b",
        source_name="WWD",
        extracted_at=AS_OF,
        paragraphs=["Specific intro.", "The Row has the later matched segment."],
        paragraphs_zh=["具体导语。", "The Row 后续匹配段落。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="相关对象", en="Entities"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="The Row", en="The Row"),
                        body=LocalizedText(zh="brand / tracked", en="brand / tracked"),
                        references=[later_ref],
                        paragraph_indices=[1],
                    )
                ],
            )
        ],
    )

    sections = build_row_one_local_article_intelligence(
        _edition([first_story, later_story]),
        {
            first_story.id: first_article,
            later_story.id: later_article,
        },
    )

    brand_watch = next(section for section in sections if section.key == "brand_watch")
    item = brand_watch.items[0]
    assert item.paragraph_indices == [1]
    assert item.segments[0].key == "entities"
    assert item.segments[0].items[0].label.en == "The Row"


def test_product_reference_segments_do_not_cross_match_same_name_entity() -> None:
    entity_ref = RowOneReference(name="Muse", type="brand", label="tracked")
    product_ref = RowOneReference(name="Muse", type="bag", label="product")
    story = _story(
        "muse-1234567890",
        "Muse product context",
        detail_path="details/muse-1234567890.html",
        entity_refs=[entity_ref],
        product_refs=[product_ref],
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="Muse local source",
        url="https://example.com/muse",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Muse brand paragraph.",
            "Muse bag paragraph.",
        ],
        paragraphs_zh=["Muse 品牌段落。", "Muse 包袋段落。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="相关对象", en="Entities"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Muse", en="Muse"),
                        body=LocalizedText(zh="brand / tracked", en="brand / tracked"),
                        references=[entity_ref],
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品信号", en="Product Signals"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Muse", en="Muse"),
                        body=LocalizedText(zh="bag / product", en="bag / product"),
                        references=[product_ref],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {story.id: article},
    )

    product_watch = next(section for section in sections if section.key == "product_watch")
    item = product_watch.items[0]
    assert item.paragraph_indices == [1]
    assert [segment.key for segment in item.segments] == ["product_signals"]
    assert item.segments[0].items[0].references == [product_ref]


def test_local_intelligence_segments_are_capped() -> None:
    story = _story(
        "capped-1234567890",
        "Capped local article",
        detail_path="details/capped-1234567890.html",
    )
    sections = [
        RowOneLocalArticleContentSection(
            key="takeaways",
            title=LocalizedText(zh="正文重点", en="Takeaways"),
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(zh=f"条目 {index}", en=f"Item {index}"),
                    body=LocalizedText(zh=f"中文 {index}", en=f"Body {index}"),
                    paragraph_indices=[index],
                )
                for index in range(6)
            ],
        ),
        RowOneLocalArticleContentSection(
            key="entities",
            title=LocalizedText(zh="相关对象", en="Entities"),
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(zh="The Row", en="The Row"),
                    body=LocalizedText(zh="brand / tracked", en="brand / tracked"),
                    paragraph_indices=[0],
                )
            ],
        ),
        RowOneLocalArticleContentSection(
            key="product_signals",
            title=LocalizedText(zh="产品信号", en="Product Signals"),
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(zh="Margaux", en="Margaux"),
                    body=LocalizedText(zh="bag / product", en="bag / product"),
                    paragraph_indices=[1],
                )
            ],
        ),
        RowOneLocalArticleContentSection(
            key="brand_signals",
            title=LocalizedText(zh="品牌信号", en="Brand Signals"),
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(zh="来源", en="Source"),
                    body=LocalizedText(zh="Vogue Business", en="Vogue Business"),
                )
            ],
        ),
        RowOneLocalArticleContentSection(
            key="takeaways",
            title=LocalizedText(zh="多余段落", en="Overflow"),
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(zh="多余", en="Overflow"),
                    body=LocalizedText(zh="不应出现", en="Should not appear"),
                )
            ],
        ),
    ]
    article = RowOneLocalArticle(
        story_id=story.id,
        title="Capped local source",
        url="https://example.com/capped",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Source paragraph."],
        content_sections=sections,
    )

    intelligence_sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {story.id: article},
    )

    strongest = next(
        section for section in intelligence_sections if section.key == "strongest_reads"
    )
    item = strongest.items[0]
    assert len(item.segments) == 4
    assert [segment.key for segment in item.segments] == [
        "takeaways",
        "entities",
        "product_signals",
        "brand_signals",
    ]
    assert len(item.segments[0].items) == 3
    assert [segment_item.label.en for segment_item in item.segments[0].items] == [
        "Item 0",
        "Item 1",
        "Item 2",
    ]
