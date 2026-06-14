## Critical findings

None.

## Important findings

None.

## Minor findings

1. **Snippet length test could be stricter for the intended cap.**
   The plan's proposed helper guarantees `<= REPORT_SNIPPET_MAX_CHARS`, but because it does `normalized[: REPORT_SNIPPET_MAX_CHARS - 3].rstrip() + "..."`, truncated snippets can be shorter than 500 characters when the cut point lands before/after whitespace. That is still a safe cap, but if "deterministic 500-character ASCII-ellipsis" is meant as exactly 500 characters for long non-empty inputs, the tests should assert `len(item.summary) == REPORT_SNIPPET_MAX_CHARS` for a long input without whitespace at the truncation boundary. If "maximum 500" is intended, the current approach is acceptable.

2. **Dashboard query should remain explicitly non-creating.**
   The planned `recent_signals()` correctly checks `db_path.exists()` before calling `create_sqlite_engine()`, which avoids creating the data directory for missing databases. It would be worth preserving that exact ordering in implementation and test coverage, because `create_sqlite_engine()` itself creates parent directories.

3. **Consider documenting the dashboard's local-only/public-field boundary in tests or docs.**
   The plan lists the intended recent-signal fields and excludes non-public/internal review data. This is good; adding a test that the returned dict keys are exactly the expected public/local review fields would make that boundary more robust.

## Verdict

The plan is acceptable to execute. It stays within Stage 36 scope, avoids schema/dependency/source-collection changes, puts snippet safety at the right model boundary, adds transparent score components without migration, and expands dashboard coverage using existing `EntityType`.

APPROVED FOR STAGE 36 REPORT DASHBOARD QUALITY
