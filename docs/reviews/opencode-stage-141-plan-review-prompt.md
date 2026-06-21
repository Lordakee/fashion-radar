# Stage 141 Plan Review Prompt

You are reviewing the Stage 141 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Add exact builder parity tests for imported-review and community-handoff workflow smoke fixtures, then update fixture step metadata to match runtime builder JSON.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-141-workflow-fixture-parity-design.md`
- `docs/superpowers/plans/2026-06-21-stage-141-workflow-fixture-parity-plan.md`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the parity tests use the correct builder args and JSON mode.
- Whether the fixture metadata values match builder output exactly.
- Whether runtime behavior remains unchanged.
- Whether the RED/GREEN strategy is valid.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
