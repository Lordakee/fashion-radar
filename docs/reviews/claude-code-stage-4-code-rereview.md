# Claude Code Stage 4 Code Re-Review

Re-review complete. Both I1 (FK cascade) and I2 (stable first-seen) are fully
resolved in the updated Stage 5 plan.

## Summary

**Verdict:** Approved for Stage 4 commit and Stage 5 implementation

The plan fixes are comprehensive and testable:

**I1 Resolution (FK cascade):**

- Explicitly acknowledges SQLite FK cascade is inert by default.
- Requires explicit deletion of `item_entities` rows before deleting items.
- Adds TDD tasks proving no orphan matcher rows remain even when FK cascade is
  off.
- Includes acceptance criterion verifying the fix.

**I2 Resolution (stable first-seen):**

- Adds `entity_first_seen` table for lifecycle tracking independent of item
  retention.
- Updates matching to persist first-seen from item `collected_at`.
- Updates scoring to prefer stable table over retained item history.
- Adds TDD tasks with regression tests proving old entities do not become `new`
  after pruning.
- Includes acceptance criterion verifying pruning correctness.

Both fixes are integrated into the Stage 5 TDD workflow with explicit contracts,
tasks, and verification requirements. Stage 4 can be committed now, and Stage 5
implementation can proceed.
