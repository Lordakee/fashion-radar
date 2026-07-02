# opencode Stage 264 Plan Review Prompt

You are the secondary/fallback reviewer for Fashion Radar Stage 264. Review the
Stage 264 design and implementation plan in read-only mode. Do not edit files.

## Context

Claude Code is the primary reviewer. If a Claude plan review exists, consider
its findings and decide whether the plan needs revision. If no Claude review is
available, perform an independent plan review.

## Objective

Stage 264 adds ROW ONE Daily Readiness & Preview:

- a derived `RowOneReadiness` helper;
- a homepage Latest Edition status strip;
- `fashion-radar row-one preview`;
- first-run smoke coverage for ROW ONE CLI help and schedule ordering;
- package archive guardrails for ROW ONE docs/schema/package files.

## Boundaries

The plan must not add new source acquisition, scraping, browser automation,
platform APIs, login/cookie/session behavior, translation, LLM calls, image
generation, paid APIs, deployment, remote hosting, auth, scoring/ranking changes,
demand proof, platform coverage verification, or compliance-review product work.
It must not change the `row-one-app/v1` JSON contract shape.

## Files To Review

- `docs/superpowers/specs/2026-07-02-stage-264-row-one-daily-readiness-preview-design.md`
- `docs/superpowers/plans/2026-07-02-stage-264-row-one-daily-readiness-preview-plan.md`
- `docs/reviews/claude-code-stage-264-plan-review.md` if present
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- Existing ROW ONE implementation and tests under `src/fashion_radar/row_one/`
  and `tests/test_row_one*.py`

## Output Format

Return one coherent review body with:

- Critical
- Important
- Minor
- Plan revision recommendations
- Verdict

Do not include command logs, tool chatter, or duplicated verdicts.
