# Claude Code Stage 22 Plan Review Prompt

You are reviewing the Stage 22 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Goal

Stage 22 proposes a new local read-only command:

```bash
fashion-radar imported-signals-summary --data-dir ./data
fashion-radar imported-signals-summary --data-dir ./data --format json
```

The command summarizes retained `manual_import` rows already stored in local
SQLite by stored `source_name` label. It reports retained row counts,
item-level stored match presence counts, and first/latest collected timestamps
per source label.

## Architecture And Tech Stack

- Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, SQLite read-only URI mode,
  pytest, ruff, uv.
- No new dependencies and no lockfile changes.
- Extend `src/fashion_radar/imported_signals.py` with source-summary models,
  query helper, and table renderer.
- Add a thin Typer command in `src/fashion_radar/cli.py`.
- Reuse existing imported-signals schema verification and read-only SQLite
  engine behavior.
- Missing databases return empty summaries without creating `--data-dir`.
- Existing databases are read-only.
- No `--as-of`, lookback window, or limit is proposed; the command summarizes
  the currently retained local `manual_import` rows in the database.

## Scope Guard

Stage 22 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, platform APIs,
  account automation, login cookies, browser profiles, proxy pools, CAPTCHA
  bypass, rate-limit bypass, source acquisition, or platform export
  instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, import behavior changes, database migrations, matching
  changes, scoring changes, report generation changes, dashboard writes, or
  digest changes;
- source health, source quality, source coverage, source ranking, top-source,
  product-facing approval, audit, policy checklist, authorization
  verification, or legal-review workflows.

Wording should remain bounded to retained local rows, imported local signals,
local source-name labels, and stored match presence derived from
`item_entities`. It should not imply platform coverage, market-wide ranking,
verified demand, real-time monitoring, source quality, source health, or source
acquisition.

## Documents To Review

- `docs/superpowers/specs/2026-06-13-stage-22-imported-source-summary-design.md`
- `docs/superpowers/plans/2026-06-13-stage-22-imported-source-summary-plan.md`

These are currently planning artifacts. Stage 22 production code has not been
implemented yet.

## Review Request

Please evaluate whether the design and implementation plan are ready for
implementation. Focus on:

1. Is `imported-signals-summary` a clear CLI name that stays inside the
   imported-signals review boundary?
2. Is the command sufficiently distinct from `imported-signals` without
   becoming source health, source quality, source coverage, or ranking?
3. Is it appropriate to summarize all currently retained local `manual_import`
   rows without `--as-of`, lookback, or limit?
4. Does the proposed output avoid exposing row-level URLs, titles, summaries,
   raw import rows, imported source file paths, and internal match details,
   while explicitly allowing the existing-style top-level local `database`
   path?
5. Are counts well defined as current retained local row counts grouped by
   stored source-name label?
6. Does item-level stored match presence avoid inflating counts when one item
   has multiple entity matches?
7. Is exact stored source-name ascending sorting deterministic, clear about
   SQLite stored-text behavior, and free of ranking implications?
8. Does the design preserve read-only behavior for missing and existing
   databases?
9. Does the plan avoid DB migrations, matching/scoring changes, reports,
   dashboard writes, schedulers, watch folders, collectors, source-health
   behavior, source-quality behavior, and platform/API integrations?
10. Are tests sufficient for missing DB, invalid format, manual-only filtering,
    grouping, match-count inflation, sorting, schema errors, table/JSON output,
    no mutation, special-character paths, and docs boundaries?
11. Are verification commands adequate before code review, release checks,
    commit, and push?
12. Is anything missing before implementation begins?

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 22 implementation`
- `Not approved`

Do not modify files.
