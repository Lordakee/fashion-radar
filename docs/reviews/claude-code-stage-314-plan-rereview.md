# Claude Code Stage 314 Plan Rereview

## Critical

None. All previous Critical findings are resolved.

## Important

None. All four previous Important findings are resolved:

1. **`_render_status_site_with_local_article` ambiguity** — Resolved. Task 3
   Step 1 now carries an inline comment explaining that the plan uses the
   existing helper in `tests/test_row_one_cli.py`.
2. **Wrong workflow test name** — Resolved. Task 5 Step 1 and the run command
   now use `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`.
3. **Missing `items=[]`** — Resolved. The `_write_article` fixture in Task 1
   Step 2 now explicitly passes `items=[]` to `RowOneLocalArticleContentSection`.
4. **Task 5 pre-check wording** — Resolved. The plan now explicitly says to run
   the workflow test before deciding whether render wiring needs to change.

## Minor

- **Hardcoded assertion values in Task 3 not verified against the helper.** The
  test asserts `paragraph_count: 2` and `organized_section_count: 2`, but the
  plan does not show the helper implementation. The implementor should confirm
  those values match before committing the test.

- **Stale sidecar counting** (carried over). `site_metrics.py` counts all
  `data/articles/*.json`, not only current-edition ones. The docs note about
  `--latest-only` addresses this at the docs layer; it is not a blocker.

- **Docs test exact phrase sensitivity** (carried over). The supplied paragraph
  must be copied verbatim into both Markdown files.

## Verdict

All previous Critical/Important findings are resolved. The plan is ready to
implement. No new Critical or Important issues were introduced.
