# Claude Code Stage 345 Code Review Prompt

You are reviewing the current uncommitted Stage 345 implementation in
`/home/ubuntu/fashion-radar`. Use maximum reasoning. Operate read-only. Do not
edit files.

## Goal

Stage 345 adds a generated-site-only Saved Article Daily Summary section inside
`articles/index.html`.

## Files To Review

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-08-stage-345-saved-article-daily-summary-design.md`
- `docs/superpowers/plans/2026-07-08-stage-345-saved-article-daily-summary-plan.md`

## Review Questions

1. Does the implementation stay generated-site-only?
2. Does it avoid duplicating Theme Digest, Reference Atlas, Evidence Board,
   Content Organization, and Organization Coverage Matrix content?
3. Are article-library section anchors scoped to `articles/index.html` only?
4. Are safe-link, empty-state, contract, and artifact guards sufficient?
5. Are there any Critical or Important issues that should block commit?

Return a concise severity-labeled review.
