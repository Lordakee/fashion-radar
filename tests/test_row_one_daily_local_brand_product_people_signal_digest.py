from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.daily_local_brand_product_people_signal_digest import (
    DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT,
    DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT,
    build_row_one_daily_local_brand_product_people_signal_digest,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 13, 4, 0, tzinfo=UTC)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh if zh is not None else en)


def _reference(name: str, reference_type: str, *, label: str | None = None) -> RowOneReference:
    return RowOneReference(
        name=name,
        type=reference_type,
        label=label if label is not None else reference_type,
    )


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
        headline=headline or story_id.replace("-", " ").title(),
        summary=_lt("Saved local summary."),
        why_it_matters=_lt("Saved local coverage adds context."),
        editorial_takeaway=_lt("The saved article provides a factual signal."),
        signal_context=_lt("The signal remains grounded in local saved text."),
        reader_path=_lt("Read the saved local article."),
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


def _item(
    label: str,
    body: str | None,
    *references: RowOneReference,
    label_zh: str | None = None,
    body_zh: str | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=_lt(label, label_zh),
        body=_lt(body, body_zh) if body is not None else None,
        references=list(references),
        paragraph_indices=[0],
    )


def _section(
    key: str,
    *items: RowOneLocalArticleContentItem,
    title: str | None = None,
    title_zh: str | None = None,
    body: str | None = None,
    body_zh: str | None = None,
) -> RowOneLocalArticleContentSection:
    section_title = title if title is not None else key.replace("_", " ").title()
    return RowOneLocalArticleContentSection(
        key=key,  # type: ignore[arg-type]
        title=_lt(section_title, title_zh),
        body=_lt(body, body_zh) if body is not None else None,
        items=list(items),
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title or f"Saved article {story_id}",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=["Saved local article text."],
        paragraphs_zh=["保存的本地文章文本。"],
        content_sections=sections or [],
    )


def _hrefs(*story_ids: str) -> dict[str, str]:
    return {story_id: f"{story_id}.html" for story_id in story_ids}


