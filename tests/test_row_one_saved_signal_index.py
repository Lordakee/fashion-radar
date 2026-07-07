from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_signal_index import (
    _strict_valid_saved_signal_paragraph_indices,
    build_row_one_saved_signal_index,
)

AS_OF = datetime(2026, 7, 6, 4, 0, tzinfo=UTC)


def _story(story_id: str, headline: str, *, section_key: str = "top_stories") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        story_type="tracked_entity",
        headline=headline,
        summary=LocalizedText(zh=f"{headline} 摘要", en=f"{headline} summary"),
        why_it_matters=LocalizedText(zh="重要。", en="Important."),
        editorial_takeaway=LocalizedText(zh="编辑判断。", en="Editorial read."),
        signal_context=LocalizedText(zh="信号背景。", en="Signal context."),
        reader_path=LocalizedText(zh="阅读路径。", en="Reader path."),
        source_name="Story Source",
        source_url="https://example.com/story",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="今日摘要。", en="Daily summary."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="重点。", en="Top reads."),
            ),
            RowOneSection(
                key="brand_moves",
                title=LocalizedText(zh="品牌动态", en="Brand Moves"),
                dek=LocalizedText(zh="品牌。", en="Brands."),
            ),
            RowOneSection(
                key="celebrity_style",
                title=LocalizedText(zh="明星穿搭", en="Celebrity Style"),
                dek=LocalizedText(zh="明星。", en="Celebrity looks."),
            ),
            RowOneSection(
                key="hot_products",
                title=LocalizedText(zh="热门单品", en="Hot Products"),
                dek=LocalizedText(zh="单品。", en="Products."),
            ),
            RowOneSection(
                key="rising_radar",
                title=LocalizedText(zh="上升雷达", en="Rising Radar"),
                dek=LocalizedText(zh="上升。", en="Rising signals."),
            ),
        ],
        stories=list(stories),
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh or [],
        content_sections=content_sections or [],
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
        label=LocalizedText(zh=label, en=label),
        body=(
            LocalizedText(
                zh=body_zh if body_zh is not None else body or "",
                en=body or "",
            )
            if body is not None
            else None
        ),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    key: str,
    title: str,
    *,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,
        title=LocalizedText(zh=title, en=title),
        items=items or [],
    )


def _signal_ref(name: str, *, type: str = "brand", label: str = "tracked") -> RowOneReference:
    return RowOneReference(name=name, type=type, label=label)


def test_saved_signal_index_ignores_blank_and_unknown_reference_types() -> None:
    story = _story("allowed-types-1234567890", "Allowed type signal")

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Valid and invalid references appear together."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "References",
                                paragraph_indices=[0],
                                references=[
                                    _signal_ref("Mystery Signal", type="trendlet"),
                                    _signal_ref("Blank Type Signal", type="   "),
                                    _signal_ref("Zendaya", type="celebrity", label="person"),
                                ],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    assert [(entry.name, entry.type) for entry in index.entries] == [("Zendaya", "celebrity")]
    assert index.signal_count == 1
    assert index.supporting_article_count == 1
    assert index.source_count == 1


def test_saved_signal_index_accepts_allowed_reference_types() -> None:
    story = _story("singular-types-1234567890", "Singular type signals")
    refs = [
        _signal_ref("Loewe", type="brand", label="brand"),
        _signal_ref("Jonathan Anderson", type="designer", label="designer"),
        _signal_ref("Zendaya", type="person", label="person"),
        _signal_ref("Margaux", type="product", label="product"),
        _signal_ref("Baguette", type="bag", label="bag"),
        _signal_ref("Tabi", type="shoe", label="shoe"),
        _signal_ref("Sofia Richie", type="celebrity", label="celebrity"),
    ]

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Allowed reference types are saved."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[_item("References", paragraph_indices=[0], references=refs)],
                    )
                ],
            )
        },
    )

    assert index is not None
    assert {entry.name: entry.type for entry in index.entries} == {
        "Loewe": "brand",
        "Jonathan Anderson": "designer",
        "Zendaya": "person",
        "Margaux": "product",
        "Baguette": "bag",
        "Tabi": "shoe",
        "Sofia Richie": "celebrity",
    }


