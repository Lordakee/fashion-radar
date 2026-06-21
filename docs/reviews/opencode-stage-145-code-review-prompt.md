# Stage 145 Code Review Prompt

You are reviewing Stage 145 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the actual `steps` list must contain exactly the six expected JSON object steps, with no ignored extra tail entries.

Review range:
- Base: `d98d81245929cf871049341ce79a04779929183c`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-21-stage-145-community-handoff-step-shape-design.md`
- `docs/superpowers/plans/2026-06-21-stage-145-community-handoff-step-shape-plan.md`
- `docs/reviews/opencode-stage-145-plan-review-prompt.md`
- `docs/reviews/opencode-stage-145-plan-review.md`
- `docs/reviews/opencode-stage-145-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new test proves the prior gap with a true RED case.
- Whether `validate_community_handoff_workflow()` validates actual step list length and non-object entries before names and commands.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
