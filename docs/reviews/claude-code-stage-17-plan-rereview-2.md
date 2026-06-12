Not approved

- `Critical:` None.

- `Important:`
  - `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`, Task 3, `test_community_signal_lint_dir_json_invalid_directory_shape` and `test_community_signal_lint_dir_json_no_matching_files_shape`: the revised plan still does not fully satisfy “CLI JSON failure paths ... have exact stable shape and values.”
    - `invalid_directory` checks the top-level key order and most aggregate values, but only asserts `payload["findings"][0]["code"] == "invalid_directory"`. It should assert the full `findings` list shape and stable values, including severity, code, row, field, and message.
    - `no_matching_files` is weaker: it does not assert top-level `directory`, `input_format`, `pattern`, `field_counts`, `source_name_counts`, or `platform_counts`, and also only checks the finding code. It should match the invalid-directory test’s exact top-level assertions and assert the full finding object.
    - Required change: make both JSON failure tests assert the complete expected payload shape for all stable fields, especially:
      - `directory`
      - `input_format`
      - `pattern`
      - all aggregate counts
      - empty aggregate dictionaries
      - `files == []`
      - `findings == [...]` with exact stable serialized finding contents.

- `Minor:`
  - `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`, Task 3, no-artifact helper: `test_community_signal_lint_dir_does_not_create_project_artifacts` duplicates the artifact assertions instead of using `assert_no_community_lint_artifacts(...)`. Reusing the helper would reduce drift between success-path and failure-path coverage.
  - `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`, Task 1 aggregation test: source/platform ordering coverage is meaningful, and field ordering is checked, but the field-count test would be stronger if it used multiple files with differing field sets so the merged field counts and ordering are both proven, not just sorted header order from uniform files.
  - The plan otherwise resolves the prior findings for unreadable-directory nonzero/no-traceback/no-artifact coverage, serialized severity count correctness, out-of-order CLI JSON file ordering, success and nonzero no-artifact paths, and the Stage 17 local-only/product-boundary constraints.
