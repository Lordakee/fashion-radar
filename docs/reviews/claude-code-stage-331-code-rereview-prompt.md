Re-review the current uncommitted Stage 331 changes in
`/home/ubuntu/fashion-radar` after fixes for the prior code review.

Prior Important findings:
1. Missing render test proving `body_source="skipped"` sidecars with no
   paragraphs do not render a detail-page `id="local-article"` section.
2. `uv.lock` mirror-registry churn is unrelated to Stage 331 and should be
   excluded from the commit.

Fixes applied:
- Added `test_render_row_one_detail_suppresses_skipped_local_article`.
- Updated docs wording from "no saved body" to "no publishable saved body".
- Updated the Stage 331 plan's final `git add` list to include
  `tests/test_row_one_cli.py` and omit unchanged `docs/first-run.md` /
  `tests/test_cli_docs.py`.
- `uv.lock` remains intentionally unstaged/uncommitted local mirror drift.

Please verify whether the prior Important findings are closed and whether any
new Critical or Important issue was introduced. Do not modify files. Report
Critical, Important, Minor findings with file/line references. If no
Critical/Important findings remain, say so explicitly.
