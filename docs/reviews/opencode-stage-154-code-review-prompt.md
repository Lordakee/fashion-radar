# Stage 154 Code Review Prompt

You are reviewing the Stage 154 implementation for `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so the
top-level `config_dir` and `data_dir` fields are pinned exactly, while the real
smoke flow passes its runtime temp paths into the validator explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-154-imported-review-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-154-imported-review-top-level-field-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`

Review only the intended Stage 154 changes. Ignore `uv.lock` if it only contains
local mirror URL churn.

Please review:
- Whether the new RED tests isolate top-level `config_dir` and `data_dir` drift
  after command fragments are rewritten consistently.
- Whether `validate_imported_review_workflow()` compares the top-level fields
  against caller-supplied expected values instead of payload-derived values.
- Whether `run_first_run_flow(context)` passes the real smoke context paths into
  the validator.
- Whether the deterministic smoke-flow test emits `imported-review-workflow`
  JSON from `build_imported_review_workflow(...).model_dump_json()` using the
  test context paths.
- Whether existing command-specific and metadata-specific labels remain
  unchanged.
- Whether runtime CLI behavior remains unchanged.

Return findings first with severity and file/line references. If there are no
blocking issues, say that explicitly.
