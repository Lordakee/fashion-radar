## Critical

No Critical blockers found. The Stage 19 design is broadly ready for implementation: it preserves the Stage 18 validation contract, keeps import execution local-only, validates before SQLite/data-dir creation, and reuses the existing single-file persistence path.

## Important

1. **Make the “invalid `--imported-at` + `--dry-run`” behavior explicit.**

   The design says `--dry-run` preserves Stage 18 behavior, but also says invalid `--imported-at` is reported before reading files or creating `--data-dir`. The implementation plan parses `imported_at` before checking `dry_run`.

   Because Stage 18 had no `--imported-at` on `import-signals-dir`, this is not a JSON-shape regression, but the intended behavior should be explicit:

   - Either `--imported-at` is accepted and validated even during dry-run, despite being unused;
   - Or `--imported-at` is ignored during dry-run because dry-run does not write rows.

   I recommend validating it consistently whenever supplied, because that matches the current plan and helps catch bad production commands early. Add a CLI test for:

   ```bash
   import-signals-dir ... --dry-run --imported-at not-a-date
   ```

   so the behavior is locked.

2. **Strengthen the no-artifact test list for invalid and unreadable directories.**

   The design’s testing requirements include invalid directory, unreadable directory, and no-match cases. The implementation plan’s Task 2 Step 3 explicitly lists:

   - invalid `--imported-at`;
   - one clean file plus one bad file;
   - no matching files;
   - `--dry-run` with `--data-dir`.

   It does not explicitly list invalid directory and unreadable directory in that step, although they are mentioned elsewhere in the design. Before implementation, add explicit checklist items/tests ensuring both failure modes:

   - exit non-zero;
   - print Stage 18 dry-run diagnostics;
   - do not create `--data-dir`;
   - do not create SQLite;
   - do not create config/report artifacts.

3. **Clarify implementation detail for preserving Stage 18 JSON key order and shape.**

   The design correctly requires dry-run JSON/table shape preservation. The plan says `dry_run_manual_signal_directory(...)` should call `load_manual_signal_directory_rows(...).result`, which is good.

   However, the new `ManualSignalDirectoryLoadResult` must not alter the serialized dry-run model. Implementation should ensure:

   - `ManualSignalDirectoryDryRunResult` fields remain exactly as currently defined;
   - no `rows` field leaks into dry-run JSON;
   - existing `files[*]` and `findings[*]` fields remain unchanged;
   - dry-run JSON still comes from `result.model_dump_json(indent=2)` on `ManualSignalDirectoryDryRunResult`.

   This is probably what the plan intends, but it is important enough to state explicitly in the implementation notes/tests.

4. **Add a test that validation reads all matched files before import and fails atomically.**

   The mixed clean/invalid file test covers “no rows returned” at module level and CLI “imports nothing” at command level. To make the safety guarantee very clear, the CLI test should assert that the clean file’s row is not present after a failure, preferably by checking no DB file exists at all.

   The current plan says this, but the test should specifically use multiple matched files where the first sorted file is valid and the later sorted file is invalid. That confirms the implementation does not import incrementally as it validates.

5. **Be careful with the plan’s docs boundary scan.**

   The proposed `rg` boundary scan includes terms like `authorization`, `audit`, and `policy`, but the plan/design themselves intentionally contain negative boundary language using those terms. The expected result says hits should be command examples or explicit negative boundary language, which is fine.

   Implementation should not treat the scan as “zero hits expected.” It should be reviewed manually so negative boundary statements are allowed, while source acquisition/scraping/approval workflow language is not.

## Minor

1. **`ManualSignalDirectoryLoadResult` model config can be stricter.**

   The plan proposes:

   ```python
   model_config = ConfigDict(arbitrary_types_allowed=True)
   ```

   Since both fields are Pydantic models/lists of Pydantic models, `arbitrary_types_allowed=True` likely is unnecessary. Consider:

   ```python
   model_config = ConfigDict(extra="forbid")
   ```

   This would match the rest of the importer result models and avoid accidental extra fields.

2. **Consider adding a JSON success summary snapshot-ish assertion.**

   The plan already checks exact top-level key order for JSON success output. That is good. It may also be useful to assert `directory`, `input_format`, and `pattern` values, not only counts, so the compact import summary contract is fully covered.

3. **Clarify empty matched files behavior if not already accepted.**

   Existing `load_manual_signal_rows()` accepts CSV with headers and no data as zero rows, and JSON `[]` as zero rows. The plan appears to preserve that. If zero-row matched files should be considered valid, no change needed. If not, Stage 19 is not the place to change it, but tests should avoid unintentionally implying a new policy.

4. **CLI help wording should change from dry-run-only.**

   Current command docstring says:

   ```python
   """Dry-run local manual signal files in one directory without importing rows."""
   ```

   The plan says to implement import execution but does not explicitly call out updating the docstring/help summary. It should be updated to something like:

   ```python
   """Validate or import local manual signal files from one directory."""
   ```

5. **Renderer wording is acceptable but slightly ambiguous.**

   `Files: 2 imported` means two files were successfully imported, not that files were copied. That is probably fine, but `Files: 2 validated` or `Files: 2 processed` would be marginally clearer. Not a blocker.

## Review Questions Answered

1. **Stage 18 dry-run behavior and JSON shape:** Mostly preserved. The plan’s loader reuse is sound, provided dry-run still serializes only `ManualSignalDirectoryDryRunResult`.

2. **Import safety:** Yes. The plan validates `--imported-at`, then validates all matched files, and only then opens SQLite/creates `--data-dir`.

3. **Reuse of `store_manual_signal_rows(...)`:** Yes. This is consistent with single-file import behavior, including URL upsert semantics and `items_added = after_count - before_count`.

4. **CLI option semantics:** Mostly clear. `--data-dir`, `--imported-at`, `--dry-run`, `--format`, and `--output-format` are compatible with existing style. Clarify `--imported-at` behavior during dry-run.

5. **Non-recursive deterministic matching:** Yes. Both design and plan preserve `iterdir()`, `is_file()`, `fnmatch.fnmatch(path.name, pattern)`, and sorting by path string. They explicitly reject `Path.glob()`/`rglob()`.

6. **Test coverage:** Good overall, but strengthen explicit coverage for invalid/unreadable directory no-artifact behavior and invalid `--imported-at` with `--dry-run`.

7. **Docs boundaries:** The design and plan avoid adding source acquisition, scraping, platform coverage, authorization verification, approval/audit/policy workflow features, and market-wide ranking claims. The scope guard is strong.

8. **Anything missing:** Only the clarifications/test tightenings above. No architectural blocker.

Approved for Stage 19 implementation
