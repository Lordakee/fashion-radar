Approved for Stage 10 implementation

- `Critical:` None.

- `Important:` None.

- `Minor:` `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`, Task 1 still describes running the original plan review command and saving to `docs/reviews/claude-code-stage-10-plan-review.md`, while lines 113-116 allow follow-up rereview files to satisfy the gate. Consider adding one sentence that this rereview output satisfies the plan gate once saved as the rereview artifact.

- `Minor:` The prompt’s tech stack mentions Rich tables, but the updated plan intentionally specifies plain Typer echo table-style output to match existing CLI testing patterns. This is acceptable if consistency/testability is preferred, but align wording before implementation if Rich output is a hard requirement.

The updated plan resolves the prior review findings:

1. Invalid config/config-path regressions are tested before DB opening.
2. CLI and dashboard reject incompatible existing databases read-only.
3. Dashboard trend query verifies schema before reading and avoids initialization/migrations.
4. Stage 10 forbids migrations, persistent trend tables, writable indexes, and DB writes.
5. Dashboard config loading and `--config-dir` plumbing are specified.
6. Mixed-direction movement is deterministic and conservatively labeled `stable`.
7. Integration/spy tests prove `build_trend_comparison()` composes `score_entities()` and `discover_candidates()`.
8. CLI option plumbing covers `--include-dropped`, `--limit`, default baseline, and missing-DB JSON output.
9. Runtime no-external-services scope is clear.
10. Dashboard visible copy and docs are required to avoid market-wide or platform-wide claims.
 has no items.
  - Entity and candidate keys are required to use `normalize_alias_key()`.
  - Dashboard incompatible database handling, global summary failure isolation, and concise trend schema errors are now covered.
  - Dashboard invalid/missing config paths are covered with no `data_dir` or SQLite creation.
  - Runtime scope remains local-only and read-only for trends, with no platform collection, no migrations, no persistent trend tables, and no DB writes.
