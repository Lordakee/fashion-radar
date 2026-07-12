from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.local_article_synthesis_brief import (
    build_row_one_local_article_synthesis_brief,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 12, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline="The Row resets the quiet luxury signal",
        summary=_lt(
            "The saved article frames a quieter product-led luxury read.",
            "这篇保存文章呈现更克制的产品驱动奢侈品判断。",
        ),
        why_it_matters=_lt(
            "It matters because the signal is already visible in key bags.",
            "重要之处在于这一信号已经体现在关键包袋中。",
        ),
        editorial_takeaway=_lt(
            "The stronger read is restraint turning into a merchandising advantage.",
            "更强的判断是克制正在转化为商品优势。",
        ),
        signal_context=_lt(
            "Quiet luxury attention is shifting from logo absence to durable hero items.",
            "静奢注意力正从无标识转向耐久明星单品。",
        ),
        reader_path=_lt(
            "Read the body through brand, product, and buyer cues.",
            "从品牌、产品与购买者线索阅读正文。",
        ),
        source_name="Vogue Business",
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _brief_section(
    key: str,
    body_en: str,
    body_zh: str | None = None,
) -> RowOneLocalArticleBriefSection:
    return RowOneLocalArticleBriefSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(key.replace("_", " ").title(), key),
        body=_lt(body_en, body_zh),
    )


def _item(
    label: str,
    *,
    body: LocalizedText | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, label),
        body=body,
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    title: str,
    *,
    key: str = "brand_signals",
    body: LocalizedText | None = None,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, title),
        body=body,
        items=items or [],
    )


