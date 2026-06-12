Not approved

- `Critical:` None.

- `Important:` `docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md:144-147` should be tightened to fully match current matcher semantics. It currently says `context_terms` affect “single-word aliases” and aliases in `UNSAFE_COMMON_ALIASES`, but for non-product aliases `safe_single_word` with a reason is accepted before context is consulted. The design should say that context terms affect single-word/common non-product aliases only when they are not effective safe aliases, and that `safe_single_word` is ignored by the product-with-`parent_brand` branch.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md:392-398` leaves the core matcher classification helper under-specified. Before implementation, add explicit rules/pseudocode for classifying each alias into:
  - product with `parent_brand`: parent/context gated, `safe_single_word` ignored;
  - non-product safe single/common alias with reason: accepted via safe alias, not context-gated;
  - non-product single-word or `UNSAFE_COMMON_ALIASES`: context-gated unless safe;
  - ordinary multi-word alias: accepted without context even if `context_terms` exist.

  This is important because several findings and counts depend on this exact branch order: `context_terms_no_effect`, `ungated_alias_with_context_terms`, `safe_alias_bypasses_context`, `safe_alias_ignored_for_parent_product`, `context_gated_aliases`, `accepted_without_context_aliases`, and `product_parent_gated_aliases`.

- `Important:` `docs/superpowers/specs/2026-06-12-stage-15-entity-pack-quality-design.md:7-9` mentions “future externally supplied community-signal imports.” Given the explicit out-of-scope boundary against community/platform acquisition, ingestion, and current-hotness claims, remove or rephrase this to something narrower like “existing local matching, reporting, candidate, and trend-delta workflows.” The linter should be framed only as local YAML diagnostics, not preparation for community-signal acquisition or ingestion.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md:441-461` asks for tests covering many codes but does not require tests for the exact matcher-contract edge cases called out in the review prompt. Add explicit tests proving:
  - ordinary multi-word aliases with `context_terms` are accepted without context and produce `ungated_alias_with_context_terms`;
  - `context_terms_no_effect` is emitted only when no alias actually consults context under current matcher rules;
  - safe non-product single/common aliases bypass context;
  - product aliases with `parent_brand` ignore `safe_single_word`;
  - product aliases with `parent_brand` use parent-brand aliases and product `context_terms`.

- `Minor:` The proposed `product_missing_parent_brand` warning is useful, but the docs and message should avoid implying that all product entities are invalid or unsafe without `parent_brand`. Products without `parent_brand` follow ordinary alias semantics; the warning should be framed as a precision recommendation for named products, not a correctness problem.

- `Minor:` The repository watchlist smoke test in `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md:83-92` checks only `error_count == 0`, which is appropriate if the public pack may intentionally produce advisory warnings. If the intent is a clean public example pack, add `warning_count == 0`; otherwise explicitly say the smoke test permits warnings.

- `Minor:` Add a verification item to inspect the final generated docs for prohibited language beyond the current `rg` terms. The current check at `docs/superpowers/plans/2026-06-12-stage-15-entity-pack-quality-plan.md:743-750` searches only a few terms and could miss “social monitoring,” “platform search,” “exports,” “demand proof,” or “ranking” language.

- `Minor:` In the plan’s module implementation section, specify how raw YAML entities are correlated with validated entities for omitted-default diagnostics. Index-based correlation is probably sufficient after successful validation, but it should be stated so duplicate/invalid configs still return only `invalid_config` and valid configs get deterministic `implicit_initial_weight` / `implicit_match_confidence` findings.
