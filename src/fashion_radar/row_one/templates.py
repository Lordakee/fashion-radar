from __future__ import annotations

import re
from html import escape
from pathlib import PurePosixPath

from fashion_radar.row_one.display import display_for_story, safe_story_image_src
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
from fashion_radar.row_one.readiness import RowOneReadiness, build_row_one_readiness
from fashion_radar.row_one.utils import safe_external_url

_DETAIL_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html$")


def render_index_html(
    edition: RowOneEdition,
    *,
    app_payload: dict[str, object] | None = None,
) -> str:
    contents_nav = _render_edition_nav(edition)
    briefing_topics = _render_briefing_topics(app_payload)
    readiness = build_row_one_readiness(edition)
    status_strip = _render_edition_status(edition, readiness)
    summary_note_en = (
        f"{readiness.story_count} stories · {readiness.safe_evidence_count} evidence links"
    )
    summary_note_zh = f"{readiness.story_count} 条故事 · {readiness.safe_evidence_count} 条证据链接"
    lead_story = _lead_story(edition)
    lead_story_block = (
        _render_lead_story(lead_story, _section_title(edition, lead_story.section_key))
        if lead_story
        else ""
    )
    story_cards = "\n".join(_render_section(edition, section.key) for section in edition.sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=f"{edition.brand} — {edition.edition_date.date().isoformat()}",
            description=edition.summary.en,
            page_type="website",
        )
    }
<title>{_esc(edition.brand)} — {_esc(edition.edition_date.date().isoformat())}</title>
<link rel="stylesheet" href="assets/row-one.css">
</head>
<body>
<div class="site-shell">
<header class="site-header">
  <div class="site-header-inner">
    <div class="site-title-block">
      <div class="edition-kicker">Daily Fashion Intelligence</div>
      <h1>{_esc(edition.brand)}</h1>
      <p class="edition-date">{_esc(edition.edition_date.strftime("%B %d, %Y"))}</p>
      <p class="site-dek">
        <span data-lang="en">Local signals, edited for fashion context.</span>
        <span data-lang="zh">本地信号，以时尚语境整理。</span>
      </p>
      <div class="language-toggle" aria-label="Language">
        <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
        <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
      </div>
      <p class="edition-summary">
        <span data-lang="en">{_esc(edition.summary.en)}</span>
        <span data-lang="zh">{_esc(edition.summary.zh)}</span>
      </p>
    </div>
    <aside class="edition-summary-panel" aria-label="Edition summary">
      <p class="summary-kicker">
        <span data-lang="en">Edition</span>
        <span data-lang="zh">每日版本</span>
      </p>
      <p class="summary-date">{_esc(edition.edition_date.date().isoformat())}</p>
      <p class="summary-status">
        <span data-lang="en">{_esc(readiness.readiness.en)}</span>
        <span data-lang="zh">{_esc(readiness.readiness.zh)}</span>
      </p>
      <p class="summary-note">
        <span data-lang="en">{_esc(summary_note_en)}</span>
        <span data-lang="zh">{_esc(summary_note_zh)}</span>
      </p>
    </aside>
  </div>
