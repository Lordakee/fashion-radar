# Claude Code Stage 18 Code Review Prompt

You are reviewing `/home/ubuntu/fashion-radar` in read-only mode. Do not edit
files. Use maximum reasoning.

## Goal

Stage 18 adds a local, read-only directory import dry-run command:

```bash
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run
fashion-radar import-signals-dir ./exports --format json --pattern "*.json" --dry-run
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --dry-run --output-format json
```

The command validates batches of user-provided local CSV/JSON signal files using
the same importer model as `import-signals --dry-run`. It intentionally does not
implement batch import.

## Architecture And Tech Stack

- Python 3.11+, Typer, Pydantic v2, pytest, ruff, uv.
- No new dependencies and no lockfile changes.
- `src/fashion_radar/importers/manual_signals.py` adds:
  - directory dry-run Pydantic result models;
  - `dry_run_manual_signal_directory(...)`;
  - `render_manual_signal_directory_dry_run_table(...)`;
  - a private `_dry_run_manual_signal_file(...)` wrapper around existing
    `load_manual_signal_rows()`.
- `src/fashion_radar/cli.py` adds:
  - `import-signals-dir DIRECTORY --format csv|json --pattern TEXT --dry-run`;
  - `--output-format table|json`;
  - `--source-name`, defaulting to `Manual Import`.
- The CLI requires `--dry-run` in Stage 18. Without it, it exits non-zero before
  reading files.
- The command has no `--data-dir`, `--config-dir`, `--reports-dir`, or
  `--imported-at`.
- Directory matching must be non-recursive:
  - `directory.iterdir()`;
  - `path.is_file()`;
  - `fnmatch.fnmatch(path.name, pattern)`;
  - deterministic `sorted(paths, key=lambda path: str(path))`.

## Scope Guard

This stage must remain local-only and read-only. It must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, MCP platform
  scraping servers, platform APIs, account automation, login cookies, browser
  profiles, proxies, CAPTCHA/rate-limit/access-control bypass, or source export
  acquisition instructions;
- collectors, source types, background jobs, watch folders, schedulers, batch
  import, SQLite writes, migrations, matching/scoring/report changes, dashboard
  changes, or digest changes;
- product-facing compliance/audit/approval/policy workflow features.

## Files To Review

Production:

- `src/fashion_radar/importers/manual_signals.py`
- `src/fashion_radar/cli.py`

Tests:

- `tests/test_manual_signal_import.py`
- `tests/test_cli.py`

Docs:

- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `README.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`

Planning/review artifacts:

- `docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md`
- `docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md`
- `docs/reviews/claude-code-stage-18-plan-review*.md`
- this prompt and the resulting review file.

## Verification Already Run

```text
.venv/bin/python -m pytest tests/test_manual_signal_import.py -q -k "directory_dry_run"
10 passed, 29 deselected

.venv/bin/python -m pytest tests/test_cli.py -q -k import_signals_dir
9 passed, 80 deselected

.venv/bin/python -m pytest tests/test_manual_signal_import.py tests/test_cli.py -q -k "directory_dry_run or import_signals_dir"
19 passed, 109 deselected

git diff --check
exit 0

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
78 files already formatted

.venv/bin/python -m pytest -q
385 passed

codegraph status
Files indexed: 92; Total nodes: 1499; Total edges: 3991
```

Docs boundary scan was also run:

```bash
rg -n "import-signals-dir|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|exports|ranking|demand proof|compliance|audit|authorization" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md CHANGELOG.md
```

Hits should be reviewed as command examples or explicit negative/boundary
contexts only.

## Review Request

Please review the current working-tree diff, not just committed code:

```bash
git diff -- src/fashion_radar/importers/manual_signals.py src/fashion_radar/cli.py tests/test_manual_signal_import.py tests/test_cli.py docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md README.md docs/architecture.md docs/source-boundaries.md CHANGELOG.md docs/superpowers/specs/2026-06-12-stage-18-import-signals-directory-dry-run-design.md docs/superpowers/plans/2026-06-12-stage-18-import-signals-directory-dry-run-plan.md
```

Find issues by severity:

- Critical: correctness, non-local side effects, security/secrets, scope
  violations, SQLite writes, or broken command behavior.
- Important: missing required tests, unstable JSON shape, wrong exit behavior,
  recursive matching, docs that could mislead users, deterministic ordering
  issues, or no-artifact gaps.
- Minor: wording, maintainability, or polish.

Explicitly answer:

1. Does the implementation require `--dry-run` before reading files?
2. Does it avoid SQLite, data/config/report directory creation, import writes,
   collectors, reports, dashboard, matching, scoring, and digest behavior?
3. Does it preserve non-recursive direct-child matching and deterministic order?
4. Are directory-level messages stable for missing/non-directory, unreadable,
   and no-match cases?
5. Does JSON output preserve the planned stable shape?
6. Do tests cover success, file failure, invalid directory, no-match, unreadable
   directory, no-`--dry-run`, non-recursive matching, no glob/rglob, and
   no-artifact behavior?
7. Do docs keep the distinction between strict `community-signal-lint-dir` and
   importer-model `import-signals-dir --dry-run` clear?
8. Do docs avoid scraping/platform/source-acquisition/account automation,
   authorization verification, compliance/audit, or policy workflow product
   features?
9. Is Stage 18 ready for release checks, commit, and push after fixing any
   Critical/Important findings?

Please return approval status plus findings. Do not modify files.