def test_daily_bpp_digest_aggregates_first_seen_coverage() -> None:
    first_id = "the-row-signal-1111111111"
    second_id = "khaite-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition(
            [
                _story(first_id, headline="The Row signal"),
                _story(second_id, headline="Khaite signal", source_name="WWD"),
            ]
        ),
        {
            first_id: _article(
                first_id,
                title="The Row saved article",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "The Row and the Margaux bag anchor this saved local note.",
                            _reference("The Row", "brand"),
                            _reference("Margaux", "bag"),
                            _reference("Mary-Kate Olsen", "designer"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                title="Khaite saved article",
                source_name="WWD",
                sections=[
                    _section(
                        "entities",
                        _item(
                            "Khaite",
                            "Khaite adds a second saved local note.",
                            _reference("Khaite", "brand"),
                            _reference("The Row", "brand"),
                            _reference("Le Teckel", "bag"),
                            _reference("Margaux", "bag"),
                            _reference("Miuccia Prada", "designer"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    assert digest.article_count == 2
    assert digest.source_count == 2
    assert digest.entity_count == 6
    assert [bucket.key for bucket in digest.buckets] == ["brands", "products", "people"]
    assert [item.name.en for item in digest.buckets[0].items] == ["The Row", "Khaite"]
    assert [item.name.en for item in digest.buckets[1].items] == ["Margaux", "Le Teckel"]
    assert [item.name.en for item in digest.buckets[2].items] == [
        "Mary-Kate Olsen",
        "Miuccia Prada",
    ]
    the_row = digest.buckets[0].items[0]
    assert the_row.article_count == 2
    assert the_row.source_count == 2
    assert [support.href for support in the_row.supports] == [
        f"articles/{first_id}.html#local-article-content-section-1",
        f"articles/{second_id}.html#local-article-content-section-1",
    ]


def test_daily_bpp_digest_requires_two_safe_contributors() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"
    first_article = _article(
        first_id,
        sections=[
            _section(
                "brand_signals",
                _item("The Row", "A valid brand signal.", _reference("The Row", "brand")),
            )
        ],
    )
    second_article = _article(
        second_id,
        sections=[
            _section(
                "product_signals",
                _item("Margaux", "A valid product signal.", _reference("Margaux", "bag")),
            )
        ],
    )

    assert (
        build_row_one_daily_local_brand_product_people_signal_digest(
            _edition([_story(first_id)]),
            {first_id: first_article},
            _hrefs(first_id),
        )
        is None
    )
    assert (
        build_row_one_daily_local_brand_product_people_signal_digest(
            _edition([_story(first_id), _story(second_id)]),
            {first_id: first_article, second_id: second_article},
            {first_id: f"{first_id}.html", second_id: "https://example.com/unsafe.html"},
        )
        is None
    )


def test_daily_bpp_digest_rejects_mismatches_and_unsupported_types() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"
    mismatched_id = "mismatched-signal-3333333333"
    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id), _story(mismatched_id)]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "entities",
                        _item(
                            "The Row",
                            "The Row is a valid saved article signal.",
                            _reference("The Row", "brand"),
                            _reference("Paris Fashion Week", "event"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "product_signals",
                        _item(
                            "Margaux",
                            "Margaux is a valid saved article signal.",
                            _reference("Margaux", "bag"),
                            _reference("Runway", "event"),
                        ),
                    )
                ],
            ),
            mismatched_id: _article(
                "other-signal-4444444444",
                source_name="Untrusted Source",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "Untrusted Brand",
                            "This mismatched sidecar must never contribute.",
                            _reference("Untrusted Brand", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id, mismatched_id),
    )

    assert digest is not None
    assert digest.article_count == 2
    assert digest.source_count == 2
    assert [bucket.key for bucket in digest.buckets] == ["brands", "products"]
    emitted = repr(digest)
    assert "Untrusted Brand" not in emitted
    assert "Paris Fashion Week" not in emitted
    assert "Runway" not in emitted


def test_daily_bpp_digest_dedupes_section_supports_with_language_fallback() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"
    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "",
                            _reference("The Row", "brand"),
                            _reference("the row", "brand"),
                        ),
                        title="",
                        title_zh="品牌信号",
                        body="",
                        body_zh="本地保存证据。",
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "A second article confirms the local brand signal.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    the_row = digest.buckets[0].items[0]
    assert the_row.article_count == 2
    assert len(the_row.supports) == 2
    assert the_row.supports[0].label.en == "品牌信号"
    assert the_row.supports[0].label.zh == "品牌信号"
    assert the_row.supports[0].excerpt.en == "本地保存证据。"
    assert the_row.supports[0].excerpt.zh == "本地保存证据。"
    assert the_row.supports[0].href == (f"articles/{first_id}.html#local-article-content-section-1")


def test_daily_bpp_digest_caps_long_evidence_excerpt_before_tail() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"
    tail = "TAIL-MUST-NOT-APPEAR-IN-EXCERPT"
    long_evidence = ("The Row remains relevant in saved local coverage. " * 8) + tail

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            long_evidence,
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "Khaite",
                            "Khaite contributes a second saved local brand signal.",
                            _reference("Khaite", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    the_row = next(item for item in digest.buckets[0].items if item.name.en == "The Row")
    excerpt = the_row.supports[0].excerpt.en
    assert len(excerpt) == 170
    assert excerpt.startswith(long_evidence[:100])
    assert tail not in excerpt


def test_daily_bpp_digest_uses_second_section_anchor() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "takeaways",
                        _item("Overview", "A saved local overview without entities."),
                    ),
                    _section(
                        "brand_signals",
                        _item(
                            "Khaite",
                            "Khaite is named in the second content section.",
                            _reference("Khaite", "brand"),
                        ),
                    ),
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "Khaite",
                            "A second saved local article confirms Khaite.",
                            _reference("Khaite", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    khaite = digest.buckets[0].items[0]
    assert khaite.supports[0].href == (f"articles/{first_id}.html#local-article-content-section-2")


def test_daily_bpp_digest_dedupes_entities_across_section_items() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "The Row is named in the first saved local item.",
                            _reference("The Row", "brand"),
                        ),
                        _item(
                            "the row",
                            "The normalized entity repeats in another saved local item.",
                            _reference("the row", "brand"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "A second article provides another saved local support.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    the_row = digest.buckets[0].items[0]
    assert [support.href for support in the_row.supports] == [
        f"articles/{first_id}.html#local-article-content-section-1",
        f"articles/{second_id}.html#local-article-content-section-1",
    ]


def test_daily_bpp_digest_dedupes_same_source() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"
    shared_source = "Same Saved Source"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition(
            [
                _story(first_id, source_name=shared_source),
                _story(second_id, source_name=shared_source),
            ]
        ),
        {
            first_id: _article(
                first_id,
                source_name=shared_source,
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "The Row appears in the first eligible article.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name=shared_source,
                sections=[
                    _section(
                        "product_signals",
                        _item(
                            "Margaux",
                            "Margaux appears in the second eligible article.",
                            _reference("Margaux", "bag"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    assert digest.source_count == 1


def test_daily_bpp_digest_counts_distinct_articles() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "The first section identifies The Row.",
                            _reference("The Row", "brand"),
                        ),
                    ),
                    _section(
                        "entities",
                        _item(
                            "The Row",
                            "The second section also identifies The Row.",
                            _reference("The Row", "brand"),
                        ),
                    ),
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "A second article identifies the same brand.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    the_row = digest.buckets[0].items[0]
    assert len(the_row.supports) == 3
    assert the_row.article_count == 2


def test_daily_bpp_digest_caps_items_and_supports_first_seen() -> None:
    stories = [_story(f"cap-signal-{index:010d}") for index in range(4)]
    shared_brand = _reference("Shared Brand", "brand")
    first_id = stories[0].id
    first_references = [
        shared_brand,
        *[_reference(f"Brand {index}", "brand") for index in range(6)],
    ]
    local_articles = {
        first_id: _article(
            first_id,
            sections=[
                _section(
                    "brand_signals",
                    _item(
                        "Brand roster",
                        "The first section fixes the first-seen entity order.",
                        *first_references,
                    ),
                )
            ],
        )
    }
    local_articles.update(
        {
            story.id: _article(
                story.id,
                source_name=f"Source {index}",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "Shared Brand",
                            f"Article {index} adds another factual support.",
                            shared_brand,
                        ),
                    )
                ],
            )
            for index, story in enumerate(stories[1:], start=1)
        }
    )

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition(stories),
        local_articles,
        _hrefs(*(story.id for story in stories)),
    )

    assert digest is not None
    brands = digest.buckets[0].items
    assert len(brands) == DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT
    assert [item.name.en for item in brands] == [
        "Shared Brand",
        "Brand 0",
        "Brand 1",
        "Brand 2",
        "Brand 3",
    ]
    shared = brands[0]
    assert shared.article_count == len(stories)
    assert len(shared.supports) == DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT
    assert [support.href for support in shared.supports] == [
        f"articles/{story.id}.html#local-article-content-section-1"
        for story in stories[:DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT]
    ]


def test_daily_bpp_digest_classifies_labels_and_creative_directors() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "entities",
                        _item(
                            "The Row",
                            "The Row is named as a brand in saved local coverage.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "entities",
                        _item(
                            "The Row and Sarah Burton",
                            "The saved local coverage labels The Row and names Sarah Burton.",
                            _reference("The Row", "product", label="brand"),
                            _reference("Sarah Burton", "creative-director"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None and [
        item.name.en for bucket in digest.buckets if bucket.key == "brands" for item in bucket.items
    ] == ["The Row"]
    assert digest is not None and [
        item.name.en for bucket in digest.buckets if bucket.key == "people" for item in bucket.items
    ] == ["Sarah Burton"]


def test_daily_bpp_digest_uses_canonical_type_from_label() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id), _story(second_id, source_name="WWD")]),
        {
            first_id: _article(
                first_id,
                sections=[
                    _section(
                        "entities",
                        _item(
                            "Khaite",
                            "Khaite is labeled as a brand in saved local coverage.",
                            _reference("Khaite", "product", label="brand"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="WWD",
                sections=[
                    _section(
                        "entities",
                        _item(
                            "Khaite",
                            "A second saved local article also labels Khaite as a brand.",
                            _reference("Khaite", "product", label="brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    brands = next(bucket for bucket in digest.buckets if bucket.key == "brands")
    assert brands.items[0].reference_type == "brand"


def test_daily_bpp_digest_does_not_count_blank_sources() -> None:
    first_id = "first-signal-1111111111"
    second_id = "second-signal-2222222222"

    digest = build_row_one_daily_local_brand_product_people_signal_digest(
        _edition([_story(first_id, source_name=""), _story(second_id, source_name="")]),
        {
            first_id: _article(
                first_id,
                source_name="",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "The first saved local article identifies The Row.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
            second_id: _article(
                second_id,
                source_name="",
                sections=[
                    _section(
                        "brand_signals",
                        _item(
                            "The Row",
                            "The second saved local article identifies The Row.",
                            _reference("The Row", "brand"),
                        ),
                    )
                ],
            ),
        },
        _hrefs(first_id, second_id),
    )

    assert digest is not None
    assert digest.article_count == 2
    assert digest.source_count == 0
    brands = next(bucket for bucket in digest.buckets if bucket.key == "brands")
    assert brands.items[0].source_count == 0
    assert [support.source_name for support in brands.items[0].supports] == [
        "Saved local source",
        "Saved local source",
    ]