def _article(
    story_id: str = "the-row-signal-1234567890",
    *,
    source_name: str = "Vogue Runway",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    brief_sections: list[RowOneLocalArticleBriefSection] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title="The Row makes restraint commercial",
        url="https://example.com/article",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs
        if paragraphs is not None
        else [
            "The opening paragraph shows how restraint is becoming a clearer luxury code.",
            "The Margaux bag gives the story a product proof point.",
            "Retail buyers describe demand moving toward durable silhouettes.",
        ],
        paragraphs_zh=paragraphs_zh
        if paragraphs_zh is not None
        else [
            "开篇段落显示克制正在成为更清晰的奢侈品代码。",
            "Margaux 包为这篇文章提供产品证据点。",
            "零售买手描述需求正转向耐久廓形。",
        ],
        brief_sections=brief_sections
        if brief_sections is not None
        else [
            _brief_section(
                "signal_context",
                "The local article connects restraint with product-level buying signals.",
                "本地文章把克制与产品层面的购买信号连接起来。",
            ),
            _brief_section(
                "what_happened",
                "A runway-to-retail read gives the story a concrete fashion-market frame.",
                "从秀场到零售的阅读为故事提供具体时尚市场框架。",
            ),
        ],
        content_sections=content_sections
        if content_sections is not None
        else [
            _section(
                "Brand Signals",
                body=_lt(
                    "The article adds brand evidence around The Row's disciplined merchandising.",
                    "文章补充了 The Row 克制商品策略的品牌证据。",
                ),
                items=[
                    _item(
                        "The Row",
                        body=_lt(
                            "The Row appears as the commercial anchor rather than "
                            "only an aesthetic reference.",
                            "The Row 在这里是商业锚点，而不只是审美参照。",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            ),
            _section(
                "Product Signals",
                key="product_signals",
                body=_lt(
                    "The Margaux example turns the trend into a concrete accessory signal.",
                    "Margaux 案例把趋势转化为具体配饰信号。",
                ),
                items=[_item("Margaux", paragraph_indices=[1])],
            ),
        ],
    )


def test_build_local_article_synthesis_brief_uses_story_and_local_article_text() -> None:
    brief = build_row_one_local_article_synthesis_brief(
        story=_story(),
        local_article=_article(),
    )

    assert brief is not None
    assert brief.title.en == "Local Article Synthesis Brief"
    assert brief.title.zh == "本地文章综合简报"
    assert brief.source_name == "Vogue Runway"
    assert brief.lead.en == "The stronger read is restraint turning into a merchandising advantage."
    assert (
        brief.thesis.en == "The local article connects restraint with product-level buying signals."
    )
    assert (
        brief.article_adds.en
        == "The article adds brand evidence around The Row's disciplined merchandising."
    )
    assert "saved body anchors" in brief.reader_move.en
    assert brief.basis_note.en == (
        "Built from saved ROW ONE story fields and local article text already stored for this page."
    )
    assert [anchor.href for anchor in brief.anchors] == [
        "#local-article-content-section-1",
        "#local-article-content-section-2",
        "#local-article-paragraph-1",
    ]


def test_build_local_article_synthesis_brief_returns_none_for_mismatched_story() -> None:
    assert (
        build_row_one_local_article_synthesis_brief(
            story=_story(),
            local_article=_article(story_id="different-story-1234567890"),
        )
        is None
    )


def test_build_local_article_synthesis_brief_returns_none_for_unsafe_story_id() -> None:
    unsafe_id = "../unsafe"
    assert (
        build_row_one_local_article_synthesis_brief(
            story=_story(story_id=unsafe_id),
            local_article=_article(story_id=unsafe_id),
        )
        is None
    )


def test_build_local_article_synthesis_brief_returns_none_without_meaningful_text() -> None:
    blank = _lt("", "")
    story = _story().model_copy(
        update={
            "summary": blank,
            "why_it_matters": blank,
            "editorial_takeaway": blank,
            "signal_context": blank,
            "reader_path": blank,
        }
    )
    article = _article(
        paragraphs=[" ", ""],
        paragraphs_zh=["", ""],
        brief_sections=[],
        content_sections=[],
    )

    assert build_row_one_local_article_synthesis_brief(story=story, local_article=article) is None


def test_build_local_article_synthesis_brief_handles_missing_and_misaligned_zh() -> None:
    story = _story().model_copy(
        update={
            "editorial_takeaway": _lt("English-only editorial read.", ""),
            "summary": _lt("English-only summary.", ""),
            "signal_context": _lt("English-only signal context.", ""),
        }
    )
    article = _article(
        paragraphs=["English paragraph one.", "English paragraph two."],
        paragraphs_zh=[""],
        brief_sections=[
            _brief_section("signal_context", "English-only local signal.", ""),
            _brief_section("what_happened", "English-only local happened.", ""),
        ],
        content_sections=[
            _section(
                "English Section",
                body=_lt("English-only section body.", ""),
                items=[_item("Signal", body=_lt("English-only item body.", ""))],
            )
        ],
    )

    brief = build_row_one_local_article_synthesis_brief(story=story, local_article=article)

    assert brief is not None
    assert brief.lead.zh == "English-only editorial read."
    assert brief.thesis.zh == "English-only local signal."
    assert brief.article_adds.zh == "English-only section body."
    assert brief.anchors[0].label.zh == "English Section"


def test_build_local_article_synthesis_brief_caps_text_and_anchors() -> None:
    long_lead = "Lead " * 80
    long_thesis = "Thesis " * 80
    long_adds = "Adds " * 80
    article = _article(
        brief_sections=[_brief_section("signal_context", long_thesis)],
        content_sections=[
            _section("One", body=_lt(long_adds)),
            _section("Two", key="entities", body=_lt("Second section support.")),
            _section("Three", key="product_signals", body=_lt("Third section support.")),
        ],
        paragraphs=["First paragraph support.", "Second paragraph support."],
    )
    story = _story().model_copy(update={"editorial_takeaway": _lt(long_lead)})

    brief = build_row_one_local_article_synthesis_brief(story=story, local_article=article)

    assert brief is not None
    assert len(brief.lead.en) == 180
    assert brief.lead.en.endswith("...")
    assert len(brief.thesis.en) == 160
    assert brief.thesis.en.endswith("...")
    assert len(brief.article_adds.en) == 160
    assert brief.article_adds.en.endswith("...")
    assert len(brief.anchors) == 3


def test_build_local_article_synthesis_brief_dedupes_consumed_sources() -> None:
    consumed_signal = "Distinct signal context."
    story = _story().model_copy(
        update={
            "editorial_takeaway": _lt("Distinct editorial read."),
            "summary": _lt("Fallback summary should not be consumed."),
            "signal_context": _lt(consumed_signal),
        }
    )
    article = _article(
        brief_sections=[
            _brief_section("signal_context", consumed_signal),
            _brief_section("what_happened", "Fallback happened text."),
        ],
        content_sections=[
            _section(
                "Brand Signals",
                body=_lt(consumed_signal),
                items=[_item("The Row", body=_lt("Distinct item body."))],
            )
        ],
        paragraphs=[consumed_signal],
    )

    brief = build_row_one_local_article_synthesis_brief(story=story, local_article=article)

    assert brief is not None
    emitted = {brief.lead.en, brief.thesis.en, brief.article_adds.en}
    assert emitted == {
        "Distinct editorial read.",
        "Distinct signal context.",
        "Distinct item body.",
    }


def test_build_local_article_synthesis_brief_dedupes_content_section_body_source() -> None:
    body = "Shared section body should be consumed only once."
    story = _story().model_copy(
        update={
            "editorial_takeaway": _lt("Distinct editorial read."),
            "summary": _lt("Fallback summary."),
            "signal_context": _lt("", ""),
        }
    )
    article = _article(
        brief_sections=[],
        content_sections=[
            _section(
                "Shared Section",
                body=_lt(body),
                items=[_item("The Row", body=_lt("Distinct item body."))],
            )
        ],
        paragraphs=["Distinct paragraph body."],
    )

    brief = build_row_one_local_article_synthesis_brief(story=story, local_article=article)

    assert brief is not None
    assert brief.lead.en == "Distinct editorial read."
    assert brief.thesis.en == "Shared Section: Shared section body should be consumed only once."
    assert brief.article_adds.en == "Distinct item body."


def test_build_local_article_synthesis_brief_requires_three_unique_cards() -> None:
    repeated = "Only one meaningful sentence exists."
    story = _story().model_copy(
        update={
            "editorial_takeaway": _lt(repeated),
            "summary": _lt(repeated),
            "why_it_matters": _lt(repeated),
            "signal_context": _lt(repeated),
        }
    )
    article = _article(
        paragraphs=[repeated],
        paragraphs_zh=[repeated],
        brief_sections=[
            _brief_section("signal_context", repeated),
            _brief_section("what_happened", repeated),
            _brief_section("watch_next", repeated),
        ],
        content_sections=[
            _section(
                "Repeated",
                body=_lt(repeated),
                items=[_item("Repeated item", body=_lt(repeated))],
            )
        ],
    )

    assert build_row_one_local_article_synthesis_brief(story=story, local_article=article) is None
