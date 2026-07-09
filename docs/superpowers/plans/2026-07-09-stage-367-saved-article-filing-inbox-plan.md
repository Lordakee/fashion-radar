# Stage 367 Saved Article Filing Inbox Implementation Plan

> **For agentic workers:** REQUIRED PROCESS: submit this plan for Claude Code review before implementation. After implementation, request code review, run full gates, commit, push, and write a Handoff Summary.

**Goal:** Add a generated-site-only Saved Article Filing Inbox to `articles/index.html` so unfiled saved paragraphs from downloaded/local articles are visible from the saved article library.

**Architecture:** Add a small builder module that derives unfiled saved paragraph rows from current `RowOneLocalArticle` objects and the existing local article page href map. Pass the view model into the saved article library renderer and render it as HTML only on `articles/index.html`. Do not change app JSON, schemas, runtime/manifest contracts, source collection, fetching, scoring, ranking, LLM, connectors, scheduling, deployment, analytics, recommendation, personalization, or compliance behavior.

**Tech Stack:** Python 3, existing ROW ONE static site renderer, dataclasses, pytest, ruff.

---

## File Map

- Create `src/fashion_radar/row_one/saved_article_filing_inbox.py`
  - Define inbox dataclasses.
  - Build current-edition unfiled paragraph rows.
  - Validate safe local article hrefs and paragraph indices.
- Modify `src/fashion_radar/row_one/render.py`
  - Build the inbox during site rendering.
  - Pass it through the saved article library page writer.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept `saved_article_filing_inbox` in `render_saved_article_library_html(...)`.
  - Render `_render_saved_article_filing_inbox(...)` only in the library page.
  - Add scoped CSS selectors and mobile rules.
- Add `tests/test_row_one_saved_article_filing_inbox.py`
  - Unit-test the builder.
- Modify `tests/test_row_one_render.py`
  - Add render, generated-site-only, and CSS tests.
- Modify `tests/test_workflows.py`
  - Add contract denylist, artifact denylist, and wrapper guard.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document and verify Stage 367 boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Plan Review

**Files:**

- Create: `docs/reviews/2026-07-09-stage-367-saved-article-filing-inbox-plan-claude.md`

- [ ] Request Claude Code plan review before implementation.
- [ ] Confirm the reviewer checks:
  - article-library-only scope.
  - builder uses only current edition/local article sidecars and article-page hrefs.
  - unfiled paragraphs derive only from item-level `paragraph_indices`.
  - safe local article paragraph hrefs only.
  - no app JSON/schema/route/artifact changes.
  - no compliance-review behavior.
- [ ] Save the plan review result to the file above.
- [ ] Do not edit production code until the plan review says implementation can proceed.

## Task 2: Builder RED Tests

**Files:**

- Create: `tests/test_row_one_saved_article_filing_inbox.py`

- [ ] Add builder imports:

```python
from fashion_radar.row_one.saved_article_filing_inbox import (
    build_row_one_saved_article_filing_inbox,
)
```

- [ ] Add `test_build_saved_article_filing_inbox_collects_unfiled_paragraphs`.
  - Use `_edition()` and `_signal_briefing_local_article()` patterns from existing tests.
  - Construct an article with three nonblank paragraphs.
  - Content-section item references paragraph 0 only.
  - Pass `local_article_page_hrefs_by_detail_path={story.detail_path: "the-row-signal-1234567890.html"}`.
  - Assert the inbox is not `None`.
  - Assert it has one article row.
  - Assert unfiled paragraphs are paragraph 2 and paragraph 3 in reader-facing one-based labels.
  - Assert paragraph hrefs are `the-row-signal-1234567890.html#local-article-paragraph-2` and `the-row-signal-1234567890.html#local-article-paragraph-3`.
- [ ] Add `test_build_saved_article_filing_inbox_filters_invalid_indices_and_hrefs`.
  - Use paragraph indices `[True, "0", -1, 0, 0, 1, 99]`.
  - Include a blank paragraph at index 1.
  - Assert valid filed set only includes paragraph 0.
  - Assert blank paragraphs are not emitted as unfiled.
  - Assert unsafe href mappings such as `javascript:alert(1)`, `../secret.html`, `nested/story.html`, and `https://example.com/story.html` are rejected.
