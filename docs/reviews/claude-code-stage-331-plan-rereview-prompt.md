# Claude Code Stage 331 Plan Re-Review Prompt

You are re-reviewing the Stage 331 plan in `/home/ubuntu/fashion-radar`.

Model/effort requirement from the user: use max reasoning effort.

## Context

Initial plan review found:

- C1: Task 3 render test used nonexistent `render_row_one_detail_page`,
  `_edition_with_story`, and `_story` helpers.
- C2: Task 1 builder implementation did not explicitly delete/replace the
  existing combined `if result.skipped or not result.text` branch.
- The first review output was truncated after starting an Important finding, so
  do a fresh complete review of the updated plan.

The plan has been updated to:

- Use `_edition()`, `edition.stories[0]`, and `render_detail_html(...)`.
- Explicitly delete and replace the combined skipped/empty-text branch.
- List `src/fashion_radar/row_one/article_readiness.py` as a verify-only file
  because its payload delegates local article metrics payload generation.

## Files To Review

- `docs/superpowers/specs/2026-07-07-stage-331-row-one-local-article-provenance-design.md`
- `docs/superpowers/plans/2026-07-07-stage-331-row-one-local-article-provenance-plan.md`

Use existing code context as needed:

- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/articles.py`
- `src/fashion_radar/row_one/site_metrics.py`
- `src/fashion_radar/row_one/article_readiness.py`
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/cli.py`
- relevant `tests/test_row_one_*.py`

## Review Focus

Findings first, ordered by severity. Look for any remaining Critical/Important
plan issue that would break implementation, tests, contracts, final commit, or
release verification.

Do not propose compliance review product functionality.

## Output Format

- Critical
- Important
- Medium
- Minor
- Verdict

Keep the review concise but complete.
