# Stage 150 Plan Review Prompt

You are reviewing the Stage 150 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` and `external-tool-readiness` first-run smoke validation so top-level `display_name` must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-150-display-name-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-150-display-name-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_workflow.py`
- `src/fashion_radar/external_tool_readiness.py`

Please review:
- Whether the RED test would fail before implementation and pass after exact display-name equality.
- Whether the pinned display name matches the runtime builders and first-run fixtures.
- Whether existing targeted metadata errors remain intact.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
