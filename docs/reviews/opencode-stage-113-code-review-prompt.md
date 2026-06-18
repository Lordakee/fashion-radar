# Stage 113 Code Review Prompt

Review the Stage 113 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 113 adds a runtime warning in the dashboard Candidate Signals tab when
the latest report snapshot predates the newest local collected item. It keeps
the stale-decision logic in `dashboard/app.py`, preserves `generated_at` report
metadata in `dashboard/queries.py`, and adds focused tests in
`tests/test_dashboard.py`, including the parse-error/no-extra-stale-warning
boundary.

## Files To Review

- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_dashboard.py`
- `docs/superpowers/specs/2026-06-19-stage-113-dashboard-candidate-stale-warning-design.md`
- `docs/superpowers/plans/2026-06-19-stage-113-dashboard-candidate-stale-warning-plan.md`
- `docs/reviews/opencode-stage-113-plan-review.md`
- `docs/reviews/opencode-stage-113-code-review-prompt.md`

## Review Focus

1. Does the runtime warning trigger only when the newest local collected item is
   newer than the latest report timestamp?
2. Does the implementation avoid string-based timestamp comparison and use
   normalized datetimes instead?
3. Does the change preserve existing Candidate Signals parse-error behavior and
   dataframe rendering?
4. Is the query-layer metadata extension minimal and appropriate?
5. Are there any release-blocking regressions or missing tests?

## Verification Already Run

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard.py -q
uv --no-config run --frozen ruff check src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_dashboard.py
uv --no-config run --frozen ruff format --check src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_dashboard.py
git diff --check
```

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
