# Claude Code Stage 17 Code Rereview Prompt

You are rereviewing `/home/ubuntu/fashion-radar` in read-only mode. Do not edit
files. Use maximum reasoning.

## Previous Review Result

Initial Stage 17 code review requested changes with one Important finding:

- `lint_community_signal_directory()` used an unstable unreadable-directory
  message by embedding the caught `OSError` text:
  `message=f"Could not read community signal directory: {exc}"`.

No Critical findings were reported.

## Fixes Made

- Added a focused regression assertion in
  `tests/test_community_signal_lint.py::test_directory_lint_reports_unreadable_directory`
  requiring:

  ```python
  assert result.findings[0].message == "Could not read community signal directory."
  ```

- Confirmed RED before the fix:

  ```text
  AssertionError:
  - Could not read community signal directory.
  + Could not read community signal directory: no access
  ```

- Changed `src/fashion_radar/community_signals.py` so the OSError branch now
  catches `except OSError:` and returns:

  ```python
  message="Could not read community signal directory."
  ```

- Addressed the minor docs note by updating the early
  `docs/architecture.md` flow/component summary to mention the non-recursive
  directory batch wrapper.

## Verification After Fix

```text
.venv/bin/python -m pytest tests/test_community_signal_lint.py -q -k unreadable_directory
1 passed, 22 deselected

.venv/bin/python -m pytest tests/test_community_signal_lint.py tests/test_cli.py -q -k "community_signal_lint_dir or directory_lint"
22 passed, 81 deselected

git diff --check
exit 0

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
78 files already formatted

.venv/bin/python -m pytest -q
366 passed

codegraph status
Files indexed: 92; Total nodes: 1457; Total edges: 3870
```

## Rereview Request

Please review the current working-tree diff, focusing on:

1. Whether the previous Important finding is fixed.
2. Whether the regression test is placed correctly and meaningful.
3. Whether the architecture docs update is accurate and not over-scoped.
4. Whether any new Critical or Important issues were introduced.
5. Whether Stage 17 is now approved for release checks, commit, and push.

The Stage 17 scope guard still applies: local-only, read-only directory batch
diagnostics; no scraping/crawling/browser automation/account automation/platform
APIs/source acquisition instructions; no import, SQLite, collector, scheduler,
dashboard, report, matching, scoring, policy/compliance/audit workflow changes.

Please return an approval status plus findings by severity. Do not modify files.
