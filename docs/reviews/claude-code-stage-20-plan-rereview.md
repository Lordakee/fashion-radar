## Critical

None.

## Important

1. **Schema verification should explicitly validate `schema_metadata.version` exists before selecting it.**
   The design requires checking `schema_metadata.version`, but the implementation plan only verifies the table exists and then executes `select(schema_metadata.c.version)`. If a malformed local DB has `schema_metadata` without a usable `version` column, the command will likely still exit non-zero without traceback via the CLI catch, but the schema error will be less intentional and less deterministic than the required `items` / `item_entities` column checks.
   **Recommendation:** add `schema_metadata` to explicit column verification, e.g. require `{"version"}`, before reading the version.

2. **The plan should specify deterministic sanitization for table cells.**
   The table renderer directly interpolates `source_name`, `title`, `url`, and matched entity names. Imported local rows may contain pipes or newlines, which can make the table output ambiguous or multi-line in non-deterministic-looking ways. This is not a report/scoring issue, but it affects the output contract.
   **Recommendation:** define a tiny table-cell formatter that replaces `\r`/`\n` with spaces and either leaves `|` as-is intentionally or replaces it with `/`/escaped text. Add at least one renderer test for this.

3. **Add a direct populated table renderer test, not only a CLI table substring test.**
   The plan has a direct empty-table renderer test and CLI populated-output assertions, but it does not fully lock the populated table contract at module level. Since `render_imported_signals_table(...)` is part of the proposed public module surface, it should have direct tests for header order, row order, match-cell formatting, weight formatting, and populated source counts.

4. **Avoid reusing `AS_OF_OPTION` help text that says “report timestamp.”**
   Existing `AS_OF_OPTION` is compatible functionally, but the help text is report-oriented: “UTC report timestamp…”. For `imported-signals`, this is a review window boundary, not a report.
   **Recommendation:** define a command-specific `typer.Option(..., "--as-of", help="UTC review timestamp...")` or adjust shared wording to be generic.

## Minor

1. **Hard-coded schema version values in tests are a maintainability footgun.**
   Several planned invalid-schema tests insert `version = 4`. Since current `SCHEMA_VERSION` is 4, this is correct today, but future schema changes would make these tests fail for the wrong reason. Prefer importing and using `SCHEMA_VERSION` where the test intends “current supported version.”

2. **Consider documenting match ordering explicitly.**
   The plan orders matches by `item_entities.item_id, item_entities.id`, which is deterministic. The design only says match status comes from existing rows. If JSON consumers may compare snapshots, explicitly state matches are ordered by stored `item_entities.id`.

3. **`limit: int | None` is broader than the CLI contract.**
   The CLI exposes `--limit` default `50`, min `0`, with no obvious way to pass `None`. Keeping the helper flexible is fine, but the plan should clarify that CLI limit is always an integer while the Python helper accepts `None` for unbounded internal use, if that is intentional.

4. **Docs scope scan terms are good but may be noisy.**
   The proposed `rg` scans include very broad terms like `API`, `browser`, `background`, and `monitoring`, which may hit established negative-boundary or unrelated docs. The expected-result language handles this, so this is only operational polish.

## Review Questions

1. **Is `imported-signals` a clear and compatible CLI name?**
   Yes. It is distinct from `import-signals` / `import-signals-dir`, reads naturally as a review command, and accurately scopes itself to already-imported rows.

2. **Is required `--as-of` plus `--lookback-days` compatible with existing read-only command style?**
   Yes. It matches the deterministic style used by `candidates` / `trends`, especially the practice of avoiding implicit runtime-dependent windows. The only polish is command-specific help text.

3. **Is the query shape sufficient for local post-import review without becoming a report/scoring feature?**
   Yes. Filtering `items.source_type == "manual_import"` and `window_start < collected_at <= as_of`, with optional exact `source_name`, is appropriately narrow. It does not compute scores, rankings, trend deltas, or recommendations.

4. **Does `--unmatched-only` add useful review value without triggering matching or scoring?**
   Yes. It is useful for post-import triage and is safe as long as it is implemented only as `NOT EXISTS` / absence of existing `item_entities` rows. The design and plan preserve that boundary.

5. **Does the design preserve read-only behavior for missing and existing databases?**
   Mostly yes. Missing DB is checked with `db_path.exists()` before creating an engine. Existing DB uses the existing read-only SQLite URI helper. Tests also monkeypatch helper usage and check database counts after CLI invocation.

6. **Does the plan avoid creating `--data-dir` on missing DB and invalid `--as-of`?**
   Yes. `default_database_path(data_dir)` does not create directories, and invalid `--as-of` is parsed before query/database access. The planned tests cover both missing DB no-artifact behavior and invalid `--as-of` no-query behavior.

7. **Is schema verification sufficient, including `schema_metadata.version` and command-required columns?**
   Close, but not quite. It verifies required tables, schema version equality, and `items` / `item_entities` columns. It should also explicitly verify `schema_metadata.version` exists before selecting it.

8. **Are table and JSON output contracts deterministic enough?**
   JSON is deterministic enough through Pydantic field order and sorted/grouped source counts. Table output is mostly deterministic but should define cell sanitization and add direct populated renderer tests.

9. **Do tests cover the requested behaviors?**
   Broadly yes: manual-only filtering, exact window boundaries, ordering, limit, source-name filter, unmatched-only, match status without count inflation, missing DB no-artifact behavior, invalid as-of, invalid schema, CLI help, table, JSON key order, private/internal field exclusion, direct read-only helper usage, skipped query on invalid as-of, and unchanged existing DB are all covered or substantially covered.
   Gaps: direct populated table-renderer contract and explicit `schema_metadata.version` column validation.

10. **Do docs avoid prohibited source acquisition / scraping / authorization / audit / ranking claims?**
   Yes in the design and plan language reviewed. The docs plan repeatedly frames the command as local SQLite review of retained `manual_import` rows and includes explicit negative boundaries.

11. **Is anything missing before implementation begins?**
   Yes: address the two implementation-plan gaps before coding:
   - explicit `schema_metadata.version` column verification;
   - deterministic table-cell formatting plus direct populated table renderer tests.

## Overall

The Stage 20 design is sound and appropriately scoped. The command name, read-only architecture, time-window filtering, manual-only query, unmatched-only behavior, and documentation boundaries all align with the goal. However, because the schema verification and table-output contract need tightening before implementation, I would not start implementation until those plan fixes are made.

Not approved
