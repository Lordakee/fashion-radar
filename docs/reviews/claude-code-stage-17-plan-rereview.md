Not approved

- `Critical:` None.

- `Important:`
  1. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 3: Add CLI Command And CLI Tests`, Step 1: CLI invalid-directory coverage is still incomplete for unreadable directories.
     The plan adds CLI tests for a missing directory and a file path used as a directory, and module coverage for unreadable directory via `Path.iterdir` monkeypatch, but it does not add a user-facing CLI unreadable-directory test. Add a CLI test that monkeypatches `Path.iterdir` or otherwise simulates enumeration `OSError` and asserts:
     - exit code is non-zero;
     - output includes `invalid_directory`;
     - output does not include a traceback;
     - JSON output is stable if `--format json` is used, or add a separate JSON failure-path test;
     - no config/data/report/SQLite/report/digest/latest/index/workflow artifacts are created on this failure path.

  2. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 3`, JSON CLI tests: JSON failure-path shape is not explicitly tested.
     The successful JSON test checks top-level key presence, but the plan does not require CLI JSON tests for directory-level errors such as `invalid_directory` or `no_matching_files`. Add JSON tests for at least:
     - missing or invalid directory producing `invalid_directory`;
     - no matching files producing `no_matching_files`.

     These should assert exact stable shape and values, including:
     - `file_count == 0`;
     - `row_count == 0`;
     - `valid_row_count == 0`;
     - `error_count == 1`;
     - `warning_count == 0`;
     - `info_count == 0`;
     - `files == []`;
     - `findings[0]["code"]` is the expected directory finding;
     - output is valid JSON only, with no traceback or table text mixed in.

  3. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 3`, `test_community_signal_lint_dir_prints_json`: serialized severity counts are only checked for key presence, not correctness.
     The prior review specifically called out severity counts as serialized fields rather than non-serialized properties. The revised model does that, but the JSON shape test should also assert exact `error_count`, `warning_count`, and `info_count` values. Add a JSON CLI test with mixed findings, or strengthen the existing JSON test plus add another case, so broken counting cannot pass by serializing all counts as `0`.

  4. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 1` / `Task 3`: deterministic aggregate count ordering is specified but not meaningfully tested.
     The implementation instruction correctly says `_merge_count_dicts()` should return `dict(sorted(counter.items()))`, but the planned tests only use single-key `source_name_counts` and `platform_counts`. Add a module or CLI JSON test with multiple unordered values and assert key order, for example:
     - `list(result.source_name_counts) == ["Alpha", "Zulu"]`;
     - `list(result.platform_counts) == ["community", "forum"]`;
     - `list(result.field_counts) == sorted(result.field_counts)`.

  5. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 3`, JSON CLI tests: deterministic serialized file ordering is not tested at the CLI boundary.
     The module test covers sorted `result.files`, but the CLI JSON test uses only one file. Add a CLI JSON test that creates files out of order, e.g. `b.csv` then `a.csv`, and asserts:
     ```python
     assert [Path(file["path"]).name for file in payload["files"]] == ["a.csv", "b.csv"]
     ```

  6. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 3`, no-artifact test: no-artifact behavior is only tested on a successful warning-only path.
     The current no-artifact assertions are concrete and broad for the success path, but the command’s no-side-effect guarantee should also hold on non-zero exits. Add at least one no-artifact test for a failure path, preferably missing directory, unreadable directory, or no matching files, with env config/data/reports set and `cwd` changed to `tmp_path`. Assert the same artifact absence list after the non-zero exit.

- `Minor:`
  1. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → `Task 2`, directory finding ordering: the plan says directory-level findings should be sorted, but Stage 17 appears to emit at most one directory-level finding per run. Either clarify that ordering is trivially deterministic in Stage 17 because only one directory-level finding is emitted, or add a small direct model/renderer test that constructs multiple directory findings and asserts sorted output.

  2. `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md` → no-artifact assertions: the broad checks are acceptable, especially `assert not Path("reports").exists()`, but the plan would be clearer if it explicitly states this is the primary assertion covering named report subpaths, with glob checks as secondary guards for digest/latest/index/workflow artifacts.

Resolved items: direct-child non-recursive matching is technically specified with `directory.iterdir()` plus `fnmatch.fnmatch(path.name, pattern)`; invalid directory handling is specified at module level; severity counts are modeled as serialized fields; aggregate sorting is specified in implementation; and the docs/scope language still avoids platform/source acquisition instructions, platform claims, and compliance/audit/policy product features.
