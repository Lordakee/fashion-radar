from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_article_intelligence_brief import (
    DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES,
    DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE,
    DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES,
    build_row_one_daily_local_article_intelligence_brief,
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
    refs: list[RowOneReference] | None = None,
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline or f"Headline {story_id}",
        summary=_lt("Summary", "摘要"),
        why_it_matters=_lt(f"{headline or story_id} matters", f"{headline or story_id} 重要"),
        editorial_takeaway=_lt("Takeaway", "编辑判断"),
        signal_context=_lt("Signal context", "信号背景"),
        reader_path=_lt("Reader path", "阅读路径"),
        source_name=source_name,
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
        entity_refs=refs or [],
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
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=_lt(f"{label} support", f"{label} 支撑"),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "brand_signals",
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, f"{title} zh"),
        body=_lt(f"{title} section body", f"{title} 栏目正文"),
        items=items or [],
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    brand: str = "The Row",
    product: str = "Margaux bag",
    person: str = "Mary-Kate Olsen",
    theme: str = "Quiet luxury reset",
    paragraphs: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title or f"Local article {story_id}",
        url="https://example.com/source",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs
        or [
            f"{brand} sets the opening signal.",
            f"{product} becomes the product proof.",
            f"{person} frames the styling context.",
        ],
        paragraphs_zh=[
            f"{brand} 建立开场信号。",
            f"{product} 成为单品证据。",
            f"{person} 提供造型背景。",
        ],
        brief_sections=[_brief(f"{brand} opens the saved local read.")],
        content_sections=[
            _section(
                "Brand Signals",
                key="brand_signals",
                items=[
                    _item(
                        brand,
                        references=[
                            _ref(brand, ref_type="brand", label="brand"),
                            _ref(product, ref_type="bag", label="product"),
                            _ref(person, ref_type="person", label="designer"),
                        ],
                        paragraph_indices=[0, 1],
                    )
                ],
            ),
            _section(
                theme,
                key="takeaways",
                items=[
                    _item(
                        product,
                        references=[_ref(f"{product} flats", ref_type="shoe", label="product")],
                        paragraph_indices=[2],
                    )
                ],
            ),
        ]
        if content_sections is None
        else content_sections,
    )


def test_build_daily_local_article_intelligence_brief_summarizes_saved_articles() -> None:
    first = _story("the-row-signal-1111111111", headline="The Row signal")
    second = _story("khaite-signal-2222222222", headline="Khaite signal", source_name="WWD")

    brief = build_row_one_daily_local_article_intelligence_brief(
        _edition(first, second),
        {
            first.id: _article(first.id, source_name="Vogue Business"),
            second.id: _article(
                second.id,
                source_name="WWD",
                brand="Khaite",
                product="Lotus tote",
                person="Cate Holstein",
                theme="Soft structure",
            ),
        },
        {
            first.id: f"{first.id}.html",
            second.id: f"{second.id}.html",
        },
    )

    assert brief is not None
    assert brief.title.en == "Daily Local Article Intelligence Brief"
    assert brief.title.zh == "每日文章情报摘要"
    assert brief.article_count == 2
    assert brief.source_count == 2
    assert brief.signal_count == 12
    assert brief.evidence_count == 6
    assert brief.opening_signal.en == "The Row opens the saved local read."
    assert [lane.key for lane in brief.lanes] == ["brands", "products", "people", "themes"]
    assert len(brief.lanes) <= DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES
    by_key = {lane.key: lane for lane in brief.lanes}
    assert [chip.label.en for chip in by_key["brands"].chips] == ["The Row", "Khaite"]
    assert [chip.support_count for chip in by_key["brands"].chips] == [1, 1]
    assert [chip.label.en for chip in by_key["products"].chips] == [
        "Margaux bag",
        "Margaux bag flats",
        "Lotus tote",
        "Lotus tote flats",
    ]
    assert [article.href for article in brief.articles] == [
        f"articles/{first.id}.html#local-article-content-section-1",
        f"articles/{second.id}.html#local-article-content-section-1",
    ]
    assert brief.articles[0].routes[0].href == (
        f"articles/{first.id}.html#local-article-content-section-1"
    )
    assert brief.articles[0].routes[1].href == (
        f"articles/{first.id}.html#local-article-content-section-2"
    )


