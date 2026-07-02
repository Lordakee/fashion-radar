from __future__ import annotations

import re
from html import escape
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)

_DETAIL_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html$")


def render_index_html(edition: RowOneEdition) -> str:
    contents_nav = _render_edition_nav(edition)
    story_cards = "\n".join(_render_section(edition, section.key) for section in edition.sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(edition.brand)} — {_esc(edition.edition_date.date().isoformat())}</title>
<link rel="stylesheet" href="assets/row-one.css">
</head>
<body>
<header class="site-header">
  <div class="edition-kicker">Daily Fashion Intelligence</div>
  <h1>{_esc(edition.brand)}</h1>
  <p class="edition-date">{_esc(edition.edition_date.strftime("%B %d, %Y"))}</p>
  <div class="language-toggle" aria-label="Language">
    <button type="button" data-lang-toggle="en" aria-pressed="true">EN</button>
    <button type="button" data-lang-toggle="zh" aria-pressed="false">中文</button>
  </div>
  <p class="edition-summary">
    <span data-lang="en">{_esc(edition.summary.en)}</span>
    <span data-lang="zh">{_esc(edition.summary.zh)}</span>
  </p>
</header>
<main>
{contents_nav}
{story_cards}
</main>
<script src="assets/row-one.js"></script>
</body>
</html>
"""


def render_detail_html(edition: RowOneEdition, story: RowOneStory) -> str:
    section_title = _section_title(edition, story.section_key)
    evidence = "\n".join(_render_evidence(link) for link in story.evidence)
    source_link = _external_link(story.source_url, story.source_name, css_class="source-link")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
    <p class="story-source">{source_link}</p>
    <section>
      <h2>
        <span data-lang="en">Summary</span>
        <span data-lang="zh">摘要</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.summary.en)}</span>
        <span data-lang="zh">{_esc(story.summary.zh)}</span>
      </p>
    </section>
    <section>
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
      <p class="story-section">
        <span data-lang="en">Editorial Synthesis</span>
        <span data-lang="zh">编辑整理</span>
      </p>
      <h2>
        <span data-lang="en">How To Read This Signal</span>
        <span data-lang="zh">如何阅读这条信号</span>
      </h2>
      <p>
        <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
        <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
      </p>
      <p>
        <span data-lang="en">{_esc(story.signal_context.en)}</span>
        <span data-lang="zh">{_esc(story.signal_context.zh)}</span>
      </p>
      <p>
        <span data-lang="en">{_esc(story.reader_path.en)}</span>
        <span data-lang="zh">{_esc(story.reader_path.zh)}</span>
      </p>
    </section>
    <section>
      <h2>
        <span data-lang="en">Evidence</span>
        <span data-lang="zh">来源线索</span>
      </h2>
      <div class="evidence-list">{evidence}</div>
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
  --paper: #f5f1ea;
  --ink: #15120f;
  --muted: #746d64;
  --line: #d8d0c4;
  --accent: #7d1f2d;
  --panel: #fffaf2;
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
.site-header {
  min-height: 52vh;
  padding: 44px min(7vw, 88px) 32px;
  border-bottom: 1px solid var(--ink);
  display: grid;
  align-content: space-between;
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
main { padding: 36px min(7vw, 88px) 72px; }
.edition-nav {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  padding: 24px 0;
  margin-bottom: 32px;
}
.edition-nav-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}
.edition-nav-item {
  border: 1px solid var(--line);
  color: var(--ink);
  display: grid;
  gap: 8px;
  min-height: 150px;
  padding: 16px;
  text-decoration: none;
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
[data-lang="zh"] { display: none; }
body.lang-zh [data-lang="en"] { display: none; }
body.lang-zh [data-lang="zh"] { display: inline; }
body.lang-zh p [data-lang="zh"] { display: inline; }
@media (max-width: 760px) {
  .site-header { min-height: 46vh; padding: 28px 20px; }
  main { padding: 24px 20px 56px; }
  .edition-nav-grid { grid-template-columns: 1fr; }
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
  <div class="edition-nav-grid">{rows}</div>
</nav>"""


def _render_edition_nav_item(
    edition: RowOneEdition,
    section: RowOneSection,
) -> str:
    story_count = len(edition.section_stories(section.key))
    count_en = "1 story" if story_count == 1 else f"{story_count} stories"
    count_zh = f"{story_count} 条"
    return f"""<a class="edition-nav-item" href="#{_esc(section.key)}">
  <span class="edition-nav-title">
    <span data-lang="en">{_esc(section.title.en)}</span>
    <span data-lang="zh">{_esc(section.title.zh)}</span>
  </span>
  <span class="edition-nav-count">
    <span data-lang="en">{_esc(count_en)}</span>
    <span data-lang="zh">{_esc(count_zh)}</span>
  </span>
  <span class="edition-nav-dek">
    <span data-lang="en">{_esc(section.dek.en)}</span>
    <span data-lang="zh">{_esc(section.dek.zh)}</span>
  </span>
</a>"""


def row_one_js() -> str:
    return """(() => {
  const buttons = Array.from(document.querySelectorAll("[data-lang-toggle]"));
  const setLang = (lang) => {
    document.body.classList.toggle("lang-zh", lang === "zh");
    document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.langToggle === lang ? "true" : "false");
    });
  };
  buttons.forEach((button) => {
    button.addEventListener("click", () => setLang(button.dataset.langToggle || "en"));
  });
  setLang("en");
})();
"""


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
    return f"""<article class="story-card">
  <div>
    <h3><a href="{detail_href}">{_esc(story.headline)}</a></h3>
  </div>
  {_render_story_orientation(story, section_title)}
  <p class="story-takeaway">
    <span data-lang="en">{_esc(story.editorial_takeaway.en)}</span>
    <span data-lang="zh">{_esc(story.editorial_takeaway.zh)}</span>
  </p>
  <p>
    <span data-lang="en">{_esc(story.summary.en)}</span>
    <span data-lang="zh">{_esc(story.summary.zh)}</span>
  </p>
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


def _published_label(story: RowOneStory) -> LocalizedText:
    if story.published_at is None:
        return LocalizedText(zh="时间未标注", en="Undated")
    return LocalizedText(
        zh=story.published_at.strftime("%Y-%m-%d"),
        en=story.published_at.strftime("%b %d, %Y"),
    )


def _render_evidence(link: RowOneLink) -> str:
    rendered = _external_link(link.url, link.title)
    return (
        f'<div class="evidence-item">{rendered}'
        f'<p class="story-meta">{_esc(link.source_name)}</p></div>'
    )


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
    if not url:
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return url


def _section_title(edition: RowOneEdition, section_key: RowOneSectionKey):
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    return type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title())


def _esc(value: object) -> str:
    return escape(str(value), quote=True) if value is not None else ""
