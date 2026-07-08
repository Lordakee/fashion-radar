from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_key_signals import (
    SAVED_ARTICLE_KEY_SIGNALS_EVIDENCE_LIMIT,
    SAVED_ARTICLE_KEY_SIGNALS_EXCERPT_CHARS,
    SAVED_ARTICLE_KEY_SIGNALS_REFERENCE_LIMIT,
    SAVED_ARTICLE_KEY_SIGNALS_STATEMENT_CHARS,
    SAVED_ARTICLE_KEY_SIGNALS_THEME_LIMIT,
    build_row_one_saved_article_key_signals,
)

AS_OF = datetime(2026, 7, 8, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=f"Headline {story_id}",
        summary=_lt("Summary"),
        why_it_matters=_lt("Story why it matters", "Story why zh"),
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


def _reference(
    name: str = "The Row",
    *,
    ref_type: str = "brand",
    label: str = "brand",
) -> RowOneReference:
    return RowOneReference(name=name, type=ref_type, label=label)


def _brief(
    key: str = "why_it_matters",
    *,
    body: LocalizedText | None = None,
) -> RowOneLocalArticleBriefSection:
    return RowOneLocalArticleBriefSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(key.replace("_", " ").title()),
        body=body or _lt("Local why it matters", "Local why zh"),
    )


def _item(
    label: str,
    *,
    body: LocalizedText | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, f"{label} zh"),
        body=body if body is not None else _lt(f"{label} body", f"{label} body zh"),
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
    story_id: str = "the-row-signal-1234567890",
    *,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    brief_sections: list[RowOneLocalArticleBriefSection] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"Local article {story_id}",
        url="https://example.com/source",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=paragraphs
        or [
            "The Row reset its restraint signal for the season.",
            "The Margaux bag kept showing up as the commercial anchor.",
            "Alaia shoes gained fresh editor attention.",
            "Mary-Kate Olsen framed the silhouette shift.",
        ],
        paragraphs_zh=paragraphs_zh
        or [
            "The Row reset zh.",
            "Margaux bag zh.",
            "Alaia shoes zh.",
            "Mary-Kate Olsen zh.",
        ],
        brief_sections=brief_sections or [],
        content_sections=content_sections or [],
    )


def test_build_key_signals_uses_local_why_it_matters_before_story_fallback() -> None:
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(
            brief_sections=[_brief(body=_lt("Local explains the market signal", ""))]
        ),
    )

    assert signals is not None
    why = signals.groups[0]
    assert why.key == "why_it_matters"
    assert why.statement is not None
    assert why.statement.en == "Local explains the market signal"
    assert why.statement.zh == "Local explains the market signal"
    assert why.evidence == ()


def test_build_key_signals_uses_story_why_fallback_only_with_saved_text() -> None:
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(brief_sections=[_brief(body=_lt(" ", ""))]),
    )

    assert signals is not None
    why = signals.groups[0]
    assert why.key == "why_it_matters"
    assert why.statement is not None
    assert why.statement.en == "Story why it matters"
    assert why.evidence == ()

    assert (
        build_row_one_saved_article_key_signals(
            story=_story(),
            local_article=_article(
                paragraphs=[" ", ""],
                paragraphs_zh=[],
                brief_sections=[_brief(body=_lt(" ", ""))],
                content_sections=[],
            ),
        )
        is None
    )


def test_build_key_signals_buckets_references_and_keeps_readable_support() -> None:
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(
            brief_sections=[_brief(body=_lt("Why the signal matters"))],
            content_sections=[
                _section(
                    "People and brands",
                    key="entities",
                    items=[
                        _item(
                            "The Row",
                            body=_lt("The Row is the brand anchor.", "The Row support zh"),
                            references=[
                                _reference("The Row", ref_type="brand", label="brand"),
                                _reference("the row", ref_type="brand", label="tracked"),
                                _reference("Margaux", ref_type="accessory", label="product"),
                                _reference("Mary-Kate Olsen", ref_type="person", label="designer"),
                                _reference("Archive", ref_type="source", label="context"),
                                _reference(" ", ref_type="brand", label="brand"),
                            ],
                            paragraph_indices=[0, 1, 3],
                        )
                    ],
                )
            ],
        ),
    )

    assert signals is not None
    by_key = {group.key: group for group in signals.groups}
    assert [reference.name for reference in by_key["brands"].references] == ["The Row"]
    assert [reference.name for reference in by_key["products"].references] == ["Margaux"]
    assert [reference.name for reference in by_key["people"].references] == ["Mary-Kate Olsen"]
    assert by_key["brands"].statement is not None
    assert by_key["brands"].statement.en == "The Row is the brand anchor."
    assert by_key["brands"].evidence[0].href == "#local-article-paragraph-1"
    assert [paragraph.href for paragraph in by_key["brands"].evidence] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-2",
        "#local-article-paragraph-4",
    ]


def test_build_key_signals_uses_later_readable_support_when_first_item_is_blank() -> None:
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(
            brief_sections=[_brief(body=_lt("Why the signal matters"))],
            content_sections=[
                RowOneLocalArticleContentSection(
                    key="brand_signals",
                    title=_lt(" ", ""),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=_lt(" ", ""),
                            body=_lt(" ", ""),
                            references=[_reference("The Row", ref_type="brand", label="brand")],
                        ),
                        _item(
                            "The Row support",
                            body=_lt(
                                "Later item gives the readable brand signal.",
                                "Later support zh",
                            ),
                            references=[_reference("Alaia", ref_type="brand", label="brand")],
                        ),
                    ],
                )
            ],
        ),
    )

    assert signals is not None
    brands = {group.key: group for group in signals.groups}["brands"]
    assert brands.statement is not None
    assert brands.statement.en == "Later item gives the readable brand signal."