def test_build_daily_local_article_intelligence_brief_filters_unsafe_inputs() -> None:
    valid = _story("valid-signal-1111111111")
    mismatched = _story("mismatched-signal-2222222222")
    unsafe = _story("unsafe/story")
    missing_href = _story("missing-href-3333333333")
    bad_href = _story("bad-href-4444444444")

    brief = build_row_one_daily_local_article_intelligence_brief(
        _edition(valid, mismatched, unsafe, missing_href, bad_href),
        {
            valid.id: _article(valid.id, brand="The Row"),
            mismatched.id: _article("other-signal-5555555555", brand="Khaite"),
            unsafe.id: _article(unsafe.id, brand="Alaia"),
            missing_href.id: _article(missing_href.id, brand="Prada"),
            bad_href.id: _article(bad_href.id, brand="Chanel"),
        },
        {
            valid.id: f"{valid.id}.html",
            mismatched.id: f"{mismatched.id}.html",
            unsafe.id: "unsafe/story.html",
            bad_href.id: "../bad-href-4444444444.html",
        },
    )

    assert brief is not None
    assert [article.title.en for article in brief.articles] == [valid.headline]
    assert brief.articles[0].href == (f"articles/{valid.id}.html#local-article-content-section-1")
    emitted = repr(brief)
    assert "../" not in emitted
    assert "unsafe/story" not in emitted
    assert "articles/mismatched-signal-2222222222.html" not in emitted
    assert "articles/missing-href-3333333333.html" not in emitted


def test_build_daily_local_article_intelligence_brief_caps_and_sorts_deterministically() -> None:
    stories = [_story(f"cap-story-{index}-1111111111") for index in range(6)]
    articles = {
        story.id: _article(
            story.id,
            brand=f"Brand {index}",
            product=f"Product {index}",
            person=f"Person {index}",
            theme=f"Theme {index}",
            content_sections=[
                _section(
                    "Brand Signals",
                    key="brand_signals",
                    items=[
                        _item(
                            f"Brand {index} item",
                            references=[
                                _ref("Shared Brand", ref_type="brand", label="brand"),
                                _ref(f"Brand {index}", ref_type="brand", label="brand"),
                                _ref(f"Brand Extra {index}", ref_type="brand", label="brand"),
                                _ref(f"Brand Hidden {index}", ref_type="brand", label="brand"),
                                _ref(f"Brand Overflow {index}", ref_type="brand", label="brand"),
                            ],
                            paragraph_indices=[0, 1, 2],
                        )
                    ],
                )
            ],
        )
        for index, story in enumerate(stories)
    }

    brief = build_row_one_daily_local_article_intelligence_brief(
        _edition(*stories),
        articles,
        {story.id: f"{story.id}.html" for story in stories},
    )

    assert brief is not None
    assert len(brief.articles) == DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES
    assert [article.title.en for article in brief.articles] == [
        story.headline for story in stories[:DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES]
    ]
    by_key = {lane.key: lane for lane in brief.lanes}
    assert len(by_key["brands"].chips) == DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE
    assert [chip.label.en for chip in by_key["brands"].chips] == [
        "Shared Brand",
        "Brand 0",
        "Brand Extra 0",
        "Brand Hidden 0",
        "Brand 1",
    ]
    assert by_key["brands"].chips[0].support_count == (
        DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES
    )
    assert by_key["brands"].total_count > DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE
    assert brief.evidence_count == DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES * 3
    assert brief.signal_count == sum(lane.total_count for lane in brief.lanes)
    assert "Brand 5" not in repr(brief)


def test_build_daily_local_article_intelligence_brief_keeps_metrics_aligned() -> None:
    skipped = _story("skipped-route-1111111111", headline="Skipped route story")
    included = _story("included-route-2222222222", headline="Included route story")
    lane_only_section = RowOneLocalArticleContentSection(
        key="brand_signals",  # type: ignore[arg-type]
        title=_lt("", ""),
        body=_lt("", ""),
        items=[
            RowOneLocalArticleContentItem(
                label=_lt("", ""),
                body=_lt("", ""),
                references=[_ref("Skipped Brand", ref_type="brand", label="brand")],
                paragraph_indices=[],
            )
        ],
    )

    brief = build_row_one_daily_local_article_intelligence_brief(
        _edition(skipped, included),
        {
            skipped.id: _article(
                skipped.id,
                brand="Skipped Brand",
                content_sections=[lane_only_section],
            ),
            included.id: _article(included.id, brand="Included Brand"),
        },
        {
            skipped.id: f"{skipped.id}.html",
            included.id: f"{included.id}.html",
        },
    )

    assert brief is not None
    assert [article.title.en for article in brief.articles] == [included.headline]
    assert brief.source_count == 1
    assert brief.evidence_count == 3
    by_key = {lane.key: lane for lane in brief.lanes}
    assert [chip.label.en for chip in by_key["brands"].chips] == ["Included Brand"]
    assert "Skipped Brand" not in repr(brief)


def test_build_daily_local_article_intelligence_brief_returns_none_without_content() -> None:
    story = _story("empty-signal-1111111111")

    assert (
        build_row_one_daily_local_article_intelligence_brief(
            _edition(story),
            {},
            {story.id: f"{story.id}.html"},
        )
        is None
    )
    assert (
        build_row_one_daily_local_article_intelligence_brief(
            _edition(story),
            {story.id: _article(story.id, paragraphs=[" ", ""], content_sections=[])},
            {story.id: f"{story.id}.html"},
        )
        is None
    )
    assert (
        build_row_one_daily_local_article_intelligence_brief(
            _edition(story),
            {story.id: _article(story.id)},
            {},
        )
        is None
    )
