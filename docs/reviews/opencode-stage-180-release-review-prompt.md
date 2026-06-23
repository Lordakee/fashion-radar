# Stage 180 Release Review Prompt

Review the Stage 180 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 180 Release Review

Objective:

Add a regression test proving the package archive checker reports both invalid
UTF-8 errors when a wheel contains invalid bytes in both `METADATA` and
`entry_points.txt`.

Changed files:

- `tests/test_package_archives.py`
  - Adds
    `test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback`.
- Stage 180 spec, plan, plan-review prompt, plan-review artifact, code-review
  prompt, and code-review artifact.

Scope boundaries:

- Test-only hardening.
- No package archive checker runtime changes.
- No archive metadata, required-member, forbidden-member, sdist, dependency, or
  `uv.lock` changes.
- No source acquisition, scraping, platform APIs, monitoring, scheduling, demand
  proof, ranking, coverage verification features, or compliance-review product
  features.

Review history:

- `docs/reviews/opencode-stage-180-plan-review.md`
  - No critical or important findings.
  - Minor notes only: exact-line stderr membership differs from sibling
    substring assertions but is valid; order is deterministic but not asserted
    because the goal is aggregation presence.
- `docs/reviews/opencode-stage-180-code-review.md`
  - No critical or important findings.
  - Minor notes only: exact-line assertion is valid, order is intentionally not
    asserted, and invalid bytes are a reliable adversarial fixture.

Focused verification evidence:

- RED/absence:
  - `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback -q`
  - Result before adding test: no matching test collected.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback -q`
  - Result: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_with_invalid_utf8_without_traceback tests/test_package_archives.py::test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback tests/test_package_archives.py::test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback -q`
  - Result: 3 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_package_archives.py -q`
  - Result: 75 passed.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_package_archives.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_package_archives.py`
  - Result: 1 file already formatted.

Release gate evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1377 passed.
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
- Review artifact hygiene helper:
  - Result: no process output, ANSI escapes, capture markers, or tool messages
    in Stage 180 review artifacts.

Release review questions:

1. Is Stage 180 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this test-only stage?
4. Did any out-of-scope runtime, archive metadata, required-member,
   forbidden-member, sdist, dependency, lockfile, source acquisition, ranking,
   coverage-verification feature, or compliance-review product feature behavior
   slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
