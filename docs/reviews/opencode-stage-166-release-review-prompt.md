# Stage 166 Release Review Prompt

Review the Stage 166 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 166 Release Review
```

Objective:

Confirm that Stage 166 is ready to commit and push.

Changed files:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-design.md`
- `docs/superpowers/plans/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-plan.md`
- `docs/reviews/opencode-stage-166-plan-review-prompt.md`
- `docs/reviews/opencode-stage-166-plan-review.md`
- `docs/reviews/opencode-stage-166-code-review-prompt.md`
- `docs/reviews/opencode-stage-166-code-review.md`
- `docs/reviews/opencode-stage-166-release-review-prompt.md`

Scope boundaries:

- Local first-run smoke validator hardening only.
- No product code changes under `src/`.
- No exact assertions for nested `files` lists.
- No exact assertions for nested `findings` lists.
- No CLI changes.
- No JSON producer/model changes.
- No database, import, lint, candidate, workflow, dashboard, or report changes.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking,
  coverage verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-166-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-166-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- RED before implementation:
  - `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"`
  - Result: 23 failed, 7 passed, 131 deselected. The failures were the newly
    added drift cases that current validator did not catch.
- GREEN after implementation:
  - `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"`
  - Result: 30 passed, 131 deselected.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  - Result: 2 files already formatted.

Release verification evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1363 passed.
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

1. Is Stage 166 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this smoke-validator
   hardening stage?
4. Did any out-of-scope behavior, production file under `src/`, generated
   artifact, secret, token, or local private data enter the working tree?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
