# Stage 94 Plan Re-Review Prompt

Re-review the Stage 94 design and implementation plan in
`/home/ubuntu/fashion-radar` after addressing the prior Critical finding.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-94-dashboard-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-94-dashboard-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-94-plan-review.md`
- Current `docs/dashboard.md`

## Prior Critical Finding

The first plan review found that the planned test asserted this phrase, which
does not exist in `docs/dashboard.md`:

```text
do not initialize schema, migrate a database, create trend tables
```

The plan has been changed to remove that invalid phrase and keep only existing
phrases, including:

```text
trend reads verify schema read-only
do not initialize, migrate, or write trend tables
```

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

1. Is the prior Critical finding resolved?
2. Are all remaining proposed docs assertions present in current
   `docs/dashboard.md`?
3. Are there any remaining Critical or Important blockers before
   implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
