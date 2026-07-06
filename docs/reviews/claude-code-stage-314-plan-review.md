# Claude Code Stage 314 Plan Review

## Critical

**`_render_status_site_with_local_article` helper is referenced but never
defined.**

Task 3 Step 1 (`test_row_one_cli.py`) calls
`_render_status_site_with_local_article(tmp_path)` inside
`test_row_one_status_json_includes_local_article_metrics`, but Claude Code did
not find the function in the plan or existing test file. This would be a
`NameError` if the helper were absent.

Resolution note: the helper does exist in `tests/test_row_one_cli.py`. The plan
still needs to name it as an existing helper explicitly to avoid ambiguity.

## Important

**Wrong test name referenced in Task 5.**

The plan instructs the implementor to modify
`test_write_row_one_site_files_writes_local_article_sidecar_without_mutating_summary`.
The actual function in `tests/test_workflows.py` is named
`test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`.

**`RowOneLocalArticleContentSection` is constructed without `items` in the Task
1 Step 2 fixture.**

The `_write_article` helper calls `RowOneLocalArticleContentSection(...)` with
no `items` argument. Add `items=[]` so the fixture is explicit and safe.

**Task 5 needs an explicit pre-check.**

The existing workflow test already proves the sidecar and detail paragraph, but
not `id="local-article"` or homepage modules. The plan should state that the
implementor must run the strengthened test before deciding whether render
wiring changes are needed.

## Minor

**`site_metrics.py` counts all `data/articles/*.json` sidecars, not just
current-edition ones.**

`status_integrity` rejects stale sidecars for `row-one status`, but build or
preview metrics over a non-clean output dir could count leftovers. Consider a
docs note that `--latest-only` ensures counts reflect only the current build.

**The `isinstance(local_articles, dict)` guard in the status text path silently
suppresses missing output.**

Since this is diagnostic output, direct access to the computed payload is
clearer.

**Docs test exact phrase sensitivity.**

The docs test requires exact phrase strings in both Markdown files. Copy the
supplied paragraph exactly.

## Verdict

The spec is clean, correctly scoped to observability only, and the
`site_metrics.py` approach is technically sound and orthogonal to the existing
integrity validator. The implementation plan is feasible without network
access and does not touch any contract files. Fix the helper reference, test
name, fixture `items=[]`, and Task 5 pre-check wording before proceeding. No
boundary violations, new JSON artifacts, or contract drift found.
