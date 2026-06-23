# Stage 170 Release Review Prompt

Review the Stage 170 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 170 Release Review

Objective:

Confirm that Stage 170 is ready to commit and push.

Changed files:

- `src/fashion_radar/community_signals.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`
- `docs/superpowers/specs/2026-06-23-stage-170-community-signal-directory-file-row-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-170-community-signal-directory-file-row-grammar-plan.md`
- `docs/reviews/opencode-stage-170-plan-review-prompt.md`
- `docs/reviews/opencode-stage-170-plan-review.md`
- `docs/reviews/opencode-stage-170-code-review-prompt.md`
- `docs/reviews/opencode-stage-170-code-review.md`
- `docs/reviews/opencode-stage-170-release-review-prompt.md`

Scope boundaries:

- Human-readable `community-signal-lint-dir` per-file row-count wording only.
- No changes to `lint_community_signal_directory(...)`.
- No changes to `lint_community_signal_file(...)`.
- No changes to structured models, JSON output, CLI command flow, field counts,
  source counts, platform counts, finding ordering, finding messages, or
  finding-count grammar.
- No changes to top-level summary lines such as `Rows: ... total, ...
  import-ready`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-170-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-170-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q`
  - Result before implementation: 1 failed. The file line rendered
    `- exports/signals.csv: 1 rows, 0 import-ready, 1 error, 1 warning, 1 info`.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_signal_lint.py -q`
  - Result: 90 passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
  - Result: 1 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
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
  - Result: Resolved 84 packages in 4ms.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no token-bearing header configured.

Release review questions:

1. Is Stage 170 in scope and ready to commit?
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
