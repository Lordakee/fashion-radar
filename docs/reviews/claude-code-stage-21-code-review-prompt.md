# Claude Code Stage 21 Code Review Prompt

You are reviewing Stage 21 for `/home/ubuntu/fashion-radar` in read-only mode.
Do not edit files. Use maximum reasoning.

## Goal

Stage 21 clarifies `imported-signals` table semantics and adds CLI/read-only
SQLite regressions without expanding scope.

## Implemented Changes

- `src/fashion_radar/imported_signals.py`
  - changed the human-readable table summary label from `Matches:` to
    `Matched rows:`;
  - did not change the `ImportedSignalsReview` model or JSON field names.
- `tests/test_imported_signals.py`
  - updated table renderer expectations for empty and populated output;
  - asserts the old `Matches:` prefix is absent.
- `tests/test_cli.py`
  - updated table-output expectation;
  - added invalid `--lookback-days 0`, `--limit -1`, and `--format xml`
    validation regressions that monkeypatch `query_imported_signals` to prove
    invalid CLI values fail before query/database access;
  - added full CLI coverage for a `--data-dir` whose final directory name
    contains `? # & %`.
- `tests/test_db.py`
  - added direct read-only SQLite engine coverage for a path containing
    `? # & %`;
  - proves reads succeed and writes fail through the read-only engine.
- `CHANGELOG.md`
  - added a narrow Stage 21 polish bullet.
- Stage 21 process docs were added under `docs/superpowers/` and
  `docs/reviews/`.

## Verification Already Run

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py tests/test_db.py -q -k "imported_signals or create_sqlite_engine_handles_uri_special_characters or readonly"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

The focused pytest run reported `35 passed, 110 deselected`. Ruff and
`git diff --check` passed.

## Scope Guard

Do not recommend scraping, crawling, browser automation, platform APIs, account
automation, schedulers, watch folders, source acquisition, compliance/audit
workflow features, matching/scoring changes, report generation changes,
dashboard writes, database migrations, or new dependencies.

The command remains a local read-only review of retained `manual_import` rows
already stored in SQLite. Wording should stay bounded to retained local rows,
imported local signals, and stored match presence derived from `item_entities`.

## Review Focus

Review the current uncommitted diff against `fee145b`.

Check:

1. Table output now says `Matched rows:` and JSON output remains unchanged.
2. CLI validation tests prove invalid `--lookback-days`, `--limit`, and
   `--format` fail before query/database access and before `--data-dir`
   creation.
3. Special-character SQLite paths are covered through the full CLI path and
   direct read-only engine usage.
4. Existing databases remain read-only; no command path initializes, migrates,
   imports, matches, scores, reports, or writes artifacts.
5. Documentation wording stays local-first and does not imply platform
   coverage, source acquisition, market-wide ranking, verified demand, or
   source provenance not present in the database.
6. Tests are focused and deterministic.
7. The implementation does not introduce lockfile/dependency changes.

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

End with one of:

- `Approved for Stage 21 release checks`
- `Not approved`
