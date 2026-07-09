from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_saved_article_organizer import (
    DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS,
    DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE,
    DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD,
    build_row_one_daily_local_saved_article_organizer,
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

AS_OF = datetime(2026, 7, 9, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _ref(
    name: str,
    *,
    ref_type: str = "brand",
    label: str = "brand",
) -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _story(
    story_id: str,
    *,
    headline: str | None = None,
    source_name: str = "Vogue Business",
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline or f"Headline {story_id}",
        summary=_lt("Summary", "摘要"),
        why_it_matters=_lt("Why it matters", "为什么重要"),
        editorial_takeaway=_lt("Takeaway", "编辑判断"),
        signal_context=_lt("Signal context", "信号背景"),
        reader_path=_lt("Reader path", "阅读路径"),
        source_name=source_name,
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
        entity_refs=[],
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
                dek=_lt("Top saved reads", "重点保存阅读"),
            )
        ],
        stories=list(stories),
    )


def _brief(body: str) -> RowOneLocalArticleBriefSection:
    return RowOneLocalArticleBriefSection(
        key="why_it_matters",
        title=_lt("Why It Matters", "为什么重要"),
        body=_lt(body, f"{body} zh"),
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
        label=_lt(label, f"{label} zh"),
        body=(
            _lt(body, body_zh if body_zh is not None else f"{body} zh")
            if body is not None
            else None
        ),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "entities",
    body: str | None = None,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        body=_lt(body, f"{body} zh") if body is not None else None,
        items=items or [],
    )


