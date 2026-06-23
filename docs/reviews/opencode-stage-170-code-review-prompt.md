# Stage 170 Code Review Prompt

Review the Stage 170 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 170 Code Review

Objective:

Fix singular `1 row` wording in human-readable `community-signal-lint-dir`
per-file lines.

Changed files:

- `src/fashion_radar/community_signals.py`
  - Imports `format_count_label`.
  - Uses it only in `render_community_signal_directory_lint_table(...)` for the
    per-file `file.row_count` phrase.
- `tests/test_community_signal_lint.py`
  - Tightens the existing renderer test so a synthetic one-row per-file result
    must render `- exports/signals.csv: 1 row, 0 import-ready, ...`.
- `docs/community-signal-quality.md`
  - Syncs the example output from `1 rows` to `1 row`.
- Stage 170 spec, plan, plan-review prompt, and plan-review artifact.

Scope boundaries:

- Human-readable `community-signal-lint-dir` per-file row-count wording only.
- No changes to `lint_community_signal_directory(...)`.
- No changes to `lint_community_signal_file(...)`.
- No changes to structured models, JSON output, CLI command flow, field counts,
  source counts, platform counts, finding ordering, finding messages, or
  finding-count grammar.
- No changes to top-level summary lines such as `Rows: ... total, ...
  import-ready`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking, coverage
  verification, or compliance-review product features.

Plan review history:

- First plan review found one important issue: a non-existent focused pytest
  node id in the spec/plan.
- The spec and plan were corrected to use
  `tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples`.
- The second plan review in `docs/reviews/opencode-stage-170-plan-review.md`
  has no critical findings and no important findings.

RED/GREEN evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q`
  - Result before implementation: 1 failed. The file line rendered
    `- exports/signals.csv: 1 rows, 0 import-ready, 1 error, 1 warning, 1 info`.
- GREEN:
  - Same focused command after implementation.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_signal_lint.py -q`
  - Result: 90 passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
  - Result: 1 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
  - Result: 2 files already formatted.

Review questions:

1. Does the implementation meet the Stage 170 objective?
2. Is the test properly renderer-scoped and was the RED/GREEN cycle meaningful?
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
