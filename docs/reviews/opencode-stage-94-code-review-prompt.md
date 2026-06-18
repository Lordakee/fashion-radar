# Stage 94 Code Review Prompt

Review the Stage 94 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 94 adds `tests/test_dashboard_docs.py`, a standalone docs drift guard for
`docs/dashboard.md`. It asserts local inspection, read-only trend, local
security, and no scraping/browser/platform API/account/cookie boundaries.

## Files To Review

- `tests/test_dashboard_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-94-dashboard-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-94-dashboard-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-94-plan-review-prompt.md`
- `docs/reviews/opencode-stage-94-plan-review.md`
- `docs/reviews/opencode-stage-94-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-94-plan-rereview.md`

## Scope Constraints

Allowed changes:

- `tests/test_dashboard_docs.py`
- Stage 94 review artifacts

Disallowed changes:

- `docs/dashboard.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime dashboard tests

Do not propose adding dashboard behavior, Streamlit behavior, runtime imports,
source collection, entity matching, report generation, network requests, trend
writes, schema changes, authentication, host binding changes, source
acquisition, platform coverage, demand proof, ranking, scraping, connectors,
browser automation, platform APIs, account/cookie handling, new linter
restrictions, or compliance-review product features.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
uv --no-config run --frozen pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q
uv --no-config run --frozen ruff check tests/test_dashboard_docs.py
uv --no-config run --frozen ruff format --check tests/test_dashboard_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 94 reviewed/re-reviewed plan and
   scope?
2. Are the docs assertions present, stable enough, and limited to dashboard
   boundaries?
3. Is the new standalone test independent from runtime dashboard tests and
   broad CLI docs tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
