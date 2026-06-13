## Critical findings

None.

## Important findings

1. **The concrete CLI tests do not sufficiently prove “no subprocess execution / no SQLite / no report-dashboard-source code.”**
   The design requires tests to prove the command does not call subprocess execution, SQLite creation, report generation, dashboard code, or source collection. The plan states that goal, but the provided concrete test only monkeypatches `Path.iterdir` and checks that `data_dir` does not exist. That would not fail if the CLI accidentally called `subprocess.run`, `sqlite3.connect`, report/dashboard functions, or source collection code that did not create `data_dir`.
   **Recommendation:** Add explicit monkeypatch guards for likely side-effect entry points, e.g. `subprocess.run`, `subprocess.Popen`, `sqlite3.connect`, and any project-local importer/report/dashboard/source collection functions that would be risky if accidentally invoked.

2. **The “does not read directory” test is too narrow.**
   Monkeypatching only `Path.iterdir` does not catch reads through `Path.exists`, `Path.is_dir`, `Path.glob`, `Path.rglob`, `os.scandir`, `open`, or other traversal paths. The missing-directory success test is useful, but it does not fully prove the hard boundary.
   **Recommendation:** Add guards for `Path.glob`, `Path.rglob`, `Path.exists`/`is_dir` if the intended guarantee includes no filesystem metadata checks, and/or `os.scandir`. At minimum, make the test name match what it actually proves if only iteration is guarded.

3. **The plan’s “invalid timestamp raises through the CLI path, not the builder only” requirement is not fully aligned with the module test list.**
   The design says module tests should include “invalid timestamp raises through the CLI path, not the builder only,” but the plan places the invalid timestamp test only in `tests/test_cli.py`. That is likely acceptable behaviorally, but the wording in the design/plan is slightly inconsistent.
   **Recommendation:** Either clarify that this is a CLI test, or add a small module-level test documenting builder parsing behavior separately.

## Minor findings

1. **Table-output tests should assert intentional path echo more explicitly.**
   The JSON test checks `payload["directory"]`, and docs mention intentional path echo. The table test currently checks command names and no artifacts, but not that the supplied directory/config/data paths are printed intentionally in copyable commands.
   **Recommendation:** Add assertions that table output includes the supplied directory, config dir, and data dir, especially paths containing spaces, and that they are shell-quoted in commands.

2. **The plan should explicitly verify stable JSON step keys, not just top-level keys.**
   The JSON test asserts stable top-level keys and step names/effects, but not the exact key order/shape for each step.
   **Recommendation:** Add `assert list(payload["steps"][0]) == ["order", "name", "purpose", "command", "suggested_effect"]`.

3. **Boundary scan wording may miss some unsafe terms.**
   The boundary scan includes many risky words, but the user specifically mentions “fetch URLs,” “login,” “download media,” “browser automation,” “prove demand,” “verify platform coverage,” and “rank sources.” Some of these are absent or only partially covered.
   **Recommendation:** Expand the final `rg` scan to include `fetch|url|login|download|browser|automation|demand|platform coverage|rank sources|ranking`.

4. **Task 4 introduces review prompt artifacts under `docs/reviews/`, which are not mentioned in the Stage 30 design scope.**
   This is not unsafe, but it expands the file set beyond the design’s docs list.
   **Recommendation:** Keep if this is the project’s standard review workflow; otherwise make it optional or clarify it is process-only documentation.

5. **The implementation snippet’s `_shell_command(*parts: str)` relies on all passed values being strings.**
   Current literals likely are strings, but if `ManualSignalFormat` ever becomes an enum, `shlex.join` would fail.
   **Recommendation:** Either cast in `_shell_command` with `shlex.join(str(part) for part in parts)` or ensure input format remains a string literal type.

APPROVED FOR STAGE 30 IMPLEMENTATION
