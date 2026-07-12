from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_synthesis_brief import (
    DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS,
    build_row_one_daily_local_synthesis_brief,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 12, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _story(
    story_id: str,
    *,
    headline: str | None = None,
    source_name: str = "Vogue Business",
    lead: str | None = None,
    lead_zh: str | None = None,
) -> RowOneStory:
    title = headline or story_id.replace("-", " ").title()
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=title,
        summary=_lt(f"{title} summary frames the saved article."),
        why_it_matters=_lt(f"{title} matters because the local text adds context."),
        editorial_takeaway=_lt(
            lead or f"{title} gives the daily read a distinct local signal.",
            lead_zh,
        ),
        signal_context=_lt(f"{title} signal context stays article-backed."),
        reader_path=_lt(f"Read {title} through saved local evidence."),
        source_name=source_name,
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _edition(stories: list[RowOneStory]) -> RowOneEdition:
    return RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=_lt("Daily ROW ONE summary."),
        stories=stories,
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


def _item(label: str, body: str, body_zh: str | None = None) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, label),
        body=_lt(body, body_zh),
        paragraph_indices=[0],
    )


def _section(
    title: str,
    body: str,
    *,
    key: str = "brand_signals",
    body_zh: str | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(title, title),
        body=_lt(body, body_zh),
        items=[_item(f"{title} item", f"{body} Item support.", body_zh)],
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Runway",
    thesis: str | None = None,
    thesis_zh: str | None = None,
    adds: str | None = None,
    adds_zh: str | None = None,
) -> RowOneLocalArticle:
    article_title = title if title is not None else story_id.replace("-", " ").title()
    return RowOneLocalArticle(
        story_id=story_id,
        title=article_title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            f"{article_title} paragraph one keeps the article synthesis grounded.",
            f"{article_title} paragraph two gives the local read more texture.",
        ],
        paragraphs_zh=[
            f"{article_title} 第一段让文章综合保持本地依据。",
            f"{article_title} 第二段补充本地阅读纹理。",
        ],
        brief_sections=[
            _brief_section(
                "signal_context",
                thesis or f"{article_title} thesis comes from the saved brief section.",
                thesis_zh,
            ),
            _brief_section(
                "what_happened",
                f"{article_title} happened text is available as fallback.",
            ),
        ],
        content_sections=[
            _section(
                "Article Adds",
                adds or f"{article_title} adds a concrete article-level evidence mix.",
                body_zh=adds_zh,
            )
        ],
    )


def _blank_story(story_id: str) -> RowOneStory:
    blank = _lt("", "")
    return _story(story_id).model_copy(
        update={
            "summary": blank,
            "why_it_matters": blank,
            "editorial_takeaway": blank,
            "signal_context": blank,
            "reader_path": blank,
        }
    )


def _blank_article(story_id: str) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title="",
        url=f"https://example.com/{story_id}",
        source_name="",
        extracted_at=AS_OF,
        paragraphs=[],
        paragraphs_zh=[],
        brief_sections=[],
        content_sections=[],
    )


def _hrefs(*story_ids: str) -> dict[str, str]:
    return {story_id: f"{story_id}.html" for story_id in story_ids}


