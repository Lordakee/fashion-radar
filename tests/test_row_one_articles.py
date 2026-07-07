from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.collectors.article import ArticleExtractionResult
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.row_one.articles import (
    build_row_one_local_articles,
    row_one_local_articles_enabled,
    text_to_local_article_paragraphs,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 2, 4, 0, tzinfo=UTC)


def _edition(
    *, source_name: str = "Vogue Business", source_url: str = "https://example.com/the-row"
):
    story = RowOneStory(
        id="the-row-signal-1234567890",
        section_key="top_stories",
        story_type="tracked_entity",
        headline="The Row signal",
        summary=LocalizedText(zh="摘要", en="Summary"),
        why_it_matters=LocalizedText(zh="重要", en="Important"),
        editorial_takeaway=LocalizedText(zh="编辑", en="Editorial"),
        signal_context=LocalizedText(zh="背景", en="Context"),
        reader_path=LocalizedText(zh="路径", en="Path"),
        source_name=source_name,
        source_url=source_url,
        published_at=AS_OF,
        detail_path="details/the-row-signal-1234567890.html",
    )
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="今日", en="Today"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="重点", en="Top"),
            )
        ],
        stories=[story],
    )


def _source(
    *,
    name: str = "Vogue Business",
    url: str = "https://example.com/feed.xml",
    enabled: bool = True,
    max_chars: int = 80,
) -> SourceDefinition:
    return SourceDefinition(
        name=name,
        type=SourceType.RSS,
        url=url,
        article={"enabled": False},
        row_one_article={"enabled": enabled, "max_chars": max_chars},
    )


def _extractor(text: str):
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Signal source",
            text=text,
            skipped=False,
        )

    return extractor


def _skipped_extractor(reason: str):
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(url=url, skipped=True, reason=reason)

    return extractor


def _raising_extractor():
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise RuntimeError("boom")

    return extractor


def _assert_local_article_brief_sections(article, story) -> None:
    assert [section.key for section in article.brief_sections] == [
        "what_happened",
        "why_it_matters",
        "signal_context",
        "watch_next",
    ]
    assert [section.title.en for section in article.brief_sections] == [
        "What Happened",
        "Why It Matters",
        "Signal Context",
        "Watch Next",
    ]
    assert [section.title.zh for section in article.brief_sections] == [
        "发生了什么",
        "为什么重要",
        "信号背景",
        "接下来观察",
    ]
    assert [section.body.en for section in article.brief_sections] == [
        story.summary.en,
        story.why_it_matters.en,
        story.signal_context.en,
        story.reader_path.en,
    ]
    assert [section.body.zh for section in article.brief_sections] == [
        story.summary.zh,
        story.why_it_matters.zh,
        story.signal_context.zh,
        story.reader_path.zh,
    ]


def _content_section(article, key: str):
    return next(section for section in article.content_sections if section.key == key)


def _content_item(section, label_en: str):
    return next(item for item in section.items if item.label.en == label_en)


def test_row_one_local_article_content_sections_default_empty() -> None:
    article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph."],
    )

    assert article.content_sections == []


def test_row_one_local_article_defaults_body_source_for_existing_sidecars() -> None:
    article = RowOneLocalArticle.model_validate(
        {
            "story_id": "the-row-signal-1234567890",
            "url": "https://example.com/the-row",
            "source_name": "Vogue Business",
            "extracted_at": AS_OF.isoformat(),
            "paragraphs": ["Saved paragraph."],
        }
    )

    assert article.body_source == "extracted"


def test_text_to_local_article_paragraphs_caps_total_text_at_word_boundary() -> None:
    paragraphs = text_to_local_article_paragraphs(
        "First paragraph has compact context.\n\nSecond paragraph has trailing marker TAIL.",
        max_chars=68,
    )

    assert paragraphs == [
        "First paragraph has compact context.",
        "Second paragraph has trailing...",
    ]
    assert sum(len(paragraph) for paragraph in paragraphs) <= 68


def test_text_to_local_article_paragraphs_omits_tiny_truncated_tail() -> None:
    paragraphs = text_to_local_article_paragraphs(
        "First sentence has enough context.\n\nSecond sentence would only leave a tiny tail.",
        max_chars=40,
    )

    assert paragraphs == ["First sentence has enough context."]


