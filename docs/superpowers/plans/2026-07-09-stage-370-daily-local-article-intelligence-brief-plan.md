# Stage 370 Daily Local Article Intelligence Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Daily Local Article Intelligence Brief to the ROW ONE homepage.

**Architecture:** Build a focused homepage aggregate from Stage 369 per-article briefs, then render it in `index.html` after Daily Local Theme Summary Strip and before Saved Article Content Organization. Keep the feature out of app contracts, JSON artifacts, article pages, detail pages, source collection, and LLM paths.

**Tech Stack:** Python dataclasses, existing ROW ONE models/renderers, pytest, ruff, uv.

---

## Files

- Create: `src/fashion_radar/row_one/daily_local_article_intelligence_brief.py`
- Create: `tests/test_row_one_daily_local_article_intelligence_brief.py`
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Add reviews: `docs/reviews/claude-code-stage-370-plan-review.md`
- Add reviews: `docs/reviews/opencode-stage-370-plan-review.md`
- Add reviews after implementation:
  `docs/reviews/claude-code-stage-370-code-review.md` and
  `docs/reviews/opencode-stage-370-code-review.md`

## Constants

Use these exact caps unless plan review changes them:

```python
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES = 4
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES = 4
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE = 5
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTES = 4
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_OPENING_CHARS = 180
```

## Task 1: Builder RED Tests

**Files:**
- Create: `tests/test_row_one_daily_local_article_intelligence_brief.py`

- [ ] Add fixtures for `RowOneStory`, `RowOneLocalArticle`, references, and safe article href mappings.
- [ ] Add `test_build_daily_local_article_intelligence_brief_summarizes_saved_articles`:
  - two current-edition stories with matching local articles
  - each article has Stage 369-compatible brief/content sections, references, and paragraph indices
  - assert title text is `Daily Local Article Intelligence Brief` / `每日文章情报摘要`
  - assert metrics include two articles, two sources, lane signal count, and evidence count
  - assert lane keys include `brands`, `products`, and `themes`
  - assert article cards link to the first safe Stage 369 route, for example
    `articles/<story-id>.html#local-article-content-section-1`
  - assert first route links use safe paragraph/content-section fragments
- [ ] Add `test_build_daily_local_article_intelligence_brief_filters_unsafe_inputs`:
  - include mismatched local article story ID
  - include unsafe story ID
  - include missing href mapping
  - include unsafe href with `../`, absolute path, whitespace, and external URL
  - assert only valid current-edition articles remain
- [ ] Add `test_build_daily_local_article_intelligence_brief_caps_and_sorts_deterministically`:
  - more than four articles and more than five chips per lane
  - use at least three articles with non-overlapping brand chips so the
    aggregate exceeds the Stage 370 chip cap even though each Stage 369
    per-article lane is capped at four chips
  - assert article order follows edition order
  - assert lane chips sort by support count descending, first story index, label
  - assert caps match constants
- [ ] Add `test_build_daily_local_article_intelligence_brief_returns_none_without_publishable_content`:
  - no local articles
  - all blank paragraphs
  - no safe hrefs
  - assert `None`
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_article_intelligence_brief.py -q
```

Expected: fail because module does not exist.

## Task 2: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/daily_local_article_intelligence_brief.py`

- [ ] Implement dataclasses:

```python
@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefLaneChip:
    label: LocalizedText
    support_count: int

@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefLane:
    key: str
    title: LocalizedText
    chips: tuple[RowOneDailyLocalArticleIntelligenceBriefLaneChip, ...]
    total_count: int

@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefRoute:
    label: LocalizedText
    href: str

@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefArticle:
    title: LocalizedText
    source_name: str
    opening_signal: LocalizedText
    href: str
    evidence_count: int
    routes: tuple[RowOneDailyLocalArticleIntelligenceBriefRoute, ...]

@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBrief:
    title: LocalizedText
    opening_signal: LocalizedText
    article_count: int
    source_count: int
    signal_count: int
    evidence_count: int
    lanes: tuple[RowOneDailyLocalArticleIntelligenceBriefLane, ...]
    articles: tuple[RowOneDailyLocalArticleIntelligenceBriefArticle, ...]
```

- [ ] Implement:

```python
def build_row_one_daily_local_article_intelligence_brief(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalArticleIntelligenceBrief | None:
```

- [ ] Reuse `build_row_one_local_article_intelligence_brief(story=story, local_article=article)`.
- [ ] Validate page hrefs with same rules as other homepage local-article sections:
  only `story-id.html`, no whitespace, no `..`, no absolute/external URL, story ID must match.
- [ ] Validate fragments with Stage 369-compatible regex semantics:
  exact pattern `#local-article-(?:paragraph|content-section)-[1-9][0-9]*`
  only.
- [ ] Build final homepage article card primary hrefs from the first safe
  converted Stage 369 route. Do not emit bare `articles/{story_id}.html` card
  hrefs.
- [ ] Build final homepage route hrefs as
  `articles/{story_id}.html#local-article-content-section-N` or
  `articles/{story_id}.html#local-article-paragraph-N`.
- [ ] Skip an article if it has no safe converted paragraph/content-section
  route, because every Stage 370 homepage link must include a valid fragment.
- [ ] Compute `signal_count` as the sum of aggregate lane `total_count` values.
- [ ] Compute `evidence_count` as the sum of `len(brief.evidence)` across all
  per-article Stage 369 briefs included in the result.
- [ ] Run builder tests and fix until green.

