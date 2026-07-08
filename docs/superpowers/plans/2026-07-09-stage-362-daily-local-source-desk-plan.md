# Stage 362 Daily Local Source Desk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage Daily Local Source Desk that
groups already-saved current-edition local articles by source/publication.

**Architecture:** Keep the feature render-only. `render.py` will pass the
existing safe story-id-to-local-article-page href map into `render_index_html`.
`templates.py` will derive source groups from `edition.stories`,
`local_articles_by_story_id`, story references, local article paragraphs,
body-source labels, and the generated href map. No builders, schemas, JSON
payloads, sidecars, routes, fetching, LLM, scheduling, or deployment behavior
are added.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing Pydantic
models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add optional
    `daily_local_source_desk_article_hrefs_by_story_id: Mapping[str, str] | None = None`
    to `render_index_html(...)`.
  - Render `_render_daily_local_source_desk(...)` after
    `daily_local_article_reading_brief_section` and before
    `saved_article_content_organization_section`.
  - Add private source-desk dataclasses/helpers and scoped CSS.
- Modify `src/fashion_radar/row_one/render.py`
  - Reuse `_local_article_page_hrefs_by_story_id(...)`.
  - Pass the existing story-id href map into `render_index_html(...)`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for grouping, ordering, caps, link safety, escaping,
    placement, homepage-only site generation, and CSS.
- Modify `tests/test_workflows.py`
  - Add generated contract payload denylist entries, artifact stem guards, and
    a generated-site-only wrapper for Stage 362.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 362 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Direct Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add section extraction helper**

Add near existing homepage section helpers:

```python
def _daily_local_source_desk_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-source-desk"'
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

Add `test_render_index_html_includes_daily_local_source_desk`. Build eight
stories using `_edition().stories[0].model_copy(deep=True, update={...})`.
Use these story/source pairs:

```python
[
    ("source-desk-vogue-1111111111", "Vogue <Business>"),
    ("source-desk-vogue-2222222222", "Vogue <Business>"),
    ("source-desk-vogue-3333333335", "Vogue <Business>"),
    ("source-desk-wwd-3333333333", "WWD"),
    ("source-desk-wwd-lower-3333333334", "wwd"),
    ("source-desk-bof-4444444444", "Business of Fashion"),
    ("source-desk-cut-5555555555", "The Cut"),
    ("source-desk-overflow-6666666666", "Zzz Overflow Source"),
]
```

Give the first story hostile and reference-rich values:

```python
"headline": "Source desk <script>",
"entity_refs": [
    RowOneReference(name="The Row", type="brand", label="brand"),
    RowOneReference(name="Brand <script>", type="brand", label="brand"),
],
"product_refs": [
    RowOneReference(name="Margaux bag", type="bag", label="product"),
],
"designer_refs": [
    RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer"),
    RowOneReference(name="Ashley Olsen", type="designer", label="designer"),
    RowOneReference(name="Miu Miu", type="brand", label="brand"),
    RowOneReference(name="Loewe", type="brand", label="brand"),
    RowOneReference(name="Ballet flat", type="shoe", label="product"),
],
```

Give the second Vogue story a duplicate `The Row` reference so the test can
assert the Vogue group renders that chip once after source-level reference
deduplication.

The fixture list intentionally includes three eligible Vogue stories in the
same source group. Give the first Vogue story more than five unique references
across `entity_refs`, `product_refs`, and `designer_refs`. This makes the
direct render test exercise both per-source link-pair capping and
reference-chip capping.

Create matching local articles. The two Vogue articles should together have
more saved paragraphs than the other sources so Vogue sorts first. Use hostile
text in source/title/paragraphs to prove escaping:

```python
_signal_briefing_local_article().model_copy(
    deep=True,
    update={
        "story_id": story.id,
        "title": f"{story.headline} source <script>",
        "source_name": source_name,
        "body_source": "extracted",
        "paragraphs": [
            "Opening source paragraph <b> for the source desk.",
            "Second source paragraph links the publication context.",
        ],
        "paragraphs_zh": [
            "第一段来源正文 <b> 用于来源台。",
            "第二段来源正文连接出版方背景。",
        ],
    },
)
```

Set one rendered eligible article, preferably the second Vogue article, to
`"title": None` so the null article-title path is inside the first two capped
Vogue link pairs.

Call:

```python
local_articles_by_story_id = {
    story.id: article for story, article in zip(stories, articles, strict=True)
}
html = render_index_html(
    _edition_with_stories(*stories),
    local_articles_by_story_id=local_articles_by_story_id,
    daily_local_source_desk_article_hrefs_by_story_id={
        story.id: f"{story.id}.html" for story in stories
    },
)
```

Assert:

- section class renders;
- `Daily Local Source Desk` and `每日本地来源台` render;
- Vogue appears before WWD, WWD before Business of Fashion, Business of Fashion
  and The Cut both render, and overflow source does not render because the
  source cap is four;
- source metrics render article and paragraph counts;
- body-source label renders bilingually with `Extracted article text` and
  `已提取文章正文`;
- reference chips render `The Row`, `Margaux bag`, and `Mary-Kate Olsen`;
- at least one reference chip contains hostile text such as
  `Brand <script>` and renders escaped as `Brand &lt;script&gt;`;
- the duplicate `The Row` reference appears once in the Vogue source group;
- only five unique reference chips render in the capped Vogue source group even
  though the fixture provides more than five unique references;
- only two article/paragraph link pairs render in the capped Vogue source group
  even though the fixture provides more than two eligible Vogue articles;
- the `WWD` and `wwd` stories merge into one source group because the grouping
  key is `normalized_source_name.casefold()`, the merged source display name is
  the first normalized value seen (`WWD`), and that group shows an article count
  of two;
- same-site links include
  `articles/source-desk-vogue-1111111111.html#local-article-digest` and
  `articles/source-desk-vogue-1111111111.html#local-article-paragraph-1`;
