# Stage 206 Plan Review Prompt

Review the Stage 206 implementation plan in
`docs/superpowers/plans/2026-06-25-stage-206-explicit-alias-context-gates-plan.md`.

Goal: add a backward-compatible alias-level `requires_context` gate to
deterministic matching, then apply it to high-risk optional watchlist category
aliases so broad phrases such as `boat shoes`, `Mary Jane shoes`, `east-west
bag`, and `suede sneakers` can require surrounding fashion context.

Context:

- Current matcher behavior only context-gates products with `parent_brand`,
  single-word aliases, and aliases listed in `UNSAFE_COMMON_ALIASES`.
- Current optional watchlist category entities define `context_terms`, but
  ordinary multi-word aliases can still match without context.
- `entity-pack-lint` currently reports this as `context_terms_no_effect` and
  `ungated_alias_with_context_terms`.
- Runtime evidence from the current tree shows generic matches such as
  `Boat shoes were required on the dock.` -> `Boat Shoes` and
  `Suede sneakers appeared in a court filing.` -> `Suede Sneakers`.
- This stage must not add social/platform connectors, scraping, source
  acquisition, source packs, dependency changes, scoring/report/dashboard
  changes, demand proof, platform coverage verification, hot-list/ranking
  behavior, or compliance-review product features.

Please review:

1. Is adding `requires_context: bool = False` to `AliasDefinition` the right
   minimal, backward-compatible model change?
2. Should explicit alias context gates run before `safe_single_word` can bypass
   context for non-product aliases?
3. Is the config validation for `requires_context` aliases without
   `context_terms` sufficient?
4. Is classifying explicit gates as `context_gated_aliases` in the linter
   correct, without adding a new finding code?
5. Are the proposed watchlist changes limited to appropriate high-risk
   category aliases, and is leaving `Sandy Liang` out of this stage reasonable?
6. Do the tests prove RED/GREEN behavior for matcher, config validation,
   linter classification, optional watchlist false positives, and sample
   workflow compatibility?
7. Are docs/changelog/review artifacts and verification gates sufficient?
8. Does the plan avoid source acquisition, connectors, scraping, ranking,
   demand proof, platform coverage verification, dependency changes, and
   compliance-review behavior?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
