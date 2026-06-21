# Stage 139 Plan Review Prompt

You are reviewing the Stage 139 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Tighten remaining first-run smoke workflow command validators from substring checks to exact argv checks.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-139-first-run-workflow-command-argv-design.md`
- `docs/superpowers/plans/2026-06-21-stage-139-first-run-workflow-command-argv-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the plan preserves runtime CLI behavior.
- Whether expected argv lists match the workflow builders.
- Whether fixture metadata additions mirror real Pydantic payloads.
- Whether the proposed RED tests would fail before implementation and pass after exact validation.

Return a concise review with findings first. If there are no blocking issues, say that explicitly.
