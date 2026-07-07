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
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_evidence_board import (
    SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS,
    build_row_one_saved_article_evidence_board,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
)

AS_OF = datetime(2026, 7, 8, 4, 0, tzinfo=UTC)


def _localized(value: str) -> LocalizedText:
    return LocalizedText(zh=value, en=value)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline="The Row signal",
        summary=_localized("Summary"),
        why_it_matters=_localized("Why"),
        editorial_takeaway=_localized("Takeaway"),
        signal_context=_localized("Signal"),
        reader_path=_localized("Reader"),
        source_name="Vogue Business",
        source_url="https://example.com/the-row",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=["brand"],
        evidence=[],
    )


def _edition(story: RowOneStory | None = None) -> RowOneEdition:
    active_story = story or _story()
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=_localized("Daily summary"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=_localized("Top Stories"),
                dek=_localized("Top reads"),
            )
        ],
        stories=[active_story],
    )


def _article(story_id: str = "the-row-signal-1234567890") -> RowOneLocalArticle:
    long_paragraph = "Long paragraph " + ("detail " * 80) + "unpublished ending marker"
    return RowOneLocalArticle(
        story_id=story_id,
        title="The Row saved article",
        source_name="Vogue Business",
        url="https://example.com/the-row",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            "The Row paragraph one anchors the saved local evidence board.",
            "Alaia flats paragraph two carries a product reference.",
            "Dover Street Market paragraph three is source context.",
            long_paragraph,
        ],
        brief_sections=[],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=_localized("Read First"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=_localized("Desk note"),
                        body=_localized("The Row board lead"),
                        paragraph_indices=[0, True, 0, 99],
                        references=[RowOneReference(name="The Row", type="brand", label="tracked")],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=_localized("Products"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=_localized("Product note"),
                        body=_localized("Alaia board lead"),
                        paragraph_indices=[1],
                        references=[
                            RowOneReference(
                                name="Alaia flats",
                                type="shoe",
                                label="product",
                            )
                        ],
                    ),
                    RowOneLocalArticleContentItem(
                        label=_localized("Long note"),
                        body=_localized("Long board lead"),
                        paragraph_indices=[3],
                        references=[
                            RowOneReference(name="The Row bag", type="bag", label="product")
                        ],
                    ),
                ],
            ),
        ],
        body_source="extracted",
    )


def _library(
    detail_path: str,
    *,
    reader_path: str | None = None,
    digest_path: str | None = None,
    evidence_path: str | None = None,
) -> RowOneSavedArticleLibrary:
    entry = RowOneSavedArticleLibraryEntry(
        title=_localized("The Row saved article"),
        source_name="Vogue Business",
        section_title=_localized("Top Stories"),
        saved_paragraph_count=4,
        organized_section_count=2,
        body_source="extracted",
        digest_path=digest_path or f"{detail_path}#local-article-digest",
        reader_path=reader_path or f"{detail_path}#local-article-reader",
        evidence_path=evidence_path or f"{detail_path}#local-article-paragraph-evidence",
        paragraph_links=(),
        references=(),
    )
    return RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=4,
        organized_section_count=2,
        extracted_article_count=1,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=4,
                organized_section_count=2,
                entries=[entry],
            )
        ],
    )


def _organization(detail_path: str) -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=_localized("Read First"),
                dek=_localized("Start here"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_localized("The Row saved article"),
                        source_name="Vogue Business",
                        section_title=_localized("Top Stories"),
                        section_label=_localized("Read First"),
                        lead=_localized("The Row board lead"),
                        detail_path=f"{detail_path}#local-article-content-section-1",
                        paragraph_indices=(0, True, 0, 99),
                        references=(
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ),
                    )
                ],
            ),
            RowOneSavedArticleContentOrganizationGroup(
                key="product_signals",
                title=_localized("Products"),
                dek=_localized("Product evidence"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_localized("The Row saved article"),
                        source_name="Vogue Business",
                        section_title=_localized("Top Stories"),
                        section_label=_localized("Products"),
                        lead=_localized("Alaia board lead"),
                        detail_path=f"{detail_path}#local-article-content-section-2",
                        paragraph_indices=(1, 3),
                        references=(
                            RowOneReference(
                                name="Fallback",
                                type="source",
                                label="fallback",
                            ),
                        ),
                    )
                ],
            ),
        ]
    )


def _organization_for_section(
    detail_path: str,
    group_key: str,
    section_number: int,
    paragraph_indices: list[int],
) -> RowOneSavedArticleContentOrganization:
    group_title = "Read First" if group_key == "takeaways" else "Products"
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key=group_key,
                title=_localized(group_title),
                dek=_localized("Evidence"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_localized("The Row saved article"),
                        source_name="Vogue Business",
                        section_title=_localized("Top Stories"),
                        section_label=_localized(group_title),
                        lead=_localized("Evidence lead"),
                        detail_path=(
                            f"{detail_path}#local-article-content-section-{section_number}"
                        ),
                        paragraph_indices=tuple(paragraph_indices),
                        references=(
                            RowOneReference(
                                name="Fallback",
                                type="source",
                                label="fallback",
                            ),
                        ),
                    )
                ],
            )
        ]
    )