def test_saved_signal_index_canonicalizes_plural_reference_type_aliases() -> None:
    story = _story("plural-types-1234567890", "Plural type signals")
    refs = [
        _signal_ref("Loewe", type="brands", label="brand"),
        _signal_ref("Jonathan Anderson", type="designers", label="designer"),
        _signal_ref("Zendaya", type="people", label="person"),
        _signal_ref("Margaux", type="products", label="product"),
        _signal_ref("Baguette", type="bags", label="bag"),
        _signal_ref("Tabi", type="shoes", label="shoe"),
    ]

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Plural aliases should become canonical singular types."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[_item("References", paragraph_indices=[0], references=refs)],
                    )
                ],
            )
        },
    )

    assert index is not None
    assert {entry.name: entry.type for entry in index.entries} == {
        "Loewe": "brand",
        "Jonathan Anderson": "designer",
        "Zendaya": "person",
        "Margaux": "product",
        "Baguette": "bag",
        "Tabi": "shoe",
    }


def test_saved_signal_index_groups_references_and_builds_support_links() -> None:
    story_a = _story("the-row-a-1234567890", "The Row signal", section_key="top_stories")
    story_b = _story("the-row-b-1234567890", "Second Row signal", section_key="brand_moves")

    index = build_row_one_saved_signal_index(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                source_name="Vogue Business",
                paragraphs=["The Row paragraph.", "Ignored later section paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body="The Row appears in the saved text.",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                            )
                        ],
                    ),
                    _section(
                        "brand_signals",
                        "Later Brand Signals",
                        items=[
                            _item(
                                "The Row later",
                                paragraph_indices=[1],
                                references=[_signal_ref("The Row")],
                            )
                        ],
                    ),
                ],
            ),
            story_b.id: _article(
                story_b.id,
                source_name="WWD",
                paragraphs=["The Row second paragraph."],
                content_sections=[
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _item(
                                "Margaux",
                                body="The Row Margaux is mentioned.",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(
                                        name=" the row ",
                                        type="brand",
                                        label="brand",
                                    ),
                                    RowOneReference(
                                        name="Margaux",
                                        type="product",
                                        label="bag",
                                    ),
                                ],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert index is not None
    assert index.signal_count == 2
    assert index.supporting_article_count == 2
    assert index.source_count == 2
    assert index.supporting_paragraph_count == 3
    assert [entry.name for entry in index.entries] == ["The Row", "Margaux"]
    row_entry = index.entries[0]
    assert row_entry.type == "brand"
    assert row_entry.label == "tracked"
    assert row_entry.article_count == 2
    assert row_entry.source_count == 2
    assert row_entry.supporting_paragraph_count == 2
    assert [support.title.en for support in row_entry.supports] == [
        "The Row signal",
        "Second Row signal",
    ]
    assert row_entry.supports[0].section_title.en == "Top Stories"
    assert row_entry.supports[0].content_section_title.en == "People & Brands"
    assert row_entry.supports[0].section_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert [link.href for link in row_entry.supports[0].paragraph_links] == [
        "details/the-row-a-1234567890.html#local-article-paragraph-1"
    ]
    assert row_entry.supports[0].paragraph_links[0].label.en == "Paragraph 1"


def test_saved_signal_index_filters_unsafe_or_unusable_articles() -> None:
    valid_story = _story("valid-1234567890", "Valid story")
    unsafe_route_story = _story("unsafe-route-1234567890", "Unsafe route").model_copy(
        update={"detail_path": "../outside.html"}
    )
    bad_id_story = _story("bad id", "Bad ID").model_copy(
        update={"detail_path": "details/bad-id-1234567890.html"}
    )
    mismatched_article_story = _story("mismatch-1234567890", "Mismatched article")
    blank_paragraph_story = _story("blank-paragraph-1234567890", "Blank paragraph")
    blank_reference_story = _story("blank-reference-1234567890", "Blank reference")

    edition = _edition(
        valid_story,
        unsafe_route_story,
        bad_id_story,
        mismatched_article_story,
        blank_paragraph_story,
        blank_reference_story,
    )
    unusable_articles = {
        valid_story.id: _article(
            valid_story.id,
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Blank ref",
                            paragraph_indices=[0],
                            references=[_signal_ref("   ")],
                        )
                    ],
                )
            ],
        ),
        unsafe_route_story.id: _article(
            unsafe_route_story.id,
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Unsafe",
                            paragraph_indices=[0],
                            references=[_signal_ref("Unsafe")],
                        )
                    ],
                )
            ],
        ),
        bad_id_story.id: _article(
            bad_id_story.id,
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Bad ID",
                            paragraph_indices=[0],
                            references=[_signal_ref("Bad ID")],
                        )
                    ],
                )
            ],
        ),
        mismatched_article_story.id: _article(
            "other-story-1234567890",
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Mismatch",
                            paragraph_indices=[0],
                            references=[_signal_ref("Mismatch")],
                        )
                    ],
                )
            ],
        ),
        blank_paragraph_story.id: _article(
            blank_paragraph_story.id,
            paragraphs=["   "],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[_item("Blank paragraph", references=[_signal_ref("Blank paragraph")])],
                )
            ],
        ),
        blank_reference_story.id: _article(
            blank_reference_story.id,
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Blank reference",
                            paragraph_indices=[0],
                            references=[_signal_ref(" ")],
                        )
                    ],
                )
            ],
        ),
        "not-in-edition-1234567890": _article(
            "not-in-edition-1234567890",
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Outside",
                            paragraph_indices=[0],
                            references=[_signal_ref("Outside")],
                        )
                    ],
                )
            ],
        ),
    }

    assert build_row_one_saved_signal_index(edition, unusable_articles) is None

    usable_articles = {
        **unusable_articles,
        valid_story.id: _article(
            valid_story.id,
            paragraphs=["Saved."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Valid",
                            paragraph_indices=[0],
                            references=[_signal_ref("Valid")],
                        )
                    ],
                )
            ],
        ),
    }
    index = build_row_one_saved_signal_index(edition, usable_articles)

    assert index is not None
    assert [entry.name for entry in index.entries] == ["Valid"]
    assert index.supporting_article_count == 1
    assert index.source_count == 1