- [ ] Add `test_build_saved_article_filing_inbox_caps_and_preserves_order`.
  - Create more than 8 eligible articles.
  - Assert only 8 rows render.
  - Create more than 3 unfiled paragraphs in the first article.
  - Assert only 3 paragraph links are kept.
  - Assert article/source order follows edition story order.
- [ ] Add `test_build_saved_article_filing_inbox_returns_none_without_unfiled_paragraphs`.
  - Fully file every nonblank paragraph.
  - Assert builder returns `None`.
  - Assert empty local article maps return `None`.

## Task 3: Render RED Tests

**Files:**

- Modify: `tests/test_row_one_render.py`

- [ ] Add `test_render_saved_article_library_html_includes_filing_inbox`.
  - Build a `RowOneSavedArticleFilingInbox` fixture directly or via the builder.
  - Pass it to `render_saved_article_library_html(...)`.
  - Assert `class="saved-article-filing-inbox"` appears.
  - Assert English and Chinese headings:
    - `Saved Article Filing Inbox`
    - `保存文章归档收件箱`
  - Assert article title, source, unfiled count, escaped excerpt, and safe paragraph href appear.
  - Assert unsafe text is escaped.
  - Assert no unsafe href appears.
- [ ] Add `test_render_saved_article_library_html_omits_empty_filing_inbox_shell`.
  - Pass `saved_article_filing_inbox=None`.
  - Assert section class and title do not appear.
- [ ] Add `test_render_row_one_site_writes_saved_article_filing_inbox_only_in_library`.
  - Render a site with at least one article containing unfiled paragraphs.
  - Assert `articles/index.html` includes the inbox.
  - Assert `index.html`, `articles/<story-id>.html`, and `details/<story-id>.html` do not include it.
  - Assert generated contract payload excludes:
    - `saved_article_filing_inbox`
    - `article_filing_inbox`
    - `filing_inbox`
    - `saved-article-filing-inbox`
    - `article-filing-inbox`
    - `Saved Article Filing Inbox`
  - Assert no matching `.json` or `.html` sidecar exists under root, `articles/`, or `data/`.
- [ ] Add `test_row_one_css_includes_saved_article_filing_inbox_styles`.
  - Assert CSS contains:
    - `.saved-article-filing-inbox`
    - `.saved-article-filing-inbox-header`
    - `.saved-article-filing-inbox-metrics`
    - `.saved-article-filing-inbox-list`
    - `.saved-article-filing-inbox-item`
    - `.saved-article-filing-inbox-paragraphs`
    - `.saved-article-filing-inbox-paragraph`
  - Assert mobile single-column/list layout is covered in `@media (max-width: 760px)`.

## Task 4: Builder Implementation

**Files:**

- Create: `src/fashion_radar/row_one/saved_article_filing_inbox.py`

- [ ] Define constants:

```python
SAVED_ARTICLE_FILING_INBOX_MAX_ARTICLES = 8
SAVED_ARTICLE_FILING_INBOX_MAX_PARAGRAPHS_PER_ARTICLE = 3
SAVED_ARTICLE_FILING_INBOX_EXCERPT_CHARS = 140
```

- [ ] Define dataclasses:

```python
@dataclass(frozen=True)
class RowOneSavedArticleFilingInboxParagraph:
    index: int
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleFilingInboxItem:
    title: LocalizedText
    source_name: str
    body_source_label: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    unfiled_paragraph_count: int
    paragraphs: tuple[RowOneSavedArticleFilingInboxParagraph, ...]


@dataclass(frozen=True)
class RowOneSavedArticleFilingInbox:
    items: tuple[RowOneSavedArticleFilingInboxItem, ...]
```

- [ ] Implement `build_row_one_saved_article_filing_inbox(...)`.
  - Signature:

```python
def build_row_one_saved_article_filing_inbox(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleFilingInbox | None:
```

  - Iterate `edition.stories` in order.
  - Look up matching local article by story id.
  - Require a safe local article page href for `story.detail_path`.
  - Build filed index set from content-section item-level paragraph indices only.
  - Build unfiled nonblank paragraph entries.
  - Use aligned zh paragraph text when available; otherwise reuse English excerpt.
  - Return `None` if no items remain.
- [ ] Implement private helpers:
  - `_safe_filing_inbox_article_href(href: str) -> str | None`
  - `_rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]`
  - `_filed_paragraph_indices(article: RowOneLocalArticle, rendered_indices: set[int]) -> set[int]`
  - `_strict_valid_paragraph_indices(indices: Sequence[object], rendered_indices: set[int]) -> tuple[int, ...]`
  - `_paragraph_excerpt(text: str) -> str`
  - `_body_source_label(article: RowOneLocalArticle) -> LocalizedText`
