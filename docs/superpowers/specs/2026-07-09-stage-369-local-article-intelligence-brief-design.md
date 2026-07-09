# Stage 369 Local Article Intelligence Brief Design

## Goal

Stage 369 adds a generated-site-only Local Article Intelligence Brief to each `articles/<story-id>.html` page. The section turns already-saved local article structure into a concise, readable intelligence panel that helps the ROW ONE webpage show what the article is about rather than only linking to paragraphs.

## User Value

The user wants ROW ONE to organize fashion information into useful local reading output. Stage 369 adds a single page-level brief that summarizes the current saved article into practical lanes: what to notice first, which entities are involved, where the evidence lives, and how to continue reading locally.

## Scope

In scope:
- Render only on generated local article pages: `articles/<story-id>.html`.
- Reuse the current `RowOneStory` and matching `RowOneLocalArticle` already passed to the renderer.
- Reuse existing local article fields: `brief_sections`, `content_sections`, item labels, item bodies, references, item `paragraph_indices`, saved paragraphs, content-section anchors, and paragraph anchors.
- Build a small pure view-model module with deterministic caps.
- Render compact bilingual HTML with same-page anchors only.
- Add docs, tests, generated-site-only guards, plan review artifacts, and code review artifacts.

Out of scope:
- No new app-facing JSON contract.
- No schema, runtime, manifest, data artifact, route family, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.
- No new article-source sidecars.
- No outbound article URLs as primary navigation.
- No homepage, library index, or detail-page changes.

## Placement

Render inside `articles/<story-id>.html` after the Stage 368 Local Article Body Organizer and before the saved local article body. Current local article page order becomes:

1. local article information panel
2. saved article local reading companion
3. saved article local section binder
4. saved article key signals
5. local article content segment deck
6. local article body organizer
7. local article intelligence brief
8. saved local article body

This placement gives readers a structured brief after the detailed paragraph organizer but before the full local article body.

## Proposed Feature

Feature name: **Local Article Intelligence Brief**.

The generated section contains:

- **Opening Signal**: one short statement from `why_it_matters` brief section when available, otherwise story `why_it_matters`, otherwise the first meaningful content-section body/item body.
- **Entity Lanes**: capped lanes for brands, products, people, and themes derived from existing item references and section/item labels.
- **Evidence Trail**: capped links to same-page paragraph anchors from valid item `paragraph_indices`, with safe excerpt text from saved local paragraphs.
- **Reader Route**: capped same-page links to the most useful content-section anchors, preserving local article section order.

## Data Rules

- Match only when `story.id == local_article.story_id` and `safe_local_article_story_id(story.id)` passes.
- Treat nonblank saved paragraphs as rendered-body paragraphs, matching local article body anchor semantics.
- Use strict paragraph-index validation: reject bool, non-int, negative, overflow, blank paragraph, and duplicate indices.
- Use same-page anchors only:
  - `#local-article-paragraph-N`
  - `#local-article-content-section-N`
- Normalize text with existing ROW ONE text helpers.
- Deduplicate references case-insensitively within each lane.
- Use the existing `row_one_saved_article_reference_bucket(reference)` helper as
  the canonical reference-type mapping. Keep only buckets `brands`, `products`,
  and `people` as reference lanes; derive the `themes` lane from section titles
  and item labels that are not already emitted as reference chips.
- Cap output deterministically:
  - max 4 entity lanes
  - max 4 chips per lane
  - max 4 evidence links
  - max 4 reader-route links
  - max excerpt length around 140 characters
  - max route support length around 110 characters

## Architecture

Create `src/fashion_radar/row_one/local_article_intelligence_brief.py` with dataclasses and a pure builder:

- `RowOneLocalArticleIntelligenceBrief`
- `RowOneLocalArticleIntelligenceLane`
- `RowOneLocalArticleIntelligenceChip`
- `RowOneLocalArticleIntelligenceEvidence`
- `RowOneLocalArticleIntelligenceRoute`
- `build_row_one_local_article_intelligence_brief(story, local_article)`

Render in `templates.py` using new private helpers near the Stage 368 body organizer helpers. Keep href validation local to the renderer and reuse existing fragment regexes.

## Tests

Add `tests/test_row_one_local_article_intelligence_brief.py` for builder behavior:

- builds opening signal, lanes, evidence, and route from saved local article structure.
- filters invalid paragraph indices and unsafe/mismatched story IDs.
- dedupes and caps lanes/chips/evidence/routes deterministically.
- falls back when brief sections are absent.
- handles misaligned Chinese paragraphs.

Extend `tests/test_row_one_render.py`:

- section appears only on local article pages.
- placement is after Local Article Body Organizer and before `id="local-article"`.
- HTML escapes names, labels, excerpts, and source text.
- unsafe hrefs do not render.
- section does not appear on homepage, article library index, or detail pages.
- CSS selectors exist and mobile layout is defined.

Extend `tests/test_workflows.py` and docs tests:

- generated contract payload does not contain Stage 369 identifiers.
- no standalone JSON/HTML artifacts are created in root, `articles/`, `data/`, or `data/articles/`.
- Stage 369 generated-site-only boundary appears in README and docs/row-one.md before Stage 368.

## Review Workflow

- Submit this plan to local Claude Code with `--effort max` before implementation.
- Run opencode plan review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- After implementation, request code review; if Claude Code is unavailable due budget/timeouts, record the failure and use opencode fallback.
- Fix critical and important findings before commit.

## Risks

- Overlap with Stage 356 Saved Article Key Signals: Stage 369 should not duplicate that section; it should summarize the full local article reading route and evidence trail, not compete with key signals.
- Anchor mismatch: builder must align with existing saved body anchors, which use original paragraph index + 1 for nonblank source paragraphs.
- Contract leakage: all outputs must stay HTML-only and generated-site-only.
- File size: keep builder logic in a focused module; only add thin render helpers in `templates.py`.
