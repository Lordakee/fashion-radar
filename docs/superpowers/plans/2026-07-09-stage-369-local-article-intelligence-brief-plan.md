# Stage 369 Local Article Intelligence Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. REQUIRED PROJECT GATE: submit this plan for Claude Code review before implementation; after Claude Code's plan review, run local opencode plan revision/review per `docs/REVIEW_PROTOCOL.md`.

**Goal:** Add a generated-site-only Local Article Intelligence Brief to `articles/<story-id>.html` so already-saved local article structure is turned into an opening signal, entity lanes, evidence links, and a local reader route.

**Architecture:** Add a pure builder module that derives a capped, deterministic view model from the current `RowOneStory` and matching `RowOneLocalArticle`. Render the model inside the local article page after Stage 368 Local Article Body Organizer and before the saved local article body, using same-page anchors only. Keep all outputs generated-site-only: no app JSON, schemas, runtime/manifest contracts, source collection, fetching, scoring, ranking, LLM, connectors, scheduling, deployment, analytics, recommendation, personalization, or compliance behavior changes.

**Tech Stack:** Python 3, existing ROW ONE static site renderer, dataclasses, pytest, ruff.

---

## File Map

- Create `src/fashion_radar/row_one/local_article_intelligence_brief.py`
  - Define dataclasses for the brief, lanes, chips, evidence, and route links.
  - Build opening signal, entity lanes, paragraph evidence links, and content-section route links from existing saved local article data.
  - Keep strict paragraph-index validation local and aligned with Stage 368 semantics.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import/use the Stage 369 builder.
  - Render Local Article Intelligence Brief inside local article pages only, after Stage 368 body organizer and before the saved body.
  - Add scoped CSS selectors and mobile rules.
- Add `tests/test_row_one_local_article_intelligence_brief.py`
  - Unit-test builder behavior and safety rules.
- Modify `tests/test_row_one_render.py`
  - Add renderer placement, escaping, anchor, contract, page-scope, and CSS tests.
- Modify `tests/test_workflows.py`
  - Add Stage 369 generated-site-only contract and artifact denylist coverage.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document and verify Stage 369 boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Plan Review

**Files:**

- Create: `docs/reviews/claude-code-stage-369-plan-review.md`
- Create: `docs/reviews/opencode-stage-369-plan-review.md`

- [ ] Request Claude Code plan review before implementation.
- [ ] Confirm the reviewer checks:
  - generated local-article-page-only scope.
  - builder uses only current story/local article saved sidecar state.
  - opening signal falls back deterministically.
  - entity lanes derive from existing references and labels only.
  - evidence derives from valid item-level `paragraph_indices` only.
  - route links use same-page local article section anchors only.
  - no app JSON/schema/route/artifact changes.
  - no source collection, fetching, ranking, LLM, connector, scheduling, deployment, analytics, recommendation, personalization, or compliance-review behavior.
- [ ] Save Claude Code plan review result to `docs/reviews/claude-code-stage-369-plan-review.md`.
- [ ] Run opencode plan revision/review with GLM 5.2 max and save it to `docs/reviews/opencode-stage-369-plan-review.md`.
- [ ] Fix critical and important planning issues before production code edits.
- [ ] Do not edit production code until the plan review says implementation can proceed.

## Task 2: Builder RED Tests

**Files:**

- Create: `tests/test_row_one_local_article_intelligence_brief.py`

- [ ] Add builder imports:

```python
from fashion_radar.row_one.local_article_intelligence_brief import (
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE,
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_EVIDENCE_LINKS,
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES,
    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTE_LINKS,
    build_row_one_local_article_intelligence_brief,
)
```

- [ ] Add local helpers `_lt`, `_story`, `_reference`, `_item`, `_section`, and `_article` using `RowOneStory`, `RowOneReference`, `RowOneLocalArticleContentItem`, `RowOneLocalArticleContentSection`, and `RowOneLocalArticle`.
- [ ] Add `test_build_local_article_intelligence_brief_summarizes_article_structure`:
  - Construct one safe story and matching local article.
  - Include a `why_it_matters` brief section for the opening signal.
  - Include content items with brand, product, person, and theme references.
  - Include valid paragraph indices `[0, 1, 2]` and saved paragraphs.
  - Assert the brief is not `None`.
  - Assert title is `Local Article Intelligence Brief` / `本地文章情报摘要`.
  - Assert opening signal text comes from the local `why_it_matters` brief section.
  - Assert lanes include `Brands`, `Products`, `People`, and `Themes` in that order when data exists.
  - Assert chip names are deduped and capped.
  - Assert evidence links use `#local-article-paragraph-N`.
  - Assert route links use `#local-article-content-section-N`.
- [ ] Add `test_build_local_article_intelligence_brief_filters_invalid_indices_and_blank_paragraphs`:
  - Use paragraph indices `[True, "0", -1, 0, 0, 1, 99]`.
  - Include a blank paragraph at index `1`.
  - Assert only paragraph `0` is emitted as evidence.
  - Assert no `#local-article-paragraph-0` href appears because paragraph
    anchors are 1-based (`index + 1`).
  - Assert no blank, overflow, negative, bool, or string-index href appears.
