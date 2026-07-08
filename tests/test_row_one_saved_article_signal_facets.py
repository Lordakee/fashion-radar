from __future__ import annotations

from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT,
    SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT,
    build_row_one_saved_article_signal_facets,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _entry(
    index: int = 0,
    *,
    detail_path: str = "details/the-row-signal-1234567890.html",
) -> RowOneSavedArticleLibraryEntry:
    return RowOneSavedArticleLibraryEntry(
        title=_lt(f"The Row signal {index}"),
        source_name="Vogue Business",
        section_title=_lt("Top Stories", "今日重点"),
        saved_paragraph_count=3,
        organized_section_count=2,
        body_source="extracted",
        digest_path=f"{detail_path}#local-article-digest",
        reader_path=f"{detail_path}#local-article-reader",
        evidence_path=f"{detail_path}#local-article-paragraph-evidence",
        paragraph_links=(),
        references=(),
    )


def _library(*entries: RowOneSavedArticleLibraryEntry) -> RowOneSavedArticleLibrary:
    rows = list(entries) or [_entry()]
    return RowOneSavedArticleLibrary(
        article_count=len(rows),
        source_count=1,
        saved_paragraph_count=sum(entry.saved_paragraph_count for entry in rows),
        organized_section_count=sum(entry.organized_section_count for entry in rows),
        extracted_article_count=len(rows),
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=len(rows),
                saved_paragraph_count=sum(entry.saved_paragraph_count for entry in rows),
                organized_section_count=sum(entry.organized_section_count for entry in rows),
                entries=rows,
            )
        ],
    )


def _card(
    group_name: str,
    fragment: int,
    *,
    references: tuple[RowOneReference, ...],
    detail_path: str = "details/the-row-signal-1234567890.html",
) -> RowOneSavedArticleContentOrganizationCard:
    return RowOneSavedArticleContentOrganizationCard(
        title=_lt(f"{group_name} card"),
        source_name="Vogue Business",
        section_title=_lt("Top Stories", "今日重点"),
        section_label=_lt(group_name),
        lead=_lt(f"{group_name} lead"),
        detail_path=f"{detail_path}#local-article-content-section-{fragment}",
        paragraph_indices=(0,),
        references=references,
    )


def _organization() -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=_lt("People & Brands", "人物与品牌"),
                dek=_lt("Brand cards"),
                cards=[
                    _card(
                        "People & Brands",
                        1,
                        references=(
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="the row", type="brand", label="tracked"),
                        ),
                    )
                ],
            ),
            RowOneSavedArticleContentOrganizationGroup(
                key="product_signals",
                title=_lt("Products", "产品"),
                dek=_lt("Product cards"),
                cards=[
                    _card(
                        "Products",
                        2,
                        references=(
                            RowOneReference(name="Alaia flats", type="shoe", label="product"),
                            RowOneReference(name="Margaux Bag", type="bag", label="product"),
                        ),
                    ),
                    _card(
                        "Unsafe",
                        3,
                        references=(
                            RowOneReference(name="Unsafe Product", type="bag", label="product"),
                        ),
                        detail_path="../secret.html",
                    ),
                ],
            ),
        ],
    )


def _unsafe_only_organization() -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=_lt("People & Brands", "人物与品牌"),
                dek=_lt("Unsafe only"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_lt("Unsafe only"),
                        source_name="Vogue Business",
                        section_title=_lt("Top Stories", "今日重点"),
                        section_label=_lt("Unsafe"),
                        lead=_lt("Unsafe lead"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                        references=(
                            RowOneReference(
                                name="Unsafe Only Facet",
                                type="brand",
                                label="tracked",
                            ),
                        ),
                    )
                ],
            )
        ],
    )


def _large_library() -> RowOneSavedArticleLibrary:
    entries = [
        _entry(index, detail_path=f"details/the-row-signal-{index:010d}.html") for index in range(8)
    ]
    return _library(*entries)