</header>
{status_strip}
<main class="site-main" id="main-content">
{contents_nav}
{lead_story_block}
{briefing_topics}
{story_cards}
</main>
</div>
<script src="assets/row-one.js"></script>
</body>
</html>
"""


def render_detail_html(edition: RowOneEdition, story: RowOneStory) -> str:
    section_title = _section_title(edition, story.section_key)
    evidence = "\n".join(_render_evidence(link) for link in story.evidence)
    source_link = _external_link(story.source_url, story.source_name, css_class="source-link")
    visual = _render_story_visual(story, section_title, context="detail-visual")
    article_contents = _render_article_contents()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=story.headline,
            description=story.summary.en,
            page_type="article",
        )
    }
<title>{_esc(story.headline)} — {_esc(edition.brand)}</title>
<link rel="stylesheet" href="../assets/row-one.css">
</head>
<body>
<header class="detail-header">
  <a class="back-link" href="../index.html">ROW ONE</a>
  <div class="language-toggle" aria-label="Language">
    <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
    <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
  </div>
</header>
<main class="detail-main">
  <article class="detail-article">
    <p class="story-section">
      <span data-lang="en">{_esc(section_title.en)}</span>
      <span data-lang="zh">{_esc(section_title.zh)}</span>
    </p>
    <p class="section-return">
      <a href="../index.html#{_esc(story.section_key)}">
        <span data-lang="en">Back to section</span>
        <span data-lang="zh">回到栏目</span>
      </a>
    </p>
    <h1>{_esc(story.headline)}</h1>
    {visual}
    <p class="story-source">{source_link}</p>
    {article_contents}
    <section id="summary">
      <h2>
        <span data-lang="en">Summary</span>
        <span data-lang="zh">摘要</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.summary.en)}</span>
        <span data-lang="zh">{_esc(story.summary.zh)}</span>
      </p>
    </section>
    <section id="why-it-matters">
      <h2>
        <span data-lang="en">Why It Matters</span>
        <span data-lang="zh">为什么重要</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.why_it_matters.en)}</span>
        <span data-lang="zh">{_esc(story.why_it_matters.zh)}</span>
      </p>
    </section>
    <section class="detail-panel">
      <h2 id="editorial-takeaway">
        <span data-lang="en">Editorial Takeaway</span>
        <span data-lang="zh">编辑整理</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
        <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
      </p>
      <h2 id="signal-context">
        <span data-lang="en">Signal Context</span>
        <span data-lang="zh">信号背景</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.signal_context.en)}</span>
        <span data-lang="zh">{_esc(story.signal_context.zh)}</span>
      </p>
      <h2 id="reader-path">
        <span data-lang="en">Reader Path</span>
        <span data-lang="zh">阅读路径</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.reader_path.en)}</span>
        <span data-lang="zh">{_esc(story.reader_path.zh)}</span>
      </p>
    </section>
    <section id="evidence-trail">
      <h2>
        <span data-lang="en">Evidence Trail</span>
        <span data-lang="zh">来源线索</span>
      </h2>
      <div class="evidence-trail">{evidence}</div>
    </section>
  </article>
</main>
<script src="../assets/row-one.js"></script>
</body>
</html>
"""


