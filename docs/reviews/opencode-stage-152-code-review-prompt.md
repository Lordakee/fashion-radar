# Stage 152 Code Review Prompt

You are reviewing Stage 152 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Review range:
- Base: `3472b34814b408a38b6b305fa49af9c4c38ff673`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-152-community-handoff-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-152-community-handoff-step-metadata-exactness-plan.md`
- `docs/reviews/opencode-stage-152-plan-review-prompt.md`
- `docs/reviews/opencode-stage-152-plan-review.md`
- `docs/reviews/opencode-stage-152-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_community_handoff_workflow()` now checks exact step metadata equality.
- Whether existing import/post-import effect tests still fail through their current more specific labels.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
