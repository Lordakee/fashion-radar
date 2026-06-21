# Stage 149 Plan Review Prompt

You are reviewing the Stage 149 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-template` first-run smoke validation so the two Rednote example rows must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-149-template-item-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-149-template-item-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_templates.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact item equality.
- Whether the pinned item values match the runtime builder and first-run fixture.
- Whether existing targeted errors for missing fields, private/raw fields, extra fields, and wrong platform remain intact.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