def row_one_css() -> str:
    return """@font-face { font-family: RowOneSerif; src: local("Georgia"); }
:root {
  --paper: #f4f6f8;
  --ink: #101216;
  --muted: #626a73;
  --line: #d6dce3;
  --panel: #ffffff;
  --accent: #2454ff;
  --steel: #e8edf3;
  --chrome: #c8d0da;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}
.site-shell {
  min-height: 100vh;
}
.site-header {
  min-height: 52vh;
  padding: 44px min(7vw, 88px) 32px;
  border-bottom: 1px solid var(--ink);
  display: grid;
  align-content: space-between;
}
.site-header-inner {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.42fr);
  gap: 32px;
  align-items: end;
}
.site-title-block {
  display: grid;
  gap: 14px;
}
.site-dek {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.4vw, 2.6rem);
  line-height: 1.05;
  margin: 0;
  max-width: 820px;
}
.edition-summary-panel {
  align-self: end;
  border: 1px solid var(--ink);
  background: rgba(255, 255, 255, 0.54);
  padding: 20px;
}
.summary-kicker,
.summary-date,
.summary-status,
.summary-note {
  margin: 0;
}
.summary-kicker {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.summary-date {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: 2rem;
  line-height: 1;
  margin-top: 12px;
}
.summary-status {
  color: var(--ink);
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 14px;
  text-transform: uppercase;
}
.summary-note {
  color: var(--muted);
  font-size: 0.86rem;
  margin-top: 8px;
}
.edition-kicker, .story-section {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
h1 {
  margin: 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(4.5rem, 16vw, 13rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.86;
}
.edition-date, .edition-summary {
  max-width: 780px;
  color: var(--muted);
  font-size: 1rem;
}
.language-toggle {
  display: inline-flex;
  width: fit-content;
  border: 1px solid var(--ink);
}
.language-toggle button {
  border: 0;
  border-right: 1px solid var(--ink);
  background: transparent;
  color: var(--ink);
  padding: 8px 13px;
  cursor: pointer;
  font: inherit;
}
.language-toggle button:last-child { border-right: 0; }
.language-toggle button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
main, .site-main { padding: 36px min(7vw, 88px) 72px; }
.edition-status {
  display: grid;
  grid-template-columns: minmax(150px, 1.2fr) repeat(5, minmax(120px, 1fr));
  gap: 0;
  border-bottom: 1px solid var(--ink);
  background: var(--paper);
}
.edition-status > div {
  border-right: 1px solid var(--line);
  padding: 18px min(2vw, 24px);
}
.edition-status > div:last-child { border-right: 0; }
.edition-status strong {
  color: var(--ink);
  display: block;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.05rem, 1.8vw, 1.8rem);
  font-weight: 500;
  line-height: 1.05;
  margin-top: 6px;
}
.edition-status-label {
  color: var(--muted);
  display: block;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.edition-nav {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  padding: 24px 0;
  margin-bottom: 32px;
}
.edition-rail {
  margin-top: 18px;
}
.edition-rail-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.edition-nav-item,
.edition-rail-item {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  min-height: 150px;
  padding: 16px;
  text-decoration: none;
}
.edition-rail-item {
  background: var(--paper);
  border: 0;
  grid-template-columns: 36px minmax(0, 1fr);
  min-height: 168px;
}
.rail-item-index {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
}
.rail-item-copy {
  display: grid;
  gap: 8px;
}
.rail-item-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.25rem;
  line-height: 1;
}
.rail-item-count {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.edition-nav-title {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.25rem;
  line-height: 1;
}
.edition-nav-count {
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.edition-nav-dek {
  color: var(--muted);
  font-size: 0.86rem;
  line-height: 1.35;
}
.briefing-topics {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.briefing-topics-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.briefing-topics-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.briefing-topics-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.briefing-topic-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.briefing-topic-card {
  background: var(--panel);
  color: var(--ink);
  display: grid;
  gap: 14px;
  min-height: 230px;
  padding: 18px;
  text-decoration: none;
}
.briefing-topic-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.5rem, 2.6vw, 2.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
}
.briefing-topic-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.briefing-topic-label,
.briefing-topic-count {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.briefing-topic-meta {
  align-self: end;
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  padding-top: 12px;
}
.briefing-topic-empty {
  border: 1px solid var(--line);
  color: var(--muted);
  margin: 0;
  padding: 18px;
}
.lead-story {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 32px 0;
}
.lead-story-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr);
  gap: 32px;
  align-items: end;
}
.lead-story h2 {
  margin: 10px 0 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(3rem, 8vw, 7.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.9;
}
.lead-story h2 a, .lead-story-link {
  color: var(--ink);
  text-decoration: none;
}
.lead-story-link {
  border-bottom: 1px solid var(--accent);
  color: var(--accent);
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-top: 12px;
  padding-bottom: 4px;
  text-transform: uppercase;
}
.story-visual {
  border: 1px solid var(--ink);
  background: var(--panel);
  display: grid;
  margin: 0;
  min-height: 220px;
  overflow: hidden;
  position: relative;
}
.story-visual img {
  display: block;
  height: 100%;
  object-fit: cover;
  width: 100%;
}
.story-visual-fallback {
  align-content: space-between;
  background:
    linear-gradient(90deg, rgba(16, 18, 22, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(16, 18, 22, 0.08) 1px, transparent 1px),
    var(--steel);
  background-size: 28px 28px;
  color: var(--ink);
  display: grid;
  min-height: inherit;
  padding: 16px;
}
.story-visual-mark {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 7vw, 6rem);
  line-height: 0.88;
  max-width: 8ch;
}
.story-visual-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.story-visual--editorial { background: var(--panel); }
.story-visual--portrait { background: var(--chrome); }
.story-visual--product { background: var(--steel); }
.story-visual--signal { background: var(--paper); }
.story-visual--ink { border-color: var(--ink); }
.story-visual--graphite { border-color: var(--muted); }
.story-visual--steel { border-color: var(--chrome); }
.story-visual--cobalt { border-color: var(--accent); }
.story-visual--rose { border-color: var(--muted); }
.lead-story-visual { min-height: clamp(280px, 36vw, 520px); }
.story-card-visual {
  margin-bottom: 16px;
  min-height: 180px;
}
.detail-visual {
  margin: 24px 0 30px;
  min-height: clamp(260px, 45vw, 520px);
}
.section-block {
  display: grid;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  gap: 32px;
  border-top: 1px solid var(--line);
  padding: 32px 0;
}
.section-heading h2 {
  margin: 0 0 10px;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4vw, 4.4rem);
  font-weight: 500;
  letter-spacing: 0;
}
.section-heading p { color: var(--muted); margin: 0; }
.story-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}
.story-card {
  min-height: 230px;
  border: 1px solid var(--line);
  background: var(--panel);
  padding: 20px;
  display: grid;
  align-content: space-between;
}
.story-card-header,
.story-card-body,
.story-card-footer {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}
.story-card-header {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.11em;
  margin-bottom: 14px;
  text-transform: uppercase;
}
.story-card-body {
  display: grid;
}
.story-card-footer {
  align-items: center;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  margin-top: 14px;
  padding-top: 12px;
  text-transform: uppercase;
}
.story-detail-link {
  color: var(--accent);
  font-weight: 700;
}
.story-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0 0;
}
.story-tag-list span {
  border: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-transform: uppercase;
}
.story-card a {
  color: var(--ink);
  text-decoration: none;
}
.story-card h3 {
  margin: 0;
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.35rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.story-takeaway {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.06rem;
  margin: 8px 0;
}
.story-card p, .detail-article p { color: var(--muted); line-height: 1.55; }
.story-orientation {
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  margin: 10px 0 0;
  text-transform: uppercase;
}
.story-meta {
  color: var(--accent);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-header {
  padding: 24px min(7vw, 88px);
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--line);
}
.back-link, .source-link, .evidence-item a {
  color: var(--accent);
  text-decoration: none;
}
.detail-main { max-width: 920px; margin: 0 auto; }
.detail-article h1 { font-size: clamp(3rem, 8vw, 7rem); margin: 18px 0 24px; }
.detail-article h2 {
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin-top: 36px;
}
.article-contents {
  border-bottom: 1px solid var(--line);
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 28px 0;
  padding: 14px 0;
}
.article-contents a {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 8px 10px;
  text-decoration: none;
  text-transform: uppercase;
}
.detail-panel {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  margin: 34px 0;
  padding: 22px 0;
}
.detail-panel h2 { margin-top: 8px; }
.section-return {
  margin: 0 0 22px;
}
.section-return a {
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.evidence-item {
  padding: 14px 0;
  border-top: 1px solid var(--line);
}
.evidence-trail {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}
.evidence-item--safe,
.evidence-item--retained {
  background: var(--panel);
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  padding: 14px;
}
.evidence-item--retained {
  border-left-color: var(--muted);
  color: var(--muted);
}
.evidence-label,
.evidence-retained-label {
  color: var(--accent);
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin-bottom: 6px;
  text-transform: uppercase;
}
.evidence-retained-label {
  color: var(--muted);
}
.evidence-retained-title {
  display: block;
}
[data-lang="zh"] { display: none; }
body.lang-zh [data-lang="en"] { display: none; }
body.lang-zh [data-lang="zh"] { display: inline; }
body.lang-zh p [data-lang="zh"] { display: inline; }
@media (max-width: 760px) {
  .site-header { min-height: 46vh; padding: 28px 20px; }
  .site-header-inner { grid-template-columns: 1fr; }
  .edition-status { grid-template-columns: 1fr; }
  .edition-status > div {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 16px 20px;
  }
  .edition-status > div:last-child { border-bottom: 0; }
  main { padding: 24px 20px 56px; }
  .edition-rail-grid { grid-template-columns: 1fr; }
  .briefing-topics-header { grid-template-columns: 1fr; }
  .briefing-topic-grid { grid-template-columns: 1fr; }
  .lead-story-grid { grid-template-columns: 1fr; gap: 18px; }
  .section-block { grid-template-columns: 1fr; gap: 18px; }
  .story-grid { grid-template-columns: 1fr; }
  .detail-header { padding: 18px 20px; }
}
"""


