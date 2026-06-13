# Stage 21 Imported Signals Polish Design

## Goal

Tighten the Stage 20 `imported-signals` review command without expanding its
scope. Stage 21 clarifies table output semantics, adds missing CLI validation
regressions, and strengthens the SQLite read-only path regression tests.

The command remains a local-first review surface for retained
`manual_import` rows already stored in local SQLite. It does not collect
sources, fetch URLs, run matching, score signals, generate reports, monitor
directories, initialize or migrate databases, or write dashboard artifacts.

## Problem

Stage 20 shipped the core read-only review command and passed release checks.
Claude Code noted one minor ambiguity: the table summary line
`Matches: 1 matched, 1 unmatched` can be read as entity-match row counts, while
the implementation actually counts imported item rows that currently have at
least one `item_entities` row.

The current tests also cover direct helper validation for `lookback_days` and
`limit`, and Typer already declares `--lookback-days min=1` and `--limit min=0`.
However, the CLI layer does not yet have focused regressions proving invalid
CLI values fail before database/query access.

Finally, Stage 20 fixed SQLite URL handling for paths containing URI-special
characters. The imported-signals query has a direct helper test for those paths,
and the writable engine has a database test, but the full CLI path from
`--data-dir` to `fashion-radar.sqlite` and the read-only engine write rejection
are not both locked down.

## Recommended Approach

Use a narrow quality patch:

1. Change only the human-readable table summary label from `Matches:` to
   `Matched rows:`. Keep JSON field names (`matched_count`,
   `unmatched_count`) unchanged to avoid breaking the machine-readable
   contract.
2. Add CLI tests for invalid `--lookback-days 0`, invalid `--limit -1`, and
   invalid `--format xml`. These tests must confirm no traceback and no query
   call when validation fails.
3. Add CLI coverage for a `--data-dir` containing `? # & %`, proving the
   command can open the existing SQLite database through the complete CLI
   path.
4. Add a direct read-only SQLite engine regression proving a write fails when a
   database path contains URI-special characters.
5. Update documentation examples that show the table summary so readers see the
   clarified label.

This approach keeps Stage 21 small, test-first, and low-risk. It does not add
new CLI options, new models, new queries, or new dependencies.

## User-Facing Behavior

Only table output changes:

```text
Imported manual signals from local SQLite.
Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00
Rows: 2 shown, 3 total
Matched rows: 1 matched, 2 unmatched
Sources: Community Tool Export=2, Manual Import=1
```

When no rows match:

```text
Imported manual signals from local SQLite.
Window: 2026-06-05T12:00:00+00:00 < collected_at <= 2026-06-12T12:00:00+00:00
Rows: 0 shown, 0 total
Matched rows: 0 matched, 0 unmatched
Sources: none
No imported manual signals found.
```

JSON output remains unchanged.

## Architecture And Tech Stack

- Python 3.11+
- Typer for CLI parsing and validation
- Pydantic v2 for existing output models
- SQLAlchemy Core and SQLite read-only URI mode
- pytest for tests
- ruff for lint and format checks
- uv for dependency, lockfile, and package verification

No new runtime or development dependencies are required.

## Files

Modify:

- `src/fashion_radar/imported_signals.py`
- `tests/test_imported_signals.py`
- `tests/test_cli.py`
- `tests/test_db.py`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `README.md` if it contains table-output wording that mentions match-count
  semantics
- `CHANGELOG.md`

Create process artifacts:

- `docs/superpowers/specs/2026-06-13-stage-21-imported-signals-polish-design.md`
- `docs/superpowers/plans/2026-06-13-stage-21-imported-signals-polish-plan.md`
- `docs/reviews/claude-code-stage-21-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-21-plan-review.md`
- code review prompt/result files after implementation

## Testing Requirements

Module tests:

- empty table rendering uses `Matched rows: 0 matched, 0 unmatched`;
- populated table rendering uses `Matched rows: 1 matched, 1 unmatched`;
- the previous `Matches:` line no longer appears in rendered table output.

CLI tests:

- table output uses `Matched rows:` and no longer uses `Matches:`;
- `--lookback-days 0` exits non-zero, prints the relevant option name, has no
  traceback, does not create `--data-dir`, and does not call
  `query_imported_signals`;
- `--limit -1` exits non-zero, prints the relevant option name, has no
  traceback, does not create `--data-dir`, and does not call
  `query_imported_signals`;
- `--format xml` exits non-zero, prints the relevant option name, has no
  traceback, does not create `--data-dir`, and does not call
  `query_imported_signals`;
- a `--data-dir` path containing `? # & %` reads the existing SQLite database
  and returns the expected JSON counts.

Database tests:

- `create_readonly_sqlite_engine()` can open a SQLite file whose path contains
  `? # & %`;
- a write statement through that engine fails;
- the database still resolves to the intended file path.

Full verification must include:

```bash
pytest tests/test_imported_signals.py tests/test_cli.py tests/test_db.py -q -k "imported_signals or create_sqlite_engine_handles_uri_special_characters or readonly"
pytest -q
ruff check .
ruff format --check .
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage21
```

## Scope Guard

Stage 21 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, platform APIs,
  account automation, login cookies, browser profiles, proxy pools, CAPTCHA
  bypass, rate-limit bypass, source acquisition, or platform export
  instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, import behavior changes, database migrations, matching
  changes, scoring changes, report generation changes, dashboard writes, or
  digest changes;
- product-facing approval, audit, policy checklist, authorization
  verification, or legal-review workflows.

Wording must stay bounded to retained local rows, imported local signals, and
stored match presence derived from `item_entities`. It must not imply platform
coverage, market-wide ranking, verified demand, real-time monitoring, or source
acquisition.
