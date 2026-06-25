# Stage 207 Plan Review Prompt

Review the Stage 207 implementation plan in
`docs/superpowers/plans/2026-06-26-stage-207-context-term-containment-lint-plan.md`.

Goal: add an advisory entity-pack lint warning for context terms that are
contained in a gated alias, so local pack edits such as alias `Mary Jane shoes`
with `requires_context: true` and `context_terms: [shoes]` become visible as a
precision risk.

Context:

- Stage 206 added `AliasDefinition.requires_context` and explicit context gates
  for non-product aliases.
- Stage 206 intentionally left matcher behavior unchanged for products with
  `parent_brand`, which keep parent-brand-or-context behavior.
- Stage 206 docs tell users to choose context terms that require surrounding
  fashion language instead of terms satisfied by the alias text itself.
- The current linter only catches exact alias/context equality via
  `self_context_term`; it does not catch proper token containment such as
  context term `shoes` inside alias `Mary Jane shoes`.
- This stage should be linter-only and should not change matcher behavior,
  entity schema, configs, source acquisition, scoring, reports, dashboard,
  social/platform connectors, scraping, demand proof, platform coverage
  verification, dependency files, or compliance-review behavior.

Please review:

1. Is the proposed `contained_context_term_for_gated_alias` warning useful and
   scoped correctly?
2. Is proper token containment safer than arbitrary substring matching?
3. Should exact equality remain covered only by `self_context_term`?
4. Are the planned tests enough to prove warning, non-warning, and exact
   equality behavior?
5. Is the plan clear about avoiding matcher/schema/config/source/dependency
   changes?
6. Are docs/changelog/review/release gates sufficient?
7. Are there any likely false positives or stale docs sample risks?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
