from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from html import escape

import pytest
from pydantic import ValidationError

import fashion_radar.row_one.render as row_one_render
from fashion_radar.row_one.models import (
    LocalizedText,
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
    _story_directory_route_payload,
    clean_row_one_site_children,
    render_row_one_site,
)
from fashion_radar.row_one.templates import (
    _safe_daily_local_intelligence_href,
    render_index_html,
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
    assert "Briefing Topics" not in detail_html
    assert 'class="source-action-link"' in detail_html
    assert '<span data-lang="en">Open Source Article</span>' in detail_html
    assert '<span data-lang="zh">打开原文</span>' in detail_html
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
    assert "First local paragraph about The Row demand." in detail_html
    assert "Second local paragraph with styling context." in detail_html
    assert 'id="local-article-paragraph-1"' in detail_html
    assert 'id="local-article-paragraph-2"' in detail_html
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
    assert detail_html.index('class="local-article-brief"') < detail_html.index(
        'class="local-article-content-sections"'
    )
    assert detail_html.index('class="local-article-content-sections"') < detail_html.index(
        'class="local-article-body"'
    )
    assert '<span data-lang="en">First local paragraph about The Row demand.</span>' in detail_html
    assert '<span data-lang="zh">第一段本地正文，关于 The Row 需求。</span>' in detail_html
    assert detail_html.index('href="#local-article-paragraph-1"') < detail_html.index(
        'id="local-article-paragraph-1"'
    )
    assert detail_html.index('data-lang="en">First local paragraph') < detail_html.index(
        'data-lang="zh">第一段本地正文'
    )
    assert 'href="#local-article"' in detail_html
    assert detail_html.index('href="#summary"') < detail_html.index('href="#local-article"')
    assert detail_html.index('href="#local-article"') < detail_html.index('href="#why-it-matters"')
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
    assert 'href="#local-article"' in detail_html


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

    assert '<p id="local-article-paragraph-1">One source paragraph.</p>' in detail_html
    assert '<p id="local-article-paragraph-2">Second source paragraph.</p>' in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert '<span data-lang="en">Structured English.</span>' in detail_html
    assert '<span data-lang="zh">结构化中文。</span>' in detail_html
    assert '<span data-lang="zh">一段中文。</span>' not in detail_html


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
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-paragraph-3"' in detail_html
    assert detail_html.count('href="#local-article-paragraph-3"') == 2
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
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'id="local-article-paragraph-1"' in detail_html
    assert "<script>Brief</script>" not in detail_html
    assert "<script>" not in detail_html
    assert 'onerror="alert' not in detail_html
    assert "<img" not in detail_html


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
    assert "#local-article-paragraph-" not in "".join(re.findall(r'href="([^"]+)"', html))
    assert "Paragraph 1" in html
    assert "段落 1" in html

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
    stale_detail.parent.mkdir(parents=True)
    stale_asset.parent.mkdir(parents=True)
    stale_data.parent.mkdir(parents=True)
    keep_path.write_text("do not delete", encoding="utf-8")
    stale_detail.write_text("old", encoding="utf-8")
    stale_asset.write_text("old", encoding="utf-8")
    stale_data.write_text("old", encoding="utf-8")
    (tmp_path / "index.html").write_text("old", encoding="utf-8")
    (tmp_path / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert keep_path.read_text(encoding="utf-8") == "do not delete"
    assert not stale_detail.exists()
    assert not stale_asset.exists()
    assert not stale_data.exists()
    assert (tmp_path / "index.html").exists()


def test_render_row_one_site_latest_only_refuses_unmarked_directory_children(tmp_path) -> None:
    stale_asset = tmp_path / "assets" / "keep.css"
    stale_detail = tmp_path / "details" / "manual.html"
    stale_data = tmp_path / "data" / "manual.json"
    stale_asset.parent.mkdir(parents=True)
    stale_detail.parent.mkdir(parents=True)
    stale_data.parent.mkdir(parents=True)
    stale_asset.write_text("keep", encoding="utf-8")
    stale_detail.write_text("keep", encoding="utf-8")
    stale_data.write_text("keep", encoding="utf-8")

    with pytest.raises(ValueError, match="not marked"):
        render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert stale_asset.exists()
    assert stale_detail.exists()
    assert stale_data.exists()


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
