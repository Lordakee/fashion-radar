# Stage 154 Plan Review Prompt

You are reviewing the Stage 154 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so the top-level `config_dir` and `data_dir` fields are pinned exactly, while the real smoke flow passes its runtime temp paths into the validator explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-154-imported-review-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-154-imported-review-top-level-field-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`

Please review:
- Whether the RED tests isolate the top-level field assertions after command rewrites.
- Whether the validator signature and `run_smoke(context)` call thread expected runtime paths correctly.
- Whether the deterministic smoke-flow test uses temp-path payloads for `imported-review-workflow`.
- Whether existing command-specific and metadata-specific labels remain unchanged.
- Whether direct `python scripts/check_first_run_smoke.py --repo-root .` verification is included.
- Whether runtime behavior remains unchanged.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
