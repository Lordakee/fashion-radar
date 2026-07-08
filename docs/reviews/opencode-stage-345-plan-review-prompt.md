# OpenCode Stage 345 Plan Review Prompt

Review `/home/ubuntu/fashion-radar` in read-only mode.

Use model `zhipuai-coding-plan/glm-5.2` with max reasoning if available.

## Goal

Stage 345 will add a generated-site-only Saved Article Daily Summary section to
`articles/index.html`.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-345-saved-article-daily-summary-design.md`
- `docs/superpowers/plans/2026-07-08-stage-345-saved-article-daily-summary-plan.md`

## Scope Boundary

The section should derive only from existing saved article library and existing
ROW ONE article-library surfaces. It should provide compact orientation and safe
quick links. It must not add schema changes, JSON artifacts, route families,
source collection, fetching, extraction, ranking, LLM calls, connectors,
scheduling, deployment behavior, analytics, personalization, recommendation, or
compliance-review behavior.

## Review Questions

1. Is the plan technically feasible with the existing render helpers?
2. Does the plan risk duplicating existing Theme Digest, Reference Atlas,
   Evidence Board, Content Organization, or Organization Coverage Matrix output?
3. Are the safe-link and empty-state rules sufficient?
4. Are the tests and docs guards enough to keep the feature generated-site-only?
5. Are there any Critical or Important blockers?

Return a concise severity-labeled review. If approved, say Stage 345 is approved
for implementation.