- [ ] Add `test_build_local_article_intelligence_brief_caps_outputs_deterministically`:
  - Create more lanes/chips/evidence/route candidates than caps.
  - Assert cap constants are respected and source order is preserved.
- [ ] Add `test_build_local_article_intelligence_brief_falls_back_without_brief_sections`:
  - Omit local brief sections.
  - Assert opening signal falls back to story `why_it_matters`, then content section/item body if story text is blank.
- [ ] Add `test_build_local_article_intelligence_brief_returns_none_without_meaningful_body`:
  - Assert mismatched story id returns `None`.
  - Assert unsafe story id returns `None`.
  - Assert all-blank paragraphs and no meaningful section data returns `None`.
- [ ] Run RED command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_intelligence_brief.py -q
```

Expected before implementation: import/module failures or failing assertions because the feature does not exist yet.

## Task 3: Render RED Tests

**Files:**

- Modify: `tests/test_row_one_render.py`

- [ ] Add helper `_local_article_intelligence_brief_html(html: str) -> str` that slices from `<section class="local-article-intelligence-brief"` to `id="local-article"`.
- [ ] Add `test_render_local_article_page_includes_intelligence_brief_after_body_organizer`:
  - Render a local article page with references, paragraphs, and content sections.
  - Assert `Local Article Intelligence Brief` and `本地文章情报摘要` appear.
  - Assert order: content segment deck < body organizer < intelligence brief < `id="local-article"`.
  - Assert same-page paragraph and content-section anchors appear.
- [ ] Add `test_render_local_article_intelligence_brief_escapes_and_filters_links`:
  - Include `<script>` in source name, labels, references, and paragraph text.
  - Include invalid paragraph indices.
  - Assert raw `<script>` is absent from the brief.
  - Assert escaped `&lt;script&gt;` appears where appropriate.
  - Assert no external URL, `../`, `#local-article-paragraph-0`, blank
    paragraph, or overflow href appears.
- [ ] Add `test_render_row_one_site_writes_intelligence_brief_only_on_local_article_page`:
  - Render site into `tmp_path`.
  - Assert the brief appears in the generated local article page.
  - Assert it does not appear in `index.html`, `articles/index.html`, or detail pages.
- [ ] Add `test_render_row_one_site_intelligence_brief_does_not_leak_contracts_or_artifacts`:
  - Assert edition/runtime/manifest JSON do not include Stage 369 names.
  - Assert no root/articles/data/data/articles standalone JSON or HTML artifacts exist.
- [ ] Add `test_row_one_css_includes_local_article_intelligence_brief_styles`:
  - Assert key CSS selectors and mobile single-column rule exist.

## Task 4: Builder Implementation

**Files:**

- Create: `src/fashion_radar/row_one/local_article_intelligence_brief.py`

- [ ] Implement dataclasses:

```python
@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceChip:
    label: LocalizedText
    href: str | None = None
    meta: str = ""

@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceLane:
    key: str
    title: LocalizedText
    chips: tuple[RowOneLocalArticleIntelligenceChip, ...]
    total_count: int

@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceEvidence:
    label: LocalizedText
    href: str
    excerpt: LocalizedText

@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceRoute:
    label: LocalizedText
    href: str
    support: LocalizedText | None

@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceBrief:
    title: LocalizedText
    source_name: str
    opening_signal: LocalizedText
    lanes: tuple[RowOneLocalArticleIntelligenceLane, ...]
    evidence: tuple[RowOneLocalArticleIntelligenceEvidence, ...]
    routes: tuple[RowOneLocalArticleIntelligenceRoute, ...]
```

- [ ] Implement constants:

```python
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_EVIDENCE_LINKS = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTE_LINKS = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_EXCERPT_CHARS = 140
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_SUPPORT_CHARS = 110
```

- [ ] Implement `build_row_one_local_article_intelligence_brief(story, local_article)`:
  - Return `None` for mismatched/unsafe story ids.
  - Derive rendered paragraph indices from nonblank `local_article.paragraphs`.
  - Build opening signal from local `why_it_matters` brief section, story `why_it_matters`, then section/item body fallback.
  - Build lanes for brands/products/people/themes from existing references and labels.
  - Build evidence from valid paragraph indices.
  - Build routes from content sections with meaningful title/body/items.
  - Return `None` if there is no opening signal, no lanes, no evidence, and no routes.
- [ ] Use the existing `row_one_saved_article_reference_bucket(reference)` helper
  as the canonical reference mapping. Emit reference lanes only for buckets
  `brands`, `products`, and `people`; derive the `themes` lane from section
  titles and item labels that are not already emitted as reference chips.
- [ ] Preserve anchor numbering rules:
  - Paragraph href `N` is original paragraph index + 1.
  - Content-section href `N` is the 1-based `section_position`.
- [ ] Keep helper functions local:
  - `_nonblank_localized_text`
  - `_truncate_localized_text`
  - `_strict_valid_paragraph_indices`
  - `_paragraph_view_model`
  - `_paragraph_excerpt`
  - `_section_href`
  - `_lane_titles`

