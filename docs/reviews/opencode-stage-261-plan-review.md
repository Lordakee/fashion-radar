# opencode Stage 261 Plan Review

Reviewer: opencode (GLM 5.2 max), fallback reviewer after the local primary
review route was unavailable
Stage: 261 (ROW ONE editorial synthesis)
Scope: Stage 261 design spec and implementation plan before coding

## Verdict

Accept with fixes.

The architecture, scope boundaries, and test strategy are sound and verified
against the current code. The fallback reviewer found no critical issues.

## Critical Issues

None.

## Important Issues

- `signal_context` duplicated existing `why_it_matters` text because the
  original helper examples restated heat/candidate scores and source counts.
- `reader_path` was effectively a per-section static sentence repeated across
  many stories, which weakly delivered the information-organization goal.

## Minor Notes

- Recent-item `editorial_takeaway` reused the headline and could be redundant on
  homepage cards.
- The spec listed more input fields than the helper examples consumed.
- Entity and candidate helper examples accepted an unused `source_name`
  parameter.
- The plan referenced an undefined `section-kicker` CSS class.
- The plan should state exactly where the homepage takeaway is inserted.

## Required Plan And Spec Changes Before Coding

- Make `signal_context` additive to `why_it_matters` by using mention deltas,
  growth ratio, match evidence, first-seen timing, or local-item/source context
  rather than heat score, candidate score, source count, and section placement.
- Give `reader_path` per-story variation through label, tag, source, or rank.
- Remove unused `source_name` parameters from entity/candidate helper examples.
- Replace `section-kicker` with a defined class or add CSS for the class.
- Sync the spec data-input list with the fields the helper examples consume.

## Resolution

Applied before coding:

- `signal_context` now uses current/baseline mentions and growth ratio for
  entities, current/baseline mentions and first-seen date for candidates, and
  retained local-item/source context for recent items.
- `reader_path` now varies by entity label, candidate label, or source name.
- Entity and candidate helper examples no longer accept `source_name`.
- The detail panel uses `.story-section`, and the plan calls out CSS for
  `.story-takeaway`, `.detail-panel`, and `.story-section`.
- The spec data-input and acceptance-criteria sections now match the intended
  helper inputs.

## Recommended Next Action

Proceed to Task 1. A second full plan review is not required; a quick re-check of
the updated helper bodies and CSS class choice is sufficient before coding.
