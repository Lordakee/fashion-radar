# Stage 139 Code Review Prompt

You are reviewing Stage 139 changes in `/home/ubuntu/fashion-radar`.

Base commit: `969a0b9c8f6e77c43e42a8d1cbaa8f9ec61f5793`

Review scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 139 plan and review docs

Requirements:
- First-run smoke imported-review and community-handoff validators must reject command argv drift, not just missing substrings.
- Runtime CLI builders must not be changed.
- Fixture metadata should mirror real workflow JSON.
- Tests should prove failures that old substring validators missed.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
