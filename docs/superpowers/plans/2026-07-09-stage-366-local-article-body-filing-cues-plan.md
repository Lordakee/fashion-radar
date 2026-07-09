# Stage 366 Local Article Body Filing Cues Implementation Plan

> **For agentic workers:** REQUIRED PROCESS: submit this plan for Claude Code review before implementation. After implementation, request code review, run full gates, commit, push, and write a Handoff Summary.

**Goal:** Add generated-site-only Local Article Body Filing Cues inside the saved body of first-class ROW ONE local article pages so each rendered paragraph is visibly filed under existing content organization or marked as unfiled saved text.

**Architecture:** Keep the feature render-only in `templates.py`. Extend the existing local article paragraph rendering path by deriving per-paragraph filing context from `RowOneLocalArticle.content_sections`, existing item labels, existing section titles, and existing content-section anchors. Do not add builders, schemas, JSON payloads, sidecars, routes, fetching, LLM, scheduling, analytics, recommendation, personalization, or compliance-review behavior.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing dataclass/Pydantic models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add Stage 366 constants near other local article constants.
  - Add `_render_local_article_body_filing_cue(...)` and private helper functions.
  - Update `_render_local_article_paragraphs(...)` to include cues inside rendered saved body paragraphs.
  - Add scoped CSS selectors.
- Modify `tests/test_row_one_render.py`
  - Add direct local article page render tests.
  - Add generated-site article-page-only tests.
  - Add CSS selector tests.
- Modify `tests/test_workflows.py`
  - Add generated contract denylist entries and artifact stem guards.
  - Add Stage 366 generated-site-only wrapper.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document and verify the Stage 366 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Direct Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add `_local_article_body_html(html: str) -> str` helper if an existing body slice helper is not already available.
- [ ] Add `test_render_local_article_page_includes_body_filing_cues`.
  - Use `_signal_briefing_local_article()` with at least two nonblank saved paragraphs.
  - Make one paragraph cited by an existing item-level paragraph index with a usable item label, one paragraph cited by an item whose label is blank so it falls back to the parent section title, and one paragraph uncited.
  - Assert the body contains `Local Article Body Filing Cues`-specific class names only inside `#local-article-body`.
  - Assert cited paragraph cue says `Filed under` / `已归档到`.
  - Assert cited cue links only to `#local-article-content-section-1`.
  - Assert item-level cues use item labels when available and fall back to the parent section title when item labels are blank.
  - Assert uncited paragraph cue says `Unfiled saved paragraph` / `未归档保存段落`.
  - Assert paragraph text and existing `id="local-article-paragraph-N"` anchors remain unchanged.
  - Assert hostile section/item labels are escaped.
- [ ] Add `test_render_local_article_page_body_filing_cues_filter_invalid_links`.
  - Include bool, string, negative, duplicate, blank-paragraph, and overflow paragraph indices in content section items.
  - Assert only valid rendered paragraph cues become filed.
  - Assert invalid anchors such as `#local-article-content-section-0`, `#local-article-paragraph-0`, `javascript:`, `../`, and raw `<script>` do not appear.
- [ ] Add `test_render_local_article_page_omits_body_filing_cues_without_rendered_paragraphs`.
  - Cover blank-only paragraph lists.
- [ ] Add placement/relationship assertions:
  - `.local-article-content-segment-deck` remains before `id="local-article"`.
  - body filing cues appear after `id="local-article-body"` and inside paragraph markup, not as another pre-body section.

## Task 2: Template Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Add constant:
  - `LOCAL_ARTICLE_BODY_FILING_CUES_MAX_CONTEXTS = 3`
- [ ] Implement `_local_article_body_filing_contexts(article, rendered_indices=...)`.
  - Return a `dict[int, list[_LocalArticleParagraphContextCue]]`.
  - Iterate content sections with original section positions so anchors stay aligned with existing `#local-article-content-section-N`.
  - Use `_strict_valid_local_article_paragraph_indices(...)` for item-level `item.paragraph_indices`.
  - Prefer item label for cue text and fall back to section title when item label is blank.
  - Do not access `section.paragraph_indices`; the current `RowOneLocalArticleContentSection` model has no standalone paragraph-index field.
  - Dedupe context labels/anchors case-insensitively per paragraph.
  - Cap contexts per paragraph at `LOCAL_ARTICLE_BODY_FILING_CUES_MAX_CONTEXTS`.
- [ ] Implement `_render_local_article_body_filing_cue(entries) -> str`.
  - If entries exist, render a compact filed cue with links to content-section anchors.
  - If entries are empty, render a compact unfiled cue without links.
  - Escape all labels and anchors.
- [ ] Update `_render_local_article_paragraphs(article)`.
  - When `paragraphs_zh` are aligned, render body filing cue before existing paragraph context and bilingual paragraph text.
  - When `paragraphs_zh` are not aligned, still render cue before escaped paragraph text.
  - Keep existing paragraph IDs unchanged.
- [ ] Add scoped CSS for:
  - `.local-article-body-filing-cue`
  - `-label`
  - `-links`
  - `-unfiled`
  - links inside cue.

## Task 3: Generated Site Boundary Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add `test_render_row_one_site_writes_body_filing_cues_only_on_local_article_pages`.
  - Render a site with publishable local articles and saved paragraphs.
  - Assert `articles/<story-id>.html` includes body filing cues.
  - Assert `index.html`, `articles/index.html`, and `details/<story-id>.html` do not include body filing cues.
  - Assert generated contract payload does not include `local_article_body_filing_cues`, `article_body_filing_cues`, `body_filing_cues`, `paragraph_filing_cues`, `local-article-body-filing-cues`, or `Body Filing Cues`.
  - Assert no matching JSON/HTML sidecar artifact exists under root, `articles/`, or `data/`.
- [ ] Add `test_row_one_css_includes_local_article_body_filing_cue_styles`.

## Task 4: Workflow and Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] Extend generated contract payload denylist with Stage 366 snake/kebab/title names.
- [ ] Extend artifact denylist with:
  - `local-article-body-filing-cues`
  - `article-body-filing-cues`
  - `body-filing-cues`
  - `paragraph-filing-cues`
  - `local_article_body_filing_cues`
  - `article_body_filing_cues`
  - `body_filing_cues`
  - `paragraph_filing_cues`
- [ ] Add `test_stage_366_local_article_body_filing_cues_stays_generated_site_only`.
  - Monkeypatch `_render_local_article_body_filing_cue` to a callable with the expected signature: `lambda _entries: ""`.
  - Call `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)`.
  - This follows the existing wrapper-test pattern in this file; do not replace the renderer with a string.
- [ ] Add Stage 366 docs before Stage 365 in README and `docs/row-one.md`.
- [ ] Add `test_row_one_docs_describe_stage_366_local_article_body_filing_cues_boundary`.

## Task 5: Review and Verification

- [ ] Submit this plan for Claude Code review before implementation and save the result to:
  - `docs/reviews/2026-07-09-stage-366-local-article-body-filing-cues-plan-claude.md`
- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -k "body_filing_cues or stage_366 or local_article_without_mutating_sqlite"
```

- [ ] Run focused formatting/lint:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

- [ ] Request Claude Code review and save to:
  - `docs/reviews/2026-07-09-stage-366-local-article-body-filing-cues-code-claude.md`
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
git commit -m "Stage 366: add local article body filing cues"
```

- [ ] Push `main` and write Handoff Summary with repo status, verified commands, uncommitted files, and next step.
