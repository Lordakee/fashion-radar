from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_news_timeline import (
    build_row_one_daily_local_news_timeline,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneSection,
    RowOneStory,
)


def _text(value: str) -> LocalizedText:
    return LocalizedText(en=value, zh=value)


def _story(
    story_id: str,
    *,
    headline: str,
    published_at: str | None,
    source_name: str = "Vogue Business",
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline,
        summary=_text(f"{headline} summary"),
        why_it_matters=_text(f"{headline} why it matters"),
        editorial_takeaway=_text(f"{headline} takeaway"),
        signal_context=_text(f"{headline} signal"),
        reader_path=_text(f"{headline} reader path"),
        source_name=source_name,
        published_at=published_at,
        detail_path=f"details/{story_id}.html",
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    published_at: str | None = None,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        published_at=published_at,
        paragraphs=paragraphs or ["First saved paragraph for local reading."],
        paragraphs_zh=paragraphs_zh or [],
        brief_sections=[],
        content_sections=[],
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
            )
        ],
        stories=list(stories),
    )


def _hrefs(*stories: RowOneStory) -> dict[str, str]:
    return {story.id: f"{story.id}.html" for story in stories}


def test_daily_local_news_timeline_orders_newest_first_with_tie_breakers() -> None:
    older = _story(
        "older-story-1111111111",
        headline="Older saved story",
        published_at="2026-07-10T08:00:00Z",
    )
    tie_winner = _story(
        "tie-winner-2222222222",
        headline="Tie winner by edition order",
        published_at="2026-07-10T10:00:00Z",
        source_name="WWD",
    )
    tie_loser = _story(
        "tie-loser-3333333333",
        headline="Tie loser by edition order",
        published_at="2026-07-10T10:00:00Z",
        source_name="wwd",
    )
    newest = _story(
        "newest-story-4444444444",
        headline="Newest saved story",
        published_at="2026-07-10T12:00:00Z",
    )
    stories = (older, tie_winner, tie_loser, newest)

    timeline = build_row_one_daily_local_news_timeline(
        _edition(*stories),
        {story.id: _article(story.id, source_name=story.source_name) for story in stories},
        _hrefs(*stories),
    )

    assert timeline is not None
    assert [item.title.en for item in timeline.items] == [
        "Newest saved story",
        "Tie winner by edition order",
        "Tie loser by edition order",
        "Older saved story",
    ]
    assert timeline.item_count == len(timeline.items)
    assert timeline.source_count == 2
    assert timeline.latest_label.en == "Jul 10, 2026"
    assert timeline.latest_label.zh == "2026-07-10"


def test_daily_local_news_timeline_prefers_article_published_at() -> None:
    story = _story(
        "article-date-wins-1111111111",
        headline="Story date loses",
        published_at="2026-07-10T12:00:00Z",
    )

    timeline = build_row_one_daily_local_news_timeline(
        _edition(story),
        {
            story.id: _article(
                story.id,
                published_at="2026-07-09T07:00:00Z",
            )
        },
        _hrefs(story),
    )

    assert timeline is not None
    assert timeline.items[0].published_at == datetime(2026, 7, 9, 7, 0, tzinfo=UTC)
    assert timeline.items[0].published_label.en == "Jul 09, 2026"
    assert timeline.items[0].published_label.zh == "2026-07-09"


def test_daily_local_news_timeline_prefers_story_headline_before_article_title() -> None:
    story = _story(
        "headline-wins-1111111111",
        headline="Curated edition headline",
        published_at="2026-07-10T12:00:00Z",
    )

    timeline = build_row_one_daily_local_news_timeline(
        _edition(story),
        {
            story.id: _article(
                story.id,
                title="Raw extracted article title",
            )
        },
        _hrefs(story),
    )

    assert timeline is not None
    assert timeline.items[0].title.en == "Curated edition headline"
    assert timeline.items[0].title.zh == "Curated edition headline"


