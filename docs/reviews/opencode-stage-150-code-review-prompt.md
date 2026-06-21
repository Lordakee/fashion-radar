# Stage 150 Code Review Prompt

You are reviewing Stage 150 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` and `external-tool-readiness` first-run smoke validation so top-level `display_name` must match the pinned first-run contract exactly.

Review range:
- Base: `e4a59d0f8da372e5f2b4d8a22275d1ea7c48f50a`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-150-display-name-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-150-display-name-exactness-plan.md`
- `docs/reviews/opencode-stage-150-plan-review-prompt.md`
- `docs/reviews/opencode-stage-150-plan-review.md`
- `docs/reviews/opencode-stage-150-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new test proves the prior gap with true RED cases for both validators.
- Whether both validators now check exact display-name equality.
- Whether existing targeted metadata error messages remain intact.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
