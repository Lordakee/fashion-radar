# Stage 146 Plan Review Prompt

You are reviewing the Stage 146 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden first-run workflow smoke validators so coordinated drift between top-level semantic metadata and step command strings is rejected.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-146-workflow-metadata-pinning-design.md`
- `docs/superpowers/plans/2026-06-22-stage-146-workflow-metadata-pinning-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the two RED tests would fail before implementation and pass after metadata pinning.
- Whether the implementation should keep path fields (`directory`, `config_dir`, `data_dir`) payload-derived.
- Whether the proposed pinned constants match the first-run smoke fixtures and runtime default workflows.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
