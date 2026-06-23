# Stage 167 Code Review Prompt

Review the Stage 167 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 167 Code Review
```

Objective:

Fix singular `1 error` wording in the human-readable
`community-handoff-check-dir` table for lint and import dry-run summaries.

Changed files:

- `src/fashion_radar/community_handoff_check.py`
  - Imports `format_count_label`.
  - Uses it for the lint and import dry-run `error_count` table phrases.
- `tests/test_community_handoff_check.py`
  - Adds a renderer-only RED/GREEN test that forces both nested error counts to
    `1` with `model_copy(...)` and expects `1 error`.
- `docs/superpowers/specs/2026-06-23-stage-167-community-handoff-check-error-label-design.md`
- `docs/superpowers/plans/2026-06-23-stage-167-community-handoff-check-error-label-plan.md`
- `docs/reviews/opencode-stage-167-plan-review-prompt.md`
- `docs/reviews/opencode-stage-167-plan-review.md`

Scope boundaries:

- Human-readable `community-handoff-check-dir` table wording only.
- No changes to `check_community_handoff_directory(...)`.
- No model, JSON, CLI command flow, lint, dry-run, candidate preview,
  strict-mode, or readiness semantics changes.
- No changes to `files`, `rows`, or `candidates` wording.
- No changes to `manual_signals.py`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, login, cookies, monitoring, scheduling, demand proof, ranking,
  coverage verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-167-plan-review.md`
  - No critical findings.
  - No important findings.
  - Three minor findings only, none blocking.

RED/GREEN evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q`
  - Result before implementation: 1 failed. The lint line ended with
    `, 1 errors`.
- GREEN:
  - Same focused test.
  - Result after implementation: 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  - Result: 7 passed.
- `uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py`
  - Result: 2 files already formatted.

Review questions:

1. Does the implementation meet the Stage 167 objective?
2. Is the test properly renderer-scoped and not coupled to malformed CSV
   internals?
3. Is the `format_count_label(...)` reuse safe and cycle-free?
4. Did any out-of-scope behavior or wording change slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
