from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.readiness import build_row_one_readiness

AS_OF = datetime(2026, 7, 2, 4, 0, tzinfo=UTC)


def _edition() -> RowOneEdition:
    story = RowOneStory(
        id="the-row-signal-1234567890",
        section_key="top_stories",
        headline="The Row signal",
        summary=LocalizedText(
            zh="来源摘要：The Row signal.",
            en="Original source summary: The Row signal.",
        ),
        why_it_matters=LocalizedText(
            zh="这条信号进入今日重点。",
            en="This signal belongs in Top Stories.",
        ),
        editorial_takeaway=LocalizedText(
            zh="The Row 是今日重点信号。",
            en="The Row is today's priority signal.",
        ),
        signal_context=LocalizedText(
            zh="本地报告显示它来自 1 个来源。",
            en="The local report shows one supporting source.",
        ),
        reader_path=LocalizedText(
            zh="先看摘要，再打开证据链接。",
            en="Read the brief, then open the evidence link.",
        ),
        source_name="Vogue Business",
        source_url="https://example.com/the-row",
        published_at=AS_OF,
        detail_path="details/the-row-signal-1234567890.html",
        evidence=[
            RowOneLink(
                title="Safe evidence",
                url="https://example.com/evidence",
                source_name="Vogue Business",
            ),
            RowOneLink(
                title="Unsafe evidence",
                url="javascript:alert(1)",
                source_name="Bad Source",
            ),
        ],
    )
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(
            zh="ROW ONE 今日整理了 1 条本地时尚信号。",
            en="ROW ONE organized 1 local fashion signal for today.",
        ),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="Read first."),
            ),
            RowOneSection(
                key="brand_moves",
                title=LocalizedText(zh="品牌动态", en="Brand Moves"),
                dek=LocalizedText(
                    zh="品牌、零售与商业动作。",
                    en="Brand and retail context.",
                ),
            ),
        ],
        stories=[story],
    )


def test_build_row_one_readiness_counts_only_safe_evidence_links() -> None:
    readiness = build_row_one_readiness(_edition())

    assert readiness.story_count == 1
    assert readiness.section_count == 2
    assert readiness.safe_evidence_count == 1
    assert readiness.empty_section_keys == ["brand_moves"]
    assert readiness.empty_sections.en == "Brand Moves"
    assert readiness.empty_sections.zh == "品牌动态"
    assert readiness.readiness.en == "ready"
    assert readiness.readiness.zh == "可阅读"
    assert readiness.generated_at == "2026-07-02T04:00:00Z"
    assert readiness.edition_date == "2026-07-02"


def test_build_row_one_readiness_marks_empty_edition() -> None:
    edition = _edition()
    edition.stories = []

    readiness = build_row_one_readiness(edition)

    assert readiness.story_count == 0
    assert readiness.safe_evidence_count == 0
    assert readiness.empty_section_keys == ["top_stories", "brand_moves"]
    assert readiness.empty_sections.en == "Top Stories, Brand Moves"
    assert readiness.empty_sections.zh == "今日重点，品牌动态"
    assert readiness.readiness.en == "empty"
    assert readiness.readiness.zh == "暂无故事"
