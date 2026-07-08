# Stage 361 Daily Local Article Reading Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage Daily Local Article Reading Brief
that organizes already-saved local article content into concise reading lanes.

**Architecture:** Keep the feature render-only. `render.py` will pass the
existing safe story-id-to-local-article-page href map into `render_index_html`.
`templates.py` will derive reading lanes from `edition.stories`,
`local_articles_by_story_id`, story references, local article paragraphs,
brief sections, content sections, and the generated href map.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing Pydantic
models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add optional
    `daily_local_article_reading_brief_article_hrefs_by_story_id: Mapping[str, str] | None = None`
    to `render_index_html(...)`.
  - Render `_render_daily_local_article_reading_brief(...)` after Stage 360
    `daily_local_article_capsules_section` and before
    `saved_article_content_organization_section`.
  - Add private reading-brief dataclasses/helpers and scoped CSS.
- Modify `src/fashion_radar/row_one/render.py`
  - Reuse `_local_article_page_hrefs_by_story_id(...)`.
  - Pass the existing story-id href map into `render_index_html(...)`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for content, filtering, link safety, escaping,
    ordering, caps, placement, homepage-only site generation, and CSS.
- Modify `tests/test_workflows.py`
  - Add generated contract payload denylist entries, artifact stem guards, and
    a generated-site-only wrapper for Stage 361.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 361 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Direct Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add section extraction helper**

Add near existing homepage section helpers:

```python
def _daily_local_article_reading_brief_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-article-reading-brief"'
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]
```

- [ ] **Step 2: Write failing direct render test**

Add `test_render_index_html_includes_daily_local_article_reading_brief`. Build
an edition with five stories using `_edition().stories[0].model_copy(...)`.
Use ids:

```python
[
    "reading-brief-first-1111111111",
    "reading-brief-brand-2222222222",
    "reading-brief-product-3333333333",
    "reading-brief-context-4444444444",
    "reading-brief-overflow-5555555555",
]
```

Give the first story hostile headline/source values and both entity/product
refs:

```python
"headline": "Reading brief <script>",
"source_name": "Vogue <Business>",
"why_it_matters": LocalizedText(
    en="Why this article matters <b>.",
    zh="为什么这篇文章重要 <b>。",
),
"entity_refs": [RowOneReference(name="The Row", type="brand", label="brand")],
"product_refs": [RowOneReference(name="Margaux bag", type="bag", label="product")],
```

For stories 2, 3, and 5, explicitly set:

```python
"entity_refs": [],
"product_refs": [],
"designer_refs": [],
```

For story 4, explicitly set:

```python
"entity_refs": [RowOneReference(name="Chanel", type="brand", label="brand")],
"product_refs": [],
"designer_refs": [],
```

This keeps the overflow assertion tied to the deterministic fill order: Read
First renders stories 1-3, Brand Watch adds story 4 after dedupe, and story 5
does not render because the global cap is four.

Create local articles with:

```python
_signal_briefing_local_article().model_copy(
    deep=True,
    update={
        "story_id": story.id,
        "title": f"{story.headline} source <script>",
        "source_name": "Vogue <Business>",
        "body_source": "extracted",
        "paragraphs": [
            "Opening saved paragraph <b> for the reading brief.",
            "Second saved paragraph links the story context.",
        ],
        "paragraphs_zh": [
            "第一段保存正文 <b> 用于阅读简报。",
            "第二段保存正文连接故事背景。",
        ],
    },
)
```

Call:

```python
html = render_index_html(
    edition,
    local_articles_by_story_id=local_articles_by_story_id,
    daily_local_article_reading_brief_article_hrefs_by_story_id={
        story.id: f"{story.id}.html" for story in stories
    },
)
```

Assert:
- section class renders;
- `Daily Local Article Reading Brief` and `每日本地文章阅读简报` render;
- lane labels `Read First`, `Brand Watch`, and `Product Watch` render;
- first four story headlines render, overflow fifth headline does not render;
- hostile strings render escaped and raw `<script>`, `<b>`, `<Business>` do not;
- body-source label `Extracted article text`, source, why-it-matters, and first
  paragraph excerpt render;
- same-site links include
  `articles/reading-brief-first-1111111111.html#local-article-digest` and
  `articles/reading-brief-first-1111111111.html#local-article-paragraph-1`;
- no outbound URL appears.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_article_reading_brief \
  -q