## Task 3: Homepage Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add helper `_daily_local_article_intelligence_brief_section_html(html: str) -> str` slicing from `<section class="daily-local-article-intelligence-brief"` to `<section class="saved-article-content-organization"`.
- [ ] Add `test_render_index_html_includes_daily_local_article_intelligence_brief`:
  - build a brief with lanes and articles
  - call `render_index_html(..., daily_local_article_intelligence_brief=brief)`
  - assert English/Chinese heading, metrics, chips, article links, and route links render
  - assert placement is after `daily-local-theme-summary-strip` and before `saved-article-content-organization`
- [ ] Add `test_render_daily_local_article_intelligence_brief_escapes_and_filters_links`:
  - include `<script>` in title/source/chips
  - include unsafe route hrefs
  - assert escaped text and no `javascript:`, `../`, external URLs, or invalid
    `#local-article-paragraph-0` fragments
- [ ] Add `test_render_row_one_site_writes_daily_local_article_intelligence_brief_homepage_only`:
  - call `render_row_one_site`
  - assert section appears in `index.html`
  - assert section does not appear in `articles/index.html`, `articles/<story-id>.html`, or detail pages
  - assert edition/runtime/manifest payloads do not include Stage 370 names
  - assert no Stage 370 JSON/HTML artifact files exist
- [ ] Add `test_row_one_css_includes_daily_local_article_intelligence_brief_styles`.
- [ ] Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_article_intelligence_brief"
```

Expected: fail because render integration is not implemented.

## Task 4: Homepage Render Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/render.py`

- [ ] Import Stage 370 dataclasses and builder.
- [ ] Add optional `daily_local_article_intelligence_brief` parameter to `render_index_html`.
- [ ] In `render_row_one_site`, build the Stage 370 object after `local_article_page_hrefs_by_story_id` exists.
- [ ] Render Stage 370 after `{daily_local_theme_summary_strip_section}` and before `{saved_article_content_organization_section}` in the `render_index_html()` template insertion point currently adjacent to the Daily Local Theme Summary Strip and Saved Article Content Organization slots.
- [ ] Add `_render_daily_local_article_intelligence_brief` and small helpers for lane chips, article cards, route links, and safe href filtering.
- [ ] Add CSS selectors:
  - `.daily-local-article-intelligence-brief`
  - `.daily-local-article-intelligence-brief-header`
  - `.daily-local-article-intelligence-brief-metrics`
  - `.daily-local-article-intelligence-brief-lanes`
  - `.daily-local-article-intelligence-brief-lane`
  - `.daily-local-article-intelligence-brief-chip`
  - `.daily-local-article-intelligence-brief-grid`
  - `.daily-local-article-intelligence-brief-card`
  - `.daily-local-article-intelligence-brief-route`
- [ ] Add mobile one-column rules for lanes and card grid.
- [ ] Run render tests and fix until green.

## Task 5: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] Add this exact Stage 370 boundary paragraph before Stage 369 in README and docs/row-one.md:

```text
Stage 370 adds generated-site only Daily Local Article Intelligence Brief inside `index.html` between the Daily Local Theme Summary Strip and Saved Article Content Organization; it reuses current-edition stories, current-edition saved local article sidecars, Stage 369 local article intelligence briefs, generated local article page routes, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to summarize today's saved articles into a homepage opening read, entity lanes, article cards, and same-site reader routes without changing app-facing contracts; it does not create `data/daily-local-article-intelligence-brief.json`, does not create `data/local-article-intelligence-brief.json`, does not create `data/article-intelligence-brief.json`, does not create `daily-local-article-intelligence-brief.html`, does not create `local-article-intelligence-brief.html`, does not create `article-intelligence-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] Add docs test verifying the exact paragraph appears before Stage 369.
- [ ] Extend workflow app contract denylist with:
  - `daily_local_article_intelligence_brief`
  - `local_article_intelligence_brief`
  - `article_intelligence_brief`
  - `RowOneDailyLocalArticleIntelligenceBrief`
  - `Daily Local Article Intelligence Brief`
  - `每日文章情报摘要`
  - `daily-local-article-intelligence-brief`
  - `local-article-intelligence-brief`
  - `article-intelligence-brief`
- [ ] Extend artifact stems with:
  - `daily-local-article-intelligence-brief`
  - `local-article-intelligence-brief`
  - `article-intelligence-brief`
  - `daily_local_article_intelligence_brief`
  - `local_article_intelligence_brief`
  - `article_intelligence_brief`
- [ ] Add wrapper guard monkeypatching `_render_daily_local_article_intelligence_brief` to `""` and reuse the existing sqlite mutation guard pattern.

## Task 6: Verification and Review

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_article_intelligence_brief.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "daily_local_article_intelligence_brief or stage_370 or article_intelligence_brief or stage_369"
```

- [ ] Run full gates:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] Request code review:

```bash
claude -p --effort max --permission-mode bypassPermissions "<Stage 370 code review prompt>"
opencode run -m zhipuai-coding-plan/glm-5.2 --auto "<Stage 370 code review prompt>"
```

- [ ] Fix Critical and Important findings.
- [ ] Re-run focused tests and full gates after fixes.
- [ ] Commit and push:

```bash
git add src/fashion_radar/row_one/daily_local_article_intelligence_brief.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_article_intelligence_brief.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py README.md docs/row-one.md docs/superpowers/specs/2026-07-09-stage-370-daily-local-article-intelligence-brief-design.md docs/superpowers/plans/2026-07-09-stage-370-daily-local-article-intelligence-brief-plan.md docs/reviews/claude-code-stage-370-plan-review.md docs/reviews/opencode-stage-370-plan-review.md docs/reviews/claude-code-stage-370-code-review.md docs/reviews/opencode-stage-370-code-review.md
git commit -m "Stage 370: add daily local article intelligence brief"
git push origin main
```
