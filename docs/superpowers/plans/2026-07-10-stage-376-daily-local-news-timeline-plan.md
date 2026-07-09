# Stage 376 Daily Local News Timeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site only Daily Local News Timeline to the ROW ONE homepage so readers can scan the newest locally saved fashion stories in chronological order.

**Architecture:** Add one pure builder module that derives a compact homepage timeline from `RowOneEdition`, saved local article sidecars, and existing local article page hrefs. Wire the optional model into `render_row_one_site(...)` and `render_index_html(...)`, render it between Daily Local Theme Summary Strip and Daily Local Article Intelligence Brief, and keep all generated JSON/app/runtime/manifest contracts unchanged.

**Tech Stack:** Python dataclasses, `datetime`, pathlib-free pure builders, existing ROW ONE Pydantic models, existing HTML template helpers, pytest, ruff, uv.

---

## Product Gap

Stage 376 closes the "latest news order" gap in the collect -> match -> report
pipeline. Existing ROW ONE generated pages organize saved local article content
by theme, source, signal, and reading sequence. The new timeline adds a
chronological homepage layer so the daily website shows what published most
recently without fetching new sources or adding ranking.

## File Map

- Create `src/fashion_radar/row_one/daily_local_news_timeline.py`
  - Owns dataclasses, safe filtering, date selection, excerpt selection, and
    timeline ordering.
- Modify `src/fashion_radar/row_one/render.py`
  - Builds the timeline after local article page hrefs are known.
  - Passes the optional model into `render_index_html(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Adds `daily_local_news_timeline` argument to `render_index_html(...)`.
  - Renders the new homepage section between Theme Summary Strip and Daily Local
    Article Intelligence Brief.
  - Adds CSS for compact timeline cards.
- Create `tests/test_row_one_daily_local_news_timeline.py`
  - Unit tests for builder behavior.
- Modify `tests/test_row_one_render.py`
  - Homepage rendering, placement, escaping/filtering, generated-site-only, CSS.
- Modify `tests/test_workflows.py`
  - Contract/artifact denylist and generated-site-only guard.
- Modify `tests/test_row_one_docs.py`
  - Stage 376 docs boundary test.
- Modify `README.md` and `docs/row-one.md`
  - Stage 376 boundary paragraph above Stage 375.
- Create review records under `docs/reviews/` during plan/code review.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-376-plan-review.md`
- Create: `docs/reviews/opencode-stage-376-plan-review.md`
- Modify if needed: `docs/superpowers/specs/2026-07-10-stage-376-daily-local-news-timeline-design.md`
- Modify if needed: `docs/superpowers/plans/2026-07-10-stage-376-daily-local-news-timeline-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 376 Daily Local News Timeline plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-10-stage-376-daily-local-news-timeline-design.md and docs/superpowers/plans/2026-07-10-stage-376-daily-local-news-timeline-plan.md. Goal: add a generated-site only homepage timeline of the newest saved local articles using existing RowOneEdition stories, saved local article sidecars, and same-site local article page hrefs. Technical stack: Python dataclasses, datetime, existing ROW ONE models, templates.py, render.py, pytest, ruff, uv. Implementation method: pure builder module, optional render_index_html model, render_row_one_site integration after local article href map, no generated JSON artifacts or app/runtime/manifest contract changes. Check feasibility, date semantics, route safety, placement, generated-site-only boundaries, app-contract/artifact leakage risk, duplication with existing local article stages, and test plan. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-376-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 376 Daily Local News Timeline plan/spec. Read docs/reviews/claude-code-stage-376-plan-review.md if present, docs/superpowers/specs/2026-07-10-stage-376-daily-local-news-timeline-design.md, and docs/superpowers/plans/2026-07-10-stage-376-daily-local-news-timeline-plan.md. Check feasibility, route safety, date ordering, generated-site-only boundaries, test coverage, docs boundaries, and whether the feature duplicates existing ROW ONE sections. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-376-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update the spec/plan and
run matching rereviews:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 376 Daily Local News Timeline plan/spec after fixes. Return remaining Critical and Important findings only."
```

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 376 Daily Local News Timeline plan/spec after fixes. Return remaining Critical and Important findings only."
```

Save outputs as:

- `docs/reviews/claude-code-stage-376-plan-rereview.md`
- `docs/reviews/opencode-stage-376-plan-rereview.md`

## Task 2: Builder RED Tests

**Files:**
- Create: `tests/test_row_one_daily_local_news_timeline.py`

- [ ] **Step 1: Add model-valid fixtures**

Create fixtures that build `RowOneEdition`, `RowOneStory`, and
`RowOneLocalArticle` objects with required fields only. Use no forbidden extra
fields.

Key fixture shape:

```python
from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneSection,
    RowOneStory,
)


