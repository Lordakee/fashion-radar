# Stage 167 Release Review Prompt

Review the Stage 167 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 167 Release Review

Objective:

Confirm that Stage 167 is ready to commit and push.

Changed files:

- `src/fashion_radar/community_handoff_check.py`
- `tests/test_community_handoff_check.py`
- `docs/superpowers/specs/2026-06-23-stage-167-community-handoff-check-error-label-design.md`
- `docs/superpowers/plans/2026-06-23-stage-167-community-handoff-check-error-label-plan.md`
- `docs/reviews/opencode-stage-167-plan-review-prompt.md`
- `docs/reviews/opencode-stage-167-plan-review.md`
- `docs/reviews/opencode-stage-167-code-review-prompt.md`
- `docs/reviews/opencode-stage-167-code-review.md`
- `docs/reviews/opencode-stage-167-release-review-prompt.md`

Scope boundaries:

- Human-readable `community-handoff-check-dir` table wording only.
- Fix singular `1 error` wording for lint and import dry-run summary lines.
- No changes to `check_community_handoff_directory(...)`.
- No model, JSON, CLI command flow, lint, dry-run, candidate preview,
  strict-mode, or readiness semantics changes.
- No changes to `files`, `rows`, or `candidates` wording.
- No changes to `manual_signals.py`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking,
  coverage verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-167-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-167-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- RED before implementation:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q`
  - Result before implementation: 1 failed. The lint line ended with
    `, 1 errors`.
- GREEN after implementation:
  - Same focused test.
  - Result after implementation: 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  - Result: 7 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: 2 files already formatted.

Release verification evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1364 passed.
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

Additional read-only scope review:

- A Codex read-only explorer confirmed the uncommitted code change is limited to
  `src/fashion_radar/community_handoff_check.py` and
  `tests/test_community_handoff_check.py`, with `manual_signals.py` untouched.
- The explorer reported no critical, important, or minor findings.

Release review questions:

1. Is Stage 167 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this renderer-wording
   stage?
4. Did any out-of-scope behavior, generated artifact, secret, token, or local
   private data enter the working tree?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