def test_text_to_local_article_paragraphs_strips_feed_html_and_generated_prefix() -> None:
    paragraphs = text_to_local_article_paragraphs(
        (
            'Original source summary: &lt;a href="https://example.com/story"&gt;'
            '&lt;img alt="" src="hero.jpg" /&gt;&lt;/a&gt;'
            "The Row expanded its appointment calendar &amp; showroom notes."
        ),
        max_chars=240,
    )

    assert paragraphs == ["The Row expanded its appointment calendar & showroom notes."]


def test_text_to_local_article_paragraphs_removes_boilerplate_and_dedupes_long_sentences() -> None:
    paragraphs = text_to_local_article_paragraphs(
        (
            "Saint Laurent named a new executive. Read the full story here. "
            "Saint Laurent named a new executive. Prices rose. Prices rose."
        ),
        max_chars=240,
    )

    assert paragraphs == ["Saint Laurent named a new executive. Prices rose. Prices rose."]


def test_text_to_local_article_paragraphs_dedupes_long_sentences_across_paragraphs() -> None:
    paragraphs = text_to_local_article_paragraphs(
        (
            "Saint Laurent named a new executive director today.\n\n"
            "Saint Laurent named a new executive director today."
        ),
        max_chars=200,
    )

    assert paragraphs == ["Saint Laurent named a new executive director today."]


def test_text_to_local_article_paragraphs_keeps_repeated_short_sentences_across_paragraphs() -> (
    None
):
    paragraphs = text_to_local_article_paragraphs(
        "Prices rose.\n\nPrices rose.",
        max_chars=200,
    )

    assert paragraphs == ["Prices rose.", "Prices rose."]


def test_text_to_local_article_paragraphs_strips_script_and_style_content() -> None:
    paragraphs = text_to_local_article_paragraphs(
        (
            "The Row opened a new appointment room."
            "<script>alert('inline noise')</script>"
            "<style>.ad { display: block; }</style>"
            "Buyers reported a tighter edit."
        ),
        max_chars=240,
    )

    assert paragraphs == ["The Row opened a new appointment room. Buyers reported a tighter edit."]


def test_text_to_local_article_paragraphs_strips_unknown_feed_tags() -> None:
    paragraphs = text_to_local_article_paragraphs(
        'Lead <webfeedsFeaturedVisual data-x="1">inline</webfeedsFeaturedVisual> text.',
        max_chars=200,
    )

    assert paragraphs == ["Lead inline text."]


def test_text_to_local_article_paragraphs_strips_chinese_prefix_and_boilerplate() -> None:
    paragraphs = text_to_local_article_paragraphs(
        "来源摘要：品牌发布了新系列。阅读全文。点击查看全文。",
        max_chars=200,
    )

    assert paragraphs == ["品牌发布了新系列。"]


def test_text_to_local_article_paragraphs_splits_long_paragraphs_before_budget() -> None:
    paragraphs = text_to_local_article_paragraphs(
        (
            "First sentence sets the fashion context for the story. "
            "Second sentence adds the buyer and brand implication for ROW ONE. "
            "Third sentence gives the product angle and closes the brief."
        ),
        max_chars=220,
    )

    assert paragraphs == [
        "First sentence sets the fashion context for the story. "
        "Second sentence adds the buyer and brand implication for ROW ONE.",
        "Third sentence gives the product angle and closes the brief.",
    ]


def test_text_to_local_article_paragraphs_unescapes_entities_once() -> None:
    paragraphs = text_to_local_article_paragraphs(
        "A literal encoded ampersand &amp;amp; a plain ampersand & should stay readable.",
        max_chars=160,
    )

    assert paragraphs == [
        "A literal encoded ampersand &amp; a plain ampersand & should stay readable."
    ]


def test_text_to_local_article_paragraphs_filters_extraction_boilerplate() -> None:
    text = """
    We use cookies to improve your experience.

    Sign up for our newsletter.

    Share this article.

    Advertisement.

    Image credit: Courtesy of the brand.

    https://example.com/fashion/story

    The Row opened a Milan showroom after buyers cited stronger demand for quiet-luxury tailoring.

    window.__INITIAL_STATE__ = {"tracking": true};

    阅读全文。

    Miu Miu named a new CEO.
    """

    paragraphs = text_to_local_article_paragraphs(text, max_chars=220)

    assert paragraphs == [
        "The Row opened a Milan showroom after buyers cited stronger demand for "
        "quiet-luxury tailoring.",
        "Miu Miu named a new CEO.",
    ]