def _text(value: str) -> LocalizedText:
    return LocalizedText(en=value, zh=value)


def _story(story_id: str, *, headline: str, published_at: str | None) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline=headline,
        summary=_text(f"{headline} summary"),
        why_it_matters=_text(f"{headline} why it matters"),
        editorial_takeaway=_text(f"{headline} takeaway"),
        signal_context=_text(f"{headline} signal"),
        reader_path=_text(f"{headline} reader path"),
        source_name="Vogue Business",
        published_at=published_at,
        detail_path=f"details/{story_id}.html",
    )


def _article(
    story_id: str,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    published_at: str | None = None,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=title,
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=datetime(2026, 7, 10, 4, 0, tzinfo=UTC),
        published_at=published_at,
        paragraphs=paragraphs or ["First saved paragraph for local reading."],
        paragraphs_zh=paragraphs_zh or [],
        brief_sections=[],
        content_sections=[],
        body_source="extracted",
        skipped=False,
    )
```

- [ ] **Step 2: Add failing builder tests**

Add these tests:

- `test_daily_local_news_timeline_orders_newest_first_with_tie_breakers`
- `test_daily_local_news_timeline_prefers_article_published_at`
- `test_daily_local_news_timeline_links_first_nonblank_paragraph_without_renumbering`
- `test_daily_local_news_timeline_filters_unsafe_and_unusable_entries`
- `test_daily_local_news_timeline_caps_entries`
- `test_daily_local_news_timeline_returns_none_without_usable_entries`

Expected assertions:

```python
timeline = build_row_one_daily_local_news_timeline(
    edition,
    articles,
    hrefs,
)
assert timeline is not None
assert [item.title.en for item in timeline.items] == [
    "Newest saved story",
    "Tie winner by edition order",
    "Tie loser by edition order",
]
assert timeline.items[0].href == "articles/story-id-1234567890.html#local-article-paragraph-2"
assert timeline.item_count == len(timeline.items)
assert timeline.source_count == 2
assert timeline.latest_label.en == "Jul 10, 2026"
assert timeline.latest_label.zh == "2026-07-10"
```

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_news_timeline.py -q
```

Expected: fails because `fashion_radar.row_one.daily_local_news_timeline` does
not exist yet.

## Task 3: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/daily_local_news_timeline.py`
- Test: `tests/test_row_one_daily_local_news_timeline.py`

- [ ] **Step 1: Implement dataclasses and constants**

Create:

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_NEWS_TIMELINE_MAX_ITEMS = 6
DAILY_LOCAL_NEWS_TIMELINE_EXCERPT_CHARS = 180


@dataclass(frozen=True)
class RowOneDailyLocalNewsTimelineItem:
    title: LocalizedText
    source_name: str
    published_at: datetime
    published_label: LocalizedText
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalNewsTimeline:
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    latest_label: LocalizedText
    items: tuple[RowOneDailyLocalNewsTimelineItem, ...]
