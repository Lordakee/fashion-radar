# Stage 352 Saved Article Reading Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Saved Article Reading Queue that gives readers a compact, ordered list of safe local article links inside `articles/index.html`.

**Architecture:** Build a small in-memory queue from existing `RowOneSavedArticleLibrary` entries, render it only in the saved article library page, and keep all links to existing safe local article page hrefs or same-site detail digest anchors. Do not add artifacts, schemas, route families, app contracts, ranking, extraction, LLM calls, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Create `src/fashion_radar/row_one/saved_article_reading_queue.py`
  - Add `SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT = 5`.
  - Add frozen dataclasses:
    - `RowOneSavedArticleReadingQueue`
    - `RowOneSavedArticleReadingQueueItem`
  - Add `build_row_one_saved_article_reading_queue(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import the builder and dataclasses.
  - Build the queue in `render_saved_article_library_html(...)` from the existing saved article library and local article page href allowlist.
  - Add `_render_saved_article_reading_queue(...)`.
  - Render after `organization_jump_index` and before `signal_facets`.
  - Add CSS selectors for the section, header, list, item, metadata, and action link.
- Add `tests/test_row_one_saved_article_reading_queue.py`.
- Modify `tests/test_row_one_render.py`.
- Modify `tests/test_workflows.py`.
- Modify `tests/test_row_one_docs.py`.
- Modify `README.md` and `docs/row-one.md`.
- Add `docs/reviews/claude-code-stage-352-plan-review-prompt.md`.
- Add `docs/reviews/opencode-stage-352-plan-review-prompt.md`.

## Task 1: Write Failing Builder Tests

**Files:**
- Create: `tests/test_row_one_saved_article_reading_queue.py`

- [ ] **Step 1: Add fixtures**

Create helpers using `RowOneSavedArticleLibrary`, `RowOneSavedArticleLibrarySourceGroup`, and `RowOneSavedArticleLibraryEntry`.

The helper entries should include:

- valid `digest_path`;
- optional `reader_path`;
- `body_source`;
- saved paragraph and organized section counts;
- one unsafe entry with traversal or JavaScript-like detail path.
- more than five safe entries for the cap test.
- one entry with no local page mapping and no safe detail digest fragment.

- [ ] **Step 2: Add happy-path test**

Add `test_build_saved_article_reading_queue_preserves_library_order()`:

```python
queue = build_row_one_saved_article_reading_queue(
    library,
    local_article_page_hrefs_by_detail_path={
        "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
    },
)

assert queue is not None
assert queue.item_count == 2
assert [item.title.en for item in queue.items] == ["The Row signal", "Alaia signal"]
assert queue.items[0].href == "the-row-signal-1234567890.html#local-article-digest"
assert queue.items[1].href == "../details/alaia-signal-1234567890.html#local-article-digest"
```

Expected before implementation: module import failure.

- [ ] **Step 3: Add cap, empty, and safety tests**

Add tests that assert:

```python
assert len(queue.items) == SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT
assert build_row_one_saved_article_reading_queue(None, local_article_page_hrefs_by_detail_path={}) is None
assert build_row_one_saved_article_reading_queue(empty_library, local_article_page_hrefs_by_detail_path={}) is None
assert "javascript:" not in {item.href for item in queue.items}
assert all(".." not in item.href.removeprefix("../details/") for item in queue.items)
assert not any(item.href.startswith(("http:", "https:", "//")) for item in queue.items)
assert not any(not item.href.strip() or item.href != item.href.strip() for item in queue.items)
```

Also assert queue items retain the source names and body-source labels, and
that entries with no safe local page href or safe detail digest fallback are
omitted.

- [ ] **Step 4: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_queue.py -q
```

Expected: FAIL because the module does not exist.

## Task 2: Implement Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_reading_queue.py`

- [ ] **Step 1: Add dataclasses and constants**

Implement:

```python
@dataclass(frozen=True)
class RowOneSavedArticleReadingQueueItem:
    title: LocalizedText
    source_name: str
    body_source_label: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    href: str
    detail_path: str


@dataclass(frozen=True)
class RowOneSavedArticleReadingQueue:
    item_count: int
    items: tuple[RowOneSavedArticleReadingQueueItem, ...]
```

- [ ] **Step 2: Add builder logic**

`build_row_one_saved_article_reading_queue(...)` should:

- return `None` for missing/empty library;
- walk `library.groups` and `group.entries` in existing order;
- prefer safe local article page hrefs from `local_article_page_hrefs_by_detail_path`;
- fall back to safe detail digest hrefs via `safe_row_one_detail_fragment_href`;
- convert detail digest links with the same page-relative behavior used by
  `_saved_article_library_page_href(...)`: a safe `details/<file>.html#local-article-digest`
  fallback becomes `../details/<file>.html#local-article-digest` for
  `articles/index.html`;
- cap at `SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT`;
- preserve counts and body-source labels;
- omit entries with no safe href.

- [ ] **Step 3: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_queue.py -q
```

Expected: PASS.

## Task 3: Wire Template And Render Tests

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render tests**

Add generated-site test asserting:

```python
assert 'class="saved-article-reading-queue"' in library_html
assert library_html.index('class="saved-article-organization-jump-index"') < library_html.index(
    'class="saved-article-reading-queue"'
)
assert library_html.index('class="saved-article-reading-queue"') < library_html.index(
    'class="saved-article-signal-facets"'
)
assert 'class="saved-article-reading-queue"' not in homepage_html
assert 'class="saved-article-reading-queue"' not in detail_html
```

Add escaping and unsafe-link tests with a direct `RowOneSavedArticleReadingQueue` fixture. Add empty-shell tests for `None`, empty queue objects, and a queue where every item is filtered after href validation.

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reading_queue"
```

Expected: FAIL until template support exists.

- [ ] **Step 3: Implement template rendering**

Add `_render_saved_article_reading_queue(...)` with:

- section id/class `saved-article-reading-queue`;
- escaped labels, titles, source names, body-source labels, and counts;
- href filtering that rejects external URLs, JavaScript, traversal, whitespace, and empty strings;
- href filtering that accepts only local article page hrefs and canonical
  `../details/<safe-detail-file>.html#local-article-digest` fallback links;
- href filtering that rejects external URLs, protocol-relative URLs,
  JavaScript, non-canonical traversal, whitespace, and empty strings;
- no rendering when all items are filtered.

Place the section after `organization_jump_index` and before `signal_facets`.

- [ ] **Step 4: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reading_queue or organization_jump_index"
```

Expected: PASS.

## Task 4: Workflow And Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add generated-site-only workflow guard**

Add `test_stage_352_saved_article_reading_queue_stays_generated_site_only(...)` delegating to the existing local article mutation workflow guard.

Extend generated contract denylist with:

```python
"saved_article_reading_queue"
"article_reading_queue"
"Saved Article Reading Queue"
"saved-article-reading-queue"
"article-reading-queue"
```

Extend forbidden artifact checks for root, `articles/`, and `data/` variants of:

- `saved-article-reading-queue.json/html`
- `article-reading-queue.json/html`

- [ ] **Step 2: Add docs boundary test and paragraphs**

Add a Stage 352 docs test mirroring Stage 351, and insert this paragraph before Stage 351 in both `README.md` and `docs/row-one.md`:

```text
Stage 352 adds generated-site only Saved Article Reading Queue inside `articles/index.html`; it reuses existing saved article library entries, existing local article page hrefs, existing safe detail digest anchors, existing body-source labels, saved paragraph counts, and organized section counts to provide a compact local reading sequence without changing app-facing contracts; it does not create `data/saved-article-reading-queue.json`, does not create `data/article-reading-queue.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 3: Run guard tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "stage_352 or reading_queue"
```

Expected: PASS after docs/guards are implemented.

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

Then request read-only code review, commit:

```bash
git commit -m "Stage 352: add saved article reading queue"
```
