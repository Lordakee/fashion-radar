Approved for Stage 14 implementation

- `Critical:` None.

- `Important:` None.

- `Minor:`
  - In `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 3 docs should be especially careful to phrase the `match`, `report`, `candidates`, and `trends` commands as operating only after signals already exist. The plan already says this, but the implementation should keep that wording adjacent to the commands so readers do not infer that the pack acquires sources or performs monitoring.
  - Consider adding a small docs/test guard that the entity-pack guide does not mention `collect` except in negative boundary language. The proposed `rg` guard covers this manually; an automated text assertion would make the boundary harder to regress.
  - Consider adding accented brand/product aliases where useful, especially `Alaïa` / `Alaïa Le Teckel`, while keeping the current ASCII aliases. This would improve practical matching coverage without changing runtime behavior.
  - Consider adding product-form aliases such as `Arcadie bag`, `Le Teckel bag`, or `Puzzle bag` only if they remain unique and appropriately context-guarded. The proposed pack is conservative and safe as-is; this is only a coverage improvement.
  - In the code-review prompt created during implementation, repeat that review files under `docs/reviews/` are process artifacts, not product-facing compliance/audit/safety workflow features. The plan already says this; implementation should preserve that distinction.

Overall review against the requested questions:

1. An optional entity watchlist pack is a good next stage after the community import contract because it expands local matching coverage without adding acquisition, ingestion, or runtime behavior.
2. Keeping the default starter config unchanged is the right boundary. It preserves smoke-test simplicity and avoids surprising existing users.
3. The proposed pack contents are useful as a seed watchlist and are framed appropriately as local tracking configuration, not current-hotness, market-wide demand, or platform-wide trend proof.
4. Alias/context/parent-brand handling is planned safely for the existing matcher. The plan correctly recognizes that `context_terms` are not universal disambiguation for every phrase and uses `parent_brand` for named products.
5. The proposed tests cover loading, type mix, expected examples, parent-brand references, single/common alias guardrails, generic rejection, contextual acceptance, and unchanged default config.
6. The docs plan avoids platform/source acquisition instructions and ranking claims, provided the implementation keeps workflow commands clearly scoped to already-produced local/configured-source signals.
7. Verification is sufficient for GitHub upload: focused tests, full pytest, ruff check/format check, `git diff --check`, CodeGraph status, and a max-effort Claude Code review are appropriate for a static YAML/docs/tests stage.
