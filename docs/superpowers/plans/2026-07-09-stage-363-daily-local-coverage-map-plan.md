# Stage 363 Daily Local Coverage Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage Daily Local Coverage Map that cross-tabs already-saved local article sources against existing saved article organization buckets.

**Architecture:** Keep the feature render-only. `render.py` will pass the existing safe detail-path-to-local-article-page href map into `render_index_html`. `templates.py` will derive coverage rows from the current `RowOneSavedArticleContentOrganization`, saved local articles, current-edition stories, existing card references, paragraph indices, and generated href maps. No builders, schemas, JSON payloads, sidecars, routes, fetching, LLM, scheduling, analytics, personalization, recommendation, or compliance-review behavior are added.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing Pydantic models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add optional `daily_local_coverage_map_hrefs_by_detail_path: Mapping[str, str] | None = None` to `render_index_html(...)`.
  - Render `_render_daily_local_coverage_map(...)` after `daily_local_source_desk_section` and before `saved_article_content_organization_section`.
  - Add private coverage-map dataclasses/helpers and scoped CSS.
- Modify `src/fashion_radar/row_one/render.py`
  - Reuse `_local_article_page_hrefs_by_detail_path(...)`.
  - Pass the existing detail-path href map into `render_index_html(...)`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for grouping, ordering, caps, link safety, escaping, placement, homepage-only site generation, and CSS.
- Modify `tests/test_workflows.py`
  - Add generated contract payload denylist entries, artifact stem guards, and a generated-site-only wrapper for Stage 363.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 363 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Direct Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add section extraction helper**

Add near existing homepage section helpers:

```python
def _daily_local_coverage_map_section_html(index_html: str) -> str:
    marker = '<section class="daily-local-coverage-map"'
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

Add `test_render_index_html_includes_daily_local_coverage_map`. Build an edition with five safe stories and one overflow story. Give multiple organization cards across sources and buckets:

- `Vogue <Business>` with cards in `Read First`, `People & Brands`, and `Products`.
- `WWD` and `wwd` cards that should merge into one source row.
- `Business of Fashion` and `The Cut` as additional eligible rows.
- `Overflow Source` as a fifth eligible source that should be capped out.

Use `RowOneSavedArticleContentOrganization` directly with groups containing `RowOneSavedArticleContentOrganizationCard` entries. Cards should include:

- hostile text in source names, titles, section labels, and references;
- duplicate references such as `The Row` across Vogue cards;
- paragraph indices `(0, 1)` for anchor fallback coverage;
- detail paths like `details/source-map-vogue-1111111111.html#local-article-content-section-1`.

Call `render_index_html(...)` with:

```python
html = render_index_html(
    edition,
    saved_article_content_organization=organization,
    local_articles_by_story_id=local_articles_by_story_id,
    daily_local_source_desk_article_hrefs_by_story_id={
        story.id: f"{story.id}.html" for story in stories
    },
    daily_local_coverage_map_hrefs_by_detail_path={
        f"details/{story.id}.html": f"{story.id}.html" for story in stories
    },
)
```

Assert:

- `class="daily-local-coverage-map"` renders;
- `Daily Local Coverage Map` and `每日本地覆盖地图` render;
- Vogue appears before WWD, WWD before Business of Fashion, and overflow source does not render;
- source metrics show bucket/article/paragraph counts;
- bucket chips render group titles and support counts;
- duplicate `The Row` reference renders once in the Vogue row;
- hostile reference text renders escaped and raw `<script>`/`<Business>` do not appear;
- same-site hrefs include `articles/source-map-vogue-1111111111.html#local-article-content-section-1`;
- a paragraph fallback href renders as `articles/source-map-vogue-2222222222.html#local-article-paragraph-2` when the card detail path lacks a safe content-section fragment;
- no saved paragraph body excerpt appears in the section;
- `https://example.com` does not appear.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_coverage_map \
  -q
