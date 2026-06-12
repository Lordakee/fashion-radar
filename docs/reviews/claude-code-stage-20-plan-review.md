Using `code-review` to assess the Stage 20 design/plan in read-only mode.

## Critical

None.

I did not find any plan defect that would inherently violate the Stage 20 scope or make the feature unsafe to implement, assuming the planned implementation follows the proposed module/CLI structure.

## Important

### 1. Read-only behavior is designed correctly, but the tests do not fully prove read-only SQLite opening

The design and plan say existing databases are opened through `create_readonly_sqlite_engine(db_path)`, which matches the existing `trends` read-only helper:

```python
sqlite:///file:{db_path.as_posix()}?mode=ro&uri=true
```

That is the right implementation direction.

However, the planned CLI test:

```python
test_imported_signals_command_does_not_mutate_existing_database
```

only compares row counts before and after. That proves the command did not happen to write rows, but it does **not** prove the database was opened read-only. A future implementation could accidentally use `create_sqlite_engine(...)`, perform no writes, and still pass this test.

Before implementation, strengthen the plan with a test that would fail if the command opens the DB in read-write/create mode. Options:

- monkeypatch `fashion_radar.imported_signals.create_readonly_sqlite_engine` and assert it is called;
- or add a lower-level module test that opens via the query path and verifies write attempts through the created engine fail;
- or use SQLite/file permission setup carefully, though monkeypatching the helper is likely more deterministic.

This matters because “existing database should be opened read-only” is a core Stage 20 requirement, not just an incidental non-mutation property.

### 2. Invalid `--as-of` is handled correctly in the plan, but the test should prove SQLite is not opened

The planned CLI implementation parses `--as-of` before calling `query_imported_signals(...)`, so the behavior is correct:

```python
as_of_value = parse_datetime_utc(as_of)
...
review = query_imported_signals(...)
```

But the test only checks that a missing `data_dir` is not created. It does not prove that SQLite/database access is skipped when a database already exists.

Add a test where `data_dir/fashion-radar.sqlite` exists, `--as-of` is invalid, and `query_imported_signals` or the read-only engine helper is monkeypatched to fail if called. This would directly cover the requirement:

> Invalid `--as-of` should exit non-zero before opening SQLite or creating directories.

### 3. Documentation boundary scan is too narrow for the stated scope guard

The design and implementation plan contain strong negative scope language, and the planned docs wording is appropriately bounded to local retained `manual_import` rows.

However, the planned docs scan only searches:

```text
imported-signals|platform-wide|market-wide|current-hotness|source acquisition|source-acquisition|platform search|social monitoring|ranking|demand proof|authorization|audit|policy
```

The Stage 20 scope guard is broader. The scan should also include terms such as:

- `scrap`, `crawl`, `crawler`
- `browser`, `Playwright`, `Selenium`
- `MCP`
- `platform API`, `API`
- `login`, `cookie`, `profile`, `proxy`
- `CAPTCHA`, `rate-limit`, `bypass`
- `watch folder`, `scheduler`, `background`
- `approval`, `legal`, `legal-review`
- `source export`, `export acquisition`
- `coverage`, `monitoring`

The plan does not need to ban all ordinary occurrences globally, but the boundary scan should be broad enough to catch accidental source-acquisition or compliance-workflow language in the modified docs.

### 4. Schema verification may be acceptable by existing project style, but clarify whether table presence is enough

The plan verifies:

- `schema_metadata` exists;
- `items` exists;
- `item_entities` exists;
- `schema_metadata.version == SCHEMA_VERSION`.

That matches the existing `verify_readonly_trend_schema(...)` pattern and is probably compatible with the codebase.

However, the Stage 20 prompt asks whether schema verification is sufficient, including `schema_metadata.version`. If the intended definition of “invalid schema” includes missing required columns, the plan currently does not explicitly verify columns before querying. Instead, missing columns would fail later and be caught by the CLI’s broad exception handler.

That is acceptable if the project’s schema contract is “known schema version implies known columns.” But the design/plan should say that explicitly, or add minimal column checks for the columns used by this command:

`items.id`, `source_name`, `source_type`, `url`, `title`, `published_at`, `collected_at`, `source_weight`, `summary`; and `item_entities.item_id`, `entity_name`, `entity_type`, `alias`, `confidence`.