def test_saved_signal_index_filters_invalid_paragraph_indices() -> None:
    story = _story("the-row-a-1234567890", "The Row market signal")
    item = _item(
        "Refs",
        references=[_signal_ref("The Row")],
    ).model_copy(
        update={
            "paragraph_indices": [
                True,
                False,
                -1,
                0,
                1,
                2,
                2,
                99,
            ]
        }
    )

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["First paragraph.", "   ", "Third paragraph."],
                content_sections=[_section("entities", "People & Brands", items=[item])],
            )
        },
    )

    assert index is not None
    assert [link.href for link in index.entries[0].supports[0].paragraph_links] == [
        "details/the-row-a-1234567890.html#local-article-paragraph-1",
        "details/the-row-a-1234567890.html#local-article-paragraph-3",
    ]
    assert index.entries[0].supporting_paragraph_count == 2


def test_saved_signal_index_preserves_section_support_without_valid_paragraph_links() -> None:
    story = _story("section-support-1234567890", "Section-level support")

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Rendered paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "No paragraph links",
                                references=[_signal_ref("The Row", type="brand")],
                            ).model_copy(update={"paragraph_indices": [True, "0", -1, 99]})
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    assert index.supporting_article_count == 1
    assert index.source_count == 1
    assert index.supporting_paragraph_count == 0
    assert index.entries[0].article_count == 1
    assert index.entries[0].source_count == 1
    assert index.entries[0].supporting_paragraph_count == 0
    assert index.entries[0].supports[0].paragraph_links == ()


def test_strict_valid_saved_signal_paragraph_indices_rejects_bool_and_string_values() -> None:
    assert _strict_valid_saved_signal_paragraph_indices(
        [True, False, -1, 0, 0, 1, "2", 2, 99],
        {0, 2},
    ) == (0, 2)


def test_saved_signal_index_keeps_same_name_different_types_separate() -> None:
    story_a = _story("margaux-a-1234567890", "Margaux brand")
    story_b = _story("margaux-b-1234567890", "Margaux product")

    index = build_row_one_saved_signal_index(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                paragraphs=["Margaux brand paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Brand",
                                paragraph_indices=[0],
                                references=[_signal_ref("Margaux", type="brand", label="brand")],
                            )
                        ],
                    )
                ],
            ),
            story_b.id: _article(
                story_b.id,
                paragraphs=["Margaux product paragraph."],
                content_sections=[
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _item(
                                "Product",
                                paragraph_indices=[0],
                                references=[
                                    _signal_ref(" margaux ", type="product", label="bag"),
                                    _signal_ref("MARGAUX", type="brand", label="later label"),
                                ],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert index is not None
    assert [(entry.name, entry.type, entry.label) for entry in index.entries] == [
        ("Margaux", "brand", "brand"),
        ("margaux", "product", "bag"),
    ]
    assert [entry.article_count for entry in index.entries] == [2, 1]
    assert [entry.supporting_paragraph_count for entry in index.entries] == [2, 1]


def test_saved_signal_index_caps_entries_supports_and_paragraph_links() -> None:
    stories = [_story(f"cap-{index}-1234567890", f"Cap Story {index}") for index in range(15)]
    local_articles: dict[str, RowOneLocalArticle] = {}
    for index, story in enumerate(stories):
        references = [_signal_ref("Shared Signal", type="brand", label="tracked")]
        if index == 0:
            references.extend(
                _signal_ref(f"Signal {signal_index:02d}", type="product", label="signal")
                for signal_index in range(13)
            )
        local_articles[story.id] = _article(
            story.id,
            source_name=f"Source {index}",
            paragraphs=[f"Paragraph {paragraph}" for paragraph in range(5)],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Refs",
                            paragraph_indices=[0, 1, 2, 3, 4],
                            references=references,
                        )
                    ],
                )
            ],
        )

    index = build_row_one_saved_signal_index(_edition(*stories), local_articles)

    assert index is not None
    assert index.signal_count == 12
    assert len(index.entries) == 12
    assert index.entries[0].name == "Shared Signal"
    assert index.entries[0].article_count == 15
    assert len(index.entries[0].supports) == 4
    assert len(index.entries[0].supports[0].paragraph_links) == 3