```

- [ ] **Step 2: Implement the builder**

Implement:

```python
def build_row_one_daily_local_news_timeline(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalNewsTimeline | None:
    candidates = []
    for story_index, story in enumerate(edition.stories):
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue
        published_at = article.published_at or story.published_at
        if published_at is None:
            continue
        paragraph = _first_paragraph(article)
        if paragraph is None:
            continue
        paragraph_index, excerpt = paragraph
        title = _title(story.headline, article.title, story.id)
        source_name = _source_name(article.source_name, story.source_name)
        href = f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}"
        candidates.append(
            (
                story_index,
                story.id,
                RowOneDailyLocalNewsTimelineItem(
                    title=title,
                    source_name=source_name,
                    published_at=published_at,
                    published_label=_published_label(published_at),
                    excerpt=excerpt,
                    href=href,
                ),
            )
        )
    candidates.sort(key=lambda value: (-value[2].published_at.timestamp(), value[0], value[1]))
    items = tuple(item for _story_index, _story_id, item in candidates[:DAILY_LOCAL_NEWS_TIMELINE_MAX_ITEMS])
    if not items:
        return None
    source_count = len({item.source_name.casefold() for item in items if item.source_name})
    return RowOneDailyLocalNewsTimeline(
        title=LocalizedText(en="Daily Local News Timeline", zh="每日本地新闻时间线"),
        dek=LocalizedText(
            en="Newest saved local fashion stories in publication order.",
            zh="按发布时间排列的最新本地保存时尚资讯。",
        ),
        item_count=len(items),
        source_count=source_count,
        latest_label=items[0].published_label,
        items=items,
    )
```

The final implementation may split long lines for formatting.

- [ ] **Step 3: Implement private helpers**

Implement:

```python
def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name
```

Also implement `_first_paragraph`, `_localized_excerpt`, `_title`,
`_source_name`, and `_published_label` using the design rules.

Required paragraph/excerpt helper contract:

```python
def _first_paragraph(article: RowOneLocalArticle) -> tuple[int, LocalizedText] | None:
    for index, paragraph in enumerate(article.paragraphs):
        paragraph_en = normalize_row_one_paragraph(paragraph)
        if not paragraph_en:
            continue
        paragraph_zh = ""
        if len(article.paragraphs_zh) == len(article.paragraphs):
            paragraph_zh = normalize_row_one_paragraph(article.paragraphs_zh[index])
        excerpt_en = _localized_excerpt(paragraph_en)
        excerpt_zh = _localized_excerpt(paragraph_zh or paragraph_en)
        return index, LocalizedText(en=excerpt_en, zh=excerpt_zh)
    return None


def _localized_excerpt(value: str) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= DAILY_LOCAL_NEWS_TIMELINE_EXCERPT_CHARS:
        return normalized
    return normalized[: DAILY_LOCAL_NEWS_TIMELINE_EXCERPT_CHARS - 3].rstrip() + "..."
```

This preserves the original paragraph index for
`#local-article-paragraph-{index + 1}` while allowing aligned Chinese text only
when `paragraphs_zh` has the same length as `paragraphs` and the aligned value
is nonblank.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_news_timeline.py -q
```

Expected: all builder tests pass.

## Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add timeline fixture helpers**

Add helpers near existing daily local fixture helpers:

```python
def _daily_local_news_timeline_fixture() -> RowOneDailyLocalNewsTimeline:
    return RowOneDailyLocalNewsTimeline(
        title=LocalizedText(en="Daily Local News Timeline", zh="每日本地新闻时间线"),
        dek=LocalizedText(en="Newest saved local fashion stories.", zh="最新本地保存时尚资讯。"),
        item_count=1,
        source_count=1,
        latest_label=LocalizedText(en="Jul 10, 2026", zh="2026-07-10"),
        items=(
            RowOneDailyLocalNewsTimelineItem(
                title=LocalizedText(en="The Row timeline", zh="The Row 时间线"),
                source_name="Vogue Business",
                published_at=datetime(2026, 7, 10, 8, 30, tzinfo=UTC),
                published_label=LocalizedText(en="Jul 10, 2026", zh="2026-07-10"),
                excerpt=LocalizedText(en="A saved local paragraph.", zh="一段本地保存正文。"),
                href="articles/the-row-signal-1234567890.html#local-article-paragraph-1",
            ),
        ),
    )
