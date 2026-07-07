You are Claude Code reviewing Stage 327 for `/home/ubuntu/fashion-radar`.

Use maximum reasoning. Do not edit files.

## Stage 327 Goal

Add a generated-site only Saved Signal Index inside `articles/index.html` so ROW
ONE organizes the current edition's saved local articles by existing
brand/person/designer/product references from local article content sections.

## Proposed Approach

- New pure render-only builder: `src/fashion_radar/row_one/saved_signal_index.py`
- Builder inputs: current `RowOneEdition` plus in-memory
  `local_articles_by_story_id`
- Builder source data:
  - `RowOneLocalArticle.content_sections`
  - `RowOneLocalArticleContentItem.references`
  - `RowOneLocalArticleContentItem.paragraph_indices`
  - existing `story.detail_path`
- Render section inside existing `articles/index.html`, after the saved article
  library hero and before source-grouped article list.
- No new generated top-level directory and no new page outside
  `articles/index.html`.
- Optional homepage copy update only; no duplicated signal cards on homepage.

## Specs And Plans

- Spec: `docs/superpowers/specs/2026-07-07-stage-327-row-one-saved-signal-index-design.md`
- Plan: `docs/superpowers/plans/2026-07-07-stage-327-row-one-saved-signal-index-plan.md`

## Required Boundaries

- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `saved_signal_index`, `signal_index`, `entity_index`,
  `brand_index`, `product_index`, `saved_article_entity_index`,
  `saved_article_brand_index`, `saved_article_product_index`, or related keys to
  app/runtime/manifest JSON.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not change story IDs, detail routes, local article reader anchors,
  paragraph anchors, content-section anchors, or paragraph evidence anchors.
- Do not add source collection, fetching, extraction, matching, semantic
  inference, scoring, ranking, demand proof, platform coverage verification, LLM
  calls, translation calls, image generation, connectors, scheduling,
  deployment, app/client behavior, or compliance-review product features.
- Do not add dependencies.

## What To Check

- Is the feature the right next step toward organizing local fashion information
  instead of only presenting links?
- Whether the embedded `articles/index.html` approach is feasible for Stage 327's
  generated-site only scope?
- Whether no-child-page containment is adequately tested by generated output and cleanup
  sentinels?
- Do not propose a separate generated child page for Stage 327.
- Does the builder design correctly stay current-edition and in-memory only?
- Are link safety, escaping, caps, ordering, and stale-sidecar risks covered?
- Are the proposed tests sufficient and concrete enough?
- Are JSON contract sentinels and docs boundaries adequate?
- Are there any contradictions between the spec and plan?

## Output Format

### Strengths

### Issues

#### Critical (Must Fix)

#### Important (Should Fix)

#### Minor (Nice to Have)

For each issue, include file:line, what is wrong, why it matters, and how to
fix.

### Recommendation

Proceed with implementation? Yes | No | With fixes
