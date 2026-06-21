# Stage 156 Code Review Prompt

You are reviewing the Stage 156 implementation for `/home/ubuntu/fashion-radar`.

Goal: Harden first-run smoke validation for `external-tool-workflow` and
`external-tool-readiness` so top-level `directory`, `config_dir`, and `data_dir`
are pinned against caller-supplied expected values, while the real first-run
smoke flow passes its runtime temp paths explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-156-external-tool-path-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-156-external-tool-path-exactness-plan.md`
- `docs/reviews/opencode-stage-156-plan-review.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_workflow.py`
- `src/fashion_radar/external_tool_readiness.py`

Review only the intended Stage 156 changes.

Please review:
- Whether the new RED tests prove coordinated top-level path drift is rejected
  for both external-tool workflow surfaces and all three path fields.
- Whether explicit runtime-path acceptance is covered.
- Whether `validate_external_tool_workflow()` and
  `validate_external_tool_readiness()` assert top-level paths against expected
  kwargs and synthesize nested command argv from those expected values.
- Whether old non-empty-only path loops and payload-derived path bindings were
  removed.
- Whether `run_first_run_flow(context)` passes runtime context paths into both
  validators.
- Whether the deterministic first-run flow fake stdout now uses context-path
  external-tool workflow/readiness payloads without changing static builder
  parity fixtures.
- Whether runtime builders remain unchanged.

Return findings first with severity and file/line references. If there are no
blocking issues, say that explicitly.
