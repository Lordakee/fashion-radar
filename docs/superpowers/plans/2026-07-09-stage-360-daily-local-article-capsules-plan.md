# Stage 360 Daily Local Article Capsules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage section that turns already-saved
local article text into compact readable article capsules with same-site local
article links.

**Architecture:** Keep the feature render-only. `render.py` will pass a
safe story-id-to-local-article-page href map into `render_index_html(...)`;
`templates.py` will derive capsules from `edition.stories`,
`local_articles_by_story_id`, and the generated href map without adding app
payload fields or JSON artifacts.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing Pydantic
models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add optional
    `daily_local_article_capsules_article_hrefs_by_story_id: Mapping[str, str] | None = None`
    to `render_index_html(...)`.
  - Render `_render_daily_local_article_capsules(...)` after Stage 359
    `daily_local_heat_signals_section` and before
    `saved_article_content_organization_section`.
  - Add private capsule dataclasses/helpers and scoped CSS.
- Modify `src/fashion_radar/row_one/render.py`
  - Reuse `_local_article_page_hrefs_by_story_id(...)`.
  - Pass the existing story-id href map into `render_index_html(...)`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for capsule content, link safety, escaping,
    ordering, caps, placement, homepage-only site generation, and CSS.
- Modify `tests/test_workflows.py`
  - Add generated contract payload denylist entries, artifact stem guards, and
    a generated-site-only wrapper for Stage 360.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 360 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Homepage Capsule Rendering Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add section extraction helper**

Add near existing homepage section helpers:

```python
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
```

- [ ] **Step 2: Write failing direct render test**

Add `test_render_index_html_includes_daily_local_article_capsules`. Create an
edition with five stories:

```python
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
```

Use local articles:

```python
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
```

For the other first four stories, use `_signal_briefing_local_article().model_copy(...)`
with safe story IDs and titles. Give the fifth story a valid local article so
the test proves the four-card cap.

Call:

```python
html = render_index_html(
    edition,
    local_articles_by_story_id=local_articles_by_story_id,
    daily_local_article_capsules_article_hrefs_by_story_id={
        story.id: f"{story.id}.html" for story in stories
    },
)
```

Assert:
- `class="daily-local-article-capsules"` renders;
- `Daily Local Article Capsules` and `每日本地文章胶囊` render;
- first four story headlines render in edition order;
- the fifth story headline does not render;
- source, body-source label, why-it-matters, paragraph 1-3 excerpts, reference
  chips, and same-site links render;
- paragraph 4 does not render;
- links include
  `articles/article-capsule-1111111111.html#local-article-digest` and
  `articles/article-capsule-1111111111.html#local-article-paragraph-1`;
- raw `<script>`, `<b>`, and `<Business>` do not render.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_article_capsules \
  -q
