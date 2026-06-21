# Stage 155 Plan Review

## Verdict

**No critical blockers.** Two **important** findings must be addressed before
implementation begins because they affect correctness of the design's stated
resilience goal. Several low-severity clarifications follow. Tests-only scope,
helper derivation, and verification commands are sound.

## Findings

### IMPORTANT

**I1. Plan/Design omit several `fashion_radar-0.1.0` sites that break under
version bump**

The design lists items to update, but misses several places where hardcoded
`fashion_radar-0.1.0.dist-info` keys must track `WHEEL_FILES` keys. After
`WHEEL_FILES` is routed through `EXPECTED_WHEEL_DIST_INFO_DIR`, a future version
bump could cause these overrides to fail to replace keys:

- `tests/test_package_archives.py:577` -
  `wheel_files_with_dist_info_dir()` uses
  `path.startswith("fashion_radar-0.1.0.dist-info/")`.
- `tests/test_package_archives.py:1001` - override key
  `"fashion_radar-0.1.0.dist-info/METADATA"` in
  `test_rejects_wheel_metadata_without_project_name`.
- `tests/test_package_archives.py:1016` - same override key in
  `test_rejects_wheel_metadata_without_project_version`.
- `tests/test_package_archives.py:1031` - override key
  `"fashion_radar-0.1.0.dist-info/entry_points.txt"` in
  `test_rejects_wheel_entry_points_without_console_script`.

The plan must explicitly enumerate these override sites and the
`wheel_files_with_dist_info_dir` helper.

**I2. Assertion strings referencing the project name/version must also be
derived**

The design mentions "expected strings" generically but does not enumerate these
assertion sites:

- `tests/test_package_archives.py:1009` -
  `"METADATA is missing Name: fashion-radar"` should use
  `EXPECTED_METADATA.name`.
- `tests/test_package_archives.py:1024` -
  `"METADATA is missing Version: 0.1.0"` should use
  `EXPECTED_METADATA.version`.
- `tests/test_package_archives.py:1041` -
  `"entry_points.txt is missing fashion-radar = fashion_radar.cli:app"` should
  derive from `EXPECTED_METADATA.console_script_lines`.
- `tests/test_package_archives.py:282-310` - the positive expected portions of
  the `expected_error` strings in
  `test_rejects_package_archives_with_mismatched_filenames` should be derived,
  while negative fixture names stay explicit.
- `tests/test_package_archives.py:353-354` and `:604-606` - the expected
  portions should use `EXPECTED_SDIST_ROOT_DIR` and
  `EXPECTED_WHEEL_DIST_INFO_DIR`.

### LOW

**L1. The proposed guard test does not prove routing**

The proposed guard test proves the derived key exists in `WHEEL_FILES`, not that
the key was constructed from the constant. Soften the wording and consider
checking all five dist-info keys.

**L2. Unsafe-path test inputs not addressed**

`tests/test_package_archives.py:359-401` embeds `fashion_radar-0.1.0` as test
input. Recommended handling: leave these explicit because they are specific
traversal patterns, and document that choice.

**L3. `write_sdist_with_raw_member` refactor shape is unspecified**

The function currently hardcodes both archive name and root prefix. The plan
should state whether to add keyword parameters or reference module constants
directly.

## Notes

- Tests-only scope is preserved.
- Derived constants reuse existing checker helpers.
- Negative fixtures should remain explicit.
- Verification commands are sufficient and use `uv --no-config run --frozen`.

## Required Plan Revisions

1. Expand Task 3 Step 1 to update `wheel_files_with_dist_info_dir()`.
2. Add a Task 3 step for the three `WHEEL_FILES` override keys.
3. Expand the expected string step with the exact assertion sites from I2.
4. Soften the design wording about the guard test proving routing.
5. Add a note that unsafe path traversal inputs remain explicit.
