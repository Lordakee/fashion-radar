## Stage 331 Plan Review

Claude Code reviewed the Stage 331 plan before implementation.

### Critical

**C1 - Task 3 referenced the wrong render function and nonexistent helpers.**

The initial plan used `render_row_one_detail_page`,
`_edition_with_story(...)`, and `_story(...)`, none of which matched the
existing render-test helpers. The plan was updated to use the existing
`render_detail_html(...)`/`render_row_one_site(...)` patterns and current
`_edition()` fixtures.

**C2 - The combined skipped/empty extraction branch had to be replaced.**

The initial plan did not state clearly enough that the existing
`if result.skipped or not result.text:` branch in `articles.py` must be deleted
and replaced with separate reason-preserving branches. The plan was updated to
make the replacement explicit.

### Important

**I1 - Article-readiness integration needed explicit verification.**

Claude Code noted that `article_readiness.py` delegates its local article
payload through `row_one_local_article_site_metrics_payload()`. The plan was
updated to list it as a verified file and to cover the inherited payload keys in
tests without requiring a source change.

### Follow-Up

The plan was revised and re-reviewed in:

- `docs/reviews/claude-code-stage-331-plan-rereview.md`
- `docs/reviews/claude-code-stage-331-plan-rereview-2.md`

The final re-review found no Critical or Important findings and cleared the
plan for implementation.