def test_saved_signal_index_caps_entries_after_signal_strength_sorting() -> None:
    early_stories = [
        _story(f"early-{index}-1234567890", f"Early Story {index}") for index in range(13)
    ]
    strong_stories = [
        _story(f"strong-{index}-1234567890", f"Strong Story {index}") for index in range(3)
    ]
    local_articles: dict[str, RowOneLocalArticle] = {}

    for index, story in enumerate(early_stories):
        local_articles[story.id] = _article(
            story.id,
            source_name=f"Early Source {index}",
            paragraphs=["Early paragraph."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "One-off",
                            paragraph_indices=[0],
                            references=[
                                _signal_ref(
                                    f"Early Signal {index:02d}",
                                    type="product",
                                    label="product",
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    for index, story in enumerate(strong_stories):
        local_articles[story.id] = _article(
            story.id,
            source_name=f"Strong Source {index}",
            paragraphs=["Strong first paragraph.", "Strong second paragraph."],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Strong",
                            paragraph_indices=[0, 1],
                            references=[
                                _signal_ref(
                                    "Strong Later Signal",
                                    type="product",
                                    label="product",
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    index = build_row_one_saved_signal_index(
        _edition(*(early_stories + strong_stories)),
        local_articles,
    )

    assert index is not None
    assert index.signal_count == 12
    assert index.entries[0].name == "Strong Later Signal"
    assert index.entries[0].article_count == 3
    assert index.entries[0].source_count == 3
    assert index.entries[0].supporting_paragraph_count == 6
    assert "Strong Later Signal" in {entry.name for entry in index.entries}
    assert "Early Signal 12" not in {entry.name for entry in index.entries}


def test_saved_signal_index_uses_current_edition_and_ignores_extra_local_articles() -> None:
    story = _story("current-1234567890", "Current story")
    extra_story_id = "outside-edition-1234567890"

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["Current paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Current",
                                paragraph_indices=[0],
                                references=[_signal_ref("Current")],
                            )
                        ],
                    )
                ],
            ),
            extra_story_id: _article(
                extra_story_id,
                paragraphs=["Outside paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Outside",
                                paragraph_indices=[0],
                                references=[_signal_ref("Outside")],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert index is not None
    assert [entry.name for entry in index.entries] == ["Current"]
    assert index.supporting_article_count == 1


def test_saved_signal_index_never_derives_hrefs_from_display_strings() -> None:
    story = _story("safe-story-1234567890", "../story#bad-fragment<script>")

    index = build_row_one_saved_signal_index(
        _edition(story),
        {
            story.id: _article(
                story.id,
                title="../title#bad-fragment<script>",
                source_name="../source#bad-fragment<script>",
                paragraphs=["Safe paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "../section#bad-fragment<script>",
                        items=[
                            _item(
                                "../item#bad-fragment<script>",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(
                                        name="../The Row#bad-fragment<script>",
                                        type="brand",
                                        label="../tracked#bad-fragment<script>",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert index is not None
    hrefs = [
        index.entries[0].supports[0].section_path,
        *(link.href for link in index.entries[0].supports[0].paragraph_links),
    ]
    assert hrefs == [
        "details/safe-story-1234567890.html#local-article-content-section-1",
        "details/safe-story-1234567890.html#local-article-paragraph-1",
    ]
    for href in hrefs:
        assert "../" not in href
        assert "#bad-fragment" not in href
        assert "<script>" not in href
