# Stage 206 Plan Rereview

## Verdict

**No Critical findings. No Important findings.** All four prior findings (I1, M1, M2, M3) are resolved. The plan is approvable for implementation.

## Critical

None.

## Important

None.

## Prior Findings - Verification

1. **I1 (matcher/linter agreement for `requires_context` + `safe_single_word`) - RESOLVED.**
   `_classify_alias_gate(...)` now tests `alias.requires_context` first and returns `CONTEXT_REQUIRED` before the `safe_single_word` branch. This mirrors the matcher's explicit-gate ordering in `_evaluate_alias(...)`. It is pinned by `test_explicit_context_alias_takes_precedence_over_safe_alias_lint`, which asserts `context_gated_aliases == 1` and `safe_aliases == 0` for the combined-flag alias.

2. **M1 (unreachable `requires_context or` in matcher helper) - RESOLVED.**
   The matcher `_requires_context(...)` keeps only `len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES`. The `requires_context` check lives only in the explicit matcher branch and defensively in the linter helper, as M1 prescribed.

3. **M2 (self-satisfaction tests) - RESOLVED.**
   `test_fashion_watchlist_context_gates_broad_category_aliases` includes `Mary Jane shoes were noted.`, `Mary Janes joined the dinner list.`, `Mary Jane flats were noted.`, plus the boat-shoes / east-west-bag / suede-sneakers generic mentions, all asserting `{"missing_context"}`. The tuned `context_terms` (`footwear/runway/styling`, `handbag/runway/styling`, etc.) are not substrings of any alias text, so the gate is genuinely unsatisfied by the alias itself and no `self_context_term` warning is produced.

4. **M3 (sample-workflow `summary`-only fallback) - RESOLVED.**
   Task 3 Step 3 now states the fallback edits only the `summary` column of `examples/community-signals.watchlist.example.csv`, keeping URLs as `example.com`.

## Cross-checks performed

- RED mechanics: `AliasDefinition(extra="forbid")` rejects the unknown `requires_context` key pre-implementation, so the Task 1/Task 3 RED tests fail for the stated reason. The `_entity(...)` helper accepts the alias-dict + `context_terms` + `match_confidence` args used.
- Backward compatibility: ordinary multi-word aliases without `requires_context` still hit the `not _requires_context(alias)` accept branch unchanged; `test_multi_word_brand_alias_is_accepted_without_context` and the Ballet Flats/UNSAFE-common path are unaffected.
- Watchlist regression: existing positive tests `..._accepts_parent_brand_or_fashion_context` and `..._sample_matches_expected_entities_and_types` still pass because their text/CSV summaries already contain the new context terms (`runway footwear`, `handbag styling`), so Mary Jane Shoes and East-West Bags remain accepted. CSV fallback is therefore likely a no-op, and the hedged wording is safe.
- Docs parity: `test_entity_pack_quality_docs.py` dynamically compares docs samples to live lint output, so regenerating the fenced JSON/table samples keeps it green. The pack still emits warnings, so the docs "one representative `warning`" sample shape and `["warning"]` severity assertion remain valid.
- `test_entity_pack_lint.py::test_lint_repository_watchlist_pack_has_no_errors` only asserts `error_count == 0` and `product_parent_gated_aliases > 0`, neither of which the change affects.

## Minor (non-blocking, optional)

1. **Linter helper redundancy.** `_alias_requires_context(...)` retains `alias.requires_context or`, but after `_classify_alias_gate(...)` early-returns on `alias.requires_context`, that clause is unreachable from its only caller. It is harmless defensive code and exactly what prior M1 requested; leaving it is fine. Dropping it later would be a pure cleanup.
2. **Validation scope.** The new check `if alias.requires_context and not entity.context_terms` applies to all entity types. For the out-of-scope parent-brand-`PRODUCT` case the matcher ignores `requires_context`, so the check is mildly conservative there. No current or planned config is affected because the field is only applied to `category` aliases.
3. **Rereview artifact naming.** Per `docs/REVIEW_PROTOCOL.md`, record this rereview as `docs/reviews/opencode-stage-206-plan-rereview.md` and keep the original `opencode-stage-206-plan-review.md` intact to preserve the I1/M1/M2/M3 audit trail.

**Recommendation:** proceed to Task 1 (RED tests).
