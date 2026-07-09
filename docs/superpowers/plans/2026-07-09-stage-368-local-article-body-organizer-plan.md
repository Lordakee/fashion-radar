# Stage 368 Local Article Body Organizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. REQUIRED PROJECT GATE: submit this plan for Claude Code review before implementation; after Claude Code's plan review, run local opencode plan revision/review per `docs/REVIEW_PROTOCOL.md`.

**Goal:** Add a generated-site-only Local Article Body Organizer to `articles/<story-id>.html` so already-saved local article paragraphs are organized into filed sections, unfiled paragraph queue, and a compact read-first body route.

**Architecture:** Add a small pure builder module that derives a view model from the current `RowOneStory` and matching `RowOneLocalArticle`. Pass that model into the existing first-class local article page renderer and render a compact HTML-only section with same-page content-section and paragraph anchors. Keep all outputs generated-site-only: no app JSON, schemas, runtime/manifest contracts, source collection, fetching, scoring, ranking, LLM, connectors, scheduling, deployment, analytics, recommendation, personalization, or compliance behavior changes.

**Tech Stack:** Python 3, existing ROW ONE static site renderer, dataclasses, pytest, ruff.

---

## File Map

- Create `src/fashion_radar/row_one/saved_article_body_organizer.py`
  - Define organizer dataclasses.
  - Build filed section rows, unfiled paragraph rows, metrics, and read-first paragraph route.
  - Validate same-page local article paragraph and section anchors.
  - Keep paragraph-index validation helpers local with an inline note that they
    intentionally mirror Stage 367 filing inbox semantics, while returning
    ordered tuples for body-route rendering.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import/use `RowOneSavedArticleBodyOrganizer`.
  - Build and render the organizer inside the local article page HTML only.
  - Add scoped CSS selectors and mobile rules.
- Modify `src/fashion_radar/row_one/saved_article_filing_inbox.py`
  - Add a reciprocal comment near Stage 367 paragraph-index validation helpers
    pointing to the Stage 368 body organizer helper.
- Add `tests/test_row_one_saved_article_body_organizer.py`
  - Unit-test the builder and safety rules.
- Modify `tests/test_row_one_render.py`
  - Add renderer placement, contract, artifact, anchor, and CSS tests.
  - Optionally strengthen Stage 367 render boundary assertions identified by read-only review.
- Modify `tests/test_workflows.py`
  - Add Stage 368 generated-site-only contract and artifact denylist coverage.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document and verify Stage 368 boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Plan Review

**Files:**

- Create: `docs/reviews/claude-code-stage-368-plan-review.md`
- Create: `docs/reviews/opencode-stage-368-plan-review.md`

- [ ] Request Claude Code plan review before implementation.
- [ ] Confirm the reviewer checks:
  - local-article-page-only scope.
  - builder uses only current story/local article sidecar state.
  - filed paragraphs derive only from item-level `paragraph_indices`.
  - same-page safe local article section and paragraph anchors only.
  - no app JSON/schema/route/artifact changes.
  - no source collection, fetching, ranking, LLM, connector, scheduling, deployment, analytics, recommendation, personalization, or compliance-review behavior.
- [ ] Save the Claude Code plan review result to `docs/reviews/claude-code-stage-368-plan-review.md`.
- [ ] Run opencode plan revision/review with GLM 5.2 max and save it to `docs/reviews/opencode-stage-368-plan-review.md`.
- [ ] Fix critical and important planning issues before production code edits.
- [ ] Confirm the Stage 368 placement language says the organizer renders
  between the content segment deck and the saved local article body, after
  Saved Article Key Signals in the current template order.
- [ ] Confirm the plan chooses local paragraph-index helpers with a sibling
  Stage 367 reciprocal comment, not a shared utility extraction in this node.
- [ ] Confirm the lockfile verification command remains
  `UV_NO_CONFIG=1 uv --no-config lock --check --offline`; the opencode review
  reported a malformed `uv run lock` command, but the reviewed plan already
  contains the correct command.
- [ ] Do not edit production code until the plan review says implementation can proceed.

## Task 2: Builder RED Tests

**Files:**

- Create: `tests/test_row_one_saved_article_body_organizer.py`

- [ ] Add builder imports:

```python
from fashion_radar.row_one.saved_article_body_organizer import (
    build_row_one_saved_article_body_organizer,
)
```

