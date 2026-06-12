## Critical

None found.

## Important

1. **Read-only SQLite URI construction can fail for valid local `--data-dir` paths containing URI-special characters.**

   - Existing helper: `src/fashion_radar/trends.py:82-86`
   - Stage 20 use: `src/fashion_radar/imported_signals.py:109-114`
   - CLI path: `src/fashion_radar/cli.py:769-776`

   `query_imported_signals()` correctly avoids creating a missing database and uses `create_readonly_sqlite_engine()` for existing DBs. However, that helper interpolates `db_path.as_posix()` directly into:

   ```python
   sqlite:///file:{db_path.as_posix()}?mode=ro&uri=true
   ```

   Because SQLite URI parsing is enabled, valid filesystem paths containing characters such as `?`, `#`, `%`, or `&` can be interpreted as URI syntax rather than as filename characters. That can make `imported-signals --data-dir ...` fail even when `db_path.exists()` is true, or potentially point SQLite at a different interpreted URI target.

   This is especially relevant because `--data-dir` is user-supplied and Stage 20’s command is explicitly about safe local read-only DB inspection. I would fix or at least add a targeted regression test before upload.

## Minor

1. **CLI validation tests do not cover all public option constraints.**

   - CLI command: `src/fashion_radar/cli.py:751-759`
   - Existing tests cover missing/invalid `--as-of`, help text, schema errors, JSON/table behavior.
   - Missing direct CLI tests for:
     - `--lookback-days 0`
     - `--limit -1`
     - invalid `--format`

   The Typer declarations look correct, and helper-level negative limit coverage exists at `tests/test_imported_signals.py:359-369`, so this is not a correctness blocker. It is mainly a UX/regression coverage gap.

2. **CLI table/JSON determinism is partly tested but not fully pinned at CLI level.**

   - Table CLI test: `tests/test_cli.py:1773-1802`
   - JSON CLI test: `tests/test_cli.py:1804-1866`
   - Core deterministic rendering test is stronger: `tests/test_imported_signals.py:536-594`

   Core rendering/order behavior is well covered, but CLI tests mostly assert substrings and selected JSON fields. A future CLI-level formatting/order drift could slip through. Optional polish: assert full `splitlines()` for the table command and fuller JSON payload/order in the CLI JSON test.

3. **Summary label “Matches” is slightly ambiguous.**

   - `src/fashion_radar/imported_signals.py:148-149`

   The implementation correctly counts matched **items** using `EXISTS`, avoiding one-to-many inflation from `item_entities`. But the table summary:

   ```text
   Matches: 1 matched, 1 unmatched
   ```

   could be misread as counting entity match rows. Optional wording such as `Matched rows:` or `Items:` would make the semantics clearer.

4. **Changelog wording says “stored match status,” but status is derived.**

   - `CHANGELOG.md:57`

   The code derives `match_status` from whether `item_entities` rows exist; it does not read a persisted match-status column. Optional wording: “stored matches” or “current stored match presence.”

## Positive checks

- Missing DB behavior is correct: `query_imported_signals()` returns an empty review before opening an engine and does not create directories.
- Time-window semantics are explicit and tested: `window_start < collected_at <= as_of`.
- Counts avoid one-to-many inflation from `item_entities`; matches are fetched separately after item rows are selected.
- Schema verification checks required tables, command-required columns, and exact schema version before querying.
- JSON uses Pydantic `model_dump_json(indent=2)`.
- Table output sanitizes pipes and line breaks and has deterministic source/count ordering.
- No hidden imports, matching, scoring, report/dashboard writes, migrations, source acquisition, scraping, collectors, schedulers, or dashboard artifact creation found in Stage 20 code.
- Docs consistently preserve local-only/source-boundary language.

Not approved