def test_build_key_signals_filters_invalid_paragraph_indices_and_zh_alignment() -> None:
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(
            paragraphs=[
                "Usable first paragraph.",
                "   ",
                "Usable third paragraph.",
            ],
            paragraphs_zh=["Only one zh paragraph."],
            brief_sections=[_brief(body=_lt("Why"))],
            content_sections=[
                _section(
                    "Brand signals",
                    key="brand_signals",
                    items=[
                        _item(
                            "Alaia",
                            references=[_reference("Alaia", ref_type="brand", label="brand")],
                            paragraph_indices=[True, 0, 0, 1, -1, "2", 99, 2],  # type: ignore[list-item]
                        )
                    ],
                )
            ],
        ),
    )

    assert signals is not None
    brands = {group.key: group for group in signals.groups}["brands"]
    assert [paragraph.href for paragraph in brands.evidence] == [
        "#local-article-paragraph-1",
        "#local-article-paragraph-3",
    ]
    assert brands.evidence[0].excerpt.zh == "Usable first paragraph."
    assert brands.evidence[1].excerpt.zh == "Usable third paragraph."


def test_build_key_signals_themes_use_display_labels_and_skip_reference_duplicates() -> None:
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(
            brief_sections=[_brief(body=_lt("Why"))],
            content_sections=[
                _section(
                    "Brand Signals",
                    key="brand_signals",
                    items=[
                        _item(
                            "The Row",
                            references=[_reference("The Row", ref_type="brand", label="brand")],
                        ),
                        _item("Quiet luxury reset", references=[]),
                    ],
                ),
                _section(
                    "Product Signals",
                    key="product_signals",
                    items=[_item("Margaux", references=[_reference("Margaux", label="product")])],
                ),
            ],
        ),
    )

    assert signals is not None
    themes = {group.key: group for group in signals.groups}["themes"]
    assert [theme.label.en for theme in themes.themes] == [
        "Brand Signals",
        "Quiet luxury reset",
        "Product Signals",
    ]
    assert "brand_signals" not in [theme.label.en for theme in themes.themes]
    assert "The Row" not in [theme.label.en for theme in themes.themes]
    assert "Margaux" not in [theme.label.en for theme in themes.themes]
    assert [theme.href for theme in themes.themes] == [
        "#local-article-content-section-1",
        "#local-article-content-section-1",
        "#local-article-content-section-2",
    ]


def test_build_key_signals_caps_references_themes_evidence_and_text() -> None:
    long_text = "Signal language " * 40
    signals = build_row_one_saved_article_key_signals(
        story=_story(),
        local_article=_article(
            paragraphs=[long_text, *[f"Paragraph {index}" for index in range(12)]],
            paragraphs_zh=[long_text, *[f"Paragraph zh {index}" for index in range(12)]],
            brief_sections=[_brief(body=_lt(long_text, long_text))],
            content_sections=[
                _section(
                    "Brand Signals",
                    key="brand_signals",
                    items=[
                        _item(
                            f"Theme {index}",
                            body=_lt(long_text, long_text),
                            references=[
                                _reference(
                                    f"Brand {index}",
                                    ref_type="brand",
                                    label="brand",
                                )
                            ],
                            paragraph_indices=[index],
                        )
                        for index in range(12)
                    ],
                )
            ],
        ),
    )

    assert signals is not None
    by_key = {group.key: group for group in signals.groups}
    assert by_key["why_it_matters"].statement is not None
    assert len(by_key["why_it_matters"].statement.en) <= (
        SAVED_ARTICLE_KEY_SIGNALS_STATEMENT_CHARS + 1
    )
    assert by_key["why_it_matters"].statement.en.endswith("...")
    assert len(by_key["brands"].references) == SAVED_ARTICLE_KEY_SIGNALS_REFERENCE_LIMIT
    assert len(by_key["brands"].evidence) == SAVED_ARTICLE_KEY_SIGNALS_EVIDENCE_LIMIT
    assert len(by_key["themes"].themes) == SAVED_ARTICLE_KEY_SIGNALS_THEME_LIMIT
    assert len(by_key["brands"].evidence[0].excerpt.en) <= (
        SAVED_ARTICLE_KEY_SIGNALS_EXCERPT_CHARS + 1
    )
    assert by_key["brands"].evidence[0].excerpt.en.endswith("...")


def test_build_key_signals_returns_none_for_unsafe_mismatch_or_no_meaningful_groups() -> None:
    assert (
        build_row_one_saved_article_key_signals(
            story=_story("unsafe/story"),
            local_article=_article("unsafe/story"),
        )
        is None
    )
    assert (
        build_row_one_saved_article_key_signals(
            story=_story("the-row-signal-1234567890"),
            local_article=_article(
                "other-signal-1234567890",
                brief_sections=[_brief(body=_lt("Why"))],
            ),
        )
        is None
    )
    assert (
        build_row_one_saved_article_key_signals(
            story=_story(),
            local_article=_article(
                paragraphs=[" ", ""],
                paragraphs_zh=[],
                brief_sections=[],
                content_sections=[
                    _section(
                        " ",
                        items=[
                            _item(
                                " ",
                                body=_lt(" ", ""),
                                references=[
                                    _reference("Archive", ref_type="source", label="context")
                                ],
                                paragraph_indices=[0],
                            )
                        ],
                    )
                ],
            ),
        )
        is None
    )
