# Stage 325 ROW ONE Paragraph Evidence Polish Design

## Goal

Close the non-blocking Stage 324 code-review polish items for the ROW ONE detail-page paragraph evidence index without changing contracts, data models, source behavior, or feature scope.

## User Value

Stage 324 added a generated-site-only paragraph evidence index that helps readers understand how saved local article paragraphs support ROW ONE's organized content sections. Claude Code approved the implementation and identified three minor polish items:

- avoid an empty `<div></div>` when an evidence support item has no references
- avoid an empty Chinese body span when `item.body.zh` is blank or whitespace-only by falling back to the escaped English body excerpt
- explicitly test that the local article map links to the paragraph evidence block

Stage 325 makes those tidyups now so the detail page HTML is cleaner and the navigation contract is tested directly before moving on to larger information-organization features.

## Scope

- Generated ROW ONE detail HTML only.
- Focused tests in `tests/test_row_one_render.py`.
- Existing `RowOneLocalArticle` data only.
- Existing `#local-article-paragraph-evidence` and local article map behavior only.
- No app/runtime/manifest JSON changes.

## Non-Goals

- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not change story IDs, detail routes, local article reader anchors, paragraph anchors, content-section anchors, or the Stage 324 evidence section id.
- Do not add source collection, fetching, extraction, scoring, ranking, LLM calls, translation calls, image generation, connectors, scheduling, deployment behavior, or compliance-review product features.
- Do not add dependencies.

## Behavior

When rendering a paragraph evidence support item:

- If `item.references` is empty, omit the reference wrapper instead of emitting an empty `<div></div>`.
- If `item.body.zh` is blank or whitespace-only, render the Chinese body span with the normalized, escaped English body excerpt fallback.
- Continue escaping all rendered values with `_esc()`.
- Continue using existing local fragment hrefs only.
- Preserve existing English rendering and reference-chip rendering.

When rendering the local article map:

- Keep the `Evidence / 线索` map link only when the paragraph evidence index exists.
- Add a focused test that slices the map HTML and asserts `href="#local-article-paragraph-evidence"` appears before the evidence block.

## Testing Requirements

- Render test: a paragraph evidence support item without references does not emit an empty `<div></div>` in the evidence section.
- Render test: a paragraph evidence support item with whitespace-only `body.zh` falls back to the normalized, escaped English body excerpt in the Chinese span.
- Render test: the local article map explicitly links to `#local-article-paragraph-evidence` before the evidence block.
- Existing Stage 324 focused render tests continue to pass.
- Full project tests, Ruff, lock check, release hygiene, and secret marker scan pass.

## Definition Of Done

- Stage 325 spec and plan are reviewed before implementation.
- Stage 324 minor polish items are covered by failing tests first and then implemented.
- No JSON contracts, schemas, models, artifacts, source behavior, connector behavior, scheduling, deployment, or compliance-review product behavior changes.
- Claude Code code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
