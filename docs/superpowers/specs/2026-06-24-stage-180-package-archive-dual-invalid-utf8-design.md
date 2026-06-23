# Stage 180 Package Archive Dual Invalid UTF-8 Design

## Objective

Add a regression test proving the package archive checker reports both invalid
UTF-8 errors when a wheel contains invalid bytes in both `METADATA` and
`entry_points.txt`.

## Background

Stage 163 added invalid UTF-8 handling for each wheel text member separately.
Its release review recorded one optional follow-up: no test covers a single
wheel where both `METADATA` and `entry_points.txt` are invalid UTF-8. The
implementation already aggregates errors from both validators inside
`validate_wheel(...)`, so this stage should be a test-only guard unless the new
test exposes a real defect.

## Scope

In scope:

- Add one focused test in `tests/test_package_archives.py`.
- Build a wheel fixture with invalid bytes for both
  `<dist-info>/METADATA` and `<dist-info>/entry_points.txt`.
- Assert both stable error messages are present in stderr.
- Assert no traceback or raw `UnicodeDecodeError` leaks into stderr.
- Add Stage 180 plan/review artifacts.

Out of scope:

- Runtime checker changes unless the new aggregation test exposes a real
  defect.
- Changes to archive names, expected metadata, required members, forbidden
  member checks, sdist behavior, dependency files, or `uv.lock`.
- Source acquisition, scraping, platform APIs, monitoring, scheduling, demand
  proof, ranking, coverage verification features, or compliance-review product
  features.

## Technical Approach

Reuse the existing `write_wheel`, `write_sdist`, and `run_checker` helpers from
`tests/test_package_archives.py`. Add the new test next to the existing invalid
UTF-8 wheel tests so future maintainers see the single-member and combined
cases together.

The fixture should use the same invalid bytes as the existing tests:

```python
b"\xff\xfe\xfa"
```

The expected checker behavior is:

- exit code is `1`;
- stderr lines contain `METADATA is not valid UTF-8`;
- stderr lines contain `entry_points.txt is not valid UTF-8`;
- stderr does not contain `Traceback`;
- stderr does not contain `UnicodeDecodeError`.

## Acceptance Criteria

- A new dual invalid UTF-8 aggregation test exists in
  `tests/test_package_archives.py`.
- The test fails if either stable error line is missing.
- The test fails if a traceback or raw `UnicodeDecodeError` leaks.
- Focused package archive tests pass.
- `ruff check` and `ruff format --check` pass for the touched test file.
- Full release gate remains clean before commit.
