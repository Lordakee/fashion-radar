from __future__ import annotations

from dataclasses import replace
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
    RowOneSavedArticleLocalRelatedReadCard,
    RowOneSavedArticleLocalRelatedReadEvidenceBridge,
    RowOneSavedArticleLocalRelatedReadReference,
    build_row_one_saved_article_local_related_read_connection_brief,
    build_row_one_saved_article_local_related_read_lanes,
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


def test_saved_article_local_related_reads_adds_shared_reference_evidence_bridge() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared The Row signal")
    edition = _edition(current, shared)
    articles = {
        current.id: _article(
            current.id,
            paragraphs=["Current opening.", "Current The Row paragraph."],
            content_sections=[
                _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[1])
            ],
        ),
        shared.id: _article(
            shared.id,
            paragraphs=["Shared opening.", "Shared The Row paragraph."],
            content_sections=[
                _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[1])
            ],
        ),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=edition,
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert len(related.cards) == 1
    bridge = related.cards[0].evidence_bridges[0]
    assert bridge.reference.name == "The Row"
    assert bridge.current_label.en == "Here ¶2"
    assert bridge.current_label.zh == "本文 ¶2"
    assert bridge.current_href == "#local-article-paragraph-2"
    assert bridge.candidate_label.en == "Next read ¶2"
    assert bridge.candidate_label.zh == "下一篇 ¶2"
    assert bridge.candidate_href == "shared-row-2222222222.html#local-article-paragraph-2"


def test_saved_article_local_related_reads_omits_bridge_when_current_paragraph_invalid() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared The Row signal")

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                paragraphs=["Current opening."],
                content_sections=[
                    _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[9])
                ],
            ),
            shared.id: _article(
                shared.id,
                content_sections=[
                    _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[0])
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert related.cards[0].reason.en == "Shared signal: The Row"
    assert related.cards[0].evidence_bridges == ()


def test_saved_article_local_related_reads_omits_bridge_when_candidate_paragraph_invalid() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared The Row signal")

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
                paragraphs=["Shared opening."],
                content_sections=[
                    _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[9])
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert related.cards[0].reason.en == "Shared signal: The Row"
    assert related.cards[0].evidence_bridges == ()


def test_saved_article_local_related_reads_same_section_card_has_no_evidence_bridge() -> None:
    current = _story("current-row-0000000000")
    same_section = _story("same-section-3333333333", headline="Same section read")

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, same_section),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                content_sections=[
                    _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
                ],
            ),
            same_section.id: _article(
                same_section.id,
                content_sections=[
                    _content_section("Other refs", refs=[_ref("Alaia")], paragraph_indices=[0])
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, same_section),
    )

    assert related is not None
    assert related.cards[0].reason.en == "Same ROW ONE section"
    assert related.cards[0].evidence_bridges == ()


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


def test_saved_article_local_related_reads_caps_evidence_bridges() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared signal read")
    refs = [_ref("The Row"), _ref("Alaia"), _ref("Tabi"), _ref("Phoebe Philo")]

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                paragraphs=["Current A.", "Current B.", "Current C.", "Current D."],
                content_sections=[
                    _content_section(
                        "Current refs",
                        refs=refs,
                        paragraph_indices=[0, 1, 2, 3],
                    )
                ],
            ),
            shared.id: _article(
                shared.id,
                paragraphs=["Shared A.", "Shared B.", "Shared C.", "Shared D."],
                content_sections=[
                    _content_section(
                        "Shared refs",
                        refs=refs,
                        paragraph_indices=[0, 1, 2, 3],
                    )
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert len(related.cards[0].evidence_bridges) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS


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


def test_saved_article_local_related_reads_groups_cards_into_lanes() -> None:
    current = _story("current-row-0000000000", section_key="top_stories")
    shared = _story(
        "shared-row-1111111111",
        headline="Shared The Row signal",
        source_name="WWD",
    )
    same_section = _story(
        "same-section-2222222222",
        headline="Same section read",
        source_name="Harper's Bazaar",
    )
    same_source = _story(
        "same-source-3333333333",
        headline="Same source read",
        section_key="brand_moves",
    )
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
        same_section.id: _article(same_section.id, source_name=same_section.source_name),
        same_source.id: _article(same_source.id, source_name=same_source.source_name),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared, same_section, same_source),
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, shared, same_section, same_source),
    )

    assert related is not None
    lanes = build_row_one_saved_article_local_related_read_lanes(related.cards)

    assert [lane.key for lane in lanes] == [
        "shared_signal",
        "same_section",
        "same_source",
    ]
    assert [lane.cards[0].candidate_story_id for lane in lanes] == [
        shared.id,
        same_section.id,
        same_source.id,
    ]
    assert lanes[0].title.en == "Shared signals"
    assert lanes[0].dek.en == "Next reads carrying the same named fashion signal."
    assert lanes[1].title.en == "Same ROW ONE section"
    assert lanes[1].dek.en == "Next reads filed near this story in today's edition."
    assert lanes[2].title.en == "Same source desk"
    assert lanes[2].dek.en == "Next reads from the same saved local source context."


def test_saved_article_local_related_read_lanes_dedupe_and_omit_unknown_reasons() -> None:
    safe_card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="safe-row-1111111111",
        title=_text("Safe read"),
        source_name="WWD",
        reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
        excerpt=_text("Saved excerpt"),
        href="safe-row-1111111111.html#local-article-paragraph-1",
        references=(RowOneSavedArticleLocalRelatedReadReference(name="The Row", label="Brand"),),
    )
    duplicate_card = replace(safe_card)
    unknown_card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="unknown-row-2222222222",
        title=_text("Unknown read"),
        source_name="WWD",
        reason=LocalizedText(en="Editorial adjacency", zh="编辑相邻"),
        excerpt=_text("Unknown excerpt"),
        href="unknown-row-2222222222.html#local-article-paragraph-1",
    )

    lanes = build_row_one_saved_article_local_related_read_lanes(
        (safe_card, duplicate_card, unknown_card)
    )

    assert len(lanes) == 1
    assert lanes[0].key == "shared_signal"
    assert [card.candidate_story_id for card in lanes[0].cards] == ["safe-row-1111111111"]


def test_saved_article_local_related_read_connection_brief_summarizes_cards() -> None:
    card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="shared-row-1111111111",
        title=_text("Shared read"),
        source_name="WWD",
        reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
        excerpt=_text("Saved excerpt"),
        href="shared-row-1111111111.html#local-article-paragraph-1",
        references=(RowOneSavedArticleLocalRelatedReadReference(name="The Row", label="Brand"),),
        evidence_bridges=(
            RowOneSavedArticleLocalRelatedReadEvidenceBridge(
                reference=RowOneSavedArticleLocalRelatedReadReference(
                    name="The Row",
                    label="Brand",
                ),
                current_label=LocalizedText(en="Here ¶1", zh="本文 ¶1"),
                current_href="#local-article-paragraph-1",
                candidate_label=LocalizedText(en="Next read ¶1", zh="下一篇 ¶1"),
                candidate_href="shared-row-1111111111.html#local-article-paragraph-1",
            ),
        ),
    )
    same_source = replace(
        card,
        candidate_story_id="source-row-2222222222",
        source_name="Vogue Business",
        reason=LocalizedText(en="Same source desk", zh="同一来源"),
        href="source-row-2222222222.html#local-article-paragraph-1",
        evidence_bridges=(),
    )
    same_section = replace(
        card,
        candidate_story_id="section-row-3333333333",
        source_name="Harper's Bazaar",
        reason=LocalizedText(en="Same ROW ONE section", zh="同一 ROW ONE 栏目"),
        href="section-row-3333333333.html#local-article-paragraph-1",
        evidence_bridges=(),
    )

    brief = build_row_one_saved_article_local_related_read_connection_brief(
        (card, same_source, same_section)
    )

    assert brief is not None
    assert not hasattr(brief, "dek")
    assert brief.title.en == "Connection Brief"
    assert brief.title.zh == "关联阅读简报"
    assert brief.card_count == 3
    assert brief.source_count == len(brief.source_names) == 3
    assert brief.signal_count == len(brief.signal_references) == 1
    assert brief.evidence_bridge_count == 1
    assert [label.en for label in brief.lane_labels] == [
        "Shared signals",
        "Same ROW ONE section",
        "Same source desk",
    ]
    assert [label.zh for label in brief.lane_labels] == [
        "共同信号",
        "同一 ROW ONE 栏目",
        "同一来源台",
    ]
    assert [reference.name for reference in brief.signal_references] == ["The Row"]
    assert brief.source_names == ("WWD", "Vogue Business", "Harper's Bazaar")
    assert brief.lead.en == (
        "This path connects 3 local reads through shared signals, source context, "
        "and paragraph evidence already saved in ROW ONE."
    )
    assert brief.lead.zh == (
        "这条路径用 ROW ONE 已保存的共同信号、来源语境与段落证据串联 3 篇本地阅读。"
    )