def test_text_to_local_article_paragraphs_filters_noise_before_budgeting() -> None:
    text = """
    Subscribe to continue reading this article and unlock unlimited fashion coverage.

    The Row opened a Milan showroom after buyers cited stronger demand.

    Buyers cited demand.
    """

    paragraphs = text_to_local_article_paragraphs(text, max_chars=95)

    assert paragraphs == [
        "The Row opened a Milan showroom after buyers cited stronger demand.",
        "Buyers cited demand.",
    ]


def test_text_to_local_article_paragraphs_preserves_short_valid_fashion_news() -> None:
    text = """
    Prices rose.

    Buyers cited demand.

    The Row opened a showroom.

    Miu Miu named a CEO.

    Zendaya wore Margaux.

    Sales rose 8%.

    品牌发布了新系列。

    By Malene Birger opened a showroom.

    Photography drove the campaign.
    """

    assert text_to_local_article_paragraphs(text, max_chars=500) == [
        "Prices rose.",
        "Buyers cited demand.",
        "The Row opened a showroom.",
        "Miu Miu named a CEO.",
        "Zendaya wore Margaux.",
        "Sales rose 8%.",
        "品牌发布了新系列。",
        "By Malene Birger opened a showroom.",
        "Photography drove the campaign.",
    ]


def test_build_row_one_local_articles_extracts_enabled_source_and_caps_text() -> None:
    calls: list[tuple[str, int, bool]] = []

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        calls.append((url, source.article.max_summary_chars, source.article.enabled))
        return ArticleExtractionResult(
            url=url,
            title="Extracted title",
            text=(
                "First paragraph has compact context.\n\nSecond paragraph has trailing marker TAIL."
            ),
            published_at="2026-07-02T03:00:00Z",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=68)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert calls == [("https://example.com/the-row", 568, True)]
    assert article.title == "Extracted title"
    assert article.source_name == "Vogue Business"
    assert article.body_source == "extracted"
    assert article.reason is None
    assert article.skipped is False
    assert article.paragraphs == [
        "First paragraph has compact context.",
        "Second paragraph has trailing...",
    ]
    assert article.extracted_at == AS_OF
    assert article.published_at == datetime(2026, 7, 2, 3, 0, tzinfo=UTC)


def test_build_row_one_local_articles_uses_extraction_buffer_before_final_cap() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        assert source.article.enabled is True
        assert source.article.max_summary_chars > 68
        return ArticleExtractionResult(
            url=url,
            title="Buffered title",
            text="First paragraph has compact context. Second paragraph has trailing marker TAIL.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=68)],
        now=AS_OF,
        extractor=extractor,
    )

    paragraphs = articles["the-row-signal-1234567890"].paragraphs
    assert sum(len(paragraph) for paragraph in paragraphs) <= 68
    assert paragraphs[-1].endswith("...")
    assert not paragraphs[-1].endswith("traili...")


def test_build_row_one_local_articles_marks_extracted_body_source() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_extractor("The Row opened a new showroom.\n\nBuyers cited demand."),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "extracted"
    assert article.reason is None
    assert article.skipped is False


def test_build_row_one_local_articles_env_kill_switch_wins(monkeypatch) -> None:
    monkeypatch.setenv("ROW_ONE_LOCAL_ARTICLES", "0")

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise AssertionError("extractor should not be called when kill switch is off")

    assert row_one_local_articles_enabled(local_articles_enabled=True) is False
    assert (
        build_row_one_local_articles(
            _edition(),
            [_source()],
            now=AS_OF,
            extractor=extractor,
        )
        == {}
    )


def test_build_row_one_local_articles_skips_unsafe_or_unmatched_stories() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise AssertionError("extractor should not be called for skipped stories")

    assert (
        build_row_one_local_articles(
            _edition(source_url="javascript:alert(1)"),
            [_source()],
            now=AS_OF,
            extractor=extractor,
        )
        == {}
    )
    assert (
        build_row_one_local_articles(
            _edition(source_name="Removed Source", source_url="https://missing.example/story"),
            [_source()],
            now=AS_OF,
            extractor=extractor,
        )
        == {}
    )


