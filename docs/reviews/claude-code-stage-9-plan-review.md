Not approved

- `Critical:` None.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 4, lines 488-531: the proposed `import_manual_signal_rows(..., dry_run=True)` implementation still constructs `ItemRepository(engine)` and calls `count_items()` before checking `dry_run`. The CLI Task 5 correctly bypasses engine creation during `--dry-run`, but the importer workflow API itself violates the Stage 9 architecture if called directly with `dry_run=True`: dry-run should validate only and should not touch the database. Move the `if dry_run:` branch immediately after `load_manual_signal_rows()` and before any `ItemRepository` construction or `count_items()` call. Add/update a test that proves dry-run does not require an initialized schema or usable database connection, not just that it writes no rows.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 4 tests, lines 419-440: `test_import_manual_signal_rows_dry_run_writes_nothing` initializes the database before calling dry-run. This does not drive the required behavior that dry-run must avoid database initialization/access. Add a test at the CLI level and/or importer level that uses a non-existent `data_dir` or an uninitialized engine and asserts no database file/directory/schema is created or required. The existing CLI test at lines 583-608 is good, but the workflow-level test currently encourages a weaker implementation.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3, lines 290-321: `ManualSignalRow.published_at` and `collected_at` are typed as `object`, with a validator returning datetimes. This will probably work at runtime, but it weakens Pydantic's schema/typing and makes tests less precise. Use `datetime` and `datetime | None` for these fields so validators and downstream `CollectedItem` construction are type-driven. Add explicit tests asserting `published_at` and `collected_at` are UTC-aware datetimes after parsing.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 3 tests, lines 155-253: parser/validator tests are a good start but not yet specific enough to fully drive a correct importer. Add tests for:
  - JSON top-level invalid shapes, including object without `items` and non-object list entries.
  - CSV with no headers / empty file.
  - missing or blank `title` and `published_at`, not only blank `url`.
  - invalid `published_at` and invalid `collected_at`.
  - `source_weight` boundaries: `0`, negative, `>5`, non-numeric, and default `1.0`.
  - row `source_name` fallback behavior when blank.
  - unknown CSV columns ignored, not just unknown JSON keys.
  These cases matter because the feature's safety depends on validating all rows before writes and storing only sanitized metadata.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 5, lines 637-663: the CLI catches only `ManualSignalImportError`. Invalid `--imported-at` currently goes through `parse_datetime_utc()` outside that exception type and will be caught by Typer's generic exception handling, if any, rather than producing the concise import error promised by the design. Either wrap `imported_at` parsing in a `try` block that reports a controlled non-zero error, or add an explicit test for invalid `--imported-at` and document the intended error.

- `Minor:` `docs/superpowers/specs/2026-06-12-stage-9-manual-signal-import-design.md`, lines 5-7 and plan line 5: "platform/export tools" and "manual/exported data" are probably safe because no acquisition instructions are provided, but the wording could be tightened to "user-provided local CSV/JSON files" to avoid implying Fashion Radar helps obtain platform exports. Similarly, the CLI examples using `"Manual Social Export"` could be changed to `"Manual Export"`.

- `Minor:` `docs/superpowers/specs/2026-06-12-stage-9-manual-signal-import-design.md`, lines 143-146 and plan lines 77-80: the plan says CLI output reports "new items added separately from rows imported." The proposed implementation computes this via before/after total counts, which is acceptable for single-process local SQLite usage but can be inaccurate under concurrent writes. If concurrency is out of scope, note that this is an approximate local count under normal CLI use; otherwise, consider deriving new-vs-updated status per normalized URL before import.

- `Minor:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 2: adding `SourceType.MANUAL_IMPORT` is safe if `SourceDefinition` rejects it, and `_default_collectors()` does not need a manual importer entry. Add a test through `load_source_config()` with YAML containing `type: manual_import`, not only direct `SourceDefinition(...)`, to prove `sources.yaml` rejection matches the user-facing config path.

- `Minor:` `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`, Task 6 safety grep, lines 722-730: the grep is useful but broad enough that required negative boundary wording will trigger many matches. Add an instruction that each match must be manually reviewed and classified as negative-boundary wording vs unsafe claim, rather than expecting "no matches" except loosely defined exceptions.

- `Minor:` Verification plan is generally sufficient: focused tests, full pytest, ruff, lock/sync checks, build, installed-wheel CLI smoke, CodeGraph status, and max-effort code review. Consider adding an installed-wheel smoke for an actual `import-signals --dry-run` against a temporary CSV, not just `import-signals --help`, because dry-run's "no data_dir creation" property is one of the key Stage 9 guarantees.
