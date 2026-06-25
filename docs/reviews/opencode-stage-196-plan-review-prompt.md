# Stage 196 Plan Review Prompt

Review the Stage 196 plan:

`docs/superpowers/plans/2026-06-25-stage-196-latin-fold-parity-and-starter-doc-guards-plan.md`

Context:

- Stage 195 added common Latin diacritic folding for deterministic text and runtime alias matching.
- Code review noted future-awareness around non-decomposing Latin letters such as `ø`.
- Stage 195 also broadened the default starter source config and updated README wording.

Review questions:

1. Does the plan correctly improve normalization/runtime alias parity for non-decomposing Latin letters without adding dependencies?
2. Is the explicit `_ASCII_FOLD_OVERRIDES` fallback map technically sound and safe for the codebase, without deriving future normalization behavior from `_DIACRITIC_CLASS_BY_ASCII`?
3. Is the README/starter docs guard useful and offline?
4. Does the plan avoid source connectors, social scraping, browser automation, platform APIs, source ranking, demand proof, platform coverage claims, and compliance-review product features?
5. Are there critical or important issues to fix before implementation?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Concrete fixes required before implementation
