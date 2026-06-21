# Stage 149 Code Review Prompt

You are reviewing Stage 149 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-template` first-run smoke validation so the two Rednote example rows must match the pinned first-run contract exactly.

Review range:
- Base: `46f646bdf1499bb50395e7b88c928ff88aa6d470`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-149-template-item-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-149-template-item-exactness-plan.md`
- `docs/reviews/opencode-stage-149-plan-review-prompt.md`
- `docs/reviews/opencode-stage-149-plan-review.md`
- `docs/reviews/opencode-stage-149-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_external_tool_template()` now checks exact item equality after existing structural checks.
- Whether existing targeted structural error messages remain intact.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
