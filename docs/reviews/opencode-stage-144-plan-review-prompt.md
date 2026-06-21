# Stage 144 Plan Review Prompt

You are reviewing the Stage 144 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so all seven workflow step commands must match exact argv.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-144-imported-review-command-argv-design.md`
- `docs/superpowers/plans/2026-06-21-stage-144-imported-review-command-argv-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`

Please review:
- Whether the expected argv parts match `build_imported_review_workflow()`.
- Whether the RED test would fail before implementation and pass after exact argv validation.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
