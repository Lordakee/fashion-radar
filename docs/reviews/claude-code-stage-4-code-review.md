# Claude Code Stage 4 Code Review

Review complete.

**Verdict:** Approved after fixes. Stage 4 is clean to commit, but two findings
must be folded into Stage 5 before `clean-old-data` lands.

## Critical

None.

## Important

### I1. SQLite foreign-key cascade is inert by default

`item_entities.item_id` declares `ondelete="CASCADE"`, but SQLite ignores
foreign-key cascade unless `PRAGMA foreign_keys=ON` is set per connection.
Stage 5's planned `clean-old-data` command must not rely on cascade alone or it
can orphan matcher rows.

Recommended Stage 5 fix: enable SQLite foreign keys in the engine, or explicitly
delete `item_entities` rows before deleting pruned `items`. Add a regression test
proving no orphan matcher rows remain.

### I2. `first_seen_at` is derived from retained item history

Stage 4 scoring computes entity `first_seen_at` from retained item rows. Once
Stage 5 pruning deletes old items, a long-lived entity can be mislabeled `new`
because its earlier retained history disappeared.

Recommended Stage 5 fix: persist a stable entity first-seen timestamp
independent of item retention, then have scoring prefer that stable timestamp.
Add a regression test that prunes old items and proves a previously seen entity
is not re-labeled `new`.

## Minor

- `metadata.item_count` currently reports a top-N current mention total rather
  than a distinct item count.
- `_load_distinct_mentions()` loads all match history into memory; this is
  acceptable for Stage 4 but should be bounded after stable first-seen is
  persisted.
- Migrated v3 `collected_at` is nullable in SQLite even though the canonical
  table declares it non-null. This is harmless after backfill but worth noting
  if migrations are hardened later.
- `weighted_mentions_7d` is slightly misleading because the current window is
  configurable, but it matches the approved Stage 4 YAML contract.

## What Checked Out

- Stage 4 satisfies the approved plan.
- Scoring windows are based on `items.collected_at`, half-open at the current
  window start and inclusive at `as_of`.
- Mention counting uses max confidence per distinct `(entity_name, item_id)`.
- Growth-rate normalization, formula components, label order, and deterministic
  ranking are correct and tested.
- v1 -> v2 -> v3 and v2 -> v3 migrations preserve existing items.
- `source_weight` and `collected_at` upsert behavior is correct for Stage 4:
  inserts store both, updates preserve first-seen `collected_at`.
- Report serialization boundaries are strict; JSON and Markdown do not leak
  `content_hash`, normalized URL, full article text, or raw matcher rows.
- Stage 4 tests are meaningful and sufficient.

## Stage 5 Plan Review

The updated Stage 5 plan is concrete and largely safe: optional dashboard
dependency handling, read-only localhost dashboard behavior, no social scraping,
explicit `as_of`, and serialization-boundary reuse are all well specified.

The Stage 5 plan must explicitly address I1 and I2 before implementation.

## Final Verdict

**Approved after fixes**. Stage 4 may be committed as-is. Before Stage 5
implements `clean-old-data`, resolve I1 and I2 in the Stage 5 plan and add the
corresponding tasks and tests.
