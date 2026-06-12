## Critical

None.

## Important

1. **Planned match aggregation test compares Pydantic models to dicts and will fail as written.**
   In `test_query_imported_signals_reads_match_status_and_unmatched_only`, the plan asserts:

   ```python
   assert matched.matches == [
       {"entity_name": "The Row", ...},
       ...
   ]
   ```

   But the proposed model defines `matches: list[ImportedSignalMatch]`, so `matched.matches` will be a list of Pydantic model instances, not dicts. The test should compare:

   ```python
   assert [match.model_dump() for match in matched.matches] == [...]
   ```

   or compare individual attributes. This should be fixed before implementation because otherwise the TDD plan contains an avoidable false failure.

2. **Direct helper behavior for negative `limit` is under-specified/inconsistent.**
   The CLI option sets `min=0`, but the proposed module implementation silently clamps direct `query_imported_signals(..., limit=-1)` to `0` via:

   ```python
   item_query = item_query.limit(max(0, int(limit)))
   ```

   Since the plan explicitly calls out “direct read-only helper usage” and validates `lookback_days < 1`, the helper should probably also reject negative `limit` with `ValueError` rather than silently changing caller input. Add a small module test if this contract matters.

3. **The implementation plan should explicitly ensure JSON serialization uses JSON-mode dumping if future fields become non-primitive.**
   The proposed models currently store datetimes as strings, so `review.model_dump_json(indent=2)` is deterministic enough. Still, because this project uses Pydantic v2 and other code sometimes uses `model_dump(mode="json")`, the plan should state the intended JSON emission path remains `model_dump_json(indent=2)` and model fields intentionally stay JSON primitives/strings. This is not blocking, but it helps keep the JSON contract stable.

4. **The plan is broad on documentation edits; reviewers should watch for scope drift.**
   The listed docs updates are reasonable, but the number of docs touched creates risk of accidental wording around “monitoring,” “coverage,” “ranking,” “source acquisition,” or “approval/audit.” The plan includes boundary scans, which is good. I would keep the docs changes minimal: examples plus explicit negative boundaries only.

## Minor

1. **CLI name is clear and compatible.**
   `imported-signals` is a good name. It distinguishes review from the mutating `import-signals` / `import-signals-dir` commands while staying aligned with existing noun-based commands like `candidates` and `trends`.

2. **Required `--as-of` plus `--lookback-days` is compatible with the existing read-only style.**
   Requiring `--as-of` follows the deterministic style of `trends` and `candidates`. `--lookback-days` is appropriate here because this command is a review window, not a scoring/report snapshot.

3. **Query shape is appropriately bounded.**
   Filtering only `items.source_type == "manual_import"` and `window_start < collected_at <= as_of` is sufficient for local post-import review. The plan avoids scoring, candidate extraction, report generation, trend comparison, and matching behavior.

4. **`--unmatched-only` is useful and safely scoped.**
   It adds review value by surfacing imported rows without existing `item_entities` matches. The design correctly states that it reads stored matches only and must not invoke matching/scoring.

5. **Read-only behavior is well preserved.**
   The design and plan cover:
   - missing DB returns empty result;
   - no `--data-dir` creation for missing DB;
   - invalid `--as-of` handled before database access;
   - existing DB opened through read-only SQLite URI mode;
   - existing DB unchanged after CLI execution.

6. **Schema verification is sufficient for this command.**
   Checking required tables, `schema_metadata.version`, expected `SCHEMA_VERSION`, and command-required columns in `items` / `item_entities` is appropriate. It intentionally avoids requiring unrelated tables such as `entity_first_seen`, which keeps the command focused.

7. **Table output contract is deterministic enough.**
   Fixed row ordering, fixed header lines, fixed source-count formatting, fixed weight formatting, and deterministic sanitization of `\r`, `\n`, and `|` are sufficient.

8. **JSON output contract is deterministic enough.**
   Top-level field order follows Pydantic model declaration order. Item and match keys are explicitly tested. Internal/private fields are excluded.

9. **Test coverage is strong.**
   The planned tests cover the requested areas: manual-only filtering, boundaries, ordering, limit, source filter, unmatched-only, match count inflation avoidance, missing DB/no-artifact behavior, invalid `--as-of`, invalid schema, CLI help, table/JSON, private field exclusion, read-only helper use, skipped DB access on invalid date, sanitization, and unchanged DB.

10. **Scope guard is respected.**
    The design and plan avoid scraping, crawling, platform APIs, source acquisition instructions, browser automation, account automation, background jobs, watch folders, migrations, matching/scoring/report/dashboard writes, and approval/audit/policy workflow features.

## Overall readiness

The Stage 20 design is ready in concept. The implementation plan is also largely ready, but I would fix the Pydantic model-vs-dict test assertion before implementation starts, and preferably clarify direct-helper handling for negative `limit`.

Approved for Stage 20 implementation
