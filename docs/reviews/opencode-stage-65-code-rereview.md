Reviewed the post-review delta: the new sort tie-breaker test (`tests/test_imported_entity_evidence.py:302-332`), the parameterized numeric-option rejection test plus `pytest` import (`tests/test_cli.py:9` and `:5210-5256`), and the three docs rewrites. All four delta tests pass locally.

## Verdict: PASS

## Critical findings
None.

## Important findings
None.

The delta is correct and scoped:
- `test_query_imported_entity_evidence_sorts_same_timestamp_by_higher_id` exercises the third sort key (`-row.id` at `imported_entity_evidence.py:210`) with two same-window, same-`collected_at` rows and asserts `[higher_id, lower_id]`; the `higher_id > lower_id` guard prevents silent false positives if SQLite id assignment ever surprised us.
- The parameterized `test_imported_entity_evidence_command_rejects_invalid_numbers_without_query` correctly relies on Typer's `min=1`/`min=0` parse-time rejection (`cli.py:1718-1720`), monkeypatches `query_imported_entity_evidence` to fail if reached, and asserts non-zero exit, the option name in stderr, no traceback, and no `data_dir` creation.
- Docs ordering in `README.md`, `docs/community-signal-import.md`, and `docs/architecture.md` now matches `build_imported_review_workflow` step order (`imported_review_workflow.py:62-185`: summary → match → entity-deltas → entity-evidence → candidates → unmatched → heat-movers), and the new boundary language is consistent with AGENTS.md scope rules.

## Test gaps
- Non-blocking: the prior review's second minor gap still stands — limit-cutoff-after-sort is only asserted for `limit=0`; a `limit=1` case with multiple sorted rows would close it. Not a blocker given the deterministic sort key.
