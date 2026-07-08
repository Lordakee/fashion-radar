from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_key_signals_digest import (
    DAILY_LOCAL_KEY_SIGNALS_DIGEST_REFERENCE_LIMIT,
    DAILY_LOCAL_KEY_SIGNALS_DIGEST_THEME_LIMIT,
    DAILY_LOCAL_KEY_SIGNALS_DIGEST_WHY_LIMIT,
    build_row_one_daily_local_key_signals_digest,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 8, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _story(story_id: str, headline: str) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline,
        summary=_lt(f"{headline} summary"),
        why_it_matters=_lt(f"{headline} story why", f"{headline} story why zh"),
        editorial_takeaway=_lt("Takeaway"),
        signal_context=_lt("Signal context"),
        reader_path=_lt("Reader path"),
        source_name="Vogue Business",
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=["brand"],
        evidence=[],
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=_lt("Daily summary", "每日摘要"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=_lt("Top Stories", "今日重点"),
                dek=_lt("The lead signals", "重点信号"),
            )
        ],
        stories=list(stories),
    )


def _reference(
    name: str,
    *,
    ref_type: str = "brand",
    label: str = "brand",
) -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _item(
    label: str,
    *,
    body: str | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=_lt(body or f"{label} support", f"{label} support zh"),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "entities",
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        body=_lt(f"{title} body", f"{title} body zh"),
        items=items or [],
    )


def _article(
    story_id: str,
    *,
    title: str | None,
    why: str = "Local why",
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url="https://example.com/source",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs
        or [
            f"{title} first paragraph.",
            f"{title} second paragraph.",
            f"{title} third paragraph.",
        ],
        paragraphs_zh=[
            f"{title} 第一段。",
            f"{title} 第二段。",
            f"{title} 第三段。",
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="why_it_matters",
                title=_lt("Why It Matters", "为什么重要"),
                body=_lt(why, f"{why} zh"),
            )
        ],
        content_sections=content_sections or [],
    )


