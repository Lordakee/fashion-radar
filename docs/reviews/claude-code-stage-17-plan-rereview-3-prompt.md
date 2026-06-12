# Claude Code Stage 17 Plan Rereview 3 Prompt

You are rereviewing the Stage 17 plan for Fashion Radar after the third Claude
Code plan review returned `Not approved`. Run this as a read-only planning
review. Do not edit files, do not commit, do not call the network, do not run
collectors, do not create directories, do not open SQLite, and do not execute
platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-17-plan-rereview-3-prompt.md
```

## Prior Review Result

The third review had one remaining Important finding:

- CLI JSON failure-path tests for `invalid_directory` and `no_matching_files`
  did not assert the complete expected payload shape and stable serialized
  finding object.

It also listed Minor improvements:

- Use the no-artifact helper for the success no-artifact test.
- Strengthen field-count ordering coverage with differing field sets.

## Changes To Rereview

The plan now requires:

- `test_community_signal_lint_dir_json_invalid_directory_shape` to assert exact
  top-level key order, all aggregate values, empty dictionaries/lists, and the
  full `findings` list with severity, code, message, row, and field.
- `test_community_signal_lint_dir_json_no_matching_files_shape` to assert the
  same exact payload shape and full finding object.
- Success and failure no-artifact tests to reuse
  `assert_no_community_lint_artifacts`.
- The module aggregate ordering test to use differing field sets and assert
  `source_weight` count plus sorted field/source/platform key order.

## Plan And Design To Rereview

Please rereview:

- `docs/superpowers/specs/2026-06-12-stage-17-community-signal-directory-lint-design.md`
- `docs/superpowers/plans/2026-06-12-stage-17-community-signal-directory-lint-plan.md`

## Response Format

Start with one of:

- `Approved for Stage 17 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
