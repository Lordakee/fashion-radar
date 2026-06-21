# Stage 155 Plan Rereview

## Verdict

**No remaining Critical or Important blockers.** All required revisions from
the first plan review's IMPORTANT findings (I1, I2) and the supporting LOW
clarifications (L1, L3) are now reflected in the design and plan. The
negative-input boundary (L2) is also documented.

## Verification of Required Revisions

**I1 — `wheel_files_with_dist_info_dir()` and three override keys covered**
- Design spec:67-70 explicitly covers the helper and the override keys.
- Plan Task 3 Step 3 (plan:117-123) enumerates all three override sites:
  `test_rejects_wheel_metadata_without_project_name`,
  `test_rejects_wheel_metadata_without_project_version`, and
  `test_rejects_wheel_entry_points_without_console_script`.
- Plan Task 3 Step 4 (plan:125-129) updates `wheel_files_with_dist_info_dir()`
  to use `EXPECTED_WHEEL_DIST_INFO_DIR`.

**I2 — Expected-string assertion sites covered**
Plan Task 3 Step 6 (plan:141-158) explicitly covers:
- expected archive filenames (`test_rejects_package_archives_with_mismatched_filenames`)
- sdist root (`test_rejects_sdist_with_mismatched_root_directory`)
- dist-info directory (`test_rejects_wheel_with_mismatched_dist_info_directory`)
- `METADATA is missing Name: ...`
- `METADATA is missing Version: ...`
- `entry_points.txt is missing ...` (console script)

**L1 — Guard test wording softened**
Design spec:109-112 no longer claims the guard test proves routing. It now
states the guard verifies the derived dist-info key is present in `WHEEL_FILES`
and credits the end-to-end positive archive test for proving alignment with
checker expectations.

**L2 — Unsafe traversal inputs documented as explicit negatives**
Design spec:91-94 lists unsafe archive-member path strings as negative fixtures.
Plan Task 3 Step 6 (plan:156-158) reiterates they stay explicit.

**L3 — `write_sdist_with_raw_member` refactor shape specified**
Design spec:74-75 states the function uses `EXPECTED_SDIST_ARCHIVE_NAME` and
`EXPECTED_SDIST_ROOT_DIR` directly inside the body. Plan Task 3 Step 5
(plan:131-139) mirrors this.

## New Blockers Introduced

None. The plan remains tests-only, preserves checker/runtime behavior, keeps
negative fixtures explicit, and uses frozen `uv --no-config` verification
commands throughout.
