# Stage 169 Release Review Prompt

Review the Stage 169 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 169 Release Review

Objective:

Confirm that Stage 169 is ready to commit and push.

Changed files:

- `src/fashion_radar/importers/manual_signals.py`
- `tests/test_manual_signal_import.py`
- `docs/superpowers/specs/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-plan.md`
- `docs/reviews/opencode-stage-169-plan-review-prompt.md`
- `docs/reviews/opencode-stage-169-plan-review.md`
- `docs/reviews/opencode-stage-169-code-review-prompt.md`
- `docs/reviews/opencode-stage-169-code-review.md`
- `docs/reviews/opencode-stage-169-release-review-prompt.md`

Scope boundaries:

- Human-readable `import-signals-dir --dry-run` per-file table wording only.
- No changes to `dry_run_manual_signal_directory(...)`.
- No changes to `load_manual_signal_rows(...)`.
- No changes to import semantics, SQLite writes, row validation, directory
  scanning, sorting, structured models, JSON output, CLI command flow, first-run
  smoke command shape, or readiness checks.
- No changes to summary lines such as `Files: ...`, `Rows: ...`, or
  `Errors: ...`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-169-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-169-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_manual_signal_import.py::test_render_manual_signal_directory_dry_run_table_uses_singular_file_count_labels -q`
  - Result before implementation: 1 failed. The file line ended with
    `1 rows, 1 errors`.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_manual_signal_import.py -q`
  - Result: 43 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py`
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
  - Result: Resolved 84 packages in 1ms.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no token-bearing header configured.

Release review questions:

1. Is Stage 169 in scope and ready to commit?
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
