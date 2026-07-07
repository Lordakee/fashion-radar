## Stage 330 Plan Re-Review

### Critical

**Integration test is incomplete — monkeypatching not shown**

Task 2 Step 1 (lines 347-420) writes the real SQLite integration test that's supposed to patch collect/match/report/site helpers while allowing `clean_old_data` to run. Line 396 has a comment:

```python
# Patch collect/match/report/site helpers to avoid network and generated-site work.
# Do not patch clean_old_data.
```

But the test code after this comment jumps directly to calling `CliRunner().invoke(...)` without showing the actual `monkeypatch.setattr` calls. The test will fail because the unpatched helpers will try to do real network/filesystem work.

**Fix:** The integration test should call `_patch_successful_row_one_refresh_pipeline(monkeypatch,...)` between setting up the repository and calling `CliRunner().invoke()`, similar to how the skip-retention test (lines 176-183) and failure-warning test (lines 226-233) use it.

---

### Important

**1. Previous Important findings are now RESOLVED:**

All four Important findings from the original review have been addressed:
- `PruneResult` field names (`items_deleted`, `item_entities_deleted`) verified in repositories.py:266-270 and used correctly in plan.
- `ItemRepository.count_items()` exists at repositories.py:70-72 and returns int.
- Scoring window interaction is documented via sentinels "scoring window" and "heat scores" in Task 3 Step 1 line 470.
- Retention failure handling uses a separate try/except (Task 1 Step 4 lines 300-309) that warns without converting success to failure.

---

### Medium

**2. `skip_data_retention` double-negative UX remains**

Task 1 Step 4 (line 289) defines:
```python
skip_data_retention: bool = typer.Option(
    False,
    help="Skip ROW ONE SQLite item retention after refresh.",
),
```

Typer will render this as `--skip-data-retention / --no-skip-data-retention`. The `--no-skip-data-retention` variant is awkward (double-negative: "don't skip" = "do it").

The help assertion (line 435) only checks that `"--skip-data-retention" in result.output`, so it passes either way. The original review suggested using `typer.Option(False, "--skip-data-retention", is_flag=True, help="...")` to suppress the negative variant, but the plan hasn't incorporated this.

This is a UX polish issue, not a functional blocker.

---

**3. `row-one refresh` command not documented in cli-reference.md baseline**

The cli-reference.md (read just now) lists `row-one build`, `row-one preview`, `row-one status`, `row-one ops-check`, `row-one local-ops`, `row-one install-local`, `row-one serve`, and `row-one schedule` but does not document `row-one refresh` at all.

The plan Task 3 says "Modify: `docs/cli-reference.md`" and assumes documentation exists to update. The command exists in the CLI (design doc line 60describes its behavior), but cli-reference.md doesn't describe it yet.

The docs tests (line 462) check README, ROW_ONE_DOC, and FIRST_RUN_DOC for the sentinels, not CLI_REFERENCE. So the missing cli-reference.md baseline may not cause test failures, but it means the plan should ADD a `row-one refresh` section to cli-reference.md rather than just updating existing text.

---

### Minor

None beyond what was already identified in the original review.

---

### Verdict

**One Critical blocker:** The integration test (Task 2 Step 1) is incomplete and will fail because it doesn't actually set up the required monkeypatches before invoking the CLI.

**Two Medium findings:** The double-negative flag UX issue and the cli-reference.md baseline gap. Neither blocks implementation, but both should be addressed for polish.

Fix the Critical finding by adding the `_patch_successful_row_one_refresh_pipeline` call to the integration test setup between repository initialization and CLI invocation. After that fix, the plan is ready for implementation.
