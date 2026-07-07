from __future__ import annotations

from dataclasses import replace
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
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
    build_row_one_saved_article_content_organization,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
    build_row_one_saved_article_library,
)
from fashion_radar.row_one.saved_article_reading_paths import (
    build_row_one_saved_article_reading_paths,
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
                key="hot_products",
                title=LocalizedText(zh="热门单品", en="Hot Products"),
                dek=LocalizedText(zh="单品。", en="Products."),
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


def test_saved_article_reading_paths_builds_paths_from_library_and_content_organization() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    library = build_row_one_saved_article_library(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["The Row paragraph.", "Alaia paragraph."],
                content_sections=[
                    _section(
                        "takeaways",
                        "Read First",
                        items=[
                            _item(
                                "Lead",
                                body="Start with The Row retail signal.",
                                body_zh="先看 The Row 零售信号。",
                                paragraph_indices=[0],
                            )
                        ],
                    ),
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Brand",
                                body="The Row remains central.",
                                body_zh="The Row 仍是核心。",
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
                    ),
                ],
            )
        },
    )
    organization = build_row_one_saved_article_content_organization(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["The Row paragraph.", "Alaia paragraph."],
                content_sections=[
                    _section(
                        "takeaways",
                        "Read First",
                        items=[
                            _item(
                                "Lead",
                                body="Start with The Row retail signal.",
                                body_zh="先看 The Row 零售信号。",
                                paragraph_indices=[0],
                            )
                        ],
                    ),
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Brand",
                                body="The Row remains central.",
                                body_zh="The Row 仍是核心。",
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
                    ),
                ],
            )
        },
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    assert reading_paths.path_count == 2
    assert reading_paths.step_count == 2
    assert [path.key for path in reading_paths.paths] == ["takeaways", "entities"]
    assert reading_paths.paths[0].title.en == "Read First"
    assert reading_paths.paths[0].steps[0].lead.en == "Start with The Row retail signal."
    assert reading_paths.paths[0].steps[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert reading_paths.paths[0].steps[0].paragraph_indices == (0,)
    assert reading_paths.paths[1].steps[0].references[0].name == "The Row"


def test_saved_article_reading_paths_canonicalizes_content_card_detail_paths() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    library = build_row_one_saved_article_library(
        _edition(story),
        {
            story.id: _article(
                story.id,
                content_sections=[
                    _section(
                        "takeaways",
                        "Read First",
                        items=[_item("Lead", body="Canonical lead.", paragraph_indices=[0])],
                    )
                ],
            )
        },
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Start here", zh="从这里开始"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Canonical card", zh="规范卡片"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        section_label=LocalizedText(en="Read First", zh="优先阅读"),
                        lead=LocalizedText(en="Canonical lead.", zh="规范摘要。"),
                        detail_path=(
                            "details/./the-row-a-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                    )
                ],
            )
        ],
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    assert reading_paths.paths[0].steps[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )


def test_saved_article_reading_paths_rejects_noncanonical_content_section_fragments() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Zero section lead", zh="零栏目摘要"),
                        detail_path=(
                            "details/the-row-a-1234567890.html#local-article-content-section-0"
                        ),
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Padded section lead", zh="补零栏目摘要"),
                        detail_path=(
                            "details/the-row-a-1234567890.html#local-article-content-section-01"
                        ),
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Paragraph lead", zh="段落摘要"),
                        detail_path="details/the-row-a-1234567890.html#local-article-paragraph-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Missing hash lead", zh="缺少锚点摘要"),
                        detail_path="details/the-row-a-1234567890.html",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="JS lead", zh="脚本摘要"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Traversal lead", zh="越界摘要"),
                        detail_path="../secrets.html#local-article-content-section-1",
                    ),
                ],
            )
        ]
    )
    library = RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=1,
        organized_section_count=1,
        extracted_article_count=1,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=1,
                organized_section_count=1,
                entries=[
                    RowOneSavedArticleLibraryEntry(
                        title=LocalizedText(en="Entry", zh="条目"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        body_source="extracted",
                        digest_path="details/the-row-a-1234567890.html#local-article-digest",
                        reader_path="details/the-row-a-1234567890.html#local-article-reader",
                        evidence_path=(
                            "details/the-row-a-1234567890.html#local-article-paragraph-evidence"
                        ),
                    )
                ],
            )
        ],
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    text = " ".join(step.lead.en for path in reading_paths.paths for step in path.steps)
    assert "Safe lead" in text
    assert "Zero section lead" not in text
    assert "Padded section lead" not in text
    assert "Paragraph lead" not in text
    assert "Missing hash lead" not in text
    assert "JS lead" not in text
    assert "Traversal lead" not in text


