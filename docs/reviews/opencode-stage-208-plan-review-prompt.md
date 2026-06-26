# Stage 208 Plan Review Prompt

Review the Stage 208 implementation plan in
`docs/superpowers/plans/2026-06-26-stage-208-context-term-warning-detail-plan.md`.

Goal: make the existing advisory `contained_context_term_for_gated_alias`
entity-pack lint warning name the specific offending context term in its
message, without changing matcher behavior or lint result schemas.

Context:

- Stage 206 added explicit alias-level context gates for deterministic
  matching.
- Stage 207 added the advisory `contained_context_term_for_gated_alias` warning
  when a context term is a proper normalized token subset of a gated alias.
- Stage 207 intentionally kept exact alias/context equality on the existing
  `self_context_term` warning and emits at most one containment warning per
  offending alias.
- The Stage 207 message is generic, so pack authors with several
  `context_terms` must manually compare all terms against the alias.
- This stage should only improve the message by naming the selected context
  term. It must not add JSON fields or change `EntityPackFinding`.

Please review:

1. Is this stage useful and scoped correctly as linter-message explainability?
2. Does preserving `EntityPackFinding` and only changing `message` avoid an API
   contract change?
3. Is deterministic selection by sorted normalized context key appropriate and
   consistent with Stage 207?
4. Is preserving the first configured display term for each normalized context
   key reasonable for human-readable messages?
5. Are the planned tests enough to prove single-token, multi-token, and
   multi-contained-term deterministic message behavior?
6. Does the plan avoid matcher/schema/config/source/dependency/social/scraping
   changes?
7. Are docs/changelog/review/release gates sufficient?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