```

Expected: fail because the new render argument and section do not exist.

- [ ] **Step 3: Write failing filtering/link-safety test**

Add `test_render_index_html_filters_unsafe_daily_local_coverage_map` with one safe card and cards that should be filtered for:

- unsafe story id in detail path;
- detail path not under `details/`;
- absolute detail path;
- traversal detail path;
- nested malformed local article href;
- whitespace local article href;
- leading slash/dot/double-slash local article href;
- mismatched local article href stem;
- missing href map entry;
- missing local article;
- mismatched local article story id;
- blank source name;
- empty local article paragraphs.

Assert only the safe source/card renders and all unsafe labels/hrefs are absent.

- [ ] **Step 4: Write failing empty-section test**

Add `test_render_index_html_omits_daily_local_coverage_map_without_eligible_cards` covering:

- `saved_article_content_organization=None`;
- no local articles;
- eligible cards but `daily_local_coverage_map_hrefs_by_detail_path=None`;
- eligible cards but empty href map;
- eligible local articles but all cards filtered.

Assert the section class and title do not render.

- [ ] **Step 5: Write failing placement tests**

Add two tests:

1. `test_render_index_html_places_daily_local_coverage_map_between_source_desk_and_saved_organization` proving order is Source Desk, Coverage Map, Saved Article Content Organization.
2. `test_render_index_html_places_daily_local_coverage_map_before_saved_organization_without_source_desk` proving Coverage Map still renders before Saved Article Content Organization when Source Desk is absent.

## Task 2: Template Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add constants and dataclasses**

Add near Stage 360-362 constants:

```python
DAILY_LOCAL_COVERAGE_MAP_MAX_SOURCES = 4
DAILY_LOCAL_COVERAGE_MAP_MAX_BUCKETS_PER_SOURCE = 4
DAILY_LOCAL_COVERAGE_MAP_MAX_REFS_PER_SOURCE = 5
DAILY_LOCAL_COVERAGE_MAP_MAX_LINKS_PER_SOURCE = 2
```

Add dataclasses near `_DailyLocalSourceDeskSource`:

```python
@dataclass(frozen=True)
class _DailyLocalCoverageMapBucket:
    title: LocalizedText
    support_count: int


@dataclass(frozen=True)
class _DailyLocalCoverageMapLink:
    title: LocalizedText
    source_name: str
    href: str
    bucket_title: LocalizedText


@dataclass(frozen=True)
class _DailyLocalCoverageMapSource:
    source_name: str
    bucket_count: int
    article_count: int
    saved_paragraph_count: int
    buckets: tuple[_DailyLocalCoverageMapBucket, ...]
    references: tuple[RowOneReference, ...]
    links: tuple[_DailyLocalCoverageMapLink, ...]
```

- [ ] **Step 2: Add render entrypoint and placement**

Add `daily_local_coverage_map_hrefs_by_detail_path` to `render_index_html(...)` after Stage 362's source-desk href argument. Build:

```python
daily_local_coverage_map_section = _render_daily_local_coverage_map(
    saved_article_content_organization,
    local_articles_by_story_id=local_articles_by_story_id,
    hrefs_by_detail_path=daily_local_coverage_map_hrefs_by_detail_path,
)
```

Insert `{daily_local_coverage_map_section}` after `{daily_local_source_desk_section}` and before `{saved_article_content_organization_section}`.

- [ ] **Step 3: Implement coverage derivation helpers**

Implement `_daily_local_coverage_map_sources(...)` that:

- returns `()` when organization, local articles, or href map is absent;
- iterates organization groups/cards in existing order;
- normalizes and groups source names with `casefold()`;
- extracts a story id from safe `details/<story-id>.html` detail paths;
- validates the matching local article exists, story id matches, and has usable paragraphs;
- validates the supplied href is one safe single-file local article html filename whose stem equals the story id;
- builds a content-section href from `#local-article-content-section-N` when present and safe;
- otherwise builds a paragraph href from the first safe paragraph index in `card.paragraph_indices`;
- aggregates bucket support counts, unique article ids, saved paragraph totals, references, and capped links.

Use existing helpers where possible: `normalize_row_one_paragraph`, `_usable_local_article_paragraph_count`, `safe_local_article_story_id`, `RowOneReference`, `_count_label`, and `PurePosixPath`.

- [ ] **Step 4: Implement HTML helpers**

Implement:

- `_render_daily_local_coverage_map(...)`
- `_render_daily_local_coverage_map_source(...)`
- `_render_daily_local_coverage_map_bucket(...)`
- `_render_daily_local_coverage_map_ref(...)`
- `_render_daily_local_coverage_map_link(...)`

Keep markup compact and bilingual. Escape all visible text and hrefs. Do not render saved paragraph body excerpts.

- [ ] **Step 5: Add CSS**

Add scoped CSS near Stage 362 styles for:

- `.daily-local-coverage-map`
- `.daily-local-coverage-map-header`
- `.daily-local-coverage-map-metrics`
- `.daily-local-coverage-map-grid`
- `.daily-local-coverage-map-source`
- `.daily-local-coverage-map-source-header`
- `.daily-local-coverage-map-counts`
- `.daily-local-coverage-map-buckets`
- `.daily-local-coverage-map-bucket`
- `.daily-local-coverage-map-refs`
- `.daily-local-coverage-map-ref`
- `.daily-local-coverage-map-links`
- `.daily-local-coverage-map-link`

