# Claude Code Stage 38 Plan Review Prompt

You are reviewing the Stage 38 local schema maintenance plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Add a local `migrate-db` command and read-only `doctor` schema status so users
can inspect and upgrade the SQLite schema explicitly.

## Proposed Technical Approach

- Add `migrate-db --data-dir ...` that calls `create_sqlite_engine()` and
  `initialize_schema()` for the local SQLite database, then prints the resulting
  schema version.
- Extend `doctor` with a read-only database schema status line. Missing database
  is OK; current schema is OK; old/future/invalid schema exits non-zero with a
  user-facing message.
- Add read-only schema mismatch hints that point to
  `fashion-radar migrate-db --data-dir ...` for older/missing schemas.
- Keep future schema errors distinct so they do not imply `migrate-db` can
  downgrade a newer database.
- Add focused tests proving `doctor` is non-mutating and `migrate-db` does not
  collect, import, match, score, report, package digests, schedule, watch, or
  touch external sources.
- Keep all changes local: no connectors, scraping, crawling, browser
  automation, login/cookie/account/proxy/CAPTCHA/source-acquisition/platform
  API functionality.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-38-local-schema-maintenance-design.md`
- `docs/superpowers/plans/2026-06-14-stage-38-local-schema-maintenance-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 38 LOCAL SCHEMA MAINTENANCE
```