```

Expected: fail because `render_index_html(...)` does not accept the new
argument and the section does not exist.

- [ ] **Step 3: Write failing filtering/link-safety test**

Add `test_render_index_html_filters_unsafe_daily_local_article_capsules` with:

- one safe story with local article and mapped href `"safe-capsule-1111111111.html"`;
- one story with unsafe ID `"unsafe/capsule-2222222222"`;
- one story with no local article;
- one story with empty `paragraphs`;
- one story whose mapped href is `"../secret.html"`;
- one story whose mapped href is a safe but mismatched filename
  `"other-capsule-3333333333.html"`.

Assert only the safe story renders and no unsafe/missing/empty/mismatched text
or href appears. Explicitly assert `"../secret"` and
`"other-capsule-3333333333.html"` are absent from the rendered HTML.

Run the test and expect failure.

- [ ] **Step 4: Write failing paragraph alignment test**

Add `test_render_index_html_daily_local_article_capsules_aligns_zh_paragraphs`
with one story whose saved local article has three English paragraphs but only
one `paragraphs_zh` entry. Assert paragraph 1 renders with both EN/ZH text,
paragraphs 2-3 still render with English excerpts, and missing ZH excerpts do
not leak stale or duplicated text from paragraph 1.

Run the test and expect failure.

- [ ] **Step 5: Write failing placement test**

Add `test_render_index_html_places_daily_local_article_capsules_between_sections`.
Use:

- app payload that renders Stage 359 `Daily Local Heat Signals`;
- local article data that renders Stage 360 capsules;
- saved article content organization fixture.

Assert:

```python
assert html.index('class="daily-local-heat-signals"') < html.index(
    'class="daily-local-article-capsules"'
)
assert html.index('class="daily-local-article-capsules"') < html.index(
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
daily_local_article_capsules_article_hrefs_by_story_id: Mapping[str, str] | None = None,
```

Compute:

```python
daily_local_article_capsules_section = _render_daily_local_article_capsules(
    edition,
    local_articles_by_story_id=local_articles_by_story_id,
    article_hrefs_by_story_id=daily_local_article_capsules_article_hrefs_by_story_id,
)
```

Insert between:

```html
{daily_local_heat_signals_section}
{saved_article_content_organization_section}
```

- [ ] **Step 2: Add capsule dataclasses**

Add near existing private render dataclasses:

```python
@dataclass(frozen=True)
class _DailyLocalArticleCapsuleParagraph:
    index: int
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class _DailyLocalArticleCapsule:
    title: LocalizedText
    source_name: str
    body_source: str
    why_it_matters: LocalizedText
    href: str
    paragraphs: tuple[_DailyLocalArticleCapsuleParagraph, ...]
    references: tuple[RowOneReference, ...]
```

`index` is zero-based internally; rendered paragraph fragments are one-based
through `_local_article_paragraph_anchor(index)`, so the first paragraph links
to `#local-article-paragraph-1`. Construct `title: LocalizedText` consistently
from the story headline and local article title fallback rather than mixing raw
strings with localized values.

- [ ] **Step 3: Add renderer helpers**

Add helpers near Stage 359 homepage helpers:

```python
DAILY_LOCAL_ARTICLE_CAPSULES_MAX_ITEMS = 4
DAILY_LOCAL_ARTICLE_CAPSULES_MAX_PARAGRAPHS = 3
DAILY_LOCAL_ARTICLE_CAPSULES_MAX_REFS = 6
DAILY_LOCAL_ARTICLE_CAPSULE_EXCERPT_CHARS = 150

def _render_daily_local_article_capsules(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str:
    capsules = _daily_local_article_capsules(
        edition,
        local_articles_by_story_id=local_articles_by_story_id,
        article_hrefs_by_story_id=article_hrefs_by_story_id,
    )
    if not capsules:
        return ""
    ...
```

Also add:

- `_daily_local_article_capsules(...)`
- `_daily_local_article_capsule_from_story(...)`
- `_daily_local_article_capsule_href(...)`
- `_safe_daily_local_article_capsule_page_href(...)`
- `_daily_local_article_capsule_paragraphs(...)`
- `_daily_local_article_capsule_excerpt(...)`
- `_daily_local_article_capsule_references(...)`
- `_render_daily_local_article_capsule(...)`
- `_render_daily_local_article_capsule_paragraph(...)`
- `_render_daily_local_article_capsule_ref(...)`

Safety rules:

- Validate story IDs with `safe_local_article_story_id(...)`.
- Validate mapped hrefs as one safe `.html` filename with no whitespace,
  traversal, leading dot, leading slash, or nested slash.
- Require mapped filename stem to equal the current story ID.
- Require `_usable_local_article_paragraph_count(article) > 0`.
- Link digest to `articles/<story-id>.html#local-article-digest`.
- Link paragraphs to `articles/<story-id>.html#local-article-paragraph-N`
  where `N` is one-based (`paragraph_index + 1`).
- Do not construct links from story ID alone.
- The href helper must guard `article_hrefs_by_story_id is None` before calling
  `.get(...)`, for example:

```python
def _daily_local_article_capsule_href(
    story_id: str,
    article_hrefs_by_story_id: Mapping[str, str] | None,
    *,
    fragment: str,
) -> str | None:
    if article_hrefs_by_story_id is None:
        return None
    page_href = _safe_daily_local_article_capsule_page_href(
        story_id,
        article_hrefs_by_story_id.get(story_id),
    )
    if page_href is None:
        return None
    return f"articles/{page_href}#{fragment}"
```

- [ ] **Step 4: Add scoped CSS**

Add selectors:

- `.daily-local-article-capsules`
- `.daily-local-article-capsules-header`
- `.daily-local-article-capsules-metrics`
- `.daily-local-article-capsules-grid`
- `.daily-local-article-capsule`
- `.daily-local-article-capsule-header`
- `.daily-local-article-capsule-title`
- `.daily-local-article-capsule-meta`
- `.daily-local-article-capsule-paragraphs`
- `.daily-local-article-capsule-paragraph`
- `.daily-local-article-capsule-refs`
- `.daily-local-article-capsule-link`

Add responsive rules:

```css
@media (min-width: 700px) {
  .daily-local-article-capsules-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.daily-local-article-capsules-header { grid-template-columns: 1fr; }
.daily-local-article-capsules-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 5: Verify direct render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_article_capsules \
  tests/test_row_one_render.py::test_render_index_html_filters_unsafe_daily_local_article_capsules \
  tests/test_row_one_render.py::test_render_index_html_daily_local_article_capsules_aligns_zh_paragraphs \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_article_capsules_between_sections \
  -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing homepage-only site test**

Add `test_render_row_one_site_writes_daily_local_article_capsules_homepage_only`.
Use an edition story with a saved local article. Render:

```python
render_row_one_site(
    edition,
    tmp_path,
    local_articles_by_story_id={story.id: _signal_briefing_local_article()},
)
```

Assert:

- `index.html` contains `class="daily-local-article-capsules"`;
- `articles/index.html`, `articles/<story-id>.html`, and the story detail page
  do not contain that class;
- generated contract payloads (`data/edition.json`, `data/manifest.json`,
  `data/runtime.json`) do not contain:
  - `daily_local_article_capsules`
  - `daily-local-article-capsules`
  - `Daily Local Article Capsules`
- no root/articles/data artifact exists for stems:
  - `daily-local-article-capsules`
  - `daily-local-capsules`
  - `article-capsules`
  - `daily_local_article_capsules`
  - `daily_local_capsules`
  - `article_capsules`

Run and expect failure because `render.py` does not pass the story-id map to the
homepage renderer yet.

- [ ] **Step 2: Pass href map from `render.py`**

In `render_row_one_site(...)`, reuse the already-computed
`local_article_page_hrefs_by_story_id` and pass:

```python
daily_local_article_capsules_article_hrefs_by_story_id=(
    local_article_page_hrefs_by_story_id
),
```

to `render_index_html(...)`.

- [ ] **Step 3: Verify site integration passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_article_capsules_homepage_only \
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

Insert before Stage 359 in both `README.md` and `docs/row-one.md`:

```markdown
Stage 360 adds generated-site only Daily Local Article Capsules as a homepage-only section inside `index.html` after Daily Local Heat Signals and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing body-source labels, existing story references, generated local article page routes, and existing paragraph anchors to turn saved local text into compact readable article cards without changing app-facing contracts; it does not create `data/daily-local-article-capsules.json`, does not create `data/daily-local-capsules.json`, does not create `data/article-capsules.json`, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs test**

Add `test_row_one_docs_describe_stage_360_daily_local_article_capsules_boundary`
before the Stage 359 docs test. Assert the Stage 360 paragraph exists in both
docs and includes generated-site-only, homepage-only, placement, reused data,
forbidden artifact stems, and stale phrase exclusions.

- [ ] **Step 3: Add workflow guard**

In `tests/test_workflows.py`, add Stage 360 denylist entries for generated
contract payloads and artifact stems. Add:

```python
def test_stage_360_daily_local_article_capsules_stays_generated_site_only(monkeypatch, tmp_path):
    monkeypatch.setattr(row_one_templates, "_render_daily_local_article_capsules", lambda *args, **kwargs: "")
    _assert_generated_site_only_surface(...)
```

Mirror the Stage 359 wrapper style and keep it render-only.

- [ ] **Step 4: Verify docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_360_daily_local_article_capsules_boundary \
  tests/test_workflows.py::test_stage_360_daily_local_article_capsules_stays_generated_site_only \
  -q
```

Expected: pass.

## Task 5: CSS Test and Focused Regression

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add CSS selector test**

Add `test_row_one_css_includes_daily_local_article_capsules_styles`.
Assert all selectors from Task 2 Step 4 exist.

- [ ] **Step 2: Run focused Stage 360 tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_article_capsules \
  tests/test_row_one_render.py::test_render_index_html_filters_unsafe_daily_local_article_capsules \
  tests/test_row_one_render.py::test_render_index_html_daily_local_article_capsules_aligns_zh_paragraphs \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_article_capsules_between_sections \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_article_capsules_homepage_only \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_local_article_capsules_styles \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_360_daily_local_article_capsules_boundary \
  tests/test_workflows.py::test_stage_360_daily_local_article_capsules_stays_generated_site_only \
  -q
```

Expected: pass.

## Task 6: Reviews, Full Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-360-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-360-code-review.md`

- [ ] **Step 1: Request code reviews**

Run Claude Code with `--effort max` against the current diff and save prompt
and output under `docs/reviews/`. Also dispatch Codex reviewer subagents with
`reasoning_effort: xhigh`.

- [ ] **Step 2: Fix valid review findings**

For every Critical/Important finding, add or adjust tests first, reproduce the
issue, fix implementation, and rerun focused tests.

- [ ] **Step 3: Run full gates**

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

- [ ] **Step 4: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  docs/reviews/claude-code-stage-360-*.md \
  docs/superpowers/plans/2026-07-09-stage-360-daily-local-article-capsules-plan.md \
  docs/superpowers/specs/2026-07-09-stage-360-daily-local-article-capsules-design.md
git commit -m "Stage 360: add daily local article capsules"
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \
  git -c http.version=HTTP/1.1 push origin main
```

- [ ] **Step 5: Handoff Summary**

Report:

- repo status;
- pushed commit;
- verified commands;
- uncommitted files;
- next recommended stage.
