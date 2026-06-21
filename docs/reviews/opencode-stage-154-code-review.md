## Stage 154 Code Review Findings

**No blocking issues.** The implementation exactly matches the design and plan,
and all verification passes.

### Detailed review against criteria

**1. RED tests isolate top-level field drift after command rewrites** -
`tests/test_first_run_smoke.py:2052-2073`
- `test_validate_imported_review_workflow_rejects_config_dir_drift` mutates
  `payload["config_dir"]` and rewrites all `--config-dir configs` fragments;
  `test_validate_imported_review_workflow_rejects_data_dir_drift` does the same
  for `data_dir` / `--data-dir data`.
- The rewrites cover every step that references the drifted path, so command
  argv stays internally consistent and the only remaining drift is the top-level
  field. Correct isolation.

**2. Validator compares against caller-supplied expected values** -
`scripts/check_first_run_smoke.py:1007-1077`
- Signature now has keyword-only `expected_config_dir: str = "configs"` and
  `expected_data_dir: str = "data"`.
- Payload-derived locals were removed; replaced with `assert_equal(...)` checks
  for `config_dir` and `data_dir`, placed after day-window assertions and before
  command synthesis.
- `expected_imported_review_workflow_command_parts(...)` is fed
  `expected_config_dir` and `expected_data_dir`, not payload values. Defaults
  preserve unit-fixture behavior.

**3. `run_first_run_flow(context)` threads real smoke paths** -
`scripts/check_first_run_smoke.py:2406-2411`
- Passes `expected_config_dir=str(context.config_dir)` and
  `expected_data_dir=str(context.data_dir)`. Matches design exactly.

**4. Deterministic test emits real builder JSON with context paths** -
`tests/test_first_run_smoke.py:3595-3600`
- Uses `build_imported_review_workflow(...).model_dump_json()` with
  `config_dir=context.config_dir`, `data_dir=context.data_dir`,
  `as_of=smoke.AS_OF`, and `source_name=smoke.SOURCE_NAME`. Matches plan Task 3
  Step 4.

**5. Existing labels unchanged** - Confirmed via diff. Command argv drift test,
coordinated metadata drift test, step metadata, and heat-final labels are
untouched. New `config_dir` / `data_dir` labels follow the same
`{command_name} {field}` convention.

**6. Runtime CLI behavior unchanged** - `src/fashion_radar/imported_review_workflow.py`
has zero changes. Only the smoke checker and its tests were modified.

### Verification run

| Check | Result |
|---|---|
| `imported_review_workflow and (config_dir_drift or data_dir_drift)` | 2 passed |
| `imported_review_workflow or deterministic_local_command_sequence` | 19 passed |
| Full `tests/test_first_run_smoke.py` | 123 passed |
| `python scripts/check_first_run_smoke.py --repo-root .` | `First-run sample smoke passed.` |
| `ruff check` + `ruff format --check` | All checks passed; 2 files already formatted |
| `git diff --check` | Clean |

The change is minimal, well-scoped, and faithful to the spec. Ready to commit.