def _render_edition_nav(edition: RowOneEdition) -> str:
    rows = "\n".join(_render_edition_nav_item(edition, section) for section in edition.sections)
    return f"""<nav class="edition-nav" aria-label="Edition contents">
  <p class="story-section">
    <span data-lang="en">Edition Contents</span>
    <span data-lang="zh">今日目录</span>
  </p>
  <div class="edition-rail">
    <div class="edition-rail-grid">{rows}</div>
  </div>
</nav>"""


def _render_edition_status(
    edition: RowOneEdition,
    readiness: RowOneReadiness | None = None,
) -> str:
    if readiness is None:
        readiness = build_row_one_readiness(edition)
    status_metrics = "\n  ".join(
        (
            _render_status_metric(
                "Generated",
                "生成时间",
                readiness.generated_at,
                readiness.generated_at,
            ),
            _render_status_metric(
                "Edition date",
                "刊期",
                readiness.edition_date,
                readiness.edition_date,
            ),
            _render_status_metric(
                "Stories",
                "故事",
                str(readiness.story_count),
                f"{readiness.story_count} 条",
            ),
            _render_status_metric(
                "Evidence links",
                "证据链接",
                str(readiness.safe_evidence_count),
                f"{readiness.safe_evidence_count} 条",
            ),
            _render_status_metric(
                "Empty sections",
                "空栏目",
                readiness.empty_sections.en,
                readiness.empty_sections.zh,
            ),
        )
    )
    return f"""<section class="edition-status" aria-label="Latest edition status">
  <div>
    <p class="story-section">
      <span data-lang="en">Latest Edition</span>
      <span data-lang="zh">今日状态</span>
    </p>
    <strong>
      <span data-lang="en">{_esc(readiness.readiness.en)}</span>
      <span data-lang="zh">{_esc(readiness.readiness.zh)}</span>
    </strong>
  </div>
  {status_metrics}
</section>"""


