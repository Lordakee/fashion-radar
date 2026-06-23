# Stage 168 Release Review Prompt

Review the Stage 168 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 168 Release Review

Objective:

Confirm that Stage 168 is ready to commit and push.

Changed files:

- `docs/source-packs.md`
- `tests/test_source_packs_docs.py`
- `docs/superpowers/specs/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-design.md`
- `docs/superpowers/plans/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-plan.md`
- `docs/reviews/opencode-stage-168-plan-review-prompt.md`
- `docs/reviews/opencode-stage-168-plan-review.md`
- `docs/reviews/opencode-stage-168-code-review-prompt.md`
- `docs/reviews/opencode-stage-168-code-review.md`
- `docs/reviews/opencode-stage-168-release-review-prompt.md`

Scope boundaries:

- Documentation and documentation-test drift guard only.
- No changes to `configs/source-packs/fashion-public.example.yaml`.
- No source-pack linter behavior changes.
- No CLI changes.
- No collector changes.
- No network availability probing.
- No Google News RSS, Google Trends, source acquisition expansion, scraping,
  browser automation, platform APIs, login, cookies, monitoring, scheduling,
  demand proof, ranking, coverage verification, or compliance-review product
  features.

Review history:

- `docs/reviews/opencode-stage-168-plan-review.md`
  - No critical findings.
  - No important findings.
  - Recommended two minor improvements, both adopted.
- `docs/reviews/opencode-stage-168-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- RED:
  - Temporarily stashed only `docs/source-packs.md` to run the new tests
    against the previous docs while keeping the new tests.
  - `uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q`
  - Result: 2 failed, 1 passed. Failures were the two new drift tests.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q`
  - Result: 3 passed.
- `uv --no-config run --frozen ruff check tests/test_source_packs_docs.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py`
  - Result: 1 file already formatted.
- `git diff --check`
  - Result: no output, exit 0.

Release verification evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1366 passed.
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

1. Is Stage 168 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this docs/test-only
   source-pack synchronization stage?
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
