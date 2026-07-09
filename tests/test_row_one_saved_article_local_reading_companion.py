from __future__ import annotations

from dataclasses import replace

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)
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
from fashion_radar.row_one.saved_article_local_reading_companion import (
    SAVED_ARTICLE_LOCAL_READING_COMPANION_RELATED_LIMIT,
    RowOneSavedArticleLocalReadingCompanionTrailLink,
    build_row_one_saved_article_local_reading_companion,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=f"Headline {story_id}",
        summary=_lt("Summary"),
        why_it_matters=_lt("Why it matters"),
        editorial_takeaway=_lt("Takeaway"),
        signal_context=_lt("Signal context"),
        reader_path=_lt("Reader path"),
        source_name="Vogue Business",
        source_url="https://example.com/source",
        detail_path=f"details/{story_id}.html",
        tags=["brand"],
        evidence=[],
    )


def _local_article(story_id: str = "the-row-signal-1234567890") -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        url="https://example.com/source",
        source_name="Vogue Business",
        title=f"Local article {story_id}",
        body_source="extracted",
        extracted_at="2026-07-02T04:00:00+00:00",
        paragraphs=["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=["第一段。", "第二段。"],
        brief_sections=[],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=_lt("People & Brands", "品牌与人物"),
                body=_lt("The Row and Alaia context.", "The Row 与 Alaia 上下文。"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=_lt("The Row"),
                        body=_lt("The Row signal."),
                        references=[RowOneReference(name="The Row", type="brand", label="tracked")],
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )


def _entry(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    body_source: str = "extracted",
) -> RowOneSavedArticleLibraryEntry:
    detail_path = f"details/{story_id}.html"
    return RowOneSavedArticleLibraryEntry(
        title=_lt(title or f"Article {story_id}"),
        source_name=source_name,
        section_title=_lt("Top Stories", "今日重点"),
        saved_paragraph_count=2,
        organized_section_count=1,
        body_source=body_source,
        digest_path=f"{detail_path}#local-article-digest",
        reader_path=f"{detail_path}#local-article-reader",
        evidence_path=f"{detail_path}#local-article-paragraph-evidence",
        paragraph_links=(),
        references=(),
    )


def _library(*entries: RowOneSavedArticleLibraryEntry) -> RowOneSavedArticleLibrary:
    rows = list(entries)
    return RowOneSavedArticleLibrary(
        article_count=len(rows),
        source_count=len({entry.source_name.casefold() for entry in rows}),
        saved_paragraph_count=sum(entry.saved_paragraph_count for entry in rows),
        organized_section_count=sum(entry.organized_section_count for entry in rows),
        extracted_article_count=sum(1 for entry in rows if entry.body_source == "extracted"),
        summary_fallback_article_count=sum(
            1 for entry in rows if entry.body_source == "summary_fallback"
        ),
        skipped_article_count=sum(1 for entry in rows if entry.body_source == "skipped"),
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
    story_id: str,
    *,
    title: str | None = None,
    section_number: int = 1,
    source_name: str = "Vogue Business",
) -> RowOneSavedArticleContentOrganizationCard:
    return RowOneSavedArticleContentOrganizationCard(
        title=_lt(title or f"Card {story_id}"),
        source_name=source_name,
        section_title=_lt("Top Stories", "今日重点"),
        section_label=_lt("People & Brands", "品牌与人物"),
        lead=_lt(f"Lead for {story_id}", f"{story_id} 导语"),
        detail_path=f"details/{story_id}.html#local-article-content-section-{section_number}",
        paragraph_indices=(0, 1),
        references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
    )


def _organization(
    *cards: RowOneSavedArticleContentOrganizationCard,
) -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=_lt("People & Brands", "品牌与人物"),
                dek=_lt("Brand context", "品牌上下文"),
                cards=list(cards),
            )
        ]
    )


def test_build_local_reading_companion_matches_current_article_and_related_local_links() -> None:
    current_id = "the-row-signal-1234567890"
    peer_id = "alaia-signal-1234567890"

    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id, title="The Row signal"), _entry(peer_id)),
        organization=_organization(_card(current_id, title="The Row card"), _card(peer_id)),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html",
            f"details/{peer_id}.html": f"{peer_id}.html",
        },
    )

    assert companion is not None
    assert companion.current_title.en == "The Row signal"
    assert companion.source_name == "Vogue Business"
    assert companion.group_title.en == "People & Brands"
    assert companion.body_source_label.en == "Extracted article text"
    assert companion.local_links[0].href == "#local-article-digest"
    assert companion.local_links[1].href == "#local-article-reader"
    assert companion.related_items[0].title.en == f"Article {peer_id}"
    assert companion.related_items[0].href == f"{peer_id}.html#local-article-digest"
    assert all(current_id not in item.href for item in companion.related_items)


