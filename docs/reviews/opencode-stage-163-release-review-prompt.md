# Stage 163 Release Review Prompt

You are reviewing Stage 163 for release readiness in `/home/ubuntu/fashion-radar`.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 163 Release Review
```

## Objective

Make `scripts/check_package_archives.py` return deterministic checker errors,
not tracebacks, when wheel `.dist-info/METADATA` or
`.dist-info/entry_points.txt` contains invalid UTF-8 bytes.

## Changed Files

- `scripts/check_package_archives.py`
  - `validate_wheel_metadata(...)` now catches `UnicodeDecodeError` around
    `read_zip_text(...)` and returns `METADATA is not valid UTF-8`.
  - `validate_wheel_entry_points(...)` now catches `UnicodeDecodeError` around
    `read_zip_text(...)` and returns `entry_points.txt is not valid UTF-8`.
- `tests/test_package_archives.py`
  - `write_wheel(...)` accepts `dict[str, str | bytes]`.
  - Adds invalid UTF-8 regression coverage for wheel `METADATA`.
  - Adds invalid UTF-8 regression coverage for wheel `entry_points.txt`.
- `docs/superpowers/specs/2026-06-23-stage-163-package-archive-invalid-utf8-design.md`
- `docs/superpowers/plans/2026-06-23-stage-163-package-archive-invalid-utf8-plan.md`
- `docs/reviews/opencode-stage-163-plan-review-prompt.md`
- `docs/reviews/opencode-stage-163-plan-review.md`
- `docs/reviews/opencode-stage-163-code-review-prompt.md`
- `docs/reviews/opencode-stage-163-code-review.md`

## Scope Boundaries

- Wheel `METADATA` and `entry_points.txt` invalid UTF-8 only.
- No package build configuration changes.
- No archive filename, required-member, forbidden-member, `.dist-info`
  directory, metadata name/version, or console-script validation semantic
  changes.
- No sdist decoding changes.
- No runtime CLI product behavior changes.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Review History

- Plan review: `docs/reviews/opencode-stage-163-plan-review.md`
  - No critical or important findings.
  - Minor commit-message precision note addressed in the plan.
- Code review: `docs/reviews/opencode-stage-163-code-review.md`
  - No critical or important findings.
  - Minor optional notes only: combined invalid-member test not required,
    post-decode `email.parser` permissiveness observation, and fixture byte
    observation.
- Read-only subagent diff review:
  - No findings.
  - Confirmed the diff is limited to invalid UTF-8 handling for wheel
    `METADATA` and `entry_points.txt`, plus tests.

## Verification Evidence

RED before implementation:

- `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_with_invalid_utf8_without_traceback tests/test_package_archives.py::test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback -q`
- Result before implementation: 2 failed.
- Failure shape: both subprocess runs emitted traceback stderr containing
  `UnicodeDecodeError` and lacked the new stable checker messages.

GREEN after implementation:

- `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_with_invalid_utf8_without_traceback tests/test_package_archives.py::test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback -q`
- Result: 2 passed.
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "invalid_utf8 or metadata or entry_points"`
- Result: 14 passed, 60 deselected.
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q`
- Result: 74 passed.
- `uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py`
- Result: All checks passed.
- `uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py`
- Result after formatting: 2 files already formatted.
- Real build smoke:
  `tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"`
- Result: checker printed `Package archives contain required files.`

Full release gate:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
- Result: 1326 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
- Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
- Result: 142 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
- Result: Resolved 84 packages in 6ms.
- `git diff --check`
- Result: clean.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
- Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
- Result: no configured extraheader.

## Review Questions

Please answer:

1. Does the final diff meet the Stage 163 objective?
2. Are the tests sufficient for invalid UTF-8 no-traceback behavior in both
   wheel text members?
3. Did any out-of-scope package archive behavior change?
4. Are the review and release artifacts clean enough to commit?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