- [ ] Add `test_build_saved_article_body_organizer_groups_filed_and_unfiled_paragraphs`.
  - Construct one safe story and matching local article with four nonblank paragraphs.
  - Add two content sections:
    - section 1 item references paragraph indices `[0, 2]`.
    - section 2 item references paragraph index `[1]`.
  - Leave paragraph index `3` unfiled.
  - Assert the organizer is not `None`.
  - Assert saved paragraph count is `4`.
  - Assert filed paragraph count is `3`.
  - Assert unfiled paragraph count is `1`.
  - Assert organized section count is `2`.
  - Assert filed rows preserve section order.
  - Assert paragraph hrefs are `#local-article-paragraph-1`, `#local-article-paragraph-3`, and `#local-article-paragraph-2`.
  - Assert the unfiled row href is `#local-article-paragraph-4`.
- [ ] Add `test_build_saved_article_body_organizer_filters_invalid_indices_and_blank_paragraphs`.
  - Use paragraph indices `[True, "0", -1, 0, 0, 1, 99]`.
  - Include a blank paragraph at index `1`.
  - Assert only paragraph `0` is filed.
  - Assert blank paragraph `1` is neither filed nor unfiled.
  - Assert no paragraph `0`, negative, duplicate, string, bool, or overflow href appears.
- [ ] Add `test_build_saved_article_body_organizer_handles_misaligned_zh`.
  - Provide `paragraphs_zh` with a mismatched length.
  - Assert excerpts still render using English/source paragraph text.
- [ ] Add `test_build_saved_article_body_organizer_caps_rows_deterministically`.
  - Create more than 5 eligible section rows.
  - Create more than 3 item labels in a section row.
  - Create more than 3 paragraph links per section row.
  - Create more than 4 unfiled paragraph rows.
  - Create more than 5 read-first route links.
  - Assert section rows, item labels, paragraph links, unfiled rows, and read-first links are capped while preserving source order.
- [ ] Add `test_build_saved_article_body_organizer_returns_none_without_meaningful_body`.
  - Assert mismatched story id returns `None`.
  - Assert unsafe story id returns `None`.
  - Assert all-blank paragraphs return `None`.

## Task 3: Render RED Tests

**Files:**

- Modify: `tests/test_row_one_render.py`

- [ ] Add `test_render_row_one_site_writes_local_article_body_organizer_only_on_local_article_page`.
  - Render a site with a local article that has filed and unfiled paragraphs.
  - Assert `articles/<story-id>.html` includes `class="local-article-body-organizer"`.
  - Assert English and Chinese headings:
    - `Local Article Body Organizer`
    - `本地正文整理器`
  - Assert metrics:
    - `4 saved paragraphs`
    - `3 filed paragraphs`
    - `1 unfiled paragraph`
    - `2 organized sections`
  - Assert filed section title, source name, item label, escaped excerpt, and safe paragraph href appear.
  - Assert unfiled paragraph queue appears with `#local-article-paragraph-4`.
  - Assert read-first route links point to existing paragraph anchors.
  - Assert the body organizer route uses
    `class="local-article-body-organizer-route"` and does not reuse
    `local-article-digest-card` as its route container.
  - Assert `index.html`, `articles/index.html`, and `details/<story-id>.html` do not include the organizer class, title, localized title, or jump links.
- [ ] Add `test_render_row_one_site_local_article_body_organizer_does_not_leak_contracts_or_artifacts`.
  - Serialize generated `data/edition.json`, `data/manifest.json`, and `data/runtime.json`.
  - Assert generated contract payload excludes:
    - `local_article_body_organizer`
    - `article_body_organizer`
    - `body_organizer`
    - `RowOneSavedArticleBodyOrganizer`
    - `BodyOrganizer`
    - `Local Article Body Organizer`
    - `Article Body Organizer`
    - `local-article-body-organizer`
    - `article-body-organizer`
    - `body-organizer`
  - Assert no matching `.json` or `.html` sidecar exists under root, `articles/`, or `data/`.
- [ ] Add `test_row_one_css_includes_local_article_body_organizer_styles`.
  - Assert CSS contains:
    - `.local-article-body-organizer`
    - `.local-article-body-organizer-header`
    - `.local-article-body-organizer-metrics`
    - `.local-article-body-organizer-route`
    - `.local-article-body-organizer-sections`
    - `.local-article-body-organizer-row`
    - `.local-article-body-organizer-unfiled`
  - Assert mobile single-column/list layout is covered in `@media (max-width: 760px)`.