def test_build_local_reading_companion_adds_cross_surface_organization_trail_links() -> None:
    current_id = "the-row-signal-1234567890"
    peer_id = "alaia-signal-1234567890"

    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id, title="The Row signal"), _entry(peer_id)),
        organization=_organization(_card(current_id, title="The Row card"), _card(peer_id)),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html",
            f"details/{peer_id}.html": f"{peer_id}.html",
        },
    )

    assert companion is not None
    assert [(link.label.en, link.href) for link in companion.filing_links] == [
        ("Library organization group", "index.html#saved-article-organization-group-entities"),
        ("Saved article library card", f"index.html#saved-article-library-card-{current_id}"),
    ]
    assert [link.label.zh for link in companion.filing_links] == [
        "文章库整理分组",
        "文章库卡片",
    ]


def test_build_local_reading_companion_omits_unsafe_organization_group_trail_link() -> None:
    current_id = "the-row-signal-1234567890"
    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id)),
        organization=RowOneSavedArticleContentOrganization(
            groups=[
                RowOneSavedArticleContentOrganizationGroup(
                    key="../bad",
                    title=_lt("Bad", "坏"),
                    dek=_lt("Bad", "坏"),
                    cards=[_card(current_id)],
                )
            ]
        ),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html"
        },
    )

    assert companion is not None
    assert [link.href for link in companion.filing_links] == [
        f"index.html#saved-article-library-card-{current_id}"
    ]


def test_build_local_reading_companion_filters_cross_surface_group_key_boundaries() -> None:
    current_id = "the-row-signal-1234567890"
    accepted = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id)),
        organization=RowOneSavedArticleContentOrganization(
            groups=[
                RowOneSavedArticleContentOrganizationGroup(
                    key="top_stories",
                    title=_lt("Top Stories", "今日重点"),
                    dek=_lt("Top context", "重点上下文"),
                    cards=[_card(current_id)],
                )
            ]
        ),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html"
        },
    )

    assert accepted is not None
    assert accepted.filing_links[0].href == (
        "index.html#saved-article-organization-group-top_stories"
    )

    for unsafe_key in ("1bad", "-bad"):
        rejected = build_row_one_saved_article_local_reading_companion(
            story=_story(current_id),
            local_article=_local_article(current_id),
            library=_library(_entry(current_id)),
            organization=RowOneSavedArticleContentOrganization(
                groups=[
                    RowOneSavedArticleContentOrganizationGroup(
                        key=unsafe_key,
                        title=_lt("Bad", "坏"),
                        dek=_lt("Bad", "坏"),
                        cards=[_card(current_id)],
                    )
                ]
            ),
            local_article_page_hrefs_by_detail_path={
                f"details/{current_id}.html": f"{current_id}.html"
            },
        )
        assert rejected is not None
        assert rejected.filing_links == (
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Saved article library card", zh="文章库卡片"),
                href=f"index.html#saved-article-library-card-{current_id}",
            ),
        )


def test_build_local_reading_companion_falls_back_to_safe_detail_content_anchor() -> None:
    current_id = "the-row-signal-1234567890"
    peer_id = "alaia-signal-1234567890"

    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id), _entry(peer_id)),
        organization=_organization(_card(current_id), _card(peer_id, section_number=2)),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html"
        },
    )

    assert companion is not None
    assert companion.related_items[0].href == (
        f"../details/{peer_id}.html#local-article-content-section-2"
    )


def test_build_local_reading_companion_filters_unsafe_inputs_and_caps_related_items() -> None:
    current_id = "the-row-signal-1234567890"
    peer_ids = [f"peer-signal-{index:010d}" for index in range(6)]
    entries = [_entry(current_id), *(_entry(peer_id) for peer_id in peer_ids)]
    cards = [
        _card(current_id),
        *(
            (
                _card(peer_id)
                if index != 3
                else replace(
                    _card(peer_id),
                    detail_path="../escape.html#local-article-content-section-1",
                )
            )
            for index, peer_id in enumerate(peer_ids)
        ),
    ]
    hrefs = {f"details/{peer_id}.html": f"{peer_id}.html" for peer_id in peer_ids}
    hrefs[f"details/{peer_ids[1]}.html"] = "bad href.html"
    hrefs[f"details/{peer_ids[2]}.html"] = "../escape.html"
    hrefs[f"details/{current_id}.html"] = f"{current_id}.html"

    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(*entries),
        organization=_organization(*cards),
        local_article_page_hrefs_by_detail_path=hrefs,
    )

    assert companion is not None
    assert len(companion.related_items) == SAVED_ARTICLE_LOCAL_READING_COMPANION_RELATED_LIMIT
    assert all("bad href" not in item.href for item in companion.related_items)
    assert all("../escape.html" not in item.href for item in companion.related_items)


def test_build_local_reading_companion_returns_none_without_safe_current_match() -> None:
    assert (
        build_row_one_saved_article_local_reading_companion(
            story=_story("missing-signal-1234567890"),
            local_article=_local_article("missing-signal-1234567890"),
            library=_library(_entry("the-row-signal-1234567890")),
            organization=_organization(_card("the-row-signal-1234567890")),
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )

    assert (
        build_row_one_saved_article_local_reading_companion(
            story=_story("the-row-signal-1234567890").model_copy(
                update={"detail_path": "../unsafe.html"}
            ),
            local_article=_local_article("the-row-signal-1234567890"),
            library=_library(_entry("the-row-signal-1234567890")),
            organization=_organization(_card("the-row-signal-1234567890")),
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )
