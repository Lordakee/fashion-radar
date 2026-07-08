from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import UTC, datetime
from html import escape

import pytest
from pydantic import ValidationError

import fashion_radar.row_one.render as row_one_render
from fashion_radar.row_one.daily_local_key_signals_digest import (
    RowOneDailyLocalKeySignalsDigest,
    RowOneDailyLocalKeySignalsDigestEntry,
    RowOneDailyLocalKeySignalsDigestGroup,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneDailyLocalIntelligenceSegment,
    RowOneDailyLocalIntelligenceSegmentItem,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
    RowOneStoryDisplay,
    RowOneStoryImage,
)
from fashion_radar.row_one.render import (
    _editorial_brief_payload,
    _story_directory_route_payload,
    clean_row_one_site_children,
    render_row_one_site,
)
from fashion_radar.row_one.saved_article_briefs import (
    RowOneSavedArticleBriefItem,
    RowOneSavedArticleBriefs,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_coverage import (
    RowOneSavedArticleCoverage,
    RowOneSavedArticleCoverageItem,
    RowOneSavedArticleCoverageSource,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
    RowOneSavedArticleDailySignalLeaderboardBucket,
    RowOneSavedArticleDailySignalLeaderboardItem,
    RowOneSavedArticleDailySignalLeaderboardSupport,
)
from fashion_radar.row_one.saved_article_evidence_board import (
    RowOneSavedArticleEvidenceBoard,
    RowOneSavedArticleEvidenceBoardCard,
    RowOneSavedArticleEvidenceBoardGroup,
)
from fashion_radar.row_one.saved_article_key_signals import (
    RowOneSavedArticleKeySignalEvidence,
    RowOneSavedArticleKeySignalGroup,
    RowOneSavedArticleKeySignalReference,
    RowOneSavedArticleKeySignals,
    RowOneSavedArticleKeySignalTheme,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibraryParagraphLink,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_article_local_reading_companion import (
    RowOneSavedArticleLocalReadingCompanion,
    RowOneSavedArticleLocalReadingCompanionItem,
    RowOneSavedArticleLocalReadingCompanionLink,
)
from fashion_radar.row_one.saved_article_local_section_binder import (
    RowOneSavedArticleLocalSectionBinder,
    RowOneSavedArticleLocalSectionBinderParagraph,
    RowOneSavedArticleLocalSectionBinderRow,
)
from fashion_radar.row_one.saved_article_organization_jump_index import (
    RowOneSavedArticleOrganizationJumpIndex,
    RowOneSavedArticleOrganizationJumpIndexGroup,
    RowOneSavedArticleOrganizationJumpIndexItem,
)
from fashion_radar.row_one.saved_article_read_next_clusters import (
    RowOneSavedArticleReadNextCluster,
    RowOneSavedArticleReadNextClusterItem,
    RowOneSavedArticleReadNextClusters,
)
from fashion_radar.row_one.saved_article_reading_paths import (
    RowOneSavedArticleReadingPath,
    RowOneSavedArticleReadingPaths,
    RowOneSavedArticleReadingPathStep,
    build_row_one_saved_article_reading_paths,
)
from fashion_radar.row_one.saved_article_reading_queue import (
    RowOneSavedArticleReadingQueue,
    RowOneSavedArticleReadingQueueItem,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    RowOneSavedArticleReferenceAtlas,
    RowOneSavedArticleReferenceAtlasBucket,
    RowOneSavedArticleReferenceAtlasEntry,
    RowOneSavedArticleReferenceAtlasSupport,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacetChip,
    RowOneSavedArticleSignalFacetRow,
    RowOneSavedArticleSignalFacets,
    build_row_one_saved_article_signal_facets,
)
from fashion_radar.row_one.saved_article_theme_digest import (
    RowOneSavedArticleThemeDigest,
    RowOneSavedArticleThemeDigestItem,
    RowOneSavedArticleThemeDigestTheme,
)
from fashion_radar.row_one.saved_signal_index import (
    RowOneSavedSignalIndex,
    RowOneSavedSignalIndexEntry,
    RowOneSavedSignalIndexParagraphLink,
    RowOneSavedSignalIndexSupport,
)
from fashion_radar.row_one.templates import (
    EDITORIAL_BRIEF_BODY_EXCERPT_CHARS,
    _EditorialBrief,
    _EditorialBriefItem,
    _render_saved_signal_index_support_row,
    _safe_daily_local_intelligence_href,
    _strict_valid_local_article_paragraph_indices,
    render_detail_html,
    render_index_html,
    render_local_article_page_html,
    render_saved_article_library_html,
    row_one_css,
)

AS_OF = datetime(2026, 7, 2, 4, 0, tzinfo=UTC)


def _edition() -> RowOneEdition:
    story = RowOneStory(
        id="the-row-signal-1234567890",
        section_key="top_stories",
        story_type="tracked_entity",
        headline='The Row <signals> "quiet" demand',
        summary=LocalizedText(
            zh="来源摘要：The Row signal with <angle> detail.",
            en="Original source summary: The Row signal with <angle> detail.",
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
        tags=["brand", "hot"],
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


def _detail_story(
    story_id: str,
    headline: str,
    *,
    section_key: str = "top_stories",
    summary_en: str | None = None,
    summary_zh: str | None = None,
) -> RowOneStory:
    return (
        _edition()
        .stories[0]
        .model_copy(
            deep=True,
            update={
                "id": story_id,
                "headline": headline,
                "section_key": section_key,
                "summary": LocalizedText(
                    zh=summary_zh if summary_zh is not None else f"{headline} 摘要。",
                    en=summary_en if summary_en is not None else f"{headline} summary.",
                ),
                "detail_path": f"details/{story_id}.html",
            },
        )
    )


def _edition_with_stories(*stories: RowOneStory) -> RowOneEdition:
    edition = _edition()
    edition.stories = list(stories)
    return edition


def _saved_article_library_fixture() -> RowOneSavedArticleLibrary:
    entry = RowOneSavedArticleLibraryEntry(
        title=LocalizedText(zh="The Row source", en="The Row source"),
        source_name="Vogue Business",
        section_title=LocalizedText(zh="今日重点", en="Top Stories"),
        saved_paragraph_count=1,
        organized_section_count=1,
        body_source="summary_fallback",
        digest_path="details/the-row-signal-1234567890.html#local-article-digest",
        reader_path="details/the-row-signal-1234567890.html#local-article-reader",
        evidence_path=("details/the-row-signal-1234567890.html#local-article-paragraph-evidence"),
        paragraph_links=(
            RowOneSavedArticleLibraryParagraphLink(
                label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
            ),
        ),
    )
    return RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=1,
        organized_section_count=1,
        extracted_article_count=0,
        summary_fallback_article_count=1,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=1,
                organized_section_count=1,
                entries=[entry],
            )
        ],
    )


def _signal_briefing_local_article() -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Signal source article",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            "The Row Margaux bag appears in saved source text.",
            "Alaia flats appear in saved source text.",
            "A third saved paragraph carries styling context.",
        ],
        paragraphs_zh=[
            "The Row Margaux 手袋出现在保存正文中。",
            "Alaia 平底鞋出现在保存正文中。",
            "第三个保存段落提供造型背景。",
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="What Happened", zh="发生了什么"),
                body=LocalizedText(
                    en="The saved article frames a new signal.",
                    zh="保存正文呈现了新信号。",
                ),
            ),
            RowOneLocalArticleBriefSection(
                key="why_it_matters",
                title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                body=LocalizedText(
                    en="It changes the read on quiet luxury.",
                    zh="这改变了静奢解读。",
                ),
            ),
            RowOneLocalArticleBriefSection(
                key="signal_context",
                title=LocalizedText(en="Signal Context", zh="信号背景"),
                body=LocalizedText(
                    en="The signal context would normally occupy a third brief slot.",
                    zh="信号背景通常会占用第三个简报位置。",
                ),
            ),
            RowOneLocalArticleBriefSection(
                key="watch_next",
                title=LocalizedText(en="Watch Next", zh="接下来观察"),
                body=LocalizedText(
                    en="Watch what happens next in the saved source.",
                    zh="继续观察保存来源中的后续变化。",
                ),
            ),
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                body=LocalizedText(
                    en="Brand context from saved text.",
                    zh="保存正文中的品牌背景。",
                ),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        body=LocalizedText(
                            en="The Row appears in paragraph one.",
                            zh="The Row 出现在第一段。",
                        ),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0, 1],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(en="Products", zh="单品"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Alaia flats", zh="Alaia 平底鞋"),
                        body=LocalizedText(
                            en="Alaia flats appear in paragraph two.",
                            zh="Alaia 平底鞋出现在第二段。",
                        ),
                        references=[
                            RowOneReference(
                                name="Alaia flats",
                                type="shoe",
                                label="product",
                            ),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )


def _theme_digest_local_article() -> RowOneLocalArticle:
    article = _signal_briefing_local_article()
    return article.model_copy(
        deep=True,
        update={
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="takeaways",
                    title=LocalizedText(en="Read First", zh="优先阅读"),
                    body=LocalizedText(
                        en="Start with the saved The Row signal.",
                        zh="先看保存正文中的 The Row 信号。",
                    ),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="Opening read", zh="入口阅读"),
                            body=LocalizedText(
                                en="Start with The Row retail signal.",
                                zh="先看 The Row 零售信号。",
                            ),
                            references=[
                                RowOneReference(name="The Row", type="brand", label="tracked"),
                            ],
                            paragraph_indices=[0],
                        )
                    ],
                ),
                *article.content_sections,
            ],
        },
    )


def _reference_atlas_local_article() -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Reference atlas source article",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            "The Row appears in paragraph one.",
            "Alaia flats appear in paragraph two.",
            "Retail context appears in paragraph three.",
        ],
        paragraphs_zh=[
            "The Row 出现在第一段。",
            "Alaia 平底鞋出现在第二段。",
            "零售背景出现在第三段。",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="品牌与人物", en="People & Brands"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="The Row", en="The Row"),
                        body=LocalizedText(
                            zh="The Row 是本地正文中的核心品牌信号。",
                            en="The Row is the core brand signal in the local text.",
                        ),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品", en="Products"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Alaia flats", en="Alaia flats"),
                        body=LocalizedText(
                            zh="Alaia 平底鞋是本地正文中的产品信号。",
                            en="Alaia flats are the product signal in the local text.",
                        ),
                        references=[
                            RowOneReference(name="Alaia flats", type="shoe", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="brand_signals",
                title=LocalizedText(zh="市场语境", en="Market Context"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Retail context", en="Retail context"),
                        body=LocalizedText(
                            zh="Dover Street Market 提供来源语境。",
                            en="Dover Street Market provides source context.",
                        ),
                        references=[
                            RowOneReference(
                                name="Dover Street Market",
                                type="retailer",
                                label="market",
                            ),
                        ],
                        paragraph_indices=[2],
                    )
                ],
            ),
        ],
    )


def _evidence_board_local_article() -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Evidence board source article",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            "The Row paragraph one anchors the saved local evidence board.",
            "Alaia flats paragraph two carries a product reference.",
            "Dover Street Market paragraph three is source context.",
        ],
        paragraphs_zh=[
            "The Row 第一段支撑保存文章证据板。",
            "Alaia 平底鞋第二段携带产品引用。",
            "Dover Street Market 第三段提供来源语境。",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="优先阅读", en="Read First"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="入口段落", en="Opening paragraph"),
                        body=LocalizedText(
                            zh="The Row 第一段是证据入口。",
                            en="The Row paragraph one is the evidence opener.",
                        ),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品", en="Products"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Alaia flats", en="Alaia flats"),
                        body=LocalizedText(
                            zh="Alaia 平底鞋第二段是产品证据。",
                            en="Alaia flats paragraph two is product evidence.",
                        ),
                        references=[
                            RowOneReference(name="Alaia flats", type="shoe", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )


def test_render_row_one_detail_includes_local_article_paragraph_evidence_index() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    detail_html = render_detail_html(edition, story, local_article=local_article)

    assert 'id="local-article-paragraph-evidence"' in detail_html
    assert 'class="local-article-paragraph-evidence"' in detail_html
    assert "Saved Paragraph Evidence" in detail_html
    assert "本地段落线索" in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-content-section-1"' in detail_html
    assert "People &amp; Brands" in detail_html
    assert "The Row" in detail_html
    assert detail_html.index('class="local-article-map"') < detail_html.index(
        'id="local-article-paragraph-evidence"'
    )
    map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-paragraph-evidence"'
        )
    ]
    assert 'href="#local-article-paragraph-evidence"' in map_html
    assert detail_html.index('id="local-article-paragraph-evidence"') < detail_html.index(
        'id="local-article-digest"'
    )


def test_render_row_one_detail_omits_local_article_paragraph_evidence_without_matches() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            body=LocalizedText(en="No paragraph mapping", zh="没有段落映射"),
                            references=[],
                            paragraph_indices=[],
                        )
                    ],
                )
            ]
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)

    assert 'id="local-article-paragraph-evidence"' not in detail_html
    assert 'href="#local-article-paragraph-evidence"' not in detail_html


def test_render_row_one_detail_paragraph_evidence_filters_invalid_indices() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": ["First saved paragraph.", "", "Third saved paragraph."],
            "paragraphs_zh": ["第一段。", "", "第三段。"],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            body=LocalizedText(
                                en="Uses filtered mappings",
                                zh="使用过滤映射",
                            ),
                            references=[],
                            paragraph_indices=[-1, 0, 1, 2, 2, 99],
                        )
                    ],
                )
            ],
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert 'href="#local-article-paragraph-1"' in evidence_html
    assert 'href="#local-article-paragraph-3"' in evidence_html
    assert 'href="#local-article-paragraph-0"' not in evidence_html
    assert 'href="#local-article-paragraph-2"' not in evidence_html
    assert 'href="#local-article-paragraph-100"' not in evidence_html
    assert evidence_html.count('class="local-article-paragraph-evidence-row"') == 2
    assert evidence_html.count('href="#local-article-paragraph-3"') == 1


def test_strict_valid_local_article_paragraph_evidence_indices_rejects_bool_values() -> None:
    assert _strict_valid_local_article_paragraph_indices(
        [True, False, 0, 0, 1, "2", 2],
        {0, 2},
    ) == [0, 2]


def test_render_row_one_detail_paragraph_evidence_escapes_values() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": ['<script>alert("p")</script> paragraph'],
            "paragraphs_zh": ['<script>alert("zh")</script> 段落'],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(
                        en="<script>Section</script>",
                        zh="<script>栏目</script>",
                    ),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(
                                en="<script>Label</script>",
                                zh="<script>标签</script>",
                            ),
                            body=LocalizedText(
                                en='<img src=x onerror="alert(1)"> body',
                                zh='<img src=x onerror="alert(2)"> 正文',
                            ),
                            references=[
                                RowOneReference(
                                    name="<script>Ref</script>",
                                    type="brand<script>",
                                    label="hot<script>",
                                )
                            ],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ],
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'class="local-article-reader"'
        )
    ]

    assert "<script>" not in evidence_html
    assert '<img src=x onerror="alert' not in evidence_html
    assert "&lt;script&gt;Section&lt;/script&gt;" in evidence_html
    assert "&lt;script&gt;Label&lt;/script&gt;" in evidence_html
    assert "&lt;script&gt;Ref&lt;/script&gt;" in evidence_html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt; body" in evidence_html


def test_render_row_one_detail_paragraph_evidence_omits_empty_reference_wrapper() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            body=LocalizedText(en="Support without refs", zh="无引用支持"),
                            references=[],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ]
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert 'class="local-article-paragraph-evidence-support"' in evidence_html
    assert "<div></div>" not in evidence_html
    assert 'class="local-article-paragraph-evidence-ref"' not in evidence_html


def test_render_row_one_detail_paragraph_evidence_body_zh_falls_back_to_english() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            body=LocalizedText(en="English <fallback> body.", zh="   "),
                            references=[],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ]
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert '<span data-lang="en">English &lt;fallback&gt; body.</span>' in evidence_html
    assert '<span data-lang="zh">English &lt;fallback&gt; body.</span>' in evidence_html
    assert '<span data-lang="zh"></span>' not in evidence_html
    assert "English <fallback> body." not in evidence_html


def test_render_row_one_detail_paragraph_evidence_caps_rows_items_and_refs() -> None:
    edition = _edition()
    story = edition.stories[0]
    paragraphs = [f"Saved paragraph {index}" for index in range(12)]
    sections = [
        RowOneLocalArticleContentSection(
            key="entities",
            title=LocalizedText(en="People & Brands", zh="品牌与人物"),
            body=None,
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(en=f"Item {item_index}", zh=f"条目 {item_index}"),
                    body=LocalizedText(en=f"Body {item_index}", zh=f"正文 {item_index}"),
                    references=[
                        RowOneReference(name=f"Ref {ref_index}", type="brand", label="hot")
                        for ref_index in range(6)
                    ],
                    paragraph_indices=list(range(12)),
                )
                for item_index in range(6)
            ],
        )
    ]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": paragraphs,
            "paragraphs_zh": [f"保存段落 {index}" for index in range(12)],
            "content_sections": sections,
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'class="local-article-reader"'
        )
    ]

    assert evidence_html.count('class="local-article-paragraph-evidence-row"') == 8
    assert evidence_html.count('class="local-article-paragraph-evidence-support"') == 32
    assert evidence_html.count('class="local-article-paragraph-evidence-ref"') == 128
    assert 'href="#local-article-paragraph-9"' not in evidence_html


def test_render_row_one_site_writes_static_site_files(tmp_path) -> None:
    result = render_row_one_site(_edition(), tmp_path)

    assert result.index_path == tmp_path / "index.html"
    assert result.story_count == 1
    assert (tmp_path / ".row-one-site").read_text(encoding="utf-8").startswith("ROW ONE")
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "details" / "the-row-signal-1234567890.html").exists()
    assert (tmp_path / "assets" / "row-one.css").exists()
    assert (tmp_path / "assets" / "row-one.js").exists()
    assert (tmp_path / "data" / "edition.json").exists()


def test_render_row_one_site_rejects_duplicate_story_ids(tmp_path) -> None:
    edition = _edition()
    duplicate = edition.stories[0].model_copy(deep=True)
    edition.stories = [edition.stories[0], duplicate]

    with pytest.raises(ValueError, match="Duplicate ROW ONE story id"):
        render_row_one_site(edition, tmp_path)

    assert not (tmp_path / ".row-one-site").exists()
    assert not (tmp_path / "details").exists()


def test_render_row_one_site_rejects_duplicate_detail_paths(tmp_path) -> None:
    edition = _edition()
    duplicate = edition.stories[0].model_copy(
        deep=True,
        update={"id": "different-story-2222222222"},
    )
    edition.stories = [edition.stories[0], duplicate]

    with pytest.raises(ValueError, match="Duplicate ROW ONE detail path"):
        render_row_one_site(edition, tmp_path)

    assert not (tmp_path / ".row-one-site").exists()
    assert not (tmp_path / "details").exists()


def test_render_row_one_site_escapes_html_and_omits_unsafe_links(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert '<html lang="en">' in index_html
    assert "ROW ONE" in index_html
    assert 'data-lang-toggle="zh"' in index_html
    assert 'data-lang-toggle="en"' in index_html
    assert 'class="site-shell"' in index_html
    assert 'class="site-header-inner"' in index_html
    assert "Local signals" in index_html
    assert "本地信号" in index_html
    assert 'class="edition-summary-panel"' in index_html
    script = (tmp_path / "assets" / "row-one.js").read_text(encoding="utf-8")
    assert "document.documentElement.lang" in script
    assert "zh-Hans" in script
    assert re.search(r'document\.documentElement\.lang\s*=.*"en"', script)
    assert 'class="edition-rail"' in index_html
    assert 'class="edition-nav-item edition-rail-item"' in index_html
    rail_match = re.search(
        r'<nav class="edition-nav" aria-label="Edition contents">(?P<nav>.*?)</nav>',
        index_html,
        re.S,
    )
    assert rail_match is not None
    rail_html = rail_match.group("nav")
    assert 'class="edition-rail-grid"' in rail_html
    assert 'class="edition-nav-item edition-rail-item"' in rail_html
    assert "Top Stories" in rail_html
    assert "Brand Moves" in rail_html
    assert "1 story" in rail_html
    assert "0 stories" in rail_html
    assert 'class="story-card-header"' in index_html
    assert 'class="story-card-body"' in index_html
    assert 'class="story-card-footer"' in index_html
    assert 'class="story-tag-list"' in index_html
    tag_list_match = re.search(
        r'<p class="story-tag-list">(?P<tags>.*?)</p>',
        index_html,
        re.S,
    )
    assert tag_list_match is not None
    tag_list_html = tag_list_match.group("tags")
    assert "<span>brand</span>" in tag_list_html
    assert "<span>hot</span>" in tag_list_html
    assert 'class="story-takeaway"' in index_html
    orientation_match = re.search(
        r'<p class="story-orientation">(?P<orientation>.*?)</p>',
        index_html,
        re.S,
    )
    assert orientation_match is not None
    orientation_html = orientation_match.group("orientation")
    en_orientation_match = re.search(
        r'<span data-lang="en">(?P<orientation>.*?)</span>',
        orientation_html,
        re.S,
    )
    assert en_orientation_match is not None
    en_orientation_html = en_orientation_match.group("orientation")
    assert "Top Stories" in orientation_html
    assert "Vogue Business" in orientation_html
    assert "Jul 02, 2026" in orientation_html
    assert "2026-07-02" not in en_orientation_html
    assert "1 evidence link" in orientation_html
    assert "1 条线索" in orientation_html
    assert 'class="story-date"' in index_html
    assert '<span data-lang="zh">2026-07-02</span>' in index_html
    assert '<span data-lang="en">1 source</span>' in index_html
    assert '<span data-lang="zh">1 条来源</span>' in index_html
    assert '<span data-lang="en">Read brief</span>' in index_html
    assert '<span data-lang="zh">阅读简报</span>' in index_html
    assert '<p class="story-meta">Vogue Business</p>' not in index_html
    assert "The Row 是今日重点信号。" in index_html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in index_html
    assert "The Row is today&#x27;s priority signal." in index_html
    assert 'href="../index.html#top_stories"' in detail_html
    assert "Back to section" in detail_html
    assert "回到栏目" in detail_html
    detail_panel_match = re.search(
        r'<section class="detail-panel">(?P<panel>.*?)</section>',
        detail_html,
        re.S,
    )
    assert detail_panel_match is not None
    detail_panel = detail_panel_match.group("panel")
    assert '<span data-lang="en">Editorial Takeaway</span>' in detail_panel
    assert '<span data-lang="zh">编辑整理</span>' in detail_panel
    assert '<span data-lang="en">Signal Context</span>' in detail_panel
    assert '<span data-lang="en">Reader Path</span>' in detail_panel
    assert "本地报告显示它来自 1 个来源。" in detail_panel
    assert "先看摘要，再打开证据链接。" in detail_panel
    assert 'class="article-contents"' in detail_html
    contents_match = re.search(
        r'<nav class="article-contents" aria-label="Article contents">(?P<contents>.*?)</nav>',
        detail_html,
        re.S,
    )
    assert contents_match is not None
    contents_html = contents_match.group("contents")
    assert contents_html.index("Summary") < contents_html.index("Why It Matters")
    assert contents_html.index("Why It Matters") < contents_html.index("Editorial Takeaway")
    assert contents_html.index("Editorial Takeaway") < contents_html.index("Signal Context")
    assert contents_html.index("Signal Context") < contents_html.index("Reader Path")
    assert contents_html.index("Reader Path") < contents_html.index("Evidence Trail")
    assert 'href="#summary"' in contents_html
    assert 'href="#why-it-matters"' in contents_html
    assert 'href="#editorial-takeaway"' in contents_html
    assert 'href="#signal-context"' in contents_html
    assert 'href="#reader-path"' in contents_html
    assert 'href="#evidence-trail"' in contents_html
    assert '<span data-lang="en">Evidence Trail</span>' in detail_html
    assert 'class="briefing-topics"' not in detail_html
    assert 'class="edition-brief"' not in detail_html
    assert 'class="daily-edit"' not in detail_html
    assert "Briefing Topics" not in detail_html
    assert "Daily Edit" not in detail_html
    assert "今日编辑简报" not in detail_html
    assert 'class="source-action-link"' in detail_html
    assert '<span data-lang="en">Open Source Article</span>' in detail_html
    assert '<span data-lang="zh">打开原文</span>' in detail_html
    assert 'class="source-action-link" href="https://example.com/the-row"' in detail_html
    assert 'class="evidence-trail"' in detail_html
    assert 'class="evidence-item evidence-item--safe"' in detail_html
    assert 'class="evidence-item evidence-item--retained"' in detail_html
    assert "Retained source row" in detail_html
    assert "保留的来源行" in detail_html
    assert "The local report shows one supporting source." in detail_html
    assert "Read the brief, then open the evidence link." in detail_html
    assert "javascript:alert" not in index_html
    assert "javascript:alert" not in detail_html
    assert "Unsafe evidence" in detail_html
    assert '<a href="https://example.com/evidence"' in detail_html


def test_render_row_one_site_cleans_story_summary_display_without_changing_payload(
    tmp_path,
) -> None:
    edition = _edition()
    edition.stories[0].summary.en = (
        'Original source summary: <a href="https://example.com/story">'
        '<img src="hero.jpg"></a><p><b><webfeedsFeaturedVisual data-x="1">'
        "The Row opened a <angle> private showroom."
        "</webfeedsFeaturedVisual></b></p> "
        "Read the full story here."
    )
    edition.stories[0].summary.zh = (
        '来源摘要：<a href="https://example.com/story">'
        '<img src="hero.jpg"></a><p><b><webfeedsFeaturedVisual data-x="1">'
        "The Row 开设 <angle> 私人展厅。"
        "</webfeedsFeaturedVisual></b></p>阅读全文。点击查看全文。"
    )

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    edition_json = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))

    assert index_html.count("The Row opened a &lt;angle&gt; private showroom.") >= 2
    assert "The Row opened a &lt;angle&gt; private showroom." in detail_html
    assert index_html.count("The Row 开设 &lt;angle&gt; 私人展厅。") >= 2
    assert "The Row 开设 &lt;angle&gt; 私人展厅。" in detail_html
    assert (
        '<meta name="description" content="The Row opened a &lt;angle&gt; private showroom.">'
    ) in detail_html
    assert (
        '<meta property="og:description" '
        'content="The Row opened a &lt;angle&gt; private showroom.">'
    ) in detail_html
    assert (
        '<meta name="twitter:description" '
        'content="The Row opened a &lt;angle&gt; private showroom.">'
    ) in detail_html
    assert "Original source summary" not in index_html
    assert "Original source summary" not in detail_html
    assert "来源摘要" not in index_html
    assert "来源摘要" not in detail_html
    assert "Read the full story here" not in index_html
    assert "Read the full story here" not in detail_html
    assert "webfeedsFeaturedVisual" not in index_html
    assert "webfeedsFeaturedVisual" not in detail_html
    assert "&lt;p" not in index_html
    assert "&lt;p" not in detail_html
    assert "&lt;b" not in index_html
    assert "&lt;b" not in detail_html
    assert "阅读全文" not in index_html
    assert "阅读全文" not in detail_html
    assert "&lt;img" not in index_html
    assert "&lt;img" not in detail_html
    assert "hero.jpg" not in index_html
    assert "hero.jpg" not in detail_html
    assert edition_json["stories"][0]["summary"]["en"].startswith("Original source summary:")
    assert edition_json["stories"][0]["summary"]["zh"].startswith("来源摘要：")


def test_render_row_one_detail_includes_information_map(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'class="detail-information-map"' in detail_html
    assert "Detail Information Map" in detail_html
    assert "详情信息地图" in detail_html
    assert "Story Context" in detail_html
    assert "Signal Shape" in detail_html
    assert "Evidence" in detail_html
    assert "Read Order" in detail_html
    assert "Top Stories" in detail_html
    assert "Vogue Business" in detail_html
    assert "Jul 02, 2026" in detail_html
    assert "2026-07-02" in detail_html
    assert "1 evidence link" in detail_html
    assert "brand, hot" in detail_html
    assert 'href="#summary"' in detail_html
    assert 'href="#why-it-matters"' in detail_html
    assert 'href="#signal-context"' in detail_html
    assert 'href="#evidence-trail"' in detail_html
    assert detail_html.index('class="article-contents"') < detail_html.index(
        'class="detail-information-map"'
    )
    assert detail_html.index('class="detail-information-map"') < detail_html.index('id="summary"')


def test_render_row_one_detail_includes_local_article_content(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            "First local paragraph about The Row demand.",
            "Second local paragraph with styling context.",
        ],
        paragraphs_zh=[
            "第一段本地正文，关于 The Row 需求。",
            "第二段本地正文，补充造型语境。",
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="What Happened", zh="发生了什么"),
                body=LocalizedText(
                    en="The Row demand moved this week.",
                    zh="The Row 需求本周升温。",
                ),
            ),
            RowOneLocalArticleBriefSection(
                key="why_it_matters",
                title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                body=LocalizedText(
                    en="It changes how buyers read quiet luxury.",
                    zh="这会改变买手理解静奢的方式。",
                ),
            ),
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                body=LocalizedText(en="Saved source reads.", zh="本地来源要点。"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(
                            en="The Row demand moved.",
                            zh="The Row 需求变化。",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="Entities", zh="相关对象"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        body=LocalizedText(
                            en="Source-backed reference excerpt for The Row demand.",
                            zh="The Row 需求的来源摘录。",
                        ),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    article_json = json.loads(
        (tmp_path / "data" / "articles" / "the-row-signal-1234567890.json").read_text(
            encoding="utf-8"
        )
    )
    edition_json = (tmp_path / "data" / "edition.json").read_text(encoding="utf-8")

    assert 'id="local-article"' in detail_html
    assert '<span data-lang="en">Local Article</span>' in detail_html
    assert '<span data-lang="zh">本地正文</span>' in detail_html
    assert "Saved from Vogue Business" in detail_html
    assert "本地保存自 Vogue Business" in detail_html
    assert 'class="local-article-provenance"' in detail_html
    assert '<span data-lang="en">Source</span>' in detail_html
    assert '<span data-lang="zh">来源</span>' in detail_html
    assert '<span class="local-article-provenance-value">Vogue Business</span>' in detail_html
    assert '<span data-lang="en">Saved</span>' in detail_html
    assert '<span data-lang="zh">保存时间</span>' in detail_html
    assert '<span data-lang="en">Published</span>' in detail_html
    assert '<span data-lang="zh">发布时间</span>' in detail_html
    assert '<span data-lang="en">Saved paragraphs</span>' in detail_html
    assert '<span data-lang="zh">保存段落</span>' in detail_html
    assert '<span data-lang="en">Organized sections</span>' in detail_html
    assert '<span data-lang="zh">整理栏目</span>' in detail_html
    assert '<span class="local-article-provenance-value">2</span>' in detail_html
    assert "First local paragraph about The Row demand." in detail_html
    assert "Second local paragraph with styling context." in detail_html
    assert 'id="local-article-paragraph-1"' in detail_html
    assert 'id="local-article-paragraph-2"' in detail_html
    assert 'class="local-article-map"' in detail_html
    assert 'aria-label="ROW ONE local article map"' in detail_html
    assert 'href="#local-article-brief"' in detail_html
    assert 'href="#local-article-content-section-1"' in detail_html
    assert 'href="#local-article-content-section-2"' in detail_html
    assert 'href="#local-article-body"' in detail_html
    assert 'id="local-article-brief"' in detail_html
    assert 'id="local-article-content-section-1"' in detail_html
    assert 'id="local-article-content-section-2"' in detail_html
    assert 'id="local-article-body"' in detail_html
    assert '<span data-lang="en">Brief</span>' in detail_html
    assert '<span data-lang="zh">本地简报</span>' in detail_html
    assert 'id="local-article-reader"' in detail_html
    local_article_map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'class="local-article-brief"'
        )
    ]
    body_html = detail_html[detail_html.index('id="local-article-body"') :]
    assert 'class="local-article-reader"' in detail_html
    assert '<span data-lang="en">Saved Text Reader</span>' in reader_html
    assert '<span data-lang="zh">保存正文阅读</span>' in reader_html
    assert "2 saved paragraphs from Vogue Business" in reader_html
    assert "来自 Vogue Business 的 2 个保存段落" in reader_html
    assert 'class="local-article-reader-list"' in reader_html
    assert 'aria-label="Saved text paragraphs"' in reader_html
    assert 'href="#local-article-reader"' in local_article_map_html
    assert '<span data-lang="en">Reader</span>' in local_article_map_html
    assert '<span data-lang="zh">阅读</span>' in local_article_map_html
    assert 'href="#local-article-paragraph-1"' in reader_html
    assert 'href="#local-article-paragraph-2"' in reader_html
    assert '<span class="local-article-reader-number">01</span>' in reader_html
    assert '<span class="local-article-reader-number">02</span>' in reader_html
    assert '<span data-lang="en">First local paragraph about The Row demand.</span>' in reader_html
    assert '<span data-lang="zh">第一段本地正文，关于 The Row 需求。</span>' in reader_html
    assert '<span data-lang="en">Saved text</span>' in local_article_map_html
    assert '<span data-lang="zh">保存正文</span>' in local_article_map_html
    assert "Full saved text" not in detail_html
    assert "完整保存正文" not in detail_html
    assert re.search(
        r'<a href="#local-article-content-section-1">\s*'
        r'<span data-lang="en">Takeaways</span>\s*'
        r'<span data-lang="zh">要点</span>\s*</a>',
        local_article_map_html,
    )
    assert re.search(
        r'<a href="#local-article-content-section-2">\s*'
        r'<span data-lang="en">Entities</span>\s*'
        r'<span data-lang="zh">相关对象</span>\s*</a>',
        local_article_map_html,
    )
    assert 'class="local-article-brief"' in detail_html
    assert '<span data-lang="en">What Happened</span>' in detail_html
    assert '<span data-lang="zh">发生了什么</span>' in detail_html
    assert '<span data-lang="en">The Row demand moved this week.</span>' in detail_html
    assert '<span data-lang="zh">The Row 需求本周升温。</span>' in detail_html
    assert 'class="local-article-content-sections"' in detail_html
    assert '<span data-lang="en">Takeaways</span>' in detail_html
    assert '<span data-lang="zh">要点</span>' in detail_html
    assert '<span data-lang="en">Source lead</span>' in detail_html
    assert '<span data-lang="zh">来源导语</span>' in detail_html
    assert '<span data-lang="en">The Row demand moved.</span>' in detail_html
    assert '<span data-lang="zh">The Row 需求变化。</span>' in detail_html
    assert "Paragraph 1" in detail_html
    assert "段落 1" in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert re.search(
        r'<a href="#local-article-paragraph-1">\s*Paragraph 1\s*</a>',
        detail_html,
    )
    assert re.search(
        r'<a href="#local-article-paragraph-1">\s*段落 1\s*</a>',
        detail_html,
    )
    assert "Refs: The Row (brand / tracked)" in detail_html
    assert "引用：The Row（brand / tracked）" in detail_html
    content_sections_html = detail_html[
        detail_html.index('class="local-article-content-sections"') : detail_html.index(
            'class="local-article-body"'
        )
    ]
    assert (
        '<span data-lang="en">Source-backed reference excerpt for The Row demand.</span>'
        in content_sections_html
    )
    assert '<span data-lang="zh">The Row 需求的来源摘录。</span>' in content_sections_html
    assert detail_html.index('class="local-article-map"') < detail_html.index(
        'id="local-article-digest"'
    )
    assert detail_html.index('id="local-article-digest"') < detail_html.index(
        'id="local-article-reader"'
    )
    assert detail_html.index('href="#local-article-brief"') < detail_html.index(
        'href="#local-article-digest"'
    )
    assert detail_html.index('href="#local-article-digest"') < detail_html.index(
        'href="#local-article-reader"'
    )
    assert detail_html.index('href="#local-article-reader"') < detail_html.index(
        'href="#local-article-content-section-1"'
    )
    assert detail_html.index('id="local-article-reader"') < detail_html.index(
        'class="local-article-brief"'
    )
    assert detail_html.index('id="local-article-reader"') < detail_html.index(
        'id="local-article-body"'
    )
    assert detail_html.index('href="#local-article-content-section-1"') < detail_html.index(
        'id="local-article-content-section-1"'
    )
    assert detail_html.index('class="local-article-brief"') < detail_html.index(
        'class="local-article-content-sections"'
    )
    assert detail_html.index('class="local-article-content-sections"') < detail_html.index(
        'class="local-article-body"'
    )
    assert '<span data-lang="en">First local paragraph about The Row demand.</span>' in body_html
    assert '<span data-lang="zh">第一段本地正文，关于 The Row 需求。</span>' in body_html
    assert detail_html.index('href="#local-article-paragraph-1"') < detail_html.index(
        'id="local-article-paragraph-1"'
    )
    assert body_html.index('data-lang="en">First local paragraph') < body_html.index(
        'data-lang="zh">第一段本地正文'
    )
    assert 'href="#local-article"' in detail_html
    contents_match = re.search(
        r'<nav class="article-contents" aria-label="Article contents">(?P<contents>.*?)</nav>',
        detail_html,
        re.S,
    )
    assert contents_match is not None
    contents_html = contents_match.group("contents")
    assert contents_html.index('href="#summary"') < contents_html.index('href="#local-article"')
    assert contents_html.index('href="#local-article"') < contents_html.index(
        'href="#why-it-matters"'
    )
    assert detail_html.index('id="summary"') < detail_html.index('id="local-article"')
    assert detail_html.index('id="local-article"') < detail_html.index('id="why-it-matters"')
    assert article_json["story_id"] == "the-row-signal-1234567890"
    assert article_json["paragraphs"] == [
        "First local paragraph about The Row demand.",
        "Second local paragraph with styling context.",
    ]
    assert article_json["paragraphs_zh"] == [
        "第一段本地正文，关于 The Row 需求。",
        "第二段本地正文，补充造型语境。",
    ]
    assert [section["key"] for section in article_json["brief_sections"]] == [
        "what_happened",
        "why_it_matters",
    ]
    assert [section["key"] for section in article_json["content_sections"]] == [
        "takeaways",
        "entities",
    ]
    assert article_json["content_sections"][1]["items"][0]["references"] == [
        {"name": "The Row", "type": "brand", "label": "tracked"}
    ]
    assert article_json["content_sections"][1]["items"][0]["body"] == {
        "en": "Source-backed reference excerpt for The Row demand.",
        "zh": "The Row 需求的来源摘录。",
    }
    assert "The Row demand moved." not in edition_json
    assert "First local paragraph about The Row demand." not in edition_json
    assert "local-article-reader" not in edition_json


def test_render_row_one_detail_local_article_provenance_uses_article_source(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.source_name = "Story Feed"
    story.source_url = "https://example.com/story-feed"
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="Article source title",
        url="https://example.com/local-article",
        source_name="Article Desk",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=["One saved local paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    local_article_html = detail_html[
        detail_html.index('id="local-article"') : detail_html.index('id="why-it-matters"')
    ]

    assert "Article source title" in local_article_html
    assert "Article Desk" in local_article_html
    assert "Story Feed" not in local_article_html
    assert 'href="https://example.com/local-article"' in local_article_html
    assert 'href="https://example.com/story-feed"' not in local_article_html
    assert 'target="_blank" rel="noopener"' in local_article_html
    assert "Jul 02, 2026" in local_article_html
    assert '<span data-lang="en">Saved paragraphs</span>' in local_article_html
    assert '<span data-lang="zh">保存段落</span>' in local_article_html
    assert '<span data-lang="en">Organized sections</span>' in local_article_html
    assert '<span data-lang="zh">整理栏目</span>' in local_article_html
    assert '<span data-lang="en">Text source</span>' in local_article_html
    assert '<span data-lang="zh">正文来源</span>' in local_article_html
    assert "Extracted article text" in local_article_html


def test_render_row_one_detail_local_article_renders_body_source_and_reason(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row signal",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        body_source="summary_fallback",
        reason="robots_disallowed",
        paragraphs=["Summary fallback paragraph."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    local_article_html = detail_html[
        detail_html.index('id="local-article"') : detail_html.index('id="why-it-matters"')
    ]

    assert '<span data-lang="en">Text source</span>' in local_article_html
    assert '<span data-lang="zh">正文来源</span>' in local_article_html
    assert "ROW ONE summary fallback" in local_article_html
    assert '<span data-lang="en">Fallback reason</span>' in local_article_html
    assert '<span data-lang="zh">兜底原因</span>' in local_article_html
    assert "robots_disallowed" in local_article_html


def test_render_row_one_detail_suppresses_skipped_local_article(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row signal",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        body_source="skipped",
        skipped=True,
        reason="no_publishable_paragraphs",
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="local-article"' not in detail_html
    assert "no_publishable_paragraphs" not in detail_html


def test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph.", "Second source paragraph."],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert '<p id="local-article-paragraph-1">One source paragraph.</p>' in detail_html
    assert '<p id="local-article-paragraph-2">Second source paragraph.</p>' in detail_html
    assert 'data-lang="zh">One source paragraph.' not in detail_html
    assert 'class="local-article-brief"' not in detail_html
    assert 'class="local-article-content-sections"' not in detail_html
    assert 'class="local-article-map"' not in detail_html
    assert 'id="local-article-body"' in detail_html
    assert 'href="#local-article"' in detail_html


def test_render_row_one_detail_plain_local_article_gets_reader_without_map(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Plain source article",
        url="https://example.com/plain",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First saved source paragraph for the local reader.",
            "Second saved source paragraph for the local reader.",
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="local-article-reader"' in detail_html
    assert "2 saved paragraphs from Fashion Desk" in detail_html
    assert 'class="local-article-reader-list"' in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-paragraph-2"' in detail_html
    assert 'class="local-article-map"' not in detail_html
    assert (
        '<p id="local-article-paragraph-1">First saved source paragraph for the local reader.</p>'
    ) in detail_html
    assert (
        '<p id="local-article-paragraph-2">Second saved source paragraph for the local reader.</p>'
    ) in detail_html


def test_render_row_one_detail_reader_uses_singular_paragraph_meta(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Single paragraph article",
        url="https://example.com/single",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=["One saved source paragraph for the reader."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "1 saved paragraph from Fashion Desk" in detail_html
    assert "1 saved paragraphs from Fashion Desk" not in detail_html


def test_render_row_one_detail_reader_falls_back_when_aligned_zh_excerpt_is_blank(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Aligned blank zh article",
        url="https://example.com/aligned",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First aligned paragraph for the reader.",
            "Second aligned paragraph falls back when zh is blank.",
        ],
        paragraphs_zh=[
            "第一段用于阅读器。",
            "   ",
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert '<span data-lang="zh">第一段用于阅读器。</span>' in reader_html
    assert (
        '<span data-lang="zh">Second aligned paragraph falls back when zh is blank.</span>'
        in reader_html
    )


def test_render_row_one_detail_reader_uses_plain_excerpt_when_zh_paragraphs_mismatch(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Mismatched zh article",
        url="https://example.com/mismatch",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First source paragraph uses plain reader output.",
            "Second source paragraph also uses plain reader output.",
        ],
        paragraphs_zh=["只有一个中文段落。"],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert "First source paragraph uses plain reader output." in reader_html
    assert "Second source paragraph also uses plain reader output." in reader_html
    assert 'data-lang="zh">只有一个中文段落。' not in reader_html
    assert 'data-lang="en">First source paragraph uses plain reader output.' not in reader_html


def test_render_row_one_detail_reader_skips_blank_escapes_and_truncates(
    tmp_path,
) -> None:
    edition = _edition()
    long_text = (
        "The Row paragraph includes <script>alert('x')</script> and a very long "
        "source sentence that should be shortened inside the reader index while "
        "the existing saved text remains available through the paragraph anchor."
    )
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Escaped reader article",
        url="https://example.com/escaped",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[long_text, "   ", "Final concise paragraph."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'id="local-article-body"'
        )
    ]
    body_html = detail_html[detail_html.index('id="local-article-body"') :]

    assert "local-article-paragraph-2" not in reader_html
    assert 'href="#local-article-paragraph-1"' in reader_html
    assert 'href="#local-article-paragraph-3"' in reader_html
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in reader_html
    assert "<script>alert" not in reader_html
    assert "paragraph anchor." not in reader_html
    assert "…" in reader_html
    assert 'id="local-article-paragraph-1"' in body_html
    assert "paragraph anchor." in body_html
    assert '<p id="local-article-paragraph-3">Final concise paragraph.</p>' in detail_html


def test_render_row_one_detail_reader_keeps_app_contract_stable(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Contract stable article",
        url="https://example.com/contract",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Reader-only local paragraph for contract stability."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    edition_json = json.dumps(edition_payload, ensure_ascii=False)

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    assert "Reader-only local paragraph for contract stability." not in edition_json
    assert "local-article-reader" not in edition_json


def test_render_row_one_detail_includes_saved_text_digest_from_content_sections(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Structured digest source",
        url="https://example.com/digest",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row demand moved through the saved source paragraph.",
            "Zendaya styled the Margaux bag in the second saved paragraph.",
        ],
        paragraphs_zh=[
            "The Row 需求出现在保存正文第一段。",
            "Zendaya 在第二段中搭配 Margaux 包袋。",
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="What Happened", zh="发生了什么"),
                body=LocalizedText(en="Digest brief.", zh="整理简报。"),
            )
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(
                            en="Zendaya styled the Margaux bag in the second saved paragraph.",
                            zh="Zendaya 在第二段中搭配 Margaux 包袋。",
                        ),
                        paragraph_indices=[1],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="Entities", zh="相关对象"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0],
                    ),
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Zendaya", zh="Zendaya"),
                        references=[
                            RowOneReference(name="Zendaya", type="celebrity", label="new"),
                        ],
                        paragraph_indices=[1],
                    ),
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(en="Product Signals", zh="产品信号"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Margaux", zh="Margaux"),
                        references=[
                            RowOneReference(name="Margaux", type="bag", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    edition_json = (tmp_path / "data" / "edition.json").read_text(encoding="utf-8")
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]
    map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]
    people_html = digest_html[
        digest_html.index('<span data-lang="en">People &amp; Brands</span>') : digest_html.index(
            '<span data-lang="en">Products</span>'
        )
    ]
    products_html = digest_html[
        digest_html.index('<span data-lang="en">Products</span>') : digest_html.index(
            '<span data-lang="en">Source Map</span>'
        )
    ]
    source_map_html = digest_html[digest_html.index('<span data-lang="en">Source Map</span>') :]

    assert 'class="local-article-digest"' in digest_html
    assert 'aria-label="Saved text digest"' in digest_html
    assert '<span data-lang="en">Saved Text Digest</span>' in digest_html
    assert '<span data-lang="zh">保存正文整理</span>' in digest_html
    assert '<span data-lang="en">Read First</span>' in digest_html
    assert '<span data-lang="zh">先读</span>' in digest_html
    assert "Zendaya styled the Margaux bag in the second saved paragraph." in digest_html
    assert "Zendaya 在第二段中搭配 Margaux 包袋。" in digest_html
    assert 'href="#local-article-paragraph-2"' in digest_html
    assert '<span data-lang="en">People &amp; Brands</span>' in digest_html
    assert '<span data-lang="zh">品牌与人物</span>' in digest_html
    assert people_html.count('class="local-article-digest-chip"') == 2
    assert ">The Row<" in people_html
    assert ">Zendaya<" in people_html
    assert '<span data-lang="en">Products</span>' in digest_html
    assert '<span data-lang="zh">产品</span>' in digest_html
    assert products_html.count('class="local-article-digest-chip"') == 1
    assert ">Margaux<" in products_html
    assert '<span data-lang="en">Source Map</span>' in digest_html
    assert '<span data-lang="zh">来源结构</span>' in digest_html
    assert "Vogue Business" in source_map_html
    assert '<span data-lang="en">2 saved paragraphs</span>' in source_map_html
    assert '<span data-lang="zh">2 个保存段落</span>' in source_map_html
    assert '<span data-lang="en">3 organized sections</span>' in source_map_html
    assert '<span data-lang="zh">3 个整理栏目</span>' in source_map_html
    assert 'href="#local-article-digest"' in map_html
    assert '<span data-lang="en">Digest</span>' in map_html
    assert '<span data-lang="zh">整理</span>' in map_html
    assert 'id="local-article-digest"' not in map_html
    assert 'class="local-article-digest"' not in map_html
    assert 'class="local-article-reader"' not in map_html
    assert detail_html.index('href="#local-article-brief"') < detail_html.index(
        'href="#local-article-digest"'
    )
    assert detail_html.index('href="#local-article-digest"') < detail_html.index(
        'href="#local-article-reader"'
    )
    assert detail_html.index('id="local-article-digest"') < detail_html.index(
        'id="local-article-reader"'
    )
    assert detail_html.index('id="local-article-digest"') < detail_html.index(
        'id="local-article-brief"'
    )
    assert "local-article-digest" not in edition_json


def test_render_row_one_detail_plain_local_article_gets_digest_without_map(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Plain digest source",
        url="https://example.com/plain-digest",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "First saved source paragraph becomes the digest fallback.",
            "Second saved source paragraph stays in the saved text reader.",
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]

    assert 'id="local-article-digest"' in detail_html
    assert "First saved source paragraph becomes the digest fallback." in digest_html
    assert 'href="#local-article-paragraph-1"' in digest_html
    assert "Fashion Desk" in digest_html
    assert "2 saved paragraphs" in digest_html
    assert "0 organized sections" in digest_html
    assert 'class="local-article-map"' not in detail_html


def test_render_row_one_detail_digest_escapes_dedupes_filters_and_truncates(
    tmp_path,
) -> None:
    edition = _edition()
    long_text = (
        "The Row paragraph includes <script>alert('x')</script> and a very long "
        "saved source sentence that should be shortened inside the digest card "
        "while the complete saved text remains available through its anchor."
    )
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Escaped digest source",
        url="https://example.com/escaped-digest",
        source_name="Vogue <Business>",
        extracted_at=AS_OF,
        paragraphs=[long_text, "   ", "Final saved paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Unsafe", zh="不安全"),
                        body=LocalizedText(en=long_text, zh=long_text),
                        paragraph_indices=[0, 1, 99],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="Entities", zh="相关对象"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(
                                name="<script>Brand</script>",
                                type="brand",
                                label="unsafe",
                            ),
                        ],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]
    reference_html = digest_html[
        digest_html.index('<span data-lang="en">People &amp; Brands</span>') : digest_html.index(
            '<span data-lang="en">Source Map</span>'
        )
    ]
    body_html = detail_html[detail_html.index('id="local-article-body"') :]

    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in digest_html
    assert "&lt;script&gt;Brand&lt;/script&gt;" in digest_html
    assert "<script>" not in digest_html
    assert reference_html.count('class="local-article-digest-chip"') == 2
    assert reference_html.count(">The Row<") == 1
    assert 'href="#local-article-paragraph-1"' in digest_html
    assert 'href="#local-article-paragraph-2"' not in digest_html
    assert 'href="#local-article-paragraph-100"' not in digest_html
    assert "2 saved paragraphs" in digest_html
    assert "3 saved paragraphs" not in digest_html
    assert "complete saved text remains available" not in digest_html
    assert "…" in digest_html
    assert "complete saved text remains available" in body_html


def test_render_row_one_detail_digest_keeps_app_contract_stable(tmp_path) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Contract digest source",
        url="https://example.com/contract-digest",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Digest-only local paragraph for contract stability."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    edition_json = json.dumps(edition_payload, ensure_ascii=False)

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    assert "Digest-only local paragraph for contract stability." not in edition_json
    assert "local-article-digest" not in edition_json


def test_render_row_one_detail_digest_keeps_takeaway_body_without_valid_links(
    tmp_path,
) -> None:
    edition = _edition()
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Invalid link digest source",
        url="https://example.com/invalid-link-digest",
        source_name="Fashion Desk",
        extracted_at=AS_OF,
        paragraphs=["Only publishable saved paragraph.", "   "],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(
                            en="Use this organized takeaway even without valid paragraph links.",
                            zh="即使没有有效段落链接，也使用这条整理要点。",
                        ),
                        paragraph_indices=[1, 99],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    digest_html = detail_html[
        detail_html.index('id="local-article-digest"') : detail_html.index(
            'id="local-article-reader"'
        )
    ]

    assert "Use this organized takeaway even without valid paragraph links." in digest_html
    assert "即使没有有效段落链接，也使用这条整理要点。" in digest_html
    assert 'href="#local-article-paragraph-2"' not in digest_html
    assert 'href="#local-article-paragraph-100"' not in digest_html
    assert "1 saved paragraph" in digest_html


def test_render_row_one_detail_map_handles_brief_only_local_article(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph."],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="What Happened", zh="发生了什么"),
                body=LocalizedText(en="Brief only.", zh="只有简报。"),
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    local_article_map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert 'href="#local-article-brief"' in local_article_map_html
    assert 'href="#local-article-digest"' in local_article_map_html
    assert 'href="#local-article-reader"' in local_article_map_html
    assert '<span data-lang="en">Digest</span>' in local_article_map_html
    assert '<span data-lang="zh">整理</span>' in local_article_map_html
    assert '<span data-lang="en">Reader</span>' in local_article_map_html
    assert '<span data-lang="zh">阅读</span>' in local_article_map_html
    assert 'href="#local-article-body"' in local_article_map_html
    assert local_article_map_html.index('href="#local-article-brief"') < (
        local_article_map_html.index('href="#local-article-digest"')
    )
    assert local_article_map_html.index('href="#local-article-digest"') < (
        local_article_map_html.index('href="#local-article-reader"')
    )
    assert local_article_map_html.index('href="#local-article-reader"') < (
        local_article_map_html.index('href="#local-article-body"')
    )
    assert "#local-article-content-section-" not in local_article_map_html
    assert 'id="local-article-brief"' in detail_html
    assert 'id="local-article-reader"' in detail_html
    assert 'id="local-article-body"' in detail_html


def test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph.", "Second source paragraph."],
        paragraphs_zh=["一段中文。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(en="Structured English.", zh="结构化中文。"),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    local_article_map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert '<p id="local-article-paragraph-1">One source paragraph.</p>' in detail_html
    assert '<p id="local-article-paragraph-2">Second source paragraph.</p>' in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-digest"' in local_article_map_html
    assert 'href="#local-article-reader"' in local_article_map_html
    assert local_article_map_html.index('href="#local-article-digest"') < (
        local_article_map_html.index('href="#local-article-reader"')
    )
    assert '<span data-lang="en">Reader</span>' in local_article_map_html
    assert '<span data-lang="zh">阅读</span>' in local_article_map_html
    assert local_article_map_html.index('href="#local-article-reader"') < (
        local_article_map_html.index('href="#local-article-content-section-1"')
    )
    assert local_article_map_html.index('href="#local-article-content-section-1"') < (
        local_article_map_html.index('href="#local-article-body"')
    )
    assert '<span data-lang="en">Structured English.</span>' in detail_html
    assert '<span data-lang="zh">结构化中文。</span>' in detail_html
    assert '<span data-lang="zh">一段中文。</span>' not in detail_html


def test_render_row_one_detail_content_items_show_saved_paragraph_previews(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "First saved source paragraph about The Row.",
            "Second saved source paragraph about Margaux.",
            "Third saved source paragraph that should be capped.",
        ],
        paragraphs_zh=[
            "第一段保存正文，关于 The Row。",
            "第二段保存正文，关于 Margaux。",
            "第三段保存正文会被上限省略。",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(en="Structured item body.", zh="结构化条目正文。"),
                        paragraph_indices=[0, 1, 2],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = detail_html[
        detail_html.index('id="local-article-content-section-1"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert 'class="local-article-content-previews"' in section_html
    assert '<span data-lang="en">Saved paragraph 1</span>' in section_html
    assert '<span data-lang="zh">保存段落 1</span>' in section_html
    assert '<span data-lang="en">Saved paragraph 2</span>' in section_html
    assert '<span data-lang="zh">保存段落 2</span>' in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-paragraph-2"' in section_html
    assert "First saved source paragraph about The Row." in section_html
    assert "第一段保存正文，关于 The Row。" in section_html
    assert "Second saved source paragraph about Margaux." in section_html
    assert "第二段保存正文，关于 Margaux。" in section_html
    assert "Third saved source paragraph that should be capped." not in section_html


def test_render_row_one_detail_content_previews_filter_invalid_indices_and_escape(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Valid <script>source</script> paragraph.",
            "   ",
            "Second valid paragraph.",
        ],
        paragraphs_zh=["中文长度不匹配。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        paragraph_indices=[0, 0, 1, -1, 99, 2],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = detail_html[
        detail_html.index('id="local-article-content-section-1"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert section_html.count('class="local-article-content-preview"') == 2
    assert "Valid &lt;script&gt;source&lt;/script&gt; paragraph." in section_html
    assert "Second valid paragraph." in section_html
    assert "中文长度不匹配。" not in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-paragraph-2"' not in section_html
    assert 'href="#local-article-paragraph-3"' in section_html


def test_render_row_one_detail_continue_reading_prioritizes_same_section_and_fallbacks(
    tmp_path,
) -> None:
    current = _edition().stories[0]
    same_section = _detail_story(
        "same-section-1234567890",
        "Same Section <script>Story</script>",
    )
    other_section = _detail_story(
        "other-section-1234567890",
        "Other Section Story",
        section_key="brand_moves",
    )
    unsafe = _detail_story("unsafe-story-1234567890", "Unsafe Story").model_copy(
        update={"detail_path": "../unsafe.html"}
    )
    duplicate = _detail_story("duplicate-story-1234567890", "Duplicate Story").model_copy(
        update={"detail_path": same_section.detail_path}
    )
    extra = _detail_story("extra-story-1234567890", "Extra Story", section_key="brand_moves")
    edition = _edition_with_stories(current, unsafe, other_section, same_section, duplicate, extra)

    detail_html = render_detail_html(edition, current)

    continue_start = detail_html.index('id="continue-reading"')
    rail_html = detail_html[
        continue_start : detail_html.index("</section>", continue_start) + len("</section>")
    ]

    assert '<span data-lang="en">Continue Reading</span>' in rail_html
    assert '<span data-lang="zh">继续阅读</span>' in rail_html
    assert "Same Section &lt;script&gt;Story&lt;/script&gt;" in rail_html
    assert "<script>Story</script>" not in rail_html
    assert "Other Section Story" in rail_html
    assert "Extra Story" in rail_html
    assert 'class="continue-reading-source">Vogue Business</p>' in rail_html
    assert "Unsafe Story" not in rail_html
    assert "Duplicate Story" not in rail_html
    assert "The Row &lt;signals&gt;" not in rail_html
    assert rail_html.index("Same Section &lt;script&gt;Story&lt;/script&gt;") < rail_html.index(
        "Other Section Story"
    )
    assert 'href="same-section-1234567890.html"' in rail_html
    assert 'href="other-section-1234567890.html"' in rail_html
    assert 'href="details/same-section-1234567890.html"' not in rail_html
    assert rail_html.count('class="continue-reading-card"') == 3


def test_render_row_one_detail_continue_reading_omits_without_related_stories(
    tmp_path,
) -> None:
    edition = _edition_with_stories(_edition().stories[0])

    detail_html = render_detail_html(edition, edition.stories[0])

    assert 'id="continue-reading"' not in detail_html
    assert "Continue Reading" not in detail_html


def test_render_row_one_detail_continue_reading_uses_editorial_takeaway_fallback(
    tmp_path,
) -> None:
    current = _edition().stories[0]
    fallback_story = _detail_story(
        "fallback-story-1234567890",
        "Fallback Story",
        summary_en="",
        summary_zh="",
    ).model_copy(
        update={
            "editorial_takeaway": LocalizedText(
                zh="备用中文编辑摘录。",
                en="Fallback editorial excerpt.",
            )
        }
    )
    edition = _edition_with_stories(current, fallback_story)

    detail_html = render_detail_html(edition, current)

    assert "Fallback editorial excerpt." in detail_html
    assert "备用中文编辑摘录。" in detail_html


def test_render_row_one_detail_includes_signal_briefing_panel(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={
            "headline": "The Row <script>signal</script>",
            "summary": LocalizedText(
                en="Original source summary: <b>The Row signal</b> is moving.",
                zh="来源摘要：<b>The Row 信号</b>正在变化。",
            ),
            "signal_context": LocalizedText(
                en="Signal context <script>alert(1)</script>.",
                zh="信号背景 <script>alert(1)</script>。",
            ),
            "entity_refs": [
                RowOneReference(name="The Row", type="brand", label="tracked"),
                RowOneReference(name="The Row", type="brand", label="tracked"),
            ],
            "designer_refs": [
                RowOneReference(
                    name="Mary-Kate Olsen",
                    type="designer",
                    label="person",
                ),
            ],
            "product_refs": [
                RowOneReference(name="Margaux", type="bag", label="product"),
                RowOneReference(
                    name="Signal <script>Brand</script>",
                    type="brand",
                    label="unsafe",
                ),
            ],
        },
    )
    html = render_detail_html(edition, story, local_article=_signal_briefing_local_article())

    panel_start = html.index('class="detail-signal-briefing"')
    panel_html = html[panel_start : html.index('id="summary"', panel_start)]

    assert panel_start < html.index('id="summary"')
    assert '<span data-lang="en">Signal Briefing</span>' in panel_html
    assert '<span data-lang="zh">信号简报</span>' in panel_html
    assert '<span data-lang="en">What To Know</span>' in panel_html
    assert '<span data-lang="zh">重点整理</span>' in panel_html
    assert '<span data-lang="en">Signal</span>' in panel_html
    assert '<span data-lang="zh">信号</span>' in panel_html
    assert "The Row signal is moving." in panel_html
    assert "&lt;b&gt;" not in panel_html
    assert "<script>" not in panel_html
    assert "Vogue Business" in panel_html
    assert "1 safe evidence link" in panel_html
    assert "1 条安全线索" in panel_html
    assert "Signal context &lt;script&gt;alert(1)&lt;/script&gt;." in panel_html
    assert "The Row" in panel_html
    assert "Mary-Kate Olsen" in panel_html
    assert "Margaux" in panel_html
    assert "Alaia flats" in panel_html
    assert "Signal &lt;script&gt;Brand&lt;/script&gt;" in panel_html
    assert "<script>Brand</script>" not in panel_html
    assert panel_html.count('class="detail-signal-briefing-ref"') == 5
    assert panel_html.count(">The Row<") == 1
    assert "Local Article Cues" in panel_html
    assert "本地正文线索" in panel_html
    assert "What Happened" in panel_html
    assert "Why It Matters" in panel_html
    assert "People &amp; Brands" in panel_html
    assert "Signal Context" not in panel_html
    assert "Watch Next" not in panel_html
    assert "Products" not in panel_html
    assert 'href="#local-article-paragraph-1"' in panel_html
    assert 'href="#local-article-paragraph-2"' not in panel_html
    lower_why_start = html.index('id="why-it-matters"')
    lower_why_html = html[lower_why_start : html.index("</section>", lower_why_start)]
    assert panel_start < lower_why_start
    assert "This signal belongs in Top Stories." in lower_why_html


def test_render_row_one_detail_signal_briefing_omits_local_cues_without_structure() -> None:
    edition = _edition()
    html = render_detail_html(edition, edition.stories[0])

    panel_start = html.index('class="detail-signal-briefing"')
    panel_html = html[panel_start : html.index('id="summary"', panel_start)]

    assert "Signal Briefing" in panel_html
    assert "Local Article Cues" not in panel_html
    assert "本地正文线索" not in panel_html


def test_render_row_one_detail_signal_briefing_caps_references() -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={
            "entity_refs": [
                RowOneReference(name=f"Brand {index}", type="brand", label="tracked")
                for index in range(1, 12)
            ],
        },
    )

    html = render_detail_html(edition, story)
    panel_start = html.index('class="detail-signal-briefing"')
    panel_html = html[panel_start : html.index('id="summary"', panel_start)]

    assert panel_html.count('class="detail-signal-briefing-ref"') == 8
    assert "Brand 1" in panel_html
    assert "Brand 8" in panel_html
    assert "Brand 9" not in panel_html


def test_render_row_one_detail_skips_invalid_local_article_paragraph_links(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["First rendered paragraph.", "   ", "Third rendered paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        paragraph_indices=[-1, 0, 1, 2, 2, 99],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="local-article-paragraph-1"' in detail_html
    assert 'id="local-article-paragraph-2"' not in detail_html
    assert 'id="local-article-paragraph-3"' in detail_html
    provenance_html = detail_html[
        detail_html.index('class="local-article-provenance"') : detail_html.index(
            "Source article title"
        )
    ]
    assert '<span data-lang="en">Saved paragraphs</span>' in provenance_html
    assert '<span class="local-article-provenance-value">2</span>' in provenance_html
    assert '<span class="local-article-provenance-value">3</span>' not in provenance_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-paragraph-3"' in detail_html
    reader_html = detail_html[
        detail_html.index('id="local-article-reader"') : detail_html.index(
            'class="local-article-content-sections"'
        )
    ]
    content_sections_html = detail_html[
        detail_html.index('class="local-article-content-sections"') : detail_html.index(
            'id="local-article-body"'
        )
    ]
    assert reader_html.count('href="#local-article-paragraph-3"') == 1
    assert content_sections_html.count('href="#local-article-paragraph-3"') == 3
    assert 'href="#local-article-paragraph-0"' not in detail_html
    assert 'href="#local-article-paragraph-2"' not in detail_html
    assert 'href="#local-article-paragraph-100"' not in detail_html
    assert "Paragraph 0" not in detail_html
    assert "Paragraph 2" not in detail_html
    assert "Paragraph 100" not in detail_html
    assert "段落 0" not in detail_html
    assert "段落 2" not in detail_html
    assert "段落 100" not in detail_html


def test_render_row_one_detail_omits_local_article_nav_without_content(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="local-article"' not in detail_html
    assert 'href="#local-article"' not in detail_html
    assert not (tmp_path / "data" / "articles").exists()


def test_render_row_one_detail_omits_local_article_content_sections_without_body_paragraphs(
    tmp_path,
) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(en="Structured English.", zh="结构化中文。"),
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'id="local-article"' not in detail_html
    assert 'href="#local-article"' not in detail_html
    assert not (tmp_path / "data" / "articles").exists()


def test_render_row_one_detail_escapes_local_article_content(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="<script>Title</script>",
        url="https://example.com/the-row",
        source_name="Vogue <Business>",
        extracted_at=AS_OF,
        paragraphs=[
            '<img src=x onerror="alert(1)"> & quoted text',
        ],
        paragraphs_zh=[
            '<img src=x onerror="alert(1)"> 中文 & quoted text',
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="<script>Brief</script>", zh="简报<script>"),
                body=LocalizedText(
                    en='<img src=x onerror="alert(2)"> & brief',
                    zh='<img src=x onerror="alert(3)"> 中文 & brief',
                ),
            )
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="<script>Section</script>", zh="章节<script>"),
                body=LocalizedText(
                    en='<img src=x onerror="alert(4)"> & body',
                    zh='<img src=x onerror="alert(5)"> 中文 & body',
                ),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="<script>Item</script>", zh="条目<script>"),
                        body=LocalizedText(
                            en='<img src=x onerror="alert(6)"> & item',
                            zh='<img src=x onerror="alert(7)"> 中文 & item',
                        ),
                        references=[
                            RowOneReference(
                                name="<script>Ref</script>",
                                type="brand",
                                label="tracked",
                            )
                        ],
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "&lt;script&gt;Title&lt;/script&gt;" in detail_html
    assert "Vogue &lt;Business&gt;" in detail_html
    assert "&lt;script&gt;Brief&lt;/script&gt;" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; quoted text" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt; 中文 &amp; quoted text" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(2)&quot;&gt; &amp; brief" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(3)&quot;&gt; 中文 &amp; brief" in detail_html
    assert "&lt;script&gt;Section&lt;/script&gt;" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(4)&quot;&gt; &amp; body" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(5)&quot;&gt; 中文 &amp; body" in detail_html
    assert "&lt;script&gt;Item&lt;/script&gt;" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(6)&quot;&gt; &amp; item" in detail_html
    assert "&lt;img src=x onerror=&quot;alert(7)&quot;&gt; 中文 &amp; item" in detail_html
    assert "&lt;script&gt;Ref&lt;/script&gt;" in detail_html
    local_article_map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]
    assert 'href="#local-article-content-section-1"' in local_article_map_html
    assert "&lt;script&gt;Section&lt;/script&gt;" in local_article_map_html
    assert 'href="#local-article-body"' in local_article_map_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'id="local-article-paragraph-1"' in detail_html
    assert "<script>Brief</script>" not in detail_html
    assert "<script>" not in detail_html
    assert 'onerror="alert' not in detail_html
    assert "<img" not in detail_html


def test_render_row_one_detail_omits_unsafe_local_article_provenance_url(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Unsafe source article",
        url="javascript:alert(1)",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["One source paragraph."],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    local_article_html = detail_html[
        detail_html.index('id="local-article"') : detail_html.index('id="why-it-matters"')
    ]

    assert "Unsafe source article" in local_article_html
    assert "Vogue Business" in local_article_html
    assert "javascript:alert" not in local_article_html
    assert "Original URL" not in local_article_html
    assert 'class="local-article-provenance-link"' not in local_article_html


def test_render_row_one_site_includes_saved_article_coverage(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.section_key = "top_stories"
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row saved source",
        url="https://example.com/the-row-local",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["The Row saved paragraph.", "Second saved paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="要点", en="Takeaways"),
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_json = (tmp_path / "data" / "edition.json").read_text(encoding="utf-8")
    manifest_json = (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8")
    runtime_json = (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8")
    coverage_html = html[
        html.index('class="saved-article-coverage"') : html.index('class="saved-article-briefs"')
    ]

    assert 'class="saved-article-coverage"' in coverage_html
    assert '<span data-lang="en">Saved Article Coverage</span>' in coverage_html
    assert '<span data-lang="zh">保存正文覆盖</span>' in coverage_html
    assert "1 saved article" in coverage_html
    assert "2 saved paragraphs" in coverage_html
    assert "1 organized section" in coverage_html
    assert "1 source" in coverage_html
    assert "Vogue Business" in coverage_html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in coverage_html
    assert (
        '<span data-lang="en">The Row &lt;signals&gt; &quot;quiet&quot; demand</span>'
        in coverage_html
    )
    assert (
        '<span data-lang="zh">The Row &lt;signals&gt; &quot;quiet&quot; demand</span>'
        in coverage_html
    )
    assert "Top Stories" in coverage_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-digest"' in (coverage_html)
    assert html.index('class="daily-local-intelligence"') < html.index(
        'class="saved-article-coverage"'
    )
    assert html.index('class="saved-article-coverage"') < html.index('class="saved-article-briefs"')
    for app_contract_json in (edition_json, manifest_json, runtime_json):
        assert "saved_article_coverage" not in app_contract_json
        assert "Saved Article Coverage" not in app_contract_json


def test_render_row_one_site_omits_saved_article_coverage_without_saved_articles(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "saved-article-coverage" not in html


def test_render_row_one_site_escapes_saved_article_coverage(tmp_path) -> None:
    edition = _edition()
    unsafe_story = edition.stories[0].model_copy(
        update={"headline": '<script>alert("headline")</script>'}
    )
    edition.stories = [unsafe_story]
    local_article = RowOneLocalArticle(
        story_id=unsafe_story.id,
        title="Unsafe coverage source",
        url="https://example.com/unsafe",
        source_name="<Vogue>",
        extracted_at=AS_OF,
        paragraphs=['<script>alert("body")</script>'],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={unsafe_story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    coverage_html = html[
        html.index('class="saved-article-coverage"') : html.index('class="saved-article-briefs"')
    ]

    assert "&lt;script&gt;alert(&quot;headline&quot;)&lt;/script&gt;" in coverage_html
    assert "&lt;Vogue&gt;" in coverage_html
    assert "<script>" not in coverage_html
    assert "<Vogue>" not in coverage_html


def test_render_row_one_site_rejects_invalid_saved_article_coverage_links() -> None:
    coverage = RowOneSavedArticleCoverage(
        article_count=4,
        saved_paragraph_count=4,
        organized_section_count=0,
        source_count=1,
        sources=[RowOneSavedArticleCoverageSource(name="Vogue Business", article_count=4)],
        items=[
            _saved_article_coverage_item(
                detail_path="details/the-row-signal-1234567890.html#local-article-digest",
                title="Valid digest link",
            ),
            _saved_article_coverage_item(
                detail_path="details/the-row-signal-1234567890.html#local-article-body",
                title="Wrong fragment",
            ),
            _saved_article_coverage_item(
                detail_path="../private.html#local-article-digest",
                title="Traversal link",
            ),
            _saved_article_coverage_item(
                detail_path="javascript:alert(1)#local-article-digest",
                title="Script link",
            ),
        ],
    )

    html = render_index_html(_edition(), saved_article_coverage=coverage)
    coverage_html = html[
        html.index('class="saved-article-coverage"') : html.index('class="lead-story"')
    ]

    assert "Valid digest link" in coverage_html
    assert "Wrong fragment" not in coverage_html
    assert "Traversal link" not in coverage_html
    assert "Script link" not in coverage_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-digest"' in (coverage_html)
    assert "#local-article-body" not in coverage_html
    assert "../private.html" not in coverage_html
    assert "javascript:alert" not in coverage_html


def _saved_article_coverage_item(
    *,
    detail_path: str,
    title: str,
) -> RowOneSavedArticleCoverageItem:
    return RowOneSavedArticleCoverageItem(
        title=LocalizedText(zh=title, en=title),
        source_name="Vogue Business",
        section_title=LocalizedText(zh="今日重点", en="Top Stories"),
        detail_path=detail_path,
        saved_paragraph_count=1,
        organized_section_count=0,
    )


def test_render_row_one_site_writes_saved_article_library_page(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row <source>",
        url="https://example.com/the-row",
        source_name="Vogue <Business>",
        extracted_at=AS_OF,
        paragraphs=["First local paragraph with <signals>.", "Second paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="品牌与人物", en="People & Brands"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="The Row", en="The Row"),
                        body=LocalizedText(zh="The Row 正文。", en="The Row body."),
                        paragraph_indices=[0],
                        references=[
                            RowOneReference(name="<The Row>", type="brand", label="tracked")
                        ],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    library_path = tmp_path / "articles" / "index.html"
    assert library_path.exists()
    html = library_path.read_text(encoding="utf-8")
    home_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert '<link rel="stylesheet" href="../assets/row-one.css">' in html
    assert '<script src="../assets/row-one.js"></script>' in html
    assert 'href="../index.html"' in html
    assert "Daily Saved Article Library" in html
    assert "每日本地文章库" in html
    assert "1 saved article" in html
    assert "1 source" in html
    assert "2 saved paragraphs" in html
    assert "1 organized section" in html
    assert "1 extracted text" in html
    assert "1 篇提取正文" in html
    assert '<span data-lang="en">Text source</span>' in html
    assert '<span data-lang="zh">正文来源</span>' in html
    assert "Extracted article text" in html
    assert "Vogue &lt;Business&gt;" in html
    assert "The Row &lt;source&gt;" in html
    assert "&lt;The Row&gt;" in html
    assert 'href="the-row-signal-1234567890.html"' in html
    assert 'class="saved-article-library-primary-action"' in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-reader"' not in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-evidence"' in html
    )
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    library_grid_html = html[html.index('class="saved-article-library-grid"') :]
    assert 'class="saved-article-body-guide"' in library_grid_html
    assert 'class="saved-article-body-guide-item"' in library_grid_html
    assert "What this article says" in library_grid_html
    assert "正文导读" in library_grid_html
    assert "People &amp; Brands" in library_grid_html
    assert "品牌与人物" in library_grid_html
    assert "The Row body." in library_grid_html
    assert "The Row 正文。" in library_grid_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in library_grid_html
    )
    assert "<source>" not in html
    assert "<Business>" not in html
    assert "<The Row>" not in html

    assert 'href="articles/index.html"' in home_html
    assert 'class="saved-article-library-entry"' in home_html
    assert "Daily Saved Article Library" in home_html
    assert "每日本地文章库" in home_html
    assert "1 extracted text" in home_html
    assert home_html.index('class="saved-article-coverage"') < home_html.index(
        'class="saved-article-library-entry"'
    )
    assert home_html.index('class="saved-article-library-entry"') < home_html.index(
        'class="saved-article-briefs"'
    )

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        for forbidden in (
            "saved_article_library",
            "daily_saved_article_library",
            "article_library",
            "saved-article-library",
            "Daily Saved Article Library",
            "saved_article_library_text_source",
            "text_source_map",
            "text_source",
            "body_source",
            "extracted_article_count",
            "summary_fallback_article_count",
            "skipped_article_count",
            "Text source",
            "Extracted article text",
            "ROW ONE summary fallback",
            "Skipped",
            "saved_article_body_guide",
            "article_body_guide",
            "saved-article-body-guide",
            "article-body-guide",
            "What this article says",
            "正文导读",
            "People & Brands",
            "品牌与人物",
            "The Row body.",
            "The Row 正文。",
        ):
            assert forbidden not in contract_json
    assert not (tmp_path / "data" / "saved-article-library.json").exists()


def _html_between(html: str, start: str, end: str) -> str:
    start_index = html.index(start)
    end_index = html.index(end, start_index)
    return html[start_index:end_index]


def test_render_local_article_information_panel_is_included() -> None:
    edition = _edition()
    story = edition.stories[0]

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'class="local-article-information"' in html
    assert 'id="local-article-information-title"' in html
    assert "Local Article Information" in html
    assert "本地文章信息" in html
    assert "Vogue Business" in html
    assert "Extracted article" in html
    assert "3 paragraphs" in html
    assert "2 organized sections" in html
    assert html.index('class="local-article-information"') < html.index('id="local-article"')


def test_render_local_article_information_panel_uses_local_anchors() -> None:
    edition = _edition()
    story = edition.stories[0]
    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
    )
    panel = _html_between(html, '<section class="local-article-information"', 'id="local-article"')

    assert 'href="#local-article-reader"' in panel
    assert 'href="#local-article-digest"' in panel
    assert 'href="#local-article-paragraph-evidence"' in panel
    assert 'href="#local-article-content-section-1"' in panel
    assert 'href="#local-article-paragraph-1"' in panel
    assert 'href="http' not in panel
    assert 'href="../details/' not in panel


def test_render_local_article_page_labels_saved_paragraphs_with_paragraph_context_cues() -> None:
    story = _edition().stories[0]
    html = render_local_article_page_html(
        _edition(),
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'id="local-article-paragraph-1"' in html
    assert 'class="local-article-paragraph-context"' in html
    assert 'href="#local-article-content-section-1"' in html
    assert '<span data-lang="en">Used in</span>' in html
    assert '<span data-lang="zh">用于</span>' in html
    assert "People &amp; Brands - The Row" in html


def test_render_local_article_information_panel_shows_saved_paragraph_context_cues() -> None:
    base_article = _signal_briefing_local_article()
    article = base_article.model_copy(
        update={
            "paragraphs": [
                "Unique runway buyer context cue.",
                "Unique handbag market context cue.",
                "Unreferenced paragraph should stay out of cue previews.",
            ],
            "paragraphs_zh": [
                "独特秀场买手上下文提示。",
                "独特手袋市场上下文提示。",
                "未引用段落不应出现在提示预览。",
            ],
        }
    )
    html = render_local_article_page_html(_edition(), _edition().stories[0], local_article=article)
    panel = _html_between(html, '<section class="local-article-information"', 'id="local-article"')

    assert 'href="#local-article-paragraph-1"' in panel
    assert 'href="#local-article-paragraph-2"' in panel
    assert "Unique runway buyer context cue." in panel
    assert "Unique handbag market context cue." in panel
    assert "独特秀场买手上下文提示。" in panel
    assert "未引用段落不应出现在提示预览。" not in panel


def test_render_local_article_information_panel_dedupes_caps_and_escapes_refs() -> None:
    edition = _edition()
    story = edition.stories[0]
    refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="<script>", type="brand", label="<script>"),
        RowOneReference(name="Alaia flats", type="shoe", label="product"),
        RowOneReference(name="Margaux", type="bag", label="product"),
        RowOneReference(name="Mary-Kate Olsen", type="person", label="designer"),
        RowOneReference(name="Ashley Olsen", type="person", label="designer"),
        RowOneReference(name="Extra ref", type="brand", label="overflow"),
    ]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "source_name": "Source <script>",
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="<script>", zh="<script>"),
                    body=LocalizedText(en="<script>", zh="<script>"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="<script>", zh="<script>"),
                            body=LocalizedText(en="<script>", zh="<script>"),
                            references=refs,
                            paragraph_indices=[0, 1],
                        )
                    ],
                )
            ],
        },
    )

    html = render_local_article_page_html(edition, story, local_article=local_article)
    panel = _html_between(html, '<section class="local-article-information"', 'id="local-article"')

    assert "<script>" not in panel
    assert "&lt;script&gt;" in panel
    assert panel.count('class="local-article-information-ref"') <= 6
    assert panel.count('class="local-article-information-ref">The Row') == 1


def test_render_local_article_information_panel_filters_invalid_paragraph_indices() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            paragraph_indices=[0, 0, 99],
                        )
                    ],
                )
            ],
        },
    )

    html = render_local_article_page_html(edition, story, local_article=local_article)
    panel = _html_between(html, '<section class="local-article-information"', 'id="local-article"')

    assert 'href="#local-article-paragraph-1"' in panel
    assert 'href="#local-article-paragraph-2"' not in panel
    assert 'href="#local-article-paragraph-100"' not in panel


def test_render_local_article_page_includes_saved_article_local_reading_companion() -> None:
    edition = _edition()
    story = edition.stories[0]
    companion = RowOneSavedArticleLocalReadingCompanion(
        current_title=LocalizedText(en="Current <Article>", zh="当前 <文章>"),
        source_name="Vogue <Business>",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        group_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        group_dek=LocalizedText(en="Brand context <deck>", zh="品牌上下文 <说明>"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        body_source_label=LocalizedText(en="Extracted article text", zh="已提取文章正文"),
        lead=LocalizedText(en="The Row <lead>", zh="The Row <导语>"),
        saved_paragraph_count=3,
        organized_section_count=2,
        evidence_count=2,
        detail_path="details/the-row-signal-1234567890.html",
        local_links=(
            RowOneSavedArticleLocalReadingCompanionLink(
                label=LocalizedText(en="Saved text digest", zh="保存正文整理"),
                href="#local-article-digest",
            ),
            RowOneSavedArticleLocalReadingCompanionLink(
                label=LocalizedText(en="Saved text reader", zh="保存正文阅读"),
                href="#local-article-reader",
            ),
        ),
        related_items=(
            RowOneSavedArticleLocalReadingCompanionItem(
                title=LocalizedText(en="Alaia <signal>", zh="Alaia <信号>"),
                source_name="Vogue <Business>",
                section_label=LocalizedText(en="Products", zh="单品"),
                body_source_label=LocalizedText(
                    en="ROW ONE summary fallback",
                    zh="ROW ONE 摘要回退",
                ),
                lead=LocalizedText(en="Alaia flats <lead>", zh="Alaia 平底鞋 <导语>"),
                saved_paragraph_count=2,
                organized_section_count=1,
                evidence_count=1,
                href="alaia-signal-1234567890.html#local-article-digest",
                detail_path="details/alaia-signal-1234567890.html",
                references=(RowOneReference(name="Alaia <flats>", type="shoe", label="product"),),
            ),
            RowOneSavedArticleLocalReadingCompanionItem(
                title=LocalizedText(en="Unsafe", zh="不安全"),
                source_name="Unsafe",
                section_label=LocalizedText(en="Unsafe", zh="不安全"),
                body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                lead=LocalizedText(en="Unsafe", zh="不安全"),
                saved_paragraph_count=1,
                organized_section_count=1,
                evidence_count=1,
                href="javascript:alert(1)",
                detail_path="details/unsafe-signal-1234567890.html",
            ),
            RowOneSavedArticleLocalReadingCompanionItem(
                title=LocalizedText(en="Fallback detail", zh="详情页回退"),
                source_name="Vogue Business",
                section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
                body_source_label=LocalizedText(en="Extracted article text", zh="已提取文章正文"),
                lead=LocalizedText(en="Fallback detail lead", zh="详情页回退导语"),
                saved_paragraph_count=1,
                organized_section_count=1,
                evidence_count=3,
                href="../details/fallback-signal-1234567890.html#local-article-content-section-2",
                detail_path="details/fallback-signal-1234567890.html",
            ),
        ),
        references=(RowOneReference(name="The Row <brand>", type="brand", label="tracked"),),
    )

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
        saved_article_local_reading_companion=companion,
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-local-reading-companion"',
        'id="local-article"',
    )

    assert "Saved Article Local Reading Companion" in section_html
    assert "保存文章本地伴读" in section_html
    assert "Current &lt;Article&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "The Row &lt;lead&gt;" in section_html
    assert "Alaia &lt;signal&gt;" in section_html
    assert "Alaia &lt;flats&gt;" in section_html
    assert 'href="#local-article-digest"' in section_html
    assert 'href="#local-article-reader"' in section_html
    assert 'href="alaia-signal-1234567890.html#local-article-digest"' in section_html
    assert (
        'href="../details/fallback-signal-1234567890.html#local-article-content-section-2"'
        in section_html
    )
    assert "3 evidence points" in section_html
    assert "javascript:alert" not in section_html
    assert "<Article>" not in section_html
    assert html.index('class="local-article-information"') < html.index(
        'class="saved-article-local-reading-companion"'
    )
    assert html.index('class="saved-article-local-reading-companion"') < html.index(
        'id="local-article"'
    )


def test_render_local_article_page_includes_saved_article_local_section_binder() -> None:
    edition = _edition()
    story = edition.stories[0]
    companion = RowOneSavedArticleLocalReadingCompanion(
        current_title=LocalizedText(en="Current", zh="当前"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        group_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        group_dek=LocalizedText(en="Brand context", zh="品牌上下文"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        body_source_label=LocalizedText(en="Extracted article text", zh="已提取文章正文"),
        lead=LocalizedText(en="Current lead", zh="当前导语"),
        saved_paragraph_count=3,
        organized_section_count=2,
        evidence_count=2,
        detail_path="details/the-row-signal-1234567890.html",
        local_links=(),
        related_items=(),
    )
    binder = RowOneSavedArticleLocalSectionBinder(
        title=LocalizedText(en="Binder <Title>", zh="Binder <标题>"),
        source_name="Vogue <Business>",
        rows=(
            RowOneSavedArticleLocalSectionBinderRow(
                title=LocalizedText(en="People & <Brands>", zh="品牌与 <人物>"),
                section_position=1,
                section_href="#local-article-content-section-1",
                item_labels=(LocalizedText(en="The Row <chip>", zh="The Row <标签>"),),
                references=(
                    RowOneReference(name="Margaux <bag>", type="product", label="tracked"),
                ),
                paragraphs=(
                    RowOneSavedArticleLocalSectionBinderParagraph(
                        index=0,
                        href="#local-article-paragraph-1",
                        excerpt=LocalizedText(
                            en="Paragraph <excerpt>",
                            zh="段落 <摘录>",
                        ),
                    ),
                ),
            ),
        ),
        unfiled_paragraphs=(
            RowOneSavedArticleLocalSectionBinderParagraph(
                index=2,
                href="#local-article-paragraph-3",
                excerpt=LocalizedText(en="Unfiled <paragraph>", zh="未归档 <段落>"),
            ),
        ),
    )

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
        saved_article_local_reading_companion=companion,
        saved_article_local_section_binder=binder,
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-local-section-binder"',
        'id="local-article"',
    )

    assert "Saved Article Local Section Binder" in section_html
    assert "保存文章栏目索引" in section_html
    assert "Binder &lt;Title&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "People &amp; &lt;Brands&gt;" in section_html
    assert "The Row &lt;chip&gt;" in section_html
    assert "Margaux &lt;bag&gt; / product / tracked" in section_html
    assert "Paragraph &lt;excerpt&gt;" in section_html
    assert "Unfiled &lt;paragraph&gt;" in section_html
    assert 'href="#local-article-content-section-1"' in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-paragraph-3"' in section_html
    assert "Paragraph <excerpt>" not in section_html
    assert html.index('class="saved-article-local-reading-companion"') < html.index(
        'class="saved-article-local-section-binder"'
    )
    assert html.index('class="saved-article-local-section-binder"') < html.index(
        'id="local-article"'
    )


def test_render_local_article_page_includes_saved_article_key_signals() -> None:
    edition = _edition()
    story = edition.stories[0]
    companion = RowOneSavedArticleLocalReadingCompanion(
        current_title=LocalizedText(en="Current", zh="当前"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        group_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        group_dek=LocalizedText(en="Brand context", zh="品牌上下文"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        body_source_label=LocalizedText(en="Extracted article text", zh="已提取文章正文"),
        lead=LocalizedText(en="Current lead", zh="当前导语"),
        saved_paragraph_count=3,
        organized_section_count=2,
        evidence_count=2,
        detail_path="details/the-row-signal-1234567890.html",
        local_links=(),
        related_items=(),
    )
    binder = RowOneSavedArticleLocalSectionBinder(
        title=LocalizedText(en="Binder title", zh="栏目索引"),
        source_name="Vogue Business",
        rows=(
            RowOneSavedArticleLocalSectionBinderRow(
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                section_position=1,
                section_href="#local-article-content-section-1",
                item_labels=(),
                references=(),
                paragraphs=(),
            ),
        ),
    )
    key_signals = RowOneSavedArticleKeySignals(
        title=LocalizedText(en="Saved Article Key Signals", zh="已保存文章关键信号"),
        source_name="Vogue <Business>",
        groups=(
            RowOneSavedArticleKeySignalGroup(
                key="why_it_matters",
                title=LocalizedText(en="Why <It> Matters", zh="为什么 <重要>"),
                statement=LocalizedText(
                    en="The local saved text explains <demand>.",
                    zh="本地保存正文解释 <需求>。",
                ),
                support_count=1,
            ),
            RowOneSavedArticleKeySignalGroup(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                statement=LocalizedText(
                    en="The Row <anchor> supports the signal.",
                    zh="The Row <锚点> 支撑信号。",
                ),
                references=(
                    RowOneSavedArticleKeySignalReference(
                        name="The Row <brand>",
                        reference_type="brand",
                        label="tracked",
                        bucket="brands",
                    ),
                ),
                evidence=(
                    RowOneSavedArticleKeySignalEvidence(
                        index=0,
                        href="#local-article-paragraph-1",
                        excerpt=LocalizedText(
                            en="Paragraph <excerpt>",
                            zh="段落 <摘录>",
                        ),
                    ),
                    RowOneSavedArticleKeySignalEvidence(
                        index=1,
                        href="javascript:alert(1)",
                        excerpt=LocalizedText(
                            en="Unsafe paragraph",
                            zh="不安全段落",
                        ),
                    ),
                    RowOneSavedArticleKeySignalEvidence(
                        index=2,
                        href="#local-article-paragraph-0",
                        excerpt=LocalizedText(
                            en="Zero paragraph",
                            zh="零段落",
                        ),
                    ),
                ),
                support_count=1,
                reference_count=1,
                evidence_count=3,
            ),
            RowOneSavedArticleKeySignalGroup(
                key="themes",
                title=LocalizedText(en="Themes", zh="主题"),
                themes=(
                    RowOneSavedArticleKeySignalTheme(
                        label=LocalizedText(en="Quiet <Luxury>", zh="静奢 <主题>"),
                        href="#local-article-content-section-1",
                    ),
                    RowOneSavedArticleKeySignalTheme(
                        label=LocalizedText(en="Unsafe theme", zh="不安全主题"),
                        href="../secret.html#local-article-content-section-1",
                    ),
                    RowOneSavedArticleKeySignalTheme(
                        label=LocalizedText(en="Leading zero", zh="前导零"),
                        href="#local-article-content-section-01",
                    ),
                ),
                theme_count=3,
            ),
        ),
    )

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
        saved_article_local_reading_companion=companion,
        saved_article_local_section_binder=binder,
        saved_article_key_signals=key_signals,
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-key-signals"',
        'id="local-article"',
    )

    assert "Saved Article Key Signals" in section_html
    assert "已保存文章关键信号" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "Why &lt;It&gt; Matters" in section_html
    assert "The local saved text explains &lt;demand&gt;." in section_html
    assert "The Row &lt;anchor&gt; supports the signal." in section_html
    assert "The Row &lt;brand&gt; / brand / tracked" in section_html
    assert "Quiet &lt;Luxury&gt;" in section_html
    assert "Paragraph &lt;excerpt&gt;" in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-content-section-1"' in section_html
    assert "javascript:alert" not in section_html
    assert "../secret.html" not in section_html
    assert "#local-article-paragraph-0" not in section_html
    assert "#local-article-content-section-01" not in section_html
    assert "<demand>" not in section_html
    assert html.index('class="saved-article-local-reading-companion"') < html.index(
        'class="saved-article-local-section-binder"'
    )
    assert html.index('class="saved-article-local-section-binder"') < html.index(
        'class="saved-article-key-signals"'
    )
    assert html.index('class="saved-article-key-signals"') < html.index('id="local-article"')

    html_without_binder = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
        saved_article_key_signals=key_signals,
    )
    assert html_without_binder.index('class="saved-article-key-signals"') < (
        html_without_binder.index('id="local-article"')
    )


def test_render_row_one_detail_labels_saved_paragraphs_with_paragraph_context_cues() -> None:
    story = _edition().stories[0]
    html = render_detail_html(
        _edition(),
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'id="local-article-paragraph-1"' in html
    assert 'class="local-article-paragraph-context"' in html
    assert 'href="#local-article-content-section-1"' in html
    assert "People &amp; Brands - The Row" in html


def test_render_local_article_paragraph_context_filters_invalid_duplicate_indices() -> None:
    base_article = _signal_briefing_local_article()
    section = base_article.content_sections[0]
    invalid_item = section.items[0].model_copy(
        update={"paragraph_indices": [True, 0, 0, -1, 99, 1]}
    )
    article = base_article.model_copy(
        update={
            "content_sections": [
                section.model_copy(update={"items": [invalid_item]}),
            ]
        }
    )

    html = render_local_article_page_html(_edition(), _edition().stories[0], local_article=article)

    assert 'class="local-article-paragraph-context"' in html
    assert 'href="#local-article-content-section-1"' in html
    assert "#local-article-paragraph-0" not in html
    assert "#local-article-paragraph-100" not in html


def test_render_local_article_paragraph_context_escapes_and_caps_labels() -> None:
    base_article = _signal_briefing_local_article()
    sections = []
    for index in range(1, 6):
        section = base_article.content_sections[0].model_copy(
            update={
                "title": LocalizedText(zh=f"栏目 <{index}>", en=f"Section <{index}>"),
                "items": [
                    base_article.content_sections[0]
                    .items[0]
                    .model_copy(
                        update={
                            "label": LocalizedText(
                                zh=f"条目 <{index}>",
                                en=f"Item <{index}>",
                            ),
                            "paragraph_indices": [0],
                        }
                    )
                ],
            }
        )
        sections.append(section)
    article = base_article.model_copy(update={"content_sections": sections})

    html = render_local_article_page_html(_edition(), _edition().stories[0], local_article=article)

    assert "Section &lt;1&gt; - Item &lt;1&gt;" in html
    assert "Section <1>" not in html
    assert "Section &lt;5&gt; - Item &lt;5&gt;" not in html


def test_render_row_one_site_writes_first_class_local_article_page(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_path = tmp_path / "articles" / f"{story.id}.html"
    assert article_path.exists()
    article_html = article_path.read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert 'class="local-article-page"' in article_html
    assert '<link rel="stylesheet" href="../assets/row-one.css">' in article_html
    assert '<script src="../assets/row-one.js"></script>' in article_html
    assert 'href="index.html"' in article_html
    assert 'href="../index.html"' in article_html
    assert 'href="../details/the-row-signal-1234567890.html"' in article_html
    assert 'href="assets/row-one.css"' not in article_html
    assert 'src="assets/row-one.js"' not in article_html
    assert 'id="local-article"' in article_html
    assert 'class="local-article-information"' in article_html
    assert 'id="local-article-reader"' in article_html
    assert 'id="local-article-paragraph-1"' in article_html
    assert "Signal source article" in article_html
    assert "The Row Margaux bag appears in saved source text." in article_html
    assert f'href="{story.id}.html"' in library_html
    assert 'class="saved-article-library-primary-action"' in library_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in library_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-evidence"'
        in library_html
    )
    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "local_article_pages" not in contract_json
        assert "first_class_local_article" not in contract_json
        assert "local-article-page" not in contract_json
        assert "local_article_information" not in contract_json
        assert "local-article-information" not in contract_json
        assert "local_article_reading_improvements" not in contract_json
    assert not (tmp_path / "data" / "local-article-pages.json").exists()
    assert not (tmp_path / "data" / "local-article-reading-improvements.json").exists()


def test_render_row_one_site_writes_local_article_reading_companion_with_peer_links(
    tmp_path,
) -> None:
    current_story = _edition().stories[0]
    peer_story = _detail_story("alaia-signal-1234567890", "Alaia flats signal")
    edition = _edition_with_stories(current_story, peer_story)
    peer_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "story_id": peer_story.id,
            "title": "Alaia local article",
            "paragraphs": ["Alaia flats lead the saved source."],
            "paragraphs_zh": ["Alaia 平底鞋是保存正文重点。"],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="Alaia", zh="Alaia"),
                            body=LocalizedText(en="Alaia appears locally.", zh="Alaia 出现。"),
                            references=[
                                RowOneReference(name="Alaia", type="brand", label="tracked")
                            ],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ],
        },
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={
            current_story.id: _signal_briefing_local_article(),
            peer_story.id: peer_article,
        },
    )

    current_html = (tmp_path / "articles" / f"{current_story.id}.html").read_text(encoding="utf-8")
    peer_html = (tmp_path / "articles" / f"{peer_story.id}.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    companion_html = _html_between(
        current_html,
        '<section class="saved-article-local-reading-companion"',
        'id="local-article"',
    )
    assert "Saved Article Local Reading Companion" in companion_html
    assert 'href="#local-article-digest"' in companion_html
    assert f'href="{peer_story.id}.html#local-article-digest"' in companion_html
    assert f'href="{current_story.id}.html#local-article-digest"' not in companion_html
    assert 'class="saved-article-local-reading-companion"' in peer_html
    assert 'class="saved-article-local-reading-companion"' not in homepage_html
    assert 'class="saved-article-local-reading-companion"' not in detail_html
    assert "saved_article_local_reading_companion" not in generated_contract_payload
    assert "saved-article-local-reading-companion" not in generated_contract_payload
    assert not (tmp_path / "data" / "saved-article-local-reading-companion.json").exists()
    assert not (tmp_path / "data" / "article-local-reading-companion.json").exists()


def test_render_row_one_site_writes_local_article_section_binder_only_on_article_pages(
    tmp_path,
) -> None:
    story = _edition().stories[0]

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    section_html = _html_between(
        article_html,
        '<section class="saved-article-local-section-binder"',
        'id="local-article"',
    )
    assert "Saved Article Local Section Binder" in section_html
    assert 'href="#local-article-content-section-1"' in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert "The Row Margaux bag appears in saved source text." in section_html
    assert 'class="saved-article-local-section-binder"' not in library_html
    assert 'class="saved-article-local-section-binder"' not in homepage_html
    assert 'class="saved-article-local-section-binder"' not in detail_html
    assert "saved_article_local_section_binder" not in generated_contract_payload
    assert "saved-article-local-section-binder" not in generated_contract_payload
    assert not (tmp_path / "data" / "saved-article-local-section-binder.json").exists()
    assert not (tmp_path / "data" / "article-local-section-binder.json").exists()
    assert not (tmp_path / "data" / "local-section-binder.json").exists()


def test_write_row_one_site_files_writes_key_signals_only_on_local_article_pages(
    tmp_path,
) -> None:
    story = _edition().stories[0]

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    section_html = _html_between(
        article_html,
        '<section class="saved-article-key-signals"',
        'id="local-article"',
    )
    assert "Saved Article Key Signals" in section_html
    assert "Why It Matters" in section_html
    assert "Brands" in section_html
    assert "Products" in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-content-section-1"' in section_html
    assert 'class="saved-article-key-signals"' not in library_html
    assert 'class="saved-article-key-signals"' not in homepage_html
    assert 'class="saved-article-key-signals"' not in detail_html
    assert "saved_article_key_signals" not in generated_contract_payload
    assert "saved-article-key-signals" not in generated_contract_payload
    assert "Saved Article Key Signals" not in generated_contract_payload
    for stem in (
        "saved-article-key-signals",
        "article-key-signals",
        "local-article-key-signals",
        "key-signals",
        "local-key-signals",
    ):
        for directory in (tmp_path, tmp_path / "articles", tmp_path / "data"):
            assert not (directory / f"{stem}.json").exists()
            assert not (directory / f"{stem}.html").exists()


def test_render_row_one_site_writes_daily_local_key_signals_digest_homepage_only(
    tmp_path,
) -> None:
    story = _edition().stories[0]

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    section_html = _daily_local_key_signals_digest_section_html(homepage_html)
    assert "Daily Local Key Signals Digest" in section_html
    assert "每日本地关键信号摘要" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#saved-article-key-signals-title"' in (
        section_html
    )
    assert 'href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"' in (
        section_html
    )
    assert (
        'href="articles/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert 'class="daily-local-key-signals-digest"' not in library_html
    assert 'class="daily-local-key-signals-digest"' not in article_html
    assert 'class="daily-local-key-signals-digest"' not in detail_html
    assert "daily_local_key_signals_digest" not in generated_contract_payload
    assert "daily-local-key-signals-digest" not in generated_contract_payload
    assert "Daily Local Key Signals Digest" not in generated_contract_payload
    for stem in (
        "daily-local-key-signals-digest",
        "daily-local-key-signals",
        "daily-key-signals",
        "local-key-signals-digest",
        "daily_local_key_signals_digest",
        "daily_local_key_signals",
        "daily_key_signals",
        "local_key_signals_digest",
    ):
        for directory in (tmp_path, tmp_path / "articles", tmp_path / "data"):
            assert not (directory / f"{stem}.json").exists()
            assert not (directory / f"{stem}.html").exists()


def test_render_row_one_site_writes_daily_local_signal_momentum_homepage_only(
    tmp_path,
) -> None:
    story = _edition().stories[0]

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    section_html = _daily_local_signal_momentum_section_html(homepage_html)
    assert "Daily Local Signal Momentum" in section_html
    assert "每日本地信号动量" in section_html
    assert "The Row" in section_html
    assert "Alaia flats" in section_html
    assert "Products" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-digest"' in (section_html)
    assert 'class="daily-local-signal-momentum"' not in library_html
    assert 'class="daily-local-signal-momentum"' not in article_html
    assert 'class="daily-local-signal-momentum"' not in detail_html
    assert "daily_local_signal_momentum" not in generated_contract_payload
    assert "daily-local-signal-momentum" not in generated_contract_payload
    assert "Daily Local Signal Momentum" not in generated_contract_payload
    for stem in (
        "daily-local-signal-momentum",
        "daily-local-momentum",
        "signal-momentum",
        "daily_local_signal_momentum",
        "daily_local_momentum",
        "signal_momentum",
    ):
        for directory in (tmp_path, tmp_path / "articles", tmp_path / "data"):
            assert not (directory / f"{stem}.json").exists()
            assert not (directory / f"{stem}.html").exists()


def test_render_row_one_site_writes_daily_local_heat_signals_homepage_only(
    tmp_path,
) -> None:
    story = (
        _edition()
        .stories[0]
        .model_copy(
            deep=True,
            update={
                "heat_delta": 5,
                "entity_refs": [RowOneReference(name="The Row", type="brand", label="tracked")],
                "product_refs": [RowOneReference(name="Margaux bag", type="bag", label="product")],
            },
        )
    )
    edition = _edition()
    edition.stories = [story]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    section_html = _daily_local_heat_signals_section_html(homepage_html)
    assert "Daily Local Heat Signals" in section_html
    assert "每日本地热度信号" in section_html
    assert "The Row" in section_html
    assert "Margaux bag" in section_html
    assert "Bag" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-digest"' in (section_html)
    assert 'class="daily-local-heat-signals"' not in library_html
    assert 'class="daily-local-heat-signals"' not in article_html
    assert 'class="daily-local-heat-signals"' not in detail_html
    assert "daily_local_heat_signals" not in generated_contract_payload
    assert "daily-local-heat-signals" not in generated_contract_payload
    assert "Daily Local Heat Signals" not in generated_contract_payload
    for stem in (
        "daily-local-heat-signals",
        "daily-local-heat",
        "local-heat-signals",
        "heat-signals",
        "daily_local_heat_signals",
        "daily_local_heat",
        "local_heat_signals",
        "heat_signals",
    ):
        for directory in (tmp_path, tmp_path / "articles", tmp_path / "data"):
            assert not (directory / f"{stem}.json").exists()
            assert not (directory / f"{stem}.html").exists()


def test_render_row_one_site_writes_daily_local_article_capsules_homepage_only(
    tmp_path,
) -> None:
    story = (
        _edition()
        .stories[0]
        .model_copy(
            deep=True,
            update={
                "entity_refs": [RowOneReference(name="The Row", type="brand", label="tracked")],
                "product_refs": [RowOneReference(name="Margaux bag", type="bag", label="product")],
            },
        )
    )
    edition = _edition()
    edition.stories = [story]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )

    section_html = _daily_local_article_capsules_section_html(homepage_html)
    assert "Daily Local Article Capsules" in section_html
    assert "每日本地文章胶囊" in section_html
    assert "Signal source article" in section_html
    assert "The Row" in section_html
    assert "Margaux bag" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert 'class="daily-local-article-capsules"' not in library_html
    assert 'class="daily-local-article-capsules"' not in article_html
    assert 'class="daily-local-article-capsules"' not in detail_html
    assert "daily_local_article_capsules" not in generated_contract_payload
    assert "daily-local-article-capsules" not in generated_contract_payload
    assert "Daily Local Article Capsules" not in generated_contract_payload
    for stem in (
        "daily-local-article-capsules",
        "daily-local-capsules",
        "article-capsules",
        "daily_local_article_capsules",
        "daily_local_capsules",
        "article_capsules",
    ):
        for directory in (tmp_path, tmp_path / "articles", tmp_path / "data"):
            assert not (directory / f"{stem}.json").exists()
            assert not (directory / f"{stem}.html").exists()


def test_write_local_article_pages_rejects_orphaned_href_mapping(tmp_path) -> None:
    story = _edition().stories[0]

    with pytest.raises(ValueError, match="local_article_page_specs"):
        row_one_render._write_local_article_pages(
            _edition(),
            tmp_path / "articles",
            local_articles_by_story_id={story.id: _signal_briefing_local_article()},
            local_article_page_hrefs_by_detail_path={
                "details/other-1234567890.html": "other-1234567890.html",
            },
        )


def test_render_row_one_site_local_article_page_paragraph_context_cues_are_html_only(
    tmp_path,
) -> None:
    story = _edition().stories[0]
    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    assert 'class="local-article-paragraph-context"' in article_html
    assert 'id="local-article-paragraph-1"' in article_html

    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )
    assert "saved_paragraph_context_cues" not in generated_contract_payload
    assert "paragraph_context_cues" not in generated_contract_payload
    assert not (tmp_path / "data" / "saved-paragraph-context-cues.json").exists()


def test_render_row_one_site_omits_local_article_page_for_mismatched_article_id(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={"story_id": "other-story-1234567890"},
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    assert not (tmp_path / "articles" / f"{story.id}.html").exists()
    library_path = tmp_path / "articles" / "index.html"
    if library_path.exists():
        assert f'href="{story.id}.html"' not in library_path.read_text(encoding="utf-8")


def test_render_row_one_site_omits_local_article_page_for_empty_saved_body(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={"paragraphs": ["", "   "], "paragraphs_zh": []},
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    assert not (tmp_path / "articles" / f"{story.id}.html").exists()
    library_path = tmp_path / "articles" / "index.html"
    if library_path.exists():
        assert f'href="{story.id}.html"' not in library_path.read_text(encoding="utf-8")


def test_render_row_one_site_keeps_existing_error_for_unsafe_detail_path(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={"detail_path": "../unsafe.html"},
    )
    edition.stories = [story]

    with pytest.raises(ValueError):
        render_row_one_site(
            edition,
            tmp_path,
            local_articles_by_story_id={story.id: _signal_briefing_local_article()},
        )


def test_render_row_one_site_latest_only_removes_stale_local_article_page(tmp_path) -> None:
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir(parents=True)
    (tmp_path / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    (articles_dir / "stale.html").write_text("stale", encoding="utf-8")

    render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert not (articles_dir / "stale.html").exists()


def test_render_row_one_site_saved_article_library_hides_summary_fallback_reason(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row fallback source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        body_source="summary_fallback",
        reason="robots_disallowed",
        paragraphs=["Summary fallback paragraph."],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    chip_start = html.index('<li class="saved-article-library-text-source">')
    chip_html = html[chip_start : html.index("</li>", chip_start) + len("</li>")]

    assert "1 summary fallback" in html
    assert "1 篇摘要兜底" in html
    assert "ROW ONE summary fallback" in chip_html
    assert "href=" not in chip_html
    assert "<a " not in chip_html
    assert "Fallback reason" not in html
    assert "robots_disallowed" not in html


def test_render_row_one_site_includes_saved_signal_index_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    second_story = story.model_copy(
        update={
            "id": "margaux-signal-1234567890",
            "headline": "Margaux <bag> signal",
            "detail_path": "details/margaux-signal-1234567890.html",
        }
    )
    edition.stories.append(second_story)
    local_articles = {
        story.id: RowOneLocalArticle(
            story_id=story.id,
            title="The Row saved source",
            url="https://example.com/the-row",
            source_name="Vogue <Business>",
            extracted_at=AS_OF,
            paragraphs=["The Row saved paragraph."],
            content_sections=[
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(zh="品牌与人物", en="People & Brands"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(zh="The Row", en="The Row"),
                            body=LocalizedText(zh="The Row 正文。", en="The Row body."),
                            paragraph_indices=[0],
                            references=[
                                RowOneReference(
                                    name="<The Row>",
                                    type="brand",
                                    label="tracked",
                                )
                            ],
                        )
                    ],
                )
            ],
        ),
        second_story.id: RowOneLocalArticle(
            story_id=second_story.id,
            title="Margaux saved source",
            url="https://example.com/margaux",
            source_name="WWD",
            extracted_at=AS_OF,
            paragraphs=["Margaux saved paragraph."],
            content_sections=[
                RowOneLocalArticleContentSection(
                    key="product_signals",
                    title=LocalizedText(zh="产品", en="Products"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(zh="Margaux", en="Margaux"),
                            body=LocalizedText(zh="Margaux 正文。", en="Margaux body."),
                            paragraph_indices=[0],
                            references=[
                                RowOneReference(
                                    name="Margaux <bag>",
                                    type="product",
                                    label="bag",
                                )
                            ],
                        )
                    ],
                )
            ],
        ),
    }

    render_row_one_site(edition, tmp_path, local_articles_by_story_id=local_articles)

    html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    home_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert "Saved Signal Index" in html
    assert "本地信号索引" in html
    assert "2 saved signals" in html
    assert "2 supporting articles" in html
    assert "2 sources" in html
    assert "2 supporting paragraphs" in html
    assert "&lt;The Row&gt;" in html
    assert "Margaux &lt;bag&gt;" in html
    assert "Vogue &lt;Business&gt;" in html
    assert "<The Row>" not in html
    assert "<bag>" not in html
    assert "<Business>" not in html
    assert html.index('class="saved-article-library-hero"') < html.index(
        'class="saved-signal-index"'
    )
    assert html.index('class="saved-signal-index"') < html.index(
        'class="saved-article-library-grid"'
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"' in html
    )
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert (
        'href="../details/margaux-signal-1234567890.html#local-article-content-section-1"' in html
    )
    assert 'href="../details/margaux-signal-1234567890.html#local-article-paragraph-1"' in html
    assert "Browse saved local articles by signals or sources." in home_html
    assert "按信号或来源浏览本地保存文章。" in home_html

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_signal_index" not in contract_json
        assert "signal_index" not in contract_json
        assert "entity_index" not in contract_json
        assert "brand_index" not in contract_json
        assert "product_index" not in contract_json
        assert "saved-signal-index" not in contract_json
        assert "Saved Signal Index" not in contract_json
        assert "本地信号索引" not in contract_json
    assert not (tmp_path / "data" / "saved-signal-index.json").exists()


def test_render_row_one_site_includes_saved_article_content_organization_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_content_organization_section_html(library_html)

    assert 'class="saved-article-content-organization"' in section_html
    assert "Saved Article Content Organization" in section_html
    assert "保存正文内容整理" in section_html
    assert "People &amp; Brands" in section_html
    assert "Products" in section_html
    assert "The Row appears in paragraph one." in section_html
    assert "Alaia flats appear in paragraph two." in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
    ) in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"'
    ) in section_html
    assert (
        library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-content-section-1"'
    ) in homepage_html
    library_grid_html = library_html[library_html.index('class="saved-article-library-grid"') :]
    assert 'class="saved-article-body-guide"' in library_grid_html
    assert "The Row appears in paragraph one." in library_grid_html
    assert "Alaia flats appear in paragraph two." in library_grid_html

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_content_organization" not in contract_json
        assert "content_organization" not in contract_json
        assert "saved-article-content-organization" not in contract_json
        assert "Saved Article Content Organization" not in contract_json
        assert "saved_article_body_guide" not in contract_json
        assert "article_body_guide" not in contract_json
        assert "saved-article-body-guide" not in contract_json
        assert "article-body-guide" not in contract_json
    assert not (tmp_path / "data" / "saved-article-content-organization.json").exists()


def test_render_row_one_site_includes_saved_article_reading_paths_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_reading_paths_section_html(library_html)

    assert 'class="saved-article-reading-paths"' in section_html
    assert "Saved Article Reading Paths" in section_html
    assert "保存文章阅读路径" in section_html
    assert "People &amp; Brands" in section_html
    assert "Products" in section_html
    assert "The Row appears in paragraph one." in section_html
    assert "Alaia flats appear in paragraph two." in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-library-hero"')
        < library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-reading-paths"' not in homepage_html

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_reading_paths" not in contract_json
        assert "saved_article_reading_path" not in contract_json
        assert "article_reading_paths" not in contract_json
        assert "saved-article-reading-paths" not in contract_json
        assert "saved-article-reading-path" not in contract_json
        assert "Saved Article Reading Paths" not in contract_json
        assert "保存文章阅读路径" not in contract_json
        assert "The Row appears in paragraph one." not in contract_json
    assert not (tmp_path / "data" / "saved-article-reading-paths.json").exists()


def test_render_row_one_site_includes_saved_article_theme_digest_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_theme_digest_section_html(library_html)

    assert 'class="saved-article-theme-digest"' in section_html
    assert "Saved Article Theme Digest" in section_html
    assert "保存文章主题简报" in section_html
    assert "Read First" in section_html
    assert "Products" in section_html
    assert "Start with The Row retail signal." in section_html
    assert "Alaia flats appear in paragraph two." in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-library-hero"')
        < library_html.index('class="saved-article-theme-digest"')
        < library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-theme-digest"' not in homepage_html

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_theme_digest" not in contract_json
        assert "theme_digest" not in contract_json
        assert "saved-article-theme-digest" not in contract_json
        assert "Saved Article Theme Digest" not in contract_json
        assert "保存文章主题简报" not in contract_json
        assert "Start with The Row retail signal." not in contract_json
        assert "Alaia flats appear in paragraph two." not in contract_json
        assert "Alaia flats" not in contract_json
    assert not (tmp_path / "data" / "saved-article-theme-digest.json").exists()


def test_render_row_one_site_includes_saved_article_reference_atlas_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_reference_atlas_section_html(library_html)

    assert 'class="saved-article-reference-atlas"' in section_html
    assert "Saved Article Reference Atlas" in section_html
    assert "保存文章引用图谱" in section_html
    assert "Brands" in section_html
    assert "Products" in section_html
    assert "Source Context" in section_html
    assert "The Row" in section_html
    assert "Alaia flats" in section_html
    assert "Dover Street Market" in section_html
    assert "Vogue Business" in section_html
    assert "3 references" in section_html
    assert "3 supports" in section_html
    assert "1 source" in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-theme-digest"')
        < library_html.index('class="saved-article-reference-atlas"')
        < library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-reference-atlas"' not in homepage_html

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_reference_atlas" not in contract_json
        assert "reference_atlas" not in contract_json
        assert "saved-article-reference-atlas" not in contract_json
        assert "Saved Article Reference Atlas" not in contract_json
        assert "保存文章引用图谱" not in contract_json
        assert "Dover Street Market" not in contract_json
    assert not (tmp_path / "data" / "saved-article-reference-atlas.json").exists()


def test_render_row_one_site_includes_saved_article_signal_facets_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _saved_article_signal_facets_section_html(library_html)

    assert 'class="saved-article-signal-facets"' in section_html
    assert "Saved Article Signal Facets" in section_html
    assert "信号切面" in section_html
    assert "Reference atlas source article" in section_html
    assert "Vogue Business" in section_html
    assert "Brands" in section_html
    assert "Products" in section_html
    assert "Themes" in section_html
    assert "The Row" in section_html
    assert "Alaia flats" in section_html
    assert "People &amp; Brands" not in section_html
    assert "Source Structure" not in section_html
    assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert library_html.index('class="saved-article-daily-summary"') < library_html.index(
        'class="saved-article-signal-facets"'
    )
    assert library_html.index('class="saved-article-signal-facets"') < library_html.index(
        'class="saved-article-theme-digest"'
    )
    assert 'class="saved-article-signal-facets"' not in homepage_html


def test_render_row_one_site_includes_saved_article_daily_signal_leaderboard_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _saved_article_daily_signal_leaderboard_section_html(library_html)

    assert 'class="saved-article-daily-signal-leaderboard"' in section_html
    assert "Daily Signal Leaderboard" in section_html
    assert "每日信号榜" in section_html
    assert 'href="#saved-article-daily-signal-leaderboard"' in library_html
    assert "The Row" in section_html
    assert "Alaia flats" in section_html
    assert "article" in section_html
    assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert library_html.index('class="saved-article-signal-facets"') < library_html.index(
        'class="saved-article-daily-signal-leaderboard"'
    )
    assert library_html.index('class="saved-article-daily-signal-leaderboard"') < (
        library_html.index('class="saved-article-theme-digest"')
    )
    assert 'class="saved-article-daily-signal-leaderboard"' not in homepage_html


def test_render_row_one_site_includes_saved_article_organization_jump_index_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = _saved_article_organization_jump_index_section_html(library_html)

    assert 'class="saved-article-organization-jump-index"' in section_html
    assert "Saved Article Organization Jump Index" in section_html
    assert "保存文章组织索引" in section_html
    assert 'href="#saved-article-content-organization"' in section_html
    assert 'href="#saved-article-source-vogue-business"' in section_html
    assert 'href="#saved-article-signal-facets"' in section_html
    assert 'href="#saved-article-daily-signal-leaderboard"' in section_html
    jump_hrefs = re.findall(
        r'class="saved-article-organization-jump-index-link" href="#([^"]+)"',
        section_html,
    )
    assert jump_hrefs
    for target_id in jump_hrefs:
        assert f'id="{target_id}"' in library_html
    assert library_html.index('class="saved-article-daily-summary"') < library_html.index(
        'class="saved-article-organization-jump-index"'
    )
    assert library_html.index('class="saved-article-organization-jump-index"') < (
        library_html.index('class="saved-article-content-organization"')
    )
    assert 'class="saved-article-organization-jump-index"' not in homepage_html
    assert 'class="saved-article-organization-jump-index"' not in detail_html


def test_render_row_one_site_includes_saved_article_reading_queue_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = _saved_article_reading_queue_section_html(library_html)

    assert 'class="saved-article-reading-queue"' in section_html
    assert "Saved Article Reading Queue" in section_html
    assert "保存文章阅读队列" in section_html
    assert "Reference atlas source article" in section_html
    assert "Vogue Business" in section_html
    assert "Extracted article text" in section_html
    assert "3 saved paragraphs" in section_html
    assert "3 organized sections" in section_html
    assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert library_html.index('class="saved-article-organization-jump-index"') < (
        library_html.index('class="saved-article-reading-queue"')
    )
    assert library_html.index('class="saved-article-reading-queue"') < library_html.index(
        'class="saved-article-signal-facets"'
    )
    assert 'class="saved-article-reading-queue"' not in homepage_html
    assert 'class="saved-article-reading-queue"' not in detail_html


def test_render_row_one_site_includes_saved_article_read_next_clusters_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = _saved_article_read_next_clusters_section_html(library_html)

    assert 'class="saved-article-read-next-clusters"' in section_html
    assert "Saved Article Read Next Clusters" in section_html
    assert "保存文章继续阅读集群" in section_html
    assert "Reference atlas source article" in section_html
    assert "Vogue Business" in section_html
    assert "People &amp; Brands" in section_html
    assert "Products" in section_html
    assert "The Row" in section_html
    assert "Alaia flats" in section_html
    assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert library_html.index('class="saved-article-reading-queue"') < library_html.index(
        'class="saved-article-read-next-clusters"'
    )
    assert library_html.index('class="saved-article-read-next-clusters"') < library_html.index(
        'class="saved-article-signal-facets"'
    )
    assert 'class="saved-article-read-next-clusters"' not in homepage_html
    assert 'class="saved-article-read-next-clusters"' not in detail_html


def test_render_saved_article_library_html_escapes_reading_queue_and_revalidates_links() -> None:
    queue = RowOneSavedArticleReadingQueue(
        item_count=3,
        items=(
            RowOneSavedArticleReadingQueueItem(
                title=LocalizedText(en="Unsafe <Article>", zh="不安全 <文章>"),
                source_name="Vogue <Business>",
                body_source_label=LocalizedText(en="Extracted <Text>", zh="已提取 <正文>"),
                saved_paragraph_count=2,
                organized_section_count=3,
                href="../details/the-row-signal-1234567890.html#local-article-digest",
                detail_path="details/the-row-signal-1234567890.html",
            ),
            RowOneSavedArticleReadingQueueItem(
                title=LocalizedText(en="JavaScript link", zh="脚本链接"),
                source_name="Unsafe Source",
                body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                saved_paragraph_count=1,
                organized_section_count=1,
                href="javascript:alert(1)",
                detail_path="details/the-row-signal-1234567890.html",
            ),
            RowOneSavedArticleReadingQueueItem(
                title=LocalizedText(en="Outbound link", zh="外部链接"),
                source_name="External Source",
                body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                saved_paragraph_count=1,
                organized_section_count=1,
                href="https://example.com/article.html#local-article-digest",
                detail_path="details/the-row-signal-1234567890.html",
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reading_queue=queue,
    )
    section_html = _saved_article_reading_queue_section_html(html)

    assert "Unsafe &lt;Article&gt;" in section_html
    assert "不安全 &lt;文章&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "Extracted &lt;Text&gt;" in section_html
    assert "已提取 &lt;正文&gt;" in section_html
    assert "Unsafe <Article>" not in section_html
    assert "Vogue <Business>" not in section_html
    assert "javascript:" not in section_html
    assert "https://example.com" not in section_html
    assert "JavaScript link" not in section_html
    assert "Outbound link" not in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in section_html


def test_render_saved_article_library_html_omits_empty_reading_queue_shell() -> None:
    empty_queue = RowOneSavedArticleReadingQueue(item_count=0, items=())
    filtered_queue = RowOneSavedArticleReadingQueue(
        item_count=2,
        items=(
            RowOneSavedArticleReadingQueueItem(
                title=LocalizedText(en="Unsafe traversal", zh="不安全路径"),
                source_name="Unsafe Source",
                body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                saved_paragraph_count=1,
                organized_section_count=1,
                href="../details/../unsafe-1234567890.html#local-article-digest",
                detail_path="details/unsafe-1234567890.html",
            ),
            RowOneSavedArticleReadingQueueItem(
                title=LocalizedText(en="Whitespace link", zh="空白链接"),
                source_name="Unsafe Source",
                body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                saved_paragraph_count=1,
                organized_section_count=1,
                href="the-row-signal-1234567890.html #local-article-digest",
                detail_path="details/the-row-signal-1234567890.html",
            ),
        ),
    )

    for queue in (empty_queue, filtered_queue):
        html = render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_reading_queue=queue,
        )
        assert 'class="saved-article-reading-queue"' not in html
        assert "Saved Article Reading Queue" not in html
        assert "Unsafe traversal" not in html
        assert "Whitespace link" not in html


def test_render_saved_article_library_html_escapes_read_next_clusters_and_revalidates_links() -> (
    None
):
    clusters = RowOneSavedArticleReadNextClusters(
        cluster_count=1,
        item_count=4,
        source_count=1,
        evidence_count=1,
        clusters=(
            RowOneSavedArticleReadNextCluster(
                key="takeaways",
                title=LocalizedText(en="Read <First>", zh="优先 <阅读>"),
                dek=LocalizedText(en="Cluster <dek>", zh="集群 <说明>"),
                item_count=4,
                source_count=1,
                evidence_count=1,
                items=(
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Unsafe <Article>", zh="不安全 <文章>"),
                        source_name="Vogue <Business>",
                        section_label=LocalizedText(en="People <Brands>", zh="品牌 <人物>"),
                        body_source_label=LocalizedText(
                            en="Extracted <Text>",
                            zh="已提取 <正文>",
                        ),
                        lead=LocalizedText(en="Lead <script>", zh="导语 <script>"),
                        saved_paragraph_count=2,
                        organized_section_count=3,
                        evidence_count=1,
                        href=(
                            "../details/the-row-signal-1234567890.html"
                            "#local-article-content-section-1"
                        ),
                        detail_path="details/the-row-signal-1234567890.html",
                        references=(
                            RowOneReference(
                                name="The Row <brand>",
                                type="brand",
                                label="tracked <label>",
                            ),
                        ),
                    ),
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="JavaScript link", zh="脚本链接"),
                        source_name="Unsafe Source",
                        section_label=LocalizedText(en="Bad", zh="坏"),
                        body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                        lead=LocalizedText(en="Unsafe", zh="不安全"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        evidence_count=1,
                        href="javascript:alert(1)",
                        detail_path="details/the-row-signal-1234567890.html",
                    ),
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Outbound link", zh="外部链接"),
                        source_name="Unsafe Source",
                        section_label=LocalizedText(en="Bad", zh="坏"),
                        body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                        lead=LocalizedText(en="Unsafe", zh="不安全"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        evidence_count=1,
                        href="https://example.com/article.html#local-article-digest",
                        detail_path="details/the-row-signal-1234567890.html",
                    ),
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Wrong fragment", zh="错误锚点"),
                        source_name="Unsafe Source",
                        section_label=LocalizedText(en="Bad", zh="坏"),
                        body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                        lead=LocalizedText(en="Unsafe", zh="不安全"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        evidence_count=1,
                        href="../details/the-row-signal-1234567890.html#bad-fragment",
                        detail_path="details/the-row-signal-1234567890.html",
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_read_next_clusters=clusters,
    )
    section_html = _saved_article_read_next_clusters_section_html(html)

    assert "Unsafe &lt;Article&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "Lead &lt;script&gt;" in section_html
    assert "The Row &lt;brand&gt;" in section_html
    assert "tracked &lt;label&gt;" in section_html
    assert "Unsafe <Article>" not in section_html
    assert "Vogue <Business>" not in section_html
    assert "Lead <script>" not in section_html
    assert "javascript:" not in section_html
    assert "https://example.com" not in section_html
    assert "#bad-fragment" not in section_html
    assert "JavaScript link" not in section_html
    assert "Outbound link" not in section_html
    assert "Wrong fragment" not in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )


def test_render_saved_article_library_html_omits_empty_read_next_clusters_shell() -> None:
    empty_clusters = RowOneSavedArticleReadNextClusters(
        cluster_count=0,
        item_count=0,
        source_count=0,
        evidence_count=0,
        clusters=(),
    )
    filtered_clusters = RowOneSavedArticleReadNextClusters(
        cluster_count=1,
        item_count=1,
        source_count=1,
        evidence_count=1,
        clusters=(
            RowOneSavedArticleReadNextCluster(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Unsafe only", zh="只有不安全链接"),
                item_count=1,
                source_count=1,
                evidence_count=1,
                items=(
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Unsafe traversal", zh="不安全路径"),
                        source_name="Unsafe Source",
                        section_label=LocalizedText(en="Bad", zh="坏"),
                        body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                        lead=LocalizedText(en="Unsafe", zh="不安全"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        evidence_count=1,
                        href="../details/../unsafe-1234567890.html#local-article-digest",
                        detail_path="details/unsafe-1234567890.html",
                    ),
                ),
            ),
        ),
    )

    for clusters in (None, empty_clusters, filtered_clusters):
        html = render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_read_next_clusters=clusters,
        )
        assert 'class="saved-article-read-next-clusters"' not in html
        assert "Saved Article Read Next Clusters" not in html
        assert "Unsafe traversal" not in html


def test_render_saved_article_library_html_counts_only_rendered_read_next_items() -> None:
    clusters = RowOneSavedArticleReadNextClusters(
        cluster_count=2,
        item_count=3,
        source_count=2,
        evidence_count=8,
        clusters=(
            RowOneSavedArticleReadNextCluster(
                key="unsafe",
                title=LocalizedText(en="Unsafe Cluster", zh="不安全集群"),
                dek=LocalizedText(en="Should be filtered", zh="应该过滤"),
                item_count=1,
                source_count=1,
                evidence_count=5,
                items=(
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Unsafe first", zh="不安全优先"),
                        source_name="Unsafe Source",
                        section_label=LocalizedText(en="Bad", zh="坏"),
                        body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                        lead=LocalizedText(en="Unsafe", zh="不安全"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        evidence_count=5,
                        href="javascript:alert(1)",
                        detail_path="details/the-row-signal-1234567890.html",
                    ),
                ),
            ),
            RowOneSavedArticleReadNextCluster(
                key="safe",
                title=LocalizedText(en="Safe Cluster", zh="安全集群"),
                dek=LocalizedText(en="Only rendered items count", zh="只统计已渲染项"),
                item_count=2,
                source_count=1,
                evidence_count=3,
                items=(
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Unsafe before valid", zh="有效前的不安全项"),
                        source_name="Unsafe Source",
                        section_label=LocalizedText(en="Bad", zh="坏"),
                        body_source_label=LocalizedText(en="Skipped", zh="已跳过"),
                        lead=LocalizedText(en="Unsafe", zh="不安全"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        evidence_count=2,
                        href="../details/the-row-signal-1234567890.html#bad-fragment",
                        detail_path="details/the-row-signal-1234567890.html",
                    ),
                    RowOneSavedArticleReadNextClusterItem(
                        title=LocalizedText(en="Rendered valid", zh="已渲染有效项"),
                        source_name="Vogue Business",
                        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
                        body_source_label=LocalizedText(
                            en="Extracted article text",
                            zh="已提取文章正文",
                        ),
                        lead=LocalizedText(en="Valid lead", zh="有效导语"),
                        saved_paragraph_count=3,
                        organized_section_count=2,
                        evidence_count=1,
                        href=(
                            "../details/the-row-signal-1234567890.html"
                            "#local-article-content-section-1"
                        ),
                        detail_path="details/the-row-signal-1234567890.html",
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_read_next_clusters=clusters,
    )
    section_html = _saved_article_read_next_clusters_section_html(html)

    assert "Unsafe Cluster" not in section_html
    assert "Unsafe first" not in section_html
    assert "Unsafe before valid" not in section_html
    assert "Rendered valid" in section_html
    assert "1 cluster" in section_html
    assert "1 saved article" in section_html
    assert "1 source" in section_html
    assert "1 evidence point" in section_html
    assert "2 saved articles" not in section_html
    assert "8 evidence points" not in section_html


def test_render_saved_article_library_html_escapes_daily_signal_leaderboard() -> None:
    leaderboard = RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=1,
        item_count=1,
        buckets=(
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=LocalizedText(en="Unsafe <Brand>", zh="不安全 <品牌>"),
                        article_count=2,
                        source_count=1,
                        supports=(
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Unsafe <Article>", zh="不安全 <文章>"),
                                source_name="Vogue <Business>",
                                href="details/the-row-signal-1234567890.html#local-article-digest",
                                detail_path="details/the-row-signal-1234567890.html",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_daily_signal_leaderboard=leaderboard,
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "javascript:alert(1).html",
        },
    )
    section_html = _saved_article_daily_signal_leaderboard_section_html(html)

    assert "Unsafe &lt;Brand&gt;" in section_html
    assert "不安全 &lt;品牌&gt;" in section_html
    assert "Unsafe &lt;Article&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "Unsafe <Brand>" not in section_html
    assert "Unsafe <Article>" not in section_html
    assert "javascript:" not in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in section_html


def test_render_saved_article_library_html_omits_empty_daily_signal_leaderboard_shell() -> None:
    empty_leaderboard = RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=0,
        item_count=0,
        buckets=(),
    )

    for html in (
        render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_daily_signal_leaderboard=None,
        ),
        render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_daily_signal_leaderboard=empty_leaderboard,
        ),
    ):
        assert 'class="saved-article-daily-signal-leaderboard"' not in html
        assert "Daily Signal Leaderboard" not in html
        assert 'href="#saved-article-daily-signal-leaderboard"' not in html


def test_render_saved_article_library_html_escapes_organization_jump_index() -> None:
    jump_index = RowOneSavedArticleOrganizationJumpIndex(
        group_count=1,
        item_count=2,
        groups=(
            RowOneSavedArticleOrganizationJumpIndexGroup(
                key="signals",
                title=LocalizedText(en="Signals <script>", zh="信号 <script>"),
                items=(
                    RowOneSavedArticleOrganizationJumpIndexItem(
                        label=LocalizedText(en="Signal <script>", zh="信号 <script>"),
                        href="#saved-article-signal-facets",
                        count_label=LocalizedText(en="1 <row>", zh="1 <行>"),
                    ),
                    RowOneSavedArticleOrganizationJumpIndexItem(
                        label=LocalizedText(en="Unsafe link", zh="不安全链接"),
                        href="javascript:alert(1)",
                        count_label=LocalizedText(en="1 link", zh="1 个链接"),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_organization_jump_index=jump_index,
        saved_article_signal_facets=RowOneSavedArticleSignalFacets(
            row_count=1,
            brand_count=1,
            product_count=0,
            theme_count=0,
            rows=(
                RowOneSavedArticleSignalFacetRow(
                    title=LocalizedText(en="Anchor Article", zh="锚点文章"),
                    source_name="Vogue Business",
                    href="details/the-row-signal-1234567890.html#local-article-digest",
                    detail_path="details/the-row-signal-1234567890.html",
                    safe_card_count=1,
                    brands=(
                        RowOneSavedArticleSignalFacetChip(
                            label=LocalizedText(en="The Row", zh="The Row")
                        ),
                    ),
                    products=(),
                    themes=(),
                ),
            ),
        ),
    )
    section_html = _saved_article_organization_jump_index_section_html(html)

    assert "Signals &lt;script&gt;" in section_html
    assert "信号 &lt;script&gt;" in section_html
    assert "Signal &lt;script&gt;" in section_html
    assert "1 &lt;row&gt;" in section_html
    assert "Signals <script>" not in section_html
    assert "Signal <script>" not in section_html
    assert "javascript:" not in section_html


def test_render_saved_article_library_html_omits_empty_organization_jump_index_shell() -> None:
    empty_index = RowOneSavedArticleOrganizationJumpIndex(
        group_count=0,
        item_count=0,
        groups=(),
    )

    for html in (
        render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_organization_jump_index=empty_index,
        ),
    ):
        assert 'class="saved-article-organization-jump-index"' not in html
        assert "Saved Article Organization Jump Index" not in html


def test_render_saved_article_library_html_omits_filtered_organization_jump_index_shell() -> None:
    filtered_index = RowOneSavedArticleOrganizationJumpIndex(
        group_count=1,
        item_count=2,
        groups=(
            RowOneSavedArticleOrganizationJumpIndexGroup(
                key="signals",
                title=LocalizedText(en="Signals", zh="信号"),
                items=(
                    RowOneSavedArticleOrganizationJumpIndexItem(
                        label=LocalizedText(en="Missing target", zh="缺失目标"),
                        href="#saved-article-missing-target",
                        count_label=LocalizedText(en="1 jump", zh="1 个跳转"),
                    ),
                    RowOneSavedArticleOrganizationJumpIndexItem(
                        label=LocalizedText(en="Unsafe target", zh="不安全目标"),
                        href="javascript:alert(1)",
                        count_label=LocalizedText(en="1 jump", zh="1 个跳转"),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_organization_jump_index=filtered_index,
    )

    assert 'class="saved-article-organization-jump-index"' not in html
    assert "Missing target" not in html
    assert "Unsafe target" not in html
    assert "javascript:" not in html


def test_render_saved_article_library_html_escapes_signal_facets_and_revalidates_links() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=1,
        brand_count=1,
        product_count=2,
        theme_count=1,
        rows=(
            RowOneSavedArticleSignalFacetRow(
                title=LocalizedText(en="Unsafe <Article>", zh="不安全 <文章>"),
                source_name="Vogue <Business>",
                href="details/the-row-signal-1234567890.html#local-article-digest",
                detail_path="details/the-row-signal-1234567890.html",
                safe_card_count=7,
                brands=(
                    RowOneSavedArticleSignalFacetChip(
                        label=LocalizedText(en="The Row", zh="The Row")
                    ),
                ),
                products=(
                    RowOneSavedArticleSignalFacetChip(
                        label=LocalizedText(en="Alaia flats", zh="Alaia 平底鞋")
                    ),
                    RowOneSavedArticleSignalFacetChip(
                        label=LocalizedText(en="Margaux Bag", zh="Margaux 手袋")
                    ),
                ),
                themes=(
                    RowOneSavedArticleSignalFacetChip(
                        label=LocalizedText(en="People <Brands>", zh="人物与品牌")
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_signal_facets=facets,
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "javascript:alert(1).html",
        },
    )
    section_html = _saved_article_signal_facets_section_html(html)

    assert "Unsafe &lt;Article&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "People &lt;Brands&gt;" in section_html
    assert "People <Brands>" not in section_html
    assert "javascript:" not in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert "7 safe cards" in section_html


def test_render_saved_article_library_html_omits_empty_signal_facets_shell() -> None:
    empty_facets = RowOneSavedArticleSignalFacets(
        row_count=0,
        brand_count=0,
        product_count=0,
        theme_count=0,
        rows=(),
    )

    for html in (
        render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_signal_facets=None,
        ),
        render_saved_article_library_html(
            _edition(),
            _saved_article_library_fixture(),
            saved_article_signal_facets=empty_facets,
        ),
    ):
        assert 'class="saved-article-signal-facets"' not in html
        assert "Saved Article Signal Facets" not in html


def test_render_saved_article_library_html_filters_unsafe_only_signal_facets() -> None:
    library = _saved_article_library_fixture()
    unsafe_only_organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Unsafe only", zh="仅不安全"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Unsafe only", zh="仅不安全"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        section_label=LocalizedText(en="Unsafe", zh="不安全"),
                        lead=LocalizedText(en="Unsafe lead", zh="不安全摘要"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                        references=(
                            RowOneReference(
                                name="Unsafe Only Facet",
                                type="brand",
                                label="tracked",
                            ),
                        ),
                    )
                ],
            )
        ]
    )
    facets = build_row_one_saved_article_signal_facets(library, unsafe_only_organization)

    html = render_saved_article_library_html(
        _edition(),
        library,
        saved_article_signal_facets=facets,
    )

    assert facets is None
    assert 'class="saved-article-signal-facets"' not in html
    assert "Unsafe Only Facet" not in html
    assert "javascript:" not in html


def test_render_row_one_site_includes_saved_article_evidence_board_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _evidence_board_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_evidence_board_section_html(library_html)

    assert 'class="saved-article-evidence-board"' in section_html
    assert "Saved Article Paragraph Evidence Board" in section_html
    assert "保存文章段落证据板" in section_html
    assert "Read First" in section_html
    assert "Paragraph 1" in section_html
    assert "The Row paragraph one anchors the saved local evidence board." in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert "The Row" in section_html
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-evidence-board"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-evidence-board"' not in homepage_html

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_evidence_board" not in contract_json
        assert "paragraph_evidence_board" not in contract_json
        assert "saved-article-evidence-board" not in contract_json
        assert "Saved Article Paragraph Evidence Board" not in contract_json
        assert "保存文章段落证据板" not in contract_json
        assert "The Row paragraph one anchors the saved local evidence board." not in contract_json
    assert not (tmp_path / "data" / "saved-article-evidence-board.json").exists()
    forbidden_tokens = (
        "saved_article_evidence_board",
        "paragraph_evidence_board",
        "saved-article-evidence-board",
    )
    for artifact in (tmp_path / "data").rglob("*"):
        relative_name = artifact.relative_to(tmp_path / "data").as_posix()
        assert not any(token in relative_name for token in forbidden_tokens)
        if artifact.is_file() and artifact.suffix == ".json":
            artifact_text = artifact.read_text(encoding="utf-8")
            assert not any(token in artifact_text for token in forbidden_tokens)


def test_render_row_one_site_includes_saved_article_daily_summary_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_daily_summary_section_html(library_html)

    assert 'class="saved-article-daily-summary"' in section_html
    assert "Saved Article Daily Summary" in section_html
    assert "保存文章每日导览" in section_html
    assert "1 saved local article" in section_html
    assert "1 source" in section_html
    assert "available surfaces" in section_html
    assert 'class="saved-article-source-routes"' in section_html
    assert "Saved Article Source Routes" in section_html
    assert "来源导览" in section_html
    assert 'href="#saved-article-source-vogue-business"' in section_html
    assert "Vogue Business" in section_html
    assert "1 article" in section_html
    assert "3 saved paragraphs" in section_html
    assert 'href="#saved-article-theme-digest"' in section_html
    assert 'href="#saved-article-reference-atlas"' in section_html
    assert 'href="#saved-signal-index"' in section_html
    assert 'href="#saved-article-reading-paths"' in section_html
    assert 'href="#saved-article-evidence-board"' in section_html
    assert 'href="#saved-article-content-organization"' in section_html
    assert 'href="#saved-article-library-grid"' in section_html
    assert f'href="{story.id}.html#local-article-digest"' in section_html
    assert 'id="local-article-digest"' in article_html
    assert (
        library_html.index('class="saved-article-library-hero"')
        < library_html.index('class="saved-article-daily-summary"')
        < library_html.index('class="saved-article-theme-digest"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert section_html.index('class="saved-article-daily-summary-metrics"') < section_html.index(
        'class="saved-article-source-routes"'
    )
    assert section_html.index('class="saved-article-source-routes"') < section_html.index(
        'class="saved-article-daily-summary-links"'
    )
    assert 'id="saved-article-content-organization"' not in homepage_html
    assert 'class="saved-article-daily-summary"' not in homepage_html
    assert 'class="saved-article-source-routes"' not in homepage_html

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_daily_summary" not in contract_json
        assert "daily_saved_article_summary" not in contract_json
        assert "saved-article-daily-summary" not in contract_json
        assert "Saved Article Daily Summary" not in contract_json
        assert "保存文章每日导览" not in contract_json
        assert "saved_article_source_routes" not in contract_json
        assert "article_source_routes" not in contract_json
        assert "source_routes" not in contract_json
        assert "saved-article-source-routes" not in contract_json
        assert "article-source-routes" not in contract_json
        assert "source-routes" not in contract_json
        assert "Saved Article Source Routes" not in contract_json
        assert "来源导览" not in contract_json
    assert not (tmp_path / "data" / "saved-article-daily-summary.json").exists()
    assert not (tmp_path / "data" / "saved-article-source-routes.json").exists()


def test_saved_article_daily_summary_does_not_duplicate_downstream_content(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    section_html = _saved_article_daily_summary_section_html(library_html)

    assert "Start with The Row retail signal." not in section_html
    assert "Alaia flats appear in paragraph two." not in section_html
    assert "The Row paragraph one anchors the saved local evidence board." not in section_html
    assert 'class="saved-article-theme-digest-card"' not in section_html
    assert 'class="saved-article-reference-atlas-bucket"' not in section_html
    assert 'class="saved-article-evidence-board-card"' not in section_html
    assert 'class="saved-article-organization-coverage-row"' not in section_html
    assert 'class="saved-article-content-organization-card"' not in section_html


def test_render_saved_article_library_html_omits_daily_summary_without_targets() -> None:
    html = render_saved_article_library_html(
        _edition(),
        RowOneSavedArticleLibrary(
            article_count=0,
            source_count=0,
            saved_paragraph_count=0,
            organized_section_count=0,
            extracted_article_count=0,
            summary_fallback_article_count=0,
            skipped_article_count=0,
            groups=[],
        ),
    )

    assert 'class="saved-article-daily-summary"' not in html
    assert "Saved Article Daily Summary" not in html


def test_render_saved_article_library_html_filters_daily_summary_reading_hrefs() -> None:
    library = _saved_article_library_fixture()
    html = render_saved_article_library_html(
        _edition(),
        library,
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "javascript:alert(1).html",
        },
    )

    section_html = _saved_article_daily_summary_section_html(html)

    assert "javascript:alert" not in section_html
    assert 'href="the-row-signal-1234567890.html#local-article-digest"' not in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in section_html


def test_render_saved_article_library_daily_summary_source_routes_are_safe() -> None:
    base_entry = _saved_article_library_fixture().groups[0].entries[0]
    groups = [
        RowOneSavedArticleLibrarySourceGroup(
            source_name="Empty Source",
            article_count=0,
            saved_paragraph_count=0,
            organized_section_count=0,
            entries=[],
        ),
        RowOneSavedArticleLibrarySourceGroup(
            source_name="A B",
            article_count=1,
            saved_paragraph_count=2,
            organized_section_count=1,
            entries=[
                replace(
                    base_entry,
                    title=LocalizedText(en="A B article", zh="A B article"),
                    source_name="A B",
                )
            ],
        ),
        RowOneSavedArticleLibrarySourceGroup(
            source_name="中文来源",
            article_count=1,
            saved_paragraph_count=1,
            organized_section_count=1,
            entries=[
                replace(
                    base_entry,
                    title=LocalizedText(en="Chinese source", zh="中文来源"),
                    source_name="中文来源",
                )
            ],
        ),
        RowOneSavedArticleLibrarySourceGroup(
            source_name="A+B",
            article_count=1,
            saved_paragraph_count=3,
            organized_section_count=1,
            entries=[
                replace(
                    base_entry,
                    title=LocalizedText(en="A plus B article", zh="A plus B article"),
                    source_name="A+B",
                )
            ],
        ),
        RowOneSavedArticleLibrarySourceGroup(
            source_name="WWD <script>",
            article_count=1,
            saved_paragraph_count=4,
            organized_section_count=1,
            entries=[
                replace(
                    base_entry,
                    title=LocalizedText(en="WWD article", zh="WWD article"),
                    source_name="WWD <script>",
                )
            ],
        ),
        RowOneSavedArticleLibrarySourceGroup(
            source_name="The Row / Signals",
            article_count=1,
            saved_paragraph_count=5,
            organized_section_count=1,
            entries=[
                replace(
                    base_entry,
                    title=LocalizedText(en="The Row Signals article", zh="The Row Signals article"),
                    source_name="The Row / Signals",
                )
            ],
        ),
        RowOneSavedArticleLibrarySourceGroup(
            source_name="Overflow Source",
            article_count=1,
            saved_paragraph_count=6,
            organized_section_count=1,
            entries=[
                replace(
                    base_entry,
                    title=LocalizedText(en="Overflow article", zh="Overflow article"),
                    source_name="Overflow Source",
                )
            ],
        ),
    ]
    library = RowOneSavedArticleLibrary(
        article_count=6,
        source_count=7,
        saved_paragraph_count=21,
        organized_section_count=6,
        extracted_article_count=0,
        summary_fallback_article_count=6,
        skipped_article_count=0,
        groups=groups,
    )

    html = render_saved_article_library_html(_edition(), library)
    summary_html = _saved_article_daily_summary_section_html(html)

    route_link_class = 'class="saved-article-source-route saved-article-source-routes-link"'
    assert summary_html.count(route_link_class) == 4
    assert 'href="#saved-article-source-a-b"' in summary_html
    assert 'href="#saved-article-source-a-b-2"' in summary_html
    assert 'href="#saved-article-source-wwd-script"' in summary_html
    assert 'href="#saved-article-source-the-row-signals"' in summary_html
    assert 'href="#saved-article-source-overflow-source"' not in summary_html
    assert 'id="saved-article-source-overflow-source"' in html
    assert 'id="saved-article-source-empty-source"' not in html
    assert 'id="saved-article-source-a-b"' in _saved_article_library_source_html(
        html, "saved-article-source-a-b"
    )
    assert "A B" in _saved_article_library_source_html(html, "saved-article-source-a-b")
    assert "A+B" in _saved_article_library_source_html(html, "saved-article-source-a-b-2")
    assert "WWD &lt;script&gt;" in summary_html
    assert "WWD <script>" not in summary_html

    for href in re.findall(r'class="saved-article-source-route[^"]*" href="([^"]+)"', summary_html):
        assert re.fullmatch(r"#[A-Za-z0-9-]+", href)
        assert "/" not in href
        assert ":" not in href
        assert ".." not in href
        assert "javascript" not in href.casefold()


def test_render_saved_article_library_source_routes_omit_empty_shell_without_safe_routes() -> None:
    base_entry = _saved_article_library_fixture().groups[0].entries[0]
    html = render_saved_article_library_html(
        _edition(),
        RowOneSavedArticleLibrary(
            article_count=1,
            source_count=2,
            saved_paragraph_count=1,
            organized_section_count=1,
            extracted_article_count=0,
            summary_fallback_article_count=1,
            skipped_article_count=0,
            groups=[
                RowOneSavedArticleLibrarySourceGroup(
                    source_name="",
                    article_count=0,
                    saved_paragraph_count=0,
                    organized_section_count=0,
                    entries=[],
                ),
                RowOneSavedArticleLibrarySourceGroup(
                    source_name="中文来源",
                    article_count=1,
                    saved_paragraph_count=1,
                    organized_section_count=1,
                    entries=[
                        replace(
                            base_entry,
                            source_name="中文来源",
                            title=LocalizedText(en="Chinese source", zh="中文来源"),
                        )
                    ],
                ),
            ],
        ),
    )

    assert 'class="saved-article-source-routes"' not in html
    assert 'id="saved-article-source-' not in html
    assert 'class="saved-article-library-source-grid"' in html


def test_render_row_one_site_omits_saved_article_evidence_board_when_no_valid_paragraphs(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    article = _evidence_board_local_article().model_copy(
        deep=True,
        update={
            "content_sections": [],
            "paragraphs": ["A saved paragraph remains for the article library."],
            "paragraphs_zh": ["文章库仍保留一个保存段落。"],
        },
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: article},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")

    assert 'class="saved-article-evidence-board"' not in library_html
    assert "Saved Article Paragraph Evidence Board" not in library_html
    assert "保存文章段落证据板" not in library_html
    assert 'class="saved-article-library-hero"' in library_html
    assert 'class="saved-article-library-grid"' in library_html


def test_render_row_one_site_caps_saved_article_evidence_board_full_paragraphs(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    full_marker = "FULL_PARAGRAPH_END_MARKER"
    long_paragraph = " ".join(["The Row evidence board long paragraph"] * 18) + f" {full_marker}"
    article = _evidence_board_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": [long_paragraph, *_evidence_board_local_article().paragraphs[1:]],
            "paragraphs_zh": [
                " ".join(["The Row 证据板长段落"] * 18) + f" {full_marker}",
                *_evidence_board_local_article().paragraphs_zh[1:],
            ],
        },
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: article},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    section_html = _saved_article_evidence_board_section_html(library_html)

    assert 'class="saved-article-evidence-board"' in section_html
    assert "The Row evidence board long paragraph" in section_html
    assert full_marker not in section_html
    assert long_paragraph not in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )


def test_render_row_one_site_does_not_publish_every_short_saved_paragraph(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    article = _evidence_board_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": [
                "Short saved evidence paragraph one.",
                "Short saved evidence paragraph two.",
            ],
            "paragraphs_zh": [
                "短保存证据段落一。",
                "短保存证据段落二。",
            ],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="takeaways",
                    title=LocalizedText(zh="优先阅读", en="Read First"),
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(zh="入口段落", en="Opening paragraph"),
                            body=LocalizedText(
                                zh="短文章证据入口。",
                                en="Short article evidence opener.",
                            ),
                            references=[
                                RowOneReference(
                                    name="The Row",
                                    type="brand",
                                    label="tracked",
                                ),
                            ],
                            paragraph_indices=[0, 1],
                        )
                    ],
                )
            ],
        },
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: article},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    section_html = _saved_article_evidence_board_section_html(library_html)

    assert "Short saved evidence paragraph one." in section_html
    assert "Short saved evidence paragraph two." not in section_html


def test_render_saved_article_library_html_renders_saved_article_evidence_board_directly() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_evidence_board=RowOneSavedArticleEvidenceBoard(
            group_count=1,
            card_count=1,
            source_count=1,
            groups=(
                RowOneSavedArticleEvidenceBoardGroup(
                    key="takeaways",
                    title=LocalizedText(zh="Read First", en="Read First"),
                    dek=LocalizedText(zh="Evidence", en="Evidence"),
                    card_count=1,
                    source_count=1,
                    cards=(
                        RowOneSavedArticleEvidenceBoardCard(
                            title=LocalizedText(
                                zh="The Row saved article",
                                en="The Row saved article",
                            ),
                            source_name="Vogue Business",
                            section_title=LocalizedText(zh="Top Stories", en="Top Stories"),
                            section_label=LocalizedText(zh="Read First", en="Read First"),
                            paragraph_number=1,
                            excerpt=LocalizedText(
                                zh="The Row paragraph one",
                                en="The Row paragraph one",
                            ),
                            href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
                            references=(
                                RowOneReference(name="The Row", type="brand", label="tracked"),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
    section_html = _saved_article_evidence_board_section_html(html)

    assert "Saved Article Paragraph Evidence Board" in section_html
    assert "The Row paragraph one" in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert "The Row" in section_html


def test_render_saved_article_library_html_revalidates_saved_article_evidence_board_links() -> None:
    unsafe_cards = tuple(
        RowOneSavedArticleEvidenceBoardCard(
            title=LocalizedText(zh="Unsafe", en="Unsafe"),
            source_name="Bad Source",
            section_title=LocalizedText(zh="Top Stories", en="Top Stories"),
            section_label=LocalizedText(zh="Read First", en="Read First"),
            paragraph_number=1,
            excerpt=LocalizedText(zh="Unsafe paragraph", en="Unsafe paragraph"),
            href=href,
            references=(),
        )
        for href in (
            "javascript:alert(1)#local-article-paragraph-1",
            "details/../the-row-signal-1234567890.html#local-article-paragraph-1",
            "details/the-row-signal-1234567890.html#local-article-content-section-1",
            "details/the-row-signal-1234567890.html#local-article-paragraph-0",
            "details/the-row-signal-1234567890.html#local-article-paragraph-01",
        )
    )
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_evidence_board=RowOneSavedArticleEvidenceBoard(
            group_count=1,
            card_count=len(unsafe_cards),
            source_count=1,
            groups=(
                RowOneSavedArticleEvidenceBoardGroup(
                    key="takeaways",
                    title=LocalizedText(zh="Read First", en="Read First"),
                    dek=LocalizedText(zh="Evidence", en="Evidence"),
                    card_count=len(unsafe_cards),
                    source_count=1,
                    cards=unsafe_cards,
                ),
            ),
        ),
    )

    assert "javascript:alert(1)" not in html
    assert "../the-row-signal" not in html
    assert "#local-article-content-section-1" not in html
    assert "#local-article-paragraph-0" not in html
    assert "#local-article-paragraph-01" not in html
    assert 'class="saved-article-evidence-board-card"' not in html


def test_render_row_one_site_omits_saved_article_theme_digest_when_no_saved_articles(
    tmp_path,
) -> None:
    article_without_sections = _signal_briefing_local_article().model_copy(
        deep=True,
        update={"content_sections": []},
    )
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: article_without_sections},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")

    assert 'class="saved-article-theme-digest"' not in library_html
    assert "Saved Article Theme Digest" not in library_html
    assert "保存文章主题简报" not in library_html
    assert 'class="saved-article-library-hero"' in library_html
    assert 'class="saved-article-library-grid"' in library_html


def test_render_index_html_uses_source_only_copy_for_empty_saved_signal_index() -> None:
    html = render_index_html(
        _edition(),
        saved_article_library=_saved_article_library_fixture(),
        saved_signal_index=RowOneSavedSignalIndex(
            signal_count=0,
            supporting_article_count=0,
            source_count=0,
            supporting_paragraph_count=0,
            entries=[],
        ),
    )

    assert "Browse the current edition&#x27;s saved local articles by source." in html
    assert "Browse saved local articles by signals or sources." not in html


def _saved_signal_support_with_excerpt(
    excerpt: LocalizedText | None,
) -> RowOneSavedSignalIndexSupport:
    return RowOneSavedSignalIndexSupport(
        title=LocalizedText(zh="Excerpt support", en="Excerpt support"),
        source_name="Vogue Business",
        section_title=LocalizedText(zh="今日重点", en="Top Stories"),
        content_section_title=LocalizedText(zh="品牌与人物", en="People & Brands"),
        section_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_links=(
            RowOneSavedSignalIndexParagraphLink(
                label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
            ),
        ),
        excerpt=excerpt,
    )


def test_render_saved_signal_index_support_row_escapes_excerpt_before_actions() -> None:
    support = _saved_signal_support_with_excerpt(
        LocalizedText(
            en='The Row <script>alert("x")</script> body points to Margaux.',
            zh='The Row <script>alert("x")</script> 中文正文。',
        )
    )

    html = _render_saved_signal_index_support_row(support)

    assert 'class="saved-signal-index-support-excerpt"' in html
    assert (
        "The Row &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; body points to Margaux."
    ) in html
    assert "The Row &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; 中文正文。" in html
    assert "The Row <script>" not in html
    assert (
        html.index('class="saved-signal-index-support-meta"')
        < html.index('class="saved-signal-index-support-excerpt"')
        < html.index('class="saved-signal-index-actions"')
        < html.index('class="saved-signal-index-paragraphs"')
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"' in html
    )
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html


def test_render_saved_signal_index_support_row_omits_none_excerpt() -> None:
    support = _saved_signal_support_with_excerpt(None)

    html = _render_saved_signal_index_support_row(support)

    assert "saved-signal-index-support-excerpt" not in html
    assert 'class="saved-signal-index-actions"' in html


def test_render_saved_article_library_filters_saved_signal_unsafe_links() -> None:
    index = RowOneSavedSignalIndex(
        signal_count=1,
        supporting_article_count=1,
        source_count=1,
        supporting_paragraph_count=1,
        entries=[
            RowOneSavedSignalIndexEntry(
                name="x-route-from-display.html#display-fragment",
                type="x-id-from-display",
                label='x-class-from-display" onclick="bad',
                article_count=1,
                source_count=1,
                supporting_paragraph_count=1,
                supports=[
                    RowOneSavedSignalIndexSupport(
                        title=LocalizedText(
                            zh="Unsafe link support",
                            en="Unsafe link support",
                        ),
                        source_name="Vogue Business",
                        section_title=LocalizedText(zh="今日重点", en="Top Stories"),
                        content_section_title=LocalizedText(zh="品牌", en="Brands"),
                        section_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_links=(
                            RowOneSavedSignalIndexParagraphLink(
                                label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                                href=(
                                    "details/the-row-signal-1234567890.html"
                                    "#local-article-paragraph-1"
                                ),
                            ),
                            RowOneSavedSignalIndexParagraphLink(
                                label=LocalizedText(zh="Bad", en="Bad"),
                                href="javascript:alert(1)",
                            ),
                            RowOneSavedSignalIndexParagraphLink(
                                label=LocalizedText(zh="Bad", en="Bad"),
                                href="details/../escape.html#local-article-paragraph-1",
                            ),
                            RowOneSavedSignalIndexParagraphLink(
                                label=LocalizedText(zh="Bad", en="Bad"),
                                href="details/x.html#summary",
                            ),
                            RowOneSavedSignalIndexParagraphLink(
                                label=LocalizedText(zh="Bad", en="Bad"),
                                href=123,  # type: ignore[arg-type]
                            ),
                        ),
                        excerpt=LocalizedText(
                            zh=(
                                "Display ../details/<script>.html#local-article-content-section-9 "
                                'id="from-excerpt" class="from-excerpt"'
                            ),
                            en=(
                                "Display ../details/<script>.html#local-article-content-section-9 "
                                'id="from-excerpt" class="from-excerpt"'
                            ),
                        ),
                    ),
                    RowOneSavedSignalIndexSupport(
                        title=LocalizedText(zh="Bad action", en="Bad action"),
                        source_name="WWD",
                        section_title=LocalizedText(zh="产品", en="Products"),
                        content_section_title=LocalizedText(zh="鞋履", en="Shoes"),
                        section_path="javascript:alert(2)",  # type: ignore[arg-type]
                        paragraph_links=(),
                    ),
                    RowOneSavedSignalIndexSupport(
                        title=LocalizedText(zh="Bad action", en="Bad action"),
                        source_name="WWD",
                        section_title=LocalizedText(zh="产品", en="Products"),
                        content_section_title=LocalizedText(zh="鞋履", en="Shoes"),
                        section_path="details/../escape.html#local-article-content-section-1",
                        paragraph_links=(),
                    ),
                    RowOneSavedSignalIndexSupport(
                        title=LocalizedText(zh="Bad action", en="Bad action"),
                        source_name="WWD",
                        section_title=LocalizedText(zh="产品", en="Products"),
                        content_section_title=LocalizedText(zh="鞋履", en="Shoes"),
                        section_path="details/x.html#summary",
                        paragraph_links=(),
                    ),
                    RowOneSavedSignalIndexSupport(
                        title=LocalizedText(zh="Bad action", en="Bad action"),
                        source_name="WWD",
                        section_title=LocalizedText(zh="产品", en="Products"),
                        content_section_title=LocalizedText(zh="鞋履", en="Shoes"),
                        section_path=123,  # type: ignore[arg-type]
                        paragraph_links=(),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_signal_index=index,
    )
    structural_attributes = re.findall(r'\b(?:class|href|id)="([^"]*)"', html)

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"' in html
    )
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert "javascript:" not in html
    assert "details/../escape.html" not in html
    assert "details/x.html#summary" not in html
    assert "x-route-from-display" not in " ".join(structural_attributes)
    assert "x-id-from-display" not in " ".join(structural_attributes)
    assert "x-class-from-display" not in " ".join(structural_attributes)
    assert "../details/<script>" not in html
    assert "../details/&lt;script&gt;.html#local-article-content-section-9" in html
    assert "from-excerpt" not in " ".join(structural_attributes)
    assert "local-article-content-section-9" not in " ".join(structural_attributes)
    assert "x-route-from-display.html#display-fragment" in html
    assert "x-id-from-display" in html
    assert "x-class-from-display&quot; onclick=&quot;bad" in html


def test_render_row_one_site_omits_saved_signal_index_without_references(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="Saved source without references",
        url="https://example.com/no-refs",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Saved paragraph without structured references."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Lead", en="Lead"),
                        body=LocalizedText(zh="正文。", en="Body."),
                        paragraph_indices=[0],
                        references=[],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    home_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert "saved-signal-index" not in html
    assert "Saved Signal Index" not in html
    assert "本地信号索引" not in html
    assert "Browse the current edition&#x27;s saved local articles by source." in home_html
    assert "Browse saved local articles by signals or sources." not in home_html
    assert "按信号或来源浏览本地保存文章。" not in home_html


def test_render_row_one_site_omits_saved_article_library_without_saved_articles(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert not (tmp_path / "articles" / "index.html").exists()
    assert "saved-article-library-entry" not in html
    assert "Daily Saved Article Library" not in html


def test_render_row_one_site_includes_saved_article_briefs(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row saved source",
        url="https://example.com/the-row-local",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Fallback saved paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Lead", en="Lead"),
                        body=LocalizedText(
                            zh="首页首选中文正文摘要。",
                            en="Preferred homepage takeaway.",
                        ),
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="人物品牌", en="People & Brands"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Brands", en="Brands"),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="Vogue", type="source", label="publisher"),
                        ],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品", en="Products"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Products", en="Products"),
                        references=[
                            RowOneReference(name="Margaux", type="bag", label="product"),
                        ],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    briefs_html = html[
        html.index('class="saved-article-briefs"') : html.index('class="lead-story"')
    ]

    assert 'class="saved-article-briefs"' in briefs_html
    assert '<span data-lang="en">Saved Article Briefs</span>' in briefs_html
    assert '<span data-lang="zh">保存正文简报</span>' in briefs_html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in briefs_html
    assert "Vogue Business" in briefs_html
    assert "Top Stories" in briefs_html
    assert "Preferred homepage takeaway." in briefs_html
    assert "首页首选中文正文摘要。" in briefs_html
    assert "The Row" in briefs_html
    assert "Margaux" in briefs_html
    assert "People &amp; Brands" in briefs_html
    assert "Products" in briefs_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-digest"' in briefs_html
    assert html.index('class="saved-article-coverage"') < html.index('class="saved-article-briefs"')
    assert html.index('class="saved-article-briefs"') < html.index('class="lead-story"')

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_briefs" not in contract_json
        assert "Saved Article Briefs" not in contract_json
        assert "saved-article-briefs" not in contract_json
        assert "Preferred homepage takeaway" not in contract_json
    assert not (tmp_path / "data" / "saved-article-briefs.json").exists()


def test_render_row_one_site_omits_saved_article_briefs_without_saved_articles(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "saved-article-briefs" not in html


def test_render_row_one_site_escapes_saved_article_briefs(tmp_path) -> None:
    edition = _edition()
    unsafe_story = edition.stories[0].model_copy(
        update={"headline": '<script>alert("headline")</script>'}
    )
    edition.stories = [unsafe_story]
    local_article = RowOneLocalArticle(
        story_id=unsafe_story.id,
        title="Unsafe brief source",
        url="https://example.com/unsafe",
        source_name="<Vogue>",
        extracted_at=AS_OF,
        paragraphs=['<img src=x onerror="alert(1)">'],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="人物品牌", en="People & Brands"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Brands", en="Brands"),
                        references=[
                            RowOneReference(
                                name="<The Row>",
                                type="brand",
                                label='tracked "brand"',
                            )
                        ],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={unsafe_story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    briefs_html = html[
        html.index('class="saved-article-briefs"') : html.index('class="lead-story"')
    ]

    assert "&lt;script&gt;alert(&quot;headline&quot;)&lt;/script&gt;" in briefs_html
    assert "&lt;Vogue&gt;" in briefs_html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in briefs_html
    assert "&lt;The Row&gt;" in briefs_html
    assert "tracked &quot;brand&quot;" in briefs_html
    assert "<script>" not in briefs_html
    assert "<Vogue>" not in briefs_html
    assert '<img src=x onerror="alert' not in briefs_html
    assert "<The Row>" not in briefs_html


def test_render_row_one_site_rejects_invalid_saved_article_briefs_links() -> None:
    briefs = RowOneSavedArticleBriefs(
        article_count=4,
        items=[
            _saved_article_brief_item(
                detail_path="details/the-row-signal-1234567890.html#local-article-digest",
                title="Valid digest brief",
            ),
            _saved_article_brief_item(
                detail_path="details/the-row-signal-1234567890.html#local-article-body",
                title="Wrong fragment brief",
            ),
            _saved_article_brief_item(
                detail_path="../private.html#local-article-digest",
                title="Traversal brief",
            ),
            _saved_article_brief_item(
                detail_path="javascript:alert(1)#local-article-digest",
                title="Script brief",
            ),
        ],
    )

    html = render_index_html(_edition(), saved_article_briefs=briefs)
    briefs_html = html[
        html.index('class="saved-article-briefs"') : html.index('class="lead-story"')
    ]

    assert "Valid digest brief" in briefs_html
    assert "Wrong fragment brief" not in briefs_html
    assert "Traversal brief" not in briefs_html
    assert "Script brief" not in briefs_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-digest"' in briefs_html
    assert "#local-article-body" not in briefs_html
    assert "../private.html" not in briefs_html
    assert "javascript:alert" not in briefs_html


def _saved_article_brief_item(
    *,
    detail_path: str,
    title: str,
) -> RowOneSavedArticleBriefItem:
    return RowOneSavedArticleBriefItem(
        title=LocalizedText(zh=title, en=title),
        source_name="Vogue Business",
        section_title=LocalizedText(zh="今日重点", en="Top Stories"),
        lead=LocalizedText(zh="正文摘要。", en="Saved article excerpt."),
        detail_path=detail_path,
        people_brands=(RowOneReference(name="The Row", type="brand", label="tracked"),),
        products=(RowOneReference(name="Margaux", type="bag", label="product"),),
    )


def _local_article_for_daily_intelligence() -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["The Row and Margaux are moving in saved local coverage."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                        body=LocalizedText(
                            zh="The Row 与 Margaux 的本地来源信号。",
                            en="The Row and Margaux are moving in saved local coverage.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )


def test_render_row_one_site_includes_daily_local_intelligence(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    story.heat_delta = 6

    result = render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _local_article_for_daily_intelligence()},
    )

    html = result.index_path.read_text(encoding="utf-8")
    assert "daily-local-intelligence" in html
    assert '<span data-lang="en">Daily Local Intelligence</span>' in html
    assert '<span data-lang="zh">每日本地情报</span>' in html
    assert "The Row and Margaux are moving in saved local coverage." in html
    assert 'href="details/the-row-signal-1234567890.html#local-article"' in html
    assert (
        '<a class="daily-local-intelligence-action" '
        'href="details/the-row-signal-1234567890.html#local-article">'
    ) in html
    assert '<span data-lang="en">Open saved text</span>' in html
    assert '<span data-lang="zh">打开本地正文</span>' in html
    assert "Open paragraph 1" not in html
    assert "打开段落 1" not in html
    assert "Evidence paragraph 1" in html
    assert "证据段落 1" in html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert '<a class="daily-local-intelligence-card"' not in html

    artifact = json.loads(
        (tmp_path / "data" / "local-intelligence.json").read_text(encoding="utf-8")
    )
    assert [section["key"] for section in artifact] == [
        "strongest_reads",
        "brand_watch",
        "product_watch",
        "heat_movers",
    ]
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    assert "local_article_intelligence" not in payload


def test_render_row_one_site_clusters_duplicate_daily_local_intelligence_cards(
    tmp_path,
) -> None:
    edition = _edition()
    story_a = edition.stories[0]
    story_a.id = "coach-a-1234567890"
    story_a.headline = "Coach Brooklyn Bag gains heat"
    story_a.detail_path = "details/coach-a-1234567890.html"
    story_a.heat_delta = 6
    story_b = story_a.model_copy(
        deep=True,
        update={
            "id": "coach-b-1234567890",
            "detail_path": "details/coach-b-1234567890.html",
            "heat_delta": 9,
        },
    )
    edition.stories = [story_a, story_b]
    article_a = _local_article_for_daily_intelligence().model_copy(
        deep=True,
        update={
            "story_id": story_a.id,
            "url": "https://example.com/coach-a",
            "paragraphs": ["Coach Brooklyn Bag appears in the saved local article body."],
        },
    )
    article_b = article_a.model_copy(
        deep=True,
        update={
            "story_id": story_b.id,
            "url": "https://example.com/coach-b",
        },
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story_a.id: article_a, story_b.id: article_b},
    )

    local_intelligence = json.loads(
        (tmp_path / "data" / "local-intelligence.json").read_text(encoding="utf-8")
    )
    strongest = next(
        section for section in local_intelligence if section["key"] == "strongest_reads"
    )
    heat = next(section for section in local_intelligence if section["key"] == "heat_movers")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))

    assert len(strongest["items"]) == 1
    assert len(heat["items"]) == 1
    assert strongest["items"][0]["story_count"] == 2
    assert strongest["items"][0]["article_count"] == 2
    assert strongest["items"][0]["detail_path"] == "details/coach-b-1234567890.html#local-article"
    assert (tmp_path / "details" / "coach-a-1234567890.html").exists()
    assert (tmp_path / "details" / "coach-b-1234567890.html").exists()
    assert (tmp_path / "data" / "articles" / "coach-a-1234567890.json").exists()
    assert (tmp_path / "data" / "articles" / "coach-b-1234567890.json").exists()
    assert "local_article_intelligence" not in edition_payload


def test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row source paragraph.",
            "Margaux product paragraph.",
        ],
        paragraphs_zh=["The Row 中文段落。", "Margaux 中文段落。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                body=LocalizedText(
                    zh="本地正文指出这些读法。",
                    en="The saved source points to these reads.",
                ),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="The Row 中文段落。",
                            en="The Row source paragraph.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品信号", en="Product Signals"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Margaux", en="Margaux"),
                        body=LocalizedText(zh="bag / product", en="bag / product"),
                        references=[RowOneReference(name="Margaux", type="bag", label="product")],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "daily-local-intelligence-segments" in html
    assert "Takeaways" in html
    assert "The saved source points to these reads." in html
    assert "Source lead" in html
    assert "The Row source paragraph." in html
    assert "Product Signals" in html
    assert "Margaux" in html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"' in html
    assert '<a class="daily-local-intelligence-card"' not in html
    css = row_one_css()
    assert ".daily-local-intelligence-actions" in css
    assert ".daily-local-intelligence-action" in css
    assert ".daily-local-intelligence-paragraph-link" in css
    daily_local_intelligence_block = html[
        html.index('class="daily-local-intelligence"') : html.index(
            'class="saved-article-coverage"'
        )
    ]
    daily_local_intelligence_hrefs = "".join(
        re.findall(r'href="([^"]+)"', daily_local_intelligence_block)
    )
    assert "#local-article-content-section-" not in daily_local_intelligence_hrefs
    assert "#local-article-body" not in daily_local_intelligence_hrefs
    assert "Evidence paragraph 1" in html
    assert "证据段落 1" in html

    artifact = json.loads(
        (tmp_path / "data" / "local-intelligence.json").read_text(encoding="utf-8")
    )
    strongest = next(section for section in artifact if section["key"] == "strongest_reads")
    assert strongest["items"][0]["segments"][0]["key"] == "takeaways"
    assert strongest["items"][0]["segments"][0]["body"]["en"] == (
        "The saved source points to these reads."
    )
    assert strongest["items"][0]["segments"][0]["items"][0]["paragraph_indices"] == [0]
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    assert "local_article_intelligence" not in payload


def test_render_row_one_site_filters_daily_local_intelligence_segment_paragraph_indices() -> None:
    html = render_index_html(
        _edition(),
        local_article_intelligence=[
            RowOneDailyLocalIntelligenceSection(
                key="strongest_reads",
                title=LocalizedText(zh="优先阅读", en="Strongest Reads"),
                dek=LocalizedText(zh="本地正文。", en="Saved local text."),
                items=[
                    RowOneDailyLocalIntelligenceItem(
                        title=LocalizedText(zh="本地信号", en="Local Signal"),
                        body=LocalizedText(zh="正文。", en="Body."),
                        detail_path="details/the-row-signal-1234567890.html#local-article",
                        paragraph_indices=[0],
                        segments=[
                            RowOneDailyLocalIntelligenceSegment(
                                key="takeaways",
                                title=LocalizedText(zh="正文重点", en="Takeaways"),
                                items=[
                                    RowOneDailyLocalIntelligenceSegmentItem(
                                        label=LocalizedText(zh="来源段落", en="Source paragraph"),
                                        paragraph_indices=[-1, 0, 0],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )

    assert "Paragraph 0" not in html
    assert "段落 0" not in html
    meta_match = re.search(
        r'<div class="daily-local-intelligence-segment-meta">(?P<meta>.*?)</div>',
        html,
        re.S,
    )
    assert meta_match is not None
    meta_html = meta_match.group("meta")
    assert meta_html.count("Paragraph 1") == 1
    assert meta_html.count("段落 1") == 1
    assert (
        html.count('href="details/the-row-signal-1234567890.html#local-article-paragraph-1"') == 2
    )


def test_render_row_one_site_omits_daily_local_intelligence_without_saved_articles(
    tmp_path,
) -> None:
    result = render_row_one_site(_edition(), tmp_path)

    html = result.index_path.read_text(encoding="utf-8")
    assert "daily-local-intelligence" not in html
    assert not (tmp_path / "data" / "local-intelligence.json").exists()


def test_render_row_one_site_escapes_daily_local_intelligence(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.headline = '<script>alert("headline")</script>'
    story.entity_refs = [RowOneReference(name="<The Row>", type="brand", label="tracked")]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={
            story.id: RowOneLocalArticle(
                story_id=story.id,
                url="https://example.com/the-row",
                source_name="<Vogue>",
                extracted_at=AS_OF,
                paragraphs=['<script>alert("body")</script>'],
                content_sections=[
                    RowOneLocalArticleContentSection(
                        key="takeaways",
                        title=LocalizedText(
                            zh="<script>栏目</script>",
                            en="<script>Segment</script>",
                        ),
                        body=LocalizedText(
                            zh='<img src=x onerror="alert(1)"> 中文段说明',
                            en='<img src=x onerror="alert(1)"> segment body',
                        ),
                        items=[
                            RowOneLocalArticleContentItem(
                                label=LocalizedText(
                                    zh="<script>标签</script>",
                                    en="<script>Label</script>",
                                ),
                                body=LocalizedText(
                                    zh='<img src=x onerror="alert(2)"> 中文嵌套正文',
                                    en='<img src=x onerror="alert(2)"> nested body',
                                ),
                                references=[
                                    RowOneReference(
                                        name="<script>Nested Ref</script>",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                                paragraph_indices=[0],
                            )
                        ],
                    )
                ],
            )
        },
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert '<script>alert("body")</script>' not in html
    assert "<script>Segment</script>" not in html
    assert "<script>Label</script>" not in html
    assert "<script>Nested Ref</script>" not in html
    assert '<img src=x onerror="alert' not in html
    assert "&lt;The Row&gt;" in html
    assert "&lt;script&gt;Segment&lt;/script&gt;" in html
    assert "&lt;script&gt;Label&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=&quot;alert(2)&quot;&gt; nested body" in html
    assert "&lt;script&gt;Nested Ref&lt;/script&gt;" in html


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("details/the-row-signal-1234567890.html", "details/the-row-signal-1234567890.html"),
        (
            "details/the-row-signal-1234567890.html#local-article",
            "details/the-row-signal-1234567890.html#local-article",
        ),
        (
            "details/the-row-signal-1234567890.html#local-article-paragraph-1",
            "details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
        (
            "details/the-row-signal-1234567890.html#local-article-paragraph-42",
            "details/the-row-signal-1234567890.html#local-article-paragraph-42",
        ),
        ("details/the-row-signal-1234567890.html#local-article-paragraph-0", None),
        ("details/the-row-signal-1234567890.html#local-article-paragraph-x", None),
        ("details/the-row-signal-1234567890.html#local-article-body", None),
        ("details/the-row-signal-1234567890.html#local-article-content-section-1", None),
        ("details/the-row-signal-1234567890.html#summary", None),
        ("details/the-row-signal-1234567890.html#local-article#extra", None),
        ("../details/the-row-signal-1234567890.html#local-article", None),
        ("javascript:alert(1)", None),
        (None, None),
    ],
)
def test_safe_daily_local_intelligence_href_accepts_only_safe_detail_links(
    href: object,
    expected: str | None,
) -> None:
    assert _safe_daily_local_intelligence_href(href) == expected


def _saved_article_content_organization_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-content-organization"'
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    content_organization = tail.find('<section class="saved-article-content-organization"')
    if content_organization >= 0:
        boundary_offsets.append(content_organization)
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid">')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _daily_local_key_signals_digest_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-key-signals-digest"'
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]


def _daily_local_signal_momentum_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-signal-momentum"'
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]


def _daily_local_heat_signals_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-heat-signals"'
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]


def _daily_local_article_capsules_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-article-capsules"'
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_daily_summary_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-daily-summary"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid"')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_signal_facets_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-signal-facets"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid"')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_daily_signal_leaderboard_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-daily-signal-leaderboard"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid"')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_organization_jump_index_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-organization-jump-index"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid"')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_reading_queue_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-reading-queue"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid"')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_read_next_clusters_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-read-next-clusters"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid"')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_signal_facets_column_html(section_html: str, label: str) -> str:
    label_marker = f'<span data-lang="en">{label}</span>'
    assert label_marker in section_html
    label_start = section_html.index(label_marker)
    column_start = section_html.rfind(
        '<div class="saved-article-signal-facets-column">',
        0,
        label_start,
    )
    assert column_start >= 0
    next_column = section_html.find(
        '<div class="saved-article-signal-facets-column">',
        label_start,
    )
    row_end = section_html.find("</article>", label_start)
    column_end = row_end if next_column == -1 or row_end < next_column else next_column
    assert column_end > column_start
    return section_html[column_start:column_end]


def _saved_article_library_first_card_html(index_html: str) -> str:
    marker = '<article class="saved-article-library-card">'
    assert marker in index_html
    card_start = index_html.index(marker)
    next_card = index_html.find(marker, card_start + len(marker))
    source_boundary = index_html.find("</section>", card_start)
    card_end = next_card if next_card >= 0 else source_boundary
    assert card_end > card_start
    return index_html[card_start:card_end]


def _saved_article_library_first_source_html(index_html: str) -> str:
    marker = '<section class="saved-article-library-source"'
    assert marker in index_html
    source_start = index_html.index(marker)
    next_source = index_html.find(marker, source_start + len(marker))
    source_grid_end = index_html.find("</main>", source_start)
    section_end = (
        source_grid_end if source_grid_end >= 0 else index_html.find("</section>", source_start)
    )
    source_end = next_source if next_source >= 0 else section_end
    assert source_end > source_start
    return index_html[source_start:source_end]


def _saved_article_library_source_html(index_html: str, anchor_id: str) -> str:
    marker = f'<section class="saved-article-library-source" id="{anchor_id}"'
    assert marker in index_html
    source_start = index_html.index(marker)
    next_source = index_html.find(
        '<section class="saved-article-library-source"',
        source_start + len(marker),
    )
    source_grid_end = index_html.find("</main>", source_start)
    section_end = (
        source_grid_end if source_grid_end >= 0 else index_html.find("</section>", source_start)
    )
    source_end = next_source if next_source >= 0 else section_end
    assert source_end > source_start
    return index_html[source_start:source_end]


def _saved_article_source_brief_html(index_html: str) -> str:
    marker = '<div class="saved-article-source-brief"'
    assert marker in index_html
    start = index_html.index(marker)
    depth = 0
    position = start
    while position < len(index_html):
        open_position = index_html.find("<div", position)
        close_position = index_html.find("</div>", position)
        if close_position < 0:
            break
        if open_position >= 0 and open_position < close_position:
            depth += 1
            position = open_position + len("<div")
            continue
        depth -= 1
        position = close_position + len("</div>")
        if depth == 0:
            return index_html[start:position]
    raise AssertionError("Unbalanced div in saved article source brief HTML")


def _saved_article_body_guide_html(index_html: str) -> str:
    marker = '<div class="saved-article-body-guide"'
    assert marker in index_html
    start = index_html.index(marker)
    depth = 0
    position = start
    while position < len(index_html):
        open_position = index_html.find("<div", position)
        close_position = index_html.find("</div>", position)
        if close_position < 0:
            break
        if open_position >= 0 and open_position < close_position:
            depth += 1
            position = open_position + len("<div")
            continue
        depth -= 1
        position = close_position + len("</div>")
        if depth == 0:
            return index_html[start:position]
    raise AssertionError("Unbalanced div in saved article body guide HTML")


def _saved_article_theme_digest_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-theme-digest"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid">')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_reference_atlas_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-reference-atlas"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid">')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_evidence_board_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-evidence-board"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    content_organization = tail.find('<section class="saved-article-content-organization"')
    if content_organization >= 0:
        boundary_offsets.append(content_organization)
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid">')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def _saved_article_reading_paths_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-reading-paths"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    boundary_offsets: list[int] = []
    content_organization = tail.find('<section class="saved-article-content-organization"')
    if content_organization >= 0:
        boundary_offsets.append(content_organization)
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is not None:
        boundary_offsets.append(next_section.start())
    library_grid = tail.find('<div class="saved-article-library-grid">')
    if library_grid >= 0:
        boundary_offsets.append(library_grid)
    if not boundary_offsets:
        return index_html[section_start:]
    section_end = section_start + len(marker) + min(boundary_offsets)
    assert section_end > section_start
    return index_html[section_start:section_end]


def test_render_row_one_site_prefers_saved_article_reading_on_homepage(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="local-read-path"' in index_html
    assert "local-read-action" in index_html
    assert "Read saved article" in index_html
    assert "阅读本地正文" in index_html
    assert "Saved locally" in index_html
    assert "本地已保存" in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article"' in index_html
    assert '<span data-lang="en">Read the brief</span>' not in index_html
    assert '<span data-lang="en">Read brief</span>' not in index_html


def test_render_row_one_site_omits_homepage_local_first_action_without_saved_article(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path, local_articles_by_story_id={})

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="local-read-path"' not in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article"' not in index_html
    assert "Read saved article" not in index_html
    assert "阅读本地正文" not in index_html


def test_render_detail_html_puts_saved_article_action_before_external_source() -> None:
    edition = _edition()
    story = edition.stories[0]
    detail_html = render_detail_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'class="local-read-path detail-local-read-path"' in detail_html
    assert 'href="#local-article"' in detail_html
    assert "Read saved article" in detail_html
    assert "阅读本地正文" in detail_html
    assert detail_html.index('class="local-read-path detail-local-read-path"') < detail_html.index(
        "Open Source Article"
    )
    assert "打开原文" in detail_html


def test_render_row_one_site_saved_article_content_organization_links_evidence_paragraphs(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = _saved_article_content_organization_section_html(index_html)

    assert '<article class="saved-article-content-organization-card">' in section_html
    assert '<a class="saved-article-content-organization-card"' not in section_html
    assert 'class="saved-article-content-organization-card-link"' in section_html
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-content-section-'
        in section_html
    )
    assert 'class="saved-article-content-organization-evidence"' in section_html
    assert 'class="saved-article-content-organization-evidence-link"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert "Evidence paragraph 1" in section_html
    assert "证据段落 1" in section_html
    assert 'id="local-article-paragraph-1"' in detail_html


def test_render_index_html_filters_saved_article_content_organization_evidence_links() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 2),
        references=(),
    )
    invalid_path_cards = (
        replace(
            safe_card,
            title=LocalizedText(en="JS card", zh="JS 卡片"),
            detail_path="javascript:alert(1)",
        ),
        replace(
            safe_card,
            title=LocalizedText(en="Traversal card", zh="穿越卡片"),
            detail_path="../secrets.html#local-article-content-section-1",
        ),
        replace(
            safe_card,
            title=LocalizedText(en="Wrong fragment card", zh="错误片段卡片"),
            detail_path="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
    )
    bad_index_card = replace(
        safe_card,
        title=LocalizedText(en="Bad index card", zh="坏索引卡片"),
        paragraph_indices=(-1, True),
    )
    duplicate_card = replace(
        safe_card,
        title=LocalizedText(en="Duplicate card", zh="重复卡片"),
        paragraph_indices=(0, 0, 1),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, *invalid_path_cards, bad_index_card, duplicate_card],
            ),
        ]
    )

    index_html = render_index_html(
        _edition(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(index_html)

    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-3"' in section_html
    assert "javascript:alert" not in section_html
    assert "../secrets" not in section_html
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-paragraph-0"'
        not in section_html
    )
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"' in section_html
    assert (
        section_html.count(
            'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"'
        )
        == 1
    )
    assert "JS card" not in section_html
    assert "Traversal card" not in section_html
    assert "Wrong fragment card" not in section_html
    assert "Bad index card" in section_html
    assert section_html.count('class="saved-article-content-organization-card"') == 3
    assert (
        section_html.count(
            'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"'
        )
        == 2
    )


def test_render_saved_article_library_filters_content_organization_links_on_library_page() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 2),
        references=(),
    )
    invalid_path_cards = (
        replace(
            safe_card,
            title=LocalizedText(en="JS card", zh="JS 卡片"),
            detail_path="javascript:alert(1)#local-article-content-section-1",
        ),
        replace(
            safe_card,
            title=LocalizedText(en="Traversal card", zh="穿越卡片"),
            detail_path="../secrets.html#local-article-content-section-1",
        ),
        replace(
            safe_card,
            title=LocalizedText(en="Wrong fragment card", zh="错误片段卡片"),
            detail_path="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
    )
    bad_index_card = replace(
        safe_card,
        title=LocalizedText(en="Bad index card", zh="坏索引卡片"),
        paragraph_indices=(-1, True),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, *invalid_path_cards, bad_index_card],
            ),
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "1 summary fallback" in html
    assert "1 篇摘要兜底" in html
    assert "ROW ONE summary fallback" in html
    assert 'href="ROW ONE summary fallback"' not in html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
    ) in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-3"' in section_html
    )
    assert "javascript:alert" not in section_html
    assert "../secrets" not in section_html
    assert "#local-article-paragraph-0" not in section_html
    assert "#local-article-paragraph-2" not in section_html
    assert "JS card" not in section_html
    assert "Traversal card" not in section_html
    assert "Wrong fragment card" not in section_html
    assert "Bad index card" in section_html


def test_render_saved_article_library_canonicalizes_content_organization_links() -> None:
    card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Canonical card", zh="规范卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Canonical lead", zh="规范摘要"),
        detail_path="details/./the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[card],
            ),
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
    ) in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in (
        section_html
    )
    assert "details/./the-row-signal-1234567890.html" not in section_html


def test_render_saved_article_content_organization_includes_coverage_matrix() -> None:
    first_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row signal", zh="The Row 信号"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="A brand signal.", zh="一个品牌信号。"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1),
        references=(RowOneReference(name="The Row", type="brand", label="brand"),),
    )
    second_card = replace(
        first_card,
        section_label=LocalizedText(en="Products", zh="产品"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-2",
        paragraph_indices=(1, 2),
        references=(RowOneReference(name="Margaux", type="product", label="bag"),),
    )
    third_card = replace(
        first_card,
        title=LocalizedText(en="Alaia signal", zh="Alaia 信号"),
        source_name="Business of Fashion",
        detail_path="details/alaia-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(RowOneReference(name="Alaia", type="brand", label="brand"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[first_card, third_card],
            ),
            RowOneSavedArticleContentOrganizationGroup(
                key="products",
                title=LocalizedText(en="Products", zh="产品"),
                dek=LocalizedText(en="Product context", zh="产品背景"),
                cards=[second_card],
            ),
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)
    matrix_start = section_html.index('class="saved-article-organization-coverage-matrix"')
    matrix_end = section_html.index('class="saved-article-content-organization-groups"')
    matrix_html = section_html[matrix_start:matrix_end]

    assert 'class="saved-article-organization-coverage-matrix"' in section_html
    assert section_html.index('class="saved-article-organization-coverage-matrix"') < (
        section_html.index('class="saved-article-content-organization-groups"')
    )
    assert "The Row signal" in matrix_html
    assert "Alaia signal" in matrix_html
    assert "2 organized sections" in matrix_html
    assert "3 evidence paragraphs" in matrix_html
    assert "People &amp; Brands" in matrix_html
    assert "Products" in matrix_html
    assert "The Row" in matrix_html
    assert "Margaux" in matrix_html


def test_saved_article_organization_matrix_filters_unsafe_and_strict_counts() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe article", zh="安全文章"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 0, 1, True, -1, 99),
        references=(RowOneReference(name="Safe Ref", type="brand", label="tracked"),),
    )
    unsafe_card = replace(
        safe_card,
        title=LocalizedText(en="Unsafe article", zh="不安全文章"),
        source_name="Unsafe Source",
        detail_path="javascript:alert(1)#local-article-content-section-1",
        paragraph_indices=(0, 1, 2),
        references=(RowOneReference(name="Unsafe Ref", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, unsafe_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)
    matrix_start = section_html.index('class="saved-article-organization-coverage-matrix"')
    matrix_end = section_html.index('class="saved-article-content-organization-groups"')
    matrix_html = section_html[matrix_start:matrix_end]

    assert "Safe article" in matrix_html
    assert "Unsafe article" not in matrix_html
    assert "Unsafe Ref" not in matrix_html
    assert "Unsafe Source" not in matrix_html
    assert "2 evidence paragraphs" in matrix_html
    assert "3 evidence paragraphs" not in matrix_html
    assert "local-article-paragraph-100" not in section_html
    assert "javascript:alert" not in matrix_html


def test_saved_article_organization_matrix_caps_and_escapes_references() -> None:
    references = tuple(
        RowOneReference(name=f"Ref <{index}>", type="brand", label=f"Label <{index}>")
        for index in range(1, 8)
    )
    card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Reference article", zh="引用文章"),
        source_name="Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Lead", zh="摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=references,
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)
    matrix_start = section_html.index('class="saved-article-organization-coverage-matrix"')
    matrix_end = section_html.index('class="saved-article-content-organization-groups"')
    matrix_html = section_html[matrix_start:matrix_end]

    assert "Ref &lt;1&gt;" in matrix_html
    assert "Label &lt;1&gt;" in matrix_html
    assert "Ref <1>" not in matrix_html
    assert "Ref &lt;7&gt;" not in matrix_html


def test_render_saved_article_content_organization_group_summary() -> None:
    first_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="First summary card", zh="第一张摘要卡"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="First lead", zh="第一条摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1, 1),
        references=(
            RowOneReference(name="The Row", type="brand", label="brand"),
            RowOneReference(name="Margaux", type="product", label="bag"),
        ),
    )
    second_card = replace(
        first_card,
        title=LocalizedText(en="Second summary card", zh="第二张摘要卡"),
        source_name="Business of Fashion",
        detail_path="details/another-signal-1234567890.html#local-article-content-section-2",
        paragraph_indices=(0,),
        references=(RowOneReference(name="The Row", type="brand", label="brand"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[first_card, second_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)
    summary_start = section_html.index('class="saved-article-content-organization-summary"')
    summary_end = section_html.index(
        'class="saved-article-content-organization-grid"',
        summary_start,
    )
    summary_html = section_html[summary_start:summary_end]

    assert 'class="saved-article-content-organization-summary"' in section_html
    assert "2 saved cards" in section_html
    assert "2 saved articles" in section_html
    assert "2 sources" in section_html
    assert "3 evidence paragraphs" in section_html
    assert summary_html.count('class="saved-article-content-organization-summary-ref"') == 2
    assert summary_html.count("The Row") == 1
    assert "Margaux" in summary_html
    assert section_html.index('class="saved-article-content-organization-summary"') < (
        section_html.index('class="saved-article-content-organization-grid"')
    )


def test_content_organization_group_summary_dedupes_article_sections() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="First section", zh="第一栏目"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="First lead", zh="第一条摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    base_card,
                    replace(
                        base_card,
                        title=LocalizedText(en="Second section", zh="第二栏目"),
                        detail_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-2"
                        ),
                        paragraph_indices=(1,),
                    ),
                ],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "2 saved cards" in section_html
    assert "1 saved article" in section_html
    assert "1 source" in section_html
    assert "2 evidence paragraphs" in section_html


def test_render_saved_article_content_organization_group_summary_dedupes_sources() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="First source", zh="第一来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="First lead", zh="第一条摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    base_card,
                    replace(
                        base_card,
                        title=LocalizedText(en="Second source", zh="第二来源"),
                        source_name="  vogue   business  ",
                        detail_path=(
                            "details/another-signal-1234567890.html#local-article-content-section-2"
                        ),
                    ),
                ],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "2 saved cards" in section_html
    assert "2 saved articles" in section_html
    assert "1 source" in section_html
    assert "2 sources" not in section_html


def test_render_saved_article_content_organization_group_summary_filters_unsafe_cards() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe summary card", zh="安全摘要卡"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(RowOneReference(name="Safe Ref", type="brand", label="tracked"),),
    )
    unsafe_card = replace(
        safe_card,
        title=LocalizedText(en="Unsafe summary card", zh="不安全摘要卡"),
        source_name="Unsafe Source",
        detail_path="javascript:alert(1)#local-article-content-section-1",
        paragraph_indices=(0, 1, 2),
        references=(RowOneReference(name="Unsafe Ref", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, unsafe_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)

    assert "1 saved card" in section_html
    assert "1 saved article" in section_html
    assert "1 source" in section_html
    assert "1 evidence paragraph" in section_html
    assert "Safe Ref" in section_html
    assert "Unsafe Ref" not in section_html
    assert "Unsafe Source" not in section_html
    assert "javascript:alert" not in section_html


def test_render_saved_article_content_organization_group_summary_escapes_and_caps_refs() -> None:
    cards = []
    for index in range(1, 7):
        cards.append(
            RowOneSavedArticleContentOrganizationCard(
                title=LocalizedText(en=f"Card {index}", zh=f"卡片 {index}"),
                source_name="Source",
                section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                section_label=LocalizedText(en="Products", zh="产品"),
                lead=LocalizedText(en="Lead", zh="摘要"),
                detail_path=(
                    f"details/the-row-signal-1234567890.html#local-article-content-section-{index}"
                ),
                paragraph_indices=(0,),
                references=(
                    RowOneReference(
                        name=f"Ref <{index}>",
                        type="brand",
                        label=f"Label <{index}>",
                    ),
                ),
            )
        )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="products",
                title=LocalizedText(en="Products", zh="产品"),
                dek=LocalizedText(en="Product context", zh="产品背景"),
                cards=cards,
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(html)
    summary_start = section_html.index('class="saved-article-content-organization-summary"')
    summary_end = section_html.index(
        'class="saved-article-content-organization-grid"',
        summary_start,
    )
    summary_html = section_html[summary_start:summary_end]

    assert "Ref &lt;1&gt;" in summary_html
    assert "Label &lt;1&gt;" in summary_html
    assert "Ref <1>" not in summary_html
    assert "Ref &lt;6&gt;" not in summary_html


def test_render_saved_article_library_html_escapes_and_truncates_theme_digest() -> None:
    digest = RowOneSavedArticleThemeDigest(
        theme_count=1,
        item_count=1,
        source_count=1,
        themes=(
            RowOneSavedArticleThemeDigestTheme(
                key="read_first",
                title=LocalizedText(en="Read <First>", zh="优先<阅读>"),
                dek=LocalizedText(en="Theme dek", zh="主题说明"),
                item_count=1,
                source_count=1,
                items=(
                    RowOneSavedArticleThemeDigestItem(
                        title=LocalizedText(en="The Row <script>", zh="The Row"),
                        source_name="Source <Name>",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        section_label=LocalizedText(en="Read First", zh="优先阅读"),
                        lead=LocalizedText(en="Long lead " * 80, zh="长摘要" * 80),
                        detail_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                        references=(
                            RowOneReference(
                                name="The Row <brand>",
                                type="brand",
                                label="tracked",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_theme_digest=digest,
    )
    section_html = _saved_article_theme_digest_section_html(html)

    assert "Read &lt;First&gt;" in section_html
    assert "Source &lt;Name&gt;" in section_html
    assert "The Row &lt;script&gt;" in section_html
    assert "The Row &lt;brand&gt;" in section_html
    assert "<script>" not in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )
    assert "Long lead " * 80 not in section_html
    assert section_html.count("Long lead") < 80


def test_render_saved_article_library_html_filters_unsafe_theme_digest_items() -> None:
    safe_item = RowOneSavedArticleThemeDigestItem(
        title=LocalizedText(en="Safe theme item", zh="安全主题条目"),
        source_name="Safe Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Read First", zh="优先阅读"),
        lead=LocalizedText(en="Safe theme lead", zh="安全主题摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(),
        references=(),
    )
    digest = RowOneSavedArticleThemeDigest(
        theme_count=1,
        item_count=4,
        source_count=1,
        themes=(
            RowOneSavedArticleThemeDigestTheme(
                key="read_first",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Theme dek", zh="主题说明"),
                item_count=4,
                source_count=1,
                items=(
                    safe_item,
                    replace(
                        safe_item,
                        title=LocalizedText(en="Javascript item", zh="脚本条目"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_item,
                        title=LocalizedText(en="Traversal item", zh="越界条目"),
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_item,
                        title=LocalizedText(en="Bad fragment item", zh="坏锚点条目"),
                        detail_path="details/the-row-signal-1234567890.html#bad-fragment",
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_theme_digest=digest,
    )
    section_html = _saved_article_theme_digest_section_html(html)

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert "Safe theme item" in section_html
    assert "javascript:" not in section_html
    assert "../secret.html" not in section_html
    assert "#bad-fragment" not in section_html
    assert "Javascript item" not in section_html
    assert "Traversal item" not in section_html
    assert "Bad fragment item" not in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' not in (
        section_html
    )
    assert section_html.count('class="saved-article-theme-digest-item"') == 1


def test_render_saved_article_library_html_omits_empty_theme_digest_shell() -> None:
    html_without_digest = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_theme_digest=None,
    )
    empty_digest = RowOneSavedArticleThemeDigest(
        theme_count=0,
        item_count=0,
        source_count=0,
        themes=(),
    )
    html_with_empty_digest = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_theme_digest=empty_digest,
    )

    for html in (html_without_digest, html_with_empty_digest):
        assert 'class="saved-article-theme-digest"' not in html
        assert "Saved Article Theme Digest" not in html
        assert "保存文章主题简报" not in html
        assert 'class="saved-article-library-hero"' in html
        assert 'class="saved-article-library-grid"' in html


def test_render_saved_article_library_html_omits_article_page_link_without_allowlist() -> None:
    html = render_saved_article_library_html(_edition(), _saved_article_library_fixture())

    assert 'href="the-row-signal-1234567890.html"' not in html
    assert 'class="saved-article-library-primary-action"' not in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-reader"' in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-evidence"' in html
    )


def test_render_saved_article_library_html_revalidates_article_page_allowlist_hrefs() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "javascript:alert(1).html",
        },
    )

    assert "javascript:alert" not in html
    assert 'class="saved-article-library-primary-action"' not in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-reader"' in html


def test_render_saved_article_library_html_filters_unsafe_reference_atlas_supports() -> None:
    safe_support = RowOneSavedArticleReferenceAtlasSupport(
        title=LocalizedText(en="Safe atlas support", zh="安全图谱支撑"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe <script>atlas lead</script>", zh="安全图谱摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
    )
    unsafe_supports = (
        replace(
            safe_support,
            title=LocalizedText(en="JS atlas support", zh="脚本图谱支撑"),
            lead=LocalizedText(en="JS atlas lead", zh="脚本图谱摘要"),
            detail_path="javascript:alert(1)#local-article-content-section-1",
        ),
        replace(
            safe_support,
            title=LocalizedText(en="Traversal atlas support", zh="越界图谱支撑"),
            lead=LocalizedText(en="Traversal atlas lead", zh="越界图谱摘要"),
            detail_path="../secret.html#local-article-content-section-1",
        ),
        replace(
            safe_support,
            title=LocalizedText(en="Bad fragment atlas support", zh="坏锚点图谱支撑"),
            lead=LocalizedText(en="Bad fragment atlas lead", zh="坏锚点图谱摘要"),
            detail_path="details/the-row-signal-1234567890.html#bad-fragment",
        ),
    )
    atlas = RowOneSavedArticleReferenceAtlas(
        bucket_count=1,
        reference_count=1,
        support_count=4,
        source_count=1,
        buckets=(
            RowOneSavedArticleReferenceAtlasBucket(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                dek=LocalizedText(en="Brand references", zh="品牌引用"),
                reference_count=1,
                support_count=4,
                source_count=1,
                references=(
                    RowOneSavedArticleReferenceAtlasEntry(
                        name="The Row <brand>",
                        reference_type="brand",
                        label="tracked",
                        support_count=4,
                        source_count=1,
                        supports=(safe_support, *unsafe_supports),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reference_atlas=atlas,
    )
    section_html = _saved_article_reference_atlas_section_html(html)

    assert "Safe atlas support" in section_html
    assert "Safe &lt;script&gt;atlas lead&lt;/script&gt;" in section_html
    assert "The Row &lt;brand&gt;" in section_html
    assert "<script>" not in section_html
    assert "javascript:alert" not in section_html
    assert "../secret" not in section_html
    assert "#bad-fragment" not in section_html
    assert "JS atlas support" not in section_html
    assert "Traversal atlas support" not in section_html
    assert "Bad fragment atlas support" not in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    )


def test_render_saved_article_library_html_omits_empty_reference_atlas_shell() -> None:
    html_without_atlas = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reference_atlas=None,
    )
    empty_atlas = RowOneSavedArticleReferenceAtlas(
        bucket_count=0,
        reference_count=0,
        support_count=0,
        source_count=0,
        buckets=(),
    )
    html_with_empty_atlas = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reference_atlas=empty_atlas,
    )

    for html in (html_without_atlas, html_with_empty_atlas):
        assert 'class="saved-article-reference-atlas"' not in html
        assert "Saved Article Reference Atlas" not in html
        assert "保存文章引用图谱" not in html
        assert 'class="saved-article-library-hero"' in html
        assert 'class="saved-article-library-grid"' in html


def test_render_saved_article_library_shows_organized_snippets_on_source_cards() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert 'class="saved-article-body-guide"' in grid_html
    assert 'class="saved-article-body-guide-item"' in grid_html
    assert "What this article says" in grid_html
    assert "正文导读" in grid_html
    assert "People &amp; Brands" in grid_html
    assert "品牌与人物" in grid_html
    assert "Safe lead" in grid_html
    assert "安全摘要" in grid_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in grid_html
    )
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in grid_html
    assert grid_html.index("Safe lead") < grid_html.index('class="saved-article-library-actions"')


def test_render_saved_article_library_filters_unsafe_organized_snippets() -> None:
    def card(
        title: str,
        detail_path: str,
        lead: str,
    ) -> RowOneSavedArticleContentOrganizationCard:
        return RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=title, zh=title),
            source_name="Source",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
            lead=LocalizedText(en=lead, zh=lead),
            detail_path=detail_path,
            paragraph_indices=(0,),
            references=(),
        )

    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    card(
                        "Valid card",
                        "details/the-row-signal-1234567890.html#local-article-content-section-1",
                        "Safe <script>lead</script>",
                    ),
                    card(
                        "JS card",
                        "javascript:alert(1)#local-article-content-section-1",
                        "JS lead",
                    ),
                    card(
                        "Traversal card",
                        "../secrets.html#local-article-content-section-1",
                        "Traversal lead",
                    ),
                    card(
                        "Wrong fragment card",
                        "details/the-row-signal-1234567890.html#local-article-paragraph-1",
                        "Wrong fragment lead",
                    ),
                ],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert "Safe &lt;script&gt;lead&lt;/script&gt;" in grid_html
    assert "<script>" not in grid_html
    assert "javascript:alert" not in grid_html
    assert "../secrets" not in grid_html
    assert "JS lead" not in grid_html
    assert "Traversal lead" not in grid_html
    assert "Wrong fragment lead" not in grid_html


def test_render_saved_article_library_omits_snippets_for_unsafe_entry_paths() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )
    fixture = _saved_article_library_fixture()
    entry = replace(
        fixture.groups[0].entries[0],
        reader_path="../outside.html#local-article-reader",
        digest_path="javascript:alert(1)#local-article-digest",
        evidence_path="details/the-row-signal-1234567890.html#wrong-fragment",
    )
    fixture = replace(fixture, groups=[replace(fixture.groups[0], entries=[entry])])

    html = render_saved_article_library_html(
        _edition(),
        fixture,
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert 'class="saved-article-body-guide"' not in grid_html
    assert "Safe lead" not in grid_html
    assert "javascript:alert" not in grid_html
    assert "../outside" not in grid_html


def test_render_saved_article_library_canonicalizes_caps_and_truncates_organized_snippets() -> None:
    long_lead = (
        "Canonical lead starts with The Row and keeps going long enough that the saved "
        "article library card should show a capped excerpt instead of a full organized "
        "content body ending with a unique tail marker."
    )
    cards = [
        RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=f"Card {index}", zh=f"卡片 {index}"),
            source_name="Source",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
            lead=LocalizedText(
                en=long_lead if index == 0 else f"Lead {index}",
                zh="中文摘要",
            ),
            detail_path=(
                "details/./the-row-signal-1234567890.html#local-article-content-section-1"
                if index == 0
                else (
                    "details/the-row-signal-1234567890.html"
                    f"#local-article-content-section-{index + 1}"
                )
            ),
            paragraph_indices=(0,),
            references=(),
        )
        for index in range(5)
    ]
    cards.insert(1, cards[0])
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=cards,
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]
    guide_html = _saved_article_body_guide_html(grid_html)

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in grid_html
    )
    assert "details/./the-row-signal-1234567890.html" not in grid_html
    assert grid_html.count('class="saved-article-body-guide-item"') == 2
    assert guide_html.count("Canonical lead starts with The Row") == 1
    assert "…" in guide_html
    assert "unique tail marker" not in grid_html


def test_render_row_one_site_includes_saved_article_body_guide_in_article_cards(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    card_html = _saved_article_library_first_card_html(library_html)
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert 'class="saved-article-body-guide"' in card_html
    assert "What this article says" in card_html
    assert "正文导读" in card_html
    assert "Start with The Row retail signal." in card_html
    assert "先看 The Row 零售信号。" in card_html
    assert "People &amp; Brands" in card_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in card_html
    assert card_html.index('class="saved-article-body-guide"') < card_html.index(
        'class="saved-article-library-refs"'
    )
    assert 'class="saved-article-body-guide"' not in (tmp_path / "index.html").read_text(
        encoding="utf-8"
    )

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_body_guide" not in contract_json
        assert "article_body_guide" not in contract_json
        assert "saved-article-body-guide" not in contract_json
        assert "article-body-guide" not in contract_json
        assert "What this article says" not in contract_json
        assert "正文导读" not in contract_json
    assert not (tmp_path / "data" / "saved-article-body-guide.json").exists()


def test_render_row_one_site_includes_saved_article_source_brief_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _theme_digest_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    source_html = _saved_article_library_first_source_html(library_html)
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())

    assert 'class="saved-article-source-brief"' in source_html
    assert "Source Brief" in source_html
    assert "来源简报" in source_html
    assert "Vogue Business" in source_html
    assert "1 saved article" in source_html
    assert "3 saved paragraphs" in source_html
    assert "3 organized sections" in source_html
    assert "Start with The Row retail signal." in source_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in source_html
    )
    assert source_html.index('class="saved-article-library-source-header"') < source_html.index(
        'class="saved-article-source-brief"'
    )
    assert source_html.index('class="saved-article-source-brief"') < source_html.index(
        'class="saved-article-library-source-grid"'
    )
    assert 'class="saved-article-source-brief"' not in (tmp_path / "index.html").read_text(
        encoding="utf-8"
    )

    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_source_brief" not in contract_json
        assert "source_brief" not in contract_json
        assert "source-brief" not in contract_json
        assert "saved-article-source-brief" not in contract_json
        assert "Source Brief" not in contract_json
    assert not (tmp_path / "data" / "saved-article-source-brief.json").exists()


def test_render_saved_article_library_body_guide_escapes_dedupes_and_caps() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row source", zh="The Row 来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People <Brands>", zh="品牌 <人物>"),
        lead=LocalizedText(
            en="Long <script>body</script> " + ("detail " * 80),
            zh="很长 <script>正文</script> " + ("细节 " * 80),
        ),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    base_card,
                    replace(base_card),
                    replace(
                        base_card,
                        section_label=LocalizedText(en="Products", zh="单品"),
                        lead=LocalizedText(en="Second body guide.", zh="第二条正文导读。"),
                        paragraph_indices=(1,),
                    ),
                    replace(
                        base_card,
                        section_label=LocalizedText(en="Overflow", zh="溢出"),
                        lead=LocalizedText(en="Third body guide.", zh="第三条正文导读。"),
                        paragraph_indices=(2,),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    guide_html = _saved_article_body_guide_html(html)

    assert 'class="saved-article-body-guide"' in guide_html
    assert guide_html.count('class="saved-article-body-guide-item"') == 2
    assert "People &lt;Brands&gt;" in guide_html
    assert "Long &lt;script&gt;body&lt;/script&gt;" in guide_html
    assert "<script>" not in guide_html
    assert guide_html.count("Long &lt;script&gt;body&lt;/script&gt;") == 1
    assert "Second body guide." in guide_html
    assert "Third body guide." not in guide_html
    assert guide_html.count("detail") < 80


def test_render_saved_article_library_body_guide_filters_unsafe_hrefs() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe", zh="安全"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Safe guide", zh="安全导读"),
        lead=LocalizedText(en="Safe body guide.", zh="安全正文导读。"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Script guide", zh="脚本导读"),
                        lead=LocalizedText(en="Script body guide.", zh="脚本正文导读。"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Traversal guide", zh="越界导读"),
                        lead=LocalizedText(en="Traversal body guide.", zh="越界正文导读。"),
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Boolean guide", zh="布尔导读"),
                        lead=LocalizedText(en="Boolean body guide.", zh="布尔正文导读。"),
                        paragraph_indices=(True,),
                    ),
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Negative guide", zh="负数导读"),
                        lead=LocalizedText(en="Negative body guide.", zh="负数正文导读。"),
                        paragraph_indices=(-1,),
                    ),
                    safe_card,
                    replace(
                        safe_card,
                        section_label=LocalizedText(en="Second safe guide", zh="第二条安全导读"),
                        lead=LocalizedText(en="Second safe body guide.", zh="第二条安全正文导读。"),
                        paragraph_indices=(0,),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    guide_html = _saved_article_body_guide_html(html)

    assert "Safe body guide." in guide_html
    assert "Second safe body guide." in guide_html
    assert "Script body guide." not in guide_html
    assert "Traversal body guide." not in guide_html
    assert "Boolean body guide." not in guide_html
    assert "Negative body guide." not in guide_html
    assert "javascript:" not in guide_html
    assert "../secret.html" not in guide_html
    assert "#local-article-paragraph-True" not in guide_html
    assert "#local-article-paragraph-0" not in guide_html


def test_render_saved_article_library_html_omits_empty_body_guide_shell() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=None,
    )

    assert 'class="saved-article-body-guide"' not in html
    assert "What this article says" not in html


def test_render_saved_article_library_source_brief_escapes_dedupes_and_caps() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row source", zh="The Row 来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People <Brands>", zh="品牌 <人物>"),
        lead=LocalizedText(
            en="Long <script>source</script> " + ("detail " * 80),
            zh="很长 <script>来源</script> " + ("细节 " * 80),
        ),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    base_card,
                    replace(base_card),
                    replace(
                        base_card,
                        section_label=LocalizedText(en="Products", zh="单品"),
                        lead=LocalizedText(en="Second source brief.", zh="第二条来源简报。"),
                        paragraph_indices=(1,),
                    ),
                    replace(
                        base_card,
                        section_label=LocalizedText(en="Overflow", zh="溢出"),
                        lead=LocalizedText(en="Third source brief.", zh="第三条来源简报。"),
                        paragraph_indices=(2,),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    source_html = _saved_article_library_first_source_html(html)
    brief_html = _saved_article_source_brief_html(source_html)

    assert 'class="saved-article-source-brief"' in source_html
    assert brief_html.count('class="saved-article-source-brief-item"') == 2
    assert "People &lt;Brands&gt;" in brief_html
    assert "Long &lt;script&gt;source&lt;/script&gt;" in brief_html
    assert "<script>" not in brief_html
    assert brief_html.count("Long &lt;script&gt;source&lt;/script&gt;") == 1
    assert "Second source brief." in brief_html
    assert "Third source brief." not in brief_html
    assert brief_html.count("detail") < 80
    assert "…" in brief_html


def test_render_saved_article_library_source_brief_filters_unsafe_content_links() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row source", zh="The Row 来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Safe source", zh="安全来源"),
        lead=LocalizedText(en="Safe source brief.", zh="安全来源简报。"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    unsafe_organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Script source brief.", zh="脚本来源简报。"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Traversal source brief.", zh="越界来源简报。"),
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                ],
            )
        ],
    )
    safe_organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[safe_card],
            )
        ],
    )

    unsafe_html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=unsafe_organization,
    )
    safe_html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=safe_organization,
    )

    unsafe_brief_html = _saved_article_source_brief_html(unsafe_html)
    safe_brief_html = _saved_article_source_brief_html(safe_html)

    assert "Script source brief." not in unsafe_brief_html
    assert "Traversal source brief." not in unsafe_brief_html
    assert "The Row source" in unsafe_brief_html
    assert "javascript:" not in unsafe_html
    assert "../secret.html" not in unsafe_html
    assert 'class="saved-article-source-brief"' in safe_brief_html
    assert "Safe source brief." in safe_brief_html


def test_render_saved_article_library_source_brief_falls_back_to_entry_summary() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=None,
    )

    source_html = _saved_article_library_first_source_html(html)
    brief_html = _saved_article_source_brief_html(source_html)

    assert 'class="saved-article-source-brief"' in brief_html
    assert "The Row source" in brief_html
    assert "Top Stories" in brief_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in brief_html


def test_render_saved_article_library_source_brief_fallback_local_page_targets_digest() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=None,
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
        },
    )
    brief_html = _saved_article_source_brief_html(html)

    assert 'href="the-row-signal-1234567890.html#local-article-digest"' in brief_html
    assert 'href="the-row-signal-1234567890.html">' not in brief_html


def test_render_saved_article_library_source_brief_omits_empty_shell_without_safe_items() -> None:
    unsafe_entry = RowOneSavedArticleLibraryEntry(
        title=LocalizedText(zh="Unsafe source", en="Unsafe source"),
        source_name="Vogue Business",
        section_title=LocalizedText(zh="今日重点", en="Top Stories"),
        saved_paragraph_count=1,
        organized_section_count=1,
        body_source="summary_fallback",
        digest_path="../secret.html#local-article-digest",
        reader_path="../secret.html#local-article-reader",
        evidence_path="../secret.html#local-article-paragraph-evidence",
    )
    library = RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=1,
        organized_section_count=1,
        extracted_article_count=0,
        summary_fallback_article_count=1,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=1,
                organized_section_count=1,
                entries=[unsafe_entry],
            )
        ],
    )
    unsafe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Unsafe card", zh="不安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Unsafe source", zh="不安全来源"),
        lead=LocalizedText(en="Unsafe source brief.", zh="不安全来源简报。"),
        detail_path="javascript:alert(1)#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[unsafe_card],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        library,
        saved_article_content_organization=organization,
    )

    assert 'class="saved-article-source-brief"' not in html
    assert "Unsafe source brief." not in html
    assert "javascript:" not in html


def test_render_saved_article_library_source_brief_spreads_items_across_entries() -> None:
    base_entry = _saved_article_library_fixture().groups[0].entries[0]
    second_entry = replace(
        base_entry,
        title=LocalizedText(zh="Coach source", en="Coach source"),
        digest_path="details/coach-signal-1234567890.html#local-article-digest",
        reader_path="details/coach-signal-1234567890.html#local-article-reader",
        evidence_path="details/coach-signal-1234567890.html#local-article-paragraph-evidence",
    )
    library = RowOneSavedArticleLibrary(
        article_count=2,
        source_count=1,
        saved_paragraph_count=2,
        organized_section_count=2,
        extracted_article_count=0,
        summary_fallback_article_count=2,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=2,
                saved_paragraph_count=2,
                organized_section_count=2,
                entries=[base_entry, second_entry],
            )
        ],
    )

    def source_card(
        story_id: str,
        label: str,
        lead: str,
    ) -> RowOneSavedArticleContentOrganizationCard:
        return RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=label, zh=label),
            source_name="Vogue Business",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en=label, zh=label),
            lead=LocalizedText(en=lead, zh=lead),
            detail_path=f"details/{story_id}.html#local-article-content-section-1",
            paragraph_indices=(0,),
            references=(),
        )

    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    source_card("the-row-signal-1234567890", "The Row", "First The Row brief."),
                    source_card(
                        "the-row-signal-1234567890",
                        "The Row Overflow",
                        "Second The Row brief.",
                    ),
                    source_card("coach-signal-1234567890", "Coach", "First Coach brief."),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        library,
        saved_article_content_organization=organization,
    )
    brief_html = _saved_article_source_brief_html(html)

    assert "First The Row brief." in brief_html
    assert "First Coach brief." in brief_html
    assert "Second The Row brief." not in brief_html


def test_render_saved_article_library_source_brief_dedupes_with_bilingual_text() -> None:
    base_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row source", zh="The Row 来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People", zh="人物"),
        lead=LocalizedText(en="Same English lead.", zh="第一条中文。"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[
                    base_card,
                    replace(
                        base_card,
                        section_label=LocalizedText(en="People", zh="品牌"),
                        lead=LocalizedText(en="Same English lead.", zh="第二条中文。"),
                        paragraph_indices=(1,),
                    ),
                ],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    brief_html = _saved_article_source_brief_html(html)

    assert brief_html.count('class="saved-article-source-brief-item"') == 2
    assert "第一条中文。" in brief_html
    assert "第二条中文。" in brief_html


def test_render_saved_article_library_source_brief_omits_label_only_items() -> None:
    blank_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="The Row source", zh="The Row 来源"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Label only", zh="只有标签"),
        lead=LocalizedText(en="   ", zh="   "),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体上下文"),
                cards=[blank_card],
            )
        ],
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    brief_html = _saved_article_source_brief_html(html)

    assert "Label only" not in brief_html
    assert "The Row source" in brief_html


def test_render_saved_article_library_filters_unsafe_reading_path_view_model_steps() -> None:
    safe_step = RowOneSavedArticleReadingPathStep(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe <script>lead</script>", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
    )
    unsafe_steps = [
        replace(
            safe_step,
            lead=LocalizedText(en="JS lead", zh="脚本摘要"),
            detail_path="javascript:alert(1)#local-article-content-section-1",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Traversal lead", zh="越界摘要"),
            detail_path="../secrets.html#local-article-content-section-1",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Paragraph-fragment lead", zh="段落锚点摘要"),
            detail_path="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Zero-section lead", zh="零栏目摘要"),
            detail_path="details/the-row-signal-1234567890.html#local-article-content-section-0",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Padded-section lead", zh="补零栏目摘要"),
            detail_path="details/the-row-signal-1234567890.html#local-article-content-section-01",
        ),
    ]
    reading_paths = RowOneSavedArticleReadingPaths(
        path_count=1,
        step_count=1 + len(unsafe_steps),
        paths=(
            RowOneSavedArticleReadingPath(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                step_count=1 + len(unsafe_steps),
                steps=(safe_step, *unsafe_steps),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reading_paths=reading_paths,
    )
    section_html = _saved_article_reading_paths_section_html(html)

    assert "Safe &lt;script&gt;lead&lt;/script&gt;" in section_html
    assert "1 step" in section_html
    assert "1 个步骤" in section_html
    assert "<script>" not in section_html
    assert "javascript:alert" not in section_html
    assert "../secrets" not in section_html
    assert "JS lead" not in section_html
    assert "Traversal lead" not in section_html
    assert "Paragraph-fragment lead" not in section_html
    assert "Zero-section lead" not in section_html
    assert "Padded-section lead" not in section_html


def test_render_saved_article_library_reading_path_hrefs_match_local_anchor_allowlist() -> None:
    safe_step = RowOneSavedArticleReadingPathStep(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1),
    )
    reading_paths = RowOneSavedArticleReadingPaths(
        path_count=1,
        step_count=1,
        paths=(
            RowOneSavedArticleReadingPath(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                step_count=1,
                steps=(safe_step,),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reading_paths=reading_paths,
    )
    section_html = _saved_article_reading_paths_section_html(html)
    hrefs = re.findall(r'href="([^"]+)"', section_html)

    assert hrefs
    for href in hrefs:
        assert re.fullmatch(
            r"\.\./details/[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html"
            r"#local-article-(?:content-section|paragraph)-[1-9][0-9]*",
            href,
        )


def test_render_saved_article_library_omits_reading_paths_for_unsafe_entry_paths() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )
    fixture = _saved_article_library_fixture()
    entry = replace(
        fixture.groups[0].entries[0],
        reader_path="../outside.html#local-article-reader",
        digest_path="javascript:alert(1)#local-article-digest",
        evidence_path="details/the-row-signal-1234567890.html#wrong-fragment",
    )
    fixture = replace(fixture, groups=[replace(fixture.groups[0], entries=[entry])])
    reading_paths = build_row_one_saved_article_reading_paths(fixture, organization)

    html = render_saved_article_library_html(
        _edition(),
        fixture,
        saved_article_content_organization=organization,
        saved_article_reading_paths=reading_paths,
    )

    assert 'class="saved-article-reading-paths"' not in html
    assert "Safe lead" not in html[: html.index('class="saved-article-content-organization"')]


def test_render_saved_article_library_canonicalizes_caps_and_truncates_reading_paths() -> None:
    long_lead = (
        "Canonical reading path starts with The Row and keeps going long enough that "
        "the saved article reading path should show a capped excerpt instead of a "
        "full organized content body ending with a unique reading path tail marker."
    )
    cards = [
        RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=f"Card {index}", zh=f"卡片 {index}"),
            source_name="Source",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
            lead=LocalizedText(
                en=long_lead if index == 0 else f"Lead {index}",
                zh="中文摘要",
            ),
            detail_path=(
                "details/./the-row-signal-1234567890.html#local-article-content-section-1"
                if index == 0
                else (
                    "details/the-row-signal-1234567890.html"
                    f"#local-article-content-section-{index + 1}"
                )
            ),
            paragraph_indices=(0,),
            references=(),
        )
        for index in range(5)
    ]
    cards.insert(1, cards[0])
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=cards,
            )
        ]
    )
    fixture = _saved_article_library_fixture()
    reading_paths = build_row_one_saved_article_reading_paths(fixture, organization)

    html = render_saved_article_library_html(
        _edition(),
        fixture,
        saved_article_content_organization=organization,
        saved_article_reading_paths=reading_paths,
    )
    section_html = _saved_article_reading_paths_section_html(html)

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert "details/./the-row-signal-1234567890.html" not in section_html
    assert section_html.count('class="saved-article-reading-path-step"') == 3
    assert section_html.count("Canonical reading path starts with The Row") == 1
    assert "…" in section_html
    assert "unique reading path tail marker" not in section_html


def test_render_saved_article_library_renders_skipped_text_source_chip() -> None:
    fixture = _saved_article_library_fixture()
    entry = replace(fixture.groups[0].entries[0], body_source="skipped")
    fixture = replace(
        fixture,
        extracted_article_count=0,
        summary_fallback_article_count=0,
        skipped_article_count=1,
        groups=[replace(fixture.groups[0], entries=[entry])],
    )

    html = render_saved_article_library_html(_edition(), fixture)

    assert '<li class="saved-article-library-text-source">' in html
    assert '<span data-lang="en">Text source</span>' in html
    assert '<span data-lang="zh">正文来源</span>' in html
    assert "Skipped" in html
    assert "1 skipped" in html
    assert "1 篇跳过" in html
    assert "1 summary fallback" not in html
    assert "ROW ONE summary fallback" not in html


def test_render_index_html_caps_and_dedupes_saved_article_content_organization_evidence_links() -> (
    None
):
    card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Evidence card", zh="证据卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Lead", zh="摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1, 1, 2, 3, 4),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[card],
            ),
        ]
    )

    index_html = render_index_html(
        _edition(),
        saved_article_content_organization=organization,
    )
    section_html = _saved_article_content_organization_section_html(index_html)

    assert section_html.count('class="saved-article-content-organization-evidence-link"') == 3
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-3"' in section_html
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-paragraph-4"'
        not in section_html
    )
    assert (
        section_html.count(
            'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"'
        )
        == 1
    )


def test_render_row_one_detail_information_map_escapes_story_values(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].source_name = "Vogue <signals> Business"
    render_row_one_site(edition, tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    map_match = re.search(
        r'<section class="detail-information-map"(?P<map>.*?)</section>',
        detail_html,
        re.S,
    )

    assert map_match is not None
    map_html = map_match.group("map")
    assert "Vogue &lt;signals&gt; Business" in map_html
    assert "Vogue <signals> Business" not in map_html


def test_render_row_one_site_includes_lead_story_block(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="lead-story"' in index_html
    assert "Lead Story" in index_html
    assert "今日头条" in index_html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in index_html
    assert "The Row is today&#x27;s priority signal." in index_html


def test_render_row_one_site_includes_signal_synthesis_section(tmp_path) -> None:
    edition = _edition()
    edition.stories[0] = edition.stories[0].model_copy(
        deep=True,
        update={
            "entity_refs": [
                RowOneReference(name="The Row", type="brand", label="rising"),
            ],
        },
    )

    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="signal-synthesis"' in index_html
    assert "Signal Synthesis" in index_html
    assert "Local observed signals; review required." in index_html
    assert (
        "The Row appears in 1 story, with max local mention delta +0 and 1 evidence link."
        in index_html
    )
    assert 'href="details/the-row-signal-1234567890.html"' in index_html
    assert index_html.index('class="edition-brief"') < index_html.index('class="signal-synthesis"')
    assert index_html.index('class="signal-synthesis"') < index_html.index('class="lead-story"')


def test_render_row_one_site_rejects_misaligned_signal_story_refs(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    edition = _edition()
    edition.stories[0] = edition.stories[0].model_copy(
        deep=True,
        update={
            "entity_refs": [
                RowOneReference(name="The Row", type="brand", label="rising"),
            ],
        },
    )

    def divergent_topics(stories: list[dict[str, object]]) -> list[dict[str, object]]:
        card = dict(stories[0])
        card["id"] = "different-story-2222222222"
        return [
            {
                "id": "brand-1234567890",
                "topic_type": "brand",
                "title": {"zh": "The Row", "en": "The Row"},
                "label": {"zh": "品牌", "en": "Brand"},
                "story_count": 1,
                "evidence_count": 1,
                "positive_heat_delta_sum": 0,
                "max_heat_delta": 0,
                "lead_story_id": "the-row-signal-1234567890",
                "story_ids": ["the-row-signal-1234567890"],
                "cards": [card],
                "source_refs": [{"name": "The Row", "type": "brand", "label": "rising"}],
            }
        ]

    monkeypatch.setattr(row_one_render, "briefing_topics_payload", divergent_topics)

    with pytest.raises(ValueError, match="story_refs must align with topic story_ids"):
        render_row_one_site(edition, tmp_path)


def test_render_row_one_site_localizes_signal_synthesis_meta(tmp_path) -> None:
    edition = _edition()
    edition.stories[0] = edition.stories[0].model_copy(
        deep=True,
        update={
            "entity_refs": [
                RowOneReference(name="The Row", type="brand", label="rising"),
            ],
        },
    )

    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    meta_match = re.search(
        r'<div class="signal-synthesis-meta">(?P<meta>.*?)</div>',
        index_html,
        re.S,
    )

    assert meta_match is not None
    meta_html = meta_match.group("meta")
    assert '<span data-lang="en">rising</span>' in meta_html
    assert '<span data-lang="zh">rising</span>' in meta_html
    assert '<span data-lang="en">1 story</span>' in meta_html
    assert '<span data-lang="zh">1 条故事</span>' in meta_html
    assert '<span data-lang="en">1 evidence link</span>' in meta_html
    assert '<span data-lang="zh">1 条证据链接</span>' in meta_html
    assert '<span data-lang="en">+0 local delta</span>' in meta_html
    assert '<span data-lang="zh">+0 本地增量</span>' in meta_html
    assert "1 stories" not in meta_html


def test_render_row_one_site_omits_empty_signal_synthesis_section() -> None:
    index_html = render_index_html(_edition(), app_payload={"signal_synthesis": {"groups": []}})

    assert 'class="signal-synthesis"' not in index_html


def test_render_row_one_site_includes_briefing_topics_index(tmp_path) -> None:
    edition = _edition()
    base_story = edition.stories[0]
    edition.stories = [
        base_story.model_copy(
            deep=True,
            update={
                "id": "the-row-topic-1111111111",
                "headline": 'The Row <topic> "brief"',
                "detail_path": "details/the-row-topic-1111111111.html",
                "heat_delta": 2,
                "entity_refs": [RowOneReference(name="The Row", type="brand", label="rising")],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "margaux-topic-2222222222",
                "headline": "Margaux topic",
                "detail_path": "details/margaux-topic-2222222222.html",
                "heat_delta": 7,
                "product_refs": [RowOneReference(name="Margaux", type="product", label="rising")],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "olsen-topic-3333333333",
                "headline": "Designer topic",
                "detail_path": "details/olsen-topic-3333333333.html",
                "designer_refs": [
                    RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer")
                ],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "zoe-topic-4444444444",
                "headline": "Person topic",
                "detail_path": "details/zoe-topic-4444444444.html",
                "entity_refs": [
                    RowOneReference(name="Zoe Kravitz", type="celebrity", label="style")
                ],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "fifth-topic-5555555555",
                "headline": "Fifth topic",
                "detail_path": "details/fifth-topic-5555555555.html",
                "heat_delta": 0,
                "entity_refs": [RowOneReference(name="Fifth Brand", type="brand", label="monitor")],
            },
        ),
    ]

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    app_topics = edition_payload["daily_digest"]["briefing_topics"]
    topic_match = re.search(
        r'<section id="briefing-topics" class="briefing-topics" aria-label="Briefing topics">'
        r"(?P<topics>.*?)</section>",
        index_html,
        re.S,
    )

    assert topic_match is not None
    topics_html = topic_match.group("topics")
    assert "Briefing Topics" in topics_html
    assert "今日主题" in topics_html
    assert "Organized Signals" in topics_html
    assert "整理后的时尚信号" in topics_html
    assert "The Row" in topics_html
    assert "Margaux" in topics_html
    assert "Mary-Kate Olsen" in topics_html
    assert "Zoe Kravitz" in topics_html
    assert "Brand" in topics_html
    assert "Product" in topics_html
    assert "Designer" in topics_html
    assert "Person" in topics_html
    assert "The Row &lt;topic&gt; &quot;brief&quot;" in topics_html
    assert 'href="details/the-row-topic-1111111111.html"' in topics_html
    topic_cards = re.findall(
        r'<a class="briefing-topic-card [^"]+" href="[^"]+">.*?</a>',
        topics_html,
        re.S,
    )
    assert len(topic_cards) == 4
    for topic, topic_card_html in zip(app_topics[:4], topic_cards, strict=True):
        lead_card = topic["cards"][0]
        assert topic["title"]["en"] in topic_card_html
        assert topic["label"]["en"] in topic_card_html
        assert f'href="{lead_card["detail_href"]}"' in topic_card_html
        assert escape(lead_card["headline"]) in topic_card_html
        assert f"{topic['story_count']} story" in topic_card_html
        evidence_label = (
            "1 evidence link"
            if topic["evidence_count"] == 1
            else f"{topic['evidence_count']} evidence links"
        )
        assert evidence_label in topic_card_html
    assert app_topics[4]["title"]["en"] == "Fifth Brand"
    hidden_lead_card = app_topics[4]["cards"][0]
    assert "Fifth Brand" not in topics_html
    assert hidden_lead_card["detail_href"] not in topics_html
    assert escape(hidden_lead_card["headline"]) not in topics_html
    assert 'href="https://example.com/the-row"' not in topics_html
    assert index_html.index('class="edition-nav"') < index_html.index('class="edition-brief"')
    assert index_html.index('class="edition-brief"') < index_html.index('class="lead-story"')
    assert index_html.index('class="lead-story"') < index_html.index('class="briefing-topics"')
    assert index_html.index('class="briefing-topics"') < index_html.index('class="section-block"')


def test_render_row_one_site_omits_briefing_topics_without_explicit_refs(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].section_key = "celebrity_style"
    edition.stories[0].headline = "Person topic without explicit refs"
    edition.stories[0].source_name = "Celebrity Person Desk"
    edition.stories[0].source_url = "https://example.com/person-source"
    edition.stories[0].tags = ["person", "celebrity"]

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="briefing-topics"' not in index_html
    assert "Briefing Topics" not in index_html
    assert 'class="edition-brief"' in index_html
    assert 'href="#briefing-topics"' not in index_html


def test_render_row_one_site_includes_briefing_path_from_digest_blocks(tmp_path) -> None:
    edition = _edition()
    base_story = edition.stories[0]
    edition.stories = [
        base_story.model_copy(
            deep=True,
            update={
                "id": "read-first-1111111111",
                "section_key": "top_stories",
                "headline": "Read first story",
                "detail_path": "details/read-first-1111111111.html",
                "heat_delta": 0,
                "entity_refs": [],
                "product_refs": [],
                "designer_refs": [],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "brand-move-2222222222",
                "section_key": "brand_moves",
                "headline": "Brand move story",
                "detail_path": "details/brand-move-2222222222.html",
                "heat_delta": 4,
                "entity_refs": [],
                "product_refs": [],
                "designer_refs": [],
            },
        ),
    ]

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    path_match = re.search(
        r'<section id="briefing-path" class="briefing-path" aria-label="Briefing path">'
        r"(?P<path>.*?)</section>",
        index_html,
        re.S,
    )

    assert 'class="briefing-topics"' not in index_html
    assert path_match is not None
    path_html = path_match.group("path")
    assert "Briefing Path" in path_html
    assert "今日阅读路径" in path_html
    assert "Key Takeaways" in path_html
    assert "Signals To Watch" in path_html
    assert "Read First" not in path_html
    assert "Read first story" not in path_html
    assert "Brand move story" in path_html
    assert "The Row is today&#x27;s priority signal." in path_html
    assert 'href="details/brand-move-2222222222.html"' in path_html
    assert 'href="https://example.com/the-row"' not in path_html
    assert "4 heat" in path_html
    assert "1 evidence link" in path_html
    assert index_html.index('class="edition-brief"') < index_html.index('class="lead-story"')
    assert index_html.index('class="briefing-path"') < index_html.index('class="section-block"')


def test_render_row_one_site_sanitizes_briefing_topic_and_path_hrefs() -> None:
    app_payload = {
        "daily_digest": {
            "briefing_topics": [
                {
                    "id": "unsafe-topic",
                    "topic_type": "brand",
                    "title": {"en": "Unsafe Topic", "zh": "不安全主题"},
                    "label": {"en": "Brand", "zh": "品牌"},
                    "story_count": 1,
                    "evidence_count": 1,
                    "positive_heat_delta_sum": 2,
                    "cards": [
                        {
                            "id": "unsafe-topic-card",
                            "detail_href": "javascript:alert(1)",
                            "headline": "Unsafe topic headline",
                            "editorial_takeaway": "Unsafe topic takeaway",
                        }
                    ],
                }
            ],
            "blocks": [
                {
                    "key": "signals_to_watch",
                    "title": {"en": "Signals To Watch", "zh": "观察信号"},
                    "dek": {"en": "Unsafe path block.", "zh": "不安全路径。"},
                    "cards": [
                        {
                            "id": "unsafe-path-card",
                            "detail_href": "javascript:alert(2)",
                            "headline": "Unsafe path headline",
                            "editorial_takeaway": "Unsafe path takeaway",
                            "source_name": "ROW ONE",
                            "published_date": "2026-07-02",
                            "evidence_count": 1,
                            "heat_delta": 2,
                        }
                    ],
                }
            ],
        }
    }

    index_html = render_index_html(_edition(), app_payload=app_payload)

    assert "Unsafe topic headline" in index_html
    assert "Unsafe path headline" in index_html
    assert "javascript:alert" not in index_html
    assert 'class="briefing-topic-card briefing-topic-card--brand" href="#main-content"' in (
        index_html
    )
    assert 'class="briefing-path-card" href="#main-content"' in index_html


def test_render_row_one_site_omits_briefing_path_when_digest_blocks_are_empty(tmp_path) -> None:
    edition = _edition()
    edition.stories = []

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="briefing-path"' not in index_html
    assert "Briefing Path" not in index_html
    assert 'class="edition-brief"' in index_html
    assert 'href="#briefing-path"' not in index_html


def test_render_row_one_site_includes_edition_brief_overview(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    brief_match = re.search(
        r'<section class="edition-brief" aria-label="Edition brief">(?P<brief>.*?)</section>',
        index_html,
        re.S,
    )

    assert brief_match is not None
    brief_html = brief_match.group("brief")
    assert "Edition Brief" in brief_html
    assert "今日总览" in brief_html
    assert "Stories" in brief_html
    assert "Active Sections" in brief_html
    assert "Topics" in brief_html
    assert "Evidence Links" in brief_html
    assert "Read first: The Row" in brief_html
    assert 'href="details/the-row-signal-1234567890.html"' in brief_html
    assert 'href="#briefing-path"' not in brief_html
    assert index_html.index('class="edition-nav"') < index_html.index('class="edition-brief"')
    assert index_html.index('class="edition-brief"') < index_html.index('class="lead-story"')


def test_render_row_one_site_displays_edition_brief_topic_mix_and_heat_watch(tmp_path) -> None:
    edition = _edition()
    base_story = edition.stories[0]
    edition.stories = [
        base_story.model_copy(
            deep=True,
            update={
                "heat_delta": 7,
                "entity_refs": [
                    RowOneReference(name="The Row", type="brand", label="brand"),
                    RowOneReference(name="Zendaya", type="celebrity", label="person"),
                ],
                "product_refs": [RowOneReference(name="Margaux", type="bag", label="bag")],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "designer-signal-2222222222",
                "section_key": "brand_moves",
                "headline": "Designer signal",
                "detail_path": "details/designer-signal-2222222222.html",
                "heat_delta": 3,
                "entity_refs": [
                    RowOneReference(
                        name="Mary-Kate Olsen",
                        type="designer",
                        label="designer",
                    )
                ],
            },
        ),
    ]

    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert "Topic mix: 1 brand, 1 product, 1 designer, 1 person" in index_html
    assert "主题结构：品牌 1、单品 1、设计师 1、人物 1" in index_html
    assert "Heat watch: 2 positive heat signals, highest +7" in index_html
    assert "升温观察：2 条正向热度信号，最高 +7" in index_html


def _editorial_brief_section_html(index_html: str) -> str:
    marker = '<section class="editorial-brief"'
    section_start = index_html.index(marker)
    next_section = re.search(
        r"\n<section class=",
        index_html[section_start + len(marker) :],
    )
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]


def test_render_row_one_site_includes_editorial_brief_from_local_articles(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="brand")]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert '<span data-lang="en">Editorial Brief</span>' in section_html
    assert '<span data-lang="zh">编辑正文</span>' in section_html
    assert "What changed today" in section_html
    assert "今日变化" in section_html
    assert "Why it matters" in section_html
    assert "为什么重要" in section_html
    assert "What to read locally" in section_html
    assert "本地阅读路径" in section_html
    assert "The Row is today&#x27;s priority signal." in section_html
    assert "The saved article frames a new signal." in section_html
    assert "Vogue Business" in section_html
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert index_html.index('class="saved-article-content-organization"') < section_start
    assert section_start < index_html.index('class="lead-story"')


def test_render_index_html_omits_editorial_brief_without_usable_content() -> None:
    index_html = render_index_html(_edition(), editorial_brief=None)

    assert 'class="editorial-brief"' not in index_html
    assert "Editorial Brief" not in index_html
    assert "编辑正文" not in index_html


def test_render_index_html_escapes_editorial_brief_and_filters_links() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Unsafe <b>", zh="危险 <b>"),
                    body=LocalizedText(en="Body <script>", zh="正文 <script>"),
                    href="javascript:alert(1)",
                    meta=LocalizedText(en="Meta <i>", zh="元信息 <i>"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="External", zh="外链"),
                    body=LocalizedText(en="External body.", zh="外链正文。"),
                    href="https://evil.example/story",
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Safe detail", zh="安全详情"),
                    body=LocalizedText(en="Detail body.", zh="详情正文。"),
                    href="details/the-row-signal-1234567890.html",
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Unsafe &lt;b&gt;" in section_html
    assert "Body &lt;script&gt;" in section_html
    assert "Meta &lt;i&gt;" in section_html
    assert "<script>" not in section_html
    assert "<b>" not in section_html
    assert "javascript:alert" not in section_html
    assert "https://evil.example" not in section_html
    assert 'href="details/the-row-signal-1234567890.html"' in section_html


def test_render_row_one_site_editorial_brief_falls_back_to_story_text(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="brand")]

    render_row_one_site(edition, tmp_path, local_articles_by_story_id={})

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="editorial-brief"' in index_html
    assert "The Row is today&#x27;s priority signal." in index_html
    assert "This signal belongs in Top Stories." in index_html


def test_render_row_one_site_includes_editorial_brief_source_trail(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()
    assert local_article.source_name == "Vogue Business"
    assert local_article.title == "Signal source article"
    assert local_article.paragraphs
    assert any(paragraph.strip() for paragraph in local_article.paragraphs)

    brief_section = next(
        section for section in local_article.brief_sections if section.key == "what_happened"
    )
    assert brief_section.title.en == "What Happened"
    assert brief_section.title.zh == "发生了什么"

    content_section = next(
        section for section in local_article.content_sections if section.key == "entities"
    )
    assert content_section.title.en == "People & Brands"
    assert content_section.title.zh == "品牌与人物"

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)

    assert 'class="editorial-brief-trail"' in section_html
    assert "Vogue Business" in section_html
    assert "Signal source article" in section_html
    assert "What Happened" in section_html
    assert "发生了什么" in section_html
    assert "People &amp; Brands" in section_html
    assert "品牌与人物" in section_html
    assert 'class="editorial-brief-meta"' in section_html
    assert section_html.count("Vogue Business") == 2
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert re.search(
        r'href="details/the-row-signal-1234567890.html#local-article-content-section-[1-9][0-9]*"',
        section_html,
    )
    assert '<a class="editorial-brief-card"' not in section_html
    assert '<article class="editorial-brief-card">' in section_html


def test_render_row_one_site_editorial_brief_content_section_trail_resolves_to_detail_anchor(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = _editorial_brief_section_html(index_html)
    match = re.search(
        r'href="details/the-row-signal-1234567890.html#(?P<fragment>local-article-content-section-[1-9][0-9]*)"',
        section_html,
    )

    assert match is not None
    assert f'id="{match.group("fragment")}"' in detail_html


def test_render_row_one_site_omits_editorial_brief_source_trail_without_local_article(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path, local_articles_by_story_id={})

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)

    assert 'class="editorial-brief-trail"' not in section_html
    assert "Editorial Brief" in section_html
    assert "What changed today" in section_html


def test_render_index_html_filters_editorial_brief_source_trail_links() -> None:
    from fashion_radar.row_one.detail_routes import (
        validated_row_one_detail_relative_path,
    )
    from fashion_radar.row_one.templates import (
        _EditorialBriefTrailItem,
        _safe_editorial_brief_href,
    )

    for unsafe_path in (
        "../secrets.html",
        "details/../admin.html",
        "details/%2e%2e/admin.html",
        "details/%2E%2E/admin.html",
        "details/%252e%252e/admin.html",
        "details/%2e%2e-1234567890.html",
    ):
        assert validated_row_one_detail_relative_path(unsafe_path) is None

    for unsafe_href in (
        None,
        "",
        "   ",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "http://evil.example/story",
        "https://evil.example/story",
        "//evil.example/story",
        "../secrets.html",
        "details/../admin.html",
        "details/%2e%2e/admin.html",
        "details/%2E%2E/admin.html",
        "details/%252e%252e/admin.html",
        "details/the-row-signal-1234567890.html#local-article-paragraph-0",
        "details/the-row-signal-1234567890.html#local-article-paragraph--1",
        "details/the-row-signal-1234567890.html#local-article-paragraph-",
        "details/the-row-signal-1234567890.html#local-article-paragraph-abc",
        "details/the-row-signal-1234567890.html#local-article-paragraph-1;drop",
        "details/the-row-signal-1234567890.html#local-article-content-section-0",
        "details/the-row-signal-1234567890.html#local-article-content-section--1",
        "details/the-row-signal-1234567890.html#local-article-content-section-",
        "details/the-row-signal-1234567890.html#local-article-content-section-abc",
        "details/the-row-signal-1234567890.html#local-article-content-section-1;drop",
    ):
        assert _safe_editorial_brief_href(unsafe_href) is None

    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Trail Safety", zh="线索安全"),
                    body=LocalizedText(en="Trail body.", zh="线索正文。"),
                    trail=(
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Safe paragraph", zh="安全段落"),
                            href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Safe section", zh="安全栏目"),
                            href="details/the-row-signal-1234567890.html#local-article-content-section-1",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="External <b>", zh="外链 <b>"),
                            href="https://evil.example/story",
                        ),
                    ),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Unsafe Schemes", zh="不安全地址"),
                    body=LocalizedText(en="Unsafe scheme body.", zh="不安全地址正文。"),
                    trail=(
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="JavaScript URI", zh="脚本地址"),
                            href="javascript:alert(1)",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Data URI", zh="数据地址"),
                            href="data:text/html,<script>alert(1)</script>",
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Protocol Relative", zh="协议相对"),
                            href="//evil.example/story",
                        ),
                    ),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Bad Fragment", zh="错误片段"),
                    body=LocalizedText(en="Bad fragment body.", zh="错误片段正文。"),
                    trail=(
                        _EditorialBriefTrailItem(
                            label=LocalizedText(
                                en='<script>alert(1)</script> " onmouseover="evil',
                                zh="<script>警告</script>",
                            ),
                            href=None,
                        ),
                        _EditorialBriefTrailItem(
                            label=LocalizedText(en="Bad section", zh="错误栏目"),
                            href="details/the-row-signal-1234567890.html#local-article-content-section-0",
                        ),
                    ),
                ),
            )
        ),
    )

    section_html = _editorial_brief_section_html(index_html)

    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert "External &lt;b&gt;" in section_html
    assert "JavaScript URI" in section_html
    assert "Data URI" in section_html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in section_html
    assert "&quot; onmouseover=&quot;evil" in section_html
    assert "Protocol Relative" in section_html
    assert "Bad section" in section_html
    assert '<span class="editorial-brief-trail-item">' in section_html
    assert "javascript:alert" not in section_html
    assert "data:text/html" not in section_html
    assert "https://evil.example" not in section_html
    assert "//evil.example" not in section_html
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-content-section-0"'
        not in section_html
    )
    assert "<b>" not in section_html
    assert "<script>" not in section_html


def test_render_index_html_caps_and_dedupes_editorial_brief_source_trail() -> None:
    from fashion_radar.row_one.templates import (
        EDITORIAL_BRIEF_MAX_TRAIL_ITEMS,
        _EditorialBriefTrailItem,
    )

    trail_items = (
        _EditorialBriefTrailItem(
            label=LocalizedText(en="One", zh="一"),
            href="details/the-row-signal-1234567890.html",
        ),
        _EditorialBriefTrailItem(
            label=LocalizedText(en="One", zh="一"),
            href="details/the-row-signal-1234567890.html",
        ),
        _EditorialBriefTrailItem(label=LocalizedText(en="Two", zh="二")),
        _EditorialBriefTrailItem(label=LocalizedText(en="Three", zh="三")),
        _EditorialBriefTrailItem(label=LocalizedText(en="Four", zh="四")),
    )
    assert len(trail_items) > EDITORIAL_BRIEF_MAX_TRAIL_ITEMS

    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Trail Cap", zh="线索上限"),
                    body=LocalizedText(en="Trail body.", zh="线索正文。"),
                    trail=trail_items,
                ),
            )
        ),
    )

    section_html = _editorial_brief_section_html(index_html)

    assert section_html.count("editorial-brief-trail-item") == (EDITORIAL_BRIEF_MAX_TRAIL_ITEMS)
    assert section_html.count(">One<") == 1
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    assert ">Two<" in section_html
    assert ">Three<" in section_html
    assert ">Four<" not in section_html
    assert section_html.index(">One<") < section_html.index(">Two<") < section_html.index(">Three<")


def test_render_row_one_site_editorial_brief_source_trail_uses_saved_paragraph_without_watch_next(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    base_article = _signal_briefing_local_article()
    local_article = base_article.model_copy(
        update={
            "brief_sections": [
                section for section in base_article.brief_sections if section.key != "watch_next"
            ]
        }
    )
    assert all(section.key != "watch_next" for section in local_article.brief_sections)
    assert local_article.paragraphs

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)
    title_start = section_html.index("What to read locally")
    card_start = section_html.rfind('<article class="editorial-brief-card">', 0, title_start)
    assert card_start != -1
    card_end = section_html.index("</article>", title_start) + len("</article>")
    card_html = section_html[card_start:card_end]

    assert 'class="editorial-brief-trail"' in card_html
    assert "Saved paragraph 1" in card_html
    assert "保存段落 1" in card_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in card_html


def test_render_row_one_site_editorial_brief_source_trail_omits_saved_paragraph_without_text(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]
    base_article = _signal_briefing_local_article()
    local_article = base_article.model_copy(
        update={
            "paragraphs": [],
            "paragraphs_zh": [],
            "brief_sections": [
                section for section in base_article.brief_sections if section.key != "watch_next"
            ],
        }
    )
    assert all(section.key != "watch_next" for section in local_article.brief_sections)
    assert not local_article.paragraphs

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _editorial_brief_section_html(index_html)
    title_start = section_html.index("What to read locally")
    card_start = section_html.rfind('<article class="editorial-brief-card">', 0, title_start)
    assert card_start != -1
    card_end = section_html.index("</article>", title_start) + len("</article>")
    card_html = section_html[card_start:card_end]

    assert "Saved paragraph 1" not in card_html
    assert "保存段落 1" not in card_html
    assert "#local-article-paragraph-1" not in card_html


def test_render_index_html_accepts_editorial_brief_content_section_href() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Content Section", zh="内容段落"),
                    body=LocalizedText(en="Content section body.", zh="内容段落正文。"),
                    href="details/the-row-signal-1234567890.html#local-article-content-section-1",
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert (
        'href="details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )


def test_render_index_html_accepts_editorial_brief_paragraph_href() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Paragraph", zh="段落"),
                    body=LocalizedText(en="Paragraph body.", zh="段落正文。"),
                    href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html


def test_render_index_html_rejects_editorial_brief_unknown_fragment_href() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Unknown", zh="未知"),
                    body=LocalizedText(en="Unknown body.", zh="未知正文。"),
                    href="details/the-row-signal-1234567890.html#summary",
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert 'href="details/the-row-signal-1234567890.html#summary"' not in section_html
    assert '<article class="editorial-brief-card">' in section_html


def test_render_index_html_caps_editorial_brief_to_three_items() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="One", zh="一"),
                    body=LocalizedText(en="First body.", zh="第一条。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Two", zh="二"),
                    body=LocalizedText(en="Second body.", zh="第二条。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Three", zh="三"),
                    body=LocalizedText(en="Third body.", zh="第三条。"),
                ),
                _EditorialBriefItem(
                    title=LocalizedText(en="Four", zh="四"),
                    body=LocalizedText(en="Fourth body.", zh="第四条。"),
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "First body." in section_html
    assert "Second body." in section_html
    assert "Third body." in section_html
    assert "Fourth body." not in section_html


def test_render_index_html_caps_editorial_brief_body_length() -> None:
    long_body = "Long body " * 40
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="Long", zh="长正文"),
                    body=LocalizedText(en=long_body, zh=long_body),
                ),
            )
        ),
    )

    section_start = index_html.index('class="editorial-brief"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]
    body_match = re.search(
        r'<span data-lang="en">(?P<body>Long body.*?)</span>',
        section_html,
        re.S,
    )

    assert body_match is not None
    assert long_body not in section_html
    assert "Long body Long body" in section_html
    assert body_match.group("body").endswith("…")
    assert len(body_match.group("body")) <= EDITORIAL_BRIEF_BODY_EXCERPT_CHARS + 1


def test_editorial_brief_payload_deduplicates_bodies() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "brief_sections": [
                RowOneLocalArticleBriefSection(
                    key="what_happened",
                    title=LocalizedText(en="What Happened", zh="发生了什么"),
                    body=story.editorial_takeaway,
                ),
                RowOneLocalArticleBriefSection(
                    key="why_it_matters",
                    title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                    body=story.why_it_matters,
                ),
                RowOneLocalArticleBriefSection(
                    key="watch_next",
                    title=LocalizedText(en="Watch Next", zh="接下来观察"),
                    body=story.why_it_matters,
                ),
            ],
        },
    )

    payload = _editorial_brief_payload(edition, {story.id: local_article})

    assert payload is not None
    assert [item.title.en for item in payload.items] == [
        "What changed today",
        "Why it matters",
    ]
    assert [item.body.en for item in payload.items] == [
        "The Row is today's priority signal.",
        "This signal belongs in Top Stories.",
    ]


def test_editorial_brief_item_dedupe_preserves_trail() -> None:
    from fashion_radar.row_one.render import _deduped_editorial_brief_items
    from fashion_radar.row_one.templates import _EditorialBriefTrailItem

    trail = (
        _EditorialBriefTrailItem(
            label=LocalizedText(en="Saved paragraph 1", zh="保存段落 1"),
            href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
    )

    deduped = _deduped_editorial_brief_items(
        (
            _EditorialBriefItem(
                title=LocalizedText(en="Title", zh="标题"),
                body=LocalizedText(en="Same body.", zh="相同正文。"),
                trail=trail,
            ),
            _EditorialBriefItem(
                title=LocalizedText(en="Duplicate", zh="重复"),
                body=LocalizedText(en="Same body.", zh="相同正文。"),
            ),
        )
    )

    assert len(deduped) == 1
    assert deduped[0].trail == trail


def test_render_index_html_omits_editorial_brief_with_empty_items() -> None:
    index_html = render_index_html(
        _edition(),
        editorial_brief=_EditorialBrief(
            items=(
                _EditorialBriefItem(
                    title=LocalizedText(en="   ", zh=" "),
                    body=LocalizedText(en="   ", zh=" "),
                ),
            )
        ),
    )

    assert 'class="editorial-brief"' not in index_html


def test_render_row_one_site_includes_daily_edit_section(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].entity_refs = [
        RowOneReference(name="The Row", type="brand", label="rising"),
    ]

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert '<span data-lang="en">Daily Edit</span>' in section_html
    assert '<span data-lang="zh">今日编辑简报</span>' in section_html
    assert '<span data-lang="en">What To Know</span>' in section_html
    assert '<span data-lang="zh">今日重点</span>' in section_html
    assert '<span data-lang="en">Signals To Watch</span>' in section_html
    assert '<span data-lang="zh">值得关注</span>' in section_html
    assert '<span data-lang="en">Read Next</span>' in section_html
    assert '<span data-lang="zh">阅读路径</span>' in section_html
    assert '<span data-lang="en">Evidence Note</span>' in section_html
    assert '<span data-lang="zh">线索边界</span>' in section_html
    assert "The Row" in section_html
    assert "evidence" in section_html
    assert "review the underlying stories before acting" in section_html
    assert 'href="details/the-row-signal-1234567890.html"' in section_html
    assert index_html.index('class="edition-brief"') < section_start
    assert index_html.index('class="signal-synthesis"') < section_start
    assert section_start < index_html.index('class="lead-story"')


def test_render_row_one_site_places_daily_edit_before_daily_local_intelligence() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {
                "lead_story_headline": "The Row signal",
                "lead_story_href": "details/the-row-signal-1234567890.html",
                "summary_points": [
                    {"en": "Read the lead story first.", "zh": "先读主线故事。"},
                ],
                "metrics": [],
                "links": [],
            },
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "Signals dek", "zh": "信号说明"},
                "boundaries": {"en": "Existing evidence only.", "zh": "仅限现有证据。"},
                "groups": [
                    {
                        "label": {"en": "Brands", "zh": "品牌"},
                        "signals": [
                            {
                                "name": "The Row",
                                "summary": {"en": "Brand signal.", "zh": "品牌信号。"},
                                "lead_story_href": "details/the-row-signal-1234567890.html",
                                "story_count": 1,
                                "evidence_count": 1,
                                "label": "brand",
                            }
                        ],
                    }
                ],
            },
            "daily_digest": {"evidence_count": 1, "blocks": [], "briefing_topics": []},
        },
        local_article_intelligence=[
            RowOneDailyLocalIntelligenceSection(
                key="strongest_reads",
                title=LocalizedText(zh="优先阅读", en="Strongest Reads"),
                dek=LocalizedText(zh="本地正文。", en="Saved local text."),
                items=[
                    RowOneDailyLocalIntelligenceItem(
                        title=LocalizedText(zh="本地信号", en="Local Signal"),
                        body=LocalizedText(zh="正文。", en="Body."),
                    )
                ],
            )
        ],
    )

    assert index_html.index('class="signal-synthesis"') < index_html.index('class="daily-edit"')
    assert index_html.index('class="daily-edit"') < index_html.index(
        'class="daily-local-intelligence"'
    )


def test_render_index_html_includes_daily_local_key_signals_digest() -> None:
    digest = RowOneDailyLocalKeySignalsDigest(
        article_count=2,
        groups=(
            RowOneDailyLocalKeySignalsDigestGroup(
                key="why_it_matters",
                title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                total_count=2,
                entries=(
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Article <script>", zh="文章 <script>"),
                        body=LocalizedText(
                            en="Quiet <brand> demand is accelerating.",
                            zh="静奢 <brand> 需求加速。",
                        ),
                        href=(
                            "articles/the-row-signal-1234567890.html"
                            "#saved-article-key-signals-title"
                        ),
                        source_name="Vogue <Business>",
                        support_count=2,
                    ),
                ),
            ),
            RowOneDailyLocalKeySignalsDigestGroup(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                total_count=3,
                entries=(
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="The <Row>", zh="The <Row>"),
                        body=LocalizedText(en="Brand statement.", zh="品牌陈述。"),
                        href="articles/the-row-signal-1234567890.html#local-article-paragraph-1",
                        source_name="Vogue Business",
                        support_count=3,
                    ),
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Bad JS", zh="坏 JS"),
                        body=LocalizedText(en="Bad link.", zh="坏链接。"),
                        href="javascript:alert(1)",
                        source_name="Bad",
                    ),
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Bad traversal", zh="坏路径"),
                        body=LocalizedText(en="Bad link.", zh="坏链接。"),
                        href="../details/the-row-signal-1234567890.html#local-article-paragraph-1",
                        source_name="Bad",
                    ),
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Bad nested", zh="坏嵌套"),
                        body=LocalizedText(en="Bad link.", zh="坏链接。"),
                        href="articles/unsafe/story.html#local-article-paragraph-1",
                        source_name="Bad",
                    ),
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Bad fragment", zh="坏片段"),
                        body=LocalizedText(en="Bad link.", zh="坏链接。"),
                        href="articles/the-row-signal-1234567890.html#summary",
                        source_name="Bad",
                    ),
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Bad paragraph", zh="坏段落"),
                        body=LocalizedText(en="Bad link.", zh="坏链接。"),
                        href=("articles/the-row-signal-1234567890.html#local-article-paragraph-0"),
                        source_name="Bad",
                    ),
                ),
            ),
            RowOneDailyLocalKeySignalsDigestGroup(
                key="themes",
                title=LocalizedText(en="Themes", zh="主题"),
                total_count=1,
                entries=(
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Product Signals", zh="单品信号"),
                        body=None,
                        href=(
                            "articles/the-row-signal-1234567890.html"
                            "#local-article-content-section-1"
                        ),
                        source_name="Vogue Business",
                    ),
                ),
            ),
        ),
    )

    index_html = render_index_html(_edition(), daily_local_key_signals_digest=digest)
    section_html = _daily_local_key_signals_digest_section_html(index_html)
    omitted_html = render_index_html(_edition(), daily_local_key_signals_digest=None)

    assert 'class="daily-local-key-signals-digest"' in section_html
    assert "Daily Local Key Signals Digest" in section_html
    assert "每日本地关键信号摘要" in section_html
    assert "2 articles" in section_html
    assert "3 total signals" in section_html
    assert "2 supporting articles" in section_html
    assert "Product Signals" in section_html
    assert (
        'href="articles/the-row-signal-1234567890.html#saved-article-key-signals-title"'
        in section_html
    )
    assert 'href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"' in (
        section_html
    )
    assert (
        'href="articles/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert "Article &lt;script&gt;" in section_html
    assert "Quiet &lt;brand&gt; demand is accelerating." in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "The &lt;Row&gt;" in section_html
    assert "<script>" not in section_html
    assert "<brand>" not in section_html
    assert "<Business>" not in section_html
    assert "<Row>" not in section_html
    assert "javascript:alert" not in section_html
    assert "../details" not in section_html
    assert "articles/unsafe/story.html" not in section_html
    assert "#summary" not in section_html
    assert "#local-article-paragraph-0" not in section_html
    assert 'class="daily-local-key-signals-digest"' not in omitted_html
    assert "Daily Local Key Signals Digest" not in omitted_html


def test_render_index_html_includes_daily_local_signal_momentum() -> None:
    leaderboard = RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=3,
        item_count=3,
        buckets=(
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=LocalizedText(en="The Row <brand>", zh="The Row <品牌>"),
                        article_count=2,
                        source_count=1,
                        supports=(
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(
                                    en="The Row source <script>",
                                    zh="The Row 来源 <script>",
                                ),
                                source_name="Vogue <Business>",
                                href=(
                                    "details/the-row-signal-1234567890.html#local-article-digest"
                                ),
                                detail_path="details/the-row-signal-1234567890.html",
                            ),
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(
                                    en="Fallback detail source",
                                    zh="备用详情来源",
                                ),
                                source_name="WWD",
                                href=(
                                    "details/the-row-signal-fallback-1234567890.html"
                                    "#local-article-digest"
                                ),
                                detail_path="details/the-row-signal-fallback-1234567890.html",
                            ),
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Unsafe JS", zh="不安全 JS"),
                                source_name="Bad",
                                href="javascript:alert(1)",
                                detail_path="details/unsafe-js.html",
                            ),
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Unsafe traversal", zh="不安全穿越"),
                                source_name="Bad",
                                href=(
                                    "../details/the-row-signal-1234567890.html#local-article-digest"
                                ),
                                detail_path="details/unsafe-traversal.html",
                            ),
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Unsafe fragment", zh="不安全片段"),
                                source_name="Bad",
                                href="details/the-row-signal-1234567890.html#summary",
                                detail_path="details/unsafe-fragment.html",
                            ),
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Unsafe mapped secret", zh="不安全映射"),
                                source_name="Bad",
                                href="details/unsafe-map-secret.html#summary",
                                detail_path="details/unsafe-map-secret.html",
                            ),
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Unsafe mapped nested", zh="不安全嵌套"),
                                source_name="Bad",
                                href="details/unsafe-map-nested.html#summary",
                                detail_path="details/unsafe-map-nested.html",
                            ),
                        ),
                    ),
                ),
            ),
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="products",
                title=LocalizedText(en="Products", zh="产品"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=LocalizedText(en="Margaux bag", zh="Margaux 手袋"),
                        article_count=1,
                        source_count=1,
                        supports=(
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Product article", zh="产品文章"),
                                source_name="Vogue Business",
                                href=(
                                    "details/the-row-signal-1234567890.html#local-article-digest"
                                ),
                                detail_path="details/the-row-signal-1234567890.html",
                            ),
                        ),
                    ),
                ),
            ),
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="themes",
                title=LocalizedText(en="Themes", zh="主题"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=LocalizedText(en="Quiet luxury", zh="静奢"),
                        article_count=1,
                        source_count=1,
                        supports=(
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="Theme article", zh="主题文章"),
                                source_name="Vogue Business",
                                href=(
                                    "details/the-row-signal-1234567890.html#local-article-digest"
                                ),
                                detail_path="details/the-row-signal-1234567890.html",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    index_html = render_index_html(
        _edition(),
        daily_local_signal_momentum=leaderboard,
        daily_local_signal_momentum_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
            "details/unsafe-map-secret.html": "../secret.html",
            "details/unsafe-map-nested.html": "unsafe/story.html",
        },
    )
    section_html = _daily_local_signal_momentum_section_html(index_html)
    omitted_html = render_index_html(_edition(), daily_local_signal_momentum=None)

    assert 'class="daily-local-signal-momentum"' in section_html
    assert "Daily Local Signal Momentum" in section_html
    assert "每日本地信号动量" in section_html
    assert "Brands" in section_html
    assert "Products" in section_html
    assert "Themes" in section_html
    assert "The Row &lt;brand&gt;" in section_html
    assert "The Row &lt;品牌&gt;" in section_html
    assert "2 articles" in section_html
    assert "1 source" in section_html
    assert "Margaux bag" in section_html
    assert "Quiet luxury" in section_html
    assert "The Row source &lt;script&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert (
        'href="details/the-row-signal-fallback-1234567890.html#local-article-digest"'
        in section_html
    )
    assert "<script>" not in section_html
    assert "<brand>" not in section_html
    assert "<品牌>" not in section_html
    assert "<Business>" not in section_html
    assert "javascript:alert" not in section_html
    assert "../details" not in section_html
    assert "../secret.html" not in section_html
    assert "unsafe/story.html" not in section_html
    assert "#summary" not in section_html
    assert "Unsafe JS" not in section_html
    assert "Unsafe traversal" not in section_html
    assert "Unsafe fragment" not in section_html
    assert "Unsafe mapped secret" not in section_html
    assert "Unsafe mapped nested" not in section_html
    assert 'class="daily-local-signal-momentum"' not in omitted_html
    assert "Daily Local Signal Momentum" not in omitted_html


def test_render_index_html_includes_daily_local_heat_signals() -> None:
    local_articles_by_story_id = {
        "the-row-signal-1234567890": _signal_briefing_local_article(),
        "margaux-topic-2222222222": _signal_briefing_local_article().model_copy(
            update={"story_id": "margaux-topic-2222222222", "title": "Margaux bag source"}
        ),
        "designer-topic-3333333333": _signal_briefing_local_article().model_copy(
            update={"story_id": "designer-topic-3333333333", "title": "Designer source"}
        ),
        "zero-heat-topic-4444444444": _signal_briefing_local_article().model_copy(
            update={"story_id": "zero-heat-topic-4444444444", "title": "Zero heat source"}
        ),
        "empty-local-topic-5555555555": _signal_briefing_local_article().model_copy(
            update={
                "story_id": "empty-local-topic-5555555555",
                "title": "Empty local source",
                "paragraphs": [],
            }
        ),
        "unsafe/topic-6666666666": _signal_briefing_local_article().model_copy(
            update={"story_id": "unsafe/topic-6666666666", "title": "Unsafe local source"}
        ),
        "bool-heat-topic-8888888888": _signal_briefing_local_article().model_copy(
            update={"story_id": "bool-heat-topic-8888888888", "title": "Bool heat source"}
        ),
        "string-heat-topic-9999999999": _signal_briefing_local_article().model_copy(
            update={"story_id": "string-heat-topic-9999999999", "title": "String heat source"}
        ),
        "float-heat-topic-1212121212": _signal_briefing_local_article().model_copy(
            update={"story_id": "float-heat-topic-1212121212", "title": "Float heat source"}
        ),
        "none-heat-topic-1313131313": _signal_briefing_local_article().model_copy(
            update={"story_id": "none-heat-topic-1313131313", "title": "None heat source"}
        ),
    }
    article_hrefs_by_story_id = {
        "the-row-signal-1234567890": "the-row-signal-1234567890.html",
        "margaux-topic-2222222222": "margaux-topic-2222222222.html",
        "designer-topic-3333333333": "designer-topic-3333333333.html",
        "zero-heat-topic-4444444444": "zero-heat-topic-4444444444.html",
        "empty-local-topic-5555555555": "empty-local-topic-5555555555.html",
        "unsafe/topic-6666666666": "unsafe-topic-6666666666.html",
        "nested-mapped-topic-7777777777": "nested/story.html",
        "bool-heat-topic-8888888888": "bool-heat-topic-8888888888.html",
        "string-heat-topic-9999999999": "string-heat-topic-9999999999.html",
        "float-heat-topic-1212121212": "float-heat-topic-1212121212.html",
        "none-heat-topic-1313131313": "none-heat-topic-1313131313.html",
    }

    index_html = render_index_html(
        _edition(),
        app_payload={
            "daily_digest": {
                "briefing_topics": [
                    {
                        "topic_type": "brand",
                        "title": {"en": "The Row <script>", "zh": "The Row <脚本>"},
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 4,
                        "evidence_count": 6,
                        "positive_heat_delta_sum": 5,
                        "max_heat_delta": 3,
                        "story_ids": [
                            "the-row-signal-1234567890",
                            "missing-local-topic-9999999999",
                            "unsafe/topic-6666666666",
                            "nested-mapped-topic-7777777777",
                        ],
                        "cards": [
                            {
                                "id": "the-row-signal-1234567890",
                                "headline": {
                                    "en": "The Row source <script>",
                                    "zh": "The Row 来源 <script>",
                                },
                                "source_name": "Vogue <Business>",
                            },
                            {
                                "id": "missing-local-topic-9999999999",
                                "headline": {"en": "Missing local", "zh": "缺少本地正文"},
                                "source_name": "Bad",
                            },
                            {
                                "id": "unsafe/topic-6666666666",
                                "headline": {"en": "Unsafe story", "zh": "不安全故事"},
                                "source_name": "Bad",
                            },
                            {
                                "id": "nested-mapped-topic-7777777777",
                                "headline": {"en": "Nested mapped", "zh": "嵌套映射"},
                                "source_name": "Bad",
                            },
                        ],
                        "source_refs": [
                            {"name": "The Row", "type": "brand", "label": "rising"},
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "Margaux bag", "zh": "Margaux 手袋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 2,
                        "positive_heat_delta_sum": 8,
                        "max_heat_delta": 8,
                        "story_ids": ["margaux-topic-2222222222"],
                        "cards": [
                            {
                                "id": "margaux-topic-2222222222",
                                "headline": {"en": "Margaux story", "zh": "Margaux 故事"},
                                "source_name": "Vogue Business",
                            }
                        ],
                        "source_refs": [
                            {"name": "Margaux bag", "type": "bag", "label": "It bag"},
                        ],
                    },
                    {
                        "topic_type": "designer",
                        "title": {"en": "Mary-Kate Olsen", "zh": "Mary-Kate Olsen"},
                        "label": {"en": "Designer", "zh": "设计师"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 9,
                        "max_heat_delta": 9,
                        "story_ids": ["designer-topic-3333333333"],
                        "cards": [
                            {
                                "id": "designer-topic-3333333333",
                                "headline": {"en": "Designer story", "zh": "设计师故事"},
                                "source_name": "WWD",
                            }
                        ],
                        "source_refs": [
                            {
                                "name": "Mary-Kate Olsen",
                                "type": "designer",
                                "label": "designer",
                            },
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "Zero Heat Shoe", "zh": "零热度鞋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 0,
                        "max_heat_delta": 0,
                        "story_ids": ["zero-heat-topic-4444444444"],
                        "cards": [
                            {
                                "id": "zero-heat-topic-4444444444",
                                "headline": {"en": "Zero heat", "zh": "零热度"},
                                "source_name": "Bad",
                            }
                        ],
                        "source_refs": [
                            {"name": "Zero Heat Shoe", "type": "shoe", "label": "shoe"},
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "Empty Local Sneaker", "zh": "空正文运动鞋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 7,
                        "max_heat_delta": 7,
                        "story_ids": ["empty-local-topic-5555555555"],
                        "cards": [
                            {
                                "id": "empty-local-topic-5555555555",
                                "headline": {"en": "Empty local", "zh": "空正文"},
                                "source_name": "Bad",
                            }
                        ],
                        "source_refs": [
                            {
                                "name": "Empty Local Sneaker",
                                "type": "sneaker",
                                "label": "sneaker",
                            },
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "Bool Heat Platform", "zh": "布尔热度厚底鞋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": True,
                        "max_heat_delta": 0,
                        "story_ids": ["bool-heat-topic-8888888888"],
                        "cards": [
                            {
                                "id": "bool-heat-topic-8888888888",
                                "headline": {"en": "Bool heat", "zh": "布尔热度"},
                                "source_name": "Bad",
                            }
                        ],
                        "source_refs": [
                            {"name": "Bool Heat Platform", "type": "platform", "label": "platform"},
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "String Heat Shoe", "zh": "字符串热度鞋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": "5",
                        "max_heat_delta": 0,
                        "story_ids": ["string-heat-topic-9999999999"],
                        "cards": [
                            {
                                "id": "string-heat-topic-9999999999",
                                "headline": {"en": "String heat", "zh": "字符串热度"},
                                "source_name": "Bad",
                            }
                        ],
                        "source_refs": [
                            {"name": "String Heat Shoe", "type": "shoe", "label": "shoe"},
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "Float Heat Shoe", "zh": "浮点热度鞋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 5.0,
                        "max_heat_delta": 0,
                        "story_ids": ["float-heat-topic-1212121212"],
                        "cards": [
                            {
                                "id": "float-heat-topic-1212121212",
                                "headline": {"en": "Float heat", "zh": "浮点热度"},
                                "source_name": "Bad",
                            }
                        ],
                        "source_refs": [
                            {"name": "Float Heat Shoe", "type": "shoe", "label": "shoe"},
                        ],
                    },
                    {
                        "topic_type": "product",
                        "title": {"en": "None Heat Shoe", "zh": "空热度鞋"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": None,
                        "max_heat_delta": 0,
                        "story_ids": ["none-heat-topic-1313131313"],
                        "cards": [
                            {
                                "id": "none-heat-topic-1313131313",
                                "headline": {"en": "None heat", "zh": "空热度"},
                                "source_name": "Bad",
                            }
                        ],
                        "source_refs": [
                            {"name": "None Heat Shoe", "type": "shoe", "label": "shoe"},
                        ],
                    },
                ]
            }
        },
        local_articles_by_story_id=local_articles_by_story_id,
        daily_local_heat_signals_article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    section_html = _daily_local_heat_signals_section_html(index_html)
    omitted_html = render_index_html(
        _edition(),
        app_payload={"daily_digest": {"briefing_topics": []}},
        local_articles_by_story_id=local_articles_by_story_id,
        daily_local_heat_signals_article_hrefs_by_story_id=article_hrefs_by_story_id,
    )

    assert 'class="daily-local-heat-signals"' in section_html
    assert "Daily Local Heat Signals" in section_html
    assert "每日本地热度信号" in section_html
    assert "2 heated topics" in section_html
    assert "2 local articles" in section_html
    assert "Brand" in section_html
    assert "Product" in section_html
    assert "Bag" in section_html
    assert "The Row &lt;script&gt;" in section_html
    assert "The Row &lt;脚本&gt;" in section_html
    assert "The Row source &lt;script&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "Margaux bag" in section_html
    assert 'href="articles/the-row-signal-1234567890.html#local-article-digest"' in (section_html)
    assert 'href="articles/margaux-topic-2222222222.html#local-article-digest"' in section_html
    assert section_html.index("Margaux bag") < section_html.index("The Row &lt;script&gt;")
    assert "<script>" not in section_html
    assert "<Business>" not in section_html
    assert "Mary-Kate Olsen" not in section_html
    assert "Zero Heat Shoe" not in section_html
    assert "Empty Local Sneaker" not in section_html
    assert "Bool Heat Platform" not in section_html
    assert "String Heat Shoe" not in section_html
    assert "Float Heat Shoe" not in section_html
    assert "None Heat Shoe" not in section_html
    assert "Missing local" not in section_html
    assert "Unsafe story" not in section_html
    assert "Nested mapped" not in section_html
    assert "unsafe/topic" not in section_html
    assert "nested/story.html" not in section_html
    assert 'class="daily-local-heat-signals"' not in omitted_html
    assert "Daily Local Heat Signals" not in omitted_html


def test_render_index_html_avoids_substring_daily_local_heat_signal_subtype_badges() -> None:
    story_id = "platform-topic-1111111111"
    index_html = render_index_html(
        _edition(),
        app_payload={
            "daily_digest": {
                "briefing_topics": [
                    {
                        "topic_type": "product",
                        "title": {"en": "Platform Sole", "zh": "厚底鞋底"},
                        "label": {"en": "Product", "zh": "单品"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 5,
                        "max_heat_delta": 5,
                        "story_ids": [story_id],
                        "cards": [
                            {
                                "id": story_id,
                                "headline": {"en": "Platform story", "zh": "厚底故事"},
                                "source_name": "Vogue Business",
                            }
                        ],
                        "source_refs": [
                            {"name": "Platform Sole", "type": "platform", "label": "platform"},
                        ],
                    }
                ]
            }
        },
        local_articles_by_story_id={
            story_id: _signal_briefing_local_article().model_copy(
                update={"story_id": story_id, "title": "Platform source"}
            ),
        },
        daily_local_heat_signals_article_hrefs_by_story_id={story_id: f"{story_id}.html"},
    )
    section_html = _daily_local_heat_signals_section_html(index_html)

    assert "Platform Sole" in section_html
    assert ">Flat<" not in section_html
    assert ">Shoe<" not in section_html


def test_render_index_html_sorts_daily_local_heat_signals_by_total_local_article_count() -> None:
    story_ids = (
        "two-local-topic-1111111111",
        "two-local-topic-2222222222",
        "three-local-topic-3333333333",
        "three-local-topic-4444444444",
        "three-local-topic-5555555555",
    )
    local_articles_by_story_id = {
        story_id: _signal_briefing_local_article().model_copy(
            update={"story_id": story_id, "title": f"{story_id} source"}
        )
        for story_id in story_ids
    }
    article_hrefs_by_story_id = {story_id: f"{story_id}.html" for story_id in story_ids}

    index_html = render_index_html(
        _edition(),
        app_payload={
            "daily_digest": {
                "briefing_topics": [
                    {
                        "topic_type": "brand",
                        "title": {"en": "Two Local Evidence Heavy", "zh": "两篇高证据"},
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 2,
                        "evidence_count": 10,
                        "positive_heat_delta_sum": 5,
                        "max_heat_delta": 5,
                        "story_ids": [
                            "two-local-topic-1111111111",
                            "two-local-topic-2222222222",
                        ],
                        "cards": [
                            {
                                "id": "two-local-topic-1111111111",
                                "headline": {"en": "Two local one", "zh": "两篇之一"},
                                "source_name": "Vogue Business",
                            },
                            {
                                "id": "two-local-topic-2222222222",
                                "headline": {"en": "Two local two", "zh": "两篇之二"},
                                "source_name": "WWD",
                            },
                        ],
                        "source_refs": [
                            {"name": "Two Local Evidence Heavy", "type": "brand", "label": "brand"},
                        ],
                    },
                    {
                        "topic_type": "brand",
                        "title": {"en": "Three Local Evidence Light", "zh": "三篇低证据"},
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 3,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 5,
                        "max_heat_delta": 5,
                        "story_ids": [
                            "three-local-topic-3333333333",
                            "three-local-topic-4444444444",
                            "three-local-topic-5555555555",
                        ],
                        "cards": [
                            {
                                "id": "three-local-topic-3333333333",
                                "headline": {"en": "Three local one", "zh": "三篇之一"},
                                "source_name": "Vogue Business",
                            },
                            {
                                "id": "three-local-topic-4444444444",
                                "headline": {"en": "Three local two", "zh": "三篇之二"},
                                "source_name": "WWD",
                            },
                            {
                                "id": "three-local-topic-5555555555",
                                "headline": {"en": "Three local three", "zh": "三篇之三"},
                                "source_name": "Business of Fashion",
                            },
                        ],
                        "source_refs": [
                            {
                                "name": "Three Local Evidence Light",
                                "type": "brand",
                                "label": "brand",
                            },
                        ],
                    },
                ]
            }
        },
        local_articles_by_story_id=local_articles_by_story_id,
        daily_local_heat_signals_article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    section_html = _daily_local_heat_signals_section_html(index_html)

    assert section_html.index("Three Local Evidence Light") < section_html.index(
        "Two Local Evidence Heavy"
    )
    assert "Three local one" in section_html
    assert "Three local two" in section_html
    assert "Three local three" not in section_html


def test_render_index_html_rejects_mismatched_daily_local_heat_signal_article_href() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "daily_digest": {
                "briefing_topics": [
                    {
                        "topic_type": "brand",
                        "title": {"en": "The Row", "zh": "The Row"},
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 5,
                        "max_heat_delta": 5,
                        "story_ids": ["the-row-signal-1234567890"],
                        "cards": [
                            {
                                "id": "the-row-signal-1234567890",
                                "headline": {"en": "The Row source", "zh": "The Row 来源"},
                                "source_name": "Vogue Business",
                            }
                        ],
                        "source_refs": [
                            {"name": "The Row", "type": "brand", "label": "rising"},
                        ],
                    }
                ]
            }
        },
        local_articles_by_story_id={
            "the-row-signal-1234567890": _signal_briefing_local_article(),
        },
        daily_local_heat_signals_article_hrefs_by_story_id={
            "the-row-signal-1234567890": "other-story-1234567890.html",
        },
    )

    assert 'class="daily-local-heat-signals"' not in index_html
    assert "other-story-1234567890.html" not in index_html


def test_render_index_html_includes_daily_local_article_capsules() -> None:
    base_story = _edition().stories[0]
    stories = [
        base_story.model_copy(
            deep=True,
            update={
                "id": "article-capsule-1111111111",
                "headline": "The Row capsule <script>",
                "detail_path": "details/article-capsule-1111111111.html",
                "source_name": "Vogue <Business>",
                "why_it_matters": LocalizedText(
                    en="This explains the local article signal <b>.",
                    zh="这解释了本地正文信号 <b>。",
                ),
                "entity_refs": [RowOneReference(name="The Row", type="brand", label="brand")],
                "product_refs": [RowOneReference(name="Margaux bag", type="bag", label="product")],
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "capsule-second-2222222222",
                "headline": "Second capsule",
                "detail_path": "details/capsule-second-2222222222.html",
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "capsule-third-3333333333",
                "headline": "Third capsule",
                "detail_path": "details/capsule-third-3333333333.html",
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "capsule-fourth-4444444444",
                "headline": "Fourth capsule",
                "detail_path": "details/capsule-fourth-4444444444.html",
            },
        ),
        base_story.model_copy(
            deep=True,
            update={
                "id": "capsule-fifth-5555555555",
                "headline": "Fifth capsule",
                "detail_path": "details/capsule-fifth-5555555555.html",
            },
        ),
    ]
    article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "story_id": "article-capsule-1111111111",
            "title": "Capsule source <script>",
            "source_name": "Vogue <Business>",
            "body_source": "extracted",
            "paragraphs": [
                "Opening paragraph <b> frames The Row.",
                "Second paragraph mentions Margaux bag.",
                "Third paragraph shows the merchandising angle.",
                "Fourth paragraph should be capped out.",
            ],
            "paragraphs_zh": [
                "第一段 <b> 呈现 The Row。",
                "第二段提到 Margaux 手袋。",
                "第三段呈现商品角度。",
                "第四段不应显示。",
            ],
        },
    )
    local_articles_by_story_id = {
        article.story_id: article,
        **{
            story.id: _signal_briefing_local_article().model_copy(
                deep=True,
                update={
                    "story_id": story.id,
                    "title": f"{story.headline} local source",
                },
            )
            for story in stories[1:]
        },
    }
    edition = _edition_with_stories(*stories)

    html = render_index_html(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        daily_local_article_capsules_article_hrefs_by_story_id={
            story.id: f"{story.id}.html" for story in stories
        },
    )
    section_html = _daily_local_article_capsules_section_html(html)

    assert 'class="daily-local-article-capsules"' in section_html
    assert "Daily Local Article Capsules" in section_html
    assert "每日本地文章胶囊" in section_html
    assert section_html.index("The Row capsule") < section_html.index("Second capsule")
    assert section_html.index("Second capsule") < section_html.index("Third capsule")
    assert section_html.index("Third capsule") < section_html.index("Fourth capsule")
    assert "Fifth capsule" not in section_html
    assert "Capsule source &lt;script&gt;" in section_html
    assert "Vogue &lt;Business&gt;" in section_html
    assert "Extracted article text" in section_html
    assert "This explains the local article signal &lt;b&gt;." in section_html
    assert "这解释了本地正文信号 &lt;b&gt;。" in section_html
    assert "Opening paragraph &lt;b&gt; frames The Row." in section_html
    assert "Second paragraph mentions Margaux bag." in section_html
    assert "Third paragraph shows the merchandising angle." in section_html
    assert "Fourth paragraph should be capped out." not in section_html
    assert "The Row" in section_html
    assert "Margaux bag" in section_html
    assert 'href="articles/article-capsule-1111111111.html#local-article-digest"' in section_html
    assert (
        'href="articles/article-capsule-1111111111.html#local-article-paragraph-1"' in section_html
    )
    assert "<script>" not in section_html
    assert "<b>" not in section_html
    assert "<Business>" not in section_html


def test_render_index_html_filters_unsafe_daily_local_article_capsules() -> None:
    base_story = _edition().stories[0]
    safe_story = base_story.model_copy(
        deep=True,
        update={
            "id": "safe-capsule-1111111111",
            "headline": "Safe capsule",
            "detail_path": "details/safe-capsule-1111111111.html",
        },
    )
    unsafe_id_story = base_story.model_copy(
        deep=True,
        update={
            "id": "unsafe/capsule-2222222222",
            "headline": "Unsafe id capsule",
            "detail_path": "details/unsafe-capsule-2222222222.html",
        },
    )
    missing_article_story = base_story.model_copy(
        deep=True,
        update={
            "id": "missing-capsule-2222222222",
            "headline": "Missing article capsule",
            "detail_path": "details/missing-capsule-2222222222.html",
        },
    )
    empty_article_story = base_story.model_copy(
        deep=True,
        update={
            "id": "empty-capsule-2222222222",
            "headline": "Empty article capsule",
            "detail_path": "details/empty-capsule-2222222222.html",
        },
    )
    traversal_story = base_story.model_copy(
        deep=True,
        update={
            "id": "secret-capsule-3333333333",
            "headline": "Secret capsule",
            "detail_path": "details/secret-capsule-3333333333.html",
        },
    )
    mismatched_story = base_story.model_copy(
        deep=True,
        update={
            "id": "mismatch-capsule-3333333333",
            "headline": "Mismatched capsule",
            "detail_path": "details/mismatch-capsule-3333333333.html",
        },
    )
    local_articles_by_story_id = {
        story.id: _signal_briefing_local_article().model_copy(
            deep=True,
            update={"story_id": story.id, "title": f"{story.headline} article"},
        )
        for story in (safe_story, unsafe_id_story, traversal_story, mismatched_story)
    }
    local_articles_by_story_id[empty_article_story.id] = (
        _signal_briefing_local_article().model_copy(
            deep=True,
            update={
                "story_id": empty_article_story.id,
                "title": "Empty article capsule article",
                "paragraphs": [],
            },
        )
    )

    html = render_index_html(
        _edition_with_stories(
            safe_story,
            unsafe_id_story,
            missing_article_story,
            empty_article_story,
            traversal_story,
            mismatched_story,
        ),
        local_articles_by_story_id=local_articles_by_story_id,
        daily_local_article_capsules_article_hrefs_by_story_id={
            safe_story.id: "safe-capsule-1111111111.html",
            unsafe_id_story.id: "unsafe-capsule-2222222222.html",
            empty_article_story.id: "empty-capsule-2222222222.html",
            traversal_story.id: "../secret.html",
            mismatched_story.id: "other-capsule-3333333333.html",
        },
    )
    section_html = _daily_local_article_capsules_section_html(html)

    assert "Safe capsule" in section_html
    assert "Unsafe id capsule" not in section_html
    assert "Missing article capsule" not in section_html
    assert "Empty article capsule" not in section_html
    assert "Secret capsule" not in section_html
    assert "Mismatched capsule" not in section_html
    assert "../secret" not in section_html
    assert "other-capsule-3333333333.html" not in section_html


def test_render_index_html_daily_local_article_capsules_aligns_zh_paragraphs() -> None:
    story = _edition().stories[0]
    article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "story_id": story.id,
            "paragraphs": [
                "First English paragraph.",
                "Second English paragraph.",
                "Third English paragraph.",
            ],
            "paragraphs_zh": ["第一段中文。"],
        },
    )

    html = render_index_html(
        _edition(),
        local_articles_by_story_id={story.id: article},
        daily_local_article_capsules_article_hrefs_by_story_id={
            story.id: f"{story.id}.html",
        },
    )
    section_html = _daily_local_article_capsules_section_html(html)

    assert "First English paragraph." in section_html
    assert "第一段中文。" in section_html
    assert "Second English paragraph." in section_html
    assert "Third English paragraph." in section_html
    assert section_html.count("第一段中文。") == 1


def test_render_index_html_places_daily_local_article_capsules_between_sections() -> None:
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Organization card", zh="组织卡片"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                        section_label=LocalizedText(en="Entity", zh="实体"),
                        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
                        detail_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                        references=(),
                    )
                ],
            )
        ]
    )
    app_payload = {
        "daily_digest": {
            "briefing_topics": [
                {
                    "topic_type": "brand",
                    "title": {"en": "The Row", "zh": "The Row"},
                    "label": {"en": "Brand", "zh": "品牌"},
                    "story_count": 1,
                    "evidence_count": 1,
                    "positive_heat_delta_sum": 4,
                    "max_heat_delta": 4,
                    "story_ids": ["the-row-signal-1234567890"],
                    "cards": [
                        {
                            "id": "the-row-signal-1234567890",
                            "headline": {"en": "The Row source", "zh": "The Row 来源"},
                            "source_name": "Vogue Business",
                        }
                    ],
                    "source_refs": [
                        {"name": "The Row", "type": "brand", "label": "rising"},
                    ],
                }
            ]
        }
    }

    html = render_index_html(
        _edition(),
        app_payload=app_payload,
        saved_article_content_organization=organization,
        local_articles_by_story_id={
            "the-row-signal-1234567890": _signal_briefing_local_article(),
        },
        daily_local_heat_signals_article_hrefs_by_story_id={
            "the-row-signal-1234567890": "the-row-signal-1234567890.html",
        },
        daily_local_article_capsules_article_hrefs_by_story_id={
            "the-row-signal-1234567890": "the-row-signal-1234567890.html",
        },
    )

    assert html.index('class="daily-local-heat-signals"') < html.index(
        'class="daily-local-article-capsules"'
    )
    assert html.index('class="daily-local-article-capsules"') < html.index(
        'class="saved-article-content-organization"'
    )


def test_render_index_html_places_daily_local_key_signals_digest_between_saved_sections() -> None:
    briefs = RowOneSavedArticleBriefs(
        article_count=1,
        items=[
            _saved_article_brief_item(
                detail_path="details/the-row-signal-1234567890.html#local-article-digest",
                title="Saved article brief",
            )
        ],
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Organization card", zh="组织卡片"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                        section_label=LocalizedText(en="Entity", zh="实体"),
                        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
                        detail_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                        references=(),
                    )
                ],
            )
        ]
    )
    digest = RowOneDailyLocalKeySignalsDigest(
        article_count=1,
        groups=(
            RowOneDailyLocalKeySignalsDigestGroup(
                key="why_it_matters",
                title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                total_count=1,
                entries=(
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Digest entry", zh="摘要条目"),
                        body=LocalizedText(en="Digest body.", zh="摘要正文。"),
                        href=(
                            "articles/the-row-signal-1234567890.html"
                            "#saved-article-key-signals-title"
                        ),
                        source_name="Vogue Business",
                    ),
                ),
            ),
        ),
    )

    index_html = render_index_html(
        _edition(),
        saved_article_briefs=briefs,
        daily_local_key_signals_digest=digest,
        saved_article_content_organization=organization,
    )

    assert index_html.index('class="saved-article-briefs"') < index_html.index(
        'class="daily-local-key-signals-digest"'
    )
    assert index_html.index('class="daily-local-key-signals-digest"') < index_html.index(
        'class="saved-article-content-organization"'
    )


def test_render_index_html_places_daily_local_signal_momentum_between_sections() -> None:
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Organization card", zh="组织卡片"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                        section_label=LocalizedText(en="Entity", zh="实体"),
                        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
                        detail_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                        references=(),
                    )
                ],
            )
        ]
    )
    digest = RowOneDailyLocalKeySignalsDigest(
        article_count=1,
        groups=(
            RowOneDailyLocalKeySignalsDigestGroup(
                key="why_it_matters",
                title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                total_count=1,
                entries=(
                    RowOneDailyLocalKeySignalsDigestEntry(
                        title=LocalizedText(en="Digest entry", zh="摘要条目"),
                        body=LocalizedText(en="Digest body.", zh="摘要正文。"),
                        href=(
                            "articles/the-row-signal-1234567890.html"
                            "#saved-article-key-signals-title"
                        ),
                        source_name="Vogue Business",
                    ),
                ),
            ),
        ),
    )
    leaderboard = RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=1,
        item_count=1,
        buckets=(
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        article_count=1,
                        source_count=1,
                        supports=(
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="The Row source", zh="The Row 来源"),
                                source_name="Vogue Business",
                                href=(
                                    "details/the-row-signal-1234567890.html#local-article-digest"
                                ),
                                detail_path="details/the-row-signal-1234567890.html",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    index_html = render_index_html(
        _edition(),
        daily_local_key_signals_digest=digest,
        daily_local_signal_momentum=leaderboard,
        daily_local_signal_momentum_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
        },
        saved_article_content_organization=organization,
    )

    assert index_html.index('class="daily-local-key-signals-digest"') < index_html.index(
        'class="daily-local-signal-momentum"'
    )
    assert index_html.index('class="daily-local-signal-momentum"') < index_html.index(
        'class="saved-article-content-organization"'
    )


def test_render_index_html_places_daily_local_heat_signals_between_sections() -> None:
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Organization card", zh="组织卡片"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                        section_label=LocalizedText(en="Entity", zh="实体"),
                        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
                        detail_path=(
                            "details/the-row-signal-1234567890.html#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                        references=(),
                    )
                ],
            )
        ]
    )
    leaderboard = RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=1,
        item_count=1,
        buckets=(
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        article_count=1,
                        source_count=1,
                        supports=(
                            RowOneSavedArticleDailySignalLeaderboardSupport(
                                title=LocalizedText(en="The Row source", zh="The Row 来源"),
                                source_name="Vogue Business",
                                href=(
                                    "details/the-row-signal-1234567890.html#local-article-digest"
                                ),
                                detail_path="details/the-row-signal-1234567890.html",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
    app_payload = {
        "daily_digest": {
            "briefing_topics": [
                {
                    "topic_type": "brand",
                    "title": {"en": "The Row", "zh": "The Row"},
                    "label": {"en": "Brand", "zh": "品牌"},
                    "story_count": 1,
                    "evidence_count": 1,
                    "positive_heat_delta_sum": 4,
                    "max_heat_delta": 4,
                    "story_ids": ["the-row-signal-1234567890"],
                    "cards": [
                        {
                            "id": "the-row-signal-1234567890",
                            "headline": {"en": "The Row source", "zh": "The Row 来源"},
                            "source_name": "Vogue Business",
                        }
                    ],
                    "source_refs": [
                        {"name": "The Row", "type": "brand", "label": "rising"},
                    ],
                }
            ]
        }
    }

    index_html = render_index_html(
        _edition(),
        app_payload=app_payload,
        daily_local_signal_momentum=leaderboard,
        daily_local_signal_momentum_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
        },
        saved_article_content_organization=organization,
        local_articles_by_story_id={
            "the-row-signal-1234567890": _signal_briefing_local_article(),
        },
        daily_local_heat_signals_article_hrefs_by_story_id={
            "the-row-signal-1234567890": "the-row-signal-1234567890.html",
        },
    )

    assert index_html.index('class="daily-local-signal-momentum"') < index_html.index(
        'class="daily-local-heat-signals"'
    )
    assert index_html.index('class="daily-local-heat-signals"') < index_html.index(
        'class="saved-article-content-organization"'
    )


def test_render_row_one_site_omits_daily_edit_without_usable_payload() -> None:
    index_html = render_index_html(_edition(), app_payload={})
    index_html_none = render_index_html(_edition(), app_payload=None)

    assert 'class="daily-edit"' not in index_html
    assert "Daily Edit" not in index_html
    assert "今日编辑简报" not in index_html
    assert 'class="daily-edit"' not in index_html_none
    assert "Daily Edit" not in index_html_none
    assert "今日编辑简报" not in index_html_none


def test_render_row_one_site_escapes_daily_edit_payload_values() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {
                "title": {"en": "Brief", "zh": "总览"},
                "dek": {"en": "Dek", "zh": "说明"},
                "lead_story_headline": "Lead <script>alert(1)</script>",
                "lead_story_href": "javascript:alert(1)",
                "summary_points": [
                    {"en": "Point <b>bold</b>", "zh": "要点 <b>粗体</b>"},
                ],
                "metrics": [
                    {
                        "key": "evidence",
                        "label": {"en": "Evidence", "zh": "证据"},
                        "value": 1,
                    },
                ],
                "links": [],
            },
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "Dek", "zh": "说明"},
                "boundaries": {"en": "Boundary <i>", "zh": "边界 <i>"},
                "groups": [
                    {
                        "label": {"en": "Brands", "zh": "品牌"},
                        "signals": [
                            {
                                "name": "Signal <script>",
                                "summary": {"en": "Summary <b>", "zh": "摘要 <b>"},
                                "lead_story_href": "https://evil.example/story",
                                "story_count": 1,
                                "evidence_count": 2,
                                "max_heat_delta": 3,
                                "label": "brand",
                            }
                        ],
                    }
                ],
            },
            "daily_digest": {"blocks": [], "briefing_topics": []},
        },
    )

    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Lead &lt;script&gt;alert(1)&lt;/script&gt;" in section_html
    assert "Point &lt;b&gt;bold&lt;/b&gt;" in section_html
    assert "Signal &lt;script&gt;" in section_html
    assert "Summary &lt;b&gt;" in section_html
    assert "Boundary &lt;i&gt;" in section_html
    assert "<script>" not in section_html
    assert "<b>" not in section_html
    assert "javascript:alert" not in section_html
    assert "https://evil.example" not in section_html
    assert 'href="#main-content"' in section_html


def test_render_row_one_site_daily_edit_uses_briefing_topic_fallback() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {"summary_points": [], "metrics": [], "links": []},
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "No signals", "zh": "暂无信号"},
                "boundaries": {"en": "Existing evidence only.", "zh": "仅限现有证据。"},
                "groups": [{"label": {"en": "Brands", "zh": "品牌"}, "signals": [{"name": ""}]}],
            },
            "daily_digest": {
                "evidence_count": 2,
                "blocks": [],
                "briefing_topics": [
                    {
                        "topic_type": "brand",
                        "title": {"en": "Fallback Brand", "zh": "备用品牌"},
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 1,
                        "evidence_count": 2,
                        "positive_heat_delta_sum": 4,
                        "lead_story": {
                            "detail_href": "details/fallback-brand-1234567890.html",
                            "headline": {"en": "Fallback brand signal", "zh": "备用品牌信号"},
                            "editorial_takeaway": {
                                "en": "Topic fallback summary.",
                                "zh": "主题备用摘要。",
                            },
                        },
                    }
                ],
            },
        },
    )

    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Fallback Brand" in section_html
    assert "备用品牌" in section_html
    assert "Topic fallback summary." in section_html
    assert 'href="details/fallback-brand-1234567890.html"' in section_html


def test_render_row_one_site_daily_edit_handles_topic_fallback_without_title() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {"summary_points": [], "metrics": [], "links": []},
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "No signals", "zh": "暂无信号"},
                "boundaries": {"en": "Existing evidence only.", "zh": "仅限现有证据。"},
                "groups": [{"label": {"en": "Brands", "zh": "品牌"}, "signals": [{"name": ""}]}],
            },
            "daily_digest": {
                "evidence_count": 2,
                "blocks": [],
                "briefing_topics": [
                    {
                        "topic_type": "brand",
                        "label": {"en": "Brand", "zh": "品牌"},
                        "story_count": 1,
                        "evidence_count": 2,
                        "positive_heat_delta_sum": 4,
                        "cards": [
                            {
                                "detail_href": "details/fallback-brand-1234567890.html",
                                "headline": {
                                    "en": "Fallback brand signal",
                                    "zh": "备用品牌信号",
                                },
                                "editorial_takeaway": {
                                    "en": "Topic fallback summary.",
                                    "zh": "主题备用摘要。",
                                },
                            }
                        ],
                        "lead_story": {
                            "detail_href": "details/fallback-brand-1234567890.html",
                            "headline": {"en": "Fallback brand signal", "zh": "备用品牌信号"},
                            "editorial_takeaway": {
                                "en": "Topic fallback summary.",
                                "zh": "主题备用摘要。",
                            },
                        },
                    }
                ],
            },
        },
    )

    assert 'class="daily-edit"' in index_html
    assert "Fallback brand signal" in index_html
    assert "Topic fallback summary." in index_html


def test_render_row_one_site_daily_edit_uses_digest_block_read_next() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {"summary_points": [], "metrics": [], "links": []},
            "signal_synthesis": {
                "title": {"en": "Signals", "zh": "信号"},
                "dek": {"en": "Signals dek", "zh": "信号说明"},
                "boundaries": {"en": "Existing evidence only.", "zh": "仅限现有证据。"},
                "groups": [],
            },
            "daily_digest": {
                "evidence_count": 1,
                "briefing_topics": [],
                "blocks": [
                    {
                        "key": "read_first",
                        "story_ids": ["read-first-1234567890"],
                        "cards": [{"id": "read-first-1234567890"}],
                    },
                    {
                        "key": "key_takeaways",
                        "title": {"en": "Key Takeaways", "zh": "重点整理"},
                        "dek": {"en": "Follow-up reads.", "zh": "后续阅读。"},
                        "cards": [
                            {
                                "id": "read-next-1234567890",
                                "detail_href": "details/read-next-1234567890.html",
                                "headline": {"en": "Read next headline", "zh": "继续阅读标题"},
                                "editorial_takeaway": {
                                    "en": "Read next summary.",
                                    "zh": "继续阅读摘要。",
                                },
                            }
                        ],
                    },
                ],
            },
        },
    )

    section_start = index_html.index('class="daily-edit"')
    section_html = index_html[
        section_start : index_html.index("</section>", section_start) + len("</section>")
    ]

    assert "Read next headline" in section_html
    assert "继续阅读标题" in section_html
    assert "Read next summary." in section_html
    assert 'href="details/read-next-1234567890.html"' in section_html


def test_render_row_one_site_escapes_edition_brief_payload_values() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "edition_brief": {
                "title": {"en": "Brief <script>", "zh": "总览 <script>"},
                "dek": {"en": "Dek & quote", "zh": "说明 & <tag>"},
                "lead_story_id": "hostile-1111111111",
                "lead_story_href": "details/hostile-1111111111.html",
                "lead_story_headline": 'Headline <img src=x onerror="alert(1)">',
                "metrics": [
                    {"key": "stories", "label": {"en": "Stories <x>", "zh": "故事 <x>"}, "value": 1}
                ],
                "summary_points": [{"en": "Point <b>", "zh": "要点 <b>"}],
                "links": [
                    {
                        "key": "read_first",
                        "label": {"en": "Open <x>", "zh": "打开 <x>"},
                        "href": "details/hostile-1111111111.html",
                    },
                    {
                        "key": "unsafe_js",
                        "label": {"en": "Unsafe JS", "zh": "不安全 JS"},
                        "href": "javascript:alert(1)",
                    },
                    {
                        "key": "unsafe_external",
                        "label": {"en": "Unsafe External", "zh": "不安全外链"},
                        "href": "https://evil.example/story",
                    },
                    {
                        "key": "unsafe_detail",
                        "label": {"en": "Unsafe Detail", "zh": "不安全详情"},
                        "href": "details/../escape.html",
                    },
                ],
            }
        },
    )

    assert "Brief &lt;script&gt;" in index_html
    assert "Headline &lt;img" in index_html
    assert "Point &lt;b&gt;" in index_html
    assert "Open &lt;x&gt;" in index_html
    assert 'onerror="alert' not in index_html
    assert "onerror=&quot;alert" in index_html
    assert "<script>" not in index_html
    assert 'href="details/hostile-1111111111.html"' in index_html
    assert "javascript:alert" not in index_html
    assert "https://evil.example" not in index_html
    assert "details/../escape.html" not in index_html


def test_render_row_one_site_escapes_signal_synthesis_payload_values() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "signal_synthesis": {
                "title": {"zh": "<script>标题</script>", "en": "<b>Signal</b>"},
                "dek": {"zh": "本地 <b>观察</b>", "en": "Local <b>observed</b>"},
                "boundaries": {
                    "zh": "本地观察，需人工复核。",
                    "en": "Local observed signals; review required.",
                },
                "group_count": 1,
                "signal_count": 1,
                "groups": [
                    {
                        "key": "brand",
                        "label": {"zh": "<b>品牌</b>", "en": "<b>Brands</b>"},
                        "signal_count": 1,
                        "signals": [
                            {
                                "name": "<img src=x onerror=alert(1)>",
                                "type": "brand",
                                "label": "<script>alert(1)</script>",
                                "story_count": 1,
                                "evidence_count": 1,
                                "positive_heat_delta_sum": 1,
                                "max_heat_delta": 1,
                                "lead_story_id": "the-row-signal-1234567890",
                                "lead_story_href": "../escape.html",
                                "summary": {
                                    "zh": "<b>危险</b>",
                                    "en": "<b>Unsafe</b>",
                                },
                                "story_ids": ["the-row-signal-1234567890"],
                            }
                        ],
                    }
                ],
            }
        },
    )

    assert "<script>" not in index_html
    assert "<img src=x" not in index_html
    assert "&lt;b&gt;Signal&lt;/b&gt;" in index_html
    assert "&lt;b&gt;Unsafe&lt;/b&gt;" in index_html
    assert "&lt;img src=x onerror=alert(1)&gt;" in index_html
    assert "../escape.html" not in index_html


def test_row_one_css_includes_edition_brief_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".edition-brief",
        ".edition-brief-metrics",
        ".edition-brief-links",
        ".edition-brief-metric",
        ".signal-synthesis",
        ".signal-synthesis-header",
        ".signal-synthesis-grid",
        ".signal-synthesis-group",
        ".signal-synthesis-card",
    ):
        assert selector in css_text


def test_row_one_css_includes_daily_edit_styles(tmp_path) -> None:
    index_path = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (index_path.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".daily-edit",
        ".daily-edit-header",
        ".daily-edit-grid",
        ".daily-edit-card",
        ".daily-edit-card-meta",
        ".daily-edit-link",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)

    assert "@media (max-width: 760px)" in css_text
    assert re.search(r"\.daily-edit-grid\s*\{[^}]*grid-template-columns:\s*1fr", css_text)


def test_row_one_css_includes_editorial_brief_source_trail_styles(tmp_path) -> None:
    index_path = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (index_path.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".editorial-brief-trail",
        ".editorial-brief-trail-item",
        ".editorial-brief-trail a",
        ".editorial-brief-link",
    ):
        assert selector in css_text


def test_row_one_css_includes_stage_323_local_first_and_evidence_selectors() -> None:
    css = row_one_css()

    for selector in (
        ".local-read-path",
        ".local-read-path-badge",
        ".local-read-action",
        ".saved-article-content-organization-card-link",
        ".saved-article-content-organization-evidence",
        ".saved-article-content-organization-evidence-link",
    ):
        assert selector in css


def test_row_one_css_includes_saved_article_content_organization_group_summary_styles() -> None:
    css = row_one_css()

    for selector in (
        ".saved-article-content-organization-summary",
        ".saved-article-content-organization-summary-metric",
        ".saved-article-content-organization-summary-refs",
        ".saved-article-content-organization-summary-ref",
    ):
        assert selector in css


def test_row_one_css_includes_local_article_information_styles() -> None:
    css = row_one_css()

    for selector in (
        ".local-article-information",
        ".local-article-information-header",
        ".local-article-information-metrics",
        ".local-article-information-grid",
        ".local-article-information-card",
        ".local-article-information-refs",
        ".local-article-information-paragraphs",
    ):
        assert selector in css


def test_row_one_css_includes_saved_article_local_reading_companion_styles() -> None:
    css = row_one_css()

    for selector in (
        ".saved-article-local-reading-companion",
        ".saved-article-local-reading-companion-header",
        ".saved-article-local-reading-companion-metrics",
        ".saved-article-local-reading-companion-links",
        ".saved-article-local-reading-companion-current",
        ".saved-article-local-reading-companion-related",
        ".saved-article-local-reading-companion-item",
        ".saved-article-local-reading-companion-meta",
        ".saved-article-local-reading-companion-refs",
        ".saved-article-local-reading-companion-action",
    ):
        assert selector in css


def test_row_one_css_includes_saved_article_local_section_binder_styles() -> None:
    css = row_one_css()

    for selector in (
        ".saved-article-local-section-binder",
        ".saved-article-local-section-binder-header",
        ".saved-article-local-section-binder-meta",
        ".saved-article-local-section-binder-grid",
        ".saved-article-local-section-binder-row",
        ".saved-article-local-section-binder-chips",
        ".saved-article-local-section-binder-refs",
        ".saved-article-local-section-binder-paragraphs",
        ".saved-article-local-section-binder-unfiled",
    ):
        assert selector in css


def test_row_one_css_includes_saved_article_key_signals_styles() -> None:
    css = row_one_css()

    for selector in (
        ".saved-article-key-signals",
        ".saved-article-key-signals-header",
        ".saved-article-key-signals-meta",
        ".saved-article-key-signals-grid",
        ".saved-article-key-signal",
        ".saved-article-key-signal-statement",
        ".saved-article-key-signal-refs",
        ".saved-article-key-signal-ref",
        ".saved-article-key-signal-themes",
        ".saved-article-key-signal-evidence",
    ):
        assert selector in css


def test_row_one_css_includes_daily_local_key_signals_digest_styles() -> None:
    css = row_one_css()

    for selector in (
        ".daily-local-key-signals-digest",
        ".daily-local-key-signals-digest-header",
        ".daily-local-key-signals-digest-metrics",
        ".daily-local-key-signals-digest-grid",
        ".daily-local-key-signals-digest-group",
        ".daily-local-key-signals-digest-entry",
        ".daily-local-key-signals-digest-meta",
        ".daily-local-key-signals-digest-action",
    ):
        assert selector in css


def test_row_one_css_includes_daily_local_signal_momentum_styles() -> None:
    css = row_one_css()

    for selector in (
        ".daily-local-signal-momentum",
        ".daily-local-signal-momentum-header",
        ".daily-local-signal-momentum-metrics",
        ".daily-local-signal-momentum-grid",
        ".daily-local-signal-momentum-bucket",
        ".daily-local-signal-momentum-item",
        ".daily-local-signal-momentum-label",
        ".daily-local-signal-momentum-counts",
        ".daily-local-signal-momentum-supports",
        ".daily-local-signal-momentum-support",
    ):
        assert selector in css


def test_row_one_css_includes_daily_local_heat_signals_styles() -> None:
    css = row_one_css()

    for selector in (
        ".daily-local-heat-signals",
        ".daily-local-heat-signals-header",
        ".daily-local-heat-signals-metrics",
        ".daily-local-heat-signals-grid",
        ".daily-local-heat-signals-topic",
        ".daily-local-heat-signals-topic-header",
        ".daily-local-heat-signals-topic-title",
        ".daily-local-heat-signals-topic-stories",
        ".daily-local-heat-signals-story",
        ".daily-local-heat-signals-story-meta",
    ):
        assert selector in css


def test_row_one_css_includes_daily_local_article_capsules_styles() -> None:
    css = row_one_css()

    for selector in (
        ".daily-local-article-capsules",
        ".daily-local-article-capsules-header",
        ".daily-local-article-capsules-metrics",
        ".daily-local-article-capsules-grid",
        ".daily-local-article-capsule",
        ".daily-local-article-capsule-header",
        ".daily-local-article-capsule-title",
        ".daily-local-article-capsule-meta",
        ".daily-local-article-capsule-paragraphs",
        ".daily-local-article-capsule-paragraph",
        ".daily-local-article-capsule-refs",
        ".daily-local-article-capsule-link",
    ):
        assert selector in css


def test_row_one_css_includes_local_article_paragraph_context_styles() -> None:
    css = row_one_css()

    for selector in (
        ".local-article-paragraph-context",
        ".local-article-paragraph-context-label",
        ".local-article-paragraph-context-links",
        ".local-article-paragraph-context a",
    ):
        assert selector in css


def test_row_one_css_includes_local_article_map_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".local-article-map",
        ".local-article-map a",
        ".local-article-paragraph-evidence",
        ".local-article-paragraph-evidence-header",
        ".local-article-paragraph-evidence-grid",
        ".local-article-paragraph-evidence-row",
        ".local-article-paragraph-evidence-link",
        ".local-article-paragraph-evidence-excerpt",
        ".local-article-paragraph-evidence-support",
        ".local-article-paragraph-evidence-supports",
        ".local-article-paragraph-evidence-ref",
        ".local-article-reader {",
        ".local-article-reader-list {",
        ".local-article-reader-list a {",
        ".local-article-reader-number {",
        ".local-article-reader-excerpt {",
        ".local-article-digest {",
        ".local-article-digest-header {",
        ".local-article-digest-grid {",
        ".local-article-digest-card {",
        ".local-article-digest-card h4 {",
        ".local-article-digest-list {",
        ".local-article-digest-link-list {",
        ".local-article-content-paragraph-links a",
        ".local-article-body p:target",
    ):
        assert selector in css_text


def test_row_one_css_includes_saved_article_coverage_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-coverage",
        ".saved-article-coverage-header",
        ".saved-article-coverage-metrics",
        ".saved-article-coverage-sources",
        ".saved-article-coverage-grid",
        ".saved-article-coverage-card",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_article_briefs_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-briefs",
        ".saved-article-briefs-header",
        ".saved-article-briefs-grid",
        ".saved-article-brief-card",
        ".saved-article-brief-meta",
        ".saved-article-brief-body",
        ".saved-article-brief-chip-groups",
        ".saved-article-brief-chip-group",
        ".saved-article-brief-chip-heading",
        ".saved-article-brief-chip-list",
        ".saved-article-brief-chip",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_article_library_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-library-entry",
        ".saved-article-library-entry-header",
        ".saved-article-library-entry-metrics",
        ".saved-article-library-page",
        ".saved-article-library-hero",
        ".saved-article-library-metrics",
        ".saved-article-library-source",
        ".saved-article-library-grid",
        ".saved-article-library-card",
        ".saved-article-library-card-meta",
        ".saved-article-library-actions",
        ".saved-article-library-refs",
        ".saved-article-library-paragraphs",
        ".saved-article-body-guide",
        ".saved-article-body-guide-header",
        ".saved-article-body-guide-list",
        ".saved-article-body-guide-item",
        ".saved-article-body-guide-label",
        ".saved-article-body-guide-body",
        ".saved-article-body-guide-link",
        ".saved-article-body-guide-evidence",
        ".saved-article-source-brief",
        ".saved-article-source-brief-header",
        ".saved-article-source-brief-metrics",
        ".saved-article-source-brief-list",
        ".saved-article-source-brief-item",
        ".saved-article-source-brief-label",
        ".saved-article-source-brief-body",
        ".saved-article-source-brief-link",
        ".saved-article-source-routes",
        ".saved-article-source-routes-header",
        ".saved-article-source-routes-metrics",
        ".saved-article-source-routes-list",
        ".saved-article-source-routes-item",
        ".saved-article-source-route",
        ".saved-article-source-routes-label",
        ".saved-article-source-routes-meta",
        ".saved-article-source-routes-link",
        ".saved-article-reading-queue",
        ".saved-article-reading-queue-header",
        ".saved-article-reading-queue-list",
        ".saved-article-reading-queue-item",
        ".saved-article-reading-queue-title",
        ".saved-article-reading-queue-meta",
        ".saved-article-reading-queue-action",
        ".saved-article-read-next-clusters",
        ".saved-article-read-next-clusters-header",
        ".saved-article-read-next-clusters-metrics",
        ".saved-article-read-next-clusters-grid",
        ".saved-article-read-next-clusters-cluster",
        ".saved-article-read-next-clusters-item",
        ".saved-article-read-next-clusters-meta",
        ".saved-article-read-next-clusters-lead",
        ".saved-article-read-next-clusters-refs",
        ".saved-article-read-next-clusters-action",
        ".saved-article-signal-facets",
        ".saved-article-signal-facets-header",
        ".saved-article-signal-facets-grid",
        ".saved-article-signal-facets-row",
        ".saved-article-signal-facets-article",
        ".saved-article-signal-facets-source",
        ".saved-article-signal-facets-column",
        ".saved-article-signal-facets-chip",
        ".saved-article-daily-signal-leaderboard",
        ".saved-article-daily-signal-leaderboard-header",
        ".saved-article-daily-signal-leaderboard-grid",
        ".saved-article-daily-signal-leaderboard-bucket",
        ".saved-article-daily-signal-leaderboard-item",
        ".saved-article-daily-signal-leaderboard-label",
        ".saved-article-daily-signal-leaderboard-metrics",
        ".saved-article-daily-signal-leaderboard-supports",
        ".saved-article-daily-signal-leaderboard-support",
        ".saved-article-daily-summary",
        ".saved-article-daily-summary-header",
        ".saved-article-daily-summary-metrics",
        ".saved-article-daily-summary-links",
        ".saved-article-daily-summary-link",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_signal_index_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-signal-index",
        ".saved-signal-index-header",
        ".saved-signal-index-metrics",
        ".saved-signal-index-grid",
        ".saved-signal-index-card",
        ".saved-signal-index-card-header",
        ".saved-signal-index-card-meta",
        ".saved-signal-index-support",
        ".saved-signal-index-support-row",
        ".saved-signal-index-support-meta",
        ".saved-signal-index-support-excerpt",
        ".saved-signal-index-actions",
        ".saved-signal-index-paragraphs",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_article_reading_path_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-reading-paths",
        ".saved-article-reading-paths-header",
        ".saved-article-reading-paths-grid",
        ".saved-article-reading-path-card",
        ".saved-article-reading-path-card-header",
        ".saved-article-reading-path-count",
        ".saved-article-reading-path-steps",
        ".saved-article-reading-path-step",
        ".saved-article-reading-path-step-link",
        ".saved-article-reading-path-step-number",
        ".saved-article-reading-path-step-copy",
        ".saved-article-reading-path-step-meta",
        ".saved-article-reading-path-step-lead",
        ".saved-article-reading-path-link",
        ".saved-article-reading-path-evidence",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_article_theme_digest_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-theme-digest",
        ".saved-article-theme-digest-header",
        ".saved-article-theme-digest-metrics",
        ".saved-article-theme-digest-grid",
        ".saved-article-theme-digest-card",
        ".saved-article-theme-digest-card-header",
        ".saved-article-theme-digest-card-meta",
        ".saved-article-theme-digest-items",
        ".saved-article-theme-digest-item",
        ".saved-article-theme-digest-item-meta",
        ".saved-article-theme-digest-lead",
        ".saved-article-theme-digest-actions",
        ".saved-article-theme-digest-evidence",
        ".saved-article-theme-digest-refs",
        ".saved-article-theme-digest-link",
        ".saved-article-theme-digest-ref",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_article_reference_atlas_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-reference-atlas",
        ".saved-article-reference-atlas-header",
        ".saved-article-reference-atlas-metrics",
        ".saved-article-reference-atlas-grid",
        ".saved-article-reference-atlas-bucket",
        ".saved-article-reference-atlas-bucket-header",
        ".saved-article-reference-atlas-list",
        ".saved-article-reference-atlas-entry",
        ".saved-article-reference-atlas-entry-meta",
        ".saved-article-reference-atlas-support",
        ".saved-article-reference-atlas-support-meta",
        ".saved-article-reference-atlas-lead",
        ".saved-article-reference-atlas-actions",
        ".saved-article-reference-atlas-evidence",
        ".saved-article-reference-atlas-link",
        ".saved-article-reference-atlas-ref",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_saved_article_evidence_board_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-evidence-board",
        ".saved-article-evidence-board-header",
        ".saved-article-evidence-board-metrics",
        ".saved-article-evidence-board-grid",
        ".saved-article-evidence-board-group",
        ".saved-article-evidence-board-group-header",
        ".saved-article-evidence-board-cards",
        ".saved-article-evidence-board-card",
        ".saved-article-evidence-board-card-meta",
        ".saved-article-evidence-board-paragraph",
        ".saved-article-evidence-board-excerpt",
        ".saved-article-evidence-board-actions",
        ".saved-article-evidence-board-link",
        ".saved-article-evidence-board-refs",
        ".saved-article-evidence-board-ref",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_continue_reading_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".continue-reading",
        ".continue-reading-header",
        ".continue-reading-grid",
        ".continue-reading-card",
        ".continue-reading-card a",
        ".continue-reading-section",
        ".continue-reading-source",
        ".continue-reading-excerpt",
        ".continue-reading-excerpt span",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_row_one_css_includes_detail_signal_briefing_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".detail-signal-briefing",
        ".detail-signal-briefing-header",
        ".detail-signal-briefing-grid",
        ".detail-signal-briefing-card",
        ".detail-signal-briefing-meta",
        ".detail-signal-briefing-ref",
        ".detail-signal-briefing-cues",
        ".detail-signal-briefing-cue-grid",
        ".detail-signal-briefing-cue",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)


def test_render_row_one_site_escapes_briefing_path_payload_values() -> None:
    index_html = render_index_html(
        _edition(),
        app_payload={
            "daily_digest": {
                "blocks": [
                    {
                        "key": "read_first",
                        "story_count": 1,
                        "story_ids": ["skip-1111111111"],
                        "cards": [{"id": "skip-1111111111"}],
                    },
                    {
                        "key": "key_takeaways",
                        "title": {
                            "en": 'Path <script>alert("x")</script>',
                            "zh": "路径 <script>",
                        },
                        "dek": {
                            "en": 'Dek & "quote"',
                            "zh": "说明 & <tag>",
                        },
                        "story_count": 1,
                        "cards": [
                            {
                                "id": "hostile-2222222222",
                                "detail_href": "details/hostile-2222222222.html",
                                "headline": {
                                    "en": 'Headline <img src=x onerror="alert(1)">',
                                    "zh": "标题 <img>",
                                },
                                "editorial_takeaway": {
                                    "en": "Takeaway <b>bold</b> & more",
                                    "zh": "观点 <b>",
                                },
                                "source_name": 'Source <script>alert("x")</script>',
                                "published_date": "2026-07-02",
                                "evidence_count": 1,
                                "heat_delta": 2,
                            },
                        ],
                    },
                ],
            },
        },
    )
    path_match = re.search(
        r'<section id="briefing-path" class="briefing-path" aria-label="Briefing path">'
        r"(?P<path>.*?)</section>",
        index_html,
        re.S,
    )

    assert path_match is not None
    path_html = path_match.group("path")
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in path_html
    assert "Dek &amp; &quot;quote&quot;" in path_html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in path_html
    assert "Takeaway &lt;b&gt;bold&lt;/b&gt; &amp; more" in path_html
    assert "Source &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in path_html
    assert "<script>" not in path_html
    assert "<img" not in path_html
    assert "<b>" not in path_html


def test_render_row_one_site_includes_story_display_visual_slots(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    css = (tmp_path / "assets" / "row-one.css").read_text(encoding="utf-8")

    assert "story-visual story-visual--editorial story-visual--ink lead-story-visual" in index_html
    assert "story-visual story-visual--editorial story-visual--ink story-card-visual" in index_html
    assert "story-visual story-visual--editorial story-visual--ink detail-visual" in detail_html
    assert 'data-display-variant="editorial"' in index_html
    assert 'data-display-variant="editorial"' in detail_html
    assert "THE ROW" in index_html
    assert "THE ROW" in detail_html
    assert "--paper: #f4f6f8;" in css
    assert "--accent: #2454ff;" in css
    assert ".edition-nav-grid" not in css
    assert "#f5f1ea" not in css
    assert "#7d1f2d" not in css


def test_render_row_one_site_renders_safe_display_image_and_omits_unsafe_image(
    tmp_path,
) -> None:
    edition = _edition()
    edition.stories[0].display = RowOneStoryDisplay(
        variant="editorial",
        accent="ink",
        image=RowOneStoryImage(
            src="assets/images/the-row.png",
            alt=LocalizedText(zh="The Row 图片", en="The Row image"),
        ),
    )

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert '<img src="assets/images/the-row.png"' in index_html
    assert 'alt="The Row image"' in index_html
    assert 'data-alt-en="The Row image"' in index_html
    assert 'data-alt-zh="The Row 图片"' in index_html
    assert '<img src="../assets/images/the-row.png"' in detail_html
    detail_visual_match = re.search(
        r'<figure class="story-visual story-visual--editorial story-visual--ink detail-visual"'
        r"[^>]*>(?P<visual>.*?)</figure>",
        detail_html,
        re.S,
    )
    assert detail_visual_match is not None
    assert 'src="../assets/images/the-row.png"' in detail_visual_match.group("visual")

    edition.stories[0].display.image.src = "../secret.png"
    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert "../secret.png" not in index_html
    assert "../secret.png" not in detail_html
    assert "story-visual-fallback" in index_html
    assert "story-visual-fallback" in detail_html


def test_row_one_js_persists_language_preference(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    script = (tmp_path / "assets" / "row-one.js").read_text(encoding="utf-8")

    assert 'storageKey = "row-one:language"' in script
    assert 'localizedImages = Array.from(document.querySelectorAll("img[data-alt-en]"))' in script
    assert "localStorage.getItem(storageKey)" in script
    assert "localStorage.setItem(storageKey, lang)" in script
    assert 'stored === "zh" || stored === "en"' in script
    assert 'image.setAttribute("alt", image.dataset.altZh || image.dataset.altEn || "")' in script
    assert "setLang(initialLang, { persist: false })" in script


def test_render_row_one_site_includes_index_and_detail_metadata(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert (
        '<meta name="description" content="ROW ONE organized 1 local fashion signal for today.">'
    ) in index_html
    assert '<meta property="og:title" content="ROW ONE' in index_html
    assert '<meta property="og:type" content="website">' in index_html
    assert '<meta name="twitter:card" content="summary">' in index_html

    assert (
        '<meta name="description" content="The Row signal with &lt;angle&gt; detail.">'
    ) in detail_html
    assert (
        '<meta property="og:description" content="The Row signal with &lt;angle&gt; detail.">'
    ) in detail_html
    assert (
        '<meta name="twitter:description" content="The Row signal with &lt;angle&gt; detail.">'
    ) in detail_html
    assert '<meta property="og:title" content="The Row &lt;signals&gt;' in detail_html
    assert '<meta property="og:type" content="article">' in detail_html
    assert (
        '<meta name="twitter:title" content="The Row &lt;signals&gt; &quot;quiet&quot; demand">'
    ) in detail_html


def test_render_row_one_site_writes_edition_contents_navigation(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="edition-nav"' in index_html
    assert 'aria-label="Edition contents"' in index_html
    assert 'href="#top_stories"' in index_html
    assert 'href="#brand_moves"' in index_html
    assert 'id="top_stories"' in index_html
    assert 'id="brand_moves"' in index_html
    assert index_html.index('class="edition-nav"') < index_html.index('class="section-block"')
    nav_match = re.search(
        r'<nav class="edition-nav" aria-label="Edition contents">(?P<nav>.*?)</nav>',
        index_html,
        re.S,
    )
    assert nav_match is not None
    nav_html = nav_match.group("nav")
    assert 'class="edition-rail"' in nav_html
    assert 'class="edition-nav-item edition-rail-item"' in nav_html
    assert "Top Stories" in nav_html
    assert "Brand Moves" in nav_html
    assert "1 story" in nav_html
    assert "0 stories" in nav_html
    assert "1 条" in nav_html
    assert "0 条" in nav_html
    assert "No stories in this section yet." in index_html


def test_render_row_one_site_includes_latest_edition_status_strip(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="edition-status"' in index_html
    assert "Latest Edition" in index_html
    assert "今日状态" in index_html
    assert "Generated" in index_html
    assert "2026-07-02T04:00:00Z" in index_html
    assert "Stories" in index_html
    assert '<span data-lang="en">1</span>' in index_html
    assert '<span data-lang="zh">1 条</span>' in index_html
    assert "Evidence links" in index_html
    assert "Empty sections" in index_html
    assert "Brand Moves" in index_html
    assert "品牌动态" in index_html
    assert "ready" in index_html
    assert "可阅读" in index_html


def test_render_row_one_site_status_strip_handles_empty_edition(tmp_path) -> None:
    edition = _edition()
    edition.stories = []

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert "empty" in index_html
    assert "暂无故事" in index_html
    assert '<span data-lang="en">0</span>' in index_html
    assert '<span data-lang="zh">0 条</span>' in index_html
    assert "Top Stories, Brand Moves" in index_html


def test_render_row_one_site_story_orientation_handles_single_link_and_undated(
    tmp_path,
) -> None:
    edition = _edition()
    edition.stories[0].published_at = None
    edition.stories[0].evidence = [edition.stories[0].evidence[0]]

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    orientation_match = re.search(
        r'<p class="story-orientation">(?P<orientation>.*?)</p>',
        index_html,
        re.S,
    )
    assert orientation_match is not None
    orientation_html = orientation_match.group("orientation")
    assert "Undated" in orientation_html
    assert "时间未标注" in orientation_html
    assert "1 evidence link" in orientation_html
    assert "1 条线索" in orientation_html


def test_render_row_one_site_latest_only_preserves_unrelated_files(tmp_path) -> None:
    keep_path = tmp_path / "keep.txt"
    stale_detail = tmp_path / "details" / "old.html"
    stale_asset = tmp_path / "assets" / "old.css"
    stale_data = tmp_path / "data" / "old.json"
    stale_articles = tmp_path / "articles" / "index.html"
    stale_detail.parent.mkdir(parents=True)
    stale_asset.parent.mkdir(parents=True)
    stale_data.parent.mkdir(parents=True)
    stale_articles.parent.mkdir(parents=True)
    keep_path.write_text("do not delete", encoding="utf-8")
    stale_detail.write_text("old", encoding="utf-8")
    stale_asset.write_text("old", encoding="utf-8")
    stale_data.write_text("old", encoding="utf-8")
    stale_articles.write_text("old", encoding="utf-8")
    (tmp_path / "index.html").write_text("old", encoding="utf-8")
    (tmp_path / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert keep_path.read_text(encoding="utf-8") == "do not delete"
    assert not stale_detail.exists()
    assert not stale_asset.exists()
    assert not stale_data.exists()
    assert not stale_articles.exists()
    assert not (tmp_path / "articles").exists()
    assert (tmp_path / "index.html").exists()


def test_render_row_one_site_latest_only_refuses_unmarked_directory_children(tmp_path) -> None:
    stale_asset = tmp_path / "assets" / "keep.css"
    stale_detail = tmp_path / "details" / "manual.html"
    stale_data = tmp_path / "data" / "manual.json"
    stale_articles = tmp_path / "articles" / "manual.html"
    stale_asset.parent.mkdir(parents=True)
    stale_detail.parent.mkdir(parents=True)
    stale_data.parent.mkdir(parents=True)
    stale_articles.parent.mkdir(parents=True)
    stale_asset.write_text("keep", encoding="utf-8")
    stale_detail.write_text("keep", encoding="utf-8")
    stale_data.write_text("keep", encoding="utf-8")
    stale_articles.write_text("keep", encoding="utf-8")

    with pytest.raises(ValueError, match="not marked"):
        render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert stale_asset.exists()
    assert stale_detail.exists()
    assert stale_data.exists()
    assert stale_articles.exists()


def test_render_row_one_site_writes_validated_detail_path(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].id = "not-the-path"

    render_row_one_site(edition, tmp_path)

    assert (tmp_path / "details" / "the-row-signal-1234567890.html").exists()
    assert not (tmp_path / "details" / "not-the-path.html").exists()


def test_render_row_one_site_rejects_detail_path_traversal(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].detail_path = "../escape.html"

    with pytest.raises(ValueError, match="Invalid ROW ONE detail path"):
        render_row_one_site(edition, tmp_path)


@pytest.mark.parametrize(
    "detail_path",
    [
        "details/%2e%2e%2fescape.html",
        "details/the-row\nsignal-1234567890.html",
        "details/the-row-signal.html",
    ],
)
def test_render_row_one_site_rejects_malformed_detail_paths(
    tmp_path,
    detail_path: str,
) -> None:
    edition = _edition()
    edition.stories[0].detail_path = detail_path

    with pytest.raises(ValueError, match="Invalid ROW ONE detail path"):
        render_row_one_site(edition, tmp_path)


def test_render_row_one_site_omits_malformed_https_links(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].source_url = "https:example.com/bad"
    edition.stories[0].evidence[0].url = "https:///bad"

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    assert "https:example.com" not in index_html
    assert "https:example.com" not in detail_html
    assert "https:///bad" not in detail_html


def test_clean_row_one_site_children_allows_missing_output_dir(tmp_path) -> None:
    site_dir = tmp_path / "missing"

    clean_row_one_site_children(site_dir)

    assert not site_dir.exists()


def test_render_row_one_site_writes_json_payload(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))

    assert payload["contract_version"] == "row-one-app/v7"
    assert payload["brand"] == "ROW ONE"
    assert payload["generated_at"] == "2026-07-02T04:00:00Z"
    assert payload["edition_date"] == "2026-07-02T04:00:00Z"
    assert payload["summary"]["zh"] == "ROW ONE 今日整理了 1 条本地时尚信号。"
    assert payload["story_count"] == 1
    assert payload["evidence_count"] == 1
    story = payload["stories"][0]
    brief = payload["edition_brief"]
    assert brief["title"] == {"zh": "今日总览", "en": "Edition Brief"}
    assert brief["lead_story_id"] == story["id"]
    assert brief["lead_story_href"] == story["detail_href"]
    assert brief["metrics"][0] == {
        "key": "stories",
        "label": {"zh": "故事", "en": "Stories"},
        "value": 1,
    }

    sections = {section["key"]: section for section in payload["sections"]}
    assert sections["top_stories"]["href"] == "#top_stories"
    assert sections["top_stories"]["story_count"] == 1
    assert sections["brand_moves"]["href"] == "#brand_moves"
    assert sections["brand_moves"]["story_count"] == 0

    assert story["id"] == "the-row-signal-1234567890"
    assert story["section_key"] == "top_stories"
    assert story["section"] == {
        "key": "top_stories",
        "title": {"zh": "今日重点", "en": "Top Stories"},
        "href": "#top_stories",
    }
    assert story["headline"] == 'The Row <signals> "quiet" demand'
    assert story["summary"] == {
        "zh": "来源摘要：The Row signal with <angle> detail.",
        "en": "Original source summary: The Row signal with <angle> detail.",
    }
    assert story["editorial_takeaway"]["en"] == "The Row is today's priority signal."
    assert story["signal_context"]["zh"] == "本地报告显示它来自 1 个来源。"
    assert story["reader_path"]["en"] == "Read the brief, then open the evidence link."
    assert story["detail_path"] == "details/the-row-signal-1234567890.html"
    assert story["href"] == "details/the-row-signal-1234567890.html"
    assert story["detail_href"] == "details/the-row-signal-1234567890.html"
    assert story["published_at"] == "2026-07-02T04:00:00Z"
    assert story["published_date"] == "2026-07-02"
    assert story["evidence_count"] == 1
    assert story["source_url"] == "https://example.com/the-row"
    assert story["evidence"][0]["url"] == "https://example.com/evidence"
    assert story["evidence"][0]["href"] == "https://example.com/evidence"
    assert story["evidence"][1]["url"] is None
    assert story["evidence"][1]["href"] is None

    story_directory = payload["story_directory"]
    assert story_directory["story_count"] == 1
    assert story_directory["story_ids"] == [story["id"]]
    assert story_directory["routes"] == [
        {
            "story_id": story["id"],
            "detail_href": story["detail_href"],
            "section_key": story["section_key"],
            "section_href": story["section"]["href"],
            "published_date": story["published_date"],
        }
    ]
    content_card = payload["content_sections"][0]["cards"][0]
    digest_card = payload["daily_digest"]["blocks"][0]["cards"][0]
    assert content_card["why_it_matters"] == story["why_it_matters"]
    assert content_card["signal_context"] == story["signal_context"]
    assert digest_card["why_it_matters"] == story["why_it_matters"]
    assert digest_card["signal_context"] == story["signal_context"]


def test_render_row_one_site_story_directory_preserves_story_order_and_routes(tmp_path) -> None:
    edition = _edition()
    base_story = edition.stories[0]
    brand_story = base_story.model_copy(
        deep=True,
        update={
            "id": "brand-route-1111111111",
            "section_key": "brand_moves",
            "headline": "Brand route",
            "published_at": None,
            "detail_path": "details/brand-route-1111111111.html",
        },
    )
    top_story = base_story.model_copy(
        deep=True,
        update={
            "id": "top-route-2222222222",
            "headline": "Top route",
            "detail_path": "details/top-route-2222222222.html",
        },
    )
    edition.stories = [brand_story, top_story]

    render_row_one_site(edition, tmp_path)

    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    stories = payload["stories"]
    story_directory = payload["story_directory"]

    assert story_directory["story_count"] == 2
    assert story_directory["story_ids"] == ["brand-route-1111111111", "top-route-2222222222"]
    assert story_directory["story_ids"] == [story["id"] for story in stories]
    assert story_directory["routes"] == [
        {
            "story_id": story["id"],
            "detail_href": story["detail_href"],
            "section_key": story["section_key"],
            "section_href": story["section"]["href"],
            "published_date": story["published_date"],
        }
        for story in stories
    ]
    assert story_directory["routes"][0]["section_href"] == "#brand_moves"
    assert story_directory["routes"][0]["published_date"] is None
    assert story_directory["routes"][1]["section_href"] == "#top_stories"
    assert story_directory["routes"][1]["published_date"] == "2026-07-02"


def test_story_directory_route_payload_rejects_non_object_section() -> None:
    with pytest.raises(TypeError, match="story section payload must be an object"):
        _story_directory_route_payload(
            {
                "id": "bad-section-1111111111",
                "detail_href": "details/bad-section-1111111111.html",
                "section_key": "top_stories",
                "section": "#top_stories",
                "published_date": "2026-07-02",
            }
        )


def test_render_row_one_site_sanitizes_json_source_url(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].source_url = "javascript:alert(1)"

    render_row_one_site(edition, tmp_path)

    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))

    assert payload["contract_version"] == "row-one-app/v7"
    assert payload["stories"][0]["source_url"] is None
    assert payload["stories"][0]["evidence"][1]["url"] is None
    assert payload["stories"][0]["evidence"][1]["href"] is None


def test_row_one_story_rejects_unknown_section_key() -> None:
    with pytest.raises(ValidationError):
        RowOneStory(
            id="bad-section-1234567890",
            section_key="unknown",
            story_type="tracked_entity",
            headline="Bad section",
            summary=LocalizedText(zh="摘要", en="Summary"),
            why_it_matters=LocalizedText(zh="原因", en="Why"),
            editorial_takeaway=LocalizedText(zh="整理", en="Takeaway"),
            signal_context=LocalizedText(zh="背景", en="Context"),
            reader_path=LocalizedText(zh="路径", en="Path"),
            source_name="ROW ONE",
            detail_path="details/bad-section-1234567890.html",
        )
