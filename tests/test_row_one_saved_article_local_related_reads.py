from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentKey,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_local_related_reads import (
    SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS,
    SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS,
    build_row_one_saved_article_local_related_reads,
)


def _text(value: str) -> LocalizedText:
    return LocalizedText(en=value, zh=value)


def _ref(name: str, *, label: str = "Brand") -> RowOneReference:
    return RowOneReference(name=name, type=label.lower(), label=label)


def _story(
    story_id: str,
    *,
    headline: str | None = None,
    section_key: RowOneSectionKey = "top_stories",
    source_name: str = "Vogue Business",
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        story_type="tracked_entity",
        headline=headline or f"Headline {story_id}",
        summary=_text(f"Summary {story_id}"),
        why_it_matters=_text(f"Why {story_id} matters"),
        editorial_takeaway=_text(f"Takeaway {story_id}"),
        signal_context=_text(f"Signal {story_id}"),
        reader_path=_text(f"Reader path {story_id}"),
        source_name=source_name,
        detail_path=f"details/{story_id}.html",
    )


def _content_section(
    title: str,
    *,
    key: RowOneLocalArticleContentKey = "entities",
    refs: list[RowOneReference],
    paragraph_indices: list[int],
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,
        title=_text(title),
        body=_text(f"{title} body"),
        items=[
            RowOneLocalArticleContentItem(
                label=_text(f"{title} item"),
                body=_text(f"{title} item body"),
                references=refs,
                paragraph_indices=paragraph_indices,
            )
        ],
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh or [],
        brief_sections=[],
        content_sections=content_sections or [],
        body_source="extracted",
        skipped=False,
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        edition_date=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        summary=_text("Daily fashion intelligence."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=_text("Top Stories"),
                dek=_text("Top stories."),
            ),
            RowOneSection(
                key="brand_moves",
                title=_text("Brand Moves"),
                dek=_text("Brand moves."),
            ),
            RowOneSection(
                key="hot_products",
                title=_text("Hot Products"),
                dek=_text("Hot products."),
            ),
        ],
        stories=list(stories),
    )


def _hrefs(*stories: RowOneStory) -> dict[str, str]:
    return {story.id: f"{story.id}.html" for story in stories}


def test_saved_article_local_related_reads_scores_shared_refs_section_source() -> None:
    current = _story("current-row-0000000000")
    shared = _story(
        "shared-row-2222222222",
        headline="Shared The Row signal",
        source_name="WWD",
    )
    same_section = _story(
        "same-section-3333333333",
        headline="Same section read",
        source_name="Harper's Bazaar",
    )
    same_source = _story(
        "same-source-4444444444",
        headline="Same source read",
        section_key="brand_moves",
    )
    edition = _edition(current, same_source, same_section, shared)
    articles = {
        current.id: _article(
            current.id,
            content_sections=[
                _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
            ],
        ),
        shared.id: _article(
            shared.id,
            source_name=shared.source_name,
            content_sections=[
                _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[1])
            ],
        ),
        same_section.id: _article(
            same_section.id,
            source_name=same_section.source_name,
            content_sections=[
                _content_section("Other refs", refs=[_ref("Alaia")], paragraph_indices=[0])
            ],
        ),
        same_source.id: _article(same_source.id, source_name=same_source.source_name),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=edition,
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, shared, same_section, same_source),
    )

    assert related is not None
    assert [card.title.en for card in related.cards] == [
        "Shared The Row signal",
        "Same section read",
        "Same source read",
    ]
    assert related.cards[0].candidate_story_id == shared.id
    assert related.cards[0].href == "shared-row-2222222222.html#local-article-paragraph-2"
    assert "articles/shared-row-2222222222.html" not in related.cards[0].href
    assert related.cards[0].reason.en == "Shared signal: The Row"
    assert [ref.name for ref in related.cards[0].references] == ["The Row"]
    assert related.card_count == len(related.cards)


def test_saved_article_local_related_reads_filters_unrelated_and_current_article() -> None:
    current = _story("current-row-0000000000")
    unrelated = _story(
        "unrelated-row-1111111111",
        section_key="brand_moves",
        source_name="WWD",
    )

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, unrelated),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                content_sections=[
                    _content_section(
                        "Current refs",
                        refs=[_ref("The Row")],
                        paragraph_indices=[0],
                    )
                ],
            ),
            unrelated.id: _article(
                unrelated.id,
                source_name=unrelated.source_name,
                content_sections=[
                    _content_section(
                        "Unrelated refs",
                        refs=[_ref("Alaia")],
                        paragraph_indices=[0],
                    )
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, unrelated),
    )

    assert related is None


