# Stage 172 Code Review Prompt

Review the Stage 172 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to the focused
commands listed below and return one final review body.
Start the response exactly with:

# Stage 172 Code Review

Objective:

Make the first-run smoke readiness parity test fail loudly if
`fashion_radar.external_tool_readiness` is missing or broken, instead of
silently skipping behind a stale Stage 66 fallback.

Changed files:

- `tests/test_first_run_smoke.py`
  - Replaces the stale optional import fallback with a direct import of
    `build_external_tool_readiness`.
  - Removes the stale `@pytest.mark.skipif(...)` decorator and redundant
    `assert build_external_tool_readiness is not None`.
  - Adds a meta test that rejects a `skipif` mark on
    `test_external_tool_readiness_payload_matches_real_rednote_readiness`.
- Stage 172 spec, plan, plan-review prompt, and plan-review artifact.

Scope boundaries:

- Test-hygiene only.
- No changes to `src/fashion_radar/external_tool_readiness.py`.
- No changes to first-run smoke script behavior.
- No changes to JSON payload shapes, validators, command ordering, adapter
  metadata, readiness boundaries, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-172-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: narrow `skipif` guard, same-module function-name coupling,
    and import consistency.

RED/GREEN evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q`
  - Result before implementation: 1 failed because the parity test still had a
    `skipif` pytest mark.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_matches_real_rednote_readiness -q`
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q`
  - Result: 19 passed.
- `uv --no-config run --frozen ruff check tests/test_first_run_smoke.py`
  - Initial result found one import-order issue after replacing the fallback.
  - Final result: All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py`
  - Result: 1 file already formatted.

Review questions:

1. Does the implementation meet the Stage 172 objective?
2. Is the RED meta test meaningful and scoped to the stale readiness `skipif`?
3. Is the direct import appropriate now that `external_tool_readiness` is
   implemented and tested?
4. Did any out-of-scope runtime, payload, adapter, smoke-script, or boundary
   behavior change slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
