# Claude Code Stage 23 Plan Review Prompt

You are reviewing the Stage 23 design and implementation plan for
`/home/ubuntu/fashion-radar` in read-only mode. Do not edit files. Use maximum
reasoning.

## Files To Review

- `docs/superpowers/specs/2026-06-13-stage-23-imported-entity-deltas-design.md`
- `docs/superpowers/plans/2026-06-13-stage-23-imported-entity-deltas-plan.md`

## Goal

Stage 23 proposes `fashion-radar imported-entity-deltas`, a local read-only
command that compares current stored `item_entities` matches on retained
`manual_import` rows across adjacent collected-at windows.

## Scope Boundary

This must stay a raw local SQLite summary of stored matches. Do not recommend
new ingestion paths, browser automation, platform APIs, account automation,
background workflows, source-name quality/ranking, scoring/trend machinery,
candidate discovery, report/dashboard writes, migrations, dependencies, or
compliance/audit features.

## Review Focus

Check:

1. The feature is clearly distinct from `trends`, scoring, and candidate
   discovery.
2. The wording is clear that counts use current stored matches on rows in each
   collected-at window, not historical match snapshots.
3. The query plan is read-only, returns empty for missing DB without creating
   artifacts, verifies existing schema, and uses the existing read-only SQLite
   helper.
4. Counts are item-level per `(item_id, entity_name, entity_type)` and duplicate
   match rows on one item cannot inflate entity counts.
5. Top-level and entity JSON fields are deterministic and do not expose item
   titles, URLs, summaries, raw row ids, match reasons, context terms, imported
   source file paths, or confidence details.
6. `current_matched_item_count` and `baseline_matched_item_count` are named and
   specified precisely.
7. `current_source_count`, `baseline_source_count`, and `source_count_delta`
   refer only to stored local `source_name` labels.
8. Change labels and ordering are deterministic and do not imply external
   ranking.
9. The TDD plan is concrete enough to implement without guessing, including
   model names, function signatures, CLI options, table output, JSON key order,
   edge cases, review gates, and release checks.
10. The plan obeys the user's process: plan before implementation, Claude Code
    review before code, Claude Code code review before push.

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

End with one of:

- `Approved for Stage 23 implementation`
- `Not approved`
