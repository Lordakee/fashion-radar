## Code Review: Stage 330 - ROW ONE Refresh Data Retention

### Findings

**No Critical or Important findings.**

The implementation correctly adds default SQLite data retention to `row-one refresh` with proper ordering, error handling, and documentation.

---

### Correctness Verification

**Order of operations** (`src/fashion_radar/cli.py:1514-1596`):
✓ Retention runs AFTER successful refresh (collect, match, report, site, prune)
✓ Retention is outside the try/except block that handles refresh failures
✓ Retention exceptions are caught and reported as warnings, not failures
✓ Exit code remains 0 when retention fails after successful refresh

**CLI flags** (`src/fashion_radar/cli.py:1506-1511`):
✓ `--retention-days` defaults to 1 with min=1 constraint
✓ `--skip-data-retention` boolean flag with appropriate help text
✓ No redundant `--no-skip-data-retention` flag (verified in test output)

**SQLite integration test** (`tests/test_row_one_cli.py:639-727`):
✓ Creates old item (2026-07-01) with 1 entity match
✓ Creates current item (2026-07-02) with 0 entity matches
✓ After refresh with `--retention-days 1`:
  - Verifies 1 item remains (the current one, by ID and URL)
  - Verifies 0 `item_entities` rows remain (proving old entity match deleted)
  - Proves both old `items` row and old `item_entities` row are deleted

**First-run smoke** (`scripts/check_first_run_smoke.py:3582`, `tests/test_first_run_smoke.py:1869`):
✓ Refresh command now includes `--skip-data-retention`
✓ Expected output includes "SQLite retention: skipped"
✓ Sample data will not be deleted by retention

**Documentation** (verified by test assertions):
✓ Stale claims about "leaving sqlite/data retention to clean-old-data" removed from README.md, docs/row-one.md, docs/first-run.md, docs/data-retention.md, docs/cli-reference.md
✓ New behavior documented in all relevant files with consistent terminology
✓ Scheduling docs distinguish ROW ONE default retention from standalone `clean-old-data`
✓ Tests enforce retention flags, timing ("after current site and reports are generated"), and boundaries (what is NOT pruned)

**Runtime/app contract** (verified by passing tests):
✓ `test_row_one_app_contract.py`:141 passed
✓ No `row-one-runtime/v2`
✓ No runtime JSON `retention_days` or `skip_data_retention` fields
✓ No changed `refresh.command` structure

---

### Medium Observations

None.

---

### Minor Observations

**Output message precision** (`src/fashion_radar/cli.py:1586`):
The phrase "item/entity matches" is informal but clear. Could be "item_entities rows" for technical precision, but current phrasing is adequate for user-facing output.

**Edge case handling** (`src/fashion_radar/cli.py:1578-1588`):
If `clean_old_data` returns `None` without raising an exception (which should never happen per implementation), no retention message is printed. This is not a real-world concern but could add an `else` clause for defensive completeness:
```python
else:
    typer.echo("SQLite retention: unexpected result")
```
Not required for this stage.

---

### Test Gaps

None identified. The implementation includes:
- Unit tests for flag behavior (default retention, `--skip-data-retention`, failure handling)
- Real SQLite integration test proving deletion semantics
- Docs tests enforcing removal of stale claims and presence of new behavior descriptions
- First-run smoke verification with `--skip-data-retention`
- App contract tests confirming no runtime drift

---

### Release Risks

None identified. All verification tests passed:
- 374tests for CLI, docs, scheduling, and app contract
-176 tests for first-run smoke
- `git diff --check` clean
- Help output shows correct flags

The implementation is complete and ready for release verification.