```

- [ ] **Step 2: Add render tests**

Add:

- `test_render_index_html_includes_daily_local_news_timeline`
- `test_render_daily_local_news_timeline_escapes_and_filters_links`
- `test_render_row_one_site_writes_daily_local_news_timeline_homepage_only`
- `test_row_one_css_includes_daily_local_news_timeline_styles`

Assertions:

```python
stories = [
    _coverage_map_story("theme-strip-row-1111111111", "Theme strip story", "Vogue Business"),
]
organization = RowOneSavedArticleContentOrganization(
    groups=[
        RowOneSavedArticleContentOrganizationGroup(
            key="takeaways",
            title=LocalizedText(en="Read First", zh="优先阅读"),
            dek=LocalizedText(en="Theme summary dek.", zh="主题摘要。"),
            cards=[
                _coverage_map_card(
                    stories[0],
                    source_name="Vogue Business",
                    group_title=LocalizedText(en="Read First", zh="优先阅读"),
                ),
            ],
        ),
    ],
)
html = render_index_html(
    _edition_with_stories(*stories),
    saved_article_content_organization=organization,
    local_articles_by_story_id={
        stories[0].id: _coverage_map_article(stories[0], "Vogue Business")
    },
    daily_local_theme_summary_strip_hrefs_by_detail_path={
        f"details/{stories[0].id}.html": f"{stories[0].id}.html"
    },
    daily_local_news_timeline=_daily_local_news_timeline_fixture(),
    daily_local_article_intelligence_brief=_daily_local_article_intelligence_brief_fixture(),
)
assert "Daily Local News Timeline" in html
assert "The Row timeline" in html
assert 'href="articles/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
assert html.index('class="daily-local-theme-summary-strip"') < html.index(
    'class="daily-local-news-timeline"'
)
assert html.index('class="daily-local-news-timeline"') < html.index(
    'class="daily-local-article-intelligence-brief"'
)
```

Unsafe hrefs to filter:

```python
(
    "articles/the-row-signal-1234567890.html",
    "articles/the-row-signal-1234567890.html#",
    "articles/the-row-signal-1234567890.html#local-article-paragraph-",
    "articles/the-row-signal-1234567890.html#local-article-paragraph-0",
    "articles/the-row-signal-1234567890.html#local-article-paragraph-01",
    "articles/the-row-signal-1234567890.html#local-article-paragraph-1x",
    "articles/the-row-signal-1234567890.html #local-article-paragraph-1",
    "../articles/the-row-signal-1234567890.html#local-article-paragraph-1",
    "/articles/the-row-signal-1234567890.html#local-article-paragraph-1",
    "//example.com/articles/the-row-signal-1234567890.html#local-article-paragraph-1",
    "https://example.com/articles/the-row-signal-1234567890.html#local-article-paragraph-1",
    "articles/../the-row-signal-1234567890.html#local-article-paragraph-1",
    "articles/bad story.html#local-article-paragraph-1",
    "articles/javascript:void(0).html#local-article-paragraph-1",
)
```

- [ ] **Step 3: Verify render RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_news_timeline"
```

Expected: fails because imports, render argument, renderer, or CSS are missing.

## Task 5: Render Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/render.py`
- Test: `tests/test_row_one_render.py`

- [ ] **Step 1: Import timeline models/builders**

In `templates.py`, import:

```python
from fashion_radar.row_one.daily_local_news_timeline import (
    RowOneDailyLocalNewsTimeline,
    RowOneDailyLocalNewsTimelineItem,
)
```

In `render.py`, import:

```python
from fashion_radar.row_one.daily_local_news_timeline import (
    build_row_one_daily_local_news_timeline,
)
```

- [ ] **Step 2: Add optional render_index_html parameter**

Add:

```python
daily_local_news_timeline: RowOneDailyLocalNewsTimeline | None = None,
```

Compute:

```python
daily_local_news_timeline_section = _render_daily_local_news_timeline(
    daily_local_news_timeline
)
```

