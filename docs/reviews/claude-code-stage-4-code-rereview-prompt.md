# Claude Code Stage 4 Code Re-Review Prompt

You are Claude Code re-reviewing Fashion Radar after the initial Stage 4 code
review.

Repository: `/home/ubuntu/fashion-radar`

Initial review file:

- `docs/reviews/claude-code-stage-4-code-review.md`

Initial verdict:

- Approved after fixes.

Initial important findings:

- I1: SQLite FK cascade is inert by default, so Stage 5 `clean-old-data` must not
  rely on `ON DELETE CASCADE` to remove `item_entities` rows.
- I2: Stage 4 computes `first_seen_at` from retained item history. Stage 5
  pruning can make a long-lived entity look `new` unless stable entity first-seen
  is persisted independently of item retention.

Fix applied:

- Updated `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
  Stage 5 section only.
- Added a pruning contract requiring explicit `item_entities` deletion before
  deleting pruned items, with tests proving no orphan matcher rows remain even
  when SQLite FK cascade is inert.
- Added a stable first-seen contract requiring Stage 5 schema version `3` -> `4`
  with an `entity_first_seen` table keyed by `entity_name` and `entity_type`,
  storing at least `first_seen_at` and `last_seen_at`.
- Added Stage 5 TDD tasks requiring:
  - v3 -> v4 migration tests.
  - repository helpers for entity first-seen/last-seen.
  - `match_stored_items()` updates to persist first-seen from item
    `collected_at`.
  - scoring tests proving stable first-seen is preferred over retained item
    history for the `new` label.
  - pruning tests proving old entities are not re-labeled `new` after old items
    are deleted.
  - pruning command implementation that deletes matcher rows explicitly before
    item rows.

Please review only whether the plan changes fully address I1 and I2 and whether
Stage 4 can now be committed and Stage 5 implementation can begin.

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 4 commit and Stage 5 implementation
- Approved after fixes
- Do not proceed
