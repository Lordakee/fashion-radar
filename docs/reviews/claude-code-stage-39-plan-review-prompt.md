# Claude Code Stage 39 Plan Review Prompt

You are reviewing the Stage 39 shared read-only schema inspection plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Consolidate Stage 38 read-only SQLite schema inspection into one shared helper
while preserving existing CLI behavior.

## Proposed Technical Approach

- Add `src/fashion_radar/db/schema_inspection.py` with shared helpers for strict
  schema version parsing, signed CLI schema version parsing, read-only schema
  version reads, required table/column verification, and
  `DatabaseSchemaStatus` inspection.
- Move `create_readonly_sqlite_engine()` into `src/fashion_radar/db/engine.py`
  and keep `fashion_radar.trends.create_readonly_sqlite_engine` available.
- Replace duplicated schema verification helpers in `cli.py`,
  `imported_signals.py`, and `trends.py`.
- Preserve Stage 38 behavior: missing DB is OK for `doctor`, future schemas are
  reported before compatibility checks, future schemas do not get a `migrate-db`
  hint, old/missing schemas keep the explicit `migrate-db` hint, and read-only
  commands do not mutate SQLite.
- Preserve Stage 38 parser differences: imported-signal and trend verification
  reject signed strings, while CLI database status and candidate verification
  accept signed integer strings.
- Use ordered required-column inputs so table validation order is explicit while
  missing-table names remain sorted in error text.
- Keep all changes local: no connectors, scraping, crawling, browser
  automation, login/cookie/account/proxy/CAPTCHA/source-acquisition/platform
  API functionality, schedulers, watchers, monitors, dependency changes, or
  schema version changes.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-39-shared-readonly-schema-inspection-design.md`
- `docs/superpowers/plans/2026-06-14-stage-39-shared-readonly-schema-inspection-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 39 SHARED READONLY SCHEMA INSPECTION
```
