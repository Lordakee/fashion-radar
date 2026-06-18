# Stage 94 Dashboard Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/dashboard.md` so the dashboard
documentation keeps its local inspection, read-only trend, and local-security
boundaries.

## Scope

Modify:

- `tests/test_dashboard_docs.py`
- Stage 94 spec/plan/review artifacts

Do not modify:

- `docs/dashboard.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime dashboard tests

## Design

Create a standalone docs-only test file that reads `docs/dashboard.md`,
normalizes whitespace/case, and asserts stable phrases for:

- optional Streamlit app for inspecting local Fashion Radar state
- reading local SQLite/report state
- not collecting sources, running matching, generating reports, or making
  network requests on import/refresh
- Trend Deltas using existing local SQLite state and local config, not external
  services
- trend reads verifying schema read-only and not initializing, migrating, or
  writing trend tables
- local-only dashboard binding and lack of authentication
- no scraping, browser automation, platform APIs, account work, or cookie work
  in imported entity evidence dashboard-adjacent wording

The test should not import Streamlit, dashboard modules, application modules, or
SQLite helpers.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
uv --no-config run --frozen pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q
uv --no-config run --frozen ruff check tests/test_dashboard_docs.py
uv --no-config run --frozen ruff format --check tests/test_dashboard_docs.py
```

## Boundaries

This stage is test-only. It does not add dashboard behavior, Streamlit behavior,
runtime imports, source collection, entity matching, report generation, network
requests, trend writes, schema changes, authentication, host binding changes,
source acquisition, platform coverage, demand proof, ranking, scraping,
connectors, browser automation, platform APIs, account/cookie handling, new
linter restrictions, or compliance-review product features.