def test_build_daily_local_synthesis_brief_uses_current_edition_saved_articles() -> None:
    story_ids = [
        "runway-reset-1111111111",
        "retail-shift-2222222222",
        "buyer-signal-3333333333",
    ]
    stories = [
        _story(
            story_ids[0],
            headline="Runway Reset",
            source_name="Source A",
            lead="Runway Reset turns the local read toward restraint.",
        ),
        _story(
            story_ids[1],
            headline="Retail Shift",
            source_name="Source B",
            lead="Retail Shift adds a buyer-side signal to the day.",
        ),
        _story(
            story_ids[2],
            headline="Buyer Signal",
            source_name="Source C",
            lead="Buyer Signal makes the article cluster more commercial.",
        ),
    ]
    local_articles = {
        story_ids[0]: _article(
            story_ids[0],
            title="Runway Reset Article",
            source_name="Local Source A",
            thesis="Runway Reset thesis comes from Stage 382 synthesis.",
            adds="Runway Reset article adds merchandising evidence.",
        ),
        story_ids[1]: _article(
            story_ids[1],
            title="Retail Shift Article",
            source_name="Local Source B",
            thesis="Retail Shift thesis comes from Stage 382 synthesis.",
            adds="Retail Shift article adds channel evidence.",
        ),
        story_ids[2]: _article(
            story_ids[2],
            title="Buyer Signal Article",
            source_name="Local Source C",
            thesis="Buyer Signal thesis comes from Stage 382 synthesis.",
            adds="Buyer Signal article adds demand evidence.",
        ),
        "not-in-edition-9999999999": _article("not-in-edition-9999999999"),
    }

    brief = build_row_one_daily_local_synthesis_brief(
        _edition(stories),
        local_articles,
        {
            **_hrefs(*story_ids),
            "not-in-edition-9999999999": "not-in-edition-9999999999.html",
        },
    )

    assert brief is not None
    assert brief.title.en == "Daily Local Synthesis Brief"
    assert brief.title.zh == "每日本地综合简报"
    assert brief.dek.en == "A cross-article read assembled from today's saved local text."
    assert brief.dek.zh == "基于今日已保存本地正文整理出的跨文章判断。"
    assert brief.basis_note.en == (
        "Built from current-edition ROW ONE stories and saved local article synthesis "
        "already generated for article pages."
    )
    assert brief.article_count == 3
    assert brief.source_count == 3
    assert brief.card_count == 3
    assert [card.href for card in brief.cards] == [
        "runway-reset-1111111111.html",
        "retail-shift-2222222222.html",
        "buyer-signal-3333333333.html",
    ]
    assert [card.title.en for card in brief.cards] == [
        "Runway Reset Article",
        "Retail Shift Article",
        "Buyer Signal Article",
    ]
    assert [card.source_name for card in brief.cards] == [
        "Local Source A",
        "Local Source B",
        "Local Source C",
    ]
    assert [card.read.en for card in brief.cards] == [
        "Runway Reset turns the local read toward restraint.",
        "Retail Shift adds a buyer-side signal to the day.",
        "Buyer Signal makes the article cluster more commercial.",
    ]
    assert [card.adds.en for card in brief.cards] == [
        "Runway Reset article adds merchandising evidence.",
        "Retail Shift article adds channel evidence.",
        "Buyer Signal article adds demand evidence.",
    ]
    assert brief.thesis.en == "Runway Reset thesis comes from Stage 382 synthesis."
    assert brief.opening_read.en == (
        "Today's local read connects Runway Reset Article with Retail Shift Article."
    )
    assert all(card.route_label.en == "Read the saved article" for card in brief.cards)
    assert all(card.route_label.zh == "阅读保存文章" for card in brief.cards)


def test_build_daily_local_synthesis_brief_requires_two_articles() -> None:
    story_id = "single-story-1111111111"

    brief = build_row_one_daily_local_synthesis_brief(
        _edition([_story(story_id)]),
        {story_id: _article(story_id)},
        _hrefs(story_id),
    )

    assert brief is None


def test_build_daily_local_synthesis_brief_filters_unsafe_or_missing_hrefs() -> None:
    unsafe_cases = {
        "absolute-url-1111111111": "https://example.com/article.html",
        "index-page-2222222222": "index.html",
        "traversal-3333333333": "../unsafe.html",
        "query-string-4444444444": "query-string-4444444444.html?x=1",
        "fragment-5555555555": "fragment-5555555555.html#local-article-paragraph-1",
        "prefixed-path-6666666666": "articles/prefixed-path-6666666666.html",
        "wrong-stem-7777777777": "other-story-7777777777.html",
        "whitespace-8888888888": " whitespace-8888888888.html ",
        "missing-href-9999999999": "",
        "safe-story-1010101010": "safe-story-1010101010.html",
    }
    stories = [_story(story_id) for story_id in unsafe_cases]
    local_articles = {story.id: _article(story.id) for story in stories}
    article_hrefs = {
        story_id: href
        for story_id, href in unsafe_cases.items()
        if story_id != "missing-href-9999999999"
    }

    brief = build_row_one_daily_local_synthesis_brief(
        _edition(stories),
        local_articles,
        article_hrefs,
    )

    assert brief is None


