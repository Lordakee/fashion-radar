Not approved

- Critical: `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md`, Task 1 proposed test `test_fashion_watchlist_matcher_rejects_generic_broad_alias_mentions` conflicts with the existing matcher while the architecture forbids runtime changes. The existing matcher context-gates products with `parent_brand`, single-word aliases, and aliases in `UNSAFE_COMMON_ALIASES`; it does not context-gate arbitrary multi-word category aliases just because the entity has `context_terms`. As written, the negative cases for `("Mary Jane arrived at dinner before the show.", "Mary Jane Shoes")` and `("The boat shoes stayed near the dock.", "Boat Shoes")` would be accepted unless those phrases are added to runtime unsafe aliases or matcher logic changes, both out of scope. Fix by removing those two negative matcher assertions, and preferably remove the bare `Mary Jane` alias from the YAML example; keep narrower aliases such as `Mary Jane shoes`, `Mary Janes`, and `Mary Jane flats`.

- Important: `docs/superpowers/specs/2026-06-12-stage-14-entity-watchlist-pack-design.md` lines 90-98 and plan language around “context protection” overstate what `context_terms` do for non-product multi-word aliases. Update the design/plan/docs to distinguish validator-level guardrails from matcher-level gates: existing matcher gates products, single-word aliases, and aliases listed in `UNSAFE_COMMON_ALIASES`; other multi-word category/trend aliases should be kept narrow because Stage 14 does not change matcher semantics.

- Important: `docs/superpowers/plans/2026-06-12-stage-14-entity-watchlist-pack-plan.md` Task 3 should explicitly avoid telling users that `context_terms` are a universal phrase-level disambiguation system. Add docs wording such as: “Existing matching uses context gates for product aliases with `parent_brand`, single-word aliases, and aliases listed as unsafe/common by the application. For other multi-word category or trend aliases, use narrower aliases where possible.”

- Minor: The optional watchlist pack is otherwise the right next stage after the community import contract. It extends local entity matching coverage using the existing `EntityConfig` schema and avoids collectors, source acquisition, runtime code, DB/report/scoring/dashboard changes, and platform/community ingestion.

- Minor: Keeping `configs/entities.example.yaml` and the packaged init template unchanged is the right boundary. The proposed default-config stability test is useful and should remain.

- Minor: The proposed pack contents are useful if framed as a static seed watchlist only. The design and plan correctly avoid current-hotness, market-wide demand, platform-wide, and ranking claims; preserve that wording.

- Minor: Tests are mostly well targeted: pack loading through `load_entity_config()`, type mix, expected examples, parent-brand references, alias uniqueness through the validator, default starter stability, and product/unsafe alias matcher behavior. After fixing the multi-word category mismatch, the test strategy is sufficient.

- Minor: Documentation scope is generally safe: it describes copy/edit/doctor/existing workflow commands without adding platform/social acquisition, scraping, APIs, Google News RSS, or ranking semantics. Keep the wording guard, but continue allowing explicit negative boundary phrases like “not a hot-list” and “not a ranking”.

- Minor: Verification is sufficient for GitHub upload from a static YAML/docs/tests stage: focused tests, full pytest, ruff, format check, diff check, CodeGraph status, and Claude Code review. Optionally clarify that GitHub CI/release handoff can run build and installed-wheel smoke separately, since those are not Stage 14 acceptance requirements.

After the Critical matcher/context mismatch is fixed, the plan should be approvable.
