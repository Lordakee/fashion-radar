Approved for Stage 15 implementation

- `Critical:` None.

- `Important:` None.

- `Minor:`
  - The revised spec and plan resolve the prior matcher-semantics issues. The design now states that `context_terms` are not universal gates, safe non-product aliases bypass context, and product entities with `parent_brand` ignore `safe_single_word`.
  - The implementation plan now includes explicit alias-gate pseudocode and interpretation for product parent/context gating, safe aliases, context-required aliases, and ordinary multi-word aliases.
  - The revised plan adds explicit matcher-contract edge tests for the previously under-specified cases.
  - The repository watchlist smoke test now clearly permits advisory warnings.
  - `product_missing_parent_brand` is now framed as a precision recommendation for named branded products, not a validity failure.
  - The raw-YAML-to-validated-entity index correlation guidance for omitted default diagnostics is now explicit.
  - The documentation boundary checks have been broadened to cover terms such as social monitoring, platform search, exports, demand proof, rankings, current hotness, market-wide, platform-wide, and source acquisition.

I found no remaining Critical or Important blockers. The revised plan appears safe to implement and does not add or document the prohibited social/platform acquisition, scraping, API, bypass, real-time trend, DB/collector/dashboard/report/matcher/scoring-change, or product-facing compliance/audit/legal-review scopes.