I would not require exhaustive migration-grade validation, but the plan should clarify the intended level.

## Minor

### 1. `imported-signals` is a clear and compatible CLI name

The name is good. It is close enough to `import-signals` / `import-signals-dir` to be discoverable, while the past-tense adjective “imported” makes it clear this is a review command, not an import command.

No change needed.

### 2. Required `--as-of` plus `--lookback-days` fits existing read-only style

This matches the deterministic style of `trends` and mostly aligns with `candidates`. Requiring `--as-of` avoids hidden dependence on runtime clock time and makes table/JSON output reproducible.

No change needed.

### 3. Query shape is appropriately bounded to local post-import review

The proposed query is scoped to:

```text
items.source_type == "manual_import"
window_start < collected_at <= as_of
```

with optional exact `source_name`, optional `unmatched_only`, deterministic ordering, and a display limit.

This is sufficient for local post-import review and does not become a report/scoring feature because it does not compute trends, scores, rankings, representative metrics, candidate phrases, or platform coverage.

No change needed.

### 4. `--unmatched-only` adds useful value without triggering matching

This is useful for answering “which imported local rows currently have no stored entity matches?” after import and before downstream matching/review.

The plan correctly derives this only from existing `item_entities` rows using `EXISTS`, and does not run `match_entities`, `replace_item_matches`, scoring, or candidate discovery.

No change needed.

### 5. Aggregate count semantics are coherent, but should remain explicitly documented

The design says counts are computed after source/window/unmatched filters and before limit. That means with `--unmatched-only`, `matched_count` will normally be `0`, and `unmatched_count == total_count`.

That is internally consistent. Just ensure docs/tests preserve that interpretation so users do not assume counts represent the unfiltered window.

### 6. Table output is deterministic enough, but not robust to separators/newlines

The simple pipe-delimited table is acceptable for a CLI human review command. Ordering, count ordering, and numeric formatting are deterministic.

Optional polish: sanitize or replace embedded newlines/pipes in title/source/URL fields before rendering table rows. JSON remains the stable machine-readable contract, so this is not a blocker.

### 7. JSON key order is deterministic enough

The planned Pydantic model field order plus `model_dump_json(indent=2)` should give stable key order in Python 3.11/Pydantic v2. The tests assert top-level, item, and match key order, which is good.

No change needed.

### 8. Test coverage is broadly strong

The planned tests cover most requested cases:

- manual-only filtering;
- window boundaries;
- ordering;
- limit including `0`;
- source-name trimming/filtering;
- `--unmatched-only`;
- match aggregation without item count inflation;
- missing DB no-artifact behavior;
- invalid `--as-of`;
- invalid schema no traceback;
- CLI help;
- table output;
- JSON key order;
- internal/private field exclusion;
- existing DB unchanged.

The main gaps are the stronger read-only/invalid-as-of-before-SQLite assertions described above.

### 9. The implementation plan should avoid prescribing `git push origin main`

The final task says to commit and push to `main` after approval. That may be fine for this repository’s current workflow, but as a general implementation plan it is a bit operationally aggressive. Consider changing it to “commit after approval; push according to repository workflow” unless direct pushes to `main` are explicitly desired.

This is minor and not about the feature’s technical design.

## Answers to the requested review questions

1. **CLI name:** Yes, `imported-signals` is clear and compatible.
2. **Required `--as-of` + `--lookback-days`:** Yes, compatible with deterministic read-only command style.
3. **Query shape:** Yes, sufficient and appropriately bounded to local retained imports.
4. **`--unmatched-only`:** Yes, useful and safe if based only on existing `item_entities`.
5. **Read-only behavior:** Design is good; tests should more directly prove read-only opening.
6. **No `--data-dir` creation:** Design and plan handle missing DB and invalid `--as-of`; add stronger test proving invalid `--as-of` skips DB access even when DB exists.
7. **Schema verification:** Mostly sufficient by existing schema-version style; clarify whether table+version is the contract or add column checks.
8. **Output contracts:** Deterministic enough; optional table cell sanitization.
9. **Tests:** Broad coverage, but add direct read-only-engine and no-SQLite-on-invalid-as-of tests.
10. **Docs:** Wording is scoped well, but planned boundary scan should be expanded.
11. **Missing before implementation:** The important test/scan clarifications above.

Not approved
