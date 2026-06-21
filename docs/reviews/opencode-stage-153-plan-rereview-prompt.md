# Stage 153 Plan Rereview Prompt

You are re-reviewing the updated Stage 153 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the top-level `directory`, `config_dir`, and `data_dir` fields are pinned exactly, while the real smoke flow passes its runtime temp paths into the validator explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-153-community-handoff-top-level-field-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`
- `scripts/check_first_run_smoke.py` smoke-flow call sites

Please review:
- Whether the RED tests now isolate the new top-level field assertions after the command rewrites.
- Whether the validator signature and `run_smoke(context)` call both thread the expected runtime paths correctly.
- Whether the pinned field values still match the fixture and runtime builder for the unit tests.
- Whether existing command-specific, metadata-specific, and effect-specific labels remain unchanged.
- Whether the direct `python scripts/check_first_run_smoke.py --repo-root .` verification closes the earlier gap.
- Whether runtime behavior remains unchanged.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
