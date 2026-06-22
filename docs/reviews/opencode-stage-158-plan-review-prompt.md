# Stage 158 Plan Review Prompt

Review the Stage 158 design and implementation plan for Fashion Radar.

Files to review:

- `docs/superpowers/specs/2026-06-23-stage-158-first-run-community-handoff-check-json-design.md`
- `docs/superpowers/plans/2026-06-23-stage-158-first-run-community-handoff-check-json-plan.md`
- Existing implementation context:
  - `scripts/check_first_run_smoke.py`
  - `tests/test_first_run_smoke.py`
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/community_handoff_check.py`

Objective:

Make first-run smoke request JSON from the direct `community-handoff-check-dir`
call and validate the returned local-read-only readiness/dry-run payload.

Proposed implementation:

- Add a focused `validate_community_handoff_check_dir(...)` smoke validator.
- Update `run_first_run_flow()` to call `community-handoff-check-dir` with
  `--format json`, parse stdout with `validate_json_output(...)`, and run the
  new validator.
- Add deterministic payload helper and validator tests.
- Update `expected_first_run_flow_commands()` and fake stdout so the deterministic
  first-run test covers `--format json`.
- Keep runtime CLI behavior unchanged.

Review questions:

1. Is this the right next narrow stage after Stage 157?
2. Does the validator assert useful first-run guarantees without overfitting to
   the full nested CLI schema?
3. Is the test strategy sufficient to fail before implementation and pass after?
4. Does the plan preserve the no-platform-collection and no-write-capable-import
   scope?
5. Are there any missing release-gate or review-gate steps?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