- paragraph link labels render bilingually with `Paragraph 1` and `段落 1`;
- the article whose `article_title` is `None` renders a story-headline fallback
  or omits the article-title sublabel without emitting the literal text `None`;
- no saved paragraph body excerpt appears inside the Source Desk; paragraph
  links are labels only;
- hostile strings render escaped and raw `<script>`, `<b>`, and `<Business>`
  do not appear;
- `https://example.com` does not appear.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_source_desk \
  -q
```

Expected: fail because the new argument and section do not exist.

- [ ] **Step 3: Write failing filtering/link-safety test**

Add `test_render_index_html_filters_unsafe_daily_local_source_desk` with:

- one safe story with local article and mapped href
  `"safe-source-desk-1111111111.html"`;
- one unsafe story id `"unsafe/source-desk-2222222222"`;
- one story whose local article `story_id` mismatches;
- one story with no local article;
- one story with blank source name;
- one story with empty `paragraphs`;
- one story whose mapped href is `"../secret.html"`;
- one story whose mapped href is `"nested/story.html"`;
- one story whose mapped href is `".hidden.html"`;
- one story whose mapped href is `"/absolute.html"`;
- one story whose mapped href is `"white space.html"`;
- one story whose mapped href is `"//hidden.html"`;
- one story whose mapped href is `"."`;
- one story whose mapped href is `".."`;
- one story whose mapped href is `None`;
- one story whose mapped href is `123`;
- one story whose mapped href is `"mismatch-source-desk-3333333333.html"`.

Assert only the safe source/story renders and no unsafe/missing/empty/traversal/
nested/hidden/mismatched text or href appears. Include an explicit assertion
that the mismatched local article's unique source name does not appear in the
rendered HTML.

Run the test and expect failure.

- [ ] **Step 4: Write failing empty-section test**

Add `test_render_index_html_omits_daily_local_source_desk_without_eligible_articles`.
Parametrize three cases: one edition with no `local_articles_by_story_id`, one
edition whose articles all fail eligibility because the same fixture combines
blank source names and unsafe hrefs, and one edition with eligible local
articles but `daily_local_source_desk_article_hrefs_by_story_id=None`. Include
an additional empty-map case with
`daily_local_source_desk_article_hrefs_by_story_id={}` if the parametrize shape
is cleaner with four cases. Assert:

```python
assert 'class="daily-local-source-desk"' not in html
assert "Daily Local Source Desk" not in html
```

Run the test and expect failure if the new render argument has already been
added; otherwise expect a missing-argument failure.

- [ ] **Step 5: Write failing placement test**

Add `test_render_index_html_places_daily_local_source_desk_between_sections`.
Render Daily Local Article Reading Brief, Daily Local Source Desk, and Saved
Article Content Organization by passing the same safe story id href map to
`daily_local_article_reading_brief_article_hrefs_by_story_id` and
`daily_local_source_desk_article_hrefs_by_story_id`, alongside matching
eligible local articles. Build and pass a non-`None`
`saved_article_content_organization` object with
`build_row_one_saved_article_content_organization(edition, local_articles_by_story_id)`;
make sure at least one fixture article has populated `content_sections` so the
Saved Article Content Organization section renders. Assert:

```python
assert 'class="saved-article-content-organization"' in html, (
    "fixture must produce a rendered Saved Article Content Organization"
)
assert html.index('class="daily-local-article-reading-brief"') < html.index(
    'class="daily-local-source-desk"'
)
assert html.index('class="daily-local-source-desk"') < html.index(
    'class="saved-article-content-organization"'
)
```

Run the test and expect failure.

- [ ] **Step 6: Write failing placement test without reading brief**

Add `test_render_index_html_places_daily_local_source_desk_before_saved_organization_without_reading_brief`.
Render a Source Desk and Saved Article Content Organization, but do not pass
`daily_local_article_reading_brief_article_hrefs_by_story_id`. Still pass the
same safe story id href map to
`daily_local_source_desk_article_hrefs_by_story_id`, alongside matching
eligible local articles. Build and pass a non-`None`
`saved_article_content_organization` object with
`build_row_one_saved_article_content_organization(edition, local_articles_by_story_id)`;
make sure at least one fixture article has populated `content_sections` so the
Saved Article Content Organization section renders. Assert:

```python
assert 'class="saved-article-content-organization"' in html, (
    "fixture must produce a rendered Saved Article Content Organization"
)
assert 'class="daily-local-article-reading-brief"' not in html
assert html.index('class="daily-local-source-desk"') < html.index(
    'class="saved-article-content-organization"'
)
```

Run the test and expect failure.

## Task 2: Template Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add constants and dataclasses**

Add near Stage 360/361 constants:

```python
DAILY_LOCAL_SOURCE_DESK_MAX_SOURCES = 4
DAILY_LOCAL_SOURCE_DESK_MAX_LINKS_PER_SOURCE = 2
DAILY_LOCAL_SOURCE_DESK_MAX_REFS_PER_SOURCE = 5
```

Add dataclasses near the Stage 361 private dataclasses:

```python
@dataclass(frozen=True)
class _DailyLocalSourceDeskLink:
    story_headline: str
    article_title: str | None
    href: str
    paragraph_href: str
    paragraph_number: int


