# Stage 196 Release Review Prompt

Review Stage 196 release readiness in `/home/ubuntu/fashion-radar`.

Scope:

- Latin folding parity changes in `src/fashion_radar/extract/text.py`
- Regression tests in `tests/test_text.py`, `tests/test_dedupe.py`,
  `tests/test_matcher.py`, and `tests/test_cli_docs.py`
- Stage 196 plan and review artifacts

Questions:

1. Do the implementation and tests match the approved Stage 196 plan?
2. Are all Critical/Important plan and code review findings resolved?
3. Did final verification include full pytest, release hygiene, focused ruff
   check/format, `git diff --check`, lockfile validation, and mirror-marker
   scanning?
4. Does the commit manifest include all modified Stage 196 files and exclude
   `uv.lock`/`pyproject.toml` when unchanged?
5. Does the stage avoid social scraping/core connectors, platform APIs,
   source-ranking/demand-proof claims, and compliance-review product features?

Return:

- Verdict: READY / NEEDS_WORK
- Blocking findings
- Non-blocking findings
- Verification evidence summary
- Scope boundary confirmation
- Handoff Summary