def _article(
    story_id: str,
    *,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    brief_sections: list[RowOneLocalArticleBriefSection] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
    body_source: str = "extracted",
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"Local article {story_id}",
        url="https://example.com/source",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs
        if paragraphs is not None
        else [
            "The Row leads the saved local story with a sharper retail read.",
            "The Margaux bag turns the read into product evidence.",
            "Mary-Kate Olsen gives the coverage a people and brand frame.",
        ],
        paragraphs_zh=paragraphs_zh
        if paragraphs_zh is not None
        else [
            "The Row 以更清晰的零售解读开启本地保存故事。",
            "Margaux 包把阅读转化为单品证据。",
            "Mary-Kate Olsen 为报道提供人物与品牌框架。",
        ],
        brief_sections=brief_sections
        if brief_sections is not None
        else [_brief("Read this first because it frames the local article.")],
        content_sections=content_sections
        if content_sections is not None
        else [
            _section(
                "People & Brands",
                key="entities",
                items=[
                    _item(
                        "The Row",
                        body="The Row and Mary-Kate Olsen frame the brand signal.",
                        references=[
                            _ref("The Row", ref_type="brand", label="brand"),
                            _ref("Mary-Kate Olsen", ref_type="designer", label="person"),
                        ],
                        paragraph_indices=[0, 2],
                    )
                ],
            ),
            _section(
                "Products",
                key="product_signals",
                items=[
                    _item(
                        "Margaux bag",
                        body="Margaux and ballet flats convert the read into product proof.",
                        references=[
                            _ref("Margaux bag", ref_type="bag", label="product"),
                            _ref("Ballet flat", ref_type="shoe", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
        body_source=body_source,  # type: ignore[arg-type]
    )


def test_build_daily_local_saved_article_organizer_groups_saved_content() -> None:
    story = _story("the-row-signal-1234567890", headline="The Row signal")

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=[
                    "",
                    "The Row leads the saved local story with a sharper retail read.",
                    "The Margaux bag turns the read into product evidence.",
                ],
                paragraphs_zh=[
                    "",
                    "The Row 以更清晰的零售解读开启本地保存故事。",
                    "Margaux 包把阅读转化为单品证据。",
                ],
            )
        },
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    assert organizer.title.en == "Daily Local Saved Article Organizer"
    assert organizer.title.zh == "每日保存文章整理器"
    assert organizer.article_count == 1
    assert organizer.source_count == 1
    assert organizer.card_count == 4
    assert organizer.reference_count == 4
    by_key = {lane.key: lane for lane in organizer.lanes}
    assert [lane.key for lane in organizer.lanes] == [
        "read_first",
        "people_brands",
        "products",
        "source_context",
    ]
    assert by_key["read_first"].cards[0].excerpt.en == (
        "Read this first because it frames the local article."
    )
    assert by_key["read_first"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-paragraph-2"
    )
    assert by_key["people_brands"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-1"
    )
    assert by_key["products"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-2"
    )
    assert by_key["source_context"].cards[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-paragraph-2"
    )
    assert "Extracted article text" in by_key["source_context"].cards[0].excerpt.en
    assert by_key["source_context"].cards[0].excerpt.en != by_key["read_first"].cards[0].excerpt.en
    assert [ref.name for ref in by_key["products"].cards[0].references] == [
        "Margaux bag",
        "Ballet flat",
    ]


def test_build_daily_local_saved_article_organizer_filters_unsafe_inputs() -> None:
    valid = _story("valid-signal-1111111111")
    mismatched = _story("mismatched-signal-2222222222")
    unsafe = _story("unsafe/story")
    missing_href = _story("missing-href-3333333333")
    bad_href = _story("bad-href-4444444444")

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(valid, mismatched, unsafe, missing_href, bad_href),
        {
            valid.id: _article(valid.id),
            mismatched.id: _article("other-signal-5555555555"),
            unsafe.id: _article(unsafe.id),
            missing_href.id: _article(missing_href.id),
            bad_href.id: _article(bad_href.id),
        },
        {
            valid.id: f"{valid.id}.html",
            mismatched.id: f"{mismatched.id}.html",
            unsafe.id: "unsafe/story.html",
            bad_href.id: "../bad-href-4444444444.html",
        },
    )

    assert organizer is not None
    emitted = repr(organizer)
    assert "articles/valid-signal-1111111111.html" in emitted
    assert "../" not in emitted
    assert "unsafe/story" not in emitted
    assert "mismatched-signal-2222222222.html" not in emitted
    assert "missing-href-3333333333.html" not in emitted
    assert "bad-href-4444444444.html" not in emitted


def test_build_daily_local_saved_article_organizer_uses_valid_paragraph_index_fallbacks() -> None:
    story = _story("paragraph-index-signal-1111111111")
    article = _article(
        story.id,
        brief_sections=[],
        paragraphs=["", "Indexed product evidence paragraph.", "Unused paragraph."],
        paragraphs_zh=["", "索引单品证据段落。", "未使用段落。"],
        content_sections=[
            _section(
                "Products",
                key="product_signals",
                items=[
                    _item(
                        "Indexed item",
                        references=[_ref("Indexed bag", ref_type="bag", label="product")],
                        paragraph_indices=[99, -1, 0, 1, 1],
                    )
                ],
            ),
            _section(
                "Unrecognized",
                key="takeaways",
                items=[
                    _item(
                        "Dropped item",
                        body="This unrecognized item should not be emitted.",
                        references=[_ref("General theme", ref_type="theme", label="theme")],
                        paragraph_indices=[2],
                    )
                ],
            ),
        ],
    )

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    by_key = {lane.key: lane for lane in organizer.lanes}
    assert by_key["products"].cards[0].excerpt.en == "Indexed product evidence paragraph."
    assert by_key["products"].cards[0].excerpt.zh == "索引单品证据段落。"
    assert "This unrecognized item should not be emitted" not in repr(organizer)


def test_build_daily_local_saved_article_organizer_omits_label_only_items() -> None:
    story = _story("label-only-signal-1111111111")
    article = _article(
        story.id,
        brief_sections=[],
        paragraphs=["Only the source context paragraph is available."],
        paragraphs_zh=["只有来源语境段落可用。"],
        content_sections=[
            _section(
                "Products",
                key="product_signals",
                items=[
                    _item(
                        "Label-only product",
                        references=[_ref("Label-only product", ref_type="product")],
                        paragraph_indices=[99, -1],
                    )
                ],
            )
        ],
    )

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    assert "Label-only product" not in repr(organizer)
    assert "products" not in {lane.key for lane in organizer.lanes}


def test_build_daily_local_saved_article_organizer_caps_and_dedupes() -> None:
    story = _story("cap-signal-1111111111")
    refs = [
        _ref("The Row", ref_type="brand", label="brand"),
        _ref("Margaux bag", ref_type="bag", label="product"),
        _ref("Ballet flat", ref_type="shoe", label="product"),
        _ref("Mary-Kate Olsen", ref_type="designer", label="person"),
        _ref("Hidden overflow", ref_type="brand", label="brand"),
        _ref("The Row", ref_type="brand", label="brand"),
    ]
    article = _article(
        story.id,
        content_sections=[
            _section(
                f"Products {index}",
                key="product_signals",
                items=[
                    _item(
                        f"Margaux bag {index}",
                        body=f"Margaux bag {index} body",
                        references=refs,
                        paragraph_indices=[0, 1],
                    )
                ],
            )
            for index in range(6)
        ],
    )

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    by_key = {lane.key: lane for lane in organizer.lanes}
    assert len(by_key["products"].cards) == DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE
    assert by_key["products"].total_count == 6
    assert (
        len(by_key["products"].cards[0].references)
        == DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD
    )
    assert "Hidden overflow" not in repr(by_key["products"].cards[0])
    assert "Products 5" not in repr(organizer)


def test_build_daily_local_saved_article_organizer_truncates_long_text() -> None:
    story = _story("long-text-signal-1111111111")
    full_paragraph = " ".join(["The Row local article paragraph"] * 20)

    organizer = build_row_one_daily_local_saved_article_organizer(
        _edition(story),
        {
            story.id: _article(
                story.id,
                brief_sections=[],
                paragraphs=[full_paragraph],
                paragraphs_zh=[full_paragraph],
                content_sections=[],
            )
        },
        {story.id: f"{story.id}.html"},
    )

    assert organizer is not None
    emitted = repr(organizer)
    assert full_paragraph not in emitted
    assert organizer.lanes[0].cards[0].excerpt.en.endswith("...")
    assert len(organizer.lanes[0].cards[0].excerpt.en) <= (
        DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS
    )


def test_build_daily_local_saved_article_organizer_returns_none_without_content() -> None:
    story = _story("empty-signal-1111111111")

    assert (
        build_row_one_daily_local_saved_article_organizer(
            _edition(story),
            {},
            {story.id: f"{story.id}.html"},
        )
        is None
    )
    assert (
        build_row_one_daily_local_saved_article_organizer(
            _edition(story),
            {
                story.id: _article(
                    story.id,
                    paragraphs=["", " "],
                    brief_sections=[_brief("Brief with no safe article paragraph anchor.")],
                    content_sections=[],
                )
            },
            {story.id: f"{story.id}.html"},
        )
        is None
    )
    assert (
        build_row_one_daily_local_saved_article_organizer(
            _edition(story),
            {story.id: _article(story.id)},
            {},
        )
        is None
    )
