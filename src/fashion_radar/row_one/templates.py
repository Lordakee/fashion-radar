from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import PurePosixPath

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.display import display_for_story, safe_story_image_src
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneDailyLocalIntelligenceSegment,
    RowOneDailyLocalIntelligenceSegmentItem,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
from fashion_radar.row_one.readiness import RowOneReadiness, build_row_one_readiness
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
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibraryParagraphLink,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_signal_index import (
    RowOneSavedSignalIndex,
    RowOneSavedSignalIndexEntry,
    RowOneSavedSignalIndexParagraphLink,
    RowOneSavedSignalIndexSupport,
)
from fashion_radar.row_one.text import (
    clean_row_one_sentences,
    clean_row_one_text,
    normalize_row_one_paragraph,
    protect_literal_angle_tokens,
    restore_literal_angle_tokens,
)
from fashion_radar.row_one.utils import safe_external_url

_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")
_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE = re.compile(
    r"local-article-content-section-[1-9][0-9]*$"
)
LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS = 160
LOCAL_ARTICLE_DIGEST_MAX_REFERENCES = 4
LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS = 140
LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS = 2
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_BODY_CHARS = 120
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_EXCERPT_CHARS = 140
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ITEMS = 4
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_REFS = 4
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ROWS = 8
LOCAL_ARTICLE_READER_EXCERPT_CHARS = 120
DETAIL_CONTINUE_READING_EXCERPT_CHARS = 120
DETAIL_CONTINUE_READING_MAX_ITEMS = 3
DETAIL_SIGNAL_BRIEFING_MAX_REFS = 8
DETAIL_SIGNAL_BRIEFING_MAX_CUES = 3
DAILY_EDIT_MAX_CARDS = 4
DAILY_EDIT_MAX_SIGNALS = 3
DAILY_EDIT_MAX_PATH_ITEMS = 3
EDITORIAL_BRIEF_MAX_ITEMS = 3
EDITORIAL_BRIEF_BODY_EXCERPT_CHARS = 220
EDITORIAL_BRIEF_MAX_TRAIL_ITEMS = 3
SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT = 3


@dataclass(frozen=True)
class _EditorialBriefTrailItem:
    label: LocalizedText
    href: str | None = None


@dataclass(frozen=True)
class _EditorialBriefItem:
    title: LocalizedText
    body: LocalizedText
    meta: LocalizedText | None = None
    href: str | None = None
    trail: tuple[_EditorialBriefTrailItem, ...] = ()


@dataclass(frozen=True)
class _EditorialBrief:
    items: tuple[_EditorialBriefItem, ...]


@dataclass(frozen=True)
class _LocalArticleParagraphEvidenceItem:
    section_position: int
    section_title: LocalizedText
    item_label: LocalizedText
    item_body: LocalizedText | None
    references: tuple[RowOneReference, ...]


@dataclass(frozen=True)
class _LocalArticleParagraphEvidenceEntry:
    paragraph_index: int
    excerpt: LocalizedText
    items: tuple[_LocalArticleParagraphEvidenceItem, ...]


def render_index_html(
    edition: RowOneEdition,
    *,
    app_payload: dict[str, object] | None = None,
    local_article_intelligence: Sequence[RowOneDailyLocalIntelligenceSection] | None = None,
    saved_article_coverage: RowOneSavedArticleCoverage | None = None,
    saved_article_library: RowOneSavedArticleLibrary | None = None,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
    saved_article_briefs: RowOneSavedArticleBriefs | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
    editorial_brief: _EditorialBrief | None = None,
    local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None,
) -> str:
    local_articles_by_story_id = local_articles_by_story_id or {}
    contents_nav = _render_edition_nav(edition)
    briefing_topics = _render_briefing_topics(app_payload)
    briefing_path = _render_briefing_path(app_payload)
    edition_brief = _render_edition_brief(
        app_payload,
        has_topics=bool(briefing_topics),
        has_path=bool(briefing_path),
    )
    signal_synthesis = _render_signal_synthesis(app_payload)
    daily_edit = _render_daily_edit(app_payload)
    daily_local_intelligence = _render_daily_local_intelligence(local_article_intelligence)
    saved_article_coverage_section = _render_saved_article_coverage(saved_article_coverage)
    saved_article_library_entry = _render_saved_article_library_entry(
        saved_article_library,
        saved_signal_index=saved_signal_index,
    )
    saved_article_briefs_section = _render_saved_article_briefs(saved_article_briefs)
    saved_article_content_organization_section = _render_saved_article_content_organization(
        saved_article_content_organization
    )
    editorial_brief_section = _render_editorial_brief(editorial_brief)
    readiness = build_row_one_readiness(edition)
    status_strip = _render_edition_status(edition, readiness)
    summary_note_en = (
        f"{readiness.story_count} stories · {readiness.safe_evidence_count} evidence links"
    )
    summary_note_zh = f"{readiness.story_count} 条故事 · {readiness.safe_evidence_count} 条证据链接"
    lead_story = _lead_story(edition)
    lead_story_block = (
        _render_lead_story(
            lead_story,
            _section_title(edition, lead_story.section_key),
            local_article=local_articles_by_story_id.get(lead_story.id),
        )
        if lead_story
        else ""
    )
    story_cards = "\n".join(
        _render_section(
            edition,
            section.key,
            local_articles_by_story_id=local_articles_by_story_id,
        )
        for section in edition.sections
    )
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
{edition_brief}
{signal_synthesis}
{daily_edit}
{daily_local_intelligence}
{saved_article_coverage_section}
{saved_article_library_entry}
{saved_article_briefs_section}
{saved_article_content_organization_section}
{editorial_brief_section}
{lead_story_block}
{briefing_topics}
{briefing_path}
{story_cards}
</main>
</div>
<script src="assets/row-one.js"></script>
</body>
</html>
"""


def render_saved_article_library_html(
    edition: RowOneEdition,
    library: RowOneSavedArticleLibrary,
    *,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
) -> str:
    groups = "\n".join(_render_saved_article_library_source(group) for group in library.groups)
    signal_index = _render_saved_signal_index(saved_signal_index)
    content_organization = _render_saved_article_content_organization(
        saved_article_content_organization,
        href_prefix="../",
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=f"Daily Saved Article Library - {edition.brand}",
            description="A generated ROW ONE index of today's saved local article bodies.",
            page_type="website",
        )
    }
<title>Daily Saved Article Library - {_esc(edition.brand)}</title>
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
<main class="detail-main saved-article-library-page">
  <section class="saved-article-library-hero" aria-label="Daily saved article library">
    <p class="story-section">
      <span data-lang="en">Saved Local Source Set</span>
      <span data-lang="zh">本地保存来源集合</span>
    </p>
    <h1>
      <span data-lang="en">Daily Saved Article Library</span>
      <span data-lang="zh">每日本地文章库</span>
    </h1>
    <p>
      <span data-lang="en">A current-edition index of saved local fashion articles.</span>
      <span data-lang="zh">当前版本的本地保存时尚文章索引，并链接回已整理的本地正文。</span>
    </p>
    {_render_saved_article_library_metrics(library, css_class="saved-article-library-metrics")}
  </section>
  {signal_index}
  {content_organization}
  <div class="saved-article-library-grid">{groups}</div>
</main>
<script src="../assets/row-one.js"></script>
</body>
</html>
"""


