# Stage 317 Design and Implementation Plan Review Prompt

Please review the Stage 317 spec and implementation plan for
`/home/ubuntu/fashion-radar`.

## Files to Review

- `docs/superpowers/specs/2026-07-06-stage-317-row-one-detail-saved-paragraph-previews-design.md`
- `docs/superpowers/plans/2026-07-06-stage-317-row-one-detail-saved-paragraph-previews-plan.md`

## Goal

Stage 317 should add generated-site detail-page saved paragraph previews inside
organized local article content items. This should improve the reading
experience after Stage 316 homepage cards link readers to
`#local-article-content-section-N`.

## Required Scope

The stage must be presentation-only and must reuse existing generated data:

- existing `data/articles/<story-id>.json` sidecars
- existing saved local paragraphs
- existing `content_sections`
- existing detail routes
- existing paragraph anchors

The stage must not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- source collection
- article fetching/extraction
- scoring
- connectors/social/community tools
- LLM calls
- compliance-review product behavior

It must not write a new JSON artifact.

## Please Check

- Is the proposed feature the right next node after Stage 316?
- Are the touched files scoped correctly?
- Are tests sufficient to prove preview rendering, escaping, filtering, caps,
  bilingual behavior, and contract boundaries?
- Does the plan preserve existing one-based rendered paragraph anchors and
  zero-based internal paragraph indices?
- Are there any missing risks, conflicting instructions, or likely regressions?

Return findings ordered by severity:

- Critical: must fix before implementation
- Important: should fix before implementation
- Minor: optional clarification

If there are no Critical or Important issues, state that clearly.
