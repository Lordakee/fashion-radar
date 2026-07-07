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
from fashion_radar.row_one.saved_article_reference_atlas import (
    build_row_one_saved_article_reference_atlas,
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


def _library_with_safe_stories(*story_ids: str) -> RowOneSavedArticleLibrary:
    return RowOneSavedArticleLibrary(
        article_count=len(story_ids),
        source_count=1,
        saved_paragraph_count=len(story_ids),
        organized_section_count=len(story_ids),
        extracted_article_count=len(story_ids),
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=len(story_ids),
                saved_paragraph_count=len(story_ids),
                organized_section_count=len(story_ids),
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
                        evidence_path=(f"details/{story_id}.html#local-article-paragraph-evidence"),
                    )
                    for story_id in story_ids
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
    references: tuple[RowOneReference, ...] = (),
) -> RowOneSavedArticleContentOrganizationCard:
    return RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en=title, zh=title),
        source_name=source_name,
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Read First", zh="优先阅读"),
        lead=LocalizedText(en=lead, zh=lead),
        detail_path=detail_path,
        paragraph_indices=(0,),
        references=references,
    )


def test_saved_article_reference_atlas_builds_buckets_from_existing_references() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    article = _article(
        story.id,
        paragraphs=["The Row paragraph.", "Alaia paragraph."],
        content_sections=[
            _section(
                "entities",
                "People & Brands",
                items=[
                    _item(
                        "Brand",
                        body="The Row appears as the main brand signal.",
                        paragraph_indices=[0],
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(
                                name="Mary-Kate Olsen",
                                type="designer",
                                label="person",
                            ),
                        ],
                    )
                ],
            ),
            _section(
                "product_signals",
                "Products",
                items=[
                    _item(
                        "Product",
                        body="Alaia flats appear as the product signal.",
                        paragraph_indices=[1],
                        references=[
                            RowOneReference(name="Alaia flats", type="shoe", label="product"),
                        ],
                    )
                ],
            ),
        ],
    )
    edition = _edition(story)
    library = build_row_one_saved_article_library(edition, {story.id: article})
    organization = build_row_one_saved_article_content_organization(edition, {story.id: article})

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.bucket_count == 3
    assert atlas.reference_count == 3
    assert atlas.support_count == 3
    assert [bucket.key for bucket in atlas.buckets] == ["brands", "people", "products"]
    assert atlas.buckets[0].references[0].name == "The Row"
    assert atlas.buckets[0].references[0].support_count == 1
    assert atlas.buckets[0].references[0].source_count == 1
    assert atlas.buckets[0].references[0].supports[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert atlas.buckets[1].references[0].name == "Mary-Kate Olsen"
    assert atlas.buckets[2].references[0].name == "Alaia flats"


def test_saved_article_reference_atlas_dedupes_names_and_counts_sources() -> None:
    library = _library_with_safe_stories(
        "the-row-a-1234567890",
        "the-row-b-1234567890",
    )
    card_a = _organization_card(
        title="The Row A",
        source_name="Vogue Business",
        lead="Lead A",
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
    )
    card_b = _organization_card(
        title="The Row B",
        source_name="WWD",
        lead="Lead B",
        detail_path="details/the-row-b-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="the row", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=[card_a, card_b],
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.bucket_count == 1
    reference = atlas.buckets[0].references[0]
    assert reference.name == "The Row"
    assert reference.support_count == 2
    assert reference.source_count == 2
    assert [support.lead.en for support in reference.supports] == ["Lead A", "Lead B"]


def test_saved_article_reference_atlas_rejects_unsafe_or_unmatched_support_paths() -> None:
    library = _library_with_safe_stories("the-row-a-1234567890")
    safe_card = _organization_card(
        lead="Safe lead",
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        detail_path="details/other-story.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        detail_path="details/the-row-a-1234567890.html#external",
                    ),
                ],
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.support_count == 1
    assert atlas.buckets[0].references[0].supports[0].lead.en == "Safe lead"


def test_saved_article_reference_atlas_caps_buckets_references_and_supports() -> None:
    story_ids = [f"story-{index}-1234567890" for index in range(1, 9)]
    library = _library_with_safe_stories(*story_ids)
    cards = [
        _organization_card(
            title=f"Story {index}",
            source_name="Vogue Business" if index % 2 else "WWD",
            lead=f"Lead {index}",
            detail_path=f"details/{story_id}.html#local-article-content-section-1",
            references=(RowOneReference(name=f"Brand {index}", type="brand", label="tracked"),),
        )
        for index, story_id in enumerate(story_ids, start=1)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=cards,
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.bucket_count == 1
    assert len(atlas.buckets[0].references) == 6
    assert all(len(reference.supports) <= 3 for reference in atlas.buckets[0].references)


def test_saved_article_reference_atlas_uses_spec_aliases_and_source_context_fallback() -> None:
    story_ids = [f"alias-{index}-1234567890" for index in range(1, 6)]
    library = _library_with_safe_stories(*story_ids)
    refs = (
        RowOneReference(name="Khaite", type="designer_brand", label=""),
        RowOneReference(name="Phoebe Philo", type="creative_director", label=""),
        RowOneReference(name="Speedcat", type="sneaker", label=""),
        RowOneReference(name="Dover Street Market", type="retailer", label="market"),
        RowOneReference(name="T Magazine", type="newsletter", label="editorial source"),
    )
    cards = [
        _organization_card(
            title=f"Alias {index}",
            source_name=f"Source {index}",
            lead=f"Alias lead {index}",
            detail_path=f"details/{story_id}.html#local-article-content-section-1",
            references=(ref,),
        )
        for index, (story_id, ref) in enumerate(zip(story_ids, refs, strict=True), start=1)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=cards,
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    references_by_bucket = {
        bucket.key: [reference.name for reference in bucket.references] for bucket in atlas.buckets
    }
    assert references_by_bucket == {
        "brands": ["Khaite"],
        "people": ["Phoebe Philo"],
        "products": ["Speedcat"],
        "source_context": ["Dover Street Market", "T Magazine"],
    }


def test_saved_article_reference_atlas_covers_documented_extended_aliases() -> None:
    story_ids = [f"extended-{index}-1234567890" for index in range(1, 13)]
    library = _library_with_safe_stories(*story_ids)
    refs = (
        RowOneReference(name="Alaia", type="maison", label=""),
        RowOneReference(name="Fashion Editor", type="editor", label=""),
        RowOneReference(name="Linen dress", type="dress", label=""),
        RowOneReference(name="Mesh flats", type="flat", label=""),
        RowOneReference(name="Runway footwear", type="footwear", label=""),
        RowOneReference(name="Archive handbag", type="handbag", label=""),
        RowOneReference(name="Knitwear", type="apparel", label=""),
        RowOneReference(name="Pleated skirt", type="skirt", label=""),
        RowOneReference(name="CFDA", type="event", label=""),
        RowOneReference(name="Retail channel", type="channel", label=""),
        RowOneReference(name="Trade publication", type="publication", label=""),
        RowOneReference(name="Flagship store", type="store", label=""),
    )
    cards = [
        _organization_card(
            title=f"Extended {index}",
            source_name=f"Source {index}",
            lead=f"Extended alias lead {index}",
            detail_path=f"details/{story_id}.html#local-article-content-section-1",
            references=(ref,),
        )
        for index, (story_id, ref) in enumerate(zip(story_ids, refs, strict=True), start=1)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=cards,
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    references_by_bucket = {
        bucket.key: [reference.name for reference in bucket.references] for bucket in atlas.buckets
    }
    assert references_by_bucket == {
        "brands": ["Alaia"],
        "people": ["Fashion Editor"],
        "products": [
            "Linen dress",
            "Mesh flats",
            "Runway footwear",
            "Archive handbag",
            "Knitwear",
            "Pleated skirt",
        ],
        "source_context": [
            "CFDA",
            "Retail channel",
            "Trade publication",
            "Flagship store",
        ],
    }


def test_saved_article_reference_atlas_preserves_first_non_empty_type_and_label() -> None:
    library = _library_with_safe_stories(
        "first-empty-1234567890",
        "later-filled-1234567890",
    )
    first_card = _organization_card(
        title="First empty metadata",
        lead="First lead",
        detail_path="details/first-empty-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="The Row", type="", label="tracked"),),
    )
    second_card = _organization_card(
        title="Later filled metadata",
        lead="Second lead",
        detail_path="details/later-filled-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="the row", type="brand", label="heritage"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=[first_card, second_card],
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    reference = atlas.buckets[0].references[0]
    assert reference.name == "The Row"
    assert reference.reference_type == "brand"
    assert reference.label == "tracked"


def test_saved_article_reference_atlas_counts_sources_before_support_cap() -> None:
    story_ids = [f"source-{index}-1234567890" for index in range(1, 6)]
    library = _library_with_safe_stories(*story_ids)
    cards = [
        _organization_card(
            title=f"Source {index}",
            source_name=f"Source {index}",
            lead=f"Support lead {index}",
            detail_path=f"details/{story_id}.html#local-article-content-section-1",
            references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
        )
        for index, story_id in enumerate(story_ids, start=1)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=cards,
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    reference = atlas.buckets[0].references[0]
    assert reference.support_count == 5
    assert reference.source_count == 5
    assert [support.lead.en for support in reference.supports] == [
        "Support lead 1",
        "Support lead 2",
        "Support lead 3",
    ]


def test_saved_article_reference_atlas_omits_empty_inputs() -> None:
    assert build_row_one_saved_article_reference_atlas(None, None) is None
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
    assert build_row_one_saved_article_reference_atlas(empty_library, None) is None
    empty_organization = RowOneSavedArticleContentOrganization(groups=[])
    assert build_row_one_saved_article_reference_atlas(empty_library, empty_organization) is None
