## Critical

No Critical findings.

## Important

1. **CLI-level error coverage is thinner than the review checklist asks for.**
   The plan covers `invalid_directory` at CLI level, and covers `no_matching_files` / unreadable directory at module level. But the review request explicitly calls out CLI failure coverage for invalid/no-match/unreadable directory. Add focused CLI tests for:
   - no matched files exits non-zero and emits stable `no_matching_files`;
   - unreadable directory exits non-zero without traceback/artifacts, probably via monkeypatching `Path.iterdir`;
   - preferably JSON output for `no_matching_files` too, since directory-level findings are part of the stable JSON contract.

2. **No explicit implementation guard/test prevents accidental `Path.glob()` / `rglob()` use.**
   The plan’s implementation uses `directory.iterdir()` + `path.is_file()` + `fnmatch.fnmatch(path.name, pattern)`, and tests `**/*.csv` does not recurse. That is probably sufficient behaviorally, but because this is a hard architecture constraint, add a lightweight static test or review checklist item that scans the implemented function for `.glob(` / `.rglob(`, or at least make this an explicit code-review gate.

3. **Post-acceptance “commit and push” instructions are outside the requested Stage 18 implementation plan.**
   The Stage 18 scope is implementation and verification; the plan’s “Post-Acceptance Release And Upload” section includes commit/push guidance and temporary `GIT_ASKPASS` handling. This is not a product/code scope violation, but it is operationally beyond “ready for implementation” and could be misused by an agent. I’d move this to a separate release checklist or explicitly mark it as maintainer-only, not part of implementation.

4. **Directory-level stable messages should be fully enumerated in the plan.**
   The design names stable codes and examples, and the implementation plan hardcodes messages for invalid/missing, unreadable, and no-match. Good. To make stability unambiguous, add a small table in the plan/spec mapping:
   - `invalid_directory` / not directory → exact message;
   - `invalid_directory` / unreadable → exact message;
   - `no_matching_files` → exact message.
   This helps prevent implementation drift.

5. **No test explicitly verifies `--dry-run` rejection avoids artifact creation.**
   The current no-`--dry-run` test uses a missing directory and checks no `invalid_directory`, which does prove directory validation did not run. But it does not combine this with env vars / CWD artifact assertions. Add a no-`--dry-run` no-artifact test or extend the existing one to assert no config/data/report/SQLite/report artifacts are created.

## Minor

1. **API naming is largely correct and preserves the strict-lint vs importer-dry-run distinction.**
   `dry_run_manual_signal_directory` and `render_manual_signal_directory_dry_run_table` clearly communicate importer-model dry-run behavior, distinct from `lint_community_signal_directory`. The result model names also preserve that distinction. Minor polish: `ManualSignalDryRunFindingSeverity` could be named `ManualSignalDirectoryDryRunFindingSeverity` for consistency, but this is not necessary.

2. **`--format` and `--output-format` are clear and compatible with existing `import-signals`.**
   The plan correctly keeps `--format` as input format and introduces `--output-format table|json` only for diagnostics. This avoids overloading `--format`. Help text could be slightly more explicit: “Input file format” for `--format`, “Diagnostics output format” for `--output-format`.

3. **The plan correctly avoids SQLite/import side effects.**
   The command path only calls `dry_run_manual_signal_directory()`, which wraps `load_manual_signal_rows()` and never calls `create_sqlite_engine()`, `initialize_schema()`, `store_manual_signal_rows()`, or estimates `items_added`. The command also omits `--data-dir`, `--config-dir`, `--reports-dir`, and `--imported-at`.

4. **Non-recursive deterministic matching is well specified.**
   The design and implementation plan use direct children only, regular files only, `fnmatch.fnmatch(path.name, pattern)`, and `sorted(paths, key=lambda path: str(path))`. The `**/*.csv` non-recursion test is a good guard.

5. **JSON result shape is generally stable.**
   The planned Pydantic model field ordering matches the design and test expectations. Directory-level findings are top-level; per-file failures are inside `files[*].findings`. That is coherent.

6. **Docs boundaries are strong.**
   The design and plan explicitly avoid scraping, platform acquisition, authorization verification, compliance/audit workflows, collectors, source types, background jobs, batch import, SQLite writes, matching/scoring/report changes, dashboard changes, and digest changes. The docs boundary scan is a useful guard.

7. **One wording issue: “lives in the `import-signals` namespace.”**
   Since Typer is adding a flat command named `import-signals-dir`, “namespace” could be read as implying a nested subcommand. Not a blocker, but consider rephrasing to “uses the `import-signals-dir` naming family” or “sits next to `import-signals`”.

## Answers To Review Questions

1. **API naming distinction:** Yes. The planned names distinguish strict `community-signal-lint-dir` from importer-model dry-run validation.
2. **Required `--dry-run`:** Yes, coherent and checked before directory reads. Add no-artifact assertion for this path.
3. **`--format` vs `--output-format`:** Yes, clear and compatible. Help text can be more explicit.
4. **No SQLite/artifacts/import/items_added:** Yes, the plan avoids these.
5. **Non-recursive deterministic matching:** Yes.
6. **Stable directory errors:** Mostly yes; make exact messages table-driven in the spec/plan.
7. **Test coverage:** Broad, but missing CLI-level no-match/unreadable and no-dry-run no-artifact assertions.
8. **Docs boundaries:** Yes, strong.
9. **Missing before implementation:** Add the Important test/clarity improvements above.

Not approved