def test_saved_article_local_related_read_connection_brief_returns_none_without_cards() -> None:
    assert build_row_one_saved_article_local_related_read_connection_brief(()) is None


def test_saved_article_local_related_read_connection_brief_dedupes_and_caps_values() -> None:
    references = (
        RowOneSavedArticleLocalRelatedReadReference(name=" The   Row ", label=" Brand "),
        RowOneSavedArticleLocalRelatedReadReference(name="the row", label="brand"),
        RowOneSavedArticleLocalRelatedReadReference(name=" Alaia ", label=" Brand "),
        RowOneSavedArticleLocalRelatedReadReference(name="Margaux", label="Brand"),
        RowOneSavedArticleLocalRelatedReadReference(name="Tabi", label="Product"),
    )
    source_names = (
        " WWD ",
        "wwd",
        " Vogue   Business ",
        "Business of Fashion",
    )
    cards = tuple(
        RowOneSavedArticleLocalRelatedReadCard(
            candidate_story_id=f"shared-row-{index:010d}",
            title=_text(f"Shared read {index}"),
            source_name=source_name,
            reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
            excerpt=_text("Saved excerpt"),
            href=f"shared-row-{index:010d}.html#local-article-paragraph-1",
            references=references,
        )
        for index, source_name in enumerate(source_names, start=1)
    )

    brief = build_row_one_saved_article_local_related_read_connection_brief(cards)

    assert brief is not None
    assert brief.signal_count == len(brief.signal_references)
    assert brief.signal_count == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
    assert [(reference.name, reference.label) for reference in brief.signal_references] == [
        ("The Row", "Brand"),
        ("Alaia", "Brand"),
        ("Margaux", "Brand"),
    ]
    assert brief.source_count == len(brief.source_names)
    assert brief.source_count == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
    assert brief.source_names == ("WWD", "Vogue Business", "Business of Fashion")


def test_saved_article_local_related_read_connection_brief_uses_context_lead_without_signals() -> (
    None
):
    card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="section-row-1111111111",
        title=_text("Section read"),
        source_name="WWD",
        reason=LocalizedText(en="Same ROW ONE section", zh="同一 ROW ONE 栏目"),
        excerpt=_text("Saved excerpt"),
        href="section-row-1111111111.html#local-article-paragraph-1",
    )

    brief = build_row_one_saved_article_local_related_read_connection_brief((card,))

    assert brief is not None
    assert brief.signal_references == ()
    assert brief.signal_count == 0
    assert brief.lead.en == (
        "This path connects 1 local read through section or source context already "
        "saved in ROW ONE."
    )
    assert brief.lead.zh == "这条路径用 ROW ONE 已保存的栏目或来源语境串联 1 篇本地阅读。"


def test_saved_article_local_related_read_lanes_returns_empty_for_empty_input() -> None:
    assert build_row_one_saved_article_local_related_read_lanes(()) == ()


def test_saved_article_local_related_read_lanes_preserve_order_and_cap_each_lane() -> None:
    first = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="source-row-1111111111",
        title=_text("Source read one"),
        source_name="WWD",
        reason=LocalizedText(en="", zh="同一来源"),
        excerpt=_text("Saved excerpt one"),
        href="source-row-1111111111.html#local-article-paragraph-1",
    )
    cards = (
        first,
        replace(
            first,
            candidate_story_id="source-row-2222222222",
            title=_text("Source read two"),
            href="source-row-2222222222.html#local-article-paragraph-1",
        ),
        replace(
            first,
            candidate_story_id="source-row-3333333333",
            title=_text("Source read three"),
            href="source-row-3333333333.html#local-article-paragraph-1",
        ),
        replace(
            first,
            candidate_story_id="source-row-4444444444",
            title=_text("Source read four"),
            href="source-row-4444444444.html#local-article-paragraph-1",
        ),
    )

    lanes = build_row_one_saved_article_local_related_read_lanes(cards)

    assert len(lanes) == 1
    assert lanes[0].key == "same_source"
    assert [card.candidate_story_id for card in lanes[0].cards] == [
        "source-row-1111111111",
        "source-row-2222222222",
        "source-row-3333333333",
    ]
