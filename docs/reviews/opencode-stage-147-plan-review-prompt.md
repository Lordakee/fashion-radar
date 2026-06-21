# Stage 147 Plan Review Prompt

You are reviewing the Stage 147 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` first-run smoke validation so workflow `boundaries` must match the canonical boundary list exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-147-external-workflow-boundary-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-147-external-workflow-boundary-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact boundary equality.
- Whether the expected boundary list matches the runtime builder and first-run fixture.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
