# OpenCode Stage 345 Code Review Prompt

Review `/home/ubuntu/fashion-radar` in read-only mode.

Use model `zhipuai-coding-plan/glm-5.2` with max reasoning if available.

## Goal

Stage 345 adds a generated-site-only Saved Article Daily Summary section inside
`articles/index.html`.

## Review Scope

Review the current uncommitted diff, especially:

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- Stage 345 design, plan, and review artifacts

## Review Questions

1. Does the code preserve generated-site-only boundaries?
2. Does the daily summary avoid duplicating downstream saved-article modules?
3. Are section anchors scoped to the article-library page only?
4. Are safe-link, empty-state, contract, and artifact guards sufficient?
5. Are there any Critical or Important issues?

Return a concise severity-labeled review.
