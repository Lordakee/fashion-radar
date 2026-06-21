# Stage 142 Plan Review Prompt

You are reviewing the Stage 142 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-readiness` first-run smoke validation so the Rednote MCP `install_hint` must match the exact expected string.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-142-readiness-install-hint-exact-design.md`
- `docs/superpowers/plans/2026-06-21-stage-142-readiness-install-hint-exact-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_readiness.py`

Please review:
- Whether the exact expected install hint matches runtime builder output.
- Whether the RED test would fail before implementation and pass after exact equality.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
