# Claude Code Stage 23 Plan Rereview Prompt

You are rereviewing the Stage 23 design and implementation plan for
`/home/ubuntu/fashion-radar` in read-only mode. Do not edit files. Use maximum
reasoning.

## Files To Review

- `docs/superpowers/specs/2026-06-13-stage-23-imported-entity-deltas-design.md`
- `docs/superpowers/plans/2026-06-13-stage-23-imported-entity-deltas-plan.md`
- Prior review result:
  `docs/reviews/claude-code-stage-23-plan-review.md`

## Goal

Stage 23 proposes `fashion-radar imported-entity-deltas`, a local read-only
command that compares current stored `item_entities` matches on retained
`manual_import` rows across adjacent collected-at windows.

## Prior Important Findings To Recheck

1. `current_matched_item_count` / `baseline_matched_item_count` semantics with
   `--entity-type`.
2. Concrete current/baseline row classification and boundary tests.
3. Timestamp parsing and no reliance on lexical `collected_at` ordering.
4. Deterministic tests for all change labels and ordering.
5. Direct tests for per-window stored `source_name` label counts.
6. Forbidden output fields checked broadly.
7. Explicit process gate: Claude Code plan approval before implementation.
8. Direct-main commit/push step constrained to the user-authorized workflow and
   code-review completion.

## Scope Boundary

This must stay a raw local SQLite summary of stored matches. Do not recommend
new ingestion paths, browser automation, platform APIs, account automation,
background workflows, source-name quality/ranking, scoring/trend machinery,
candidate discovery, report/dashboard writes, migrations, dependencies, or
compliance/audit features.

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

End with one of:

- `Approved for Stage 23 implementation`
- `Not approved`
