from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_reading_itinerary import (
    DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS,
    DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS,
    DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD,
    DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS,
    build_row_one_daily_local_reading_itinerary,
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
    paragraph_indices: list[int | bool] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=(
            _lt(body, body_zh if body_zh is not None else f"{body} zh")
            if body is not None
            else None
        ),
        references=references or [],
        paragraph_indices=paragraph_indices or [],  # type: ignore[arg-type]
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


def test_build_daily_local_reading_itinerary_sequences_saved_content() -> None:
    story = _story("the-row-signal-1234567890", headline="The Row signal")

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=[
                    "The Row leads the saved local story with a sharper retail read.",
                    "The Margaux bag turns the read into product evidence.",
                    "Mary-Kate Olsen gives the coverage a people and brand frame.",
                ],
            )
        },
        {story.id: f"{story.id}.html"},
    )

    assert itinerary is not None
    assert itinerary.title.en == "Daily Local Reading Itinerary"
    assert itinerary.title.zh == "每日本地阅读路径"
    assert itinerary.dek.en == "A short path through today's saved local articles."
    assert itinerary.selected_count == 1
    assert itinerary.source_count == 1
    assert itinerary.evidence_count >= 2
    assert itinerary.start_here is not None
    assert itinerary.start_here.reason.en == "Start Here"
    assert itinerary.start_here.href == (
        "articles/the-row-signal-1234567890.html#local-article-paragraph-1"
    )
    assert [card.reason.en for card in itinerary.skim_next] == [
        "Brand / people signal",
        "Product signal",
        "Source context",
    ]
    assert itinerary.skim_next[0].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-1"
    )
    assert itinerary.skim_next[1].href == (
        "articles/the-row-signal-1234567890.html#local-article-content-section-2"
    )
    assert itinerary.skim_next[2].href == (
        "articles/the-row-signal-1234567890.html#local-article-paragraph-1"
    )
    assert "Extracted article text" in itinerary.skim_next[2].excerpt.en
    assert itinerary.skim_next[2].excerpt.en != itinerary.start_here.excerpt.en
    assert itinerary.evidence_trail
    assert itinerary.evidence_trail[0].label == "The Row"
    assert "Margaux bag" in repr(itinerary)


def test_build_daily_local_reading_itinerary_filters_unsafe_inputs() -> None:
    valid = _story("valid-signal-1111111111")
    mismatched = _story("mismatched-signal-2222222222")
    unsafe = _story("unsafe/story")
    missing_href = _story("missing-href-3333333333")
    bad_href = _story("bad-href-4444444444")
    external_href = _story("external-href-5555555555")

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(valid, mismatched, unsafe, missing_href, bad_href, external_href),
        {
            valid.id: _article(valid.id),
            mismatched.id: _article("other-signal-6666666666"),
            unsafe.id: _article(unsafe.id),
            missing_href.id: _article(missing_href.id),
            bad_href.id: _article(bad_href.id),
            external_href.id: _article(external_href.id),
        },
        {
            valid.id: f"{valid.id}.html",
            mismatched.id: f"{mismatched.id}.html",
            unsafe.id: "unsafe/story.html",
            bad_href.id: "../bad-href-4444444444.html",
            external_href.id: "https://example.com/external-href-5555555555.html",
        },
    )

    assert itinerary is not None
    emitted = repr(itinerary)
    assert "articles/valid-signal-1111111111.html" in emitted
    assert "../" not in emitted
    assert "https://example.com" not in emitted
    assert "unsafe/story" not in emitted
    assert "mismatched-signal-2222222222.html" not in emitted
    assert "missing-href-3333333333.html" not in emitted
    assert "bad-href-4444444444.html" not in emitted
    assert "external-href-5555555555.html" not in emitted


