# Claude Code Stage 18 Plan Rereview Prompt

You are rereviewing the Stage 18 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Previous Review Result

Initial Stage 18 plan review returned `Not approved` with five Important
findings:

1. CLI failure coverage needed no-match and unreadable-directory cases.
2. Add a guard against accidental `Path.glob()` / `rglob()` use.
3. Mark post-acceptance commit/push steps as outside implementation.
4. Enumerate exact stable directory-level messages.
5. Add no-`--dry-run` no-artifact coverage.

## Fixes Made

Updated:

- `docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md`
- `docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md`

Changes:

- Added stable directory-level message table:
  - missing/not directory:
    `Manual signal directory does not exist or is not a directory.`
  - unreadable:
    `Could not read manual signal directory.`
  - no matches:
    `No regular files matched the pattern in the directory.`
- Added a planned module-level static guard:

  ```python
  def test_manual_signal_directory_dry_run_does_not_use_path_glob() -> None:
      source = inspect.getsource(dry_run_manual_signal_directory)

      assert ".glob(" not in source
      assert ".rglob(" not in source
  ```

- Added planned CLI tests for:
  - JSON `no_matching_files` stable payload;
  - unreadable directory exits non-zero without traceback/artifacts;
  - missing `--dry-run` exits before reading files and creates no artifacts.
- Marked `Post-Acceptance Release And Upload` as an operator/maintainer
  checklist after implementation and Claude Code code review approval, not part
  of Stage 18 product implementation.
- Rephrased “namespace” wording in the design to `import-signals-dir` naming
  family.

## Rereview Request

Please rereview the current uncommitted planning artifacts:

- `docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md`
- `docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md`

Evaluate whether all previous Critical/Important concerns are fixed and whether
the plan is ready for implementation. The Stage 18 scope remains:

- local-only directory dry-run validation;
- requires `--dry-run`;
- no SQLite writes, no row import, no data/config/report directories;
- no scraping/crawling/browser automation/account automation/platform APIs;
- no source acquisition instructions;
- no compliance/audit/policy workflow product feature.

Return findings by severity and end with one of:

- `Approved for Stage 18 implementation`
- `Not approved`

Do not modify files.
