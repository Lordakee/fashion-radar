# Claude Code Stage 20 Plan Review Prompt

You are reviewing the Stage 20 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Goal

Stage 20 proposes a local read-only command:

```bash
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --lookback-days 1
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --source-name "Community Tool Export"
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --unmatched-only
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z --format json
```

The command reviews rows already stored in local SQLite with
`source_type == "manual_import"`, so users can inspect imported local signals
after `import-signals` or `import-signals-dir` and before matching, candidates,
trends, reports, or dashboard review.

## Architecture And Tech Stack

- Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, SQLite read-only URI mode,
  pytest, ruff, uv.
- No new dependencies and no lockfile changes.
- Create `src/fashion_radar/imported_signals.py` with:
  - `ImportedSignalMatch`;
  - `ImportedSignalItem`;
  - `ImportedSignalsReview`;
  - `query_imported_signals(...)`;
  - `verify_imported_signals_schema(...)`;
  - `render_imported_signals_table(...)`.
- Add a Typer command in `src/fashion_radar/cli.py`:
  - `imported-signals --data-dir PATH`;
  - required `--as-of` with command-specific review timestamp help text;
  - `--lookback-days`, default `7`, min `1`;
  - `--limit`, default `50`, min `0`;
  - optional exact `--source-name` filter;
  - `--unmatched-only`;
  - `--format table|json`.
- Missing database should return an empty result and exit zero without creating
  `--data-dir`.
- Invalid `--as-of` should exit non-zero before opening SQLite or creating
  directories.
- Existing database should be opened read-only.
- Invalid schema should exit non-zero without traceback.
- Schema verification should check required tables, `schema_metadata.version`,
  and the `items` / `item_entities` columns used by this command.
- The query must only return `items.source_type == "manual_import"` rows.
- The query must filter `window_start < collected_at <= as_of`.
- Match status must be read from existing `item_entities` rows only and must
  not run or trigger matching.
- Table output should sanitize cell values deterministically by replacing
  carriage returns/newlines with spaces and replacing `|` with `/`.

## Scope Guard

Stage 20 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, MCP platform
  scraping servers, platform APIs, account automation, login cookies, browser
  profiles, proxies, CAPTCHA/rate-limit/access-control bypass, or source export
  acquisition instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, import behavior changes, DB migrations,
  matching/scoring/report changes, dashboard writes, or digest changes;
- product-facing approval, audit, policy checklist, authorization verification,
  or legal-review workflow features.

## Documents To Review

- `docs/superpowers/specs/2026-06-13-stage-20-imported-signals-review-design.md`
- `docs/superpowers/plans/2026-06-13-stage-20-imported-signals-review-plan.md`

These are currently uncommitted planning artifacts. Stage 20 production code
has not been implemented yet.

## Review Request

Please evaluate whether the design and implementation plan are ready for
implementation. Focus on:

1. Is `imported-signals` a clear and compatible CLI name?
2. Is required `--as-of` plus `--lookback-days` compatible with existing
   read-only command style?
3. Is the query shape sufficient for local post-import review without becoming
   a report/scoring feature?
4. Does `--unmatched-only` add useful review value without triggering matching
   or scoring?
5. Does the design preserve read-only behavior for missing and existing
   databases?
6. Does the plan avoid creating `--data-dir` on missing DB and invalid
   `--as-of`?
7. Is schema verification sufficient, including `schema_metadata.version` and
   command-required columns?
8. Are table and JSON output contracts deterministic enough?
9. Do tests cover manual-only filtering, exact time-window boundaries,
   ordering, limit, source-name filter, unmatched-only, match status without
   count inflation, missing database no-artifact behavior, invalid as-of,
   invalid schema, CLI help, table, JSON key order, private/internal field
   exclusion, direct read-only helper usage, no query/database access on invalid
   `--as-of`, table cell sanitization, and read-only unchanged existing
   databases?
10. Do docs avoid source acquisition, scraping, platform coverage,
   authorization verification, approval/audit/policy workflow features, and
   market-wide ranking claims?
11. Is anything missing before implementation begins?

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 20 implementation`
- `Not approved`

Do not modify files.