```

Expected: fail because the new argument and section do not exist.

- [ ] **Step 3: Write failing filtering/link-safety test**

Add `test_render_index_html_filters_unsafe_daily_local_article_reading_brief`
with:

- one safe story with local article and mapped href
  `"safe-reading-brief-1111111111.html"`;
- one unsafe story id `"unsafe/reading-brief-2222222222"`;
- one story with no local article;
- one story with empty `paragraphs`;
- one story whose mapped href is `"../secret.html"`;
- one story whose mapped href is `"nested/story.html"`;
- one story whose mapped href is `".hidden.html"`;
- one story whose mapped href is `"white space.html"`;
- one story whose mapped href is `"mismatch-reading-brief-3333333333.html"`.

Assert only the safe story renders and no unsafe/missing/empty/traversal/nested/
hidden/mismatched text or href appears. Explicitly assert `"../secret"`,
`"nested/story.html"`, `".hidden.html"`, `"white space.html"`, and
`"mismatch-reading-brief-3333333333.html"` are absent.

Run the test and expect failure.

- [ ] **Step 4: Write failing empty-section test**

Add `test_render_index_html_omits_daily_local_article_reading_brief_without_eligible_articles`.
Render an edition with no `local_articles_by_story_id` and assert:

```python
assert 'class="daily-local-article-reading-brief"' not in html
assert "Daily Local Article Reading Brief" not in html
```

Run the test and expect failure only if the implementation has started; before
implementation it should fail by missing the new render argument if the test
passes the new argument.

- [ ] **Step 5: Write failing placement test**

Add `test_render_index_html_places_daily_local_article_reading_brief_between_sections`.
Render Stage 360 capsules, Stage 361 reading brief, and Saved Article Content
Organization. Assert:

```python
assert html.index('class="daily-local-article-capsules"') < html.index(
    'class="daily-local-article-reading-brief"'
)
assert html.index('class="daily-local-article-reading-brief"') < html.index(
    'class="saved-article-content-organization"'
)
```

Run the test and expect failure.

## Task 2: Template Implementation and CSS

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add optional render argument and insertion**

Update `render_index_html(...)`:

```python
daily_local_article_reading_brief_article_hrefs_by_story_id: Mapping[str, str] | None = None,
```

Compute:

```python
daily_local_article_reading_brief_section = _render_daily_local_article_reading_brief(
    edition,
    local_articles_by_story_id=local_articles_by_story_id,
    article_hrefs_by_story_id=daily_local_article_reading_brief_article_hrefs_by_story_id,
)
```

Insert between:

```html
{daily_local_article_capsules_section}
{saved_article_content_organization_section}
```

- [ ] **Step 2: Add dataclasses and constants**

Add near Stage 360 dataclasses:

```python
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS = 3
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_ITEMS_PER_GROUP = 3
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_TOTAL_ITEMS = 4
DAILY_LOCAL_ARTICLE_READING_BRIEF_EXCERPT_CHARS = 150
DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_REFS = 4


@dataclass(frozen=True)
class _DailyLocalArticleReadingBriefItem:
    title: LocalizedText
    article_title: str
    source_name: str
    body_source: str
    reason: LocalizedText
    href: str
    paragraph_href: str
    references: tuple[RowOneReference, ...]


@dataclass(frozen=True)
class _DailyLocalArticleReadingBriefGroup:
    key: str
    title: LocalizedText
    dek: LocalizedText
    items: tuple[_DailyLocalArticleReadingBriefItem, ...]
```

`title.en` must be the normalized `RowOneStory.headline`. `title.zh` must be the
normalized `RowOneLocalArticle.title` when present, otherwise the normalized
story headline. `article_title` is the raw normalized local article title
rendered as item meta/subtitle and omitted when absent.

`href: str` and `paragraph_href: str` are required because the item builder must
drop the item entirely unless both the digest link and first paragraph link can
be safely generated from the provided href map.

- [ ] **Step 3: Add renderer helpers**

Add helpers near Stage 360 helpers:

- `_render_daily_local_article_reading_brief(...)`
- `_daily_local_article_reading_brief_groups(...)`
- `_daily_local_article_reading_brief_group_candidates(story, article) -> list[str]`
- `_daily_local_article_reading_brief_item_from_story(...)`
- `_daily_local_article_reading_brief_href(...)`
- `_safe_daily_local_article_reading_brief_page_href(story_id: str, href: object) -> str | None`
- `_daily_local_article_reading_brief_reason(...)`
- `_daily_local_article_reading_brief_first_paragraph_index(...)`
- `_daily_local_article_reading_brief_references(...)`
- `_render_daily_local_article_reading_brief_group(...)`
- `_render_daily_local_article_reading_brief_item(...)`
- `_render_daily_local_article_reading_brief_ref(...)`

Safety rules:

- Validate story IDs with `safe_local_article_story_id(...)`.
- Guard `article_hrefs_by_story_id is None` before `.get(...)`.
- Validate mapped hrefs as one safe `.html` filename with no whitespace,
  traversal, leading dot, leading slash, or nested slash.
- Require mapped filename stem to equal the current story ID.
- Require `_usable_local_article_paragraph_count(article) > 0`.
- Link digest to `articles/<story-id>.html#local-article-digest`.
- Link paragraphs to `articles/<story-id>.html#local-article-paragraph-N`
  where `N` is one-based.