def test_build_row_one_local_articles_uses_first_enabled_hostname_match() -> None:
    matched_sources: list[str] = []

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        matched_sources.append(source.name)
        return ArticleExtractionResult(
            url=url,
            text="Local article body.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(source_name="Historical Source", source_url="https://shared.example/story"),
        [
            _source(name="Disabled", url="https://shared.example/feed.xml", enabled=False),
            _source(name="First Enabled", url="https://shared.example/rss.xml", enabled=True),
            _source(name="Second Enabled", url="https://shared.example/atom.xml", enabled=True),
        ],
        now=AS_OF,
        extractor=extractor,
    )

    assert matched_sources == ["First Enabled"]
    assert articles["the-row-signal-1234567890"].source_name == "Historical Source"


def test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure() -> None:
    edition = _edition()

    articles = build_row_one_local_articles(
        edition,
        [_source()],
        now=AS_OF,
        extractor=_raising_extractor(),
    )

    article = articles["the-row-signal-1234567890"]
    assert article.body_source == "summary_fallback"
    assert article.reason == "extraction_failed"
    assert article.skipped is False
    assert article.paragraphs == [
        "Summary",
        "Editorial",
    ]
    assert article.paragraphs_zh == [
        "摘要",
        "编辑",
    ]
    _assert_local_article_brief_sections(article, edition.stories[0])


def test_build_row_one_local_articles_marks_skipped_extraction_as_summary_fallback() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_skipped_extractor("robots_disallowed"),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "summary_fallback"
    assert article.reason == "robots_disallowed"
    assert article.skipped is False
    assert article.paragraphs


def test_build_row_one_local_articles_marks_exception_as_summary_fallback() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_raising_extractor(),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "summary_fallback"
    assert article.reason == "extraction_failed"
    assert article.skipped is False


def test_build_row_one_local_articles_marks_unavailable_fallback_body_as_skipped() -> None:
    edition = _edition()
    edition.stories[0].summary = LocalizedText(en="   ", zh="   ")

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_raising_extractor(),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "skipped"
    assert article.reason == "extraction_failed"
    assert article.skipped is True
    assert article.paragraphs == []
    assert article.paragraphs_zh == []


def test_build_row_one_local_articles_marks_empty_text_as_summary_fallback() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_extractor("   "),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "summary_fallback"
    assert article.reason == "no_extractable_text"


def test_build_row_one_local_articles_falls_back_when_extracted_text_has_only_noise() -> None:
    edition = _edition()

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_extractor(
            "\n\n".join(
                [
                    "Subscribe to continue reading this article.",
                    "Share this article.",
                    "Advertisement.",
                    "阅读全文。",
                ]
            )
        ),
    )

    article = articles["the-row-signal-1234567890"]
    story = edition.stories[0]
    assert article.body_source == "summary_fallback"
    assert article.reason == "no_publishable_paragraphs"
    assert article.title == story.headline
    assert article.paragraphs
    assert all("Subscribe to continue" not in paragraph for paragraph in article.paragraphs)


def test_build_row_one_local_articles_keeps_extracted_body_after_filtering_mixed_text() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="product", label="bag")]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor(
            "\n\n".join(
                [
                    "Share this article.",
                    "The Row opened a Milan showroom as Margaux demand accelerated with buyers.",
                    "Advertisement.",
                    "Buyers cited demand for quieter luxury bags in the latest market notes.",
                ]
            )
        ),
    )

    article = articles[story.id]
    assert article.body_source == "extracted"
    assert article.paragraphs[0].startswith("The Row")
    assert len(article.paragraphs_zh) == len(article.paragraphs)
    for section in article.content_sections:
        for item in section.items:
            for index in item.paragraph_indices:
                assert 0 <= index < len(article.paragraphs)


def test_build_row_one_local_articles_aligns_paragraph_indices_after_filtered_preface() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="product", label="bag")]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor(
            "\n\n".join(
                [
                    "Sign up for our newsletter.",
                    "The Row opened a Milan showroom for wholesale appointments.",
                    "The Margaux bag drew stronger demand from buyers.",
                ]
            )
        ),
    )

    article = articles[story.id]
    assert article.body_source == "extracted"
    assert article.paragraphs[:2] == [
        "The Row opened a Milan showroom for wholesale appointments.",
        "The Margaux bag drew stronger demand from buyers.",
    ]
    assert _content_item(_content_section(article, "entities"), "The Row").paragraph_indices == [0]
    assert _content_item(
        _content_section(article, "product_signals"),
        "Margaux",
    ).paragraph_indices == [1]


