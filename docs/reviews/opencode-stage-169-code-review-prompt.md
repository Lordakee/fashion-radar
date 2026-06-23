# Stage 169 Code Review Prompt

Review the Stage 169 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 169 Code Review

Objective:

Fix singular `1 row` and `1 error` wording in human-readable
`import-signals-dir --dry-run` per-file lines.

Changed files:

- `src/fashion_radar/importers/manual_signals.py`
  - Imports `format_count_label`.
  - Uses it only in `render_manual_signal_directory_dry_run_table(...)` per-file
    lines for `row_count` and `error_count`.
- `tests/test_manual_signal_import.py`
  - Adds a renderer-only RED/GREEN test that creates a valid dry-run result,
    uses `model_copy(...)` to force a synthetic per-file `row_count=1` and
    `error_count=1`, adds a matching file finding for fixture consistency, and
    expects `: 1 row, 1 error`.
- Stage 169 spec, plan, plan-review prompt, and plan-review artifact.

Scope boundaries:

- Human-readable `import-signals-dir --dry-run` per-file table wording only.
- No changes to `dry_run_manual_signal_directory(...)`.
- No changes to `load_manual_signal_rows(...)`.
- No changes to import semantics, SQLite writes, row validation, directory
  scanning, sorting, structured models, JSON output, CLI command flow, first-run
  smoke command shape, or readiness checks.
- No changes to summary lines such as `Files: ...`, `Rows: ...`, or
  `Errors: ...`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-169-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor import-placement wording was addressed in the plan.
  - Minor fixture-consistency note was addressed by adding a matching synthetic
    file finding in the renderer test.

RED/GREEN evidence:

- Initial RED setup:
  - First focused run failed with a missing test import, which was corrected.
- RED:
  - `uv --no-config run --frozen pytest tests/test_manual_signal_import.py::test_render_manual_signal_directory_dry_run_table_uses_singular_file_count_labels -q`
  - Result before implementation: 1 failed. The file line ended with
    `1 rows, 1 errors`.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_manual_signal_import.py -q`
  - Result: 43 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py`
  - Result: 2 files already formatted after formatting the test file.

Review questions:

1. Does the implementation meet the Stage 169 objective?
2. Is the test properly renderer-scoped and not coupled to malformed CSV
   internals?
3. Is the `format_count_label(...)` reuse safe and cycle-free?
4. Did any out-of-scope behavior or summary wording change slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
