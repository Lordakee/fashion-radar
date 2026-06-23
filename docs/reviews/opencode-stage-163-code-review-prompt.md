# Stage 163 Code Review Prompt

Review the Stage 163 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 163 Code Review
```

Objective:

Make `scripts/check_package_archives.py` return deterministic checker errors,
not tracebacks, when wheel `.dist-info/METADATA` or
`.dist-info/entry_points.txt` contains invalid UTF-8 bytes.

Changed files:

- `scripts/check_package_archives.py`
  - `validate_wheel_metadata(...)` catches `UnicodeDecodeError` from
    `read_zip_text(...)` and returns `METADATA is not valid UTF-8`.
  - `validate_wheel_entry_points(...)` catches `UnicodeDecodeError` from
    `read_zip_text(...)` and returns `entry_points.txt is not valid UTF-8`.
- `tests/test_package_archives.py`
  - `write_wheel(...)` accepts `dict[str, str | bytes]`.
  - Adds invalid UTF-8 regression coverage for `METADATA`.
  - Adds invalid UTF-8 regression coverage for `entry_points.txt`.
- `docs/superpowers/specs/2026-06-23-stage-163-package-archive-invalid-utf8-design.md`
- `docs/superpowers/plans/2026-06-23-stage-163-package-archive-invalid-utf8-plan.md`
- `docs/reviews/opencode-stage-163-plan-review-prompt.md`
- `docs/reviews/opencode-stage-163-plan-review.md`

Scope boundaries:

- Wheel `METADATA` and `entry_points.txt` invalid UTF-8 only.
- No changes to package build configuration.
- No changes to archive filename, required-member, forbidden-member,
  `.dist-info` directory, metadata name/version, or console-script validation
  semantics.
- No sdist decoding changes.
- No runtime CLI product behavior changes.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

RED evidence before implementation:

- Command:
  `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_with_invalid_utf8_without_traceback tests/test_package_archives.py::test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback -q`
- Result before implementation: 2 failed.
- Failure shape: both subprocess runs exited nonzero with Python traceback
  stderr containing `UnicodeDecodeError`, and did not contain the expected
  stable checker messages.

GREEN evidence after implementation:

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

Review questions:

1. Does the implementation meet the Stage 163 objective?
2. Are the tests sufficient to prove deterministic no-traceback behavior for
   invalid UTF-8 in both wheel text members?
3. Is the `UnicodeDecodeError` handling narrow enough?
4. Did any out-of-scope package archive behavior change?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