- [ ] Strengthen existing Stage 367 render boundary assertions while in the same area:
  - Assert `id="saved-article-filing-inbox"`, `Saved Article Filing Inbox`, `保存文章归档收件箱`, and `#saved-article-filing-inbox` are absent from homepage, local article page, and detail page.
  - Expand Stage 367 local render artifact checks to mirror root/`articles`/`data` matrix for `saved-article-filing-inbox`, `article-filing-inbox`, and `filing-inbox`.
  - Assert `id="local-article-paragraph-3"` exists in the local article page when the filing inbox links to paragraph 3.

## Task 4: Builder Implementation

**Files:**

- Create: `src/fashion_radar/row_one/saved_article_body_organizer.py`

- [ ] Define constants:

```python
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS = 5
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ITEM_LABELS = 3
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_PARAGRAPHS_PER_ROW = 3
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_UNFILED_PARAGRAPHS = 4
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ROUTE_LINKS = 5
LOCAL_ARTICLE_BODY_ORGANIZER_EXCERPT_CHARS = 150
LOCAL_ARTICLE_BODY_ORGANIZER_SUPPORT_CHARS = 120
```

- [ ] Define dataclasses:

```python
@dataclass(frozen=True)
class RowOneLocalArticleBodyOrganizerParagraph:
    index: int
    label: LocalizedText
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneLocalArticleBodyOrganizerSectionRow:
    title: LocalizedText
    section_position: int
    section_href: str
    item_labels: tuple[LocalizedText, ...]
    support: LocalizedText | None
    paragraphs: tuple[RowOneLocalArticleBodyOrganizerParagraph, ...]


@dataclass(frozen=True)
class RowOneSavedArticleBodyOrganizer:
    title: LocalizedText
    source_name: str
    saved_paragraph_count: int
    filed_paragraph_count: int
    unfiled_paragraph_count: int
    organized_section_count: int
    read_first_route: tuple[RowOneLocalArticleBodyOrganizerParagraph, ...]
    section_rows: tuple[RowOneLocalArticleBodyOrganizerSectionRow, ...]
    unfiled_paragraphs: tuple[RowOneLocalArticleBodyOrganizerParagraph, ...]
```

- [ ] Implement `build_row_one_saved_article_body_organizer(...)`.
  - Signature:

```python
def build_row_one_saved_article_body_organizer(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleBodyOrganizer | None:
```

  - Require `story.id == local_article.story_id`.
  - Require `safe_local_article_story_id(story.id)`.
  - Build rendered paragraph index set from nonblank saved paragraphs.
  - Build filed index set from content-section item-level paragraph indices only.
  - Build section rows from `enumerate(local_article.content_sections, start=1)`;
    the `section_position` value must match existing rendered
    `id="local-article-content-section-N"` anchors.
  - Build section rows from sections that have valid paragraph references, labels, references, or support text.
  - Build unfiled nonblank paragraph entries.
  - Build read-first route from filed and unfiled rendered paragraph indices in original paragraph order.
  - Use aligned zh paragraph text only when `len(paragraphs_zh) == len(paragraphs)`; otherwise reuse English/source excerpts.
  - Return `None` if no meaningful rows remain.
- [ ] Implement private helpers:
  - `_rendered_paragraph_indices(article: RowOneLocalArticle) -> tuple[int, ...]`
  - `_strict_valid_paragraph_indices(indices: Sequence[object], rendered_indices: set[int]) -> tuple[int, ...]`
  - `_paragraph_view_model(article: RowOneLocalArticle, index: int) -> RowOneLocalArticleBodyOrganizerParagraph`
  - `_paragraph_excerpt(text: str) -> str`
  - `_nonblank_localized_text(value: LocalizedText | None) -> LocalizedText | None`
  - `_support_text(section: RowOneLocalArticleContentSection) -> LocalizedText | None`
  - `_section_href(position: int) -> str`
- [ ] Add an inline comment near `_strict_valid_paragraph_indices(...)` noting
  that its validation semantics intentionally mirror
  `saved_article_filing_inbox._strict_valid_paragraph_indices(...)`; Stage 368
  keeps a local ordered tuple helper to avoid refactoring Stage 367 in this
  article-page-only node.
- [ ] Add a reciprocal comment near
  `saved_article_filing_inbox._strict_valid_paragraph_indices(...)` noting that
  Stage 368 body organizer intentionally mirrors the same validation semantics.

## Task 5: Render Implementation

**Files:**

- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Import `build_row_one_saved_article_body_organizer` and `RowOneSavedArticleBodyOrganizer`.
- [ ] Build `local_article_body_organizer` in the first-class local article page rendering path after the content segment deck inputs are available.
- [ ] Render the organizer with a new helper:

```python
def _render_local_article_body_organizer(
    organizer: RowOneSavedArticleBodyOrganizer | None,
) -> str:
```

- [ ] Return `""` when the model is `None`, has no section rows, and has no unfiled rows.
- [ ] Render same-page safe section links and paragraph links only.
- [ ] Revalidate href fragments before emitting:
  - `#local-article-paragraph-N` where `N >= 1`.
  - `#local-article-content-section-N` where `N >= 1`.
  - no absolute URLs, protocol-relative URLs, traversal, whitespace, or JavaScript.
- [ ] Escape all titles, source names, labels, support text, excerpts, and hrefs.
- [ ] Insert the rendered organizer between `content_segment_deck` and
  `local_article_section` in `render_local_article_page_html(...)`; in the
  current template this places it after Saved Article Key Signals and before
  the saved local article body.
- [ ] Keep the organizer read-first route visually and semantically distinct
  from the existing local article digest "Read First" card by using
  `.local-article-body-organizer-route` only for the organizer route.
- [ ] Add scoped CSS and mobile rules.

## Task 6: Docs and Workflow Guards

**Files:**

- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] Add docs paragraph before Stage 367 in README and `docs/row-one.md`:

```text
Stage 368 adds generated-site only Local Article Body Organizer inside `articles/<story-id>.html`; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article content sections, existing item-level content-section paragraph indices, existing content-section anchors, and existing paragraph anchors to summarize each saved article body into filed section rows, an unfiled paragraph queue, and a read-first paragraph route without changing app-facing contracts; it does not create `data/local-article-body-organizer.json`, does not create `data/article-body-organizer.json`, does not create `data/body-organizer.json`, does not create `local-article-body-organizer.html`, does not create `article-body-organizer.html`, does not create `body-organizer.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] Add `test_row_one_docs_describe_stage_368_local_article_body_organizer_boundary`.
- [ ] Extend workflow generated contract payload denylist with:
  - `local_article_body_organizer`
  - `article_body_organizer`
  - `body_organizer`
  - `RowOneSavedArticleBodyOrganizer`
  - `BodyOrganizer`
  - `Local Article Body Organizer`
  - `Article Body Organizer`
  - `local-article-body-organizer`
  - `article-body-organizer`
  - `body-organizer`
- [ ] Extend artifact denylist for `.json` and `.html` under root, `articles/`, and `data/`:
  - `local-article-body-organizer`
  - `article-body-organizer`
  - `body-organizer`
  - `local_article_body_organizer`
  - `article_body_organizer`
  - `body_organizer`
- [ ] Add `test_stage_368_local_article_body_organizer_stays_generated_site_only`.
  - Monkeypatch
    `fashion_radar.row_one.templates._render_local_article_body_organizer`
    with `lambda _organizer: ""`.
  - Call `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)`.

## Task 7: Verification, Review, Commit, Push

- [ ] Run focused RED before production implementation:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_body_organizer.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -k "body_organizer or stage_368 or filing_inbox or stage_367 or local_article_without_mutating_sqlite"
```

Expected before implementation: new builder/render/CSS/workflow assertions fail because the feature does not exist yet.

- [ ] After implementation, run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_body_organizer.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -k "body_organizer or stage_368 or filing_inbox or stage_367 or local_article_without_mutating_sqlite"
```

Expected after implementation: all selected tests pass.

- [ ] Run full verification:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] Request Claude Code code review and save it to `docs/reviews/claude-code-stage-368-code-review.md`.
- [ ] Fix critical and important review findings.
- [ ] If Claude Code is unavailable, run opencode fallback review with GLM 5.2 max and save it to `docs/reviews/opencode-stage-368-code-review.md`.
- [ ] Commit with message:

```bash
git add src/fashion_radar/row_one/saved_article_body_organizer.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_body_organizer.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/specs/2026-07-09-stage-368-local-article-body-organizer-design.md docs/superpowers/plans/2026-07-09-stage-368-local-article-body-organizer-plan.md docs/reviews/claude-code-stage-368-plan-review.md docs/reviews/opencode-stage-368-plan-review.md docs/reviews/claude-code-stage-368-code-review.md docs/reviews/opencode-stage-368-code-review.md
git commit -m "Stage 368: add local article body organizer"
```

- [ ] Push to GitHub.
- [ ] Write Handoff Summary with:
  - repo status
  - verified commands
  - uncommitted files
  - next step