Insert `{daily_local_news_timeline_section}` between
`{daily_local_theme_summary_strip_section}` and
`{daily_local_article_intelligence_brief_section}`.

- [ ] **Step 3: Implement timeline renderer**

Add private helpers near other daily local renderers:

```python
def _render_daily_local_news_timeline(
    timeline: RowOneDailyLocalNewsTimeline | None,
) -> str:
    if timeline is None or not timeline.items:
        return ""
    items = "\n".join(
        item_html
        for item in timeline.items
        if (item_html := _render_daily_local_news_timeline_item(item))
    )
    if not items:
        return ""
    return f"""<section class="daily-local-news-timeline" aria-labelledby="daily-local-news-timeline-title">
      <div class="section-heading">
        <p class="story-section">
          <span data-lang="en">Latest Saved Locally</span>
          <span data-lang="zh">最新本地保存</span>
        </p>
        <h2 id="daily-local-news-timeline-title">
          <span data-lang="en">{_esc(timeline.title.en)}</span>
          <span data-lang="zh">{_esc(timeline.title.zh)}</span>
        </h2>
        <p>
          <span data-lang="en">{_esc(timeline.dek.en)}</span>
          <span data-lang="zh">{_esc(timeline.dek.zh)}</span>
        </p>
      </div>
      <div class="daily-local-news-timeline-meta">
        <span>{_esc(_count_label(timeline.item_count, "timed story", "timed stories"))}</span>
        <span>{_esc(_count_label(timeline.source_count, "source", "sources"))}</span>
      </div>
      <div class="daily-local-news-timeline-list">{items}</div>
    </section>"""
```

Implement `_render_daily_local_news_timeline_item(...)` and
`_safe_daily_local_news_timeline_href(...)`. Use existing `_esc` and
`_count_label` helpers in `templates.py`. Safe hrefs must allow only:

`articles/<safe-story-id>.html#local-article-paragraph-N`

where `N >= 1`.

- [ ] **Step 4: Add CSS**

Add classes inside `row_one_css()`:

```css
.daily-local-news-timeline {
  margin: 2rem 0;
}
.daily-local-news-timeline-list {
  display: grid;
  gap: 0.75rem;
}
.daily-local-news-timeline-item {
  border-top: 1px solid var(--border);
  padding-top: 0.9rem;
}
.daily-local-news-timeline-date {
  font-size: 0.78rem;
  letter-spacing: 0;
  text-transform: uppercase;
  color: var(--muted);
}
.daily-local-news-timeline-item h3 {
  margin: 0.25rem 0;
}
.daily-local-news-timeline-item p {
  margin: 0.35rem 0 0;
}
```

Use existing CSS variables; do not introduce a one-hue palette or gradient.

- [ ] **Step 5: Wire render_row_one_site**

After `local_article_page_hrefs_by_story_id` is computed, build:

```python
daily_local_news_timeline = build_row_one_daily_local_news_timeline(
    edition,
    local_articles_by_story_id,
    local_article_page_hrefs_by_story_id,
)
```

Pass:

```python
daily_local_news_timeline=daily_local_news_timeline,
```

- [ ] **Step 6: Verify render GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_news_timeline"
```

Expected: timeline render tests pass.

## Task 6: Docs And Workflow RED Tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add workflow denylist and guard tests**

Add timeline tokens to generated contract and artifact denylist checks:

```python
"daily_local_news_timeline",
"local_news_timeline",
"news_timeline",
"RowOneDailyLocalNewsTimeline",
"Daily Local News Timeline",
"daily-local-news-timeline",
"local-news-timeline",
"news-timeline",
"每日本地新闻时间线",
```

Add:

```python
def test_stage_376_daily_local_news_timeline_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_news_timeline",
        lambda *_args, **_kwargs: "",
        raising=True,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

This guard allows a live model to flow during site generation while suppressing
only the homepage renderer. It proves the feature does not create JSON
contract/artifact leakage or standalone timeline artifacts outside
`index.html`.

