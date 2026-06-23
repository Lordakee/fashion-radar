# Stage 180 Code Review Prompt

Review the Stage 180 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree.
Start the response exactly with:

# Stage 180 Code Review

Objective:

Add a regression test proving the package archive checker reports both invalid
UTF-8 errors when a wheel contains invalid bytes in both `METADATA` and
`entry_points.txt`.

Changed files:

- `tests/test_package_archives.py`
  - Adds
    `test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback`.
- Stage 180 spec, plan, plan-review prompt, and plan-review artifact.

Review context:

- `docs/superpowers/plans/2026-06-24-stage-180-package-archive-dual-invalid-utf8-plan.md`
- `docs/reviews/opencode-stage-180-plan-review.md`
- `scripts/check_package_archives.py`
- `docs/reviews/opencode-stage-163-release-review.md`

Scope boundaries:

- Test-only hardening.
- No package archive checker runtime changes unless the test exposed a real
  defect.
- No archive metadata, required-member, forbidden-member, sdist, dependency, or
  `uv.lock` changes.
- No source acquisition, scraping, platform APIs, monitoring, scheduling, demand
  proof, ranking, coverage verification features, or compliance-review product
  features.

Expected implementation:

- The new test is placed immediately after
  `test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback`.
- The fixture uses `WHEEL_FILES | {...}` and does not mutate `WHEEL_FILES` in
  place.
- Both overridden wheel members are under `EXPECTED_WHEEL_DIST_INFO_DIR`.
- The fixture writes both a wheel and an sdist before running the checker.
- The test asserts return code `1`.
- The test checks exact stderr line membership for:
  - `METADATA is not valid UTF-8`
  - `entry_points.txt is not valid UTF-8`
- The test asserts stderr does not contain `Traceback` or `UnicodeDecodeError`.
- Existing package archive tests should not be weakened or deleted.

Verification evidence:

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

Review questions:

1. Does the implementation match the approved Stage 180 plan?
2. Does the test prove both invalid UTF-8 validators run and aggregate their
   friendly errors?
3. Is the exact-line stderr assertion appropriate?
4. Did any out-of-scope runtime, archive metadata, required-member,
   forbidden-member, sdist, dependency, lockfile, source acquisition, ranking,
   coverage-verification feature, or compliance-review product feature behavior
   slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