- Do not construct links from story ID alone.

Grouping rules:

- Build `Read First` from eligible stories in edition order.
- `_daily_local_article_reading_brief_group_candidates(story, article) -> list[str]`
  must receive both the `RowOneStory` and the looked-up
  `RowOneLocalArticle | None` so content-section matching can inspect
  `article.content_sections`. It returns the group keys for which this story is
  a candidate before dedupe and cap logic.
- Build `Brand Watch` from stories with `entity_refs`, `designer_refs`, or
  content section keys in `{"entities", "brand_signals"}`.
- Build `Product Watch` from stories with `product_refs` or content section
  key `"product_signals"`.
- Build groups in this fill order: `Read First`, then `Brand Watch`, then
  `Product Watch`.
- Deduplicate item story ids across groups as groups are built in that order,
  cap total rendered items to 4, and cap each group to 3.
- `paragraph_href: str` intentionally stores one anchor chip: the first valid
  saved paragraph used by the row.
- Use `DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS` as a sanity cap/assertion
  when returning rendered groups:

```python
assert len(groups) <= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS
```

- Use fixed group copy:
  - Read First title `Read First` / `先读这个`; dek `Start with the saved local
    articles that set the day's editorial context.` / `先读建立今日编辑背景的本地保存文章。`
  - Brand Watch title `Brand Watch` / `品牌观察`; dek `Brand and designer reads
    pulled from current saved local text.` / `来自当前本地保存正文的品牌与设计师阅读线索。`
  - Product Watch title `Product Watch` / `单品观察`; dek `Product reads that
    connect saved paragraphs to items, bags, shoes, and accessories.` /
    `把保存段落连接到单品、手袋、鞋履与配饰的阅读线索。`

- [ ] **Step 4: Add scoped CSS**

Add selectors:

- `.daily-local-article-reading-brief`
- `.daily-local-article-reading-brief-header`
- `.daily-local-article-reading-brief-metrics`
- `.daily-local-article-reading-brief-grid`
- `.daily-local-article-reading-brief-group`
- `.daily-local-article-reading-brief-group-header`
- `.daily-local-article-reading-brief-items`
- `.daily-local-article-reading-brief-item`
- `.daily-local-article-reading-brief-title`
- `.daily-local-article-reading-brief-meta`
- `.daily-local-article-reading-brief-reason`
- `.daily-local-article-reading-brief-refs`
- `.daily-local-article-reading-brief-action`

Use default one-column grid and `@media (min-width: 700px)` for two columns.

- [ ] **Step 5: Verify direct render tests pass**

Before the focused command, make sure the direct render test includes fallback
coverage for reason priority:

- one story with blank `why_it_matters` and a populated local article brief
  section body;
- one story with blank `why_it_matters`, no usable brief body, and a populated
  content-section item body.

Assert the brief-section body and content-section item body render in the
reading brief section.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_article_reading_brief \
  tests/test_row_one_render.py::test_render_index_html_filters_unsafe_daily_local_article_reading_brief \
  tests/test_row_one_render.py::test_render_index_html_omits_daily_local_article_reading_brief_without_eligible_articles \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_article_reading_brief_between_sections \
  -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing homepage-only site test**

Add `test_render_row_one_site_writes_daily_local_article_reading_brief_homepage_only`.
Use one story with saved local article. Render `render_row_one_site(...)`.
Assert:

- `index.html` contains `class="daily-local-article-reading-brief"`;
- `articles/index.html`, `articles/<story-id>.html`, and the story detail page
  do not contain that class;
- generated contract payloads do not contain:
  - `daily_local_article_reading_brief`
  - `daily-local-article-reading-brief`
  - `Daily Local Article Reading Brief`
  - `每日本地文章阅读简报`
