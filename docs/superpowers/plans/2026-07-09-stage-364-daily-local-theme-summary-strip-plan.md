# Stage 364 Daily Local Theme Summary Strip Implementation Plan

> **For agentic workers:** REQUIRED PROCESS: submit this plan for Claude Code review before implementation. After implementation, request code review, run full gates, commit, push, and write a Handoff Summary.

**Goal:** Add a generated-site-only homepage Daily Local Theme Summary Strip that turns existing saved article content organization groups into compact theme-level cards with deterministic summaries, counts, references, and safe local article page links.

**Architecture:** Keep the feature render-only. `render.py` will pass the existing safe detail-path-to-local-article-page href map into `render_index_html`. `templates.py` will derive theme cards from `RowOneSavedArticleContentOrganization`, saved local articles, card leads, card references, source names, paragraph indices, and generated href maps. No builders, schemas, JSON payloads, sidecars, routes, fetching, LLM, scheduling, analytics, personalization, recommendation, or compliance-review behavior are added.

**Tech Stack:** Python 3, existing ROW ONE render pipeline, existing Pydantic models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add optional `daily_local_theme_summary_strip_hrefs_by_detail_path: Mapping[str, str] | None = None` to `render_index_html(...)`.
  - Render `_render_daily_local_theme_summary_strip(...)` after `daily_local_coverage_map_section` and before `saved_article_content_organization_section`.
  - Add private theme-strip dataclasses/helpers and scoped CSS.
- Modify `src/fashion_radar/row_one/render.py`
  - Reuse `_local_article_page_hrefs_by_detail_path(...)`.
  - Pass the existing detail-path href map into `render_index_html(...)`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for grouping, ordering, caps, link safety, escaping, placement, homepage-only site generation, and CSS.
- Modify `tests/test_workflows.py`
  - Add generated contract payload denylist entries, artifact stem guards, and a generated-site-only wrapper for Stage 364.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 364 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Direct Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] Add `_daily_local_theme_summary_strip_section_html(index_html: str) -> str` near existing homepage section helpers.
- [ ] Add `test_render_index_html_includes_daily_local_theme_summary_strip`.
  - Build organization groups for Read First, People & Brands, Products, Source Structure, and an overflow group.
  - Use hostile text in titles/leads/references to prove escaping.
  - Include duplicate references and duplicate source names to prove dedupe.
  - Include one card with a renderable content-section fragment and one card that must fall back to `#local-article-paragraph-2`.
  - Assert bilingual heading, theme order, four-theme cap, counts, source/reference chips, truncated summary, local article hrefs, no raw `<script>`, and no full saved paragraph body.
- [ ] Add `test_render_index_html_filters_unsafe_daily_local_theme_summary_strip`.
  - Cover unsafe detail paths, unsafe story ids, missing href map entries, nested/absolute/traversal/whitespace/dot/double-slash hrefs, mismatched href stems, missing local articles, mismatched local article story ids, empty paragraphs, blank source names, and invalid paragraph indices.
- [ ] Add `test_render_index_html_omits_daily_local_theme_summary_strip_without_eligible_cards`.
- [ ] Add placement tests:
  - after Daily Local Coverage Map and before Saved Article Content Organization;
  - before Saved Article Content Organization when Daily Local Coverage Map is absent.

## Task 2: Template Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] Add constants near other Daily Local constants:
  - `DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_THEMES = 4`
  - `DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_LINKS_PER_THEME = 2`
  - `DAILY_LOCAL_THEME_SUMMARY_STRIP_MAX_REFS_PER_THEME = 5`
  - `DAILY_LOCAL_THEME_SUMMARY_STRIP_SUMMARY_CHARS = 160`
- [ ] Add private dataclasses near `_DailyLocalCoverageMapSource`:
  - `_DailyLocalThemeSummaryStripLink`
  - `_DailyLocalThemeSummaryStripTheme`
- [ ] Add `daily_local_theme_summary_strip_hrefs_by_detail_path` to `render_index_html(...)` after the Stage 363 coverage-map href argument.
- [ ] Derive `daily_local_theme_summary_strip_section` with `_render_daily_local_theme_summary_strip(...)` and insert it after `{daily_local_coverage_map_section}`.
- [ ] Implement derivation helpers that:
  - iterate existing organization groups/cards in order;
  - normalize source names and references;
  - validate card detail paths with `validated_row_one_detail_relative_path(...)`;
  - validate local article availability and usable paragraphs;
  - validate generated article hrefs with existing same-site page-href helper semantics;
  - use renderable content-section anchors when possible;
  - fall back to safe paragraph anchors when needed;
  - aggregate card/source/article/paragraph counts;
  - cap themes, refs, and links.
- [ ] Implement HTML helpers with escaped bilingual text and no saved paragraph body excerpts.
- [ ] Add scoped CSS near existing Daily Local homepage styles and responsive rules.

## Task 3: Render Pipeline and Site Tests

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] Pass `daily_local_theme_summary_strip_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path` into `render_index_html(...)`.
- [ ] Add `test_render_row_one_site_writes_daily_local_theme_summary_strip_homepage_only`.
  - Assert homepage contains the strip.
  - Assert `articles/index.html`, `articles/<story-id>.html`, and detail pages do not contain the strip.
  - Assert generated contract payload does not contain `daily_local_theme_summary_strip`, `daily-local-theme-summary-strip`, or `Daily Local Theme Summary Strip`.
  - Assert no `data/daily-local-theme-summary-strip.json`, `data/local-theme-summary-strip.json`, or `data/theme-summary-strip.json` exists.
- [ ] Add `test_row_one_css_includes_daily_local_theme_summary_strip_styles`.

## Task 4: Workflow and Docs Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] Extend generated contract payload denylist with `Daily Local Theme Summary Strip`, `daily-local-theme-summary-strip`, and `daily_local_theme_summary_strip`.
- [ ] Extend artifact denylist with:
  - `daily-local-theme-summary-strip`
  - `local-theme-summary-strip`
  - `theme-summary-strip`
  - `daily_local_theme_summary_strip`
  - `local_theme_summary_strip`
  - `theme_summary_strip`
- [ ] Add `test_stage_364_daily_local_theme_summary_strip_stays_generated_site_only` workflow wrapper.
- [ ] Prepend Stage 364 boundary text before Stage 363 in README and `docs/row-one.md`.
- [ ] Add `test_row_one_docs_describe_stage_364_daily_local_theme_summary_strip_boundary` with stale-phrase guards for JSON artifacts, new routes, changed schemas, fetching, LLM, scheduling, analytics, recommendation, and compliance-review behavior.

## Task 5: Review and Verification

- [ ] Run focused Stage 364 tests.
- [ ] Run `ruff format --check` and `ruff check` on touched files.
- [ ] Request Claude Code review and save to `docs/reviews/2026-07-09-stage-364-daily-local-theme-summary-strip-code-claude.md`.
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
git commit -m "Stage 364: add daily local theme summary strip"
```

- [ ] Push `main` and write Handoff Summary with repo status, verified commands, uncommitted files, and next step.
