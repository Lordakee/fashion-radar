# Stage 353 Saved Article Read Next Clusters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Saved Article Read Next Clusters section that organizes existing saved local articles into compact topical clusters inside `articles/index.html`.

**Architecture:** Build a small in-memory cluster model from existing saved article library entries and saved content-organization cards. Render it only on the saved article library page, using safe local article page digest links or same-site content-section/digest fallback anchors. Do not add persisted artifacts, app contracts, schemas, route families, ranking, recommendation, scraping, extraction, LLM calls, scheduling, deployment, analytics, personalization, or compliance-review behavior.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Create `src/fashion_radar/row_one/saved_article_read_next_clusters.py`
  - Add `SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT = 3`.
  - Add `SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT = 3`.
  - Add `SAVED_ARTICLE_READ_NEXT_CLUSTER_REFERENCE_LIMIT = 4`.
  - Add frozen dataclasses:
    - `RowOneSavedArticleReadNextClusterItem`
    - `RowOneSavedArticleReadNextCluster`
    - `RowOneSavedArticleReadNextClusters`
  - Add `build_row_one_saved_article_read_next_clusters(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import the builder and dataclasses.
  - Build clusters in `render_saved_article_library_html(...)` from existing `library`, existing `saved_article_content_organization`, and existing `local_article_page_hrefs_by_detail_path`.
  - Add `_render_saved_article_read_next_clusters(...)`.
  - Render after `{reading_queue}` and before `{signal_facets}`.
  - Add CSS selectors for section, header, metrics, grid, cluster, item, meta, lead, refs, and action link.
- Add `tests/test_row_one_saved_article_read_next_clusters.py`.
- Modify `tests/test_row_one_render.py`.
- Modify `tests/test_workflows.py`.
- Modify `tests/test_row_one_docs.py`.
- Modify `README.md` and `docs/row-one.md`.
- Add `docs/reviews/claude-code-stage-353-plan-review-prompt.md`.
- Add `docs/reviews/opencode-stage-353-plan-review-prompt.md`.

## Task 1: Write Failing Builder Tests

**Files:**
- Create: `tests/test_row_one_saved_article_read_next_clusters.py`

- [ ] **Step 1: Add fixtures**

Create helpers using:

- `LocalizedText`
- `RowOneReference`
- `RowOneSavedArticleLibrary`
- `RowOneSavedArticleLibraryEntry`
- `RowOneSavedArticleLibrarySourceGroup`
- `RowOneSavedArticleContentOrganization`
- `RowOneSavedArticleContentOrganizationGroup`
- `RowOneSavedArticleContentOrganizationCard`

Use two safe saved articles:

```python
detail_path="details/the-row-signal-1234567890.html"
local_page_href="the-row-signal-1234567890.html"
body_source="extracted"
saved_paragraph_count=3
organized_section_count=2
```

```python
detail_path="details/alaia-signal-1234567890.html"
local_page_href missing
body_source="summary_fallback"
saved_paragraph_count=2
organized_section_count=1
```

Create content organization groups for `takeaways`, `entities`, `product_signals`, and an unsafe group card with traversal or JavaScript-like href.

- [ ] **Step 2: Add happy-path test**

Add `test_build_read_next_clusters_preserves_group_and_library_order()`:

```python
clusters = build_row_one_saved_article_read_next_clusters(
    library,
    organization,
    local_article_page_hrefs_by_detail_path={
        "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
    },
)