def test_saved_article_reading_paths_accepts_step_when_any_one_library_route_is_safe() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )

    for reader_path, digest_path, evidence_path in (
        (
            "../outside.html#local-article-reader",
            "details/the-row-a-1234567890.html#local-article-digest",
            "../outside.html#local-article-paragraph-evidence",
        ),
        (
            "../outside.html#local-article-reader",
            "../outside.html#local-article-digest",
            "details/the-row-a-1234567890.html#local-article-paragraph-evidence",
        ),
    ):
        library = RowOneSavedArticleLibrary(
            article_count=1,
            source_count=1,
            saved_paragraph_count=1,
            organized_section_count=1,
            extracted_article_count=1,
            summary_fallback_article_count=0,
            skipped_article_count=0,
            groups=[
                RowOneSavedArticleLibrarySourceGroup(
                    source_name="Vogue Business",
                    article_count=1,
                    saved_paragraph_count=1,
                    organized_section_count=1,
                    entries=[
                        RowOneSavedArticleLibraryEntry(
                            title=LocalizedText(en="Entry", zh="条目"),
                            source_name="Vogue Business",
                            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                            saved_paragraph_count=1,
                            organized_section_count=1,
                            body_source="extracted",
                            digest_path=digest_path,
                            reader_path=reader_path,
                            evidence_path=evidence_path,
                        )
                    ],
                )
            ],
        )

        reading_paths = build_row_one_saved_article_reading_paths(library, organization)

        assert reading_paths is not None
        assert reading_paths.paths[0].steps[0].lead.en == "Safe lead"


def test_saved_article_reading_paths_caps_paths_steps_and_dedupes_steps() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}") for index in range(1, 7)]
    articles = {
        story.id: _article(story.id, paragraphs=[f"Paragraph {index}."])
        for index, story in enumerate(stories, start=1)
    }
    library = build_row_one_saved_article_library(_edition(*stories), articles)
    assert library is not None

    groups: list[RowOneSavedArticleContentOrganizationGroup] = []
    for group_index in range(1, 6):
        cards: list[RowOneSavedArticleContentOrganizationCard] = []
        for step_index, story in enumerate(stories[:5], start=1):
            cards.append(
                RowOneSavedArticleContentOrganizationCard(
                    title=LocalizedText(en=f"Group {group_index} Card {step_index}", zh="卡片"),
                    source_name="Vogue Business",
                    section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                    section_label=LocalizedText(en=f"Group {group_index}", zh="分组"),
                    lead=LocalizedText(en=f"Lead {group_index}-{step_index}.", zh="摘要。"),
                    detail_path=(
                        f"details/{story.id}.html#local-article-content-section-{step_index}"
                    ),
                    paragraph_indices=(0,),
                    references=(),
                )
            )
        cards.insert(1, cards[0])
        groups.append(
            RowOneSavedArticleContentOrganizationGroup(
                key=f"group-{group_index}",
                title=LocalizedText(en=f"Group {group_index}", zh="分组"),
                dek=LocalizedText(en="Path dek", zh="路径说明"),
                cards=cards,
            )
        )
    organization = RowOneSavedArticleContentOrganization(groups=groups)

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    assert len(reading_paths.paths) == 4
    assert all(path.step_count <= 3 for path in reading_paths.paths)
    assert [step.lead.en for step in reading_paths.paths[0].steps] == [
        "Lead 1-1.",
        "Lead 1-2.",
        "Lead 1-3.",
    ]


def test_saved_article_reading_paths_requires_safe_library_entry_match() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        title=LocalizedText(en="Wrong path", zh="错误路径"),
                        lead=LocalizedText(en="Wrong path lead", zh="错误路径摘要"),
                        detail_path=(
                            "details/not-in-library-1234567890.html#local-article-content-section-1"
                        ),
                    ),
                    replace(
                        safe_card,
                        title=LocalizedText(en="Unsafe card", zh="不安全卡片"),
                        lead=LocalizedText(en="Unsafe lead", zh="不安全摘要"),
                        detail_path="../secrets.html#local-article-content-section-1",
                    ),
                ],
            )
        ]
    )
    library = RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=1,
        organized_section_count=1,
        extracted_article_count=1,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=1,
                organized_section_count=1,
                entries=[
                    RowOneSavedArticleLibraryEntry(
                        title=LocalizedText(en="Entry", zh="条目"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        body_source="extracted",
                        digest_path="details/the-row-a-1234567890.html#local-article-digest",
                        reader_path="details/the-row-a-1234567890.html#local-article-reader",
                        evidence_path=(
                            "details/the-row-a-1234567890.html#local-article-paragraph-evidence"
                        ),
                    )
                ],
            )
        ],
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    section_text = " ".join(step.lead.en for path in reading_paths.paths for step in path.steps)
    assert "Safe lead" in section_text
    assert "Wrong path lead" not in section_text
    assert "Unsafe lead" not in section_text


def test_saved_article_reading_paths_omits_empty_inputs() -> None:
    assert build_row_one_saved_article_reading_paths(None, None) is None
    empty_library = RowOneSavedArticleLibrary(
        article_count=0,
        source_count=0,
        saved_paragraph_count=0,
        organized_section_count=0,
        extracted_article_count=0,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[],
    )
    assert build_row_one_saved_article_reading_paths(empty_library, None) is None
    empty_organization = RowOneSavedArticleContentOrganization(groups=[])
    assert build_row_one_saved_article_reading_paths(empty_library, empty_organization) is None