- [ ] Safety rules for `_safe_filing_inbox_article_href`:
  - reject empty or whitespace-surrounded hrefs.
  - reject whitespace inside hrefs.
  - reject `http:`, `https:`, `//`, `javascript:`.
  - reject hrefs starting with `.`, `/`, or containing `/`.
  - require `.html`.
  - require safe story id via `safe_local_article_story_id(...)`.

## Task 5: Render Implementation

**Files:**

- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Import `build_row_one_saved_article_filing_inbox` and `RowOneSavedArticleFilingInbox`.
- [ ] Build `saved_article_filing_inbox` in `render_row_one_site(...)` after local article page hrefs are available.
- [ ] Pass the inbox into `_write_saved_article_library_page(...)`.
- [ ] Add parameter to `_write_saved_article_library_page(...)`.
- [ ] Add parameter to `render_saved_article_library_html(...)`:

```python
saved_article_filing_inbox: RowOneSavedArticleFilingInbox | None = None
```

- [ ] Render `filing_inbox = _render_saved_article_filing_inbox(saved_article_filing_inbox)` near the organization jump index/reading queue.
- [ ] Implement `_render_saved_article_filing_inbox(...)` in `templates.py`.
  - Return `""` when model is `None` or has no items.
  - Render metrics from item count and total unfiled paragraphs.
  - Render each row with safe local paragraph hrefs already built by the builder.
  - Revalidate href shape in a renderer helper before emitting.
  - Escape all labels, source names, and excerpts.
- [ ] Add scoped CSS and mobile rules.

## Task 6: Docs and Workflow Guards

**Files:**

- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] Add docs paragraph before Stage 366 in README and `docs/row-one.md`:

```text
Stage 367 adds generated-site only Saved Article Filing Inbox inside `articles/index.html`; it reuses current-edition saved local article sidecars, existing local article page routes, existing saved local paragraphs, existing item-level content-section paragraph indices, and existing paragraph anchors to aggregate unfiled saved paragraphs across the article library without changing app-facing contracts; it does not create `data/saved-article-filing-inbox.json`, does not create `data/article-filing-inbox.json`, does not create `data/filing-inbox.json`, does not create new route families, does not alter `index.html`, `articles/<story-id>.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] Add `test_row_one_docs_describe_stage_367_saved_article_filing_inbox_boundary`.
- [ ] Extend workflow `generated_contract_payload` denylist with:
  - `saved_article_filing_inbox`
  - `article_filing_inbox`
  - `filing_inbox`
  - `Saved Article Filing Inbox`
  - `Article Filing Inbox`
  - `saved-article-filing-inbox`
  - `article-filing-inbox`
  - `filing-inbox`
- [ ] Extend artifact denylist for `.json` and `.html` under root, `articles/`, and `data/`:
  - `saved-article-filing-inbox`
  - `article-filing-inbox`
  - `filing-inbox`
  - `saved_article_filing_inbox`
  - `article_filing_inbox`
  - `filing_inbox`
- [ ] Add `test_stage_367_saved_article_filing_inbox_stays_generated_site_only`.
  - Monkeypatch `_render_saved_article_filing_inbox` with `lambda _inbox: ""`.
  - Call `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)`.

## Task 7: Verification, Review, Commit, Push

- [ ] Run focused RED before production implementation:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_filing_inbox.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -k "filing_inbox or stage_367 or local_article_without_mutating_sqlite"
```

Expected before implementation: new builder/render/CSS/workflow assertions fail because the feature does not exist yet.

- [ ] After implementation, run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_filing_inbox.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -k "filing_inbox or stage_367 or local_article_without_mutating_sqlite"
```

- [ ] Run focused lint and format:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_filing_inbox.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_filing_inbox.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_filing_inbox.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_filing_inbox.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

- [ ] Request Claude Code review and save to:

```text
docs/reviews/2026-07-09-stage-367-saved-article-filing-inbox-code-claude.md
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

- [ ] Commit:

```bash
git commit -m "Stage 367: add saved article filing inbox"
```

- [ ] Push `main`.
- [ ] Write Handoff Summary with repo status, verified commands, uncommitted files, and next step.
