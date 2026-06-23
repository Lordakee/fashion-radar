# Stage 165 Release Review Prompt

Review the Stage 165 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 165 Release Review
```

Objective:

Confirm that Stage 165 is ready to commit and push.

Changed files:

- `tests/test_lint_formatting.py`
- `docs/superpowers/specs/2026-06-23-stage-165-lint-formatting-helper-tests-design.md`
- `docs/superpowers/plans/2026-06-23-stage-165-lint-formatting-helper-tests-plan.md`
- `docs/reviews/opencode-stage-165-plan-review-prompt.md`
- `docs/reviews/opencode-stage-165-plan-review.md`
- `docs/reviews/opencode-stage-165-code-review-prompt.md`
- `docs/reviews/opencode-stage-165-code-review.md`
- `docs/reviews/opencode-stage-165-release-review-prompt.md`

Relevant unchanged production file:

- `src/fashion_radar/lint_formatting.py`

Scope boundaries:

- Direct helper unit tests only.
- No production code changes.
- No renderer output changes.
- No CLI changes.
- No JSON output changes.
- No lint semantics, severity, sorting, or strict-mode changes.
- No docs output changes.
- No row-count grammar changes.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

Review history:

- `docs/reviews/opencode-stage-165-plan-review.md`
  - No critical findings.
  - No important findings.
- `docs/reviews/opencode-stage-165-code-review.md`
  - No critical findings.
  - No important findings.

Focused verification evidence:

- `uv --no-config run --frozen pytest tests/test_lint_formatting.py -q`
  - Result: 7 passed.
- `uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py -q -k "render_"`
  - Result: 14 passed, 114 deselected.
- `uv --no-config run --frozen ruff check tests/test_lint_formatting.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py`
  - Result: 1 file already formatted.

Release verification evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1340 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages in 8ms.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no token-bearing header configured.

Release review questions:

1. Is Stage 165 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this narrow test-only
   stage?
4. Did any out-of-scope behavior, production file, generated artifact, secret,
   token, or local private data enter the working tree?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
