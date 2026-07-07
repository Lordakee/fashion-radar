## Stage 330 Plan Re-Review

---

### Critical

None.

The integration test (Task 2 Step 1, plan lines 395–404) now calls `_patch_successful_row_one_refresh_pipeline(monkeypatch, ...)` before invoking the CLI, with an explicit comment that `clean_old_data` is left unpatched. The previous blocker is resolved.

---

### Important

None.

All four findings from the original review remain resolved.

---

### Medium

**1. `--skip-data-retention` double-negative still not suppressed**

Task 1 Step 4 (plan line 290–294) now passes `"--skip-data-retention"` as an explicit name to `typer.Option`, but still omits `is_flag=True`:

```python
skip_data_retention: bool = typer.Option(
    False,
    "--skip-data-retention",
    help="...",
),
```

Typer's boolean handling will still expose `--skip-data-retention / --no-skip-data-retention` unless `is_flag=True` is present. The help assertion (Task 2 Step 3) only checks that `"--skip-data-retention" in result.output`, so it passes either way. Add `is_flag=True` to suppress the negative variant:

```python
skip_data_retention: bool = typer.Option(
    False,
    "--skip-data-retention",
    is_flag=True,
    help="Skip ROW ONE SQLite item retention after refresh.",
),
```

**2. `cli-reference.md` retention content has no test coverage**

Task 3 Step 1's docs test reads only `README + ROW_ONE_DOC + FIRST_RUN_DOC`:

```python
docs = "\n".join(_normalized(_read(path)) for path in (README, ROW_ONE_DOC, FIRST_RUN_DOC))
```

Task 3 Step 3 correctly says to add/update a `row-one refresh` entry in `cli-reference.md`, but nothing in the test suite will catch a missing or wrong cli-reference entry. Consider extending the sentinel test to also validate `CLI_REFERENCE` for the new `--retention-days` and `--skip-data-retention` flags, or add a separate assertion block for it.

---

### Minor

None.

---

### Verdict

No Critical or Important blockers remain. The previous Critical blocker (missing monkeypatches in the integration test) is fixed. Two Medium findings carry over: `is_flag=True` still needs to be added to suppress `--no-skip-data-retention`, and cli-reference.md edits have no test-sentinel coverage. Neither blocks implementation, but both should be addressed before Stage 330 is closed. **Plan is ready for implementation.**
