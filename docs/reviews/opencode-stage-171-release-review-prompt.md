# Stage 171 Release Review Prompt

Review the Stage 171 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming
the evidence below and return one final review body.
Start the response exactly with:

# Stage 171 Release Review

Objective:

Confirm that Stage 171 is ready to commit and push.

Changed files:

- `src/fashion_radar/community_handoff_check.py`
- `tests/test_community_handoff_check.py`
- `docs/superpowers/specs/2026-06-23-stage-171-community-handoff-check-count-label-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-171-community-handoff-check-count-label-grammar-plan.md`
- `docs/reviews/opencode-stage-171-plan-review-prompt.md`
- `docs/reviews/opencode-stage-171-plan-review.md`
- `docs/reviews/opencode-stage-171-code-review-prompt.md`
- `docs/reviews/opencode-stage-171-code-review.md`
- `docs/reviews/opencode-stage-171-release-review-prompt.md`

Scope boundaries:

- Human-readable `community-handoff-check-dir` renderer summary count labels
  only.
- Preserve the Stage 167 singular error-count behavior.
- No changes to `check_community_handoff_directory(...)`.
- No changes to lint, candidate preview, or manual import dry-run logic.
- No changes to structured models, JSON output, CLI options, command flow,
  checks, strict-mode behavior, warnings, finding messages, or exit codes.
- No changes to historical stage design/plan/review artifacts that quote old
  output as prior context.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-171-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-171-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q`
  - Result before implementation: 1 failed. The lint line rendered
    `Lint: 1 files, 1/1 import-ready rows, 1 error`.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  - Result: 7 passed.
- `uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_check_dir_table_output_is_summary_only -q`
  - Result: 1 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: 2 files already formatted.

Release verification evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1367 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages in 13ms.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no token-bearing header configured.

Release review questions:

1. Is Stage 171 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this renderer-wording
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