def _render_status_metric(label_en: str, label_zh: str, value_en: str, value_zh: str) -> str:
    return f"""<div class="edition-status-metric">
    <span class="edition-status-label">
      <span data-lang="en">{_esc(label_en)}</span>
      <span data-lang="zh">{_esc(label_zh)}</span>
    </span>
    <strong>
      <span data-lang="en">{_esc(value_en)}</span>
      <span data-lang="zh">{_esc(value_zh)}</span>
    </strong>
  </div>"""


def _render_briefing_topics(app_payload: dict[str, object] | None) -> str:
    topics = _app_payload_briefing_topics(app_payload)[:4]
    if not topics:
        return ""
    topic_cards = "\n".join(_render_briefing_topic_card(topic) for topic in topics)
    return f"""<section class="briefing-topics" aria-label="Briefing topics">
  <div class="briefing-topics-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Briefing Topics</span>
        <span data-lang="zh">今日主题</span>
      </p>
      <h2>
        <span data-lang="en">Organized Signals</span>
        <span data-lang="zh">整理后的时尚信号</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Organized from explicit ROW ONE story references.</span>
      <span data-lang="zh">根据 ROW ONE 故事中的明确引用，整理品牌、单品、设计师与人物线索。</span>
    </p>
  </div>
  <div class="briefing-topic-grid">{topic_cards}</div>
</section>"""


def _render_briefing_topic_card(topic: dict[str, object]) -> str:
    title = _localized_topic_field(topic, "title")
    label = _localized_topic_field(topic, "label")
    topic_type = _esc(str(topic["topic_type"]))
    story_count = int(topic["story_count"])
    evidence_count = int(topic["evidence_count"])
    heat_delta = int(topic["positive_heat_delta_sum"])
    lead_story = _topic_lead_story(topic)
    href = str(lead_story["detail_href"]) if lead_story is not None else "#main-content"
    headline = _topic_localized_card_text(lead_story, "headline") if lead_story else title
    summary = _topic_localized_card_text(lead_story, "editorial_takeaway") if lead_story else title
    story_label_en = "1 story" if story_count == 1 else f"{story_count} stories"
    story_label_zh = f"{story_count} 条故事"
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"+{heat_delta} heat" if heat_delta > 0 else "steady heat"
    heat_label_zh = f"+{heat_delta} 热度" if heat_delta > 0 else "热度平稳"
    return f"""<a class="briefing-topic-card briefing-topic-card--{topic_type}" href="{_esc(href)}">
  <span class="briefing-topic-label">
    <span data-lang="en">{_esc(label.en)}</span>
    <span data-lang="zh">{_esc(label.zh)}</span>
  </span>
  <h3>
    <span data-lang="en">{_esc(title.en)}</span>
    <span data-lang="zh">{_esc(title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(headline.en)}</span>
    <span data-lang="zh">{_esc(headline.zh)}</span>
  </p>
  <p>
    <span data-lang="en">{_esc(summary.en)}</span>
    <span data-lang="zh">{_esc(summary.zh)}</span>
  </p>
  <span class="briefing-topic-meta">
    <span class="briefing-topic-count">
      <span data-lang="en">{_esc(story_label_en)}</span>
      <span data-lang="zh">{_esc(story_label_zh)}</span>
    </span>
    <span class="briefing-topic-count">
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
    </span>
    <span class="briefing-topic-count">
      <span data-lang="en">{_esc(heat_label_en)}</span>
      <span data-lang="zh">{_esc(heat_label_zh)}</span>
    </span>
  </span>
</a>"""


def _app_payload_briefing_topics(
    app_payload: dict[str, object] | None,
) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    daily_digest = app_payload.get("daily_digest")
    if not isinstance(daily_digest, dict):
        return []
    topics = daily_digest.get("briefing_topics")
    if not isinstance(topics, list):
        return []
    return [topic for topic in topics if isinstance(topic, dict)]


