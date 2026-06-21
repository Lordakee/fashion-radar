# Stage 147 Code Review Prompt

You are reviewing Stage 147 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` first-run smoke validation so workflow `boundaries` must match the canonical boundary list exactly.

Review range:
- Base: `d814214e517cd2ee1714690983521f511840e470`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-147-external-workflow-boundary-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-147-external-workflow-boundary-exactness-plan.md`
- `docs/reviews/opencode-stage-147-plan-review-prompt.md`
- `docs/reviews/opencode-stage-147-plan-review.md`
- `docs/reviews/opencode-stage-147-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gap with true RED cases.
- Whether `validate_external_tool_workflow()` now checks exact boundary equality.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
