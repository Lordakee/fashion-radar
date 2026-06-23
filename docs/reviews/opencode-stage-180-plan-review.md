# Stage 180 Plan Review

## Summary

Stage 180 is a focused, test-only hardening stage that closes the optional
Stage 163 follow-up (combined invalid UTF-8 coverage). The design and plan are
accurate, correctly scoped, and consistent with the existing
`tests/test_package_archives.py` conventions and the
`scripts/check_package_archives.py` aggregation behavior. I re-verified the
core premise against the source: both `validate_wheel_metadata(...)` and
`validate_wheel_entry_points(...)` are invoked independently inside
`validate_wheel(...)` when their members are present, each catches
`UnicodeDecodeError` and returns its single stable message, and both lists are
extended into one shared `errors` list, so both messages surface together. The
new test will pass against the current runtime without any checker changes. No
critical or important findings.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Assertion style is slightly inconsistent with the sibling tests. The plan
   uses exact-line membership
   (`stderr_lines = result.stderr.splitlines()` then
   `assert "METADATA is not valid UTF-8" in stderr_lines`), while the existing
   `test_rejects_wheel_metadata_with_invalid_utf8_without_traceback`
   (`tests/test_package_archives.py:1057`) and
   `test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback`
   (`tests/test_package_archives.py:1161`) use substring membership
   (`assert "..." in result.stderr`). Both forms are valid here because
   `main(...)` emits each error via `print(error, file=sys.stderr)`
   (`scripts/check_package_archives.py:175-176`), so each message is a whole
   stderr line. The exact-line form is arguably stricter (it will not match a
   substring of a longer future error), so this is not a defect; only a
   consistency note. Either form is acceptable.

2. The test does not assert the relative order of the two error lines. Order is
   in fact deterministic because `validate_wheel(...)` appends the METADATA
   errors before the `entry_points.txt` errors
   (`scripts/check_package_archives.py:267-274`). Order-agnostic assertions are
   more robust to refactoring and the stated objective is aggregation presence,
   not ordering, so omitting an order check is a reasonable design choice. No
   change required.

3. The plan's "self-review notes" correctly map spec coverage to the three
   tasks and correctly restate the out-of-scope boundary (no runtime checker,
   sdist, metadata, dependency, or `uv.lock` changes unless a real aggregation
   defect surfaces). No missing tasks and no placeholders detected.

## Verification Guidance

Re-confirm these claims during implementation:

- The aggregation path is real: `validate_wheel(...)` calls both validators
  when both members exist (`scripts/check_package_archives.py:267-274`), each
  returns `["METADATA is not valid UTF-8"]` / `["entry_points.txt is not valid
  UTF-8"]` from its `except UnicodeDecodeError` branch
  (`scripts/check_package_archives.py:362-365` and `:381-384`), and both lists
  are extended into one `errors` list. Both messages therefore print on
  separate stderr lines via `main(...)`.

- `WHEEL_FILES` already contains both
  `f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA"` and
  `f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt"`
  (`tests/test_package_archives.py:38` and `:45`), so the planned
  `WHEEL_FILES | {...}` override replaces both contents with
  `b"\xff\xfe\xfa"` while leaving the other required members (WHEEL, RECORD,
  LICENSE, `fashion_radar/*`) valid, so no unrelated errors are introduced.

- The fixture bytes `b"\xff\xfe\xfa"` are genuinely invalid UTF-8 (`\xff` is
  never a valid lead byte), so the decode is reached and reliably raises
  `UnicodeDecodeError`; the members themselves are present, so the presence
  guards at `scripts/check_package_archives.py:267` and `:271` pass.

- `write_wheel(...)` already accepts `dict[str, str | bytes]`
  (`tests/test_package_archives.py:153-166`) and `zipfile.ZipFile.writestr(...)`
  accepts `bytes`, so no helper change is needed.

- Placement is valid: `test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback`
  is the final test in the file (`tests/test_package_archives.py:1161-1177`),
  so "immediately after" appends cleanly at end of file.

Implementation should run, at minimum:

- `uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback -q`
  (expect pass; if it fails because one message is missing, that indicates a
  real aggregation defect and only then may the checker be touched, per the
  plan's Task 1 Step 3 note).
- `uv --no-config run --frozen pytest tests/test_package_archives.py -q`.
- `uv --no-config run --frozen ruff check tests/test_package_archives.py` and
  `uv --no-config run --frozen ruff format --check tests/test_package_archives.py`.
- The full release gate in Task 3 Step 1 before commit.

The planned release gate matches the AGENTS.md frozen/mirror conventions
(`uv --no-config run --frozen ...` and
`env -u UV_DEFAULT_INDEX ... UV_NO_CONFIG=1 uv lock --check`).

## Verdict

Approve. The Stage 180 plan directly addresses the Stage 163 combined-coverage
follow-up, the proposed test is deterministic and correctly scoped to
aggregation behavior, placement next to the existing invalid UTF-8 tests is
appropriate, the verification/review/release/commit/push steps are sufficient
for a small test-only stage, and all scope boundaries are respected. No
critical or important findings; the three minor notes are optional and do not
block implementation. Proceed to implementation.
