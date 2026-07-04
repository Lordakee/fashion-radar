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
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise RuntimeError("network failed")

    articles = build_row_one_local_articles(
        _edition(),
        [_source()],
        now=AS_OF,
        extractor=extractor,
    )

    assert articles["the-row-signal-1234567890"].paragraphs == ["Summary"]


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

    assert articles["the-row-signal-1234567890"].paragraphs == ["The Row showroom note."]
    assert edition.stories[0].summary.en == original_summary