@dataclass(frozen=True)
class _DailyLocalSourceDeskReference:
    name: str
    label: str


@dataclass(frozen=True)
class _DailyLocalSourceDeskSource:
    source_name: str
    article_count: int
    saved_paragraph_count: int
    body_source_labels: tuple[LocalizedText, ...]
    references: tuple[_DailyLocalSourceDeskReference, ...]
    links: tuple[_DailyLocalSourceDeskLink, ...]
```

- [ ] **Step 2: Wire `render_index_html(...)`**

Add argument:

```python
daily_local_source_desk_article_hrefs_by_story_id: Mapping[str, str] | None = None,
```

After `daily_local_article_reading_brief_section`, compute:

```python
daily_local_source_desk_section = _render_daily_local_source_desk(
    edition,
    local_articles_by_story_id=local_articles_by_story_id,
    article_hrefs_by_story_id=daily_local_source_desk_article_hrefs_by_story_id,
)
```

Insert `{daily_local_source_desk_section}` after
`{daily_local_article_reading_brief_section}` and before
`{saved_article_content_organization_section}`.

- [ ] **Step 3: Add safe href helper**

Use the same safety rules as Stage 361:

```python
def _safe_daily_local_source_desk_page_href(
    story_id: str,
    href: object,
) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
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
    return f"{mapped_story_id}.html"
```

Then add two concrete href helpers, with no arbitrary free-form fragment
parameter:

```python
def _daily_local_source_desk_digest_href(
    story_id: str,
    href: object,
) -> str | None:
    page_href = _safe_daily_local_source_desk_page_href(story_id, href)
    if page_href is None:
        return None
    return f"articles/{page_href}#local-article-digest"