def test_build_row_one_local_articles_cleans_fallback_without_mutating_story_summary() -> None:
    edition = _edition()
    original_summary = (
        "Original source summary: <a href='https://example.com/story'>"
        "<img src='hero.jpg'></a>The Row showroom note. Read the full story here."
    )
    edition.stories[0].summary.en = original_summary

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(url=url, skipped=True, reason="no_extractable_text")

    articles = build_row_one_local_articles(
        edition,
        [_source()],
        now=AS_OF,
        extractor=extractor,
    )

    assert articles["the-row-signal-1234567890"].paragraphs == [
        "The Row showroom note.",
        "Editorial",
    ]
    assert articles["the-row-signal-1234567890"].body_source == "summary_fallback"
    assert articles["the-row-signal-1234567890"].reason == "no_extractable_text"
    assert articles["the-row-signal-1234567890"].paragraphs_zh == [
        "摘要",
        "编辑",
    ]
    assert edition.stories[0].summary.en == original_summary


def test_build_row_one_local_articles_cleans_brief_summary_html_without_mutating_story() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.summary = LocalizedText(
        en=(
            'Original source summary: <a href="https://example.com/story">'
            '<img alt="" src="hero.jpg" /></a>'
            "The Row expanded its appointment calendar &amp; showroom notes."
        ),
        zh=(
            '来源摘要：<a href="https://example.com/story">'
            '<img alt="" src="hero.jpg" /></a>'
            "The Row 扩展预约 &amp; 陈列室笔记。"
        ),
    )
    original_summary = story.summary.model_copy(deep=True)

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise RuntimeError("network failed")

    articles = build_row_one_local_articles(
        edition,
        [_source()],
        now=AS_OF,
        extractor=extractor,
    )

    brief = articles["the-row-signal-1234567890"].brief_sections[0]
    assert brief.key == "what_happened"
    assert brief.body.en == "The Row expanded its appointment calendar & showroom notes."
    assert brief.body.zh == "The Row 扩展预约 & 陈列室笔记。"
    assert "<" not in brief.body.en
    assert ">" not in brief.body.en
    assert "<" not in brief.body.zh
    assert ">" not in brief.body.zh
    assert story.summary == original_summary


def test_build_row_one_local_articles_takeaways_prefer_signal_dense_paragraphs() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    story.designer_refs = [
        RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer")
    ]
    # Tags are intentionally excluded from signal-dense takeaway matching.
    story.tags = ["quiet luxury"]
    paragraphs = [
        "Opening market context without a named signal.",
        "The Row and Margaux bag demand accelerated in saved source reporting.",
        "General retail context continues across wholesale accounts.",
        "Mary-Kate Olsen framed the design language around restraint.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    article = articles[story.id]
    takeaways = _content_section(article, "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "The Row and Margaux bag demand accelerated in saved source reporting.",
        "Mary-Kate Olsen framed the design language around restraint.",
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1], [3]]


def test_build_row_one_local_articles_takeaways_keep_first_three_when_no_signal_matches() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    paragraphs = [
        "Opening source paragraph.",
        "Second source paragraph.",
        "Third source paragraph.",
        "Fourth source paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs[:3]
    assert [item.paragraph_indices for item in takeaways.items] == [[0], [1], [2]]


def test_build_row_one_local_articles_takeaways_keep_original_order_for_equal_scores() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="Zendaya", type="celebrity", label="new"),
    ]
    paragraphs = [
        "Opening source paragraph.",
        "The Row appears in this saved paragraph.",
        "Zendaya appears in this later saved paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs[1:]
    assert [item.paragraph_indices for item in takeaways.items] == [[1], [2]]


def test_build_row_one_local_articles_takeaways_ignore_short_ref_near_misses() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="Ro", type="brand", label="typo"),
        RowOneReference(name="Row", type="brand", label="short"),
        RowOneReference(name="The Row", type="brand", label="tracked"),
    ]
    paragraphs = [
        "Opening brown leather market context without a named signal.",
        "The Row appears as an explicit saved source signal.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "The Row appears as an explicit saved source signal."
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1]]


def test_build_row_one_local_articles_takeaways_ignore_front_row_short_ref() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="Row", type="brand", label="short"),
        RowOneReference(name="The Row", type="brand", label="tracked"),
    ]
    paragraphs = [
        "Buyers filled the front row before the show opened.",
        "The Row appears as an explicit saved source signal.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "The Row appears as an explicit saved source signal."
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1]]