def test_build_daily_local_synthesis_brief_dedupes_titles_hrefs_and_reads() -> None:
    duplicate_id = "shared-card-1111111111"
    duplicate_read_id = "duplicate-read-2222222222"
    same_title_id = "same-title-3333333333"
    same_source_id = "same-source-4444444444"
    extra_id = "extra-source-5555555555"
    stories = [
        _story(
            duplicate_id,
            headline="Shared Card One",
            source_name="Same Source",
            lead="Shared Card One creates the first distinct daily read.",
        ),
        _story(
            duplicate_id,
            headline="Shared Card One",
            source_name="Same Source",
            lead="Shared Card One creates the first distinct daily read.",
        ),
        _story(
            duplicate_read_id,
            headline="Duplicate Read",
            source_name="Different Source",
            lead="Shared Card One creates the first distinct daily read.",
        ),
        _story(
            same_title_id,
            headline="Shared Title Different Href",
            source_name="Same Source",
            lead="Shared Title Different Href keeps a distinct read.",
        ),
        _story(
            same_source_id,
            headline="Same Source Distinct",
            source_name="Same Source",
            lead="Same Source Distinct keeps another same-source read.",
        ),
        _story(
            extra_id,
            headline="Extra Source",
            source_name="Extra Source",
            lead="Extra Source counts before the card cap.",
        ),
    ]
    local_articles = {
        duplicate_id: _article(
            duplicate_id,
            title="Shared Title",
            source_name="Same Source",
            thesis="Shared Card thesis.",
            adds="Shared Card article adds.",
        ),
        duplicate_read_id: _article(
            duplicate_read_id,
            title="Duplicate Read Title",
            source_name="Different Source",
            thesis="Duplicate Read thesis.",
            adds="Duplicate Read article adds.",
        ),
        same_title_id: _article(
            same_title_id,
            title="Shared Title",
            source_name="Same Source",
            thesis="Same Title thesis.",
            adds="Same Title article adds.",
        ),
        same_source_id: _article(
            same_source_id,
            title="Same Source Distinct",
            source_name="Same Source",
            thesis="Same Source thesis.",
            adds="Same Source article adds.",
        ),
        extra_id: _article(
            extra_id,
            title="Extra Source",
            source_name="Extra Source",
            thesis="Extra Source thesis.",
            adds="Extra Source article adds.",
        ),
    }

    brief = build_row_one_daily_local_synthesis_brief(
        _edition(stories),
        local_articles,
        _hrefs(duplicate_id, duplicate_read_id, same_title_id, same_source_id, extra_id),
    )

    assert brief is not None
    assert brief.article_count == 4
    assert brief.source_count == 2
    assert brief.card_count == 3
    assert [card.href for card in brief.cards] == [
        "shared-card-1111111111.html",
        "same-title-3333333333.html",
        "same-source-4444444444.html",
    ]
    assert [card.title.en for card in brief.cards] == [
        "Shared Title",
        "Shared Title",
        "Same Source Distinct",
    ]
    assert [card.source_name for card in brief.cards].count("Same Source") == 3
    assert "duplicate-read-2222222222.html" not in {card.href for card in brief.cards}


def test_build_daily_local_synthesis_brief_handles_missing_zh() -> None:
    first_id = "english-only-1111111111"
    second_id = "english-only-2222222222"
    stories = [
        _story(
            first_id,
            headline="English Only One",
            lead="English-only first lead survives as Chinese fallback.",
            lead_zh="",
        ).model_copy(
            update={
                "summary": _lt("English-only first summary.", ""),
                "why_it_matters": _lt("English-only first why.", ""),
                "signal_context": _lt("English-only first signal.", ""),
            }
        ),
        _story(
            second_id,
            headline="English Only Two",
            lead="English-only second lead survives as Chinese fallback.",
            lead_zh="",
        ).model_copy(
            update={
                "summary": _lt("English-only second summary.", ""),
                "why_it_matters": _lt("English-only second why.", ""),
                "signal_context": _lt("English-only second signal.", ""),
            }
        ),
    ]
    local_articles = {
        first_id: _article(
            first_id,
            title="English Only One Article",
            thesis="English-only first thesis.",
            thesis_zh="",
            adds="English-only first adds.",
            adds_zh="",
        ),
        second_id: _article(
            second_id,
            title="English Only Two Article",
            thesis="English-only second thesis.",
            thesis_zh="",
            adds="English-only second adds.",
            adds_zh="",
        ),
    }

    brief = build_row_one_daily_local_synthesis_brief(
        _edition(stories),
        local_articles,
        _hrefs(first_id, second_id),
    )

    assert brief is not None
    first_card = brief.cards[0]
    assert first_card.title.zh == "English Only One Article"
    assert first_card.read.zh == "English-only first lead survives as Chinese fallback."
    assert first_card.adds.zh == "English-only first adds."
    assert brief.thesis.zh == "English-only first thesis."
    assert brief.opening_read.zh
    assert brief.basis_note.zh


