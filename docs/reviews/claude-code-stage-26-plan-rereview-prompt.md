You are rereviewing the revised Stage 26 implementation plan for this
repository.

Repository: `/home/ubuntu/fashion-radar`

Review these files only:

- `docs/superpowers/specs/2026-06-13-stage-26-imported-candidate-evidence-design.md`
- `docs/superpowers/plans/2026-06-13-stage-26-imported-candidate-evidence-plan.md`

Previous Claude Code review found two Important issues:

1. Retained-row filtering was underspecified. The plan did not explicitly prove
   old/future or otherwise non-review-window `manual_import` rows were excluded.
2. Blank `--source-name` was specified in the design but missing from
   implementation/test details.

Revisions made:

- The spec and plan now define retained-row semantics for the current schema:
  retained means the row still exists in `items`, and Stage 26 additionally
  applies the same review-window boundary as Stage 25 candidate discovery:
  `baseline_window_start < collected_at <= as_of`.
- The spec and plan now explicitly exclude older out-of-window rows and future
  rows.
- The source/window query test now inserts current, baseline, other-source,
  RSS, future, and old out-of-window rows for the same phrase and asserts only
  the expected retained/manual/source/window rows appear.
- The implementation plan now requires blank `source_name` normalization to
  `None` before applying the optional exact source-name filter.
- The spec and plan now include query and CLI coverage for blank source-name
  behavior.
- The plan now includes `limit=0` coverage preserving pre-limit counters while
  returning zero evidence rows.

Please rereview the revised plan/spec for correctness, safety, implementation
completeness, test adequacy, and alignment with existing project patterns.

Output format:

- If approved, include the exact phrase: `APPROVED FOR IMPLEMENTATION`.
- If not approved, list findings by severity: Critical, Important, Minor.
- Treat Critical and Important findings as blocking implementation.