def _localized_topic_field(topic: dict[str, object], field: str) -> LocalizedText:
    value = topic[field]
    if isinstance(value, dict):
        return LocalizedText(zh=str(value["zh"]), en=str(value["en"]))
    text = str(value)
    return LocalizedText(zh=text, en=text)


def _topic_lead_story(topic: dict[str, object]) -> dict[str, object] | None:
    cards = topic.get("cards")
    if not isinstance(cards, list) or not cards:
        return None
    first = cards[0]
    return first if isinstance(first, dict) else None


def _topic_localized_card_text(
    card: dict[str, object] | None,
    field: str,
) -> LocalizedText:
    if card is None:
        return LocalizedText(zh="", en="")
    value = card.get(field)
    if isinstance(value, dict):
        return LocalizedText(zh=str(value["zh"]), en=str(value["en"]))
    text = str(value) if value is not None else ""
    return LocalizedText(zh=text, en=text)


def _render_edition_nav_item(
    edition: RowOneEdition,
    section: RowOneSection,
) -> str:
    story_count = len(edition.section_stories(section.key))
    count_en = "1 story" if story_count == 1 else f"{story_count} stories"
    count_zh = f"{story_count} 条"
    index = next(
        (
            position
            for position, candidate in enumerate(edition.sections, start=1)
            if candidate.key == section.key
        ),
        1,
    )
    return f"""<a class="edition-nav-item edition-rail-item" href="#{_esc(section.key)}">
  <span class="rail-item-index">{index:02d}</span>
  <span class="rail-item-copy">
    <span class="edition-nav-title rail-item-title">
      <span data-lang="en">{_esc(section.title.en)}</span>
      <span data-lang="zh">{_esc(section.title.zh)}</span>
    </span>
    <span class="edition-nav-count rail-item-count">
      <span data-lang="en">{_esc(count_en)}</span>
      <span data-lang="zh">{_esc(count_zh)}</span>
    </span>
    <span class="edition-nav-dek">
      <span data-lang="en">{_esc(section.dek.en)}</span>
      <span data-lang="zh">{_esc(section.dek.zh)}</span>
    </span>
  </span>
</a>"""


def _render_article_contents() -> str:
    return """<nav class="article-contents" aria-label="Article contents">
  <a href="#summary">
    <span data-lang="en">Summary</span>
    <span data-lang="zh">摘要</span>
  </a>
  <a href="#why-it-matters">
    <span data-lang="en">Why It Matters</span>
    <span data-lang="zh">为什么重要</span>
  </a>
  <a href="#editorial-takeaway">
    <span data-lang="en">Editorial Takeaway</span>
    <span data-lang="zh">编辑判断</span>
  </a>
  <a href="#signal-context">
    <span data-lang="en">Signal Context</span>
    <span data-lang="zh">信号背景</span>
  </a>
  <a href="#reader-path">
    <span data-lang="en">Reader Path</span>
    <span data-lang="zh">阅读路径</span>
  </a>
  <a href="#evidence-trail">
    <span data-lang="en">Evidence Trail</span>
    <span data-lang="zh">证据链</span>
  </a>
</nav>"""


def row_one_js() -> str:
    return """(() => {
  const buttons = Array.from(document.querySelectorAll("[data-lang-toggle]"));
  const localizedImages = Array.from(document.querySelectorAll("img[data-alt-en]"));
  const storageKey = "row-one:language";
  const getStoredLang = () => {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored === "zh" || stored === "en" ? stored : null;
    } catch {
      return null;
    }
  };
  const persistLang = (lang) => {
    try {
      window.localStorage.setItem(storageKey, lang);
    } catch {
      // Ignore unavailable storage; language toggles still work for this page view.
    }
  };
  const setLang = (lang, options = {}) => {
    document.body.classList.toggle("lang-zh", lang === "zh");
    document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
    localizedImages.forEach((image) => {
      if (lang === "zh") {
        image.setAttribute("alt", image.dataset.altZh || image.dataset.altEn || "");
      } else {
        image.setAttribute("alt", image.dataset.altEn || "");
      }
    });
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.langToggle === lang ? "true" : "false");
    });
    if (options.persist !== false) {
      persistLang(lang);
    }
  };
  buttons.forEach((button) => {
    button.addEventListener("click", () => setLang(button.dataset.langToggle || "en"));
  });
  const initialLang = getStoredLang() || "en";
  setLang(initialLang, { persist: false });
})();
"""


