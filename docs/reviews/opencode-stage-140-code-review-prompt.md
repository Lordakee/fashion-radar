# Stage 140 Code Review Prompt

You are reviewing Stage 140 changes in `/home/ubuntu/fashion-radar`.

Base commit: `4ad41b45d89d5c872a7b0d8d1c1a2b6162073837`

Review scope:
- `tests/test_first_run_smoke.py`
- Stage 140 plan and review docs

Requirements:
- The deterministic first-run flow test must compare the full captured command sequence as exact argv tuples.
- Runtime smoke behavior must not change.
- The helper-negative test must prove exact comparison rejects command drift that old membership checks missed.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