def test_build_row_one_local_articles_takeaways_do_not_promote_appended_context() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.editorial_takeaway = LocalizedText(
        zh="The Row 编辑判断不应抢占来源段落。",
        en="The Row editorial context should not outrank saved source paragraphs.",
    )
    paragraphs = [
        "Opening source paragraph.",
        "Second saved source paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs
    assert [item.paragraph_indices for item in takeaways.items] == [[0], [1]]


def test_build_row_one_local_articles_takeaways_cap_signal_matches_at_three() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="Zendaya", type="celebrity", label="new"),
        RowOneReference(name="Mary-Kate Olsen", type="designer", label="founder"),
    ]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    paragraphs = [
        "The Row appears in the opening saved source paragraph.",
        "Zendaya appears in the second saved source paragraph.",
        "Margaux appears in the third saved source paragraph.",
        "Mary-Kate Olsen appears in the fourth saved source paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs[:3]
    assert [item.paragraph_indices for item in takeaways.items] == [[0], [1], [2]]


def test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs() -> (
    None
):
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="Zendaya", type="celebrity", label="new"),
    ]
    story.product_refs = [
        RowOneReference(name="Margaux", type="product", label="bag"),
    ]
    story.designer_refs = [
        RowOneReference(name="Mary-Kate Olsen", type="designer", label="founder"),
    ]
    story.tags = ["celebrity", "The Row", "quiet luxury", "The Row"]
    story.heat_delta = 7
    story.market_region = "US"
    story.source_region = "Global"

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Structured source",
            text=(
                "First source paragraph frames The Row demand.\n\n"
                "Second source paragraph shows Zendaya styling context around Margaux.\n\n"
                "Third source paragraph mentions Mary-Kate Olsen and a product signal."
            ),
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert [section.key for section in article.content_sections] == [
        "takeaways",
        "entities",
        "product_signals",
        "brand_signals",
    ]

    takeaways = _content_section(article, "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "Second source paragraph shows Zendaya styling context around Margaux.",
        "First source paragraph frames The Row demand.",
        "Third source paragraph mentions Mary-Kate Olsen and a product signal.",
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1], [0], [2]]

    entities = _content_section(article, "entities")
    the_row = _content_item(entities, "The Row")
    zendaya = _content_item(entities, "Zendaya")
    olsen = _content_item(entities, "Mary-Kate Olsen")
    assert the_row.references == [story.entity_refs[0]]
    assert the_row.paragraph_indices == [0]
    assert the_row.body is not None
    assert the_row.body.en == "First source paragraph frames The Row demand."
    assert the_row.body.zh == "First source paragraph frames The Row demand."
    assert zendaya.paragraph_indices == [1]
    assert zendaya.body is not None
    assert zendaya.body.en == (
        "Second source paragraph shows Zendaya styling context around Margaux."
    )
    assert olsen.paragraph_indices == [2]
    assert olsen.body is not None
    assert olsen.body.en == (
        "Third source paragraph mentions Mary-Kate Olsen and a product signal."
    )

    product_signals = _content_section(article, "product_signals")
    margaux = _content_item(product_signals, "Margaux")
    assert margaux.references == [story.product_refs[0]]
    assert margaux.paragraph_indices == [1]
    assert margaux.body is not None
    assert margaux.body.en == (
        "Second source paragraph shows Zendaya styling context around Margaux."
    )

    brand_signals = _content_section(article, "brand_signals")
    assert _content_item(brand_signals, "Heat delta").body.en == "+7"
    assert _content_item(brand_signals, "Tags").body.en == "celebrity, The Row, quiet luxury"
    assert _content_item(brand_signals, "Source").body.en == "Vogue Business"
    assert _content_item(brand_signals, "Market region").body.en == "US"
    assert _content_item(brand_signals, "Source region").body.en == "Global"


def test_build_row_one_local_articles_content_sections_work_on_fallback() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise RuntimeError("network failed")

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert [section.key for section in article.content_sections] == [
        "takeaways",
        "entities",
        "brand_signals",
    ]
    assert _content_section(article, "takeaways").items[0].body.en == "Summary"
    unmatched = _content_item(_content_section(article, "entities"), "The Row")
    assert unmatched.references == [story.entity_refs[0]]
    assert unmatched.body is not None
    assert unmatched.body.en == "brand / tracked"
    assert unmatched.body.zh == "brand / tracked"