def test_build_daily_local_synthesis_brief_returns_none_when_all_articles_lack_synthesis() -> None:
    story_ids = [
        "blank-story-1111111111",
        "blank-story-2222222222",
        "blank-story-3333333333",
    ]

    brief = build_row_one_daily_local_synthesis_brief(
        _edition([_blank_story(story_id) for story_id in story_ids]),
        {story_id: _blank_article(story_id) for story_id in story_ids},
        _hrefs(*story_ids),
    )

    assert brief is None


def test_build_daily_local_synthesis_brief_caps_text_cards_and_opening_titles() -> None:
    first_title = "First Maison merchandising discipline " + " ".join(
        f"calibrated{i}" for i in range(20)
    )
    second_title = "Second Retail channel evidence " + " ".join(f"measured{i}" for i in range(20))
    story_ids = [
        "long-title-1111111111",
        "long-title-2222222222",
        "long-title-3333333333",
        "long-title-4444444444",
    ]
    stories = [
        _story(
            story_ids[0],
            headline=first_title,
            source_name="Long Source A",
            lead="Lead A " * 40,
        ),
        _story(
            story_ids[1],
            headline=second_title,
            source_name="Long Source B",
            lead="Lead B " * 40,
        ),
        _story(
            story_ids[2],
            headline="Third Long Card",
            source_name="Long Source C",
            lead="Lead C " * 40,
        ),
        _story(
            story_ids[3],
            headline="Fourth Long Card",
            source_name="Long Source D",
            lead="Lead D " * 40,
        ),
    ]
    local_articles = {
        story_ids[0]: _article(
            story_ids[0],
            title=first_title,
            thesis="Thesis A " * 40,
            adds="Adds A " * 40,
        ),
        story_ids[1]: _article(
            story_ids[1],
            title=second_title,
            thesis="Thesis B " * 40,
            adds="Adds B " * 40,
        ),
        story_ids[2]: _article(
            story_ids[2],
            title="Third Long Card",
            thesis="Thesis C " * 40,
            adds="Adds C " * 40,
        ),
        story_ids[3]: _article(
            story_ids[3],
            title="Fourth Long Card",
            thesis="Thesis D " * 40,
            adds="Adds D " * 40,
        ),
    }

    brief = build_row_one_daily_local_synthesis_brief(
        _edition(stories),
        local_articles,
        _hrefs(*story_ids),
    )

    assert brief is not None
    assert brief.article_count == 4
    assert len(brief.cards) == 3
    assert brief.card_count == 3
    assert all(len(card.read.en) <= 150 for card in brief.cards)
    assert all(len(card.adds.en) <= 140 for card in brief.cards)
    assert all(card.read.en.endswith("...") for card in brief.cards)
    assert all(card.adds.en.endswith("...") for card in brief.cards)
    assert len(brief.thesis.en) <= 160
    assert brief.thesis.en.endswith("...")
    assert len(brief.opening_read.en) <= 180
    assert "Today's local read connects " in brief.opening_read.en
    assert "Today’s" not in brief.opening_read.en
    assert "First Maison merchandising discipline" in brief.opening_read.en
    assert "Second Retail channel evidence" in brief.opening_read.en
    assert brief.opening_read.en.count("...") >= 2
    assert brief.opening_read.en.endswith(".")
    assert len(first_title[:DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS]) < len(first_title)
    assert len(second_title[:DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS]) < len(second_title)
    assert "measu..." not in brief.opening_read.en
