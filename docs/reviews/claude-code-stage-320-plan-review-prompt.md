# Stage 320 Design and Implementation Plan Review Prompt

Please review the Stage 320 spec and implementation plan for
`/home/ubuntu/fashion-radar`.

## Files To Review

- `docs/superpowers/specs/2026-07-07-stage-320-row-one-homepage-daily-edit-design.md`
- `docs/superpowers/plans/2026-07-07-stage-320-row-one-homepage-daily-edit-plan.md`

## Goal

Stage 320 should add a generated-site-only `Daily Edit / 今日编辑简报` section to
ROW ONE homepage HTML. The section should organize existing ROW ONE payload and
sidecar information into a scan-first editorial briefing surface without
changing generated data contracts.

## Required Scope

The stage may reuse existing in-memory data already available to homepage
rendering:

- existing `RowOneEdition`
- existing `row-one-app/v7` `app_payload`
- existing `edition_brief`
- existing `signal_synthesis`
- existing `daily_digest.briefing_topics`
- existing `daily_digest.blocks`
- existing `story_directory`
- optional existing sidecar-derived homepage structures already passed into
  `render_index_html()`

The stage must not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- story IDs
- detail routes
- paragraph anchors
- source collection
- article fetching/extraction
- scoring or ranking
- connectors/social/community tools
- LLM calls
- image-generation calls
- translation workflow
- compliance-review product behavior

It must not write a new JSON artifact.

## Please Check

- Is this a reasonable next node after Stage 319?
- Is the homepage placement appropriate and non-disruptive?
- Does the plan avoid creating a new app contract or source-acquisition layer?
- Are tests sufficient for rendering, omission, escaping, safe links, CSS,
  workflow boundaries, and docs boundaries?
- Is the private helper approach in `templates.py` acceptable, or should the plan
  split a separate module?
- Are there missing risks, conflicting requirements, or likely regressions?

Return findings ordered by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional clarification.

If there are no Critical or Important issues, state that clearly.