def test_build_row_one_local_articles_reference_excerpt_requires_name_match() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.product_refs = [RowOneReference(name="Margaux", type="product", label="bag")]

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Generic product source",
            text="The bag signal is accelerating, but this paragraph names no specific product.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    product_section = _content_section(
        articles["the-row-signal-1234567890"],
        "product_signals",
    )
    margaux = _content_item(product_section, "Margaux")
    assert margaux.paragraph_indices == [0]
    assert margaux.body is not None
    assert margaux.body.en == "product / bag"
    assert margaux.body.zh == "product / bag"


def test_build_row_one_local_articles_omits_empty_optional_content_sections() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Plain source",
            text="Plain source paragraph without refs.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert [section.key for section in article.content_sections] == [
        "takeaways",
        "brand_signals",
    ]
    assert "entities" not in [section.key for section in article.content_sections]
    assert "product_signals" not in [section.key for section in article.content_sections]


def test_build_row_one_local_articles_content_sections_model_dump_json() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.product_refs = [RowOneReference(name="Margaux", type="product", label="bag")]

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Product source",
            text="The Margaux bag is the product signal to watch.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    dumped = articles["the-row-signal-1234567890"].model_dump(mode="json")
    product_section = next(
        section for section in dumped["content_sections"] if section["key"] == "product_signals"
    )
    assert product_section["items"][0]["label"]["en"] == "Margaux"
    assert product_section["items"][0]["references"] == [
        {"name": "Margaux", "type": "product", "label": "bag"}
    ]
    assert product_section["items"][0]["body"] == {
        "en": "The Margaux bag is the product signal to watch.",
        "zh": "The Margaux bag is the product signal to watch.",
    }
    assert product_section["items"][0]["paragraph_indices"] == [0]


def test_build_row_one_local_articles_enriches_short_extracted_text() -> None:
    edition = _edition()

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Short extraction",
            text="Tiny source note.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    assert articles["the-row-signal-1234567890"].paragraphs == [
        "Tiny source note.",
        "Editorial",
    ]
    assert not any(
        duplicate in articles["the-row-signal-1234567890"].paragraphs
        for duplicate in ("Important", "Context", "Path")
    )
    assert articles["the-row-signal-1234567890"].paragraphs_zh == [
        "Tiny source note.",
        "编辑",
    ]
    _assert_local_article_brief_sections(
        articles["the-row-signal-1234567890"],
        edition.stories[0],
    )


def test_build_row_one_local_articles_falls_back_when_extracted_text_cleans_empty() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Boilerplate only",
            text="Read the full story here.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    article = articles["the-row-signal-1234567890"]
    assert article.title == "The Row signal"
    assert article.paragraphs == [
        "Summary",
        "Editorial",
    ]


def test_build_row_one_local_articles_enriches_after_unusable_source_tail() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Short source with unusable tail",
            text=(
                "Tiny source note.\n\n"
                "Second paragraph is intentionally too long for the remaining budget and "
                "should not prevent ROW ONE context from filling the local article."
            ),
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=38)],
        now=AS_OF,
        extractor=extractor,
    )

    paragraphs = articles["the-row-signal-1234567890"].paragraphs

    assert paragraphs == ["Tiny source note.", "Editorial"]
    assert sum(len(paragraph) for paragraph in paragraphs) <= 38


def test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Substantial extraction",
            text=(
                "First extracted paragraph carries enough context for the local article body. "
                "It is intentionally longer than a tiny feed summary and exceeds the context "
                "threshold used for fallback enrichment.\n\n"
                "Second extracted paragraph adds source detail without requiring local editorial "
                "fallback, keeping this article substantial without ROW ONE context."
            ),
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=extractor,
    )

    paragraphs = articles["the-row-signal-1234567890"].paragraphs

    assert sum(len(paragraph) for paragraph in paragraphs) >= 240
    assert any(paragraph.startswith("First extracted paragraph") for paragraph in paragraphs)
    assert any("Second extracted paragraph" in paragraph for paragraph in paragraphs)
    assert not any(
        context in paragraph
        for paragraph in paragraphs
        for context in ("Editorial", "Important", "Context", "Path")
    )
    assert articles["the-row-signal-1234567890"].paragraphs_zh == paragraphs
