# Stage 169 Plan Review Prompt

Review the Stage 169 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 169 Plan Review

Objective:

Fix singular `1 row` and `1 error` wording in human-readable
`import-signals-dir --dry-run` per-file lines.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-plan.md`
- `src/fashion_radar/importers/manual_signals.py`
- `tests/test_manual_signal_import.py`

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

Planned implementation:

1. Add a renderer-only RED test in `tests/test_manual_signal_import.py`.
2. Create a valid directory dry-run result, then use Pydantic `model_copy(...)`
   to force one file result to `row_count=1` and `error_count=1`.
3. Expect the rendered file line to end with `: 1 row, 1 error`.
4. Import and use `format_count_label(...)` from
   `fashion_radar.lint_formatting` in
   `render_manual_signal_directory_dry_run_table(...)` for only the per-file
   row and error-count phrases.
5. Run focused tests/checks, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is it appropriate to fix both `1 rows` and `1 errors` in the same per-file
   renderer line?
4. Is the renderer-only `model_copy(...)` test preferable to malformed CSV for
   this grammar check?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
