from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.models.report import (
    CandidateReport,
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    empty_daily_brief,
)
from fashion_radar.row_one.edition import build_row_one_edition

AS_OF = datetime(2026, 7, 2, 4, 0, tzinfo=UTC)


def _representative_item(
    title: str,
    *,
    source_name: str = "Vogue Runway",
    source_url: str = "https://example.com/story",
    summary: str | None = "The Row introduced a precise new silhouette.",
) -> RepresentativeItem:
    return RepresentativeItem(
        source_name=source_name,
        source_url=source_url,
        published_at=AS_OF,
        title=title,
        summary=summary,
    )


def _entity(
    name: str,
    entity_type: str,
    *,
    score: float,
    growth_ratio: float | None = 5.0,
    representative_items: list[RepresentativeItem] | None = None,
) -> EntityReport:
    return EntityReport(
        entity_name=name,
        entity_type=entity_type,
        label="hot",
        heat_score=score,
        current_mentions=5,
        baseline_mentions=1,
        distinct_sources=3,
        growth_ratio=growth_ratio,
        representative_items=representative_items or [_representative_item(f"{name} lead")],
    )


def _candidate(
    phrase: str,
    candidate_type: str,
    *,
    score: float,
    representative_items: list[RepresentativeItem] | None = None,
) -> CandidateReport:
    return CandidateReport(
        phrase=phrase,
        candidate_type=candidate_type,
        label="rising",
        score=score,
        current_mentions=4,
        baseline_mentions=0,
        distinct_sources=2,
        growth_ratio=None,
        first_seen_at=AS_OF,
        representative_items=representative_items or [_representative_item(f"{phrase} spotted")],
    )


def _report(
    *,
    entities: list[EntityReport] | None = None,
    candidates: list[CandidateReport] | None = None,
) -> DailyReport:
    return DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=8),
        brief=empty_daily_brief(),
        entities=entities or [],
        candidates=candidates or [],
    )


def _recent_items() -> list[dict[str, object]]:
    return [
        {
            "source_name": "Vogue Business",
            "url": "https://example.com/the-row",
            "title": "The Row sharpens its retail language",
            "summary": "A concise retail update with strong buyer interest.",
            "collected_at": AS_OF.isoformat(),
        },
        {
            "source_name": "WWD",
            "url": "https://example.com/loafer",
            "title": "A low-profile loafer becomes the market signal",
            "summary": "Accessories desks are watching the shoe.",
            "collected_at": AS_OF.isoformat(),
        },
        {
            "source_name": "GQ",
            "url": "https://example.com/celebrity",
            "title": "Zendaya returns to a clean tailoring formula",
            "summary": "The look moved quickly across fashion desks.",
            "collected_at": AS_OF.isoformat(),
        },
    ]


def test_build_row_one_edition_groups_editorial_sections() -> None:
    report = _report(
        entities=[
            _entity("The Row", "brand", score=9.2),
            _entity("Zendaya", "celebrity", score=8.4),
        ],
        candidates=[
            _candidate("market loafer", "shoe", score=7.8),
            _candidate("atelier grey", "unknown", score=6.5),
        ],
    )

    edition = build_row_one_edition(report=report, recent_items=_recent_items(), as_of=AS_OF)

    assert edition.brand == "ROW ONE"
    assert [section.key for section in edition.sections] == [
        "top_stories",
        "brand_moves",
        "celebrity_style",
        "hot_products",
        "rising_radar",
    ]
    assert edition.sections[0].title.zh == "今日重点"
    assert edition.sections[0].title.en == "Top Stories"
    assert edition.section_stories("brand_moves")[0].headline == "The Row lead"
    assert edition.section_stories("celebrity_style")[0].headline == "Zendaya lead"
    assert edition.section_stories("hot_products")[0].headline == "market loafer spotted"
    assert edition.section_stories("rising_radar")[0].headline == "atelier grey spotted"
    story = edition.stories[0]
    assert story.detail_path.startswith("details/")
    assert story.editorial_takeaway.zh
    assert story.editorial_takeaway.en
    assert story.signal_context.zh
    assert story.signal_context.en
    assert story.reader_path.zh
    assert story.reader_path.en


def test_build_row_one_edition_assigns_deterministic_display_metadata() -> None:
    report = _report(
        entities=[
            _entity("The Row", "brand", score=9.2),
            _entity("Zendaya", "celebrity", score=8.4),
        ],
        candidates=[
            _candidate("market loafer", "shoe", score=7.8),
            _candidate("atelier grey", "unknown", score=6.5),
        ],
    )

    edition = build_row_one_edition(report=report, recent_items=_recent_items(), as_of=AS_OF)

    expected_display = {
        "top_stories": ("editorial", "ink"),
        "brand_moves": ("editorial", "graphite"),
        "celebrity_style": ("portrait", "rose"),
        "hot_products": ("product", "cobalt"),
        "rising_radar": ("signal", "steel"),
    }
    for section_key, (variant, accent) in expected_display.items():
        section_stories = edition.section_stories(section_key)
        assert section_stories
        for story in section_stories:
            assert story.display is not None
            assert story.display.variant == variant
            assert story.display.accent == accent
            assert story.display.image is None


