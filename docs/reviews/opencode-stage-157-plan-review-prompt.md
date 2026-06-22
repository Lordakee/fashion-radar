# Stage 157 Plan Review Prompt

Review the Stage 157 design and implementation plan for Fashion Radar.

Files to review:

- `docs/superpowers/specs/2026-06-22-stage-157-first-run-community-handoff-strict-chain-design.md`
- `docs/superpowers/plans/2026-06-22-stage-157-first-run-community-handoff-strict-chain-plan.md`
- Existing implementation context:
  - `scripts/check_first_run_smoke.py`
  - `tests/test_first_run_smoke.py`
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/community_handoff_workflow.py`
  - `src/fashion_radar/community_handoff_check.py`

Objective:

Harden `run_first_run_flow()` so the direct community handoff directory smoke
checks match the stricter local command chain already emitted and validated by
`community-handoff-workflow`.

Proposed implementation:

- Update the deterministic first-run command sequence test first.
- Add `--strict` to the direct `community-signal-lint-dir` call.
- Add a direct `community-handoff-check-dir ... --strict` call.
- Add `--imported-at AS_OF` to the direct `import-signals-dir ... --dry-run`
  call.
- Keep `--dry-run` present and do not run the write-capable directory import
  workflow command.
- Keep runtime CLI implementation unchanged.

Review questions:

1. Does the plan correctly target the gap between validated
   `community-handoff-workflow` metadata and actual first-run smoke execution?
2. Is the proposed command order reasonable and consistent with the existing
   smoke flow?
3. Does the plan preserve the local-only, no-platform-collection scope?
4. Are the tests sufficient to fail before implementation and pass after?
5. Is any additional validation needed before this stage can be implemented?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
