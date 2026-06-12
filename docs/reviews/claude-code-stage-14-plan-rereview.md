Approved for Stage 14 implementation

- `Critical:` None.

- `Important:`
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md` — “Developer Operations Boundary” and “Task 4: Verification, Claude Code Review, Commit, Push”: the plan includes commit/push and `git push origin main` steps. These are development/release operations, not part of the Stage 14 entity-pack architecture or acceptance criteria. Keep implementation focused on the static pack/tests/docs, and either remove push instructions or move them to a clearly separate “only with fresh explicit authorization” release checklist.
  - `docs/superpowers/specs/2026-06-12-stage-14-entity-watchlist-pack-design.md` — “Verification”; `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md` — “Task 4”: `uv sync`, alternate-index checks, wheel install smoke tests, and mirror-based install verification may require network/index access. They are reasonable release/CI checks, but broader than this static YAML/docs/test change. Label them as release verification, not required implementation verification.
  - `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md` — “Task 3: Add Entity Pack Documentation”: the workflow example uses `--source-name "Manual Export"`. This does not directly instruct users how to obtain platform/community exports, but the wording is close to the explicit out-of-scope boundary. Prefer a neutral example such as `"Local CSV"` or `"Research Notes CSV"` and state that `import-signals` only imports files the user already has permission and intent to use.

- `Minor:`
  - The proposed stage is a good next step after the community import contract: it improves local matching coverage using the existing entity configuration and matcher, without introducing source acquisition, connectors, scraping, scoring changes, or runtime behavior.
  - Keeping `configs/entities.example.yaml` and the packaged init template unchanged is the right boundary. It preserves the small first-run starter config while giving power users an optional broader pack.
  - The pack contents are useful as a seed watchlist and are framed appropriately as local observation inputs, not evidence of current hotness, market-wide demand, or platform-wide ranking.
  - Alias/context planning is mostly safe for the existing matcher: broad names like `Coach`, `Mary Jane`, `Boat Shoes`, `Margaux`, and `Arcadie` are explicitly tested for rejection in generic prose and acceptance with parent-brand or fashion context.
  - Tests cover the right concerns: loading through `load_entity_config()`, type mix, expected examples, parent-brand references, unchanged starter config, broad alias context protection, and actual matcher accept/reject behavior.
  - `docs/superpowers/specs/2026-06-12-stage-14-entity-watchlist-pack-design.md` — “Files”: the spec lists the plan-review prompt artifact but not the matching review output artifact, while the plan later includes both review prompt and review output files. Harmless, but worth making consistent.
  - Documentation should keep the `collect` command framed as running only existing configured sources. Add or preserve wording that the entity pack does not add sources, collectors, scraping, platform monitoring, or ranking semantics.
  - Verification is sufficient for GitHub upload once the operational boundary is cleaned up: focused pack tests, full tests, lint/format checks, diff whitespace check, build/smoke checks, and code review are enough for this static-pack stage.