def test_build_row_one_edition_uses_collision_safe_detail_paths() -> None:
    duplicate_items = [
        {
            "source_name": "Source A",
            "url": "https://example.com/a",
            "title": "Same Headline",
            "summary": "First summary",
            "collected_at": AS_OF.isoformat(),
        },
        {
            "source_name": "Source B",
            "url": "https://example.com/b",
            "title": "Same Headline",
            "summary": "Second summary",
            "collected_at": AS_OF.isoformat(),
        },
    ]

    edition = build_row_one_edition(report=_report(), recent_items=duplicate_items, as_of=AS_OF)
    paths = [story.detail_path for story in edition.stories]

    assert len(paths) == len(set(paths))
    assert all(path.startswith("details/same-headline-") for path in paths)
    assert all(path.endswith(".html") for path in paths)


def test_build_row_one_edition_backfills_top_stories_after_deduplication() -> None:
    shared_item = _representative_item("Shared lead", source_url="https://example.com/shared")
    report = _report(
        entities=[
            _entity(f"Brand {index}", "brand", score=10 - index, representative_items=[shared_item])
            for index in range(3)
        ],
        candidates=[
            _candidate(f"Shoe {index}", "shoe", score=9 - index, representative_items=[shared_item])
            for index in range(3)
        ],
    )
    recent_items = [
        {
            "source_name": "Recent Desk",
            "url": f"https://example.com/recent-{index}",
            "title": f"Recent signal {index}",
            "summary": "Fresh market signal.",
            "collected_at": AS_OF.isoformat(),
        }
        for index in range(6)
    ]

    top_stories = build_row_one_edition(
        report=report,
        recent_items=recent_items,
        as_of=AS_OF,
    ).section_stories("top_stories")

    assert len(top_stories) == 6
    assert top_stories[0].headline == "Shared lead"
    assert [story.headline for story in top_stories[1:]] == [
        "Recent signal 0",
        "Recent signal 1",
        "Recent signal 2",
        "Recent signal 3",
        "Recent signal 4",
    ]


def test_build_row_one_edition_has_bilingual_fallbacks_and_source_attribution() -> None:
    report = _report(
        entities=[
            _entity(
                "Khaite",
                "brand",
                score=7.2,
                representative_items=[
                    _representative_item(
                        "Khaite expands a soft tailoring story",
                        source_name="Business of Fashion",
                        source_url="https://example.com/khaite",
                        summary=None,
                    )
                ],
            )
        ]
    )

    edition = build_row_one_edition(report=report, recent_items=[], as_of=AS_OF)
    story = edition.section_stories("brand_moves")[0]

    assert story.summary.zh
    assert story.summary.en
    assert "来源摘要" in story.summary.zh
    assert "Original source summary" in story.summary.en
    assert story.source_name == "Business of Fashion"
    assert story.source_url == "https://example.com/khaite"
    assert story.evidence[0].source_name == "Business of Fashion"


def test_build_row_one_edition_adds_entity_synthesis_from_report_fields() -> None:
    entity = _entity("The Row", "brand", score=9.2)

    edition = build_row_one_edition(report=_report(entities=[entity]), recent_items=[], as_of=AS_OF)
    story = edition.section_stories("brand_moves")[0]

    assert "The Row" in story.editorial_takeaway.en
    assert "5 current mentions" in story.signal_context.en
    assert "1 baseline" in story.signal_context.en
    assert "hot" in story.reader_path.en
    assert "品牌动态" in story.reader_path.zh


def test_build_row_one_edition_handles_missing_entity_growth_ratio() -> None:
    entity = _entity("The Row", "brand", score=9.2, growth_ratio=None)

    edition = build_row_one_edition(report=_report(entities=[entity]), recent_items=[], as_of=AS_OF)
    story = edition.section_stories("brand_moves")[0]

    assert "growth ratio is unavailable" in story.signal_context.en
    assert "暂无增长倍数" in story.signal_context.zh
    assert "n/ax" not in story.signal_context.en


