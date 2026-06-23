# Stage 170 Code Review

Objective:

Fix singular `1 row` wording in human-readable `community-signal-lint-dir`
per-file lines.

## Summary

The change is minimal, targeted, and correct. The per-file line in
`render_community_signal_directory_lint_table` previously hard-coded
`{file.row_count} rows`, producing `1 rows` for a one-row file. It now reuses
the existing `format_count_label(file.row_count, "row", "rows")` helper, which
is the same helper already used (a) inside `format_finding_counts` for the
finding-count phrasing on the very next segment of the same line, and (b) in
`importers/manual_signals.py` and `community_handoff_check.py` for identical
row-count wording. This makes the community-signals directory renderer
consistent with the manual-signals renderer that already renders `1 row`.

Scope is respected:
- Only the per-file `file.row_count` phrase changed in
  `render_community_signal_directory_lint_table`.
- The top-level summary line `Rows: {result.row_count} total, ... import-ready`
  is untouched (intentionally, since that line uses `total` grammar, not bare
  `rows`).
- `Files:`, `Fields:`, `Sources:`, `Platforms:`, `Findings:` lines, the
  per-file `import-ready` and finding-count segments, all structured models,
  JSON output, CLI flow, and finding ordering/messages are unchanged.
- `lint_community_signal_directory(...)` and `lint_community_signal_file(...)`
  are untouched.
- The docs example is synced from `1 rows` to `1 row` and is consistent with
  what the new code emits for a 1-row file with 1 error / 3 warnings / 2 info.

No source-acquisition, connector, scraping, platform-API, login/cookie,
monitoring, scheduling, demand-proof, ranking, coverage-verification, or
compliance-review behavior is introduced.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Test name drift (non-blocking). The test
   `test_render_community_signal_directory_lint_table_singularizes_finding_counts`
   gained a new assertion that singularizes the per-file **row** count
   (`- exports/signals.csv: 1 row, 0 import-ready, `), so its name now describes
   only part of what it covers. The test body remains correct and the added
   assertion is appropriate. A future rename to something like
   `..._singularizes_row_and_finding_counts` would improve fidelity, but this is
   cosmetic and not required for release.

## Verification Assessment

I independently re-ran the declared RED/GREEN and lint evidence; all claims hold.

- RED validity (reasoned): pre-change the f-string was
  `{file.row_count} rows`, so for `row_count=1` it emitted `1 rows,`. The new
  assertion
  `file_line.startswith("- exports/signals.csv: 1 row, 0 import-ready, ")`
  requires `1 row,`, which fails against `1 rows,`. The RED state is real and
  the cycle is meaningful (the assertion genuinely guards the fixed grammar).
- GREEN (re-run, fresh):
  `uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q`
  -> 1 passed.
- Full renderer test file + docs test (re-run, fresh):
  `uv --no-config run --frozen pytest tests/test_community_signal_lint.py tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
  -> 91 passed (90 in the lint module + 1 docs test).
- Lint (re-run, fresh):
  `uv --no-config run --frozen ruff check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
  -> All checks passed.
  `uv --no-config run --frozen ruff format --check ...` -> 2 files already
  formatted.

Renderer-scoping of the test is correct: it constructs a
`CommunitySignalDirectoryLintResult` (with a one-row `CommunitySignalLintResult`)
directly in memory and invokes `render_community_signal_directory_lint_table`
with no file I/O and no lint execution, so it isolates the renderer grammar.

`format_count_label` reuse safety: the helper lives in `lint_formatting.py`,
which imports nothing from `community_signals.py`, so there is no import cycle.
`community_signals.py` already imported `format_finding_counts` from that module
(which internally calls `format_count_label`), and the same row-count call
pattern is already established in `importers/manual_signals.py:333`, so the
reuse is idiomatic and consistent across the codebase.

Out-of-scope check: the diff touches exactly the per-file f-string, the import
line, one test assertion, and one docs example line. No summary wording, model
fields, JSON shape, CLI flow, finding ordering, or finding grammar changed.

## Verdict

Approve. The Stage 170 objective is met, scope is tightly respected, the helper
reuse is safe and cycle-free, and RED/GREEN plus lint/format evidence was
reproduced fresh. No critical or important findings. The single minor naming
note is non-blocking and can be addressed in a later cleanup. Ready to proceed
to release verification.