def test_daily_local_news_timeline_links_first_nonblank_paragraph_without_renumbering() -> None:
    story = _story(
        "paragraph-anchor-1111111111",
        headline="Paragraph anchor story",
        published_at="2026-07-10T12:00:00Z",
    )

    timeline = build_row_one_daily_local_news_timeline(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=[
                    "   ",
                    "The first saved paragraph after a blank line explains the look.",
                ],
                paragraphs_zh=["", "空白段之后的第一段本地正文。"],
            )
        },
        _hrefs(story),
    )

    assert timeline is not None
    assert (
        timeline.items[0].href
        == "articles/paragraph-anchor-1111111111.html#local-article-paragraph-2"
    )
    assert timeline.items[0].excerpt.en == (
        "The first saved paragraph after a blank line explains the look."
    )
    assert timeline.items[0].excerpt.zh == "空白段之后的第一段本地正文。"


def test_daily_local_news_timeline_filters_unsafe_and_unusable_entries() -> None:
    valid = _story(
        "valid-story-1111111111",
        headline="Only valid story",
        published_at="2026-07-10T12:00:00Z",
    )
    bad_story_id = _story(
        "bad story id",
        headline="Bad story id",
        published_at="2026-07-10T12:00:00Z",
    )
    mismatch = _story(
        "mismatch-story-2222222222",
        headline="Mismatched article",
        published_at="2026-07-10T12:00:00Z",
    )
    unsafe_href = _story(
        "unsafe-href-3333333333",
        headline="Unsafe href",
        published_at="2026-07-10T12:00:00Z",
    )
    mismatched_href = _story(
        "mismatched-href-7777777777",
        headline="Mismatched href",
        published_at="2026-07-10T12:00:00Z",
    )
    missing_time = _story(
        "missing-time-4444444444",
        headline="Missing time",
        published_at=None,
    )
    blank_text = _story(
        "blank-text-5555555555",
        headline="Blank text",
        published_at="2026-07-10T12:00:00Z",
    )

    timeline = build_row_one_daily_local_news_timeline(
        _edition(
            valid,
            bad_story_id,
            mismatch,
            unsafe_href,
            mismatched_href,
            missing_time,
            blank_text,
        ),
        {
            valid.id: _article(valid.id),
            bad_story_id.id: _article(bad_story_id.id),
            mismatch.id: _article("different-story-6666666666"),
            unsafe_href.id: _article(unsafe_href.id),
            mismatched_href.id: _article(mismatched_href.id),
            missing_time.id: _article(missing_time.id, published_at=None),
            blank_text.id: _article(blank_text.id, paragraphs=[" ", "\n"]),
        },
        {
            valid.id: f"{valid.id}.html",
            bad_story_id.id: f"{bad_story_id.id}.html",
            mismatch.id: f"{mismatch.id}.html",
            unsafe_href.id: "https://example.com/unsafe-href-3333333333.html",
            mismatched_href.id: "different-safe-story-8888888888.html",
            missing_time.id: f"{missing_time.id}.html",
            blank_text.id: f"{blank_text.id}.html",
        },
    )

    assert timeline is not None
    assert [item.title.en for item in timeline.items] == ["Only valid story"]


def test_daily_local_news_timeline_caps_entries() -> None:
    stories = tuple(
        _story(
            f"cap-story-{index:010d}",
            headline=f"Cap story {index}",
            published_at=f"2026-07-10T{index:02d}:00:00Z",
        )
        for index in range(1, 9)
    )

    timeline = build_row_one_daily_local_news_timeline(
        _edition(*stories),
        {story.id: _article(story.id) for story in stories},
        _hrefs(*stories),
    )

    assert timeline is not None
    assert len(timeline.items) == 6
    assert [item.title.en for item in timeline.items] == [
        "Cap story 8",
        "Cap story 7",
        "Cap story 6",
        "Cap story 5",
        "Cap story 4",
        "Cap story 3",
    ]


def test_daily_local_news_timeline_returns_none_without_usable_entries() -> None:
    story = _story(
        "no-usable-story-1111111111",
        headline="No usable story",
        published_at=None,
    )

    assert (
        build_row_one_daily_local_news_timeline(
            _edition(story),
            {story.id: _article(story.id, published_at=None)},
            _hrefs(story),
        )
        is None
    )
