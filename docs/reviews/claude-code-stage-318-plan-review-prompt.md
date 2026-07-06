# Stage 318 Design and Implementation Plan Review Prompt

Please review the Stage 318 spec and implementation plan for
`/home/ubuntu/fashion-radar`.

## Files to Review

- `docs/superpowers/specs/2026-07-06-stage-318-row-one-detail-continue-reading-rail-design.md`
- `docs/superpowers/plans/2026-07-06-stage-318-row-one-detail-continue-reading-rail-plan.md`

## Goal

Stage 318 should add a generated-site-only `Continue Reading / 继续阅读` rail to
ROW ONE detail pages, after the evidence trail, with up to three deterministic
next reads from the same edition.

## Required Scope

The stage must be presentation-only and must reuse existing generated data:

- existing edition stories
- existing section labels
- existing detail routes
- existing story summaries and editorial takeaways

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

- Is this a reasonable next node after Stages 316-317?
- Are touched files scoped correctly?
- Are tests sufficient to prove deterministic selection, safe route handling,
  sibling detail links, escaping, omission, caps, and contract boundaries?
- Does the plan avoid creating an external-link aggregator?
- Are there any missing risks, conflicting instructions, or likely regressions?

Return findings ordered by severity:

- Critical: must fix before implementation
- Important: should fix before implementation
- Minor: optional clarification

If there are no Critical or Important issues, state that clearly.