assert clusters is not None
assert clusters.cluster_count == 2
assert [cluster.title.en for cluster in clusters.clusters] == ["Read First", "People & Brands"]
assert [item.title.en for item in clusters.clusters[0].items] == [
    "The Row signal",
    "Alaia signal",
]
assert clusters.clusters[0].items[0].href == "the-row-signal-1234567890.html#local-article-digest"
assert clusters.clusters[0].items[1].href == "../details/alaia-signal-1234567890.html#local-article-content-section-1"
assert clusters.clusters[0].items[0].body_source_label.en == "Extracted article text"
assert clusters.clusters[0].items[1].body_source_label.en == "ROW ONE summary fallback"
```

Expected before implementation: module import failure.

- [ ] **Step 3: Add cap, empty, dedupe, and safety tests**

Add tests that assert:

```python
assert clusters.cluster_count == SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT
assert all(len(cluster.items) <= SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT for cluster in clusters.clusters)
assert build_row_one_saved_article_read_next_clusters(None, organization, local_article_page_hrefs_by_detail_path={}) is None
assert build_row_one_saved_article_read_next_clusters(library, None, local_article_page_hrefs_by_detail_path={}) is None
assert build_row_one_saved_article_read_next_clusters(empty_library, empty_organization, local_article_page_hrefs_by_detail_path={}) is None
assert "javascript:" not in {item.href for cluster in clusters.clusters for item in cluster.items}
assert not any(item.href.startswith(("http:", "https:", "//")) for cluster in clusters.clusters for item in cluster.items)
assert not any(not item.href.strip() or item.href != item.href.strip() for cluster in clusters.clusters for item in cluster.items)
assert all(".." not in item.href.removeprefix("../details/") for cluster in clusters.clusters for item in cluster.items)
```

Also assert duplicate content cards for the same detail path appear once per cluster, references are capped to four per item, and unsupported organization cards not present in the library are omitted.

- [ ] **Step 4: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_read_next_clusters.py -q
```

Expected: FAIL because `fashion_radar.row_one.saved_article_read_next_clusters` does not exist.

## Task 2: Implement Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_read_next_clusters.py`

- [ ] **Step 1: Add dataclasses and constants**

Implement:

```python
@dataclass(frozen=True)
class RowOneSavedArticleReadNextClusterItem:
    title: LocalizedText
    source_name: str
    section_label: LocalizedText
    body_source_label: LocalizedText
    lead: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    evidence_count: int
    href: str
    detail_path: str
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleReadNextCluster:
    key: str
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    evidence_count: int
    items: tuple[RowOneSavedArticleReadNextClusterItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReadNextClusters:
    cluster_count: int
    item_count: int
    source_count: int
    evidence_count: int
    clusters: tuple[RowOneSavedArticleReadNextCluster, ...]
```

- [ ] **Step 2: Add detail-path and href helpers**

Implement helpers that:

- derive allowed detail paths from safe saved article library entry digest/reader/evidence paths using `safe_row_one_detail_fragment_href(...)`;
- derive content card detail paths from safe `local-article-content-section-N` hrefs using `validated_row_one_detail_relative_path(...)`;
- prefer safe local article page hrefs from `local_article_page_hrefs_by_detail_path`;
- fall back to safe content-section hrefs with `../` prefix;
- fall back to safe digest hrefs with `../` prefix only when the content-section href is not safe.

The local page href helper must reject hrefs that start with `.`, start with `/`, contain `/`, contain whitespace, do not end with `.html`, or fail `safe_local_article_story_id(...)`.

- [ ] **Step 3: Add builder logic**

`build_row_one_saved_article_read_next_clusters(...)` should:

- return `None` for missing or empty library/organization;
- create a lookup of safe library entries by detail path while preserving library order;
- walk organization groups in existing order;
- walk each group card in existing order;
- include a card only when its detail path exists in the safe library lookup;
- dedupe duplicate cards by `(cluster_key, detail_path)`;
- preserve library order within each cluster by sorting included detail paths by their library-order index, not by counts or chip frequency;
- cap clusters to `SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT`;
- cap each cluster to `SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT`;
- cap references to `SAVED_ARTICLE_READ_NEXT_CLUSTER_REFERENCE_LIMIT`;
- calculate `source_count` from normalized source names;
- calculate `evidence_count` from valid paragraph indices;
- preserve localized leads from content organization cards;
- preserve body-source labels from library entries.

