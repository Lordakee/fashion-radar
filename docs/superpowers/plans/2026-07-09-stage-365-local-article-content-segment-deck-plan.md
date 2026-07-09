# Stage 365 Local Article Content Segment Deck Implementation Plan

> **For agentic workers:** REQUIRED PROCESS: submit this plan for Claude Code review before implementation. After implementation, request code review, run full gates, commit, push, and write a Handoff Summary.

**Goal:** Add a generated-site-only Local Article Content Segment Deck to first-class ROW ONE local article pages so already-saved content sections render as compact publish-page content cards before the full saved body.

**Architecture:** Keep the feature render-only in `templates.py`. Derive a private deck view model directly from `RowOneLocalArticle.content_sections`, existing saved paragraph anchors, existing content-section anchors, and existing reference/item data already passed to `render_local_article_page_html(...)`. Do not add builders, schemas, JSON payloads, sidecars, routes, fetching, LLM, scheduling, analytics, recommendation, or compliance-review behavior.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing dataclass/Pydantic models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add Stage 365 constants near other local article constants.
  - Add private dataclasses for segment deck sections/items if useful.
  - Add `_render_local_article_content_segment_deck(...)` and helper functions.
  - Insert the rendered deck in `render_local_article_page_html(...)` after saved article key signals and before `id="local-article"`.
  - Add scoped CSS selectors.
- Modify `tests/test_row_one_render.py`
  - Add direct local article page render tests.
  - Add generated-site article-page-only tests.
  - Add CSS selector tests.
- Modify `tests/test_workflows.py`
  - Add generated contract denylist entries and artifact stem guards.
  - Add Stage 365 generated-site-only wrapper.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document and verify the Stage 365 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Direct Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add `_local_article_content_segment_deck_html(index_html: str) -> str` helper near local article page section helper patterns.
- [ ] Add `test_render_local_article_page_includes_content_segment_deck`.
  - Use `_signal_briefing_local_article()` with hostile section/item/reference text.
  - Assert bilingual heading, section titles, item labels, item excerpts, source/body-source metrics, reference chips, content-section links, paragraph links, and escaped hostile text.
  - Assert the deck appears after `saved-article-key-signals` when key signals exist and before `id="local-article"`.
  - Assert the full saved paragraph body is not duplicated in the deck.
- [ ] Add `test_render_local_article_page_content_segment_deck_filters_invalid_links`.
  - Include invalid paragraph indices, duplicate indices, empty paragraphs, malformed content-section anchor candidates, blank labels, blank references, and raw hostile strings.
  - Assert only safe same-page anchors remain.
- [ ] Add `test_render_local_article_page_omits_content_segment_deck_without_eligible_sections`.
  - Cover no rendered paragraphs, no content sections, blank sections/items, and sections with no useful body/reference/paragraph/link content.
- [ ] Add placement tests:
  - with companion + binder + key signals: companion < binder < key signals < segment deck < local article body.
  - without key signals: existing pre-body blocks still precede segment deck and segment deck precedes local article body.

## Task 2: Template Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Add constants:
  - `LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_SECTIONS = 4`
  - `LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_ITEMS_PER_SECTION = 3`
  - `LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_REFS_PER_SECTION = 5`
  - `LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_MAX_PARAGRAPH_LINKS = 3`
  - `LOCAL_ARTICLE_CONTENT_SEGMENT_DECK_EXCERPT_CHARS = 180`
- [ ] Implement `_render_local_article_content_segment_deck(article: RowOneLocalArticle) -> str`.
  - Early return when no rendered saved paragraphs exist.
  - Derive cards from current article content sections in order.
  - Cap sections/items/references/paragraph links.
  - Normalize and escape all display text.
  - Link only to `#local-article-content-section-N` and `#local-article-paragraph-N`.
  - Reuse `_strict_valid_local_article_paragraph_indices(...)`, `_local_article_rendered_paragraph_indices(...)`, `_local_article_content_section_anchor(...)`, and `_local_article_paragraph_anchor(...)`.
- [ ] Insert the deck into `render_local_article_page_html(...)` after `saved_article_key_signals` and before the local article body block.
- [ ] Add scoped CSS for:
  - `.local-article-content-segment-deck`
  - `-header`
  - `-metrics`
  - `-grid`
  - `-card`
  - `-items`
  - `-item`
  - `-refs`
  - `-ref`
  - `-paragraphs`
  - `-action`
  - mobile grid rules.

## Task 3: Generated Site Boundary Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add `test_render_row_one_site_writes_content_segment_deck_only_on_local_article_pages`.
  - Render a site with publishable local articles and content sections.
  - Assert `articles/<story-id>.html` includes the deck.
  - Assert `index.html`, `articles/index.html`, and `details/<story-id>.html` do not include the deck.
  - Assert generated contract payload does not include `local_article_content_segment_deck`, `article_content_segment_deck`, `content_segment_deck`, `local-article-content-segment-deck`, `article-content-segment-deck`, or `Content Segment Deck`.
  - Assert no matching JSON/HTML sidecar artifact exists under root, `articles/`, or `data/`.
- [ ] Add `test_row_one_css_includes_local_article_content_segment_deck_styles`.

## Task 4: Workflow and Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] Extend generated contract payload denylist with Stage 365 snake/kebab/title/Chinese names.
- [ ] Extend artifact denylist with:
  - `local-article-content-segment-deck`
  - `article-content-segment-deck`
  - `content-segment-deck`
  - `local_article_content_segment_deck`
  - `article_content_segment_deck`
  - `content_segment_deck`
- [ ] Add `test_stage_365_local_article_content_segment_deck_stays_generated_site_only`.
  - Monkeypatch `_render_local_article_content_segment_deck` to `""`.
  - Call `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)`.
- [ ] Add Stage 365 docs before Stage 364 in README and `docs/row-one.md`.
- [ ] Add `test_row_one_docs_describe_stage_365_local_article_content_segment_deck_boundary`.

## Task 5: Review and Verification

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "content_segment_deck" tests/test_row_one_docs.py -k "stage_365" tests/test_workflows.py -k "stage_365 or local_article_without_mutating_sqlite"
```

- [ ] Run focused formatting/lint:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py README.md docs/row-one.md
```

- [ ] Request Claude Code review and save to:
  - `docs/reviews/2026-07-09-stage-365-local-article-content-segment-deck-code-claude.md`
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
git commit -m "Stage 365: add local article content segment deck"
```

- [ ] Push `main` and write Handoff Summary with repo status, verified commands, uncommitted files, and next step.
