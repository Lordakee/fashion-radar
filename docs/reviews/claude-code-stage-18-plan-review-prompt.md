# Claude Code Stage 18 Plan Review Prompt

You are reviewing the Stage 18 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Goal

Stage 18 proposes a local, read-only directory import dry-run command:

```bash
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run
fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --dry-run
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run --output-format json
```

The command validates batches of already-sanitized, user-provided local
CSV/JSON signal files using the same importer model as `import-signals
--dry-run`. Stage 18 intentionally does **not** implement batch import; it only
adds a directory dry-run bridge after `community-signal-lint-dir`.

## Architecture And Tech Stack

- Python 3.11+, Typer, Pydantic v2, pytest, ruff, uv.
- No new dependencies and no lockfile changes.
- Extend `src/fashion_radar/importers/manual_signals.py` with:
  - directory dry-run result models;
  - `dry_run_manual_signal_directory(...)`;
  - `render_manual_signal_directory_dry_run_table(...)`;
  - a private single-file wrapper around existing `load_manual_signal_rows()`.
- Add a Typer command in `src/fashion_radar/cli.py`:
  - `import-signals-dir DIRECTORY --format csv|json --pattern TEXT --dry-run`
  - optional `--output-format table|json`
  - optional `--source-name`, defaulting to `Manual Import`
- The CLI must require `--dry-run` in Stage 18. Without it, it should exit
  non-zero with a stable message before reading files.
- The command must not include `--data-dir`, `--config-dir`, `--reports-dir`, or
  `--imported-at` in Stage 18.
- Directory enumeration must be non-recursive:
  - `directory.iterdir()`
  - `path.is_file()`
  - `fnmatch.fnmatch(path.name, pattern)`
  - deterministic `sorted(paths, key=lambda path: str(path))`
- No `Path.glob()` or `rglob()` for matching.

## Scope Guard

Stage 18 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, MCP platform
  scraping servers, platform APIs, account automation, login cookies, browser
  profiles, proxies, CAPTCHA/rate-limit/access-control bypass, or source export
  acquisition instructions;
- collectors, source types, background jobs, watch folders, schedulers, batch
  import, SQLite writes, migrations, matching/scoring/report changes, dashboard
  changes, or digest changes;
- product-facing compliance/audit/approval/policy workflow features.

## Documents To Review

- `docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md`
- `docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md`

These are currently uncommitted planning artifacts. Production code has not been
implemented yet.

## Review Request

Please evaluate whether the design and implementation plan are ready for
implementation. Focus on:

1. Does the API naming correctly preserve the distinction between strict
   `community-signal-lint-dir` and importer-model dry-run validation?
2. Is requiring `--dry-run` in Stage 18 coherent and safely tested?
3. Is `--format` for input format and `--output-format` for diagnostics output
   clear and compatible with existing `import-signals` behavior?
4. Does the plan avoid opening SQLite, creating data/config/report directories,
   importing rows, or estimating `items_added`?
5. Does the plan preserve non-recursive direct-child matching and deterministic
   ordering?
6. Are directory-level error messages stable enough?
7. Do planned tests cover module behavior, CLI help/output/failure, no-artifact
   behavior, no-`--dry-run` behavior, invalid/no-match/unreadable directory, bad
   file plus clean file, JSON shape, and docs boundaries?
8. Do docs avoid source acquisition, scraping, platform coverage, authorization
   verification, compliance/audit, and policy workflow product features?
9. Is anything missing before implementation begins?

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 18 implementation`
- `Not approved`

Do not modify files.