def test_build_row_one_edition_adds_candidate_synthesis_from_report_fields() -> None:
    candidate = _candidate("market loafer", "shoe", score=7.8)

    edition = build_row_one_edition(
        report=_report(candidates=[candidate]),
        recent_items=[],
        as_of=AS_OF,
    )
    story = edition.section_stories("hot_products")[0]

    assert "market loafer" in story.editorial_takeaway.en
    assert "4 current mentions" in story.signal_context.en
    assert "0 baseline" in story.signal_context.en
    assert "rising" in story.reader_path.en
    assert "Hot Products" in story.reader_path.en


def test_build_row_one_edition_orders_top_story_ties_by_name() -> None:
    report = _report(
        entities=[
            _entity("Z Brand", "brand", score=9.0),
            _entity("A Brand", "brand", score=9.0),
        ],
        candidates=[
            _candidate("z shoe", "shoe", score=8.0),
            _candidate("a shoe", "shoe", score=8.0),
        ],
    )

    top_stories = build_row_one_edition(
        report=report,
        recent_items=[],
        as_of=AS_OF,
    ).section_stories("top_stories")

    assert [story.headline for story in top_stories] == [
        "A Brand lead",
        "Z Brand lead",
        "a shoe spotted",
        "z shoe spotted",
    ]


def test_build_row_one_edition_orders_casefold_ties_by_original_name() -> None:
    report = _report(
        entities=[
            _entity("a brand", "brand", score=9.0),
            _entity("A Brand", "brand", score=9.0),
        ],
        candidates=[
            _candidate("z shoe", "shoe", score=8.0),
            _candidate("Z shoe", "shoe", score=8.0),
        ],
    )

    top_stories = build_row_one_edition(
        report=report,
        recent_items=[],
        as_of=AS_OF,
    ).section_stories("top_stories")

    assert [story.headline for story in top_stories] == [
        "A Brand lead",
        "a brand lead",
        "Z shoe spotted",
        "z shoe spotted",
    ]


def test_build_row_one_edition_adds_recent_item_synthesis_from_local_item() -> None:
    recent_item = {
        "source_name": "Vogue Business",
        "url": "https://example.com/the-row",
        "title": "The Row sharpens its retail language",
        "summary": "A concise retail update with strong buyer interest.",
        "collected_at": AS_OF.isoformat(),
    }

    edition = build_row_one_edition(report=_report(), recent_items=[recent_item], as_of=AS_OF)
    story = edition.section_stories("top_stories")[0]

    assert "The Row sharpens its retail language" in story.editorial_takeaway.en
    assert "Vogue Business" in story.signal_context.en
    assert "retained local item" in story.signal_context.en
    assert "Vogue Business" in story.reader_path.en


def test_build_row_one_edition_enforces_section_caps() -> None:
    report = _report(
        entities=[
            _entity(f"Brand {index}", "brand", score=10 - (index * 0.1)) for index in range(12)
        ]
    )

    edition = build_row_one_edition(report=report, recent_items=[], as_of=AS_OF)

    assert len(edition.section_stories("brand_moves")) == 8


def test_build_row_one_edition_preserves_all_default_capped_sections() -> None:
    report = _report(
        entities=[
            *[_entity(f"Brand {index}", "brand", score=10 - (index * 0.1)) for index in range(8)],
            *[
                _entity(f"Celebrity {index}", "celebrity", score=9 - (index * 0.1))
                for index in range(8)
            ],
        ],
        candidates=[
            *[_candidate(f"Shoe {index}", "shoe", score=8 - (index * 0.1)) for index in range(8)],
            *[
                _candidate(f"Signal {index}", "unknown", score=7 - (index * 0.1))
                for index in range(8)
            ],
        ],
    )

    edition = build_row_one_edition(report=report, recent_items=[], as_of=AS_OF)

    assert len(edition.section_stories("brand_moves")) == 8
    assert len(edition.section_stories("celebrity_style")) == 8
    assert len(edition.section_stories("hot_products")) == 8
    assert len(edition.section_stories("rising_radar")) == 8


def test_build_row_one_edition_requires_netloc_for_http_urls() -> None:
    report = _report(
        entities=[
            _entity(
                "The Row",
                "brand",
                score=8.0,
                representative_items=[
                    _representative_item(
                        "The Row keeps the original headline",
                        source_url="https:example.com/bad",
                    )
                ],
            )
        ]
    )

    story = build_row_one_edition(report=report, recent_items=[], as_of=AS_OF).stories[0]

    assert story.headline == "The Row keeps the original headline"
    assert story.source_url is None
    assert story.evidence[0].url is None


