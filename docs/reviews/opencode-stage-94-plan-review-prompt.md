# Stage 94 Plan Review Prompt

Review the Stage 94 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-94-dashboard-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-94-dashboard-docs-boundary-plan.md`
- Current `docs/dashboard.md`
- Current `tests/test_dashboard.py`
- Current `tests/test_cli_docs.py`

## Intended Goal

Add a standalone docs drift guard for `docs/dashboard.md` that pins local
inspection, read-only trend, local-security, and no-scraping/browser/platform
API/account/cookie boundaries without changing docs or runtime behavior.

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

## Review Questions

1. Are the proposed docs assertions present in current `docs/dashboard.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 91, 92, and 93?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
