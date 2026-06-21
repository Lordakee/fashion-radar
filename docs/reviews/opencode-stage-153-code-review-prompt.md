# Stage 153 Code Review Prompt

You are reviewing Stage 153 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the top-level `directory`, `config_dir`, and `data_dir` fields are pinned exactly, while the real smoke flow passes its runtime temp paths into the validator explicitly.

Review range:
- Base: `acaee740779cca6c00de96034e3932b5e51492e6`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-153-community-handoff-top-level-field-exactness-plan.md`
- `docs/reviews/opencode-stage-153-plan-review-prompt.md`
- `docs/reviews/opencode-stage-153-plan-review.md`
- `docs/reviews/opencode-stage-153-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-153-plan-rereview.md`
- `docs/reviews/opencode-stage-153-plan-rereview-2-prompt.md`
- `docs/reviews/opencode-stage-153-plan-rereview-2.md`
- `docs/reviews/opencode-stage-153-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior top-level path drift gap with true RED cases.
- Whether `validate_community_handoff_workflow()` now checks exact `directory`, `config_dir`, and `data_dir` equality using caller-supplied expected values.
- Whether `run_first_run_flow(context)` passes the real temp paths to the validator.
- Whether `test_run_first_run_flow_uses_deterministic_local_command_sequence()` now returns a temp-path community handoff payload.
- Whether existing command-specific, metadata-specific, and effect-specific labels remain unchanged.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient, including direct `scripts/check_first_run_smoke.py --repo-root .`.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
