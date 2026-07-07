from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import UTC, datetime
from html import escape

import pytest
from pydantic import ValidationError

import fashion_radar.row_one.render as row_one_render
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
from fashion_radar.row_one.templates import (
    EDITORIAL_BRIEF_BODY_EXCERPT_CHARS,
    _EditorialBrief,
    _EditorialBriefItem,
    _safe_daily_local_intelligence_href,
    _strict_valid_local_article_paragraph_indices,
    render_detail_html,
    render_index_html,
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
    assert "Vogue &lt;Business&gt;" in html
    assert "The Row &lt;source&gt;" in html
    assert "&lt;The Row&gt;" in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-reader"' in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-digest"' in html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-evidence"' in html
    )
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert "<source>" not in html
    assert "<Business>" not in html
    assert "<The Row>" not in html

    assert 'href="articles/index.html"' in home_html
    assert 'class="saved-article-library-entry"' in home_html
    assert "Daily Saved Article Library" in home_html
    assert "每日本地文章库" in home_html
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
        assert "saved_article_library" not in contract_json
        assert "daily_saved_article_library" not in contract_json
        assert "article_library" not in contract_json
        assert "saved-article-library" not in contract_json
        assert "Daily Saved Article Library" not in contract_json
    assert not (tmp_path / "data" / "saved-article-library.json").exists()


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
    next_section = re.search(
        r"\n<section class=",
        index_html[section_start + len(marker) :],
    )
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
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
