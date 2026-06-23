# Stage 178 Release Review Prompt

Review the Stage 178 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 178 Release Review

Objective:

Add focused regression guards for community handoff directory check renderer
count labels and unavailable candidate preview output.

Changed files:

- `tests/test_community_handoff_check.py`
  - Renames the singular renderer test to
    `test_render_community_handoff_directory_check_table_uses_singular_count_labels`.
  - Adds exact plural renderer summary assertions.
  - Adds exact unavailable candidate-preview renderer assertions.
- Stage 178 spec, plan, plan-review prompt, plan-review artifact, code-review
  prompt, and code-review artifact.

Scope boundaries:

- Test-only hardening.
- No runtime behavior changes.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification
  features, compliance-review product features, dependency changes, or
  `uv.lock` changes.

Review history:

- `docs/reviews/opencode-stage-178-plan-review.md`
  - No critical or important findings.
  - Minor notes only: the plural test intentionally uses `model_copy` for
    renderer-grammar coverage, the unavailable branch reuses the existing
    deterministic bad CSV scenario, and the singular rename is safe.
- `docs/reviews/opencode-stage-178-code-review.md`
  - No critical or important findings.
  - Minor notes only: the plural test's semantic decoupling is intentional, the
    plural and singular tests complement each other, and the unavailable test
    intentionally duplicates setup to pin exact rendered output.

Focused verification evidence:

- RED/absence:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_plural_count_labels -q`
  - Result before adding test: no matching test collected.
- RED/absence:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview -q`
  - Result before adding test: no matching test collected.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_count_labels tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_plural_count_labels -q`
  - Result: 2 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview -q`
  - Result: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  - Result: 9 passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_community_handoff_check.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_community_handoff_check.py`
  - Result: 1 file already formatted.

Release gate evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1376 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches, exit 1.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no configured GitHub extraheader, exit 1.
- `perl -ne 'print "$ARGV:$.:$_" if /\e|build ·|→|^\s*\$/;' docs/reviews/opencode-stage-178-*.md`
  - Result: no output, exit 0.

Release review questions:

1. Is Stage 178 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this test-only stage?
4. Did any out-of-scope runtime, source acquisition, connector, scraping,
   platform API, ranking, coverage-verification feature, compliance-review
   product feature, dependency, or lockfile behavior slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
