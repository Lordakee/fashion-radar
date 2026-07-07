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
from fashion_radar.row_one.saved_article_library import (
    _strict_valid_saved_article_library_paragraph_indices,
    build_row_one_saved_article_library,
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
            RowOneSection(
                key="celebrity_style",
                title=LocalizedText(zh="明星穿搭", en="Celebrity Style"),
                dek=LocalizedText(zh="明星。", en="Celebrity looks."),
            ),
            RowOneSection(
                key="hot_products",
                title=LocalizedText(zh="热门单品", en="Hot Products"),
                dek=LocalizedText(zh="单品。", en="Products."),
            ),
            RowOneSection(
                key="rising_radar",
                title=LocalizedText(zh="上升雷达", en="Rising Radar"),
                dek=LocalizedText(zh="上升。", en="Rising signals."),
            ),
        ],
        stories=list(stories),
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
    body_source: str = "extracted",
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh or [],
        content_sections=content_sections or [],
        body_source=body_source,
    )


def _item(
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


def test_saved_article_library_groups_articles_by_source_and_builds_counts() -> None:
    story_a = _story("the-row-a-1234567890", "The Row market signal", section_key="top_stories")
    story_b = _story("shoe-b-1234567890", "Alaia shoe signal", section_key="hot_products")

    library = build_row_one_saved_article_library(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                title="The Row saved source",
                source_name="Vogue Business",
                paragraphs=["Lead paragraph.", "Second paragraph."],
                content_sections=[
                    _section(
                        "takeaways",
                        "Takeaways",
                        items=[
                            _item(
                                "Lead",
                                body="The Row demand is rising.",
                                paragraph_indices=[0, 1],
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
            story_b.id: _article(
                story_b.id,
                title="Alaia saved source",
                source_name="Vogue Business",
                paragraphs=["Alaia mesh shoe paragraph."],
                content_sections=[
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _item(
                                "Shoe",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(
                                        name="Alaia",
                                        type="brand",
                                        label="shoe",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert library is not None
    assert library.article_count == 2
    assert library.source_count == 1
    assert library.saved_paragraph_count == 3
    assert library.organized_section_count == 2
    assert library.groups[0].source_name == "Vogue Business"
    assert library.groups[0].article_count == 2
    assert library.groups[0].saved_paragraph_count == 3
    assert library.groups[0].organized_section_count == 2
    assert [entry.title.en for entry in library.groups[0].entries] == [
        "The Row saved source",
        "Alaia saved source",
    ]
    assert [entry.section_title.en for entry in library.groups[0].entries] == [
        "Top Stories",
        "Hot Products",
    ]
    assert library.groups[0].entries[0].digest_path == (
        "details/the-row-a-1234567890.html#local-article-digest"
    )
    assert library.groups[0].entries[0].reader_path == (
        "details/the-row-a-1234567890.html#local-article-reader"
    )
    assert library.groups[0].entries[0].evidence_path == (
        "details/the-row-a-1234567890.html#local-article-paragraph-evidence"
    )
    assert [link.href for link in library.groups[0].entries[0].paragraph_links] == [
        "details/the-row-a-1234567890.html#local-article-paragraph-1",
        "details/the-row-a-1234567890.html#local-article-paragraph-2",
    ]
    assert [link.label.en for link in library.groups[0].entries[0].paragraph_links] == [
        "Paragraph 1",
        "Paragraph 2",
    ]
    assert [(ref.name, ref.type, ref.label) for ref in library.groups[0].entries[0].references] == [
        ("The Row", "brand", "tracked"),
    ]


def test_saved_article_library_tracks_body_source_counts_for_included_articles() -> None:
    extracted_story = _story("extracted-1234567890", "Extracted story")
    fallback_story = _story("fallback-1234567890", "Fallback story")
    skipped_story = _story("skipped-1234567890", "Skipped story")
    empty_skipped_story = _story("empty-skipped-1234567890", "Empty skipped story")

    library = build_row_one_saved_article_library(
        _edition(extracted_story, fallback_story, skipped_story, empty_skipped_story),
        {
            extracted_story.id: _article(extracted_story.id, body_source="extracted"),
            fallback_story.id: _article(
                fallback_story.id,
                body_source="summary_fallback",
            ),
            skipped_story.id: _article(
                skipped_story.id,
                body_source="skipped",
                paragraphs=["Diagnostic paragraph."],
            ),
            empty_skipped_story.id: _article(
                empty_skipped_story.id,
                body_source="skipped",
                paragraphs=["   "],
            ),
        },
    )

    assert library is not None
    assert library.article_count == 3
    assert library.extracted_article_count == 1
    assert library.summary_fallback_article_count == 1
    assert library.skipped_article_count == 1
    assert [entry.body_source for entry in library.groups[0].entries] == [
        "extracted",
        "summary_fallback",
        "skipped",
    ]


def test_saved_article_library_filters_unsafe_or_unusable_articles() -> None:
    valid_story = _story("valid-1234567890", "Valid story")
    unsafe_route_story = _story("unsafe-route-1234567890", "Unsafe route").model_copy(
        update={"detail_path": "../outside.html"}
    )
    bad_id_story = _story("bad id", "Bad ID").model_copy(
        update={"detail_path": "details/bad-id-1234567890.html"}
    )
    mismatched_article_story = _story("mismatch-1234567890", "Mismatched article")

    library = build_row_one_saved_article_library(
        _edition(valid_story, unsafe_route_story, bad_id_story, mismatched_article_story),
        {
            valid_story.id: _article(valid_story.id, paragraphs=["   "]),
            unsafe_route_story.id: _article(unsafe_route_story.id, paragraphs=["Saved."]),
            bad_id_story.id: _article(bad_id_story.id, paragraphs=["Saved."]),
            mismatched_article_story.id: _article(
                "other-story-1234567890",
                paragraphs=["Saved."],
            ),
            "not-in-edition-1234567890": _article(
                "not-in-edition-1234567890",
                paragraphs=["Saved."],
            ),
        },
    )

    assert library is None


def test_saved_article_library_caps_entries_references_and_paragraph_links() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}") for index in range(12)]
    local_articles = {
        story.id: _article(
            story.id,
            source_name="Shared Source" if index < 9 else f"Source {index}",
            paragraphs=[f"Paragraph {paragraph}" for paragraph in range(10)],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Refs",
                            paragraph_indices=list(range(10)),
                            references=[
                                RowOneReference(
                                    name=f"Ref {ref}",
                                    type="brand",
                                    label="tracked",
                                )
                                for ref in range(10)
                            ],
                        )
                    ],
                )
            ],
        )
        for index, story in enumerate(stories)
    }

    library = build_row_one_saved_article_library(_edition(*stories), local_articles)

    assert library is not None
    assert library.article_count == 12
    assert library.extracted_article_count == 12
    assert library.summary_fallback_article_count == 0
    assert library.skipped_article_count == 0
    assert len(library.groups) == 4
    assert len(library.groups[0].entries) == 8
    assert len(library.groups[0].entries[0].references) == 6
    assert len(library.groups[0].entries[0].paragraph_links) == 4


def test_saved_article_library_caps_source_groups() -> None:
    stories = [_story(f"group-{index}-1234567890", f"Group Story {index}") for index in range(10)]
    local_articles = {
        story.id: _article(
            story.id,
            source_name=f"Source {index}",
            paragraphs=["Saved paragraph."],
        )
        for index, story in enumerate(stories)
    }

    library = build_row_one_saved_article_library(_edition(*stories), local_articles)

    assert library is not None
    assert library.article_count == 10
    assert library.extracted_article_count == 10
    assert library.summary_fallback_article_count == 0
    assert library.skipped_article_count == 0
    assert library.source_count == 10
    assert len(library.groups) == 8
    assert [group.source_name for group in library.groups] == [
        f"Source {index}" for index in range(8)
    ]


def test_saved_article_library_filters_invalid_paragraph_indices() -> None:
    story = _story("the-row-a-1234567890", "The Row market signal")
    library = build_row_one_saved_article_library(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["First paragraph.", "   ", "Third paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Refs",
                                paragraph_indices=[
                                    -1,
                                    0,
                                    1,
                                    2,
                                    2,
                                    99,
                                ],
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert library is not None
    assert [link.href for link in library.groups[0].entries[0].paragraph_links] == [
        "details/the-row-a-1234567890.html#local-article-paragraph-1",
        "details/the-row-a-1234567890.html#local-article-paragraph-3",
    ]


def test_strict_valid_saved_article_library_paragraph_indices_rejects_bool_values() -> None:
    assert _strict_valid_saved_article_library_paragraph_indices(
        [True, False, -1, 0, 0, 1, "2", 2, 99],
        {0, 2},
    ) == (0, 2)
