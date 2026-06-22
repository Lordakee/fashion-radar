# Stage 158 Code Review Prompt

Review the Stage 158 code changes for Fashion Radar.

Files changed:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Plan and review context:

- `docs/superpowers/specs/2026-06-23-stage-158-first-run-community-handoff-check-json-design.md`
- `docs/superpowers/plans/2026-06-23-stage-158-first-run-community-handoff-check-json-plan.md`
- `docs/reviews/opencode-stage-158-plan-review.md`
- `docs/reviews/opencode-stage-158-plan-rereview.md`

Objective:

Make first-run smoke request JSON from the direct `community-handoff-check-dir`
call and validate the returned local-read-only readiness/dry-run payload.

What changed:

- Added `validate_community_handoff_check_dir(...)`.
- Updated `run_first_run_flow()` to call `community-handoff-check-dir` with
  `--format json`, parse stdout with `validate_json_output(...)`, and validate
  runtime `directory` / `config_dir`.
- Added a deterministic `community_handoff_check_dir_payload(...)` helper with
  real-model-shaped nested payloads.
- Added validator acceptance, top-level drift, and nested count drift tests.
- Updated `expected_first_run_flow_commands()` and deterministic fake stdout for
  the new `--format json` command.

Review questions:

1. Does first-run smoke now validate useful `community-handoff-check-dir` JSON
   readiness fields without overfitting to full nested schemas?
2. Does the deterministic fixture accurately mirror the real JSON model shapes
   enough for this smoke contract?
3. Does the implementation preserve local-only, read-only behavior and avoid
   write-capable directory import behavior?
4. Are the RED/GREEN tests sufficient for the new validator and first-run command
   sequence?
5. Are there any critical or important issues to fix before release-gate
   verification and commit?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
