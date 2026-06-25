# Stage 207 Plan Review

## Verdict

Plan is acceptable after resolving I1. No Critical findings. One Important
testing gap should be fixed in the plan before Stage 207 implementation.

## Critical

None.

## Important

**I1. Multi-token containment and length-guard branches are untested.**

The planned tests prove three cases: single-token warning (`shoes` inside
`Mary Jane shoes`), non-warning surrounding terms, and exact equality staying
on `self_context_term`. The most non-trivial logic in
`_context_term_contained_in_alias(...)` is the sliding window over a contiguous
token sequence and the `len(context_tokens) >= len(alias_tokens)` early return.
Add:

- A multi-token proper-subset case, such as context term `mary jane` inside
  alias `Mary Jane shoes`, to prove the contiguous-window match fires.
- An equal-length reorder negative case, such as context `jane mary` versus
  alias `Mary Jane`, to pin that the `>=` guard returns false and no warning
  fires.

## Minor

1. The advisory message does not name the offending context term. Consider
   including the matched context term in the message if deterministic wording is
   practical.
2. The exact-equality test should assert
   `contained_context_term_for_gated_alias` is absent, so exact equality and
   containment do not double-warn.
3. The surrounding-context test is valuable as a non-regression guard, but it is
   not a true RED test because it passes before implementation.
4. Excluding `PRODUCT_PARENT_OR_CONTEXT` is defensible, but the plan should
   note that parent-brand products are a deliberate future-scope item.
5. Token containment is an advisory heuristic rather than a full matcher
   simulation; docs should make that clear.
6. Docs sample stability was verified: current Stage 206 watchlist aliases and
   context terms should not trip the proposed new warning, so live docs samples
   should remain unchanged.

## Answers To Review Questions

1. The warning is useful and correctly scoped. The matcher searches context
   terms across full text, including the alias span, so self-satisfaction is a
   real precision risk.
2. Proper token containment is safer than arbitrary substring matching because
   it avoids cases like `shoe` matching `shoes`.
3. Exact equality should remain covered only by `self_context_term`.
4. Tests are almost sufficient, pending I1.
5. The plan clearly avoids matcher, schema, config, source, and dependency
   changes.
6. Docs, changelog, review, and release gates are sufficient.
7. No stale-docs risk is expected for the checked-in watchlist because the
   current Stage 206 context terms are not contained in the gated aliases.