def _organization_with_many_duplicate_cards(
    detail_path: str,
) -> RowOneSavedArticleContentOrganization:
    cards: list[RowOneSavedArticleContentOrganizationCard] = []
    for indices in (
        (0, True, 0, 99),
        (1,),
        (1,),
        (3,),
        (2,),
    ):
        cards.append(
            RowOneSavedArticleContentOrganizationCard(
                title=_localized("The Row saved article"),
                source_name="Vogue Business",
                section_title=_localized("Top Stories"),
                section_label=_localized("Read First"),
                lead=_localized("Evidence lead"),
                detail_path=f"{detail_path}#local-article-content-section-1",
                paragraph_indices=indices,
                references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
            )
        )
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=_localized("Read First"),
                dek=_localized("Start here"),
                cards=cards,
            )
        ]
    )


def test_saved_article_evidence_board_builds_groups_from_referenced_paragraphs() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization(story.detail_path),
        {story.id: _article(story.id)},
    )

    assert board is not None
    assert board.group_count == 2
    assert board.card_count == 3
    assert board.source_count == 1
    assert [group.key for group in board.groups] == ["takeaways", "product_signals"]
    assert board.groups[0].cards[0].paragraph_number == 1
    assert board.groups[0].cards[0].href == (
        "details/the-row-signal-1234567890.html#local-article-paragraph-1"
    )
    assert board.groups[0].cards[0].excerpt.en == (
        "The Row paragraph one anchors the saved local evidence board."
    )
    assert [ref.name for ref in board.groups[0].cards[0].references] == ["The Row"]


def test_saved_article_evidence_board_omits_empty_inputs() -> None:
    story = _story()
    article = _article(story.id)
    assert (
        build_row_one_saved_article_evidence_board(
            None,
            _library(story.detail_path),
            _organization(story.detail_path),
            {story.id: article},
        )
        is None
    )
    assert (
        build_row_one_saved_article_evidence_board(
            _edition(story),
            None,
            _organization(story.detail_path),
            {story.id: article},
        )
        is None
    )
    assert (
        build_row_one_saved_article_evidence_board(
            _edition(story),
            _library(story.detail_path),
            None,
            {story.id: article},
        )
        is None
    )
    assert (
        build_row_one_saved_article_evidence_board(
            _edition(story),
            _library(story.detail_path),
            _organization(story.detail_path),
            {},
        )
        is None
    )


def test_saved_article_evidence_board_rejects_unsafe_and_unmatched_routes() -> None:
    story = _story()
    unsafe = _organization("javascript:alert(1)#local-article-content-section-1")
    traversal = _organization(
        "details/../the-row-signal-1234567890.html#local-article-content-section-1"
    )
    wrong_fragment = _organization(f"{story.detail_path}#local-article-content-section-01")
    unmatched = _organization(
        "details/other-signal-1234567890.html#local-article-content-section-1"
    )
    for organization in (unsafe, traversal, wrong_fragment, unmatched):
        assert (
            build_row_one_saved_article_evidence_board(
                _edition(story),
                _library(story.detail_path),
                organization,
                {story.id: _article(story.id)},
            )
            is None
        )


def test_saved_article_evidence_board_requires_consistent_library_routes() -> None:
    story = _story()
    corrupted = _library(
        story.detail_path,
        reader_path="details/other-signal-1234567890.html#local-article-reader",
    )
    assert (
        build_row_one_saved_article_evidence_board(
            _edition(story),
            corrupted,
            _organization(story.detail_path),
            {story.id: _article(story.id)},
        )
        is None
    )


def test_saved_article_evidence_board_dedupes_rejects_bool_indices_and_caps_cards() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_with_many_duplicate_cards(story.detail_path),
        {story.id: _article(story.id)},
    )

    assert board is not None
    assert len(board.groups[0].cards) == 3
    assert [card.paragraph_number for card in board.groups[0].cards] == [1, 2, 4]


def test_saved_article_evidence_board_caps_long_excerpts_without_full_republication() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_for_section(story.detail_path, "product_signals", 2, [3]),
        {story.id: _article(story.id)},
    )

    assert board is not None
    excerpt = board.groups[0].cards[0].excerpt.en
    assert len(excerpt) <= SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS + 3
    assert excerpt.endswith("...")
    assert "unpublished ending marker" not in excerpt
    assert _article(story.id).paragraphs[3] not in excerpt


def test_saved_article_evidence_board_leaves_short_article_paragraph_unpublished() -> None:
    story = _story()
    article = _article(story.id).model_copy(
        deep=True,
        update={
            "paragraphs": [
                "Short paragraph one.",
                "Short paragraph two.",
                "Short paragraph three.",
            ],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="takeaways",
                    title=_localized("Read First"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=_localized("Desk note"),
                            body=_localized("Short article lead"),
                            paragraph_indices=[0, 1, 2],
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
        },
    )
    organization = _organization_for_section(story.detail_path, "takeaways", 1, [0, 1, 2])

    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        organization,
        {story.id: article},
    )

    assert board is not None
    rendered_excerpts = [card.excerpt.en for group in board.groups for card in group.cards]
    assert rendered_excerpts == ["Short paragraph one.", "Short paragraph two."]
    assert "Short paragraph three." not in rendered_excerpts


def test_saved_article_evidence_board_uses_item_references_for_matching_paragraph() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_for_section(story.detail_path, "product_signals", 2, [1]),
        {story.id: _article(story.id)},
    )

    assert board is not None
    assert [ref.name for ref in board.groups[0].cards[0].references] == ["Alaia flats"]


def test_saved_article_evidence_board_uses_fallback_references_without_item_match() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_for_section(story.detail_path, "product_signals", 2, [2]),
        {story.id: _article(story.id)},
    )

    assert board is not None
    assert [ref.name for ref in board.groups[0].cards[0].references] == ["Fallback"]