def test_build_daily_local_reading_itinerary_uses_valid_paragraph_index_fallbacks() -> None:
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
                        paragraph_indices=[99, -1, True, 0, 1, 1],
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

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert itinerary is not None
    product_cards = [card for card in itinerary.skim_next if card.reason.en == "Product signal"]
    assert product_cards[0].excerpt.en == "Indexed product evidence paragraph."
    assert product_cards[0].excerpt.zh == "索引单品证据段落。"
    assert product_cards[0].href == (
        "articles/paragraph-index-signal-1111111111.html#local-article-content-section-1"
    )
    assert "This unrecognized item should not be emitted" not in repr(itinerary)


def test_build_daily_local_reading_itinerary_omits_label_only_items() -> None:
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

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert itinerary is not None
    assert "Label-only product" not in repr(itinerary)
    assert "Product signal" not in {card.reason.en for card in itinerary.skim_next}


def test_build_daily_local_reading_itinerary_falls_back_when_article_title_missing() -> None:
    story = _story("missing-title-signal-1111111111", headline="Story fallback headline")
    article = _article(story.id).model_copy(update={"title": None})

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert itinerary is not None
    assert itinerary.start_here is not None
    assert itinerary.start_here.title.en == "Story fallback headline"
    assert itinerary.start_here.title.zh == "Story fallback headline"


def test_build_daily_local_reading_itinerary_evidence_label_falls_back_to_paragraph() -> None:
    story = _story("evidence-label-signal-1111111111", headline="Story fallback headline")
    article = _article(
        story.id,
        content_sections=[
            _section(
                "",
                key="product_signals",
                items=[
                    _item(
                        "",
                        body="Article-backed product body without a label.",
                        references=[],
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    ).model_copy(update={"title": None})

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert itinerary is not None
    assert itinerary.evidence_trail[0].label == "Paragraph 1"
    assert "Story fallback headline" not in repr(itinerary.evidence_trail)


def test_build_daily_local_reading_itinerary_caps_dedupes_and_truncates() -> None:
    story = _story("cap-signal-1111111111")
    full_paragraph = " ".join(["The Row local article paragraph"] * 30)
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
        paragraphs=[full_paragraph],
        paragraphs_zh=[full_paragraph],
        brief_sections=[],
        content_sections=[
            _section(
                "Products",
                key="product_signals",
                body=full_paragraph,
                items=[
                    _item(
                        f"Margaux duplicate {index}",
                        references=refs,
                        paragraph_indices=[0],
                    )
                    for index in range(6)
                ],
            ),
            *[
                _section(
                    f"Brand {index}",
                    key="entities",
                    items=[
                        _item(
                            f"Brand item {index}",
                            body=f"Brand item {index} body",
                            references=[_ref(f"Brand {index}", ref_type="brand")],
                            paragraph_indices=[0],
                        )
                    ],
                )
                for index in range(6)
            ],
        ],
    )

    itinerary = build_row_one_daily_local_reading_itinerary(
        _edition(story),
        {story.id: article},
        {story.id: f"{story.id}.html"},
    )

    assert itinerary is not None
    assert len(itinerary.skim_next) == DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS
    assert itinerary.evidence_count == len(itinerary.evidence_trail)
    assert len(itinerary.evidence_trail) == DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS
    assert len(itinerary.skim_next[0].labels) == DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD
    assert sum(1 for card in itinerary.skim_next if card.reason.en == "Product signal") == 1
    assert "Source context" in {card.reason.en for card in itinerary.skim_next}
    assert "Hidden overflow" not in repr(itinerary.skim_next[0])
    assert full_paragraph not in repr(itinerary)
    assert itinerary.start_here is not None
    assert itinerary.start_here.excerpt.en.endswith("...")
    assert len(itinerary.start_here.excerpt.en) <= DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS


def test_build_daily_local_reading_itinerary_returns_none_without_content() -> None:
    story = _story("empty-signal-1111111111")

    assert (
        build_row_one_daily_local_reading_itinerary(
            _edition(story),
            {},
            {story.id: f"{story.id}.html"},
        )
        is None
    )
    assert (
        build_row_one_daily_local_reading_itinerary(
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
        build_row_one_daily_local_reading_itinerary(
            _edition(story),
            {story.id: _article(story.id)},
            {},
        )
        is None
    )
