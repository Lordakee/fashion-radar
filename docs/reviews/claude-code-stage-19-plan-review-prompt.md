# Claude Code Stage 19 Plan Review Prompt

You are reviewing the Stage 19 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Goal

Stage 19 proposes actual local directory import execution for the existing
`import-signals-dir` command:

```bash
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --data-dir ./data
fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --data-dir ./data --imported-at 2026-06-12T12:00:00Z
```

Stage 18 already added dry-run-only directory validation. Stage 19 keeps that
dry-run behavior and adds import execution when `--dry-run` is omitted.

## Architecture And Tech Stack

- Python 3.11+, Typer, Pydantic v2, SQLAlchemy through existing repository
  helpers, pytest, ruff, uv.
- No new dependencies and no lockfile changes.
- Extend `src/fashion_radar/importers/manual_signals.py` with:
  - a directory load result that carries the Stage 18 validation result and
    loaded `ManualSignalRow` objects;
  - a compact directory import result model;
  - a table renderer for successful directory imports.
- Update `dry_run_manual_signal_directory(...)` to reuse the new loader while
  preserving its Stage 18 JSON/table shape.
- Update `src/fashion_radar/cli.py` so:
  - `--dry-run` preserves Stage 18 behavior;
  - without `--dry-run`, the command validates every matched local file before
    opening SQLite or creating `--data-dir`;
  - validation errors print the same dry-run diagnostics and exit non-zero;
  - successful import uses existing `store_manual_signal_rows(...)`;
  - `--data-dir` and `--imported-at` match single-file `import-signals`
    semantics;
  - `--output-format table|json` works for dry-run diagnostics and import
    success summaries.
- Directory matching must remain non-recursive and deterministic using
  `directory.iterdir()`, `path.is_file()`, `fnmatch.fnmatch(path.name, pattern)`,
  and sorted path strings. No `Path.glob()` or `rglob()` for matching.

## Scope Guard

Stage 19 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, MCP platform
  scraping servers, platform APIs, account automation, login cookies, browser
  profiles, proxies, CAPTCHA/rate-limit/access-control bypass, or source export
  acquisition instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, DB migrations, matching/scoring/report changes, dashboard
  changes, or digest changes;
- product-facing approval, audit, policy checklist, authorization verification,
  or legal-review workflow features.

## Documents To Review

- `docs/superpowers/specs/2026-06-12-stage-19-import-signals-directory-execution-design.md`
- `docs/superpowers/plans/2026-06-12-stage-19-import-signals-directory-execution-plan.md`

These are currently uncommitted planning artifacts. Stage 19 production code
has not been implemented yet.

## Review Request

Please evaluate whether the design and implementation plan are ready for
implementation. Focus on:

1. Does the design preserve Stage 18 dry-run behavior and JSON shape?
2. Is the actual import path safe enough: validate all matched files before
   creating data directories or opening SQLite, and import nothing on validation
   errors?
3. Is reusing `store_manual_signal_rows(...)` consistent with single-file import
   behavior, including URL upsert semantics and `items_added`?
4. Are `--data-dir`, `--imported-at`, `--dry-run`, `--format`, and
   `--output-format` semantics clear and compatible with existing CLI style?
5. Does the plan preserve non-recursive direct-child matching and deterministic
   ordering?
6. Do planned tests cover module loader behavior, CLI help, CSV import, JSON
   import JSON output, duplicate URL upserts, validation failure no-import,
   no-artifact behavior, invalid `--imported-at`, retained dry-run behavior,
   no-match/unreadable/invalid directory, and docs boundaries?
7. Do docs avoid source acquisition, scraping, platform coverage, authorization
   verification, approval/audit/policy workflow features, and market-wide
   ranking claims?
8. Is anything missing before implementation begins?

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 19 implementation`
- `Not approved`

Do not modify files.