def render_detail_html(
    edition: RowOneEdition,
    story: RowOneStory,
    *,
    local_article: RowOneLocalArticle | None = None,
) -> str:
    section_title = _section_title(edition, story.section_key)
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    evidence = "\n".join(_render_evidence(link) for link in story.evidence)
    source_link = _external_link(story.source_url, story.source_name, css_class="source-link")
    source_action = _source_action_link(story.source_url)
    visual = _render_story_visual(story, section_title, context="detail-visual")
    local_article_section = _render_local_article(local_article)
    local_read_path = _render_detail_local_read_path(
        local_article if local_article_section else None
    )
    article_contents = _render_article_contents(include_local_article=bool(local_article_section))
    detail_information_map = _render_detail_information_map(story, section_title)
    detail_signal_briefing = _render_detail_signal_briefing(story, local_article)
    continue_reading = _render_detail_continue_reading(edition, story)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{
        _render_meta_tags(
            title=story.headline,
            description=summary_en,
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
    {local_read_path}
    {source_action}
    {article_contents}
    {detail_information_map}
    {detail_signal_briefing}
    <section id="summary">
      <h2>
        <span data-lang="en">Summary</span>
        <span data-lang="zh">摘要</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(summary_en)}</span>
        <span data-lang="zh">{_esc(summary_zh)}</span>
      </p>
    </section>
    {local_article_section}
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
{continue_reading}
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
.edition-brief {
  border: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  margin: 0 0 32px;
  padding: 22px;
}
.edition-brief-header {
  display: grid;
  gap: 8px;
}
.edition-brief-header h2,
.edition-brief-header p {
  margin: 0;
}
.edition-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.4vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
}
.edition-brief-header > p:not(.story-section):not(.edition-brief-lead) {
  color: var(--muted);
  line-height: 1.45;
  max-width: 760px;
}
.edition-brief-lead {
  color: var(--ink);
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2.4vw, 2.4rem);
  line-height: 1;
}
.edition-brief-metrics {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.edition-brief-metric {
  background: var(--panel);
  display: grid;
  gap: 4px;
  padding: 12px;
}
.edition-brief-metric strong {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.6rem;
  line-height: 1;
}
.edition-brief-metric span,
.edition-brief-links a,
.edition-brief-links span {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.edition-brief-points {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}
.edition-brief-points li {
  line-height: 1.45;
}
.edition-brief-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.edition-brief-links a,
.edition-brief-links span {
  border: 1px solid var(--line);
  padding: 8px 10px;
  text-decoration: none;
}
.signal-synthesis {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.signal-synthesis-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.signal-synthesis-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.signal-synthesis-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.signal-synthesis-boundary {
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px;
  letter-spacing: 0.12em;
  margin: 0 0 18px;
  padding: 8px 10px;
  text-transform: uppercase;
}
.signal-synthesis-grid {
  display: grid;
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.signal-synthesis-group {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 260px;
  padding: 18px;
}
.signal-synthesis-group-title {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
  text-transform: uppercase;
}
.signal-synthesis-card {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  padding-top: 14px;
  text-decoration: none;
}
.signal-synthesis-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.3vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.96;
  margin: 0;
}
.signal-synthesis-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.signal-synthesis-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.7rem;
  font-weight: 700;
  gap: 8px 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.daily-local-intelligence {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-local-intelligence-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-local-intelligence-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.daily-local-intelligence-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-local-intelligence-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.daily-local-intelligence-group {
  background: var(--panel);
  display: grid;
  gap: 14px;
  min-height: 280px;
  padding: 18px;
}
.daily-local-intelligence-group-title {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-intelligence-card {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  padding-top: 14px;
  text-decoration: none;
}
.daily-local-intelligence-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.1rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.daily-local-intelligence-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-local-intelligence-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.7rem;
  font-weight: 700;
  gap: 8px 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.daily-local-intelligence-segments {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  margin-top: 4px;
  padding-top: 10px;
}
.daily-local-intelligence-segment {
  display: grid;
  gap: 6px;
}
.daily-local-intelligence-card .daily-local-intelligence-segment-title,
.daily-local-intelligence-card .daily-local-intelligence-segment-item-label {
  color: var(--ink);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  margin: 0;
  text-transform: uppercase;
}
.daily-local-intelligence-card .daily-local-intelligence-segment-body,
.daily-local-intelligence-card .daily-local-intelligence-segment-item-body,
.daily-local-intelligence-card .daily-local-intelligence-segment-meta {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.38;
  margin: 0;
}
.daily-local-intelligence-segment-items {
  display: grid;
  gap: 7px;
  margin: 0;
}
.daily-local-intelligence-segment-item {
  display: grid;
  gap: 3px;
}
.daily-local-intelligence-segment-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.65rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.daily-local-intelligence-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.85rem;
}
.daily-local-intelligence-action,
.daily-local-intelligence-paragraph-link {
  color: inherit;
  text-decoration: none;
}
.daily-local-intelligence-action {
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 999px;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  padding: 0.35rem 0.7rem;
  text-transform: uppercase;
}
.daily-local-intelligence-paragraph-link {
  border-bottom: 1px solid currentColor;
}
.saved-article-coverage {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-coverage-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-coverage-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-coverage-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-coverage-metrics,
.saved-article-coverage-sources {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0 0 14px;
  padding: 0;
}
.saved-article-coverage-metrics li,
.saved-article-coverage-sources li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-coverage-source-name {
  color: var(--ink);
  font-weight: 700;
}
.saved-article-coverage-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-coverage-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 10px;
  min-height: 190px;
  padding: 14px;
  text-decoration: none;
}
.saved-article-coverage-card strong {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.saved-article-coverage-card span {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.35;
}
.saved-article-library-entry {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-library-entry-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-library-entry-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-library-entry-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-library-entry-metrics,
.saved-article-library-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0 0 14px;
  padding: 0;
}
.saved-article-library-entry-metrics li,
.saved-article-library-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-article-library-entry-link {
  border: 1px solid var(--ink);
  color: var(--ink);
  display: inline-flex;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  padding: 10px 12px;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-library-page {
  display: grid;
  gap: 28px;
}
.saved-article-library-hero {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 14px;
  padding-bottom: 28px;
}
.saved-article-library-hero h1 {
  font-size: clamp(3.2rem, 9vw, 8.5rem);
}
.saved-article-library-hero p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 760px;
}
.saved-article-library-grid {
  display: grid;
  gap: 24px;
}
.saved-article-library-source {
  display: grid;
  gap: 12px;
}
.saved-article-library-source-header {
  border-bottom: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
  padding-bottom: 10px;
}
.saved-article-library-source-header h2,
.saved-article-library-source-header p {
  margin: 0;
}
.saved-article-library-source-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.55rem, 3vw, 3rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-article-library-source-header p {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-library-source-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.saved-article-library-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-height: 260px;
  min-width: 0;
  padding: 16px;
}
.saved-article-library-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.05rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  overflow-wrap: anywhere;
}
.saved-article-library-card-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-article-library-card-counts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-article-library-card-counts li,
.saved-article-library-ref,
.saved-article-library-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-library-actions,
.saved-article-library-refs,
.saved-article-library-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-library-actions a {
  border: 1px solid var(--accent);
  color: var(--accent);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 5px;
  letter-spacing: 0.08em;
  padding: 7px 9px;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-signal-index {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-signal-index-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-signal-index-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-header p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.saved-signal-index-metrics li {
  border: 1px solid var(--line);
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 8px 10px;
}
.saved-signal-index-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.saved-signal-index-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.saved-signal-index-card-header {
  display: grid;
  gap: 8px;
}
.saved-signal-index-card-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 3vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-card-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 800;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}
.saved-signal-index-support {
  display: grid;
  gap: 8px;
}
.saved-signal-index-support-row {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding-top: 10px;
}
.saved-signal-index-support-row strong,
.saved-signal-index-support-meta {
  min-width: 0;
  overflow-wrap: anywhere;
}
.saved-signal-index-support-meta,
.saved-signal-index-actions,
.saved-signal-index-paragraphs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
}
.saved-signal-index-support-meta {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-signal-index-support-excerpt {
  margin: 0;
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}
.saved-signal-index-actions a,
.saved-signal-index-paragraphs a {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  overflow-wrap: anywhere;
  padding: 5px 7px;
  text-decoration: none;
}
.saved-article-briefs {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-briefs-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-briefs-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-briefs-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-briefs-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-brief-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 12px;
  min-height: 260px;
  padding: 16px;
  text-decoration: none;
}
.saved-article-brief-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.25rem, 2vw, 2.05rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.saved-article-brief-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-brief-body {
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.42;
  margin: 0;
}
.saved-article-brief-chip-groups {
  display: grid;
  gap: 10px;
}
.saved-article-brief-chip-group {
  display: grid;
  gap: 6px;
}
.saved-article-brief-chip-heading {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-brief-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-brief-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  padding: 5px 7px;
}
.saved-article-brief-chip span:last-child {
  color: var(--muted);
}
.saved-article-content-organization {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-content-organization-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-content-organization-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-content-organization-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-content-organization-groups {
  display: grid;
  gap: 18px;
}
.saved-article-content-organization-group {
  display: grid;
  gap: 12px;
}
.saved-article-content-organization-group-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: space-between;
}
.saved-article-content-organization-group-header h3,
.saved-article-content-organization-group-header p {
  margin: 0;
}
.saved-article-content-organization-group-header h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.4rem, 2.4vw, 2.6rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
}
.saved-article-content-organization-group-header p {
  color: var(--muted);
  max-width: 520px;
}
.saved-article-content-organization-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-content-organization-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 12px;
  min-height: 285px;
  padding: 16px;
  text-decoration: none;
}
.saved-article-content-organization-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.18rem, 1.8vw, 1.85rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.saved-article-content-organization-meta {
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-content-organization-lead {
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.42;
  margin: 0;
}
.saved-article-content-organization-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.saved-article-content-organization-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  gap: 4px;
  padding: 5px 7px;
}
.saved-article-content-organization-chip span:last-child {
  color: var(--muted);
}
.saved-article-content-organization-card-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-content-organization-evidence {
  display: contents;
}
.saved-article-content-organization-evidence-link {
  border: 1px solid var(--accent);
  color: var(--accent);
  display: inline-flex;
  flex-wrap: wrap;
  font-size: 0.68rem;
  font-weight: 800;
  gap: 5px;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.editorial-brief-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.editorial-brief-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.editorial-brief-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.editorial-brief-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.editorial-brief-card {
  background: var(--panel);
  color: var(--ink);
  display: grid;
  gap: 12px;
  min-height: 275px;
  padding: 18px;
  text-decoration: none;
}
.editorial-brief-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.editorial-brief-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.editorial-brief-meta {
  align-self: end;
  border-top: 1px solid var(--line);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding-top: 12px;
  text-transform: uppercase;
}
.editorial-brief-trail {
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-top: 12px;
}
.editorial-brief-trail-item,
.editorial-brief-trail a {
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 4px;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief-trail a:hover,
.editorial-brief-trail a:focus-visible,
.editorial-brief-link:hover,
.editorial-brief-link:focus-visible {
  opacity: 0.75;
}
.editorial-brief-link {
  align-items: center;
  color: var(--accent);
  display: inline-flex;
  font-size: 0.74rem;
  font-weight: 800;
  gap: 6px;
  letter-spacing: 0.12em;
  text-decoration: none;
  text-transform: uppercase;
}
.editorial-brief-link::after {
  content: "↗";
}
.daily-edit {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.daily-edit-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.daily-edit-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.daily-edit-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.daily-edit-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.daily-edit-card {
  background: var(--panel);
  color: var(--ink);
  display: grid;
  gap: 12px;
  min-height: 245px;
  padding: 18px;
  text-decoration: none;
}
.daily-edit-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.35rem, 2.2vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.daily-edit-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.daily-edit-card-meta {
  align-self: end;
  border-top: 1px solid var(--line);
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 14px;
  letter-spacing: 0.1em;
  padding-top: 12px;
  text-transform: uppercase;
}
.daily-edit-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
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
.briefing-path {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.briefing-path-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.45fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.briefing-path-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.4vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
  margin: 0;
}
.briefing-path-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.briefing-path-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}
.briefing-path-block {
  background: var(--paper);
  display: grid;
  gap: 14px;
  padding: 18px;
}
.briefing-path-block h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.55rem, 2.8vw, 3rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.briefing-path-block > p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.briefing-path-card {
  border-top: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  padding-top: 14px;
  text-decoration: none;
}
.briefing-path-card h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.2rem, 2vw, 2rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 1;
  margin: 0;
}
.briefing-path-card p {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.briefing-path-meta {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
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
.local-read-path {
  align-items: center;
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.74rem;
  gap: 8px 10px;
  letter-spacing: 0.08em;
  margin: 12px 0 0;
  text-transform: uppercase;
}
.local-read-path-badge {
  border: 1px solid var(--accent);
  color: var(--accent);
  font-weight: 700;
  padding: 4px 7px;
}
.local-read-action {
  border-bottom: 1px solid var(--accent);
  color: var(--accent);
  font-weight: 800;
  padding-bottom: 3px;
  text-decoration: none;
}
.detail-local-read-path {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 12px 0;
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
.back-link, .source-link, .source-action-link, .evidence-item a {
  color: var(--accent);
  text-decoration: none;
}
.source-action {
  margin: 10px 0 0;
}
.source-action-link {
  border: 1px solid var(--accent);
  display: inline-flex;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 10px 12px;
  text-transform: uppercase;
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
.local-article {
  border-bottom: 1px solid var(--line);
  border-top: 1px solid var(--line);
  margin: 36px 0;
  padding: 28px 0;
}
.local-article-source {
  color: var(--muted);
  font-size: 0.84rem;
  margin: 0 0 18px;
}
.local-article-provenance {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 18px;
}
.local-article-provenance-item {
  border: 1px solid var(--line);
  border-radius: 4px;
  color: var(--muted);
  display: inline-flex;
  font-size: 0.76rem;
  gap: 6px;
  padding: 6px 8px;
  text-decoration: none;
}
.local-article-provenance-link { color: var(--accent); font-weight: 700; }
.local-article-provenance-value { color: var(--ink); }
.local-article h3 {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0 0 18px;
}
.local-article-map {
  border: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 22px;
  padding: 12px;
}
.local-article-map a,
.local-article-content-paragraph-links a {
  border: 1px solid var(--line);
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-content-paragraph-links a {
  display: inline-block;
  margin: 0 4px 4px 0;
}
.local-article-paragraph-evidence {
  border: 1px solid var(--line);
  border-radius: 4px;
  margin: 14px 0 16px;
  padding: 14px;
}
.local-article-paragraph-evidence-header {
  display: grid;
  gap: 6px;
  margin: 0 0 12px;
}
.local-article-paragraph-evidence-header h4,
.local-article-paragraph-evidence-header p {
  margin: 0;
}
.local-article-paragraph-evidence-header h4 {
  font-size: 0.9rem;
}
.local-article-paragraph-evidence-header p {
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-paragraph-evidence-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.local-article-paragraph-evidence-row {
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  padding-top: 10px;
}
.local-article-paragraph-evidence-link {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}
.local-article-paragraph-evidence-excerpt {
  line-height: 1.45;
  margin: 0;
}
.local-article-paragraph-evidence-supports {
  display: grid;
  gap: 8px;
}
.local-article-paragraph-evidence-support {
  border-left: 2px solid var(--line);
  display: grid;
  gap: 5px;
  padding-left: 10px;
}
.local-article-paragraph-evidence-support a {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  text-decoration: none;
}
.local-article-paragraph-evidence-support strong {
  font-size: 0.82rem;
}
.local-article-paragraph-evidence-support p {
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.4;
  margin: 0;
}
.local-article-paragraph-evidence-ref {
  border: 1px solid var(--line);
  color: var(--muted);
  display: inline-block;
  font-size: 0.7rem;
  margin: 0 4px 4px 0;
  padding: 4px 6px;
}
.local-article-reader {
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 14px;
  margin: 14px 0 16px;
}
.local-article-reader h4 {
  margin: 0 0 6px;
  font-size: 0.9rem;
}
.local-article-reader-meta {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-reader-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.local-article-reader-list a {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  color: inherit;
  text-decoration: none;
}
.local-article-reader-list a:hover {
  color: var(--accent);
}
.local-article-reader-number {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0;
  text-transform: uppercase;
}
.local-article-reader-excerpt {
  min-width: 0;
}
.local-article-digest {
  border: 1px solid var(--line);
  border-radius: 4px;
  margin: 14px 0 16px;
  padding: 14px;
}
.local-article-digest-header {
  display: grid;
  gap: 6px;
  margin: 0 0 12px;
}
.local-article-digest-header h4,
.local-article-digest-header p {
  margin: 0;
}
.local-article-digest-header h4 {
  font-size: 0.9rem;
}
.local-article-digest-header p {
  color: var(--muted);
  font-size: 0.82rem;
}
.local-article-digest-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.local-article-digest-card {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.local-article-digest-card h4 {
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-digest-card p {
  line-height: 1.45;
  margin: 0 0 8px;
}
.local-article-digest-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-digest-link-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-digest-chip,
.local-article-digest-link-list a {
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 6px 8px;
  text-decoration: none;
}
.local-article-brief {
  border: 1px solid var(--line);
  display: grid;
  gap: 0;
  margin: 0 0 22px;
}
.local-article-brief-card {
  border-bottom: 1px solid var(--line);
  padding: 16px 18px;
}
.local-article-brief-card:last-child { border-bottom: 0; }
.local-article-brief-card h4 {
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-brief-card p {
  color: var(--ink);
  line-height: 1.55;
  margin: 0;
}
.local-article-content-sections {
  display: grid;
  gap: 14px;
  margin: 0 0 24px;
}
.local-article-content-card {
  border-left: 2px solid var(--ink);
  padding: 0 0 0 16px;
}
.local-article-content-card h4 {
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-content-card p {
  color: var(--ink);
  line-height: 1.55;
  margin: 0 0 10px;
}
.local-article-content-items {
  display: grid;
  gap: 10px;
  list-style: none;
  margin: 0;
  padding: 0;
}
.local-article-content-items li {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
.local-article-content-items strong {
  display: block;
  font-size: 0.82rem;
  margin-bottom: 4px;
}
.local-article-content-previews {
  display: grid;
  gap: 8px;
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
}
.local-article-content-preview a {
  border: 1px solid var(--line);
  color: inherit;
  display: grid;
  gap: 4px;
  padding: 10px;
  text-decoration: none;
}
.local-article-content-preview a > span:first-child,
.local-article-content-preview a > span:nth-child(2) {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.local-article-content-preview a > span:last-child {
  line-height: 1.45;
}
.local-article-content-meta {
  color: var(--muted);
  font-size: 0.78rem;
  margin: 4px 0 0;
}
.local-article-body {
  display: grid;
  gap: 16px;
}
.local-article-body p {
  font-size: 1.05rem;
  line-height: 1.75;
  margin: 0;
}
.local-article-body p:target {
  background: var(--panel);
  outline: 1px solid var(--accent);
  outline-offset: 4px;
}
.detail-information-map {
  background: var(--panel);
  border: 1px solid var(--ink);
  margin: 28px 0;
  padding: 20px;
}
.detail-information-map-header {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}
.detail-information-map-header p,
.detail-information-map-header h2 {
  margin: 0;
}
.detail-information-map-header p {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0;
  text-transform: uppercase;
}
.detail-information-map-header h2 {
  color: var(--ink);
  font-size: 1.2rem;
  letter-spacing: 0;
  margin-top: 0;
  text-transform: none;
}
.detail-information-map-grid {
  background: var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
.detail-information-map-card {
  background: var(--panel);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 14px;
}
.detail-information-map-card h3,
.detail-information-map-card p {
  margin: 0;
  min-width: 0;
}
.detail-information-map-card h3 {
  color: var(--ink);
  font-size: 0.82rem;
  letter-spacing: 0;
  text-transform: uppercase;
}
.detail-information-map-card p {
  color: var(--muted);
  font-size: 0.9rem;
  overflow-wrap: anywhere;
}
.detail-information-map-card a {
  color: var(--accent);
  text-decoration: none;
}
.detail-signal-briefing {
  background: var(--ink);
  color: var(--panel);
  margin: 28px 0;
  padding: 22px;
}
.detail-signal-briefing-header {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}
.detail-signal-briefing-header p,
.detail-signal-briefing-header h2 {
  margin: 0;
}
.detail-signal-briefing-header p {
  color: var(--chrome);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.detail-signal-briefing-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.8rem, 3.4vw, 3.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  text-transform: none;
}
.detail-signal-briefing-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.detail-signal-briefing-card {
  background: #15181d;
  border: 1px solid rgba(244, 246, 248, 0.18);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 16px;
}
.detail-signal-briefing-card h3,
.detail-signal-briefing-card p {
  margin: 0;
}
.detail-signal-briefing-card h3 {
  color: var(--panel);
  font-size: 0.78rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.detail-signal-briefing-card p {
  color: var(--steel);
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.detail-signal-briefing-meta {
  color: var(--chrome);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-signal-briefing-ref {
  border: 1px solid rgba(244, 246, 248, 0.26);
  color: var(--panel);
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  margin: 0 6px 6px 0;
  padding: 6px 8px;
}
.detail-signal-briefing-cues {
  border-top: 1px solid rgba(244, 246, 248, 0.22);
  margin-top: 18px;
  padding-top: 18px;
}
.detail-signal-briefing-cues h3 {
  color: var(--panel);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  margin: 0 0 12px;
  text-transform: uppercase;
}
.detail-signal-briefing-cue-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.detail-signal-briefing-cue {
  background: #f4f6f8;
  color: var(--ink);
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 14px;
}
.detail-signal-briefing-cue h4,
.detail-signal-briefing-cue p {
  margin: 0;
}
.detail-signal-briefing-cue h4 {
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-signal-briefing-cue p {
  color: var(--muted);
  line-height: 1.45;
}
.detail-signal-briefing-cue a {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
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
.continue-reading {
  border-top: 1px solid var(--ink);
  margin-top: 40px;
  padding-top: 28px;
}
.continue-reading-header {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
}
.continue-reading-header h2,
.continue-reading-header p {
  margin: 0;
}
.continue-reading-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.2vw, 4.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
}
.continue-reading-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.continue-reading-card {
  background: var(--panel);
  min-width: 0;
}
.continue-reading-card a {
  color: var(--ink);
  display: grid;
  gap: 12px;
  min-height: 220px;
  padding: 18px;
  text-decoration: none;
}
.continue-reading-section {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0;
  text-transform: uppercase;
}
.continue-reading-source {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin: 0;
  text-transform: uppercase;
}
.continue-reading-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.4rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.continue-reading-excerpt {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.continue-reading-excerpt span {
  color: var(--ink);
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
  .edition-brief-metrics { grid-template-columns: 1fr 1fr; }
  .signal-synthesis-header { grid-template-columns: 1fr; }
  .signal-synthesis-grid { grid-template-columns: 1fr; }
  .daily-edit-header { grid-template-columns: 1fr; }
  .daily-edit-grid { grid-template-columns: 1fr; }
  .daily-local-intelligence-header { grid-template-columns: 1fr; }
  .daily-local-intelligence-grid { grid-template-columns: 1fr; }
  .saved-article-coverage-header { grid-template-columns: 1fr; }
  .saved-article-coverage-grid { grid-template-columns: 1fr; }
  .saved-article-library-entry-header { grid-template-columns: 1fr; }
  .saved-article-library-source-grid { grid-template-columns: 1fr; }
  .saved-article-briefs-header { grid-template-columns: 1fr; }
  .saved-article-briefs-grid { grid-template-columns: 1fr; }
  .saved-article-content-organization-header { grid-template-columns: 1fr; }
  .saved-article-content-organization-grid { grid-template-columns: 1fr; }
  .editorial-brief-header { grid-template-columns: 1fr; }
  .editorial-brief-grid { grid-template-columns: 1fr; }
  .local-article-digest-grid { grid-template-columns: 1fr; }
  .briefing-topics-header { grid-template-columns: 1fr; }
  .briefing-topic-grid { grid-template-columns: 1fr; }
  .briefing-path-header { grid-template-columns: 1fr; }
  .briefing-path-grid { grid-template-columns: 1fr; }
  .lead-story-grid { grid-template-columns: 1fr; gap: 18px; }
  .section-block { grid-template-columns: 1fr; gap: 18px; }
  .story-grid { grid-template-columns: 1fr; }
  .detail-header { padding: 18px 20px; }
  .detail-signal-briefing-grid { grid-template-columns: 1fr; }
  .detail-signal-briefing-cue-grid { grid-template-columns: 1fr; }
  .continue-reading-grid { grid-template-columns: 1fr; }
  .local-article-paragraph-evidence-grid { grid-template-columns: 1fr; }
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


def _render_edition_brief(
    app_payload: dict[str, object] | None,
    *,
    has_topics: bool,
    has_path: bool,
) -> str:
    brief = _app_payload_edition_brief(app_payload)
    if not brief:
        return ""
    title = _localized_from_payload(brief.get("title"))
    dek = _localized_from_payload(brief.get("dek"))
    metrics = _render_edition_brief_metrics(brief.get("metrics"))
    points = _render_edition_brief_points(brief.get("summary_points"))
    links = _render_edition_brief_links(
        brief.get("links"),
        has_topics=has_topics,
        has_path=has_path,
    )
    lead_headline = _esc(brief.get("lead_story_headline") or "")
    lead = f'<p class="edition-brief-lead">{lead_headline}</p>' if lead_headline else ""
    section_label = '<span data-lang="en">Daily Overview</span><span data-lang="zh">每日总览</span>'
    title_html = (
        f'<span data-lang="en">{_esc(title.en)}</span><span data-lang="zh">{_esc(title.zh)}</span>'
    )
    dek_html = (
        f'<span data-lang="en">{_esc(dek.en)}</span><span data-lang="zh">{_esc(dek.zh)}</span>'
    )
    return f"""<section class="edition-brief" aria-label="Edition brief">
  <div class="edition-brief-header">
    <p class="story-section">{section_label}</p>
    <h2>{title_html}</h2>
    <p>{dek_html}</p>
    {lead}
  </div>
  {metrics}
  {points}
  {links}
</section>"""


def _app_payload_edition_brief(app_payload: dict[str, object] | None) -> dict[str, object] | None:
    if app_payload is None:
        return None
    brief = app_payload.get("edition_brief")
    return brief if isinstance(brief, dict) else None


def _localized_from_payload(value: object) -> LocalizedText:
    if isinstance(value, dict):
        zh = value.get("zh")
        en = value.get("en")
        if isinstance(zh, str) and isinstance(en, str):
            return LocalizedText(zh=zh, en=en)
    return LocalizedText(zh="", en="")


def _render_edition_brief_metrics(value: object) -> str:
    if not isinstance(value, list):
        return ""
    cards = []
    for metric in value:
        if not isinstance(metric, dict):
            continue
        label = _localized_from_payload(metric.get("label"))
        cards.append(
            f"""<div class="edition-brief-metric">
      <strong>{_esc(metric.get("value", 0))}</strong>
      <span data-lang="en">{_esc(label.en)}</span>
      <span data-lang="zh">{_esc(label.zh)}</span>
    </div>"""
        )
    return f'<div class="edition-brief-metrics">{"".join(cards)}</div>' if cards else ""


def _render_edition_brief_points(value: object) -> str:
    if not isinstance(value, list):
        return ""
    items = []
    for point in value:
        text = _localized_from_payload(point)
        if text.en or text.zh:
            items.append(
                f'<li><span data-lang="en">{_esc(text.en)}</span>'
                f'<span data-lang="zh">{_esc(text.zh)}</span></li>'
            )
    return f'<ul class="edition-brief-points">{"".join(items)}</ul>' if items else ""


def _render_edition_brief_links(
    value: object,
    *,
    has_topics: bool,
    has_path: bool,
) -> str:
    if not isinstance(value, list):
        return ""
    links = []
    for link in value:
        if not isinstance(link, dict):
            continue
        href = _safe_edition_brief_href(link.get("href"), has_topics=has_topics, has_path=has_path)
        label = _localized_from_payload(link.get("label"))
        if href is None:
            if label.en or label.zh:
                links.append(
                    f'<span><span data-lang="en">{_esc(label.en)}</span>'
                    f'<span data-lang="zh">{_esc(label.zh)}</span></span>'
                )
            continue
        links.append(
            f'<a href="{_esc(href)}"><span data-lang="en">{_esc(label.en)}</span>'
            f'<span data-lang="zh">{_esc(label.zh)}</span></a>'
        )
    return f'<div class="edition-brief-links">{"".join(links)}</div>' if links else ""


def _safe_edition_brief_href(
    href: object,
    *,
    has_topics: bool,
    has_path: bool,
) -> str | None:
    if not isinstance(href, str):
        return None
    if href == "#briefing-topics":
        return href if has_topics else None
    if href == "#briefing-path":
        return href if has_path else None
    if _validated_detail_relative_path(href) is not None:
        return href
    return None


def _render_signal_synthesis(app_payload: dict[str, object] | None) -> str:
    synthesis = _app_payload_signal_synthesis(app_payload)
    if synthesis is None:
        return ""
    groups = _signal_synthesis_groups_from_payload(synthesis)
    rendered_groups = [_render_signal_synthesis_group(group) for group in groups]
    rendered_groups = [group for group in rendered_groups if group]
    if not rendered_groups:
        return ""
    title = _localized_from_payload(synthesis.get("title"))
    dek = _localized_from_payload(synthesis.get("dek"))
    boundaries = _localized_from_payload(synthesis.get("boundaries"))
    return f"""<section class="signal-synthesis" aria-label="Signal synthesis">
  <div class="signal-synthesis-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Signal Synthesis</span>
        <span data-lang="zh">今日信号整理</span>
      </p>
      <h2>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek.en)}</span>
      <span data-lang="zh">{_esc(dek.zh)}</span>
    </p>
  </div>
  <p class="signal-synthesis-boundary">
    <span data-lang="en">{_esc(boundaries.en)}</span>
    <span data-lang="zh">{_esc(boundaries.zh)}</span>
  </p>
  <div class="signal-synthesis-grid">{"".join(rendered_groups)}</div>
</section>"""


def _app_payload_signal_synthesis(
    app_payload: dict[str, object] | None,
) -> dict[str, object] | None:
    if app_payload is None:
        return None
    synthesis = app_payload.get("signal_synthesis")
    return synthesis if isinstance(synthesis, dict) else None


def _signal_synthesis_groups_from_payload(
    synthesis: dict[str, object],
) -> list[dict[str, object]]:
    groups = synthesis.get("groups")
    if not isinstance(groups, list):
        return []
    return [group for group in groups if isinstance(group, dict)]


def _render_signal_synthesis_group(group: dict[str, object]) -> str:
    label = _localized_from_payload(group.get("label"))
    signals = group.get("signals")
    if not isinstance(signals, list):
        return ""
    cards = [
        _render_signal_synthesis_card(signal) for signal in signals[:3] if isinstance(signal, dict)
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<article class="signal-synthesis-group">
  <p class="signal-synthesis-group-title">
    <span data-lang="en">{_esc(label.en)}</span>
    <span data-lang="zh">{_esc(label.zh)}</span>
  </p>
  {"".join(cards)}
</article>"""


def _render_signal_synthesis_card(signal: dict[str, object]) -> str:
    name = str(signal.get("name", "")).strip()
    if not name:
        return ""
    summary = _localized_from_payload(signal.get("summary"))
    href = _safe_signal_detail_href(signal.get("lead_story_href"))
    story_count = (
        int(signal.get("story_count", 0)) if isinstance(signal.get("story_count"), int) else 0
    )
    evidence_count = (
        int(signal.get("evidence_count", 0)) if isinstance(signal.get("evidence_count"), int) else 0
    )
    heat_delta = (
        int(signal.get("max_heat_delta", 0)) if isinstance(signal.get("max_heat_delta"), int) else 0
    )
    label = str(signal.get("label", "")).strip()
    meta = _signal_synthesis_meta_label(
        label=label,
        story_count=story_count,
        evidence_count=evidence_count,
        heat_delta=heat_delta,
    )
    body = f"""<h3>{_esc(name)}</h3>
  <p>
    <span data-lang="en">{_esc(summary.en)}</span>
    <span data-lang="zh">{_esc(summary.zh)}</span>
  </p>
  <div class="signal-synthesis-meta">{meta}</div>"""
    if href is None:
        return f'<div class="signal-synthesis-card">{body}</div>'
    return f'<a class="signal-synthesis-card" href="{_esc(href)}">{body}</a>'


def _render_daily_edit(app_payload: dict[str, object] | None) -> str:
    cards = _daily_edit_cards(app_payload)
    if not cards:
        return ""
    rendered_cards = "\n".join(_render_daily_edit_card(card) for card in cards)
    return f"""<section class="daily-edit" aria-label="Daily edit">
  <div class="daily-edit-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Edit</span>
        <span data-lang="zh">今日编辑简报</span>
      </p>
      <h2>
        <span data-lang="en">What matters today</span>
        <span data-lang="zh">今天值得先看什么</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">A scan-first edit from existing ROW ONE signals.</span>
      <span data-lang="zh">基于现有 ROW ONE 信号整理的快速编辑简报。</span>
    </p>
  </div>
  <div class="daily-edit-grid">
{rendered_cards}
  </div>
</section>"""


def _daily_edit_cards(app_payload: dict[str, object] | None) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    cards = [
        _daily_edit_what_to_know(app_payload),
        _daily_edit_signals_to_watch(app_payload),
        _daily_edit_read_next(app_payload),
        _daily_edit_evidence_note(app_payload),
    ]
    return [card for card in cards if card is not None][:DAILY_EDIT_MAX_CARDS]


def _daily_edit_what_to_know(app_payload: dict[str, object]) -> dict[str, object] | None:
    brief = _app_payload_edition_brief(app_payload)
    if brief is None:
        return None
    point = _first_localized_payload(brief.get("summary_points"))
    lead_headline = str(brief.get("lead_story_headline") or "").strip()
    if not (point.en or point.zh or lead_headline):
        return None
    if lead_headline and (point.en or point.zh):
        point = LocalizedText(
            en=f"{lead_headline}: {point.en}" if point.en else lead_headline,
            zh=f"{lead_headline}: {point.zh}" if point.zh else lead_headline,
        )
    elif not point.en and lead_headline:
        point = LocalizedText(en=lead_headline, zh=lead_headline)
    meta = []
    lead_story_id = str(brief.get("lead_story_id") or "").strip()
    if lead_story_id:
        meta.append(LocalizedText(en="Read first", zh="先读"))
    return _daily_edit_card(
        title=LocalizedText(en="What To Know", zh="今日重点"),
        body=point,
        href=_safe_daily_edit_href(brief.get("lead_story_href")),
        meta=meta,
    )


def _daily_edit_signals_to_watch(app_payload: dict[str, object]) -> dict[str, object] | None:
    synthesis = _app_payload_signal_synthesis(app_payload)
    if synthesis is not None:
        for signal in _daily_edit_signal_candidates(synthesis):
            card = _daily_edit_signal_card(signal)
            if card is not None:
                return card
    return _daily_edit_topic_fallback_card(app_payload) or _daily_edit_read_first_signal_card(
        app_payload
    )


def _daily_edit_signal_candidates(synthesis: dict[str, object]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for group in _signal_synthesis_groups_from_payload(synthesis):
        signals = group.get("signals")
        if not isinstance(signals, list):
            continue
        for signal in signals:
            if isinstance(signal, dict):
                candidates.append(signal)
                if len(candidates) >= DAILY_EDIT_MAX_SIGNALS:
                    return candidates
    return candidates


def _daily_edit_signal_card(signal: dict[str, object]) -> dict[str, object] | None:
    name = str(signal.get("name") or "").strip()
    if not name:
        return None
    summary = _localized_from_payload(signal.get("summary"))
    if not (summary.en or summary.zh):
        summary = LocalizedText(en=name, zh=name)
    meta = [
        _daily_edit_count_meta(
            _int_or_zero(signal.get("story_count")),
            "story",
            "stories",
            "条故事",
        ),
        _daily_edit_count_meta(
            _int_or_zero(signal.get("evidence_count")),
            "evidence link",
            "evidence links",
            "条证据链接",
        ),
    ]
    heat_delta = _int_or_zero(signal.get("max_heat_delta"))
    if heat_delta > 0:
        meta.append(LocalizedText(en=f"+{heat_delta} heat", zh=f"+{heat_delta} 热度"))
    label = str(signal.get("label") or "").strip()
    if label:
        meta.insert(0, LocalizedText(en=label, zh=label))
    return _daily_edit_card(
        title=LocalizedText(en="Signals To Watch", zh="值得关注"),
        body=LocalizedText(
            en=f"{name}: {summary.en}" if summary.en else name,
            zh=f"{name}: {summary.zh}" if summary.zh else name,
        ),
        href=_safe_daily_edit_href(signal.get("lead_story_href")),
        meta=meta,
    )


def _daily_edit_topic_fallback_card(app_payload: dict[str, object]) -> dict[str, object] | None:
    for topic in _app_payload_briefing_topics(app_payload):
        title = _localized_topic_field(topic, "title")
        lead_story = _topic_lead_story(topic) or _topic_nested_lead_story(topic)
        headline = _topic_localized_card_text(lead_story, "headline")
        takeaway = _topic_localized_card_text(lead_story, "editorial_takeaway")
        body = takeaway if takeaway.en or takeaway.zh else headline
        if not (title.en or title.zh or body.en or body.zh):
            continue
        meta = [
            _daily_edit_count_meta(
                _int_or_zero(topic.get("story_count")),
                "story",
                "stories",
                "条故事",
            ),
            _daily_edit_count_meta(
                _int_or_zero(topic.get("evidence_count")),
                "evidence link",
                "evidence links",
                "条证据链接",
            ),
        ]
        heat_delta = _int_or_zero(topic.get("positive_heat_delta_sum"))
        if heat_delta > 0:
            meta.append(LocalizedText(en=f"+{heat_delta} heat", zh=f"+{heat_delta} 热度"))
        if body.en or body.zh:
            body = LocalizedText(
                en=f"{title.en}: {body.en}" if title.en and body.en else title.en or body.en,
                zh=f"{title.zh}: {body.zh}" if title.zh and body.zh else title.zh or body.zh,
            )
        else:
            body = title
        href = _safe_daily_edit_href(lead_story.get("detail_href")) if lead_story else None
        return _daily_edit_card(
            title=LocalizedText(en="Signals To Watch", zh="值得关注"),
            body=body,
            href=href,
            meta=meta,
        )
    return None


def _daily_edit_read_first_signal_card(app_payload: dict[str, object]) -> dict[str, object] | None:
    card = _daily_edit_read_first_card(app_payload)
    if card is None:
        return None
    headline = _topic_localized_card_text(card, "headline")
    takeaway = _topic_localized_card_text(card, "editorial_takeaway")
    body = takeaway if takeaway.en or takeaway.zh else headline
    if not (headline.en or headline.zh or body.en or body.zh):
        return None
    if headline.en or headline.zh:
        body = LocalizedText(
            en=(
                f"{headline.en}: {body.en}"
                if headline.en and body.en and body.en != headline.en
                else headline.en or body.en
            ),
            zh=(
                f"{headline.zh}: {body.zh}"
                if headline.zh and body.zh and body.zh != headline.zh
                else headline.zh or body.zh
            ),
        )
    return _daily_edit_card(
        title=LocalizedText(en="Signals To Watch", zh="值得关注"),
        body=body,
        href=_safe_daily_edit_href(card.get("detail_href")),
        meta=[
            _daily_edit_count_meta(
                _int_or_zero(card.get("evidence_count")),
                "evidence link",
                "evidence links",
                "条证据链接",
            )
        ],
    )


def _daily_edit_read_first_card(app_payload: dict[str, object]) -> dict[str, object] | None:
    blocks = _app_payload_digest_blocks(app_payload)
    read_first_block = next((block for block in blocks if block.get("key") == "read_first"), None)
    if read_first_block is None:
        return None
    cards = _block_cards(read_first_block, set())
    return cards[0] if cards else None


def _daily_edit_read_next(app_payload: dict[str, object]) -> dict[str, object] | None:
    blocks = _app_payload_digest_blocks(app_payload)
    excluded_story_ids = _read_first_story_ids(blocks)
    for key in ("key_takeaways", "signals_to_watch"):
        for block in blocks:
            if block.get("key") != key:
                continue
            for card in _block_cards(block, excluded_story_ids)[:DAILY_EDIT_MAX_PATH_ITEMS]:
                headline = _topic_localized_card_text(card, "headline")
                takeaway = _topic_localized_card_text(card, "editorial_takeaway")
                body = takeaway if takeaway.en or takeaway.zh else headline
                if not (headline.en or headline.zh or body.en or body.zh):
                    continue
                if headline.en or headline.zh:
                    body = LocalizedText(
                        en=(
                            f"{headline.en}: {body.en}"
                            if headline.en and body.en and body.en != headline.en
                            else headline.en or body.en
                        ),
                        zh=(
                            f"{headline.zh}: {body.zh}"
                            if headline.zh and body.zh and body.zh != headline.zh
                            else headline.zh or body.zh
                        ),
                    )
                return _daily_edit_card(
                    title=LocalizedText(en="Read Next", zh="阅读路径"),
                    body=body,
                    href=_safe_daily_edit_href(card.get("detail_href")),
                    meta=[LocalizedText(en="Local reading path", zh="本地阅读路径")],
                )
    card = _daily_edit_read_first_card(app_payload)
    if card is None:
        return None
    headline = _topic_localized_card_text(card, "headline")
    takeaway = _topic_localized_card_text(card, "editorial_takeaway")
    body = takeaway if takeaway.en or takeaway.zh else headline
    if not (headline.en or headline.zh or body.en or body.zh):
        return None
    if headline.en or headline.zh:
        body = LocalizedText(
            en=(
                f"{headline.en}: {body.en}"
                if headline.en and body.en and body.en != headline.en
                else headline.en or body.en
            ),
            zh=(
                f"{headline.zh}: {body.zh}"
                if headline.zh and body.zh and body.zh != headline.zh
                else headline.zh or body.zh
            ),
        )
    return _daily_edit_card(
        title=LocalizedText(en="Read Next", zh="阅读路径"),
        body=body,
        href=_safe_daily_edit_href(card.get("detail_href")),
        meta=[LocalizedText(en="Read first fallback", zh="先读兜底")],
    )


def _topic_nested_lead_story(topic: dict[str, object]) -> dict[str, object] | None:
    lead_story = topic.get("lead_story")
    return lead_story if isinstance(lead_story, dict) else None


def _daily_edit_evidence_note(app_payload: dict[str, object]) -> dict[str, object] | None:
    evidence_count = _daily_edit_evidence_count(app_payload)
    synthesis = _app_payload_signal_synthesis(app_payload)
    boundaries = (
        _localized_from_payload(synthesis.get("boundaries")) if synthesis is not None else None
    )
    if evidence_count == 0 and (boundaries is None or not (boundaries.en or boundaries.zh)):
        return None
    evidence_en = (
        "1 existing ROW ONE evidence link"
        if evidence_count == 1
        else f"{evidence_count} existing ROW ONE evidence links"
    )
    evidence_zh = f"{evidence_count} 条现有 ROW ONE 证据链接"
    boundary_en = boundaries.en if boundaries is not None and boundaries.en else evidence_en
    boundary_zh = boundaries.zh if boundaries is not None and boundaries.zh else evidence_zh
    return _daily_edit_card(
        title=LocalizedText(en="Evidence Note", zh="线索边界"),
        body=LocalizedText(
            en=(
                f"Based on {evidence_en}; {boundary_en}; "
                "review the underlying stories before acting."
            ),
            zh=f"基于{evidence_zh}；{boundary_zh}；行动前请复核底层故事。",
        ),
        href="#main-content",
        meta=[LocalizedText(en="Existing evidence only", zh="仅限现有证据")],
    )


def _daily_edit_evidence_count(app_payload: dict[str, object]) -> int:
    daily_digest = app_payload.get("daily_digest")
    if isinstance(daily_digest, dict):
        count = daily_digest.get("evidence_count")
        if isinstance(count, int):
            return count
    brief = _app_payload_edition_brief(app_payload)
    if brief is None:
        return 0
    metrics = brief.get("metrics")
    if not isinstance(metrics, list):
        return 0
    for metric in metrics:
        if not isinstance(metric, dict) or metric.get("key") != "evidence":
            continue
        return _int_or_zero(metric.get("value"))
    return 0


def _first_localized_payload(value: object) -> LocalizedText:
    if not isinstance(value, list):
        return LocalizedText(zh="", en="")
    for item in value:
        text = _localized_from_payload(item)
        if text.en or text.zh:
            return text
    return LocalizedText(zh="", en="")


def _daily_edit_count_meta(
    count: int,
    singular: str,
    plural: str,
    zh_suffix: str,
) -> LocalizedText:
    label = singular if count == 1 else plural
    return LocalizedText(en=f"{count} {label}", zh=f"{count} {zh_suffix}")


def _daily_edit_card(
    *,
    title: LocalizedText,
    body: LocalizedText,
    href: str | None,
    meta: list[LocalizedText],
) -> dict[str, object]:
    return {"title": title, "body": body, "href": href, "meta": meta}


def _render_daily_edit_card(card: dict[str, object]) -> str:
    title = card["title"]
    body = card["body"]
    if not isinstance(title, LocalizedText) or not isinstance(body, LocalizedText):
        return ""
    href = _safe_daily_edit_href(card.get("href")) or "#main-content"
    meta = card.get("meta")
    rendered_meta = ""
    if isinstance(meta, list):
        parts = [
            f'<span data-lang="en">{_esc(item.en)}</span>'
            f'<span data-lang="zh">{_esc(item.zh)}</span>'
            for item in meta
            if isinstance(item, LocalizedText) and (item.en or item.zh)
        ]
        if parts:
            rendered_meta = f'    <div class="daily-edit-card-meta">{"".join(parts)}</div>\n'
    return f"""    <a class="daily-edit-card" href="{_esc(href)}">
      <h3>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(body.en)}</span>
        <span data-lang="zh">{_esc(body.zh)}</span>
      </p>
{rendered_meta}      <span class="daily-edit-link">
        <span data-lang="en">Open local context</span>
        <span data-lang="zh">打开本地上下文</span>
      </span>
    </a>"""


def _safe_daily_edit_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href in {"#main-content", "#briefing-topics", "#briefing-path"}:
        return href
    if _validated_detail_relative_path(href) is not None:
        return href
    return None


def _render_daily_local_intelligence(
    sections: Sequence[RowOneDailyLocalIntelligenceSection] | None,
) -> str:
    if not sections:
        return ""
    rendered_sections = [
        _render_daily_local_intelligence_section(section) for section in sections if section.items
    ]
    rendered_sections = [section for section in rendered_sections if section]
    if not rendered_sections:
        return ""
    return f"""<section class="daily-local-intelligence" aria-label="Daily local intelligence">
  <div class="daily-local-intelligence-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Local Intelligence</span>
        <span data-lang="zh">每日本地情报</span>
      </p>
      <h2>
        <span data-lang="en">Daily Local Intelligence</span>
        <span data-lang="zh">每日本地情报</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Source-backed fashion signals from saved local article bodies.</span>
      <span data-lang="zh">来自本地保存正文的时尚信号整理。</span>
    </p>
  </div>
  <div class="daily-local-intelligence-grid">{"".join(rendered_sections)}</div>
</section>"""


def _render_saved_article_coverage(coverage: RowOneSavedArticleCoverage | None) -> str:
    if coverage is None:
        return ""
    metrics = _render_saved_article_coverage_metrics(coverage)
    sources = _render_saved_article_coverage_sources(coverage)
    cards = "\n".join(_render_saved_article_coverage_card(item) for item in coverage.items)
    return f"""<section class="saved-article-coverage" aria-label="Saved article coverage">
  <div class="saved-article-coverage-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Coverage</span>
        <span data-lang="zh">保存正文覆盖</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Coverage</span>
        <span data-lang="zh">保存正文覆盖</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">The local source set behind today's saved article pages.</span>
      <span data-lang="zh">今日保存正文页面背后的本地来源集合。</span>
    </p>
  </div>
  {metrics}
  {sources}
  <div class="saved-article-coverage-grid">{cards}</div>
</section>"""


def _render_saved_article_coverage_metrics(coverage: RowOneSavedArticleCoverage) -> str:
    metrics = [
        _render_saved_article_coverage_metric(
            _count_label(coverage.article_count, "saved article", "saved articles"),
            f"{coverage.article_count} 篇保存文章",
        ),
        _render_saved_article_coverage_metric(
            _count_label(
                coverage.saved_paragraph_count,
                "saved paragraph",
                "saved paragraphs",
            ),
            f"{coverage.saved_paragraph_count} 个保存段落",
        ),
        _render_saved_article_coverage_metric(
            _count_label(
                coverage.organized_section_count,
                "organized section",
                "organized sections",
            ),
            f"{coverage.organized_section_count} 个整理栏目",
        ),
        _render_saved_article_coverage_metric(
            _count_label(coverage.source_count, "source", "sources"),
            f"{coverage.source_count} 个来源",
        ),
    ]
    return '  <ul class="saved-article-coverage-metrics">\n' + "\n".join(metrics) + "\n  </ul>"


def _render_saved_article_coverage_metric(label_en: str, label_zh: str) -> str:
    return (
        "    <li>"
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        "</li>"
    )


def _render_saved_article_coverage_sources(coverage: RowOneSavedArticleCoverage) -> str:
    if not coverage.sources:
        return ""
    source_items = []
    for source in coverage.sources:
        article_count_en = _count_label(source.article_count, "article", "articles")
        article_count_zh = f"{source.article_count} 篇文章"
        source_items.append(
            "    <li>"
            f'<span class="saved-article-coverage-source-name">{_esc(source.name)}</span>'
            f'<span data-lang="en">{_esc(article_count_en)}</span>'
            f'<span data-lang="zh">{_esc(article_count_zh)}</span>'
            "</li>"
        )
    sources = "\n".join(source_items)
    return (
        '  <ul class="saved-article-coverage-sources" aria-label="Saved article sources">\n'
        + sources
        + "\n  </ul>"
    )


def _render_saved_article_coverage_card(item: RowOneSavedArticleCoverageItem) -> str:
    href = _safe_saved_article_coverage_href(item.detail_path)
    if href is None:
        return ""
    paragraph_count_en = _count_label(
        item.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    paragraph_count_zh = f"{item.saved_paragraph_count} 个保存段落"
    section_count_en = _count_label(
        item.organized_section_count,
        "organized section",
        "organized sections",
    )
    section_count_zh = f"{item.organized_section_count} 个整理栏目"
    return f"""    <a class="saved-article-coverage-card" href="{_esc(href)}">
      <strong>
        <span data-lang="en">{_esc(item.title.en)}</span>
        <span data-lang="zh">{_esc(item.title.zh)}</span>
      </strong>
      <span>{_esc(item.source_name)}</span>
      <span>
        <span data-lang="en">{_esc(item.section_title.en)}</span>
        <span data-lang="zh">{_esc(item.section_title.zh)}</span>
      </span>
      <span>
        <span data-lang="en">{_esc(paragraph_count_en)}</span>
        <span data-lang="zh">{_esc(paragraph_count_zh)}</span>
      </span>
      <span>
        <span data-lang="en">{_esc(section_count_en)}</span>
        <span data-lang="zh">{_esc(section_count_zh)}</span>
      </span>
    </a>"""


def _safe_saved_article_coverage_href(href: object) -> str | None:
    return safe_row_one_detail_fragment_href(href, "local-article-digest")


def _has_saved_signal_index_entries(index: RowOneSavedSignalIndex | None) -> bool:
    return index is not None and bool(index.entries)


def _render_saved_article_library_entry(
    library: RowOneSavedArticleLibrary | None,
    *,
    saved_signal_index: RowOneSavedSignalIndex | None = None,
) -> str:
    if library is None:
        return ""
    has_saved_signal_index = _has_saved_signal_index_entries(saved_signal_index)
    dek_en = (
        "Browse saved local articles by signals or sources."
        if has_saved_signal_index
        else "Browse the current edition's saved local articles by source."
    )
    dek_zh = (
        "按信号或来源浏览本地保存文章。"
        if has_saved_signal_index
        else "按来源浏览当前版本的本地保存文章。"
    )
    return f"""<section class="saved-article-library-entry"
  aria-label="Daily saved article library">
  <div class="saved-article-library-entry-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Daily Saved Article Library</span>
        <span data-lang="zh">每日本地文章库</span>
      </p>
      <h2>
        <span data-lang="en">Daily Saved Article Library</span>
        <span data-lang="zh">每日本地文章库</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">{_esc(dek_en)}</span>
      <span data-lang="zh">{_esc(dek_zh)}</span>
    </p>
  </div>
  {_render_saved_article_library_metrics(library, css_class="saved-article-library-entry-metrics")}
  <a class="saved-article-library-entry-link" href="articles/index.html">
    <span data-lang="en">Open saved article library</span>
    <span data-lang="zh">打开本地文章库</span>
  </a>
</section>"""


def _render_saved_article_library_metrics(
    library: RowOneSavedArticleLibrary,
    *,
    css_class: str,
) -> str:
    metrics = [
        _render_saved_article_library_metric(
            _count_label(library.article_count, "saved article", "saved articles"),
            f"{library.article_count} 篇保存文章",
        ),
        _render_saved_article_library_metric(
            _count_label(library.source_count, "source", "sources"),
            f"{library.source_count} 个来源",
        ),
        _render_saved_article_library_metric(
            _count_label(
                library.saved_paragraph_count,
                "saved paragraph",
                "saved paragraphs",
            ),
            f"{library.saved_paragraph_count} 个保存段落",
        ),
        _render_saved_article_library_metric(
            _count_label(
                library.organized_section_count,
                "organized section",
                "organized sections",
            ),
            f"{library.organized_section_count} 个整理栏目",
        ),
    ]
    return f'<ul class="{_esc(css_class)}">\n' + "\n".join(metrics) + "\n  </ul>"


def _render_saved_article_library_metric(label_en: str, label_zh: str) -> str:
    return (
        "    <li>"
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        "</li>"
    )


def _render_saved_article_library_source(
    group: RowOneSavedArticleLibrarySourceGroup,
) -> str:
    cards = "\n".join(_render_saved_article_library_card(entry) for entry in group.entries)
    article_count_en = _count_label(group.article_count, "article", "articles")
    article_count_zh = f"{group.article_count} 篇文章"
    paragraph_count_en = _count_label(
        group.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    paragraph_count_zh = f"{group.saved_paragraph_count} 个保存段落"
    return f"""    <section class="saved-article-library-source">
      <div class="saved-article-library-source-header">
        <h2>{_esc(group.source_name)}</h2>
        <p>
          <span data-lang="en">{_esc(article_count_en)}, {_esc(paragraph_count_en)}</span>
          <span data-lang="zh">{_esc(article_count_zh)}，{_esc(paragraph_count_zh)}</span>
        </p>
      </div>
      <div class="saved-article-library-source-grid">{cards}</div>
    </section>"""


def _render_saved_article_library_card(entry: RowOneSavedArticleLibraryEntry) -> str:
    refs = _render_saved_article_library_refs(entry.references)
    paragraphs = _render_saved_article_library_paragraphs(entry.paragraph_links)
    actions = _render_saved_article_library_actions(entry)
    paragraph_count_en = _count_label(
        entry.saved_paragraph_count,
        "saved paragraph",
        "saved paragraphs",
    )
    section_count_en = _count_label(
        entry.organized_section_count,
        "organized section",
        "organized sections",
    )
    return f"""        <article class="saved-article-library-card">
          <div class="saved-article-library-card-meta">
            <span>{_esc(entry.source_name)}</span>
            <span>
              <span data-lang="en">{_esc(entry.section_title.en)}</span>
              <span data-lang="zh">{_esc(entry.section_title.zh)}</span>
            </span>
          </div>
          <h3>
            <span data-lang="en">{_esc(entry.title.en)}</span>
            <span data-lang="zh">{_esc(entry.title.zh)}</span>
          </h3>
          <ul class="saved-article-library-card-counts">
            <li>
              <span data-lang="en">{_esc(paragraph_count_en)}</span>
              <span data-lang="zh">{_esc(f"{entry.saved_paragraph_count} 个保存段落")}</span>
            </li>
            <li>
              <span data-lang="en">{_esc(section_count_en)}</span>
              <span data-lang="zh">{_esc(f"{entry.organized_section_count} 个整理栏目")}</span>
            </li>
          </ul>
          {refs}
          {paragraphs}
          {actions}
        </article>"""


def _render_saved_article_library_refs(refs: Sequence[RowOneReference]) -> str:
    if not refs:
        return ""
    chips = "".join(
        '<span class="saved-article-library-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(ref.label.strip() or ref.type)}</span>"
        "</span>"
        for ref in refs
    )
    return f"""<div class="saved-article-library-refs" aria-label="Article references">
            {chips}
          </div>"""


def _render_saved_article_library_paragraphs(
    paragraph_links: Sequence[RowOneSavedArticleLibraryParagraphLink],
) -> str:
    links = []
    for paragraph_link in paragraph_links:
        href = _safe_saved_article_library_paragraph_href(paragraph_link.href)
        if href is None:
            continue
        links.append(
            f"""<a href="{_esc(_saved_article_library_page_href(href))}">
              <span data-lang="en">{_esc(paragraph_link.label.en)}</span>
              <span data-lang="zh">{_esc(paragraph_link.label.zh)}</span>
            </a>"""
        )
    if not links:
        return ""
    return (
        '<div class="saved-article-library-paragraphs" aria-label="Saved paragraph links">'
        + "".join(links)
        + "</div>"
    )


def _render_saved_article_library_actions(entry: RowOneSavedArticleLibraryEntry) -> str:
    actions = [
        (
            entry.reader_path,
            "local-article-reader",
            "Read local article",
            "阅读本地正文",
        ),
        (
            entry.digest_path,
            "local-article-digest",
            "Open digest",
            "打开整理摘要",
        ),
    ]
    if entry.paragraph_links:
        actions.append(
            (
                entry.evidence_path,
                "local-article-paragraph-evidence",
                "Open evidence",
                "打开段落线索",
            )
        )
    rendered = []
    for href, fragment, label_en, label_zh in actions:
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        rendered.append(
            f"""<a href="{_esc(_saved_article_library_page_href(safe_href))}">
              <span data-lang="en">{_esc(label_en)}</span>
              <span data-lang="zh">{_esc(label_zh)}</span>
            </a>"""
        )
    if not rendered:
        return ""
    return '<div class="saved-article-library-actions">' + "".join(rendered) + "</div>"


def _safe_saved_article_library_paragraph_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _saved_article_library_page_href(href: str) -> str:
    return f"../{href}"


def _render_saved_signal_index(index: RowOneSavedSignalIndex | None) -> str:
    if not _has_saved_signal_index_entries(index):
        return ""
    cards = [_render_saved_signal_index_card(entry) for entry in index.entries]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<section class="saved-signal-index" aria-label="Saved signal index">
  <div class="saved-signal-index-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Signal Index</span>
        <span data-lang="zh">本地信号索引</span>
      </p>
      <h2>
        <span data-lang="en">Saved Signal Index</span>
        <span data-lang="zh">本地信号索引</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Browse the saved local article set by tracked fashion signals.</span>
      <span data-lang="zh">按已追踪的时尚信号浏览本地保存文章。</span>
    </p>
  </div>
  {_render_saved_signal_index_metrics(index)}
  <div class="saved-signal-index-grid">{"".join(cards)}</div>
</section>"""


def _render_saved_signal_index_metrics(index: RowOneSavedSignalIndex) -> str:
    metrics = [
        _render_saved_article_library_metric(
            _count_label(index.signal_count, "saved signal", "saved signals"),
            f"{index.signal_count} 个本地信号",
        ),
        _render_saved_article_library_metric(
            _count_label(
                index.supporting_article_count,
                "supporting article",
                "supporting articles",
            ),
            f"{index.supporting_article_count} 篇支撑文章",
        ),
        _render_saved_article_library_metric(
            _count_label(index.source_count, "source", "sources"),
            f"{index.source_count} 个来源",
        ),
        _render_saved_article_library_metric(
            _count_label(
                index.supporting_paragraph_count,
                "supporting paragraph",
                "supporting paragraphs",
            ),
            f"{index.supporting_paragraph_count} 个支撑段落",
        ),
    ]
    return '<ul class="saved-signal-index-metrics">\n' + "\n".join(metrics) + "\n  </ul>"


def _render_saved_signal_index_card(entry: RowOneSavedSignalIndexEntry) -> str:
    support = _render_saved_signal_index_support(entry.supports)
    article_count = _count_label(entry.article_count, "article", "articles")
    source_count = _count_label(entry.source_count, "source", "sources")
    paragraph_count = _count_label(
        entry.supporting_paragraph_count,
        "supporting paragraph",
        "supporting paragraphs",
    )
    return f"""    <article class="saved-signal-index-card">
      <div class="saved-signal-index-card-header">
        <div class="saved-signal-index-card-meta">
          <span>{_esc(entry.type)}</span>
          <span>{_esc(entry.label)}</span>
        </div>
        <h3>{_esc(entry.name)}</h3>
        <div class="saved-signal-index-card-meta">
          <span data-lang="en">{_esc(article_count)}</span>
          <span data-lang="zh">{_esc(f"{entry.article_count} 篇文章")}</span>
          <span data-lang="en">{_esc(source_count)}</span>
          <span data-lang="zh">{_esc(f"{entry.source_count} 个来源")}</span>
          <span data-lang="en">{_esc(paragraph_count)}</span>
          <span data-lang="zh">{_esc(f"{entry.supporting_paragraph_count} 个支撑段落")}</span>
        </div>
      </div>
      {support}
    </article>"""


def _render_saved_signal_index_support(
    supports: Sequence[RowOneSavedSignalIndexSupport],
) -> str:
    rows = [_render_saved_signal_index_support_row(support) for support in supports]
    rows = [row for row in rows if row]
    if not rows:
        return ""
    return '<div class="saved-signal-index-support">' + "".join(rows) + "</div>"


def _render_saved_signal_index_support_row(
    support: RowOneSavedSignalIndexSupport,
) -> str:
    actions = _render_saved_signal_actions(support)
    paragraphs = _render_saved_signal_paragraphs(support.paragraph_links)
    excerpt = _render_saved_signal_support_excerpt(support.excerpt)
    return f"""<div class="saved-signal-index-support-row">
        <strong>
          <span data-lang="en">{_esc(support.title.en)}</span>
          <span data-lang="zh">{_esc(support.title.zh)}</span>
        </strong>
        <div class="saved-signal-index-support-meta">
          <span>{_esc(support.source_name)}</span>
          <span>
            <span data-lang="en">{_esc(support.section_title.en)}</span>
            <span data-lang="zh">{_esc(support.section_title.zh)}</span>
          </span>
          <span>
            <span data-lang="en">{_esc(support.content_section_title.en)}</span>
            <span data-lang="zh">{_esc(support.content_section_title.zh)}</span>
          </span>
        </div>
        {excerpt}
        {actions}
        {paragraphs}
      </div>"""


def _render_saved_signal_support_excerpt(excerpt: LocalizedText | None) -> str:
    if excerpt is None:
        return ""
    return f"""<p class="saved-signal-index-support-excerpt">
          <span data-lang="en">{_esc(excerpt.en)}</span>
          <span data-lang="zh">{_esc(excerpt.zh)}</span>
        </p>"""


def _render_saved_signal_actions(support: RowOneSavedSignalIndexSupport) -> str:
    href = _safe_saved_signal_section_href(support.section_path)
    if href is None:
        return ""
    return f"""<div class="saved-signal-index-actions">
          <a href="{_esc(_saved_article_library_page_href(href))}">
            <span data-lang="en">Open organized section</span>
            <span data-lang="zh">打开整理栏目</span>
          </a>
        </div>"""


def _render_saved_signal_paragraphs(
    paragraph_links: Sequence[RowOneSavedSignalIndexParagraphLink],
) -> str:
    links = []
    for paragraph_link in paragraph_links:
        href = _safe_saved_signal_paragraph_href(paragraph_link.href)
        if href is None:
            continue
        links.append(
            f"""<a href="{_esc(_saved_article_library_page_href(href))}">
            <span data-lang="en">{_esc(paragraph_link.label.en)}</span>
            <span data-lang="zh">{_esc(paragraph_link.label.zh)}</span>
          </a>"""
        )
    if not links:
        return ""
    return '<div class="saved-signal-index-paragraphs">' + "".join(links) + "</div>"


def _safe_saved_signal_section_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _safe_saved_signal_paragraph_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    path, separator, fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"{safe_path}#{fragment}"


def _render_saved_article_briefs(briefs: RowOneSavedArticleBriefs | None) -> str:
    if briefs is None:
        return ""
    cards = [_render_saved_article_brief_card(item) for item in briefs.items]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<section class="saved-article-briefs" aria-label="Saved article briefs">
  <div class="saved-article-briefs-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Briefs</span>
        <span data-lang="zh">保存正文简报</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Briefs</span>
        <span data-lang="zh">保存正文简报</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Readable saved-article takeaways from today's local source bodies.</span>
      <span data-lang="zh">来自今日本地保存正文的可读文章要点。</span>
    </p>
  </div>
  <div class="saved-article-briefs-grid">{"".join(cards)}</div>
</section>"""


def _render_saved_article_brief_card(item: RowOneSavedArticleBriefItem) -> str:
    href = safe_row_one_detail_fragment_href(item.detail_path, "local-article-digest")
    if href is None:
        return ""
    people_brands = _render_saved_article_brief_chip_group(
        item.people_brands,
        heading_en="People & Brands",
        heading_zh="品牌与人物",
    )
    products = _render_saved_article_brief_chip_group(
        item.products,
        heading_en="Products",
        heading_zh="产品",
    )
    chip_groups = people_brands + products
    chip_group_block = (
        f'\n      <div class="saved-article-brief-chip-groups">{chip_groups}\n      </div>'
        if chip_groups
        else ""
    )
    return f"""    <a class="saved-article-brief-card" href="{_esc(href)}">
      <div class="saved-article-brief-meta">
        <span>{_esc(item.source_name)}</span>
        <span>
          <span data-lang="en">{_esc(item.section_title.en)}</span>
          <span data-lang="zh">{_esc(item.section_title.zh)}</span>
        </span>
      </div>
      <h3>
        <span data-lang="en">{_esc(item.title.en)}</span>
        <span data-lang="zh">{_esc(item.title.zh)}</span>
      </h3>
      <p class="saved-article-brief-body">
        <span data-lang="en">{_esc(_local_article_digest_excerpt(item.lead.en))}</span>
        <span data-lang="zh">{_esc(_local_article_digest_excerpt(item.lead.zh))}</span>
      </p>{chip_group_block}
    </a>"""


def _render_saved_article_brief_chip_group(
    refs: Sequence[RowOneReference],
    *,
    heading_en: str,
    heading_zh: str,
) -> str:
    if not refs:
        return ""
    chips = "".join(_render_saved_article_brief_chip(ref) for ref in refs)
    return f"""
        <div class="saved-article-brief-chip-group">
          <span class="saved-article-brief-chip-heading">
            <span data-lang="en">{_esc(heading_en)}</span>
            <span data-lang="zh">{_esc(heading_zh)}</span>
          </span>
          <span class="saved-article-brief-chip-list">{chips}</span>
        </div>"""


def _render_saved_article_brief_chip(ref: RowOneReference) -> str:
    label = ref.label.strip() or ref.type.strip()
    return (
        '<span class="saved-article-brief-chip">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(label)}</span>"
        "</span>"
    )


def _render_saved_article_content_organization(
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    href_prefix: str = "",
) -> str:
    if organization is None:
        return ""
    groups = [
        _render_saved_article_content_organization_group(group, href_prefix=href_prefix)
        for group in organization.groups
    ]
    groups = [group for group in groups if group]
    if not groups:
        return ""
    return f"""<section class="saved-article-content-organization"
  aria-label="Saved article content organization">
  <div class="saved-article-content-organization-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Content Organization</span>
        <span data-lang="zh">保存正文内容整理</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Content Organization</span>
        <span data-lang="zh">保存正文内容整理</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Scan-first groupings from locally saved article bodies.</span>
      <span data-lang="zh">从本地保存正文中提炼的快速浏览分组。</span>
    </p>
  </div>
  <div class="saved-article-content-organization-groups">{"".join(groups)}</div>
</section>"""


def _render_saved_article_content_organization_group(
    group: RowOneSavedArticleContentOrganizationGroup,
    *,
    href_prefix: str = "",
) -> str:
    cards = [
        _render_saved_article_content_organization_card(card, href_prefix=href_prefix)
        for card in group.cards
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""    <article class="saved-article-content-organization-group">
      <div class="saved-article-content-organization-group-header">
        <h3>
          <span data-lang="en">{_esc(group.title.en)}</span>
          <span data-lang="zh">{_esc(group.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(group.dek.en)}</span>
          <span data-lang="zh">{_esc(group.dek.zh)}</span>
        </p>
      </div>
      <div class="saved-article-content-organization-grid">{"".join(cards)}</div>
    </article>"""


def _render_saved_article_content_organization_card(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, href_prefix)
    chips = _render_saved_article_content_organization_chips(card, href_prefix=href_prefix)
    chip_block = (
        f'\n      <div class="saved-article-content-organization-chips">{chips}</div>'
        if chips
        else ""
    )
    return f"""        <article class="saved-article-content-organization-card">
      <div class="saved-article-content-organization-meta">
        <span>{_esc(card.source_name)}</span>
        <span>
          <span data-lang="en">{_esc(card.section_title.en)}</span>
          <span data-lang="zh">{_esc(card.section_title.zh)}</span>
        </span>
        <span>
          <span data-lang="en">{_esc(card.section_label.en)}</span>
          <span data-lang="zh">{_esc(card.section_label.zh)}</span>
        </span>
      </div>
      <h4>
        <span data-lang="en">{_esc(card.title.en)}</span>
        <span data-lang="zh">{_esc(card.title.zh)}</span>
      </h4>
      <p class="saved-article-content-organization-lead">
        <span data-lang="en">{_esc(_local_article_digest_excerpt(card.lead.en))}</span>
        <span data-lang="zh">{_esc(_local_article_digest_excerpt(card.lead.zh))}</span>
      </p>{chip_block}
      <a class="saved-article-content-organization-card-link" href="{_esc(href)}">
        <span data-lang="en">Open organized section</span>
        <span data-lang="zh">打开整理栏目</span>
      </a>
    </article>"""


def _render_saved_article_content_organization_chips(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
    chips = [_render_saved_article_content_organization_ref_chip(ref) for ref in card.references]
    if card.paragraph_indices:
        paragraph_count = len(card.paragraph_indices)
        paragraph_count_en = _count_label(paragraph_count, "paragraph", "paragraphs")
        chips.append(
            '<span class="saved-article-content-organization-chip">'
            f'<span data-lang="en">{_esc(paragraph_count_en)}</span>'
            f'<span data-lang="zh">{_esc(f"{paragraph_count} 个段落")}</span>'
            "</span>"
        )
    evidence = _render_saved_article_content_organization_evidence(
        card,
        href_prefix=href_prefix,
    )
    return "".join(chips) + evidence


def _render_saved_article_content_organization_evidence(
    card: RowOneSavedArticleContentOrganizationCard,
    *,
    href_prefix: str = "",
) -> str:
    links: list[str] = []
    seen: set[int] = set()
    for paragraph_index in card.paragraph_indices:
        if paragraph_index in seen:
            continue
        href = _safe_saved_article_content_organization_evidence_href(
            card.detail_path,
            paragraph_index,
        )
        if href is None:
            continue
        href = _prefixed_saved_article_content_organization_href(href, href_prefix)
        seen.add(paragraph_index)
        label_number = str(paragraph_index + 1)
        links.append(
            '<a class="saved-article-content-organization-evidence-link" '
            f'href="{_esc(href)}">'
            f'<span data-lang="en">Evidence paragraph {_esc(label_number)}</span>'
            f'<span data-lang="zh">证据段落 {_esc(label_number)}</span>'
            "</a>"
        )
        if len(links) >= SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT:
            break
    if not links:
        return ""
    return '<span class="saved-article-content-organization-evidence">' + "".join(links) + "</span>"


def _render_saved_article_content_organization_ref_chip(ref: RowOneReference) -> str:
    label = ref.label.strip() or ref.type.strip()
    return (
        '<span class="saved-article-content-organization-chip">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(label)}</span>"
        "</span>"
    )


def _safe_saved_article_content_organization_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment):
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"


def _prefixed_saved_article_content_organization_href(href: str, href_prefix: str) -> str:
    if not href_prefix:
        return href
    return f"{href_prefix}{href}"


def _safe_saved_article_content_organization_evidence_href(
    detail_path: object,
    paragraph_index: object,
) -> str | None:
    safe_section_href = _safe_saved_article_content_organization_href(detail_path)
    if safe_section_href is None:
        return None
    if not isinstance(paragraph_index, int) or isinstance(paragraph_index, bool):
        return None
    if paragraph_index < 0:
        return None
    path, _, _fragment = safe_section_href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    paragraph_fragment = f"local-article-paragraph-{paragraph_index + 1}"
    if not _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(paragraph_fragment):
        return None
    return f"{safe_path}#{paragraph_fragment}"


def _render_editorial_brief(editorial_brief: _EditorialBrief | None) -> str:
    if editorial_brief is None:
        return ""
    cards: list[str] = []
    for item in editorial_brief.items:
        has_body = normalize_row_one_paragraph(item.body.en) or normalize_row_one_paragraph(
            item.body.zh
        )
        if not has_body:
            continue
        rendered = _render_editorial_brief_card(item)
        if rendered:
            cards.append(rendered)
        if len(cards) >= EDITORIAL_BRIEF_MAX_ITEMS:
            break
    if not cards:
        return ""
    return f"""<section class="editorial-brief" aria-label="Editorial brief">
  <div class="editorial-brief-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Editorial Brief</span>
        <span data-lang="zh">编辑正文</span>
      </p>
      <h2>
        <span data-lang="en">Today, in context</span>
        <span data-lang="zh">今天的语境整理</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Short editorial reads assembled from local saved article text.</span>
      <span data-lang="zh">基于本地保存正文整理的短篇编辑解读。</span>
    </p>
  </div>
  <div class="editorial-brief-grid">
{"".join(cards)}
  </div>
</section>"""


def _render_editorial_brief_trail_item(label: LocalizedText, href: str | None) -> str:
    body = (
        f'<span data-lang="en">{_esc(label.en)}</span><span data-lang="zh">{_esc(label.zh)}</span>'
    )
    if href is None:
        return f'        <span class="editorial-brief-trail-item">{body}</span>'
    return f'        <a class="editorial-brief-trail-item" href="{_esc(href)}">{body}</a>'


def _render_editorial_brief_trail(
    items: Sequence[_EditorialBriefTrailItem],
) -> str:
    rendered_items: list[str] = []
    seen: set[tuple[str, str, str | None]] = set()
    for item in items:
        label = LocalizedText(
            en=_editorial_brief_display_text(item.label.en),
            zh=_editorial_brief_display_text(item.label.zh),
        )
        if not (label.en or label.zh):
            continue
        href = _safe_editorial_brief_href(item.href)
        key = (label.en.casefold(), label.zh.casefold(), href)
        if key in seen:
            continue
        seen.add(key)
        rendered_items.append(_render_editorial_brief_trail_item(label, href))
        if len(rendered_items) >= EDITORIAL_BRIEF_MAX_TRAIL_ITEMS:
            break
    if not rendered_items:
        return ""
    items_html = "\n".join(rendered_items)
    return f"""
      <div class="editorial-brief-trail" aria-label="Editorial source trail / 编辑来源线索">
{items_html}
      </div>"""


def _render_editorial_brief_card(item: _EditorialBriefItem) -> str:
    title = LocalizedText(
        en=_editorial_brief_display_text(item.title.en),
        zh=_editorial_brief_display_text(item.title.zh),
    )
    body = LocalizedText(
        en=_editorial_brief_body_excerpt(item.body.en),
        zh=_editorial_brief_body_excerpt(item.body.zh),
    )
    if not (body.en or body.zh):
        return ""
    meta = item.meta
    meta_block = ""
    if meta is not None:
        meta_text = LocalizedText(
            en=_editorial_brief_display_text(meta.en),
            zh=_editorial_brief_display_text(meta.zh),
        )
        if meta_text.en or meta_text.zh:
            meta_block = f"""
      <p class="editorial-brief-meta">
        <span data-lang="en">{_esc(meta_text.en)}</span>
        <span data-lang="zh">{_esc(meta_text.zh)}</span>
      </p>"""
    trail_block = _render_editorial_brief_trail(item.trail)
    action_block = ""
    href = _safe_editorial_brief_href(item.href)
    if href is not None:
        action_block = f"""
      <a class="editorial-brief-link" href="{_esc(href)}">
        <span data-lang="en">Read locally</span>
        <span data-lang="zh">本地阅读</span>
      </a>"""
    body_html = f"""      <h3>
        <span data-lang="en">{_esc(title.en)}</span>
        <span data-lang="zh">{_esc(title.zh)}</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(body.en)}</span>
        <span data-lang="zh">{_esc(body.zh)}</span>
      </p>{meta_block}{trail_block}{action_block}"""
    return f"""    <article class="editorial-brief-card">
{body_html}
    </article>"""


def _editorial_brief_body_excerpt(value: str) -> str:
    text = _editorial_brief_display_text(value)
    if len(text) <= EDITORIAL_BRIEF_BODY_EXCERPT_CHARS:
        return text
    return text[:EDITORIAL_BRIEF_BODY_EXCERPT_CHARS].rstrip() + "…"


def _editorial_brief_display_text(value: str) -> str:
    return normalize_row_one_paragraph(value)


def _safe_editorial_brief_href(href: object) -> str | None:
    text = str(href or "").strip()
    if not text:
        return None
    path, separator, fragment = text.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    if not separator:
        return str(safe_path)
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(
        fragment
    ) or _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment):
        return f"{safe_path}#{fragment}"
    return None


def _count_label(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _render_daily_local_intelligence_section(
    section: RowOneDailyLocalIntelligenceSection,
) -> str:
    cards = [_render_daily_local_intelligence_item(item) for item in section.items]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<article class="daily-local-intelligence-group">
  <p class="daily-local-intelligence-group-title">
    <span data-lang="en">{_esc(section.title.en)}</span>
    <span data-lang="zh">{_esc(section.title.zh)}</span>
  </p>
  <p>
    <span data-lang="en">{_esc(section.dek.en)}</span>
    <span data-lang="zh">{_esc(section.dek.zh)}</span>
  </p>
  {"".join(cards)}
</article>"""


def _render_daily_local_intelligence_item(item: RowOneDailyLocalIntelligenceItem) -> str:
    href = _safe_daily_local_intelligence_href(item.detail_path)
    meta = _daily_local_intelligence_meta(item)
    segments = _render_daily_local_intelligence_segments(item, detail_href=href)
    actions = _render_daily_local_intelligence_actions(item, detail_href=href)
    body = f"""<h3>
    <span data-lang="en">{_esc(item.title.en)}</span>
    <span data-lang="zh">{_esc(item.title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(item.body.en)}</span>
    <span data-lang="zh">{_esc(item.body.zh)}</span>
  </p>
  {segments}
  <div class="daily-local-intelligence-meta">{meta}</div>
  {actions}"""
    return f'<div class="daily-local-intelligence-card">{body}</div>'


def _render_daily_local_intelligence_actions(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    detail_href: str | None,
) -> str:
    if detail_href is None:
        return ""
    links = [(detail_href, "Open saved text", "打开本地正文")]
    for index in _daily_local_intelligence_paragraph_indices(item)[:3]:
        href = _daily_local_intelligence_paragraph_href(detail_href, index)
        if href is None:
            continue
        label = index + 1
        links.append((href, f"Evidence paragraph {label}", f"证据段落 {label}"))
    rendered = "".join(
        f'<a class="daily-local-intelligence-action" href="{_esc(href)}">'
        f'<span data-lang="en">{_esc(en)}</span>'
        f'<span data-lang="zh">{_esc(zh)}</span>'
        "</a>"
        for href, en, zh in links
    )
    if not rendered:
        return ""
    return f'<div class="daily-local-intelligence-actions">{rendered}</div>'


def _daily_local_intelligence_paragraph_indices(
    item: RowOneDailyLocalIntelligenceItem,
) -> list[int]:
    indices: list[int] = []
    seen: set[int] = set()
    for index in item.paragraph_indices:
        if index >= 0 and index not in seen:
            seen.add(index)
            indices.append(index)
    for segment in item.segments:
        for segment_item in segment.items:
            for index in segment_item.paragraph_indices:
                if index >= 0 and index not in seen:
                    seen.add(index)
                    indices.append(index)
    return indices


def _daily_local_intelligence_paragraph_href(
    detail_href: str,
    index: int,
) -> str | None:
    if index < 0:
        return None
    path = detail_href.split("#", 1)[0]
    return f"{path}#local-article-paragraph-{index + 1}"


def _render_daily_local_intelligence_segments(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    detail_href: str | None,
) -> str:
    segments = [
        _render_daily_local_intelligence_segment(segment, detail_href=detail_href)
        for segment in item.segments
    ]
    rendered = [segment for segment in segments if segment]
    if not rendered:
        return ""
    return f'<div class="daily-local-intelligence-segments">{"".join(rendered)}</div>'


def _render_daily_local_intelligence_segment(
    segment: RowOneDailyLocalIntelligenceSegment,
    *,
    detail_href: str | None,
) -> str:
    items = [
        _render_daily_local_intelligence_segment_item(
            segment_item,
            detail_href=detail_href,
        )
        for segment_item in segment.items
    ]
    rendered_items = [item for item in items if item]
    if not rendered_items:
        return ""
    body = ""
    if segment.body is not None and (segment.body.en.strip() or segment.body.zh.strip()):
        body = f"""<p class="daily-local-intelligence-segment-body">
      <span data-lang="en">{_esc(segment.body.en)}</span>
      <span data-lang="zh">{_esc(segment.body.zh)}</span>
    </p>"""
    return f"""<div class="daily-local-intelligence-segment">
    <p class="daily-local-intelligence-segment-title">
      <span data-lang="en">{_esc(segment.title.en)}</span>
      <span data-lang="zh">{_esc(segment.title.zh)}</span>
    </p>
    {body}
    <div class="daily-local-intelligence-segment-items">{"".join(rendered_items)}</div>
  </div>"""


def _render_daily_local_intelligence_segment_item(
    segment_item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    detail_href: str | None,
) -> str:
    body = ""
    if segment_item.body is not None and (
        segment_item.body.en.strip() or segment_item.body.zh.strip()
    ):
        body = f"""<p class="daily-local-intelligence-segment-item-body">
      <span data-lang="en">{_esc(segment_item.body.en)}</span>
      <span data-lang="zh">{_esc(segment_item.body.zh)}</span>
    </p>"""
    meta = _render_daily_local_intelligence_segment_meta(
        segment_item,
        detail_href=detail_href,
    )
    if not body and not meta:
        return ""
    return f"""<div class="daily-local-intelligence-segment-item">
    <p class="daily-local-intelligence-segment-item-label">
      <span data-lang="en">{_esc(segment_item.label.en)}</span>
      <span data-lang="zh">{_esc(segment_item.label.zh)}</span>
    </p>
    {body}
    {meta}
  </div>"""


def _render_daily_local_intelligence_segment_meta(
    segment_item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    detail_href: str | None,
) -> str:
    parts: list[str] = []
    for ref in segment_item.references:
        ref_text = " / ".join(value for value in (ref.name, ref.type, ref.label) if value)
        parts.append(
            f"<span>"
            f'<span data-lang="en">{_esc(ref_text)}</span>'
            f'<span data-lang="zh">{_esc(ref_text)}</span>'
            f"</span>"
        )
    for index in _valid_daily_local_intelligence_paragraph_indices(segment_item.paragraph_indices):
        paragraph_label = index + 1
        href = (
            _daily_local_intelligence_paragraph_href(detail_href, index)
            if detail_href is not None
            else None
        )
        label = (
            f'<span data-lang="en">Paragraph {paragraph_label}</span>'
            f'<span data-lang="zh">段落 {paragraph_label}</span>'
        )
        if href is None:
            parts.append(f"<span>{label}</span>")
        else:
            parts.append(
                f'<a class="daily-local-intelligence-paragraph-link" href="{_esc(href)}">'
                f"{label}</a>"
            )
    if not parts:
        return ""
    rendered = "".join(parts)
    return f'<div class="daily-local-intelligence-segment-meta">{rendered}</div>'


def _valid_daily_local_intelligence_paragraph_indices(indices: Sequence[int]) -> list[int]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if index < 0 or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _daily_local_intelligence_meta(item: RowOneDailyLocalIntelligenceItem) -> str:
    parts: list[tuple[str, str]] = []
    if item.source_names:
        sources = ", ".join(item.source_names)
        parts.append((sources, sources))
    if item.article_count:
        parts.append(
            (
                "1 article" if item.article_count == 1 else f"{item.article_count} articles",
                f"{item.article_count} 篇本地正文",
            )
        )
    if item.story_count:
        parts.append(
            (
                "1 story" if item.story_count == 1 else f"{item.story_count} stories",
                f"{item.story_count} 条故事",
            )
        )
    if item.evidence_count:
        parts.append(
            (
                "1 evidence link"
                if item.evidence_count == 1
                else f"{item.evidence_count} evidence links",
                f"{item.evidence_count} 条证据链接",
            )
        )
    if isinstance(item.heat_delta, int) and item.heat_delta > 0:
        parts.append((f"+{item.heat_delta} local delta", f"+{item.heat_delta} 本地增量"))
    return "".join(
        f'<span data-lang="en">{_esc(en)}</span><span data-lang="zh">{_esc(zh)}</span>'
        for en, zh in parts
    )


def _signal_synthesis_meta_label(
    *,
    label: str,
    story_count: int,
    evidence_count: int,
    heat_delta: int,
) -> str:
    story_label_en = "1 story" if story_count == 1 else f"{story_count} stories"
    story_label_zh = f"{story_count} 条故事"
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"+{heat_delta} local delta"
    heat_label_zh = f"+{heat_delta} 本地增量"
    return (
        f'<span data-lang="en">{_esc(label)}</span>'
        f'<span data-lang="zh">{_esc(label)}</span>'
        f'<span data-lang="en">{_esc(story_label_en)}</span>'
        f'<span data-lang="zh">{_esc(story_label_zh)}</span>'
        f'<span data-lang="en">{_esc(evidence_label_en)}</span>'
        f'<span data-lang="zh">{_esc(evidence_label_zh)}</span>'
        f'<span data-lang="en">{_esc(heat_label_en)}</span>'
        f'<span data-lang="zh">{_esc(heat_label_zh)}</span>'
    )


def _safe_signal_detail_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    return href if _validated_detail_relative_path(href) is not None else None


def _safe_daily_local_intelligence_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return href if _validated_detail_relative_path(href) is not None else None
    path, fragment = href.split("#", 1)
    if fragment != "local-article" and not _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment):
        return None
    return href if _validated_detail_relative_path(path) is not None else None


def _render_briefing_topics(app_payload: dict[str, object] | None) -> str:
    topics = _app_payload_briefing_topics(app_payload)[:4]
    if not topics:
        return ""
    topic_cards = "\n".join(_render_briefing_topic_card(topic) for topic in topics)
    return f"""<section id="briefing-topics" class="briefing-topics" aria-label="Briefing topics">
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
    href = (
        _safe_digest_detail_href(lead_story.get("detail_href")) if lead_story is not None else None
    )
    if href is None:
        href = "#main-content"
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


def _render_briefing_path(app_payload: dict[str, object] | None) -> str:
    blocks = _app_payload_digest_blocks(app_payload)
    excluded_story_ids = _read_first_story_ids(blocks)
    path_blocks = [
        block
        for block in blocks
        if block.get("key") in {"key_takeaways", "signals_to_watch"}
        and _block_cards(block, excluded_story_ids)
    ]
    if not path_blocks:
        return ""
    rendered_blocks = "\n".join(
        _render_briefing_path_block(block, excluded_story_ids) for block in path_blocks
    )
    return f"""<section id="briefing-path" class="briefing-path" aria-label="Briefing path">
  <div class="briefing-path-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Briefing Path</span>
        <span data-lang="zh">今日阅读路径</span>
      </p>
      <h2>
        <span data-lang="en">What to read next</span>
        <span data-lang="zh">接下来读什么</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">A compact reading path from existing daily digest blocks.</span>
      <span data-lang="zh">复用现有每日简报区块，整理后续阅读顺序。</span>
    </p>
  </div>
  <div class="briefing-path-grid">{rendered_blocks}</div>
</section>"""


def _render_briefing_path_block(
    block: dict[str, object],
    excluded_story_ids: set[str],
) -> str:
    title = _localized_topic_field(block, "title")
    dek = _localized_topic_field(block, "dek")
    cards = _block_cards(block, excluded_story_ids)[:5]
    rendered_cards = "\n".join(_render_briefing_path_card(card) for card in cards)
    return f"""<div class="briefing-path-block">
  <h3>
    <span data-lang="en">{_esc(title.en)}</span>
    <span data-lang="zh">{_esc(title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(dek.en)}</span>
    <span data-lang="zh">{_esc(dek.zh)}</span>
  </p>
  {rendered_cards}
</div>"""


def _render_briefing_path_card(card: dict[str, object]) -> str:
    href = _safe_digest_detail_href(card.get("detail_href")) or "#main-content"
    headline = _topic_localized_card_text(card, "headline")
    takeaway = _topic_localized_card_text(card, "editorial_takeaway")
    source_name = _esc(str(card.get("source_name") or "ROW ONE"))
    published_date = _esc(str(card.get("published_date") or "Undated"))
    evidence_count = _int_or_zero(card.get("evidence_count"))
    heat_delta = _int_or_zero(card.get("heat_delta"))
    evidence_label_en = (
        "1 evidence link" if evidence_count == 1 else f"{evidence_count} evidence links"
    )
    evidence_label_zh = f"{evidence_count} 条证据链接"
    heat_label_en = f"{heat_delta} heat" if heat_delta > 0 else "steady heat"
    heat_label_zh = f"{heat_delta} 热度" if heat_delta > 0 else "热度平稳"
    return f"""<a class="briefing-path-card" href="{_esc(href)}">
    <span class="briefing-path-meta">
      <span>{source_name}</span>
      <span>{published_date}</span>
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
      <span data-lang="en">{_esc(heat_label_en)}</span>
      <span data-lang="zh">{_esc(heat_label_zh)}</span>
    </span>
    <h4>
      <span data-lang="en">{_esc(headline.en)}</span>
      <span data-lang="zh">{_esc(headline.zh)}</span>
    </h4>
    <p>
      <span data-lang="en">{_esc(takeaway.en)}</span>
      <span data-lang="zh">{_esc(takeaway.zh)}</span>
    </p>
  </a>"""


def _int_or_zero(value: object) -> int:
    if value is None:
        return 0
    return int(value)


def _safe_digest_detail_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    return href if _validated_detail_relative_path(href) is not None else None


def _app_payload_digest_blocks(
    app_payload: dict[str, object] | None,
) -> list[dict[str, object]]:
    if app_payload is None:
        return []
    daily_digest = app_payload.get("daily_digest")
    if not isinstance(daily_digest, dict):
        return []
    blocks = daily_digest.get("blocks")
    if not isinstance(blocks, list):
        return []
    return [block for block in blocks if isinstance(block, dict)]


def _read_first_story_ids(blocks: list[dict[str, object]]) -> set[str]:
    read_first_block = next((block for block in blocks if block.get("key") == "read_first"), None)
    if read_first_block is None:
        return set()
    story_ids = read_first_block.get("story_ids")
    if not isinstance(story_ids, list):
        return set()
    return {str(story_id) for story_id in story_ids}


def _block_cards(
    block: dict[str, object],
    excluded_story_ids: set[str],
) -> list[dict[str, object]]:
    cards = block.get("cards")
    if not isinstance(cards, list):
        return []
    return [
        card
        for card in cards
        if isinstance(card, dict) and str(card.get("id")) not in excluded_story_ids
    ]


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
    value = topic.get(field)
    if value is None:
        return LocalizedText(zh="", en="")
    if isinstance(value, dict):
        zh = value.get("zh")
        en = value.get("en")
        return LocalizedText(
            zh=str(zh) if zh is not None else "",
            en=str(en) if en is not None else "",
        )
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


def _render_article_contents(*, include_local_article: bool = False) -> str:
    local_article_link = (
        """  <a href="#local-article">
    <span data-lang="en">Local Article</span>
    <span data-lang="zh">本地正文</span>
  </a>
"""
        if include_local_article
        else ""
    )
    return f"""<nav class="article-contents" aria-label="Article contents">
  <a href="#summary">
    <span data-lang="en">Summary</span>
    <span data-lang="zh">摘要</span>
  </a>
{local_article_link}  <a href="#why-it-matters">
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


def _render_detail_continue_reading(edition: RowOneEdition, story: RowOneStory) -> str:
    cards = [
        _render_detail_continue_reading_card(edition, related)
        for related in _detail_continue_reading_stories(edition, story)
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    rendered_cards = "".join(cards)
    return f"""    <section id="continue-reading" class="continue-reading"
      aria-label="Continue reading">
      <div class="continue-reading-header">
        <p class="story-section">
          <span data-lang="en">Continue Reading</span>
          <span data-lang="zh">继续阅读</span>
        </p>
        <h2>
          <span data-lang="en">Continue Reading</span>
          <span data-lang="zh">继续阅读</span>
        </h2>
      </div>
      <div class="continue-reading-grid">{rendered_cards}</div>
    </section>"""


def _detail_continue_reading_stories(
    edition: RowOneEdition,
    story: RowOneStory,
) -> list[RowOneStory]:
    candidates = [
        candidate
        for candidate in edition.stories
        if candidate.id != story.id and candidate.section_key == story.section_key
    ]
    candidates.extend(
        candidate
        for candidate in edition.stories
        if candidate.id != story.id and candidate.section_key != story.section_key
    )
    selected: list[RowOneStory] = []
    seen_paths: set[str] = set()
    for candidate in candidates:
        href = _detail_continue_reading_href(candidate.detail_path)
        if href is None or href in seen_paths:
            continue
        seen_paths.add(href)
        selected.append(candidate)
        if len(selected) >= DETAIL_CONTINUE_READING_MAX_ITEMS:
            break
    return selected


def _render_detail_continue_reading_card(
    edition: RowOneEdition,
    story: RowOneStory,
) -> str:
    href = _detail_continue_reading_href(story.detail_path)
    if href is None:
        return ""
    section_title = _section_title(edition, story.section_key)
    excerpt_en = _detail_continue_reading_excerpt(story.summary.en or story.editorial_takeaway.en)
    excerpt_zh = _detail_continue_reading_excerpt(story.summary.zh or story.editorial_takeaway.zh)
    return f"""        <article class="continue-reading-card">
          <a href="{_esc(href)}">
            <p class="continue-reading-section">
              <span data-lang="en">{_esc(section_title.en)}</span>
              <span data-lang="zh">{_esc(section_title.zh)}</span>
            </p>
            <p class="continue-reading-source">{_esc(story.source_name)}</p>
            <h3>{_esc(story.headline)}</h3>
            <p class="continue-reading-excerpt">
              <span data-lang="en">{_esc(excerpt_en)}</span>
              <span data-lang="zh">{_esc(excerpt_zh)}</span>
            </p>
          </a>
        </article>"""


def _detail_continue_reading_href(detail_path: str) -> str | None:
    pure_path = validated_row_one_detail_relative_path(detail_path)
    if pure_path is None:
        return None
    return pure_path.name


def _detail_continue_reading_excerpt(text: str) -> str:
    return _meta_description(
        _display_summary_text(text),
        limit=DETAIL_CONTINUE_READING_EXCERPT_CHARS,
    )


def _render_local_article(article: RowOneLocalArticle | None) -> str:
    if article is None:
        return ""
    paragraphs = _render_local_article_paragraphs(article)
    if not paragraphs:
        return ""
    title = article.title or "Source article"
    provenance = _render_local_article_provenance(article)
    brief = _render_local_article_brief(article)
    digest = _render_local_article_digest(article)
    reader = _render_local_article_reader(article)
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    paragraph_evidence = _render_local_article_paragraph_evidence(
        article,
        rendered_indices=rendered_indices,
    )
    article_map = _render_local_article_map(
        article,
        include_digest=bool(digest),
        include_reader=bool(reader),
        include_paragraph_evidence=bool(paragraph_evidence),
    )
    content_sections = _render_local_article_content_sections(
        article,
        rendered_indices=rendered_indices,
    )
    rendered_paragraphs = "\n".join(paragraphs)
    return f"""<section id="local-article" class="local-article">
      <h2>
        <span data-lang="en">Local Article</span>
        <span data-lang="zh">本地正文</span>
      </h2>
      <p class="local-article-source">
        <span data-lang="en">Saved from {_esc(article.source_name)}</span>
        <span data-lang="zh">本地保存自 {_esc(article.source_name)}</span>
      </p>
{provenance}
      <h3>{_esc(title)}</h3>
{article_map}
{paragraph_evidence}
{digest}
{reader}
{brief}
{content_sections}
      <div id="local-article-body" class="local-article-body">
{rendered_paragraphs}
      </div>
    </section>"""


def _render_local_article_provenance(article: RowOneLocalArticle) -> str:
    items = [
        _local_article_provenance_item("Source", "来源", article.source_name),
        _local_article_provenance_item(
            "Saved",
            "保存时间",
            _format_datetime(article.extracted_at),
        ),
        _local_article_provenance_item(
            "Text source",
            "正文来源",
            _local_article_body_source_label(article),
        ),
    ]
    if article.reason is not None and article.reason.strip():
        items.append(
            _local_article_provenance_item(
                "Fallback reason",
                "兜底原因",
                article.reason,
            )
        )
    if article.published_at is not None:
        items.append(
            _local_article_provenance_item(
                "Published",
                "发布时间",
                _format_datetime(article.published_at),
            )
        )
    items.extend(
        [
            _local_article_provenance_item(
                "Saved paragraphs",
                "保存段落",
                str(_local_article_saved_paragraph_count(article)),
            ),
            _local_article_provenance_item(
                "Organized sections",
                "整理栏目",
                str(len(article.content_sections)),
            ),
        ]
    )
    safe_url = _safe_external_url(article.url)
    if safe_url is not None:
        items.append(
            '<a class="local-article-provenance-item local-article-provenance-link" '
            f'href="{_esc(safe_url)}" target="_blank" rel="noopener">'
            '<span data-lang="en">Original URL</span>'
            '<span data-lang="zh">原文链接</span>'
            "</a>"
        )
    return f'      <div class="local-article-provenance">{"".join(items)}</div>'


def _local_article_body_source_label(article: RowOneLocalArticle) -> str:
    if article.body_source == "summary_fallback":
        return "ROW ONE summary fallback"
    if article.body_source == "skipped" or article.skipped:
        return "Skipped"
    return "Extracted article text"


def _local_article_provenance_item(label_en: str, label_zh: str, value: str) -> str:
    return (
        '<span class="local-article-provenance-item">'
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        f'<span class="local-article-provenance-value">{_esc(value)}</span>'
        "</span>"
    )


def _local_article_saved_paragraph_count(article: RowOneLocalArticle) -> int:
    return sum(1 for paragraph in article.paragraphs if paragraph.strip())


def _format_datetime(value: datetime) -> str:
    return value.strftime("%b %d, %Y")


def _render_local_article_reader(article: RowOneLocalArticle) -> str:
    items = _local_article_reader_items(article)
    if not items:
        return ""
    count = len(items)
    paragraph_label = "paragraph" if count == 1 else "paragraphs"
    meta_en = f"{count} saved {paragraph_label} from {article.source_name}"
    meta_zh = f"来自 {article.source_name} 的 {count} 个保存段落"
    rendered_items = "\n".join(
        _render_local_article_reader_item(
            position=position,
            paragraph_index=paragraph_index,
            excerpt_en=excerpt_en,
            excerpt_zh=excerpt_zh,
        )
        for position, (paragraph_index, excerpt_en, excerpt_zh) in enumerate(
            items,
            start=1,
        )
    )
    return f"""      <div id="local-article-reader" class="local-article-reader">
        <h4>
          <span data-lang="en">Saved Text Reader</span>
          <span data-lang="zh">保存正文阅读</span>
        </h4>
        <p class="local-article-reader-meta">
          <span data-lang="en">{_esc(meta_en)}</span>
          <span data-lang="zh">{_esc(meta_zh)}</span>
        </p>
        <ol class="local-article-reader-list" aria-label="Saved text paragraphs">
{rendered_items}
        </ol>
      </div>"""


def _local_article_reader_items(article: RowOneLocalArticle) -> list[tuple[int, str, str | None]]:
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    items: list[tuple[int, str, str | None]] = []
    for index, paragraph in enumerate(article.paragraphs):
        if not paragraph.strip():
            continue
        excerpt_en = _local_article_reader_excerpt(paragraph)
        excerpt_zh = None
        if aligned_zh:
            zh = aligned_zh[index]
            excerpt_zh = _local_article_reader_excerpt(zh) if zh.strip() else excerpt_en
        items.append((index, excerpt_en, excerpt_zh))
    return items


def _local_article_reader_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_READER_EXCERPT_CHARS,
    )


def _render_local_article_reader_item(
    *,
    position: int,
    paragraph_index: int,
    excerpt_en: str,
    excerpt_zh: str | None,
) -> str:
    href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
    number = f"{position:02d}"
    if excerpt_zh is None:
        excerpt = _esc(excerpt_en)
    else:
        excerpt = (
            f'<span data-lang="en">{_esc(excerpt_en)}</span>'
            f'<span data-lang="zh">{_esc(excerpt_zh)}</span>'
        )
    return f"""          <li>
            <a href="{_esc(href)}">
              <span class="local-article-reader-number">{_esc(number)}</span>
              <span class="local-article-reader-excerpt">{excerpt}</span>
            </a>
          </li>"""


def _render_local_article_digest(article: RowOneLocalArticle) -> str:
    if not _local_article_rendered_paragraph_indices(article):
        return ""
    cards = [
        card
        for card in (
            _render_local_article_digest_read_first(article),
            _render_local_article_digest_references(
                article,
                keys=("entities",),
                title_en="People & Brands",
                title_zh="品牌与人物",
            ),
            _render_local_article_digest_references(
                article,
                keys=("product_signals",),
                title_en="Products",
                title_zh="产品",
            ),
            _render_local_article_digest_source_map(article),
        )
        if card
    ]
    if not cards:
        return ""
    rendered_cards = "\n".join(cards)
    return (
        '      <div id="local-article-digest" class="local-article-digest" '
        'aria-label="Saved text digest">\n'
        f"""        <div class="local-article-digest-header">
          <h4>
            <span data-lang="en">Saved Text Digest</span>
            <span data-lang="zh">保存正文整理</span>
          </h4>
          <p>
            <span data-lang="en">A scan-first organization of the existing saved text.</span>
            <span data-lang="zh">基于现有保存正文的速览整理。</span>
          </p>
        </div>
        <div class="local-article-digest-grid">
{rendered_cards}
        </div>
      </div>"""
    )


def _render_local_article_digest_read_first(article: RowOneLocalArticle) -> str:
    takeaway = _local_article_digest_takeaway(article)
    if takeaway is None:
        return ""
    body_en, body_zh, paragraph_indices = takeaway
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    links = _render_local_article_digest_paragraph_links(
        paragraph_indices,
        rendered_indices=rendered_indices,
    )
    body = (
        f'            <span data-lang="en">{_esc(_local_article_digest_excerpt(body_en))}</span>\n'
        f'            <span data-lang="zh">{_esc(_local_article_digest_excerpt(body_zh))}</span>'
        if body_zh is not None
        else f"            {_esc(_local_article_digest_excerpt(body_en))}"
    )
    return f"""          <article class="local-article-digest-card">
            <h4>
              <span data-lang="en">Read First</span>
              <span data-lang="zh">先读</span>
            </h4>
            <p>
{body}
            </p>
{links}
          </article>"""


def _local_article_digest_takeaway(
    article: RowOneLocalArticle,
) -> tuple[str, str | None, list[int]] | None:
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    for section in article.content_sections:
        if section.key != "takeaways":
            continue
        for item in section.items:
            if item.body is None or not item.body.en.strip():
                continue
            return (
                item.body.en,
                item.body.zh if item.body.zh and item.body.zh.strip() else None,
                _valid_local_article_paragraph_indices(
                    item.paragraph_indices,
                    rendered_indices,
                ),
            )
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    for index, paragraph in enumerate(article.paragraphs):
        if not paragraph.strip():
            continue
        zh = aligned_zh[index] if aligned_zh and aligned_zh[index].strip() else None
        return (paragraph, zh, [index])
    return None


def _render_local_article_digest_references(
    article: RowOneLocalArticle,
    *,
    keys: tuple[str, ...],
    title_en: str,
    title_zh: str,
) -> str:
    references: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for section in article.content_sections:
        if section.key not in keys:
            continue
        for item in section.items:
            for ref in item.references:
                normalized_name = normalize_row_one_paragraph(ref.name)
                if not normalized_name:
                    continue
                dedupe_key = (
                    normalized_name.casefold(),
                    ref.type.strip().casefold(),
                    ref.label.strip().casefold(),
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                references.append(ref)
                if len(references) >= LOCAL_ARTICLE_DIGEST_MAX_REFERENCES:
                    break
            if len(references) >= LOCAL_ARTICLE_DIGEST_MAX_REFERENCES:
                break
        if len(references) >= LOCAL_ARTICLE_DIGEST_MAX_REFERENCES:
            break
    if not references:
        return ""
    items = "\n".join(
        f'              <li><span class="local-article-digest-chip">{_esc(ref.name)}</span></li>'
        for ref in references
    )
    return f"""          <article class="local-article-digest-card">
            <h4>
              <span data-lang="en">{_esc(title_en)}</span>
              <span data-lang="zh">{_esc(title_zh)}</span>
            </h4>
            <ul class="local-article-digest-list">
{items}
            </ul>
          </article>"""


def _render_local_article_digest_source_map(article: RowOneLocalArticle) -> str:
    saved_count = _local_article_saved_paragraph_count(article)
    section_count = len(article.content_sections)
    saved_label = "paragraph" if saved_count == 1 else "paragraphs"
    section_label = "section" if section_count == 1 else "sections"
    saved_text_en = f"{saved_count} saved {saved_label}"
    saved_text_zh = f"{saved_count} 个保存段落"
    section_text_en = f"{section_count} organized {section_label}"
    section_text_zh = f"{section_count} 个整理栏目"
    return f"""          <article class="local-article-digest-card">
            <h4>
              <span data-lang="en">Source Map</span>
              <span data-lang="zh">来源结构</span>
            </h4>
            <p>{_esc(article.source_name)}</p>
            <ul class="local-article-digest-list">
{_render_local_article_digest_count_chip(saved_text_en, saved_text_zh)}
{_render_local_article_digest_count_chip(section_text_en, section_text_zh)}
            </ul>
          </article>"""


def _render_local_article_digest_count_chip(label_en: str, label_zh: str) -> str:
    return (
        '              <li><span class="local-article-digest-chip">'
        f'<span data-lang="en">{_esc(label_en)}</span>'
        f'<span data-lang="zh">{_esc(label_zh)}</span>'
        "</span></li>"
    )


def _render_local_article_digest_paragraph_links(
    indices: list[int],
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(indices, rendered_indices)
    if not valid_indices:
        return ""
    links: list[str] = []
    for index in valid_indices:
        href = f"#{_local_article_paragraph_anchor(index)}"
        links.append(
            "              "
            f'<li><a href="{_esc(href)}">'
            f'<span data-lang="en">Paragraph {index + 1}</span>'
            f'<span data-lang="zh">段落 {index + 1}</span>'
            "</a></li>"
        )
    rendered_links = "\n".join(links)
    return f"""            <ul class="local-article-digest-link-list">
{rendered_links}
            </ul>"""


def _local_article_digest_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS,
    )


def _render_local_article_map(
    article: RowOneLocalArticle,
    *,
    include_digest: bool = False,
    include_reader: bool = False,
    include_paragraph_evidence: bool = False,
) -> str:
    if not article.brief_sections and not article.content_sections:
        return ""
    links = []
    if article.brief_sections:
        links.append(
            '<a href="#local-article-brief">'
            '<span data-lang="en">Brief</span>'
            '<span data-lang="zh">本地简报</span>'
            "</a>"
        )
    if include_paragraph_evidence:
        links.append(
            '<a href="#local-article-paragraph-evidence">'
            '<span data-lang="en">Evidence</span>'
            '<span data-lang="zh">线索</span>'
            "</a>"
        )
    if include_digest:
        links.append(
            '<a href="#local-article-digest">'
            '<span data-lang="en">Digest</span>'
            '<span data-lang="zh">整理</span>'
            "</a>"
        )
    if include_reader:
        links.append(
            '<a href="#local-article-reader">'
            '<span data-lang="en">Reader</span>'
            '<span data-lang="zh">阅读</span>'
            "</a>"
        )
    for position, section in enumerate(article.content_sections, start=1):
        anchor = f"#{_local_article_content_section_anchor(position)}"
        links.append(
            f'<a href="{_esc(anchor)}">'
            f'<span data-lang="en">{_esc(section.title.en)}</span>'
            f'<span data-lang="zh">{_esc(section.title.zh)}</span>'
            "</a>"
        )
    links.append(
        '<a href="#local-article-body">'
        '<span data-lang="en">Saved text</span>'
        '<span data-lang="zh">保存正文</span>'
        "</a>"
    )
    return (
        '      <nav class="local-article-map" aria-label="ROW ONE local article map">\n'
        + "\n".join(f"        {link}" for link in links)
        + "\n      </nav>"
    )


def _render_local_article_brief(article: RowOneLocalArticle) -> str:
    cards = []
    for section in article.brief_sections:
        cards.append(
            f"""        <article class="local-article-brief-card">
          <h4>
            <span data-lang="en">{_esc(section.title.en)}</span>
            <span data-lang="zh">{_esc(section.title.zh)}</span>
          </h4>
          <p>
            <span data-lang="en">{_esc(section.body.en)}</span>
            <span data-lang="zh">{_esc(section.body.zh)}</span>
          </p>
        </article>"""
        )
    if not cards:
        return ""
    rendered_cards = "\n".join(cards)
    return (
        '      <div id="local-article-brief" class="local-article-brief" '
        'aria-label="ROW ONE brief">\n'
        f"{rendered_cards}\n"
        "      </div>"
    )


def _render_local_article_content_sections(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    rendered_sections = []
    for position, section in enumerate(article.content_sections, start=1):
        section_anchor = _local_article_content_section_anchor(position)
        section_parts = [
            f'        <article id="{_esc(section_anchor)}" class="local-article-content-card">',
            "          <h4>",
            f'            <span data-lang="en">{_esc(section.title.en)}</span>',
            f'            <span data-lang="zh">{_esc(section.title.zh)}</span>',
            "          </h4>",
        ]
        if section.body is not None:
            section_parts.extend(
                [
                    "          <p>",
                    f'            <span data-lang="en">{_esc(section.body.en)}</span>',
                    f'            <span data-lang="zh">{_esc(section.body.zh)}</span>',
                    "          </p>",
                ]
            )
        rendered_items = "\n".join(
            _render_local_article_content_item(
                item,
                article=article,
                rendered_indices=rendered_indices,
            )
            for item in section.items
        )
        if rendered_items:
            section_parts.extend(
                [
                    '          <ul class="local-article-content-items">',
                    rendered_items,
                    "          </ul>",
                ]
            )
        section_parts.append("        </article>")
        rendered_sections.append("\n".join(section_parts))
    if not rendered_sections:
        return ""
    rendered = "\n".join(rendered_sections)
    return (
        '      <div class="local-article-content-sections" '
        'aria-label="ROW ONE local article content">\n'
        f"{rendered}\n"
        "      </div>"
    )


def _render_local_article_content_item(
    item: RowOneLocalArticleContentItem,
    *,
    article: RowOneLocalArticle,
    rendered_indices: set[int],
) -> str:
    item_parts = [
        "            <li>",
        "              <strong>",
        f'                <span data-lang="en">{_esc(item.label.en)}</span>',
        f'                <span data-lang="zh">{_esc(item.label.zh)}</span>',
        "              </strong>",
    ]
    if item.body is not None:
        item_parts.extend(
            [
                "              <p>",
                f'                <span data-lang="en">{_esc(item.body.en)}</span>',
                f'                <span data-lang="zh">{_esc(item.body.zh)}</span>',
                "              </p>",
            ]
        )
    previews = _render_local_article_content_paragraph_previews(
        article,
        item,
        rendered_indices=rendered_indices,
    )
    if previews:
        item_parts.append(previews)
    paragraphs = _render_local_article_paragraph_links(
        item.paragraph_indices,
        rendered_indices=rendered_indices,
    )
    if paragraphs:
        item_parts.append(paragraphs)
    refs = _render_local_article_content_references(item.references)
    if refs:
        item_parts.append(refs)
    item_parts.append("            </li>")
    return "\n".join(item_parts)


def _render_local_article_content_paragraph_previews(
    article: RowOneLocalArticle,
    item: RowOneLocalArticleContentItem,
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(
        item.paragraph_indices,
        rendered_indices,
    )[:LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS]
    if not valid_indices:
        return ""
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    previews: list[str] = []
    for index in valid_indices:
        en = _local_article_content_preview_excerpt(article.paragraphs[index])
        href = f"#{_local_article_paragraph_anchor(index)}"
        label_en = f"Saved paragraph {index + 1}"
        label_zh = f"保存段落 {index + 1}"
        if aligned_zh and aligned_zh[index].strip():
            zh = _local_article_content_preview_excerpt(aligned_zh[index])
            body = f'<span data-lang="en">{_esc(en)}</span><span data-lang="zh">{_esc(zh)}</span>'
        else:
            body = _esc(en)
        previews.append(
            "            "
            f'<li class="local-article-content-preview">'
            f'<a href="{_esc(href)}">'
            f'<span data-lang="en">{_esc(label_en)}</span>'
            f'<span data-lang="zh">{_esc(label_zh)}</span>'
            f"<span>{body}</span>"
            "</a></li>"
        )
    return (
        '          <ul class="local-article-content-previews" '
        'aria-label="Saved paragraph previews">\n' + "\n".join(previews) + "\n          </ul>"
    )


def _local_article_content_preview_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS,
    )


def _local_article_rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}


def _local_article_paragraph_anchor(index: int) -> str:
    # paragraph_indices are zero-based; fragment IDs are one-based for readers.
    return f"local-article-paragraph-{index + 1}"


def _local_article_content_section_anchor(position: int) -> str:
    return f"local-article-content-section-{position}"


def _valid_local_article_paragraph_indices(
    indices: list[int],
    rendered_indices: set[int],
) -> list[int]:
    # Both inputs use original zero-based RowOneLocalArticle.paragraphs positions.
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if index not in rendered_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _strict_valid_local_article_paragraph_indices(
    indices: Sequence[object],
    rendered_indices: set[int],
) -> list[int]:
    # Avoid bool/int coercion before building fragment links.
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if not isinstance(index, int) or isinstance(index, bool):
            continue
        if index not in rendered_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _local_article_paragraph_evidence_entries(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> tuple[_LocalArticleParagraphEvidenceEntry, ...]:
    mapped: dict[int, list[_LocalArticleParagraphEvidenceItem]] = {}
    seen_items: dict[int, set[tuple[object, ...]]] = {}
    for section_position, section in enumerate(article.content_sections, start=1):
        for item in section.items:
            valid_indices = _strict_valid_local_article_paragraph_indices(
                item.paragraph_indices,
                rendered_indices,
            )
            if not valid_indices:
                continue
            evidence_item = _local_article_paragraph_evidence_item(
                section=section,
                section_position=section_position,
                item=item,
            )
            dedupe_key = _local_article_paragraph_evidence_item_key(evidence_item)
            for index in valid_indices:
                item_keys = seen_items.setdefault(index, set())
                if dedupe_key in item_keys:
                    continue
                item_keys.add(dedupe_key)
                mapped.setdefault(index, []).append(evidence_item)
    if not mapped:
        return ()

    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    entries: list[_LocalArticleParagraphEvidenceEntry] = []
    for index in sorted(mapped):
        excerpt_en = _local_article_paragraph_evidence_excerpt(article.paragraphs[index])
        excerpt_zh = (
            _local_article_paragraph_evidence_excerpt(aligned_zh[index])
            if aligned_zh and aligned_zh[index].strip()
            else excerpt_en
        )
        entries.append(
            _LocalArticleParagraphEvidenceEntry(
                paragraph_index=index,
                excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh),
                items=tuple(mapped[index][:LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ITEMS]),
            )
        )
        if len(entries) >= LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ROWS:
            break
    return tuple(entries)


def _local_article_paragraph_evidence_item(
    *,
    section: RowOneLocalArticleContentSection,
    section_position: int,
    item: RowOneLocalArticleContentItem,
) -> _LocalArticleParagraphEvidenceItem:
    refs: list[RowOneReference] = []
    seen_refs: set[tuple[str, str, str]] = set()
    for ref in item.references:
        dedupe_key = (
            normalize_row_one_paragraph(ref.name).casefold(),
            normalize_row_one_paragraph(ref.type).casefold(),
            normalize_row_one_paragraph(ref.label).casefold(),
        )
        if dedupe_key in seen_refs:
            continue
        seen_refs.add(dedupe_key)
        refs.append(ref)
        if len(refs) >= LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_REFS:
            break
    return _LocalArticleParagraphEvidenceItem(
        section_position=section_position,
        section_title=section.title,
        item_label=item.label,
        item_body=item.body,
        references=tuple(refs),
    )


def _local_article_paragraph_evidence_item_key(
    item: _LocalArticleParagraphEvidenceItem,
) -> tuple[object, ...]:
    return (
        item.section_position,
        normalize_row_one_paragraph(item.section_title.en).casefold(),
        normalize_row_one_paragraph(item.section_title.zh).casefold(),
        normalize_row_one_paragraph(item.item_label.en).casefold(),
        normalize_row_one_paragraph(item.item_label.zh).casefold(),
        normalize_row_one_paragraph(item.item_body.en).casefold() if item.item_body else "",
        normalize_row_one_paragraph(item.item_body.zh).casefold() if item.item_body else "",
        tuple(
            (
                normalize_row_one_paragraph(ref.name).casefold(),
                normalize_row_one_paragraph(ref.type).casefold(),
                normalize_row_one_paragraph(ref.label).casefold(),
            )
            for ref in item.references
        ),
    )


def _local_article_paragraph_evidence_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_EXCERPT_CHARS,
    )


def _local_article_paragraph_evidence_body(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_BODY_CHARS,
    )


def _local_article_paragraph_evidence_body_text(body: LocalizedText) -> LocalizedText:
    en = _local_article_paragraph_evidence_body(body.en)
    zh = _local_article_paragraph_evidence_body(body.zh) if body.zh.strip() else en
    return LocalizedText(en=en, zh=zh)


def _render_local_article_paragraph_evidence(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    entries = _local_article_paragraph_evidence_entries(
        article,
        rendered_indices=rendered_indices,
    )
    if not entries:
        return ""
    rendered_entries = "\n".join(
        _render_local_article_paragraph_evidence_entry(entry) for entry in entries
    )
    return (
        '      <div id="local-article-paragraph-evidence" '
        'class="local-article-paragraph-evidence" '
        'aria-label="Saved paragraph evidence">\n'
        f"""        <div class="local-article-paragraph-evidence-header">
          <h4>
            <span data-lang="en">Saved Paragraph Evidence</span>
            <span data-lang="zh">本地段落线索</span>
          </h4>
          <p>
            <span data-lang="en">Saved paragraphs used by the organized ROW ONE reading path.</span>
            <span data-lang="zh">被 ROW ONE 正文整理引用的本地保存段落。</span>
          </p>
        </div>
        <div class="local-article-paragraph-evidence-grid">
{rendered_entries}
        </div>
      </div>"""
    )


def _render_local_article_paragraph_evidence_entry(
    entry: _LocalArticleParagraphEvidenceEntry,
) -> str:
    paragraph_number = entry.paragraph_index + 1
    paragraph_href = f"#{_local_article_paragraph_anchor(entry.paragraph_index)}"
    supports = "\n".join(
        _render_local_article_paragraph_evidence_support(item) for item in entry.items
    )
    return f"""          <article class="local-article-paragraph-evidence-row">
            <a class="local-article-paragraph-evidence-link" href="{_esc(paragraph_href)}">
              <span data-lang="en">Paragraph {paragraph_number}</span>
              <span data-lang="zh">段落 {paragraph_number}</span>
            </a>
            <p class="local-article-paragraph-evidence-excerpt">
              <span data-lang="en">{_esc(entry.excerpt.en)}</span>
              <span data-lang="zh">{_esc(entry.excerpt.zh)}</span>
            </p>
            <div class="local-article-paragraph-evidence-supports">
{supports}
            </div>
          </article>"""


def _render_local_article_paragraph_evidence_support(
    item: _LocalArticleParagraphEvidenceItem,
) -> str:
    section_href = f"#{_local_article_content_section_anchor(item.section_position)}"
    body = ""
    if item.item_body is not None:
        body_text = _local_article_paragraph_evidence_body_text(item.item_body)
        body = (
            "                <p>"
            f'<span data-lang="en">{_esc(body_text.en)}</span>'
            f'<span data-lang="zh">{_esc(body_text.zh)}</span>'
            "</p>\n"
        )
    refs = "".join(_render_local_article_paragraph_evidence_ref(ref) for ref in item.references)
    refs_html = f"                <div>{refs}</div>\n" if refs else ""
    return f"""              <div class="local-article-paragraph-evidence-support">
                <a href="{_esc(section_href)}">
                  <span data-lang="en">{_esc(item.section_title.en)}</span>
                  <span data-lang="zh">{_esc(item.section_title.zh)}</span>
                </a>
                <strong>
                  <span data-lang="en">{_esc(item.item_label.en)}</span>
                  <span data-lang="zh">{_esc(item.item_label.zh)}</span>
                </strong>
{body}{refs_html}              </div>"""


def _render_local_article_paragraph_evidence_ref(ref: RowOneReference) -> str:
    label = f"{ref.name} ({ref.type} / {ref.label})"
    return f'<span class="local-article-paragraph-evidence-ref">{_esc(label)}</span>'


def _render_local_article_paragraph_links(
    indices: list[int],
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(indices, rendered_indices)
    if not valid_indices:
        return ""
    en_links: list[str] = []
    zh_links: list[str] = []
    for index in valid_indices:
        href = f"#{_local_article_paragraph_anchor(index)}"
        en_links.append(f'<a href="{_esc(href)}">Paragraph {index + 1}</a>')
        zh_links.append(f'<a href="{_esc(href)}">段落 {index + 1}</a>')
    en = ", ".join(en_links)
    zh = "、".join(zh_links)
    css_class = "local-article-content-meta local-article-content-paragraph-links"
    return f"""              <p class="{css_class}">
                <span data-lang="en">{en}</span>
                <span data-lang="zh">{zh}</span>
              </p>"""


def _render_local_article_content_references(references: list[RowOneReference]) -> str:
    if not references:
        return ""
    en_refs = ", ".join(f"{ref.name} ({ref.type} / {ref.label})" for ref in references)
    zh_refs = "，".join(f"{ref.name}（{ref.type} / {ref.label}）" for ref in references)
    return f"""              <p class="local-article-content-meta">
                <span data-lang="en">Refs: {_esc(en_refs)}</span>
                <span data-lang="zh">引用：{_esc(zh_refs)}</span>
              </p>"""


def _render_local_article_paragraphs(article: RowOneLocalArticle) -> list[str]:
    source_paragraphs = [paragraph for paragraph in article.paragraphs if paragraph.strip()]
    if not source_paragraphs:
        return []
    if len(article.paragraphs_zh) != len(article.paragraphs):
        rendered: list[str] = []
        for index, paragraph in enumerate(article.paragraphs):
            if not paragraph.strip():
                continue
            anchor = _local_article_paragraph_anchor(index)
            rendered.append(f'      <p id="{_esc(anchor)}">{_esc(paragraph)}</p>')
        return rendered
    rendered: list[str] = []
    for index, (paragraph_en, paragraph_zh) in enumerate(
        zip(article.paragraphs, article.paragraphs_zh, strict=True)
    ):
        if not paragraph_en.strip():
            continue
        zh = paragraph_zh if paragraph_zh.strip() else paragraph_en
        anchor = _local_article_paragraph_anchor(index)
        rendered.append(
            f'      <p id="{_esc(anchor)}">'
            f'<span data-lang="en">{_esc(paragraph_en)}</span>'
            f'<span data-lang="zh">{_esc(zh)}</span>'
            "</p>"
        )
    return rendered


def _render_detail_signal_briefing(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str:
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    safe_evidence_count = _safe_evidence_count(story.evidence)
    evidence_label_en = (
        "1 safe evidence link"
        if safe_evidence_count == 1
        else f"{safe_evidence_count} safe evidence links"
    )
    evidence_label_zh = f"{safe_evidence_count} 条安全线索"
    references = _render_detail_signal_briefing_references(story, local_article)
    local_cues = _render_detail_signal_briefing_cues(local_article)
    return f"""<section class="detail-signal-briefing" aria-label="Signal briefing">
  <div class="detail-signal-briefing-header">
    <p>
      <span data-lang="en">Signal Briefing</span>
      <span data-lang="zh">信号简报</span>
    </p>
    <h2>
      <span data-lang="en">What To Know</span>
      <span data-lang="zh">重点整理</span>
    </h2>
  </div>
  <div class="detail-signal-briefing-grid">
    <article class="detail-signal-briefing-card">
      <h3>
        <span data-lang="en">Signal</span>
        <span data-lang="zh">信号</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(summary_en)}</span>
        <span data-lang="zh">{_esc(summary_zh)}</span>
      </p>
      <p class="detail-signal-briefing-meta">
        <span>{_esc(story.source_name)}</span>
        <span data-lang="en">{_esc(evidence_label_en)}</span>
        <span data-lang="zh">{_esc(evidence_label_zh)}</span>
      </p>
    </article>
    <article class="detail-signal-briefing-card">
      <h3>
        <span data-lang="en">Context</span>
        <span data-lang="zh">背景</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(story.signal_context.en)}</span>
        <span data-lang="zh">{_esc(story.signal_context.zh)}</span>
      </p>
    </article>
    <article class="detail-signal-briefing-card">
      <h3>
        <span data-lang="en">References</span>
        <span data-lang="zh">引用对象</span>
      </h3>
      {references}
    </article>
  </div>
{local_cues}
</section>"""


def _render_detail_signal_briefing_references(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str:
    references = _detail_signal_briefing_references(story, local_article)
    if not references:
        return (
            '<p><span data-lang="en">No tracked references yet.</span>'
            '<span data-lang="zh">暂无跟踪引用对象。</span></p>'
        )
    return "\n      ".join(_render_detail_signal_briefing_ref(ref) for ref in references)


def _detail_signal_briefing_references(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> list[RowOneReference]:
    references: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()

    def add(ref: RowOneReference) -> None:
        if len(references) >= DETAIL_SIGNAL_BRIEFING_MAX_REFS:
            return
        normalized_name = normalize_row_one_paragraph(ref.name)
        if not normalized_name:
            return
        key = (
            normalized_name.casefold(),
            ref.type.strip().casefold(),
            ref.label.strip().casefold(),
        )
        if key in seen:
            return
        seen.add(key)
        references.append(ref)

    for ref in story.entity_refs:
        add(ref)
    for ref in story.designer_refs:
        add(ref)
    for ref in story.product_refs:
        add(ref)
    if local_article is not None:
        for section in local_article.content_sections:
            for item in section.items:
                for ref in item.references:
                    add(ref)
                    if len(references) >= DETAIL_SIGNAL_BRIEFING_MAX_REFS:
                        return references
    return references


def _render_detail_signal_briefing_ref(ref: RowOneReference) -> str:
    return f'<span class="detail-signal-briefing-ref">{_esc(ref.name)}</span>'


def _render_detail_signal_briefing_cues(article: RowOneLocalArticle | None) -> str:
    cues = _detail_signal_briefing_cues(article)
    if not cues:
        return ""
    rendered = "\n".join(_render_detail_signal_briefing_cue(cue) for cue in cues)
    return f"""  <div class="detail-signal-briefing-cues">
    <h3>
      <span data-lang="en">Local Article Cues</span>
      <span data-lang="zh">本地正文线索</span>
    </h3>
    <div class="detail-signal-briefing-cue-grid">
{rendered}
    </div>
  </div>"""


def _detail_signal_briefing_cues(
    article: RowOneLocalArticle | None,
) -> list[tuple[LocalizedText, LocalizedText, int | None]]:
    if article is None:
        return []
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    content_cues: list[tuple[LocalizedText, LocalizedText, int | None]] = []
    for section in article.content_sections:
        body = section.body
        if body is None:
            body = next((item.body for item in section.items if item.body is not None), None)
        if body is None:
            continue
        content_cues.append(
            (
                section.title,
                body,
                _first_valid_local_article_paragraph_index(section, rendered_indices),
            )
        )
    cues: list[tuple[LocalizedText, LocalizedText, int | None]] = []
    max_brief_cues = DETAIL_SIGNAL_BRIEFING_MAX_CUES
    if content_cues:
        max_brief_cues -= 1
    for section in article.brief_sections:
        cues.append((section.title, section.body, None))
        if len(cues) >= max_brief_cues:
            break
    for cue in content_cues:
        cues.append(cue)
        if len(cues) >= DETAIL_SIGNAL_BRIEFING_MAX_CUES:
            break
    return cues


def _first_valid_local_article_paragraph_index(
    section: RowOneLocalArticleContentSection,
    rendered_indices: set[int],
) -> int | None:
    indices: list[int] = []
    for item in section.items:
        indices.extend(item.paragraph_indices)
    valid = _valid_local_article_paragraph_indices(indices, rendered_indices)
    return valid[0] if valid else None


def _render_detail_signal_briefing_cue(
    cue: tuple[LocalizedText, LocalizedText, int | None],
) -> str:
    title, body, paragraph_index = cue
    paragraph_link = ""
    if paragraph_index is not None:
        href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
        paragraph_link = (
            f'      <a href="{_esc(href)}">'
            f'<span data-lang="en">Paragraph {paragraph_index + 1}</span>'
            f'<span data-lang="zh">段落 {paragraph_index + 1}</span>'
            "</a>\n"
        )
    return f"""      <article class="detail-signal-briefing-cue">
        <h4>
          <span data-lang="en">{_esc(title.en)}</span>
          <span data-lang="zh">{_esc(title.zh)}</span>
        </h4>
        <p>
          <span data-lang="en">{_esc(body.en)}</span>
          <span data-lang="zh">{_esc(body.zh)}</span>
        </p>
{paragraph_link}      </article>"""


def _render_detail_information_map(story: RowOneStory, section_title: LocalizedText) -> str:
    published = _published_label(story)
    safe_evidence_count = _safe_evidence_count(story.evidence)
    evidence_label_en = (
        f"{safe_evidence_count} evidence link"
        if safe_evidence_count == 1
        else f"{safe_evidence_count} evidence links"
    )
    evidence_label_zh = f"{safe_evidence_count} 条线索"
    heat_delta = f"{story.heat_delta:+d}" if isinstance(story.heat_delta, int) else "n/a"
    return f"""<section class="detail-information-map" aria-label="Detail information map">
  <div class="detail-information-map-header">
    <p>
      <span data-lang="en">Structured story scan</span>
      <span data-lang="zh">结构化故事速览</span>
    </p>
    <h2>
      <span data-lang="en">Detail Information Map</span>
      <span data-lang="zh">详情信息地图</span>
    </h2>
  </div>
  <div class="detail-information-map-grid">
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Story Context</span>
        <span data-lang="zh">故事背景</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(section_title.en)}</span>
        <span data-lang="zh">{_esc(section_title.zh)}</span>
      </p>
      <p>{_esc(story.source_name)}</p>
      <p>
        <span data-lang="en">{_esc(published.en)}</span>
        <span data-lang="zh">{_esc(published.zh)}</span>
      </p>
    </article>
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Signal Shape</span>
        <span data-lang="zh">信号形态</span>
      </h3>
      <p>{_esc(_story_type_label(story))}</p>
      <p>{_esc(_joined_tags(story))}</p>
      <p>
        <span data-lang="en">Heat delta</span>
        <span data-lang="zh">热度变化</span>: {_esc(heat_delta)}
      </p>
    </article>
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Evidence</span>
        <span data-lang="zh">证据</span>
      </h3>
      <p>
        <span data-lang="en">{_esc(evidence_label_en)}</span>
        <span data-lang="zh">{_esc(evidence_label_zh)}</span>
      </p>
      <p>{_esc(story.source_name)}</p>
    </article>
    <article class="detail-information-map-card">
      <h3>
        <span data-lang="en">Read Order</span>
        <span data-lang="zh">阅读顺序</span>
      </h3>
      <p>
        <a href="#summary">
          <span data-lang="en">Summary</span>
          <span data-lang="zh">摘要</span>
        </a>
      </p>
      <p>
        <a href="#why-it-matters">
          <span data-lang="en">Why It Matters</span>
          <span data-lang="zh">为什么重要</span>
        </a>
      </p>
      <p>
        <a href="#signal-context">
          <span data-lang="en">Signal Context</span>
          <span data-lang="zh">信号背景</span>
        </a>
      </p>
      <p>
        <a href="#evidence-trail">
          <span data-lang="en">Evidence Trail</span>
          <span data-lang="zh">来源线索</span>
        </a>
      </p>
    </article>
  </div>
</section>"""


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


def _display_summary_text(text: str) -> str:
    fallback = normalize_row_one_paragraph(text)
    cleaned = clean_row_one_text(protect_literal_angle_tokens(text))
    sentences = clean_row_one_sentences(cleaned, set())
    display_text = normalize_row_one_paragraph(" ".join(sentences))
    return restore_literal_angle_tokens(display_text) or fallback


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


def _render_lead_story(
    story: RowOneStory,
    section_title: LocalizedText,
    *,
    local_article: RowOneLocalArticle | None = None,
) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    local_article_href = _local_article_href(story, local_article)
    lead_action_href = _esc(local_article_href) if local_article_href else detail_href
    lead_action_label = (
        LocalizedText(en="Read saved article", zh="阅读本地正文")
        if local_article_href
        else LocalizedText(en="Read the brief", zh="查看详情")
    )
    lead_action_class = (
        "lead-story-link local-read-action" if local_article_href else "lead-story-link"
    )
    local_read_path = _render_homepage_local_read_path(story, local_article)
    visual = _render_story_visual(story, section_title, context="lead-story-visual")
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
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
        <span data-lang="en">{_esc(summary_en)}</span>
        <span data-lang="zh">{_esc(summary_zh)}</span>
      </p>
      {local_read_path}
      <a class="{_esc(lead_action_class)}" href="{lead_action_href}">
        <span data-lang="en">{_esc(lead_action_label.en)}</span>
        <span data-lang="zh">{_esc(lead_action_label.zh)}</span>
      </a>
    </div>
  </div>
</section>"""


def _render_section(
    edition: RowOneEdition,
    section_key: RowOneSectionKey,
    *,
    local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None,
) -> str:
    section = next(section for section in edition.sections if section.key == section_key)
    stories = edition.section_stories(section_key)
    local_articles_by_story_id = local_articles_by_story_id or {}
    cards = "\n".join(
        _render_story_card(
            story,
            section.title,
            local_article=local_articles_by_story_id.get(story.id),
        )
        for story in stories
    )
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
    *,
    local_article: RowOneLocalArticle | None = None,
) -> str:
    detail_href = _internal_detail_href(story.detail_path)
    local_article_href = _local_article_href(story, local_article)
    story_action_href = _esc(local_article_href) if local_article_href else detail_href
    story_action_label = (
        LocalizedText(en="Read saved article", zh="阅读本地正文")
        if local_article_href
        else LocalizedText(en="Read brief", zh="阅读简报")
    )
    story_action_class = (
        "story-detail-link local-read-action" if local_article_href else "story-detail-link"
    )
    local_read_path = _render_homepage_local_read_path(story, local_article)
    published = _published_label(story)
    evidence_count = sum(1 for link in story.evidence if _safe_external_url(link.url) is not None)
    source_name = _esc(story.source_name)
    evidence_label_en = "1 source" if evidence_count == 1 else f"{evidence_count} sources"
    evidence_label_zh = f"{evidence_count} 条来源"
    summary_en = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
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
      <span data-lang="en">{_esc(summary_en)}</span>
      <span data-lang="zh">{_esc(summary_zh)}</span>
    </p>
    {local_read_path}
  </div>
  <div class="story-card-footer">
    <span class="story-evidence-count">
      <span data-lang="en">{_esc(evidence_label_en)}</span>
      <span data-lang="zh">{_esc(evidence_label_zh)}</span>
    </span>
    <a class="{_esc(story_action_class)}" href="{story_action_href}">
      <span data-lang="en">{_esc(story_action_label.en)}</span>
      <span data-lang="zh">{_esc(story_action_label.zh)}</span>
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


def _story_type_label(story: RowOneStory) -> str:
    return story.story_type.replace("_", " ").title()


def _joined_tags(story: RowOneStory) -> str:
    return ", ".join(story.tags) if story.tags else "No tags"


def _safe_evidence_count(evidence: list[RowOneLink]) -> int:
    return sum(1 for link in evidence if _safe_external_url(link.url) is not None)


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


def _source_action_link(url: str | None) -> str:
    safe_url = _safe_external_url(url)
    if safe_url is None:
        return ""
    return f"""<p class="source-action">
  <a class="source-action-link" href="{_esc(safe_url)}" target="_blank" rel="noopener">
    <span data-lang="en">Open Source Article</span>
    <span data-lang="zh">打开原文</span>
  </a>
</p>"""


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


def _usable_local_article_paragraph_count(article: RowOneLocalArticle | None) -> int:
    if article is None:
        return 0
    return sum(1 for paragraph in article.paragraphs if normalize_row_one_paragraph(paragraph))


def _local_article_href(
    story: RowOneStory,
    article: RowOneLocalArticle | None,
) -> str | None:
    if _usable_local_article_paragraph_count(article) <= 0:
        return None
    detail_path = _validated_detail_relative_path(story.detail_path)
    if detail_path is None:
        return None
    return f"{detail_path}#local-article"


def _local_read_count_label(count: int) -> LocalizedText:
    paragraph_label = "paragraph" if count == 1 else "paragraphs"
    return LocalizedText(en=f"{count} saved {paragraph_label}", zh=f"{count} 个保存段落")


def _render_homepage_local_read_path(
    story: RowOneStory,
    article: RowOneLocalArticle | None,
) -> str:
    href = _local_article_href(story, article)
    count = _usable_local_article_paragraph_count(article)
    if href is None or count <= 0:
        return ""
    count_label = _local_read_count_label(count)
    return f"""<p class="local-read-path">
      <span class="local-read-path-badge">
        <span data-lang="en">Saved locally</span>
        <span data-lang="zh">本地已保存</span>
      </span>
      <span>
        <span data-lang="en">{_esc(count_label.en)}</span>
        <span data-lang="zh">{_esc(count_label.zh)}</span>
      </span>
    </p>"""


def _render_detail_local_read_path(local_article: RowOneLocalArticle | None) -> str:
    count = _usable_local_article_paragraph_count(local_article)
    if count <= 0:
        return ""
    count_label = _local_read_count_label(count)
    return f"""<p class="local-read-path detail-local-read-path">
  <span class="local-read-path-badge">
    <span data-lang="en">Saved locally</span>
    <span data-lang="zh">本地已保存</span>
  </span>
  <a class="local-read-action" href="#local-article">
    <span data-lang="en">Read saved article</span>
    <span data-lang="zh">阅读本地正文</span>
  </a>
  <span>
    <span data-lang="en">{_esc(count_label.en)}</span>
    <span data-lang="zh">{_esc(count_label.zh)}</span>
  </span>
</p>"""


def _validated_detail_relative_path(path: str) -> PurePosixPath | None:
    return validated_row_one_detail_relative_path(path)


def _safe_external_url(url: str | None) -> str | None:
    return safe_external_url(url)


def _section_title(edition: RowOneEdition, section_key: RowOneSectionKey):
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    return type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title())


def _esc(value: object) -> str:
    return escape(str(value), quote=True) if value is not None else ""
