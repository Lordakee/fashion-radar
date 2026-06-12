Approved for Stage 17 implementation

- `Critical:` None.

- `Important:` None. The rereviewed plan now addresses the prior remaining Important finding:
  - `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`, Task 3, `test_community_signal_lint_dir_json_invalid_directory_shape`: asserts top-level key order, all aggregate values, empty aggregate maps/lists, and the complete `findings` list object with `severity`, `code`, `message`, `row`, and `field`.
  - Same section, `test_community_signal_lint_dir_json_no_matching_files_shape`: does the same for the no-match failure path.
  - No-artifact directory success and unreadable-directory failure tests both reuse `assert_no_community_lint_artifacts`.
  - `test_directory_lint_aggregates_matched_files_in_sorted_order` now uses differing field sets, asserts `source_weight` count, and checks sorted `field_counts`, `source_name_counts`, and `platform_counts` key order.

- `Minor:` Optional improvement: if you want to make the serialized nested finding-object ordering just as explicit as the top-level payload ordering, add assertions such as:

  ```python
  assert list(payload["findings"][0]) == ["severity", "code", "message", "row", "field"]
  ```

  to both CLI JSON failure-shape tests. The current plan already asserts the full nested finding object content, so this is not blocking.