- [ ] Run GREEN command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_intelligence_brief.py -q
```

Expected after implementation: all Stage 369 builder tests pass.

## Task 5: Render Implementation

**Files:**

- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] Import Stage 369 dataclasses and builder.
- [ ] Build `local_article_intelligence_brief` inside `render_local_article_page_html`.
- [ ] Insert rendered HTML after `{local_article_body_organizer}` and before `{local_article_section}`.
- [ ] Add render helpers:
  - `_render_local_article_intelligence_brief`
  - `_render_local_article_intelligence_lane`
  - `_render_local_article_intelligence_chip`
  - `_render_local_article_intelligence_evidence`
  - `_render_local_article_intelligence_route`
  - `_safe_local_article_intelligence_href`
- [ ] Implement `_safe_local_article_intelligence_href` by delegating to the
  existing `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and
  `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` constants.
- [ ] Add scoped CSS selectors:
  - `.local-article-intelligence-brief`
  - `.local-article-intelligence-brief-header`
  - `.local-article-intelligence-brief-opening`
  - `.local-article-intelligence-brief-lanes`
  - `.local-article-intelligence-brief-lane`
  - `.local-article-intelligence-brief-chip`
  - `.local-article-intelligence-brief-evidence`
  - `.local-article-intelligence-brief-route`
- [ ] Add mobile single-column rules.
- [ ] Run render tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "intelligence_brief or local_article_body_organizer or content_segment_deck"
```

Expected after implementation: selected render tests pass.

## Task 6: Docs and Workflow Guards

**Files:**

- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] Add this exact Stage 369 boundary paragraph before Stage 368 in README and docs/row-one.md:

```text
Stage 369 adds generated-site only Local Article Intelligence Brief inside `articles/<story-id>.html` between the Local Article Body Organizer and the saved local article body; it reuses current-edition saved local article sidecars, existing saved local paragraphs, existing local article brief sections, existing local article content sections, existing item references, existing item-level paragraph indices, existing content-section anchors, and existing paragraph anchors to summarize each saved article body into an opening signal, entity lanes, paragraph evidence trail, and local reader route without changing app-facing contracts; it does not create `data/local-article-intelligence-brief.json`, does not create `data/article-intelligence-brief.json`, does not create `data/intelligence-brief.json`, does not create `local-article-intelligence-brief.html`, does not create `article-intelligence-brief.html`, does not create `intelligence-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] Add docs test that asserts the exact paragraph appears in README and docs/row-one.md before Stage 368.
- [ ] Extend stale-phrase denylist with Stage 369 artifact and behavior phrases.
- [ ] Extend workflow JSON contract denylist with:
  - `local_article_intelligence_brief`
  - `article_intelligence_brief`
  - `intelligence_brief`
  - `RowOneLocalArticleIntelligenceBrief`
  - `Local Article Intelligence Brief`
  - `本地文章情报摘要`
  - `local-article-intelligence-brief`
  - `article-intelligence-brief`
  - `intelligence-brief`
- [ ] Extend artifact denylist in root, `articles/`, `data/`, and `data/articles/`.
- [ ] Add wrapper guard:

```python
def test_stage_369_local_article_intelligence_brief_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    monkeypatch.setattr(
        row_one_templates,
        "_render_local_article_intelligence_brief",
        lambda _brief: "",
        raising=False,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

  This wrapper intentionally follows the Stage 368 guard pattern and depends on
  the existing `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`
  workflow test remaining in `tests/test_workflows.py`.

## Task 7: Verification, Review, Commit, Push

- [ ] Run focused RED before production implementation:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_intelligence_brief.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "intelligence_brief or stage_369 or local_article_intelligence_brief or body_organizer or stage_368"
```

Expected before implementation: new builder/render/CSS/workflow assertions fail because the feature does not exist yet.

- [ ] After implementation, run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_intelligence_brief.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "intelligence_brief or stage_369 or local_article_intelligence_brief or body_organizer or stage_368"
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

- [ ] Request Claude Code code review and save it to `docs/reviews/claude-code-stage-369-code-review.md`.
- [ ] If Claude Code is unavailable, record the failure in `docs/reviews/claude-code-stage-369-code-review.md`, run opencode fallback review with GLM 5.2 max, and save it to `docs/reviews/opencode-stage-369-code-review.md`.
- [ ] Fix critical and important review findings.
- [ ] Commit with message:

```bash
git add src/fashion_radar/row_one/local_article_intelligence_brief.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_article_intelligence_brief.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/specs/2026-07-09-stage-369-local-article-intelligence-brief-design.md docs/superpowers/plans/2026-07-09-stage-369-local-article-intelligence-brief-plan.md docs/reviews/claude-code-stage-369-plan-review.md docs/reviews/opencode-stage-369-plan-review.md docs/reviews/claude-code-stage-369-code-review.md docs/reviews/opencode-stage-369-code-review.md
git commit -m "Stage 369: add local article intelligence brief"
```

- [ ] Push to GitHub.
- [ ] Write Handoff Summary with:
  - repo status
  - verified commands
  - uncommitted files
  - next step