def _meta_description(text: str, *, limit: int = 180) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _render_meta_tags(*, title: str, description: str, page_type: str) -> str:
    safe_title = _esc(title)
    safe_description = _esc(_meta_description(description))
    safe_type = _esc(page_type)
    return f"""<meta name="description" content="{safe_description}">
<meta property="og:title" content="{safe_title}">
<meta property="og:description" content="{safe_description}">
<meta property="og:type" content="{safe_type}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{safe_title}">
<meta name="twitter:description" content="{safe_description}">"""


def _lead_story(edition: RowOneEdition) -> RowOneStory | None:
    top_stories = edition.section_stories("top_stories")
    if top_stories:
        return top_stories[0]
    return edition.stories[0] if edition.stories else None


def _render_lead_story(story: RowOneStory, section_title: LocalizedText) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    visual = _render_story_visual(story, section_title, context="lead-story-visual")
    return f"""<section class="lead-story" aria-label="Lead story">
  <p class="story-section">
    <span data-lang="en">Lead Story</span>
    <span data-lang="zh">今日头条</span>
  </p>
  <div class="lead-story-grid">
    {visual}
    <div>
      <h2><a href="{detail_href}">{_esc(story.headline)}</a></h2>
      {_render_story_orientation(story, section_title)}
    </div>
    <div>
      <p class="story-takeaway">
        <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
        <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
      </p>
      <p>
        <span data-lang="en">{_esc(story.summary.en)}</span>
        <span data-lang="zh">{_esc(story.summary.zh)}</span>
      </p>
      <a class="lead-story-link" href="{detail_href}">
        <span data-lang="en">Read the brief</span>
        <span data-lang="zh">查看详情</span>
      </a>
    </div>
  </div>
</section>"""


def _render_section(edition: RowOneEdition, section_key: RowOneSectionKey) -> str:
    section = next(section for section in edition.sections if section.key == section_key)
    stories = edition.section_stories(section_key)
    cards = "\n".join(_render_story_card(story, section.title) for story in stories)
    if not cards:
        cards = (
            '<p class="empty-state">'
            '<span data-lang="en">No stories in this section yet.</span>'
            '<span data-lang="zh">这个栏目暂无故事。</span>'
            "</p>"
        )
    return f"""<section class="section-block" id="{_esc(section.key)}">
  <div class="section-heading">
    <h2>
      <span data-lang="en">{_esc(section.title.en)}</span>
      <span data-lang="zh">{_esc(section.title.zh)}</span>
    </h2>
    <p>
      <span data-lang="en">{_esc(section.dek.en)}</span>
      <span data-lang="zh">{_esc(section.dek.zh)}</span>
    </p>
  </div>
  <div class="story-grid">{cards}</div>
</section>"""


def _render_story_card(
    story: RowOneStory,
    section_title: LocalizedText,
) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    published = _published_label(story)
    evidence_count = sum(1 for link in story.evidence if _safe_external_url(link.url) is not None)
    source_name = _esc(story.source_name)
    evidence_label_en = "1 source" if evidence_count == 1 else f"{evidence_count} sources"
    evidence_label_zh = f"{evidence_count} 条来源"
    tags = "".join(f"<span>{_esc(tag)}</span>" for tag in story.tags)
    tags_block = f'\n  <p class="story-tag-list">{tags}</p>' if tags else ""
    return f"""<article class="story-card">
  {_render_story_visual(story, section_title, context="story-card-visual")}
  <div class="story-card-header">
    <span class="story-source">{source_name}</span>
    <span class="story-date">
      <span data-lang="en">{_esc(published.en)}</span>
      <span data-lang="zh">{_esc(published.zh)}</span>
    </span>
  </div>
  <div class="story-card-body">
    <h3><a href="{detail_href}">{_esc(story.headline)}</a></h3>
    {_render_story_orientation(story, section_title)}
    <p class="story-takeaway">
      <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
      <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
    </p>
    <p>
      <span data-lang="en">{_esc(story.summary.en)}</span>
      <span data-lang="zh">{_esc(story.summary.zh)}</span>
    </p>
  </div>
  <div class="story-card-footer">
    <span class="story-evidence-count">
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
    </span>
    <a class="story-detail-link" href="{detail_href}">
      <span data-lang="en">Read brief</span>
      <span data-lang="zh">阅读简报</span>
    </a>
  </div>{tags_block}
</article>"""


