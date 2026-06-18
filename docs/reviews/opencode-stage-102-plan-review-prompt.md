# Stage 102 Plan Review Prompt

Review the Stage 102 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/scoring.md`, scoped only to the
`## Limits` section, so scoring docs remain documented as local configured
source/imported-signal boundaries rather than platform-wide, publication-time,
media-analysis, external-engagement, or market-wide claims.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-102-scoring-docs-limits-design.md`
- `docs/superpowers/plans/2026-06-18-stage-102-scoring-docs-limits-plan.md`
- `docs/scoring.md`

## Planned Test

The implementation will add `tests/test_scoring_docs.py` with one docs-only test
that extracts `## Limits` and asserts:

- `Scores only reflect configured sources and imported local signals.`
- `Candidate signals only reflect configured sources and imported local signals.`
- `Trend deltas only reflect configured sources and imported local signals.`
- `Candidate deltas are limited by configured candidate discovery thresholds.`
- `Counts use collected time, not necessarily publication time.`
- `Dashboard mention tabs show mention counts, while candidate signal views read the latest report JSON.`
- `There is no image/video or external engagement analysis in v0.1.0.`

## Scope Constraints

Allowed changes:

- `tests/test_scoring_docs.py`
- Stage 102 review artifacts

Disallowed changes:

- `docs/scoring.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime scoring, candidate discovery, trend delta, report, dashboard, or CLI
  tests
- first-run, source-pack, entity-pack, scheduling, dashboard, manual-import,
  candidate-discovery, community-signal, or project-brief docs guards

Do not expand this stage into scoring algorithm changes, generated data,
dashboard/report behavior, scheduling, source acquisition, connector behavior,
platform search, social monitoring, compliance/audit/legal review, or runtime
validation.

## Review Questions

1. Does the plan protect a real `docs/scoring.md` local configured-source
   scoring boundary without changing product behavior?
2. Are the planned phrases present in `docs/scoring.md` and scoped narrowly
   enough to `## Limits`?
3. Does the plan avoid overlap with recent docs-boundary stages and runtime
   scoring/trend tests?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
