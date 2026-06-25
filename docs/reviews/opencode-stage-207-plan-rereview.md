# Stage 207 Plan Rereview

## Verdict

I1 is resolved. No Critical findings. No Important findings. The plan may
proceed to Task 1 (RED tests).

The two added tests directly exercise the two untested branches called out in
I1: the contiguous sliding-window match for a multi-token proper subset, and the
`len(context_tokens) >= len(alias_tokens)` early return for an equal-length
reorder. Both tests were traced against the proposed
`_context_term_contained_in_alias(...)` helper and the existing
`_alias_findings(...)` loop in `src/fashion_radar/entity_packs.py`, and both
produce the asserted results.

## Critical

None.

## Important

None.

## I1 Resolution Check

**I1 (multi-token containment and length-guard branches untested) — RESOLVED.**

1. `test_multi_token_context_term_contained_in_gated_alias_warns` (Task 1,
   Step 3) uses context term `mary jane` against gated alias
   `Mary Jane shoes`. The proposed helper tokenizes the alias to
   `['mary', 'jane', 'shoes']` and the context to `['mary', 'jane']`; the
   `len(context_tokens) < len(alias_tokens)` guard passes and the sliding
   window matches at offset 0, so the warning fires. This is a genuine RED
   test before implementation and pins the contiguous-window branch.

2. `test_equal_length_reordered_context_term_does_not_warn_for_gated_alias`
   (Task 1, Step 4) uses context `jane mary` against gated alias
   `Mary Jane`. Both normalize to two tokens, so
   `len(context_tokens) >= len(alias_tokens)` triggers the early
   `return False` and no containment warning fires. The test also asserts
   `self_context_term` is absent, which is correct because the normalized
   alias key `mary jane` is not equal to the normalized context key
   `jane mary`. This pins the length guard and rules out reorder false
   positives.

3. The exact-equality assertion added in Task 1, Step 5
   (`contained_context_term_for_gated_alias` absent when `self_context_term`
   fires) is satisfied because the helper short-circuits on
   `alias_key == context_key`. Exact equality and proper containment cannot
   double-warn for the same context key.

4. The note that product `parent_brand` containment is deliberately
   future-scope (Out of scope, lines 52-54) addresses the prior Minor 4 and
   keeps `PRODUCT_PARENT_OR_CONTEXT` aliases off the new code path, matching
   the existing `_classify_alias_gate(...)` routing.

5. Deterministic `sorted(context_keys)` iteration in Task 2, Step 2 makes the
   emitted finding independent of set iteration order; combined with the
   `break`, exactly one finding is emitted per offending gated alias.

6. The docs wording added in Task 3, Step 1 explicitly calls the check "an
   advisory token-containment heuristic, not a full matcher simulation,"
   addressing the prior Minor 5.

## Minor

1. **Carry-over, not blocking:** the finding message still does not name the
   offending context term (prior Minor 1). Because the `break` emits only one
   finding per alias and the message is static, this is a presentation polish
   item and can be deferred.

2. **Interaction note, not blocking:** when an entity has both an exact-equal
   context term and a separate properly-contained context term for the same
   gated alias (e.g., alias `Mary Jane shoes` with context
   `[Mary Jane shoes, shoes]`), both `self_context_term` and
   `contained_context_term_for_gated_alias` will fire. This is accurate — they
   flag distinct problems — but the plan does not call out the interaction. No
   change required; consider a sentence in `docs/entity-pack-quality.md` if
   users ask why two warnings appear.

3. The RED-stage claim for
   `test_surrounding_context_term_does_not_warn_for_explicit_gated_alias`
   (Task 1, Step 2) remains a non-regression guard rather than a true RED
   test (prior Minor 3). It passes both before and after implementation, which
   is acceptable as a guard but should not be counted toward RED coverage.

## Scope And Release Hygiene Confirmation

- No matcher, schema, config-validation, source, scoring, report, dashboard,
  importer, dependency, or lockfile behavior changes are introduced; the new
  code lives entirely inside `_alias_findings(...)` and one private helper.
- The new check is gated on `AliasGateKind.CONTEXT_REQUIRED` and is placed
  before the `if not alias.safe_single_word: continue` statement, so it runs
  for every context-required alias regardless of `safe_single_word`.
- Release verification commands match the AGENTS.md prescription
  (`uv --no-config run --frozen ...`, `UV_NO_CONFIG=1 uv lock --check`,
  `UV_NO_CONFIG=1 uv sync --locked --dev --check`) and include the first-run
  smoke check and lockfile diff guard.
- Plan, code, and release OpenCode review artifacts are all scheduled with
  `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

## Answers To Rereview Questions

1. I1 is resolved: both the multi-token proper-containment branch and the
   equal-length length-guard branch now have dedicated tests that trace
   correctly to the proposed implementation.
2. No Critical or Important planning blockers remain.
