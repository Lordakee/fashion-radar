# Stage 152 Plan Review Prompt

You are reviewing the Stage 152 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-152-community-handoff-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-152-community-handoff-step-metadata-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact step metadata equality.
- Whether the pinned metadata matches the runtime builder and first-run fixture.
- Whether existing import/post-import effect tests keep their current more specific failure labels.
- Whether the metadata equality check placement preserves current failure ordering.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
