# Stage 143 Plan Review Prompt

You are reviewing the Stage 143 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so all six workflow step commands must match exact argv, not only the readiness step.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-143-community-handoff-command-argv-design.md`
- `docs/superpowers/plans/2026-06-21-stage-143-community-handoff-command-argv-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the expected argv parts match `build_community_handoff_workflow()`.
- Whether the RED test would fail before implementation and pass after exact argv validation.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
