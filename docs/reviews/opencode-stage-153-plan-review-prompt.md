# Stage 153 Plan Review Prompt

You are reviewing the Stage 153 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the top-level `directory`, `config_dir`, and `data_dir` fields are pinned exactly instead of being reused to synthesize expected command argv.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-153-community-handoff-top-level-field-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact field assertions are added.
- Whether the pinned field values match the runtime builder and first-run fixture.
- Whether existing command-specific and effect-specific labels remain unchanged.
- Whether the new field assertions are placed before command synthesis.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