def _render_story_orientation(story: RowOneStory, section_title: LocalizedText) -> str:
    published = _published_label(story)
    evidence_count = sum(1 for link in story.evidence if _safe_external_url(link.url) is not None)
    evidence_en = "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    evidence_zh = f"{evidence_count} 条线索"
    en_parts = [
        section_title.en,
        story.source_name,
        published.en,
        evidence_en,
    ]
    en_text = " · ".join(en_parts)
    zh_text = " · ".join(
        (
            section_title.zh,
            story.source_name,
            published.zh,
            evidence_zh,
        )
    )
    return f"""<p class="story-orientation">
    <span data-lang="en">{_esc(en_text)}</span>
    <span data-lang="zh">{_esc(zh_text)}</span>
  </p>"""


def _render_story_visual(
    story: RowOneStory,
    section_title: LocalizedText,
    *,
    context: str,
) -> str:
    display = display_for_story(story)
    class_name = (
        f"story-visual story-visual--{display.variant} story-visual--{display.accent} {context}"
    )
    image = display.image
    image_src = safe_story_image_src(image.src) if image is not None else None
    if image is not None and image_src is not None:
        if context == "detail-visual" and image_src.startswith("assets/"):
            image_src = f"../{image_src}"
        return (
            f'<figure class="{_esc(class_name)}" data-display-variant="{_esc(display.variant)}">'
            f'<img src="{_esc(image_src)}" alt="{_esc(image.alt.en)}" '
            f'data-alt-en="{_esc(image.alt.en)}" data-alt-zh="{_esc(image.alt.zh)}">'
            "</figure>"
        )

    return f"""<figure class="{_esc(class_name)}" data-display-variant="{_esc(display.variant)}">
  <div class="story-visual-fallback">
    <div class="story-visual-mark">{_esc(_story_visual_initials(story))}</div>
    <div class="story-visual-meta">
      <span>{_esc(display.variant)}</span>
      <span data-lang="en">{_esc(section_title.en)}</span>
      <span data-lang="zh">{_esc(section_title.zh)}</span>
    </div>
  </div>
</figure>"""


def _story_visual_initials(story: RowOneStory) -> str:
    words = re.findall(r"[A-Za-z0-9]+", story.headline.upper())
    if not words:
        return "ROW ONE"
    return " ".join(words[:2])


def _published_label(story: RowOneStory) -> LocalizedText:
    if story.published_at is None:
        return LocalizedText(zh="时间未标注", en="Undated")
    return LocalizedText(
        zh=story.published_at.strftime("%Y-%m-%d"),
        en=story.published_at.strftime("%b %d, %Y"),
    )


def _render_evidence(link: RowOneLink) -> str:
    safe_url = _safe_external_url(link.url)
    if safe_url is None:
        return f"""<div class="evidence-item evidence-item--retained">
  <span class="evidence-retained-label">
    <span data-lang="en">Retained source row</span>
    <span data-lang="zh">保留的来源行</span>
  </span>
  <span class="evidence-retained-title">{_esc(link.title)}</span>
  <p class="story-meta">{_esc(link.source_name)}</p>
</div>"""

    rendered = _external_link(link.url, link.title)
    return f"""<div class="evidence-item evidence-item--safe">
  <span class="evidence-label">
    <span data-lang="en">Source</span>
    <span data-lang="zh">来源</span>
  </span>
  {rendered}
  <p class="story-meta">{_esc(link.source_name)}</p>
</div>"""


def _external_link(url: str | None, text: str, *, css_class: str | None = None) -> str:
    css = f' class="{_esc(css_class)}"' if css_class else ""
    safe_url = _safe_external_url(url)
    if safe_url is None:
        return f"<span{css}>{_esc(text)}</span>"
    return f'<a{css} href="{_esc(safe_url)}" target="_blank" rel="noopener">{_esc(text)}</a>'


def _internal_detail_href(path: str) -> str:
    if _validated_detail_relative_path(path) is None:
        return "#"
    return _esc(path)


def _validated_detail_relative_path(path: str) -> PurePosixPath | None:
    pure_path = PurePosixPath(path)
    name = pure_path.name
    if (
        pure_path.is_absolute()
        or len(pure_path.parts) != 2
        or pure_path.parts[0] != "details"
        or pure_path.parts[1] in ("", ".", "..")
        or ".." in pure_path.parts
        or not _DETAIL_FILENAME_RE.fullmatch(name)
    ):
        return None
    return pure_path


def _safe_external_url(url: str | None) -> str | None:
    return safe_external_url(url)


def _section_title(edition: RowOneEdition, section_key: RowOneSectionKey):
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    return type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title())


def _esc(value: object) -> str:
    return escape(str(value), quote=True) if value is not None else ""
