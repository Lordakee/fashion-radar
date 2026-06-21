# Stage 156 Plan Review Prompt

You are reviewing the Stage 156 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden first-run smoke validation for `external-tool-workflow` and
`external-tool-readiness` so top-level `directory`, `config_dir`, and `data_dir`
are pinned against caller-supplied expected values, while the real first-run
smoke flow passes its runtime temp paths explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-156-external-tool-path-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-156-external-tool-path-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_workflow.py`
- `src/fashion_radar/external_tool_readiness.py`

Please review:
- Whether the RED tests isolate coordinated top-level path drift after nested
  command fragments are rewritten consistently.
- Whether the validator signatures and `run_first_run_flow(context)` threading
  should mirror the existing imported-review/community-handoff path exactness
  pattern.
- Whether the deterministic smoke-flow test should use context-path external
  workflow/readiness payloads while preserving static default fixtures for
  builder parity tests.
- Whether using `shlex.split()` / `shlex.join()` for test command rewriting is
  sufficient and avoids broad string replacement risks.
- Whether runtime builders should remain unchanged.
- Whether verification commands are sufficient.

Return findings first with severity and file/line references. If there are no
blocking issues, say that explicitly.