Add responsive grid handling beside Stage 362 responsive rules.

## Task 3: Render Pipeline and Site Tests

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Pass href map from site renderer**

In `render_row_one_site`, pass:

```python
daily_local_coverage_map_hrefs_by_detail_path=(
    local_article_page_hrefs_by_detail_path
),
```

into `render_index_html(...)`.

- [ ] **Step 2: Add homepage-only site-generation test**

Add `test_render_row_one_site_writes_daily_local_coverage_map_homepage_only` modeled on Stage 362. Assert:

- homepage contains `class="daily-local-coverage-map"`;
- `articles/index.html`, `articles/<story-id>.html`, and detail pages do not contain the section;
- generated contract payload does not contain `daily_local_coverage_map` or `daily-local-coverage-map`;
- no `data/daily-local-coverage-map.json`, `data/local-coverage-map.json`, or `data/coverage-map.json` exists.

- [ ] **Step 3: Add CSS selector test**

Add `test_row_one_css_includes_daily_local_coverage_map_styles` with the selectors from Task 2 Step 5.

## Task 4: Workflow and Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Extend artifact denylist**

Add these stems to existing generated-site-only artifact denylist:

```python
"daily-local-coverage-map",
"daily-local-coverage",
"local-coverage-map",
"coverage-map",
"daily_local_coverage_map",
"daily_local_coverage",
"local_coverage_map",
"coverage_map",
```

- [ ] **Step 2: Add workflow wrapper**

Add:

```python
def test_stage_363_daily_local_coverage_map_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    monkeypatch.setattr(
        row_one_templates,
        "_render_daily_local_coverage_map",
        lambda *_args, **_kwargs: "",
        raising=False,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

- [ ] **Step 3: Add docs boundary entry**

Prepend Stage 363 text before Stage 362 in both README and `docs/row-one.md`:

```text
Stage 363 adds generated-site only Daily Local Coverage Map as a homepage-only section inside `index.html` after Daily Local Source Desk and before Saved Article Content Organization; it reuses current-edition stories, already-saved local article paragraphs, existing saved article content organization groups and cards, existing source names, existing card references, generated local article page routes, and existing local content-section and paragraph anchors to organize saved local text into a compact source-by-organization-bucket coverage map without changing app-facing contracts; it does not create `data/daily-local-coverage-map.json`, does not create `data/local-coverage-map.json`, does not create `data/coverage-map.json`, does not create new route families, does not publish full articles on the homepage, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 4: Add docs test**

Add `test_row_one_docs_describe_stage_363_daily_local_coverage_map_boundary` modeled on Stage 362. Include stale-phrase guards for the new JSON artifact names, route families, schema versions, outbound primary navigation, full homepage articles, and disallowed behavior families.

## Task 5: Reviews, Verification, Commit, Push

**Files:**
- Add: `docs/reviews/2026-07-09-stage-363-daily-local-coverage-map-plan-claude.md`
- Add: `docs/reviews/2026-07-09-stage-363-daily-local-coverage-map-code-claude.md`
- Add: `docs/reviews/2026-07-09-stage-363-daily-local-coverage-map-code-codex.md`

- [ ] **Step 1: Run focused tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_coverage_map \
  tests/test_row_one_render.py::test_render_index_html_filters_unsafe_daily_local_coverage_map \
  tests/test_row_one_render.py::test_render_index_html_omits_daily_local_coverage_map_without_eligible_cards \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_coverage_map_between_source_desk_and_saved_organization \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_coverage_map_before_saved_organization_without_source_desk \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_coverage_map_homepage_only \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_local_coverage_map_styles \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_363_daily_local_coverage_map_boundary \
  tests/test_workflows.py::test_stage_363_daily_local_coverage_map_stays_generated_site_only \
  -q
```

Expected after implementation: pass.

- [ ] **Step 2: Run lint/format focused gates**

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

Expected: pass.

- [ ] **Step 3: Run full gates**

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

Expected: pass.

- [ ] **Step 4: Commit and push**

```bash
git add src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py \
  tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py \
  README.md docs/row-one.md docs/superpowers/specs/2026-07-09-stage-363-daily-local-coverage-map-design.md \
  docs/superpowers/plans/2026-07-09-stage-363-daily-local-coverage-map-plan.md docs/reviews

git commit -m "Stage 363: add daily local coverage map"

env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  GIT_TERMINAL_PROMPT=0 git -c http.proxy= -c https.proxy= \
  -c http.curloptResolve=github.com:443:140.82.112.3 push origin main
```

Expected: commit and push succeed.
