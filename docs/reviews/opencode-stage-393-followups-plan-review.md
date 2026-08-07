# Stage 393 Follow-up Plan Review

## Critical
None.

The plan respects every hard constraint in the verified facts:
- Strict payload byte-compatibility is preserved because decision 3 is docs/test/docs-test only and fact 2 confirms no schema/runtime/manifest changes; default stays permissive and no normal refresh snippet contains strict, so production runtime output is untouched.
- Daily acceptance is not weakened: the `--allow-unaccepted-content` flag is scoped to the single deterministic smoke refresh (decision 2), production defaults and scheduled snippets are explicitly unchanged, and acceptance still counts only current collector results (fact 3). The empty-sources rejection is offline-smoke-only and "by design" (fact 5).
- The frozenset-membership TypeError (fact 4) is resolved by routing health evaluation through a typed helper that degrades to `attention` instead of raising, which is the correct direction for a top-level ops aggregation path.

## Important
1. **Decision 1 lacks an explicit regression test, unlike decisions 2-4.** Converting a hard `TypeError` raise into an `attention` status is a real behavior change. Add a test asserting: (a) `None`/list/dict health values yield `attention` rather than raising; (b) `"ready"` and `"not_applicable"` yield healthy; (c) the `attention` propagates to the top-level ops status rather than being swallowed. Without this, the fix can silently regress.
2. **Confirm the fix is complete, not just local.** The TypeError originates in frozenset membership (fact 4). Every call site that currently tests article health via raw `value in <frozen/healthy set>` must route through the new helper; otherwise a parallel membership check can still raise. The plan should state (or the implementation must verify) that the helper is the single health-evaluation entry point.

## Minor
- **Decision 2:** the smoke should assert both that the row-one refresh succeeds under the flag and that the expected warning is emitted, and should avoid a brittle exact-string warning match (use a stable substring) so unrelated wording tweaks don't break it.
- **Decision 3:** verify the CLI reference "strict" prose, as an indented continuation of the ops-check item, renders correctly in the docs pipeline and that the strict docs tests target text boundaries rather than over-constraining ops-check content (which could block future legitimate edits).
- **Decision 4:** map each of the five AGENTS assertions (parallel default, disjoint write scope, ownership transfer before reclamation, immediate reclaim after handoff, main worktree/main branch only) to a clear failure message tied to its AGENTS.md clause, and prefer concept/keyword matching over exact-sentence matching to keep the guard maintainable.

## Verdict
**Approve with conditions.** No Critical or blocking Important issue in scope or sequencing. The four decisions are mutually independent (code health helper, smoke flag, strict docs tests, AGENTS docs test) with disjoint write sets, so they may proceed in parallel under the existing main worktree/main branch. Before implementation closes, satisfy the two Important items: add the malformed-health `attention` regression test for decision 1, and confirm the typed helper is the sole health-evaluation entry point so no residual frozenset-membership raise path remains. The Minor items are addressable during implementation without re-review.
