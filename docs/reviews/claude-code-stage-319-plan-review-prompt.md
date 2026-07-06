# Stage 319 Design and Implementation Plan Review Prompt

Please review the Stage 319 spec and implementation plan for
`/home/ubuntu/fashion-radar`.

## Files to Review

- `docs/superpowers/specs/2026-07-06-stage-319-row-one-detail-signal-briefing-panel-design.md`
- `docs/superpowers/plans/2026-07-06-stage-319-row-one-detail-signal-briefing-panel-plan.md`

## Goal

Stage 319 should add a generated-site-only `Signal Briefing / 信号简报` panel to
ROW ONE detail pages. The panel should organize existing story fields,
references, and optional saved local article sections into a concise briefing
surface without changing generated data contracts.

## Required Scope

The stage must be presentation-only and must reuse existing generated data:

- existing `RowOneEdition`
- existing `RowOneStory`
- existing story summary, why-it-matters, signal-context, reader-path
- existing story references
- existing saved local article sidecars when present
- existing paragraph anchors

The stage must not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- detail routes
- paragraph anchors
- source collection
- article fetching/extraction
- scoring
- connectors/social/community tools
- LLM calls
- compliance-review product behavior

It must not write a new JSON artifact.

## Please Check

- Is this a reasonable next node after Stages 316-318?
- Are touched files scoped correctly?
- Are tests sufficient to prove placement, rendering, escaping, reference
  de-duplication/caps, local cue caps, paragraph anchor safety, omission of
  optional cue rows, CSS coverage, workflow boundaries, and docs boundaries?
- Does the plan avoid creating a new data contract or source-acquisition layer?
- Are there any missing risks, conflicting instructions, or likely regressions?

Return findings ordered by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional clarification.

If there are no Critical or Important issues, state that clearly.