def test_build_daily_local_key_signals_digest_preserves_story_order_and_safe_links() -> None:
    first = _story("the-row-signal-1234567890", "The Row signal")
    second = _story("alaia-signal-1234567890", "Alaia signal")

    digest = build_row_one_daily_local_key_signals_digest(
        _edition(first, second),
        {
            first.id: _article(
                first.id,
                title="The Row saved article",
                why="The Row explains the market signal.",
                content_sections=[
                    _section(
                        "Brand Signals",
                        key="brand_signals",
                        items=[
                            _item(
                                "The Row",
                                body="The Row anchors the daily brand read.",
                                references=[
                                    _reference("The Row", ref_type="brand", label="brand"),
                                    _reference("Margaux", ref_type="accessory", label="product"),
                                ],
                                paragraph_indices=[0],
                            )
                        ],
                    )
                ],
            ),
            second.id: _article(
                second.id,
                title="Alaia saved article",
                why="Alaia gives the day a product angle.",
                source_name="Business of Fashion",
                content_sections=[
                    _section(
                        "People & Products",
                        key="entities",
                        items=[
                            _item(
                                "Alaia flats",
                                body="Alaia flats give the product signal shape.",
                                references=[
                                    _reference("Alaia", ref_type="brand", label="brand"),
                                    _reference(
                                        "Mary-Kate Olsen",
                                        ref_type="person",
                                        label="designer",
                                    ),
                                ],
                                paragraph_indices=[1],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert digest is not None
    assert digest.title.en == "Daily Local Key Signals Digest"
    assert digest.article_count == 2
    by_key = {group.key: group for group in digest.groups}
    assert [entry.title.en for entry in by_key["why_it_matters"].entries] == [
        "The Row saved article",
        "Alaia saved article",
    ]
    assert [entry.body.en for entry in by_key["why_it_matters"].entries] == [
        "The Row explains the market signal.",
        "Alaia gives the day a product angle.",
    ]
    assert by_key["why_it_matters"].entries[0].href == (
        "articles/the-row-signal-1234567890.html#saved-article-key-signals-title"
    )
    assert [entry.title.en for entry in by_key["brands"].entries] == ["The Row", "Alaia"]
    assert by_key["brands"].entries[0].body is not None
    assert by_key["brands"].entries[0].body.en == "The Row anchors the daily brand read."
    assert by_key["brands"].entries[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-paragraph-1"
    )
    assert [entry.title.en for entry in by_key["products"].entries] == ["Margaux"]
    assert [entry.title.en for entry in by_key["people"].entries] == ["Mary-Kate Olsen"]
    assert [entry.title.en for entry in by_key["themes"].entries] == [
        "Brand Signals",
        "People & Products",
        "Alaia flats",
    ]
    assert by_key["themes"].entries[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-1"
    )


def test_build_daily_local_key_signals_digest_dedupes_counts_and_caps_visible_entries() -> None:
    stories = [_story(f"brand-signal-{index:010d}", f"Brand signal {index}") for index in range(10)]
    local_articles = {
        story.id: _article(
            story.id,
            title=f"Article {index}",
            why=f"Why {index}",
            content_sections=[
                _section(
                    f"Theme {index}",
                    key="brand_signals",
                    items=[
                        _item(
                            f"Theme item {index}",
                            body=f"Support statement {index}",
                            references=[
                                _reference("The Row", ref_type="brand", label="brand"),
                                _reference(
                                    f"Brand {index}",
                                    ref_type="brand",
                                    label="brand",
                                ),
                            ],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ],
        )
        for index, story in enumerate(stories)
    }

    digest = build_row_one_daily_local_key_signals_digest(
        _edition(*stories),
        local_articles,
    )

    assert digest is not None
    by_key = {group.key: group for group in digest.groups}
    assert by_key["why_it_matters"].total_count == len(stories)
    assert len(by_key["why_it_matters"].entries) == DAILY_LOCAL_KEY_SIGNALS_DIGEST_WHY_LIMIT
    assert by_key["brands"].total_count == len(stories) + 10
    assert by_key["brands"].entries[0].title.en == "The Row"
    assert by_key["brands"].entries[0].support_count == len(stories)
    assert len(by_key["brands"].entries) == DAILY_LOCAL_KEY_SIGNALS_DIGEST_REFERENCE_LIMIT
    assert by_key["themes"].total_count == 20
    assert len(by_key["themes"].entries) == DAILY_LOCAL_KEY_SIGNALS_DIGEST_THEME_LIMIT


def test_build_daily_local_key_signals_digest_falls_back_to_story_headline() -> None:
    story = _story("the-row-signal-1234567890", "The Row fallback headline")

    digest = build_row_one_daily_local_key_signals_digest(
        _edition(story),
        {
            story.id: _article(
                story.id,
                title=None,
                why="Fallback why",
                paragraphs=["Fallback saved paragraph."],
                content_sections=[],
            )
        },
    )

    assert digest is not None
    by_key = {group.key: group for group in digest.groups}
    assert by_key["why_it_matters"].entries[0].title.en == "The Row fallback headline"


def test_build_daily_local_key_signals_digest_skips_invalid_inputs_and_returns_none() -> None:
    safe_story = _story("the-row-signal-1234567890", "The Row signal")
    unsafe_story = _story("unsafe/story", "Unsafe signal")
    mismatch_story = _story("mismatch-signal-1234567890", "Mismatch signal")

    digest = build_row_one_daily_local_key_signals_digest(
        _edition(unsafe_story, mismatch_story, safe_story),
        {
            unsafe_story.id: _article(
                unsafe_story.id,
                title="Unsafe article",
                content_sections=[
                    _section(
                        "Unsafe",
                        items=[_item("Unsafe", references=[_reference("Unsafe")])],
                    )
                ],
            ),
            mismatch_story.id: _article(
                "other-signal-1234567890",
                title="Mismatch article",
                content_sections=[
                    _section(
                        "Mismatch",
                        items=[_item("Mismatch", references=[_reference("Mismatch")])],
                    )
                ],
            ),
            safe_story.id: _article(
                safe_story.id,
                title="No signal article",
                paragraphs=[" ", ""],
                content_sections=[],
            ),
        },
    )

    assert digest is None