def _daily_local_source_desk_paragraph_href(
    story_id: str,
    href: object,
    paragraph_number: int,
) -> str | None:
    page_href = _safe_daily_local_source_desk_page_href(story_id, href)
    if page_href is None or paragraph_number < 1:
        return None
    return f"articles/{page_href}#local-article-paragraph-{paragraph_number}"
```

The explicit `"//"` tuple member is redundant with `"/"` but intentionally
keeps the Stage 361 helper shape and makes the leading double-slash filter
obvious beside the `"//hidden.html"` test fixture.

- [ ] **Step 4: Build source groups**

Implement `_daily_local_source_desk_sources(...)`:

```python
def _daily_local_source_desk_sources(
    edition: RowOneEdition,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None,
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> list[_DailyLocalSourceDeskSource]:
    if not article_hrefs_by_story_id:
        return []
    ...
```

- iterate `edition.stories` in order;
- return an empty list immediately when `article_hrefs_by_story_id` is `None`
  or empty;
- reject unsafe ids;
- require `article is not None`;
- require `article.story_id == story.id`;
- require `_usable_local_article_paragraph_count(article) > 0`;
- require normalized `article.source_name`, where normalized means
  `normalize_row_one_paragraph(article.source_name)`;
- require safe digest and first-paragraph hrefs from supplied href map;
- compute the first paragraph link with the 1-based index of the first nonblank
  entry in `article.paragraphs`, using
  `next(index for index, paragraph in enumerate(article.paragraphs, start=1) if paragraph.strip())`;
- group by `normalized_source_name.casefold()`;
- store the first normalized source name seen for that grouping key as the
  source display name;
- count articles and usable paragraphs;
- sum `_usable_local_article_paragraph_count(article)` across all eligible
  articles in the same source group for `saved_paragraph_count`;
- collect body-source labels with `row_one_body_source_label(article.body_source)`;
  dedupe labels by `(label.en.casefold(), label.zh.casefold())` in source-story
  order before storing them on `_DailyLocalSourceDeskSource`. Do not add a
  separate body-source label cap constant because the known label set currently
  has three values. Do not add a separate `article.skipped` override here:
  source rows require at least one usable saved paragraph, and
  `row_one_body_source_label(article.body_source)` already handles articles
  whose `body_source` is `"skipped"`;
- collect refs from `story.entity_refs`, `story.product_refs`, and
  `story.designer_refs`, deduped across stories in the source group by
  `(normalize_row_one_paragraph(ref.name).casefold(),
  normalize_row_one_paragraph(ref.type).casefold(),
  normalize_row_one_paragraph(ref.label).casefold())`, capped to
  `DAILY_LOCAL_SOURCE_DESK_MAX_REFS_PER_SOURCE`;
- collect links in story order, capped to
  `DAILY_LOCAL_SOURCE_DESK_MAX_LINKS_PER_SOURCE`. Each
  `_DailyLocalSourceDeskLink` intentionally pairs one article digest link with
  one paragraph link, stores `story.headline` in `story_headline`, stores
  `article.title` in `article_title` as `str | None`, uses the index of the
  first nonblank paragraph in `article.paragraphs` as the 1-indexed
  `paragraph_number`, and the cap means up to two article/paragraph link pairs
  per source group;
- sort and cap sources with this exact tuple:
  `(-source.article_count, -source.saved_paragraph_count,
  source.source_name.casefold(), source.source_name)`.

Reuse the existing `_usable_local_article_paragraph_count(...)` helper in
`templates.py`; it counts nonblank saved local article paragraphs and is already
used by Stage 360 and Stage 361 homepage render helpers.

- [ ] **Step 5: Render source desk HTML**

Render:

```html
<section class="daily-local-source-desk" aria-label="Daily local source desk">
```

Header copy:

- EN kicker: `Daily Local Source Desk`
- ZH kicker: `每日本地来源台`
- EN headline: `Which sources carried today&apos;s saved local articles`
- ZH headline: `哪些来源承载了今天的本地保存文章`

Render metrics:

- number of sources;
- number of local articles;
- number of saved paragraphs;
- `Homepage only` / `仅首页展示`.

Render each source as `.daily-local-source-desk-source` with:

- `.daily-local-source-desk-grid` wrapper around source cards;
- `.daily-local-source-desk-source-header`;
- `.daily-local-source-desk-source-title`;
- `.daily-local-source-desk-counts`;
- `.daily-local-source-desk-body-sources`;
- `.daily-local-source-desk-refs`;
- `.daily-local-source-desk-links`;
- `.daily-local-source-desk-link`;
- `.daily-local-source-desk-paragraph-link`.

Local article links should show story/local article title metadata. If
`article_title is None`, use the story headline as the visible title fallback or
omit the article-title sublabel; never render the literal text `None`.
Paragraph links should show paragraph numbers only, for example `Paragraph 1` /
`段落 1`. Do not render saved paragraph excerpts in this homepage section.

- [ ] **Step 6: Add scoped CSS**

Add selectors:

```text
.daily-local-source-desk
.daily-local-source-desk-header
.daily-local-source-desk-metrics
.daily-local-source-desk-grid
.daily-local-source-desk-source
.daily-local-source-desk-source-header
.daily-local-source-desk-source-title
.daily-local-source-desk-counts
.daily-local-source-desk-body-sources
.daily-local-source-desk-refs
.daily-local-source-desk-ref
.daily-local-source-desk-links
.daily-local-source-desk-link
.daily-local-source-desk-paragraph-link
```

Use the established Stage 360/361 section styling:
`.daily-local-source-desk-grid` is the grid container, with one column by
default, two columns at `@media (min-width: 700px)`, and one column under the
mobile media query.

## Task 3: Site Wiring And Integration Tests

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Pass href map from `render_row_one_site(...)`**

In the `render_index_html(...)` call, add:

```python
daily_local_source_desk_article_hrefs_by_story_id=(
    local_article_page_hrefs_by_story_id
),
```

- [ ] **Step 2: Add homepage-only generated-site test**

Add `test_render_row_one_site_writes_daily_local_source_desk_homepage_only`.
Build one or two local articles from different sources and call
`render_row_one_site(...)`. Use the Task 1 eligible fixture shape: safe story
ids, nonblank source names, and at least one nonblank paragraph so the internal
local article page href map is generated. Assert:

- homepage `index.html` contains `Daily Local Source Desk`;
- homepage `index.html` contains `class="daily-local-source-desk"`;
- homepage section links to `articles/<story-id>.html#local-article-digest`;
- `articles/index.html`, `articles/<story-id>.html`, and `details/<story-id>.html`
  do not contain `class="daily-local-source-desk"`;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain `daily_local_source_desk`, `daily-local-source-desk`, or
  `Daily Local Source Desk`;
- no files named any of these stems exist in the root, `articles`, or `data`
  directories:

```python
(
    "daily-local-source-desk",
    "local-source-desk",
    "source-desk",
    "daily_local_source_desk",
    "local_source_desk",
    "source_desk",
)
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_source_desk_homepage_only \
  -q
```

Expected: fail until `render.py` is wired.

- [ ] **Step 3: Add CSS test**

Add `test_row_one_css_includes_daily_local_source_desk_styles` and assert every
selector from Task 2 Step 6 appears in `row_one_css()`.

## Task 4: Workflow And Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add workflow generated-site-only guard**

Add `test_stage_362_daily_local_source_desk_stays_generated_site_only`.
Follow the Stage 361 test shape. Denylist:

```python
(
    "daily_local_source_desk",
    "daily-local-source-desk",
    "Daily Local Source Desk",
    "local_source_desk",
    "local-source-desk",
    "source_desk",
    "source-desk",
)
```

Forbidden artifact stems:

```python
(
    "daily-local-source-desk",
    "local-source-desk",
    "source-desk",
    "daily_local_source_desk",
    "local_source_desk",
    "source_desk",
)
```

Assert the Stage 362 render helper is in `templates.py`, no contract payloads
contain the denylist, and no forbidden artifacts are expected under root,
`articles`, or `data`.

- [ ] **Step 2: Add docs drift test**

Add `test_row_one_docs_describe_stage_362_daily_local_source_desk_boundary`.
Assert both `README.md` and `docs/row-one.md` contain:

- `Stage 362`;
- `Daily Local Source Desk`;
- `daily-local-source-desk`;
- `does not create \`data/daily-local-source-desk.json\``;
- `does not create \`data/local-source-desk.json\``;
- `does not create \`data/source-desk.json\``;
- `does not change schemas`;
- `does not add fetching`;
- `does not add outbound article URLs as primary navigation`;
- `does not add compliance-review behavior`.

- [ ] **Step 3: Update docs**

The docs list recent ROW ONE stages newest-first. Insert a Stage 362 paragraph
immediately before Stage 361 in both README and `docs/row-one.md`:

```text
Stage 362 adds generated-site only Daily Local Source Desk as a homepage-only section inside `index.html` after Daily Local Article Reading Brief and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing body-source labels, existing story references, generated local article page routes, and existing paragraph anchors to group saved local text by source/publication with article counts, saved paragraph counts, body-source labels, reference chips, and same-site article/paragraph links without changing app-facing contracts; it does not create `data/daily-local-source-desk.json`, does not create `data/local-source-desk.json`, does not create `data/source-desk.json`, does not create new route families, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
```

## Task 5: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-362-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-362-plan-review.md`

- [ ] **Step 1: Write the Claude Code plan review prompt**

Create a prompt that includes:

- goal: generated-site-only Daily Local Source Desk;
- tech stack: Python/pytest/ruff/ROW ONE renderer;
- implementation plan path;
- design path;
- explicit non-goals and boundary checks;
- request for Critical/Important/Minor findings only.

- [ ] **Step 2: Run Claude Code plan review**

Run:

```bash
claude --print --effort max --tools "" --no-session-persistence < \
  docs/reviews/claude-code-stage-362-plan-review-prompt.md \
  > docs/reviews/claude-code-stage-362-plan-review.md
```

- [ ] **Step 3: Fix Critical and Important plan findings**

If the plan review reports Critical or Important findings, edit the spec/plan
and rerun review until no Critical/Important findings remain.

## Task 6: Focused Verification Before Code Review

**Files:**
- All touched files

- [ ] **Step 1: Run focused Stage 362 suite**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_source_desk \
  tests/test_row_one_render.py::test_render_index_html_filters_unsafe_daily_local_source_desk \
  tests/test_row_one_render.py::test_render_index_html_omits_daily_local_source_desk_without_eligible_articles \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_source_desk_between_sections \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_source_desk_before_saved_organization_without_reading_brief \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_source_desk_homepage_only \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_local_source_desk_styles \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_362_daily_local_source_desk_boundary \
  tests/test_workflows.py::test_stage_362_daily_local_source_desk_stays_generated_site_only \
  -q
```

Expected: all pass after implementation.

- [ ] **Step 2: Run touched-file lint and format checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check \
  src/fashion_radar/row_one/templates.py \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check \
  src/fashion_radar/row_one/templates.py \
  src/fashion_radar/row_one/render.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py
```

## Task 7: Code Review, Full Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-362-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-362-code-review.md`

- [ ] **Step 1: Request code review**

Run Claude Code with `--effort max` against the current worktree. Ask it to
review generated-site-only boundaries, source grouping correctness, href
safety, escaping, caps, docs, tests, and contract/artifact omissions.

- [ ] **Step 2: Request Codex reviewer subagent**

Spawn a read-only reviewer with `reasoning_effort: xhigh`. Ask for Critical,
Important, and Minor findings only. Close the agent after receiving results.

- [ ] **Step 3: Fix Critical and Important findings**

Fix every Critical and Important finding. Re-run the focused suite from Task 6
after each fix batch.

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

- [ ] **Step 5: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  docs/reviews/claude-code-stage-362-*.md \
  docs/superpowers/plans/2026-07-09-stage-362-daily-local-source-desk-plan.md \
  docs/superpowers/specs/2026-07-09-stage-362-daily-local-source-desk-design.md
git commit -m "Stage 362: add daily local source desk"
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \
  git -c http.version=HTTP/1.1 push origin main
```

## Self-Review

- Spec coverage: every design requirement is covered by Tasks 1-7.
- Placeholder scan: no TODO/TBD placeholders remain.
- Type consistency: all helper names use `daily_local_source_desk`; href maps
  are keyed by story id; rendered links use existing article and paragraph
  anchors only.
- Boundary check: no task adds contracts, schemas, JSON artifacts, routes,
  fetching, LLM, scheduling, analytics, or compliance-review behavior.
