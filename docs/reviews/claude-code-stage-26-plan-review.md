Important

1. **Retained-row filtering is underspecified in the implementation plan and tests.**
   The design correctly says the command must show only retained `manual_import` rows, but the implementation plan’s core query behavior only says to read rows from `items` where `source_type == "manual_import"` with optional `source_name`. The proposed tests also insert plain manual-import rows without proving that non-retained/rejected/unretained manual-import rows are excluded.
   This is blocking because Stage 26’s safety boundary depends on matching Stage 25’s “retained manual_import rows only” semantics. Without an explicit retained-row selector and regression test, the command could expose local imported rows that the aggregate command intentionally omits.
   **Fix:** Update the plan to reuse the same retained/import-review filtering semantics as `imported-candidates`, and add tests with at least one retained row and one non-retained/rejected manual-import row for the same phrase, asserting only the retained row appears.

2. **Blank `--source-name` behavior is specified but not carried through the implementation/test plan.**
   The design says blank `--source-name` is treated as no source-name filter, but the implementation task only says “optional exact `source_name`” and the listed CLI/query tests do not cover blank `--source-name`.
   This is blocking because it is explicit CLI behavior and part of the source-filtering requirements. If omitted, `--source-name ""` may incorrectly filter to an empty stored source name instead of behaving like no filter.
   **Fix:** Add implementation steps to normalize blank `source_name` to `None` before querying, and add CLI/query tests for blank source name behaving identically to no source filter.

Minor

1. **`--limit 0` should be tested explicitly.**
   The design allows minimum `0`, and the plan rejects negative limits, but no proposed test confirms that `--limit 0` returns zero evidence rows while preserving `total_count`, `current_mentions`, and `baseline_mentions` before limit. This is not blocking, but it would strengthen coverage of the “counts before limit” contract.

2. **No issue with the public helper-wrapper approach.**
   Exposing small public wrappers in `discovery/candidates.py` for candidate key normalization and stored-entity candidate keys is a reasonable way to avoid importing private helpers and prevent candidate-matching drift, provided the wrappers delegate exactly to the existing discovery semantics and the tests verify confidence/as-of behavior.

3. **Docs/release checks are mostly adequate.**
   The docs wording is appropriately local/read-only and avoids implying verified entities, demand proof, scraping, monitoring, acquisition, platform coverage, source quality, or ranking. The boundary scan and installed-wheel smoke are good additions.

Not approved until the Important findings are resolved.
