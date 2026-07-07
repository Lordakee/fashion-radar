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
from fashion_radar.row_one.saved_article_theme_digest import (
    build_row_one_saved_article_theme_digest,
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


def _library_with_safe_story(story_id: str) -> RowOneSavedArticleLibrary:
    return RowOneSavedArticleLibrary(
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
                        digest_path=f"details/{story_id}.html#local-article-digest",
                        reader_path=f"details/{story_id}.html#local-article-reader",
                        evidence_path=(f"details/{story_id}.html#local-article-paragraph-evidence"),
                    )
                ],
            )
        ],
    )


def _organization_card(
    *,
    title: str = "The Row card",
    source_name: str = "Vogue Business",
    lead: str = "Saved lead",
    detail_path: str = "details/the-row-a-1234567890.html#local-article-content-section-1",
) -> RowOneSavedArticleContentOrganizationCard:
    return RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en=title, zh=title),
        source_name=source_name,
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Read First", zh="优先阅读"),
        lead=LocalizedText(en=lead, zh=lead),
        detail_path=detail_path,
        paragraph_indices=(0,),
        references=(),
    )


def test_saved_article_theme_digest_builds_theme_cards_from_existing_saved_inputs() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    article = _article(
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
                "product_signals",
                "Products",
                items=[
                    _item(
                        "Product",
                        body="The new bag shape is driving saved coverage.",
                        body_zh="新包型正在带动保存报道。",
                        paragraph_indices=[1],
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="bag", type="product", label="product"),
                        ],
                    )
                ],
            ),
        ],
    )
    edition = _edition(story)
    library = build_row_one_saved_article_library(edition, {story.id: article})
    organization = build_row_one_saved_article_content_organization(edition, {story.id: article})

    digest = build_row_one_saved_article_theme_digest(library, organization)

    assert digest is not None
    assert digest.theme_count == 2
    assert digest.item_count == 2
    assert digest.source_count == 1
    assert digest.themes[0].key == "read_first"
    assert digest.themes[0].source_count == 1
    assert digest.themes[0].items[0].lead.en == "Start with The Row retail signal."
    assert digest.themes[0].items[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert digest.themes[1].key == "products"
    assert digest.themes[1].items[0].references[1].name == "bag"


def test_saved_article_theme_digest_rejects_unsafe_or_unmatched_detail_paths() -> None:
    library = _library_with_safe_story("the-row-a-1234567890")
    safe_card = _organization_card(
        lead="Safe lead",
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Start here", zh="从这里开始"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Traversal lead", zh="越界摘要"),
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Unmatched lead", zh="未匹配摘要"),
                        detail_path="details/other-story.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Wrong fragment", zh="错误锚点"),
                        detail_path="details/the-row-a-1234567890.html#external",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Javascript route", zh="脚本路由"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Leading zero", zh="前导零"),
                        detail_path=(
                            "details/the-row-a-1234567890.html#local-article-content-section-01"
                        ),
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Zero section", zh="零号栏目"),
                        detail_path=(
                            "details/the-row-a-1234567890.html#local-article-content-section-0"
                        ),
                    ),
                ],
            )
        ],
    )

    digest = build_row_one_saved_article_theme_digest(library, organization)

    assert digest is not None
    assert digest.item_count == 1
    rendered_leads = [item.lead.en for theme in digest.themes for item in theme.items]
    assert rendered_leads == ["Safe lead"]


def test_saved_article_theme_digest_caps_and_dedupes_theme_items() -> None:
    library = _library_with_safe_story("the-row-a-1234567890")
    duplicate_cards = [
        _organization_card(
            title=f"The Row card {index}",
            lead="Repeated signal",
            detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        )
        for index in range(8)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Start here", zh="从这里开始"),
                cards=duplicate_cards,
            )
        ],
    )

    digest = build_row_one_saved_article_theme_digest(library, organization)

    assert digest is not None
    assert digest.theme_count == 1
    assert digest.item_count == 1


def test_saved_article_theme_digest_maps_source_groups_and_counts_source_union() -> None:
    story_ids = [
        "story-one-1234567890",
        "story-two-1234567890",
        "story-three-1234567890",
        "story-four-1234567890",
        "story-five-1234567890",
    ]
    library = RowOneSavedArticleLibrary(
        article_count=5,
        source_count=2,
        saved_paragraph_count=5,
        organized_section_count=5,
        extracted_article_count=5,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=5,
                saved_paragraph_count=5,
                organized_section_count=5,
                entries=[
                    RowOneSavedArticleLibraryEntry(
                        title=LocalizedText(en=story_id, zh=story_id),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        body_source="extracted",
                        digest_path=f"details/{story_id}.html#local-article-digest",
                        reader_path=f"details/{story_id}.html#local-article-reader",
                        evidence_path=f"details/{story_id}.html#local-article-paragraph-evidence",
                    )
                    for story_id in story_ids
                ],
            )
        ],
    )
    groups = [
        RowOneSavedArticleContentOrganizationGroup(
            key=group_key,
            title=LocalizedText(en=group_key, zh=group_key),
            dek=LocalizedText(en="Group dek", zh="分组说明"),
            cards=[
                _organization_card(
                    source_name=source_name,
                    lead=f"{group_key} lead {index}",
                    detail_path=f"details/{story_id}.html#local-article-content-section-1",
                )
                for index, (story_id, source_name) in enumerate(
                    zip(
                        story_ids[:4],
                        ["Vogue Business", "VOGUE BUSINESS", "WWD", "Elle"],
                        strict=True,
                    ),
                    start=1,
                )
            ],
        )
        for group_key in [
            "product_signals",
            "entities",
            "brand_signals",
            "takeaways",
            "unknown",
        ]
    ]
    organization = RowOneSavedArticleContentOrganization(groups=groups)

    digest = build_row_one_saved_article_theme_digest(library, organization)

    assert digest is not None
    assert [theme.key for theme in digest.themes] == [
        "products",
        "people_brands",
        "source_structure",
        "read_first",
    ]
    assert all(theme.item_count == 3 for theme in digest.themes)
    assert all(theme.source_count == 2 for theme in digest.themes)
    assert digest.source_count == 2
    assert digest.item_count == 12


def test_saved_article_theme_digest_omits_empty_inputs() -> None:
    assert build_row_one_saved_article_theme_digest(None, None) is None
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
    assert build_row_one_saved_article_theme_digest(empty_library, None) is None
    empty_organization = RowOneSavedArticleContentOrganization(groups=[])
    assert build_row_one_saved_article_theme_digest(empty_library, empty_organization) is None
