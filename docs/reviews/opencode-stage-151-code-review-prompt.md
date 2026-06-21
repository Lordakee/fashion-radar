# Stage 151 Code Review Prompt

You are reviewing Stage 151 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Review range:
- Base: `c42f764d9f775ec3cf9ecd75beb4954e7b6f8c7b`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-151-imported-review-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-151-imported-review-step-metadata-exactness-plan.md`
- `docs/reviews/opencode-stage-151-plan-review-prompt.md`
- `docs/reviews/opencode-stage-151-plan-review.md`
- `docs/reviews/opencode-stage-151-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_imported_review_workflow()` now checks exact step metadata equality.
- Whether existing command drift tests still fail through command-specific labels.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