- no root/articles/data artifact exists for stems:
  - `daily-local-article-reading-brief`
  - `daily-local-reading-brief`
  - `article-reading-brief`
  - `reading-brief`
  - `daily_local_article_reading_brief`
  - `daily_local_reading_brief`
  - `article_reading_brief`
  - `reading_brief`

Run and expect failure until `render.py` passes the href map.

- [ ] **Step 2: Pass href map from `render.py`**

In `render_row_one_site(...)`, pass:

```python
daily_local_article_reading_brief_article_hrefs_by_story_id=(
    local_article_page_hrefs_by_story_id
),
```

to `render_index_html(...)`.

- [ ] **Step 3: Verify site integration passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_article_reading_brief_homepage_only \
  -q
```

Expected: pass.

## Task 4: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add docs boundary text**

Insert before Stage 360 in both docs:

```markdown
Stage 361 adds generated-site only Daily Local Article Reading Brief as a homepage-only section inside `index.html` after Daily Local Article Capsules and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing local article brief sections, existing local article content sections, existing body-source labels, existing story references, generated local article page routes, and existing paragraph anchors to organize saved local text into compact read-first, brand-watch, and product-watch lanes without changing app-facing contracts; it does not create `data/daily-local-article-reading-brief.json`, does not create `data/daily-local-reading-brief.json`, does not create `data/article-reading-brief.json`, does not create new route families, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs test**

Add `test_row_one_docs_describe_stage_361_daily_local_article_reading_brief_boundary`
before the Stage 360 docs test. Assert the paragraph exists in both docs and
appears before Stage 360.

- [ ] **Step 3: Add workflow guard**

In `tests/test_workflows.py`, add Stage 361 denylist entries for generated
contract payloads and artifact stems. Add:

```python
def test_stage_361_daily_local_article_reading_brief_stays_generated_site_only(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_article_reading_brief",
        lambda *args, **kwargs: "",
    )
    _assert_generated_site_only_surface(...)
```

Mirror the Stage 360 wrapper style.

- [ ] **Step 4: Verify docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_361_daily_local_article_reading_brief_boundary \
  tests/test_workflows.py::test_stage_361_daily_local_article_reading_brief_stays_generated_site_only \
  -q
```

Expected: pass.

## Task 5: CSS Test and Focused Regression

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add CSS selector test**

Add `test_row_one_css_includes_daily_local_article_reading_brief_styles`.
Assert all selectors from Task 2 Step 4 exist.

- [ ] **Step 2: Run focused Stage 361 tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_article_reading_brief \
  tests/test_row_one_render.py::test_render_index_html_filters_unsafe_daily_local_article_reading_brief \
  tests/test_row_one_render.py::test_render_index_html_omits_daily_local_article_reading_brief_without_eligible_articles \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_article_reading_brief_between_sections \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_article_reading_brief_homepage_only \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_local_article_reading_brief_styles \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_361_daily_local_article_reading_brief_boundary \
  tests/test_workflows.py::test_stage_361_daily_local_article_reading_brief_stays_generated_site_only \
  -q
```

Expected: pass.

## Task 6: Reviews, Full Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-361-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-361-plan-review.md`
- Add: `docs/reviews/claude-code-stage-361-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-361-code-review.md`

- [ ] **Step 1: Request plan review before implementation**

Run Claude Code with `--effort max` against this plan and save prompt/output
under `docs/reviews/`. Fix plan findings before implementation.

- [ ] **Step 2: Request code reviews after implementation**

Run Claude Code with `--effort max` against the current diff and dispatch Codex
reviewer subagents with `reasoning_effort: xhigh`.

- [ ] **Step 3: Fix valid review findings**

For every Critical/Important finding, add or adjust tests first, reproduce the
issue, fix implementation, and rerun focused tests.

- [ ] **Step 4: Run full gates**

Run:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

Expected: all pass.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  docs/reviews/claude-code-stage-361-*.md \
  docs/superpowers/plans/2026-07-09-stage-361-daily-local-article-reading-brief-plan.md \
  docs/superpowers/specs/2026-07-09-stage-361-daily-local-article-reading-brief-design.md
git commit -m "Stage 361: add daily local article reading brief"
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \
  git -c http.version=HTTP/1.1 push origin main
```

- [ ] **Step 6: Handoff Summary**

Report repo status, pushed commit, verified commands, uncommitted files, and
next recommended stage.
