APPROVED FOR IMPLEMENTATION

I rereviewed only:

- `docs/superpowers/specs/2026-06-13-stage-26-imported-candidate-evidence-design.md`
- `docs/superpowers/plans/2026-06-13-stage-26-imported-candidate-evidence-plan.md`

No Critical or Important blocking findings.

Minor observations / optional improvements:

- Consider adding one extra non-default window test to prove `current_days`, `baseline_days`, `current_window_start`, `baseline_window_start`, and filtering are derived from `CandidateDiscoverySettings` rather than hardcoded `7` / `30` defaults. The plan already states Stage 26 should reuse Stage 25 review-window semantics, so this is not blocking, but an explicit regression test would make that guarantee stronger.
- The revised source/window test now covers current, baseline, other-source, RSS, future, and old out-of-window rows, and the blank `source_name` behavior is covered at query and CLI levels. This resolves the two previous Important findings.
- `limit=0` pre-limit counter preservation is now explicitly covered and aligned with the output model semantics.

The revised spec and plan are correct, read-only/safety-conscious, implementation-complete, and aligned with the stated Stage 25 candidate-discovery semantics.
