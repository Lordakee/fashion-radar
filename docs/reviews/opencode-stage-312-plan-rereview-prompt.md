# opencode Stage 312 Plan Rereview Prompt

You are the fallback plan rereviewer for `/home/ubuntu/fashion-radar` on branch
`main`.

Claude Code returned a server-side 524 timeout, so opencode is the fallback
reviewer. The first opencode plan review found three Important issues:

1. The escaping render test mutated `story.headline` directly.
2. Metrics-vs-capped-grid semantics were not explicit.
3. CSS selector test location was unspecified.

The design and plan have been updated:

- Escaping test now uses `model_copy(update={...})` and replaces
  `edition.stories`.
- Design says metrics are edition-level corpus totals while the read queue is
  capped at four cards.
- Builder test asserts `article_count == 6` and `len(coverage.items) == 4`.
- CSS selector coverage is assigned to a dedicated
  `test_row_one_css_includes_saved_article_coverage_styles` test.

Review the pasted Stage 312 design and plan only. Do not run tools and do not
inspect additional files.

## Rereview Tasks

1. Confirm whether the three Important findings are fixed.
2. Check whether any new Critical or Important issue was introduced by the
   revisions.
3. If no Critical or Important findings remain, say so explicitly.
4. Keep the whole response under 80 lines.