- [ ] **Step 4: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_read_next_clusters.py -q
```

Expected: PASS.

## Task 3: Wire Template And Render Tests

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render tests**

Add generated-site test near Stage 352:

```python
assert 'class="saved-article-read-next-clusters"' in library_html
assert library_html.index('class="saved-article-reading-queue"') < library_html.index(
    'class="saved-article-read-next-clusters"'
)
assert library_html.index('class="saved-article-read-next-clusters"') < library_html.index(
    'class="saved-article-signal-facets"'
)
assert 'class="saved-article-read-next-clusters"' not in homepage_html
assert 'class="saved-article-read-next-clusters"' not in detail_html
```

Also assert visible local organization content:

```python
assert "Saved Article Read Next Clusters" in section_html
assert "保存文章下一步阅读分组" in section_html
assert "Read First" in section_html
assert "People & Brands" in section_html
assert "Reference atlas source article" in section_html
assert "Vogue Business" in section_html
assert "Extracted article text" in section_html
assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
```

Add direct render tests with a `RowOneSavedArticleReadNextClusters` fixture:

- escaping titles, cluster labels, source names, body-source labels, leads, and references;
- unsafe link filtering for `javascript:`, `https://`, protocol-relative, traversal, whitespace, and wrong fragments;
- empty shell omission for `None`, empty cluster model, and all-filtered item model.

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "read_next_clusters"
```

Expected: FAIL until template support exists.

- [ ] **Step 3: Implement template rendering**

In `templates.py`:

- import `RowOneSavedArticleReadNextClusters`, `RowOneSavedArticleReadNextCluster`, `RowOneSavedArticleReadNextClusterItem`, and `build_row_one_saved_article_read_next_clusters`;
- add optional parameter `saved_article_read_next_clusters: RowOneSavedArticleReadNextClusters | None = None` to `render_saved_article_library_html(...)`;
- build clusters when not provided:

```python
read_next_clusters_model = (
    saved_article_read_next_clusters
    if saved_article_read_next_clusters is not None
    else build_row_one_saved_article_read_next_clusters(
        library,
        saved_article_content_organization,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
)
```

- render after `{reading_queue}` and before `{signal_facets}`;
- add `_render_saved_article_read_next_clusters(...)`;
- add `_render_saved_article_read_next_cluster(...)`;
- add `_render_saved_article_read_next_cluster_item(...)`;
- add `_saved_article_read_next_cluster_href(...)` render-time href validation accepting only:
  - `<safe-story-id>.html#local-article-digest`;
  - `../details/<safe-detail-file>.html#local-article-content-section-N`;
  - `../details/<safe-detail-file>.html#local-article-digest`;
- reject all other hrefs;
- omit the whole section when every item is filtered.

- [ ] **Step 4: Add CSS and CSS coverage test**

Add selectors:

```text
.saved-article-read-next-clusters
.saved-article-read-next-clusters-header
.saved-article-read-next-clusters-metrics
.saved-article-read-next-clusters-grid
.saved-article-read-next-cluster
.saved-article-read-next-cluster-header
.saved-article-read-next-cluster-items
.saved-article-read-next-cluster-item
.saved-article-read-next-cluster-meta
.saved-article-read-next-cluster-lead
.saved-article-read-next-cluster-refs
.saved-article-read-next-cluster-ref
.saved-article-read-next-cluster-link
```

Extend `test_row_one_css_includes_saved_article_library_styles(...)` to require these selectors.

- [ ] **Step 5: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "read_next_clusters or reading_queue or signal_facets"
```

Expected: PASS.

## Task 4: Workflow And Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add generated-site-only workflow guard**

Add `test_stage_353_saved_article_read_next_clusters_stays_generated_site_only(...)` delegating to the existing local article mutation workflow guard.

Extend generated contract denylist with:

```python
"saved_article_read_next_clusters"
"article_read_next_clusters"
"Saved Article Read Next Clusters"
"saved-article-read-next-clusters"
"article-read-next-clusters"
```

Extend forbidden artifact checks for root, `articles/`, and `data/` variants of:

- `saved-article-read-next-clusters.json/html`
- `article-read-next-clusters.json/html`

- [ ] **Step 2: Add docs boundary test and paragraphs**

Add a Stage 353 docs test before Stage 352, and insert this paragraph before
Stage 352 in both `README.md` and `docs/row-one.md`:

```text
Stage 353 adds generated-site only Saved Article Read Next Clusters inside `articles/index.html`; it reuses existing saved article library entries, existing saved article content organization groups, existing local article page hrefs, existing safe detail digest and content-section anchors, existing body-source labels, local leads, references, saved paragraph counts, organized section counts, and evidence counts to organize what to read next without changing app-facing contracts; it does not create `data/saved-article-read-next-clusters.json`, does not create `data/article-read-next-clusters.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 3: Run guard tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "stage_353 or read_next_clusters"
```

Expected: PASS.

## Task 5: Full Verification And Commit

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

Then request read-only code review. Try Claude Code first:

```bash
claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash -p "$(cat docs/reviews/claude-code-stage-353-code-review-prompt.md)"
```

If Claude Code returns 502 or times out, use local OpenCode:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-353-code-review-prompt.md)"
```

Fix any Critical or Important findings, rerun affected tests and gates, then commit:

```bash
git commit -m "Stage 353: add saved article read next clusters"
```