def test_build_row_one_edition_keeps_chinese_headline_with_ascii_safe_detail_path() -> None:
    edition = build_row_one_edition(
        report=_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/cn",
                "title": "上海新锐设计师品牌升温",
                "summary": "国内设计师品牌热度上升。",
                "collected_at": AS_OF.isoformat(),
            }
        ],
        as_of=AS_OF,
    )

    assert "上海新锐设计师品牌升温" in edition.stories[0].headline
    assert edition.stories[0].detail_path.startswith("details/story-")
    assert edition.stories[0].detail_path.endswith(".html")
    assert edition.stories[0].detail_path.isascii()
    assert "%" not in edition.stories[0].detail_path


def test_build_row_one_edition_bounds_non_latin_detail_path_length() -> None:
    long_title = "上海新锐设计师品牌升温" * 12

    edition = build_row_one_edition(
        report=_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/cn-long",
                "title": long_title,
                "summary": "国内设计师品牌热度上升。",
                "collected_at": AS_OF.isoformat(),
            }
        ],
        as_of=AS_OF,
    )

    basename = edition.stories[0].detail_path.removeprefix("details/")
    assert edition.stories[0].headline == long_title
    assert basename.isascii()
    assert len(basename.encode("utf-8")) < 120


def test_build_row_one_edition_bounds_long_ascii_detail_path_length() -> None:
    long_title = "The Row " + ("very precise retail language " * 12)

    edition = build_row_one_edition(
        report=_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/long-ascii",
                "title": long_title,
                "summary": "Long ASCII title should be bounded.",
                "collected_at": AS_OF.isoformat(),
            }
        ],
        as_of=AS_OF,
    )

    basename = edition.stories[0].detail_path.removeprefix("details/")
    stem = basename.removesuffix(".html")
    slug, digest = stem.rsplit("-", 1)
    assert slug.startswith("the-row-very-precise-retail-language")
    assert len(slug) <= 64
    assert len(digest) == 10
    assert basename.isascii()
    assert len(basename.encode("utf-8")) < 120


def test_build_row_one_edition_omits_non_ascii_from_mixed_detail_path() -> None:
    edition = build_row_one_edition(
        report=_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/mixed",
                "title": "The Row 上海",
                "summary": "The Row signal.",
                "collected_at": AS_OF.isoformat(),
            }
        ],
        as_of=AS_OF,
    )

    detail_path = edition.stories[0].detail_path
    assert detail_path.startswith("details/the-row-")
    assert detail_path.endswith(".html")
    assert detail_path.isascii()
    assert "%" not in detail_path


def test_build_row_one_edition_entity_non_ascii_detail_path_is_ascii_safe() -> None:
    report = _report(
        entities=[
            _entity(
                "The Row",
                "brand",
                score=9.0,
                representative_items=[
                    _representative_item(
                        "上海新锐设计师品牌升温",
                        source_url="https://example.com/entity-cn",
                    )
                ],
            )
        ]
    )

    story = build_row_one_edition(report=report, recent_items=[], as_of=AS_OF).stories[0]

    assert story.headline == "上海新锐设计师品牌升温"
    assert story.detail_path.startswith("details/story-")
    assert story.detail_path.endswith(".html")
    assert story.detail_path.isascii()
    assert "%" not in story.detail_path


def test_build_row_one_edition_candidate_non_ascii_detail_path_is_ascii_safe() -> None:
    report = _report(
        candidates=[
            _candidate(
                "mary jane",
                "shoe",
                score=8.0,
                representative_items=[
                    _representative_item(
                        "Mary Jane 上海热度升温",
                        source_url="https://example.com/candidate-cn",
                    )
                ],
            )
        ]
    )

    story = build_row_one_edition(report=report, recent_items=[], as_of=AS_OF).stories[0]

    assert story.headline == "Mary Jane 上海热度升温"
    assert story.detail_path.startswith("details/mary-jane-")
    assert story.detail_path.endswith(".html")
    assert story.detail_path.isascii()
    assert "%" not in story.detail_path


def test_build_row_one_edition_normalizes_latin_diacritics_in_detail_path() -> None:
    edition = build_row_one_edition(
        report=_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/diacritics",
                "title": "Café déjà vu",
                "summary": "Accent marks should not enter the filename.",
                "collected_at": AS_OF.isoformat(),
            }
        ],
        as_of=AS_OF,
    )

    detail_path = edition.stories[0].detail_path
    assert detail_path.startswith("details/cafe-deja-vu-")
    assert detail_path.endswith(".html")
    assert detail_path.isascii()
    assert "%" not in detail_path


def test_build_row_one_edition_empty_state_keeps_all_sections() -> None:
    edition = build_row_one_edition(report=_report(), recent_items=[], as_of=AS_OF)

    assert edition.brand == "ROW ONE"
    assert len(edition.sections) == 5
    assert edition.stories == []
    assert edition.summary.zh
    assert edition.summary.en
    assert "No ROW ONE stories" in edition.summary.en
    assert "暂无 ROW ONE" in edition.summary.zh
