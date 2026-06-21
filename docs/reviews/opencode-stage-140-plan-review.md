# Stage 140 Plan Review

## Findings

**No blocking issues.** The plan is sound and ready for implementation.

## Minor observations

**[Low] `docs/superpowers/specs/2026-06-21-stage-140-first-run-command-sequence-design.md:78` and plan `tests/test_first_run_smoke.py` Task 2 Step 1** - The RED test fails with `NameError` from the undefined `expected_first_run_flow_commands`, which pytest reports as an error rather than an assertion failure. This still satisfies the RED state because the helper does not exist yet.

**[Low] Single helper-negative test only mutates one command** - The RED test only mutates `community-handoff-workflow`. This is sufficient because `assert_first_run_flow_commands` performs a single `captured == expected` list/tuple equality, which rejects drift on any command.

## Verification of review criteria

### 1. Expected sequence exactly matches `run_first_run_flow()`

Every `run_cli()` call in `scripts/check_first_run_smoke.py:1860-2184` was compared against the plan's `expected_first_run_flow_commands()` body and the design's expected command list. All 22 commands match in order, flag positions, and dynamic values:

- `init`
- `migrate-db`
- `doctor`
- `external-tool-adapters`
- `external-tool-template`
- `external-tool-workflow`
- `external-tool-readiness`
- `community-signal-lint`
- `community-candidates`
- `import-signals` dry run
- `import-signals` import
- `match`
- `imported-review-workflow`
- `imported-signals-summary`
- `imported-signals`
- `report`
- `candidates`
- `trends`
- `community-handoff-workflow`
- `community-signal-lint-dir`
- `community-candidates-dir`
- `import-signals-dir` dry run

Dynamic values (`str(context.config_dir)`, `str(context.data_dir)`, `str(context.reports_dir)`, `str(context.exports_dir)`, `str(example_csv)`, `smoke.AS_OF`, `smoke.SOURCE_NAME`, `smoke.DIR_PATTERN`) match exactly.

### 2. Helper-negative RED test catches drift the old checks missed

Appending `"--extra"` to the `community-handoff-workflow` tuple leaves the old loose checks satisfied because index 1, `--format`, and `json` remain present. The new strict `captured == expected_first_run_flow_commands(...)` comparison rejects the mutation.

### 3. Plan avoids runtime behavior changes

The plan modifies only `tests/test_first_run_smoke.py` plus stage artifacts. `scripts/check_first_run_smoke.py` is untouched. The existing fake `run_cli` monkeypatch path remains preserved.

### 4. Focused verification is sufficient before release gate

For a change confined to one test file, the planned focused verification is appropriate:

- `pytest tests/test_first_run_smoke.py -q`
- `ruff check tests/test_first_run_smoke.py`
- `ruff format --check tests/test_first_run_smoke.py`
- `git diff --check`

The full release gate follows afterward.

## Conclusion

**Proceed.** The plan correctly implements exact argv tuple comparison for every emitted first-run command, includes a useful RED test, avoids runtime behavior changes, and has adequate verification.