def _large_organization() -> RowOneSavedArticleContentOrganization:
    groups: list[RowOneSavedArticleContentOrganizationGroup] = []
    for index in range(8):
        detail_path = f"details/the-row-signal-{index:010d}.html"
        cards = [
            _card(
                "Products",
                fragment + 1,
                references=(
                    RowOneReference(
                        name=f"Product {index}-{fragment}",
                        type="shoe",
                        label="product",
                    ),
                ),
                detail_path=detail_path,
            )
            for fragment in range(6)
        ]
        groups.append(
            RowOneSavedArticleContentOrganizationGroup(
                key=f"products-{index}",
                title=_lt("Products", "产品"),
                dek=_lt("Product cards"),
                cards=cards,
            )
        )
    return RowOneSavedArticleContentOrganization(groups=groups)


def test_saved_article_signal_facets_reuse_reference_atlas_buckets() -> None:
    assert (
        row_one_saved_article_reference_bucket(
            RowOneReference(name="The Row", type="brand", label="brand")
        )
        == "brands"
    )
    assert (
        row_one_saved_article_reference_bucket(
            RowOneReference(name="Alaia flats", type="product", label="product")
        )
        == "products"
    )


def test_build_saved_article_signal_facets_filters_unsafe_links_and_counts_safe_cards() -> None:
    facets = build_row_one_saved_article_signal_facets(_library(), _organization())

    assert facets is not None
    assert facets.row_count == 1
    assert facets.brand_count == 1
    assert facets.product_count == 2
    assert facets.theme_count == 1
    row = facets.rows[0]
    assert row.detail_path == "details/the-row-signal-1234567890.html"
    assert row.href == "details/the-row-signal-1234567890.html#local-article-digest"
    assert row.safe_card_count == 2
    assert [chip.label.en for chip in row.brands] == ["The Row"]
    assert [chip.label.en for chip in row.products] == ["Alaia flats", "Margaux Bag"]
    assert [chip.label.en for chip in row.themes] == ["Products"]


def test_build_saved_article_signal_facets_requires_matching_digest_detail_path() -> None:
    entry = _entry(
        detail_path="details/the-row-signal-1234567890.html",
    )
    mismatched_entry = RowOneSavedArticleLibraryEntry(
        title=entry.title,
        source_name=entry.source_name,
        section_title=entry.section_title,
        saved_paragraph_count=entry.saved_paragraph_count,
        organized_section_count=entry.organized_section_count,
        body_source=entry.body_source,
        digest_path="details/other-signal-1234567890.html#local-article-digest",
        reader_path=entry.reader_path,
        evidence_path=entry.evidence_path,
        paragraph_links=entry.paragraph_links,
        references=entry.references,
    )

    facets = build_row_one_saved_article_signal_facets(
        _library(mismatched_entry),
        _organization(),
    )

    assert facets is None


def test_build_saved_article_signal_facets_excludes_people_and_source_context_chips() -> None:
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=_lt("People & Brands", "人物与品牌"),
                dek=_lt("Mixed cards"),
                cards=[
                    _card(
                        "People & Brands",
                        1,
                        references=(
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="Miuccia Prada", type="designer", label="people"),
                            RowOneReference(
                                name="Vogue Business",
                                type="publication",
                                label="source context",
                            ),
                        ),
                    )
                ],
            )
        ]
    )

    facets = build_row_one_saved_article_signal_facets(_library(), organization)

    assert facets is not None
    row = facets.rows[0]
    assert [chip.label.en for chip in row.brands] == ["The Row"]
    assert row.products == ()
    assert row.themes == ()
    assert "Miuccia Prada" not in {chip.label.en for chip in row.brands}
    assert "Vogue Business" not in {chip.label.en for chip in row.brands}


def test_build_saved_article_signal_facets_omits_empty_and_unsafe_only_rows() -> None:
    facets = build_row_one_saved_article_signal_facets(
        _library(),
        _unsafe_only_organization(),
    )

    assert facets is None


def test_build_saved_article_signal_facets_caps_rows_and_chips_but_not_safe_card_count() -> None:
    facets = build_row_one_saved_article_signal_facets(
        _large_library(),
        _large_organization(),
    )

    assert facets is not None
    assert len(facets.rows) == SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT
    assert all(len(row.products) <= SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT for row in facets.rows)
    assert facets.rows[0].safe_card_count == 6
    assert facets.rows[0].safe_card_count > SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT
