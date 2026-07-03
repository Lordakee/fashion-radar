from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from html import escape

import pytest
from pydantic import ValidationError

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
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
from fashion_radar.row_one.templates import render_index_html

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
    assert "Briefing Topics" not in detail_html
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


def test_render_row_one_site_includes_lead_story_block(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="lead-story"' in index_html
    assert "Lead Story" in index_html
    assert "今日头条" in index_html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in index_html
    assert "The Row is today&#x27;s priority signal." in index_html


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
        r'<section class="briefing-topics" aria-label="Briefing topics">'
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
    assert index_html.index('class="edition-nav"') < index_html.index('class="lead-story"')
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
        r'<section class="briefing-path" aria-label="Briefing path">'
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
    assert index_html.index('class="briefing-path"') < index_html.index('class="section-block"')


def test_render_row_one_site_omits_briefing_path_when_digest_blocks_are_empty(tmp_path) -> None:
    edition = _edition()
    edition.stories = []

    render_row_one_site(edition, tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="briefing-path"' not in index_html
    assert "Briefing Path" not in index_html


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
        r'<section class="briefing-path" aria-label="Briefing path">'
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
        '<meta name="description" content="Original source summary: The Row signal '
        'with &lt;angle&gt; detail.">'
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

    assert payload["contract_version"] == "row-one-app/v4"
    assert payload["brand"] == "ROW ONE"
    assert payload["generated_at"] == "2026-07-02T04:00:00Z"
    assert payload["edition_date"] == "2026-07-02T04:00:00Z"
    assert payload["summary"]["zh"] == "ROW ONE 今日整理了 1 条本地时尚信号。"
    assert payload["story_count"] == 1
    assert payload["evidence_count"] == 1

    sections = {section["key"]: section for section in payload["sections"]}
    assert sections["top_stories"]["href"] == "#top_stories"
    assert sections["top_stories"]["story_count"] == 1
    assert sections["brand_moves"]["href"] == "#brand_moves"
    assert sections["brand_moves"]["story_count"] == 0

    story = payload["stories"][0]
    assert story["id"] == "the-row-signal-1234567890"
    assert story["section_key"] == "top_stories"
    assert story["section"] == {
        "key": "top_stories",
        "title": {"zh": "今日重点", "en": "Top Stories"},
        "href": "#top_stories",
    }
    assert story["headline"] == 'The Row <signals> "quiet" demand'
    assert story["summary"]["zh"].startswith("来源摘要")
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

    assert payload["contract_version"] == "row-one-app/v4"
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