- [ ] **Step 2: Add docs boundary test**

Add `test_row_one_docs_describe_stage_376_daily_local_news_timeline_boundary`
with this exact paragraph:

```text
Stage 376 adds generated-site only Daily Local News Timeline inside `index.html` between Daily Local Theme Summary Strip and Daily Local Article Intelligence Brief; it reuses current-edition stories, current-edition saved local article sidecars, generated local article page routes, existing saved local paragraphs, and existing paragraph anchors to show today's saved local fashion stories in publication-time order with short same-site excerpts without changing app-facing contracts; it does not create `data/daily-local-news-timeline.json`, does not create `data/local-news-timeline.json`, does not create `data/news-timeline.json`, does not create `daily-local-news-timeline.html`, does not create `local-news-timeline.html`, does not create `news-timeline.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

Assert the paragraph appears before Stage 375 in both README and docs.

- [ ] **Step 3: Verify docs/workflow RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "daily_local_news_timeline or stage_376"
```

Expected: fails until docs and workflow implementation are updated.

## Task 7: Docs And Workflow Implementation

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Update docs**

Insert the exact Stage 376 paragraph above the Stage 375 paragraph in:

- `README.md`
- `docs/row-one.md`

- [ ] **Step 2: Verify docs/workflow GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "daily_local_news_timeline or stage_376"
```

Expected: tests pass.

## Task 8: Focused Verification

**Files:**
- Source and test files touched by Tasks 2-7.

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_news_timeline.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  -q -k "daily_local_news_timeline or stage_376"
```

Expected: all selected tests pass.

- [ ] **Step 2: Run touched files without `-k`**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_daily_local_news_timeline.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  -q
```

Expected: all touched test files pass.

- [ ] **Step 3: Run ruff**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/daily_local_news_timeline.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_daily_local_news_timeline.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py
```

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/daily_local_news_timeline.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_daily_local_news_timeline.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py
```

Expected: ruff check and format checks pass.

## Task 9: Code Review, Full Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-376-code-review.md`
- Create: `docs/reviews/opencode-stage-376-code-review.md`
- Modify as needed from review findings.

- [ ] **Step 1: Request Claude Code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 376 Daily Local News Timeline implementation in /home/ubuntu/fashion-radar. Review the diff from HEAD and the spec/plan docs/superpowers/specs/2026-07-10-stage-376-daily-local-news-timeline-design.md and docs/superpowers/plans/2026-07-10-stage-376-daily-local-news-timeline-plan.md. Check correctness, date ordering, route safety, generated-site-only boundaries, app-contract/artifact boundaries, tests, and docs. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-376-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 2: Request opencode review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 376 Daily Local News Timeline implementation. Read docs/reviews/claude-code-stage-376-code-review.md if present, current git diff, docs/superpowers/specs/2026-07-10-stage-376-daily-local-news-timeline-design.md, docs/superpowers/plans/2026-07-10-stage-376-daily-local-news-timeline-plan.md, and relevant source/tests. Check correctness, date ordering, route safety, generated-site-only boundaries, app-contract/artifact boundaries, tests, docs, and review artifact hygiene. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-376-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 3: Fix Critical and Important findings**

If reviews raise valid Critical or Important issues, fix them and run matching
rereviews:

- `docs/reviews/claude-code-stage-376-code-rereview.md`
- `docs/reviews/opencode-stage-376-code-rereview.md`

- [ ] **Step 4: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
git diff --cached --check
```

Expected: all gates pass.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-376-*.md \
  docs/reviews/opencode-stage-376-*.md \
  docs/superpowers/specs/2026-07-10-stage-376-daily-local-news-timeline-design.md \
  docs/superpowers/plans/2026-07-10-stage-376-daily-local-news-timeline-plan.md \
  src/fashion_radar/row_one/daily_local_news_timeline.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_daily_local_news_timeline.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py
git commit -m "Stage 376: add daily local news timeline"
git push origin main
```

Expected: commit and push succeed.