def test_saved_article_local_related_reads_filters_excluded_companion_story_ids() -> None:
    current = _story("current-row-0000000000")
    excluded = _story("excluded-row-1111111111", headline="Already shown")
    fallback = _story("fallback-row-2222222222", headline="Post body option")
    articles = {
        current.id: _article(
            current.id,
            content_sections=[
                _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
            ],
        ),
        excluded.id: _article(
            excluded.id,
            content_sections=[
                _content_section("Excluded refs", refs=[_ref("The Row")], paragraph_indices=[0])
            ],
        ),
        fallback.id: _article(fallback.id),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, excluded, fallback),
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, excluded, fallback),
        excluded_story_ids=(excluded.id,),
    )

    assert related is not None
    assert [card.candidate_story_id for card in related.cards] == [fallback.id]


def test_saved_article_local_related_reads_prefers_shared_ref_paragraph_anchor() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-1111111111")
    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                content_sections=[
                    _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
                ],
            ),
            shared.id: _article(
                shared.id,
                paragraphs=["First paragraph.", "Second paragraph."],
                content_sections=[
                    _content_section(
                        "Shared refs",
                        refs=[_ref("The Row")],
                        paragraph_indices=[True, 9, 1],
                    )
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert related.cards[0].href == "shared-row-1111111111.html#local-article-paragraph-2"


def test_saved_article_local_related_reads_uses_aligned_paragraphs_zh_excerpt() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-1111111111")

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared),
        local_articles_by_story_id={
            current.id: _article(current.id),
            shared.id: _article(
                shared.id,
                paragraphs=["English saved paragraph."],
                paragraphs_zh=["中文保存段落。"],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert related.cards[0].excerpt.en == "English saved paragraph."
    assert related.cards[0].excerpt.zh == "中文保存段落。"


def test_saved_article_local_related_reads_rejects_unsafe_hrefs_and_bad_indices() -> None:
    current = _story("current-row-0000000000")
    safe = _story("safe-row-1111111111")
    unsafe_prefix = _story("unsafe-prefix-2222222222")
    articles = {
        current.id: _article(
            current.id,
            content_sections=[
                _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
            ],
        ),
        safe.id: _article(
            safe.id,
            paragraphs=["Fallback first paragraph.", "Shared second paragraph."],
            content_sections=[
                _content_section(
                    "Bad indices",
                    refs=[_ref("The Row")],
                    paragraph_indices=[False, -1, 20],
                )
            ],
        ),
        unsafe_prefix.id: _article(unsafe_prefix.id),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, safe, unsafe_prefix),
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id={
            current.id: f"{current.id}.html",
            safe.id: f"{safe.id}.html",
            unsafe_prefix.id: f"articles/{unsafe_prefix.id}.html",
        },
    )

    assert related is not None
    assert [card.candidate_story_id for card in related.cards] == [safe.id]
    assert related.cards[0].href == "safe-row-1111111111.html#local-article-paragraph-1"
    assert "#local-article-paragraph-0" not in related.cards[0].href


def test_saved_article_local_related_reads_rejects_mismatched_story_href() -> None:
    current = _story("current-row-0000000000")
    mismatched = _story("mismatch-row-1111111111")

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, mismatched),
        local_articles_by_story_id={
            current.id: _article(current.id),
            mismatched.id: _article(mismatched.id),
        },
        local_article_page_hrefs_by_story_id={
            current.id: f"{current.id}.html",
            mismatched.id: "other-row-2222222222.html",
        },
    )

    assert related is None


def test_saved_article_local_related_reads_caps_cards_and_reference_chips() -> None:
    current = _story("current-row-0000000000")
    current_refs = [_ref("The Row"), _ref("Alaia"), _ref("Margaux"), _ref("Ballet Flat")]
    stories = [
        _story("shared-one-1111111111", headline="Shared one"),
        _story("shared-two-2222222222", headline="Shared two"),
        _story("shared-three-3333333333", headline="Shared three"),
        _story("shared-four-4444444444", headline="Shared four"),
    ]
    articles = {
        current.id: _article(
            current.id,
            content_sections=[
                _content_section("Current refs", refs=current_refs, paragraph_indices=[0])
            ],
        )
    }
    for story in stories:
        articles[story.id] = _article(
            story.id,
            content_sections=[
                _content_section("Shared refs", refs=current_refs, paragraph_indices=[0])
            ],
        )

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, *stories),
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, *stories),
    )

    assert related is not None
    assert related.card_count == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS
    assert len(related.cards) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS
    assert len(related.cards[0].references) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
    assert [ref.name for ref in related.cards[0].references] == [
        "The Row",
        "Alaia",
        "Margaux",
    ]


def test_saved_article_local_related_reads_returns_none_without_related_cards() -> None:
    current = _story("current-row-0000000000")

    assert (
        build_row_one_saved_article_local_related_reads(
            current_story=current,
            edition=_edition(current),
            local_articles_by_story_id={current.id: _article(current.id)},
            local_article_page_hrefs_by_story_id=_hrefs(current),
        )
        is None
    )
