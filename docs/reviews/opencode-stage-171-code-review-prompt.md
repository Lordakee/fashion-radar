# Stage 171 Code Review Prompt

Review the Stage 171 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to the focused
commands listed below and return one final review body.
Start the response exactly with:

# Stage 171 Code Review

Objective:

Fix singular count-label wording in human-readable `community-handoff-check-dir`
summary lines.

Changed files:

- `src/fashion_radar/community_handoff_check.py`
  - Keeps `format_count_label(...)` reuse inside
    `render_community_handoff_directory_check_table(...)`.
  - Singularizes only the Lint summary `file/files` and
    `import-ready row/import-ready rows` labels.
  - Singularizes only the Candidate preview `candidate/candidates` and
    `row/rows` labels.
  - Singularizes only the Import dry-run `valid file/valid files` and
    `row/rows` labels.
- `tests/test_community_handoff_check.py`
  - Extends the existing renderer grammar test with synthetic one-count nested
    results and exact expected lines.
- Stage 171 spec, plan, plan-review prompt, and plan-review artifact.

Scope boundaries:

- Human-readable `community-handoff-check-dir` renderer summary count labels
  only.
- Preserve the Stage 167 singular error-count behavior.
- No changes to `check_community_handoff_directory(...)`.
- No changes to lint, candidate preview, or manual import dry-run logic.
- No changes to structured models, JSON output, CLI options, command flow,
  checks, strict-mode behavior, warnings, finding messages, or exit codes.
- No changes to historical stage design/plan/review artifacts that quote old
  output as prior context.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-171-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: test name drift, optional plural exact assertion, and
    deliberately inconsistent synthetic renderer fixture.

RED/GREEN evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q`
  - Result before implementation: 1 failed. The lint line rendered
    `Lint: 1 files, 1/1 import-ready rows, 1 error`.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  - Result: 7 passed.
- `uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_check_dir_table_output_is_summary_only -q`
  - Result: 1 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Initial result found one E501 line-too-long issue in the Candidate preview
    label expression. The implementation was adjusted to compute
    `candidate_preview_text` via local label variables.
  - Final result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: 2 files already formatted.

Review questions:

1. Does the implementation meet the Stage 171 objective?
2. Is the test properly renderer-scoped and was the RED/GREEN cycle meaningful?
3. Are the `format_count_label(...)` calls correct for singular and plural
   labels, especially the slash-prefixed phrases?
4. Did any out-of-scope behavior, JSON shape, check logic, exit behavior, or
   historical artifact change slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
