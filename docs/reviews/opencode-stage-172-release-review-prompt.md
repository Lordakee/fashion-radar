# Stage 172 Release Review Prompt

Review the Stage 172 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live
tool status, ANSI output, command logs, markdown code fences, or multiple
drafts. This is a read-only review: do not edit files, do not run
`git stash`, and do not mutate the working tree. If you run verification, limit
it to confirming the evidence below and return one final review body.
Start the response exactly with:

# Stage 172 Release Review

Objective:

Confirm that Stage 172 is ready to commit, push, and close.

Changed files:

- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-23-stage-172-first-run-readiness-import-hardening-design.md`
- `docs/superpowers/plans/2026-06-23-stage-172-first-run-readiness-import-hardening-plan.md`
- `docs/reviews/opencode-stage-172-plan-review-prompt.md`
- `docs/reviews/opencode-stage-172-plan-review.md`
- `docs/reviews/opencode-stage-172-code-review-prompt.md`
- `docs/reviews/opencode-stage-172-code-review.md`
- `docs/reviews/opencode-stage-172-release-review-prompt.md`

Scope boundaries:

- Test-hygiene only.
- Preserve the existing `external_tool_readiness` payload shape and builder
  behavior.
- No changes to `src/fashion_radar/external_tool_readiness.py`.
- No changes to first-run smoke script behavior.
- No changes to JSON payload shapes, validators, command ordering, adapter
  metadata, readiness boundaries, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-172-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-172-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

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
- `uv --no-config run --frozen pytest -q`
  - Result: 1368 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages in 2ms.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no token-bearing header configured.

Release review questions:

1. Is Stage 172 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this test-hygiene
   stage?
4. Did any out-of-scope behavior, generated artifact, lockfile mirror churn,
   secret, token, or local private data enter the working tree?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
