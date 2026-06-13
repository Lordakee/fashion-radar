## Critical

No Critical findings.

## Important

No Important findings.

## Minor

No Minor findings.

## Review Summary

- Table output now uses `Matched rows:` in `render_imported_signals_table()`, and tests assert the old `Matches:` prefix is absent.
- JSON output contract remains unchanged, including stable `ImportedSignalsReview` keys and match item fields.
- CLI validation regressions for invalid `--lookback-days 0`, `--limit -1`, and `--format xml` monkeypatch `query_imported_signals` and assert validation fails before query/database access and before `--data-dir` creation.
- Special-character SQLite paths containing `? # & %` are covered through:
  - full `imported-signals --data-dir ... --format json` CLI execution;
  - direct read-only SQLite engine usage with successful read and rejected write.
- Existing `imported-signals` command path remains read-only: it uses `query_imported_signals()` and `create_readonly_sqlite_engine()`, and does not initialize, migrate, import, match, score, report, or write artifacts.
- Documentation/process wording reviewed stays bounded to local retained `manual_import` rows and stored match presence; no scope-expanding claims found.
- Tests are focused and deterministic.
- No dependency or lockfile changes found.

Approved for Stage 21 release checks
