Let me continue reading the test file to find the existing tests and the smoke flow function in the script.
Let me read the `run_first_run_flow` function and the deterministic smoke-flow test.
I have enough context to complete the review. Let me verify one last detail about how the existing command-argv drift test for `review_imported_candidate_phrases` interacts with the new top-level assertion.

The test at `tests/test_first_run_smoke.py:1981` drifts only the candidate step command (`--config-dir configsets`) without changing `payload["config_dir"]`. After the plan change, the top-level assertion passes (`"configs" == "configs"`), and command synthesis still catches the drift via the candidate command label. Good.

## Review Findings

**No blocking issues.** The plan is sound across all six review dimensions.

### Detailed Assessment

**1. RED tests isolate top-level field assertions correctly** — `tests/test_first_run_smoke.py:741` (`replace_workflow_command_fragments`) rewrites every matching command fragment, so the drifted payload is internally consistent:
- `{"--config-dir configs": "--config-dir other-configs"}` rewrites all 3 occurrences (steps 2, 5, 7 of `imported_review_workflow_payload` at `tests/test_first_run_smoke.py:587,622,644`).
- `{"--data-dir data": "--data-dir other-data"}` rewrites all 7 occurrences.

Under the current validator (`scripts/check_first_run_smoke.py:1055-1056`), these drifts pass because expected argv is synthesized from the payload. After the change, the explicit `assert_equal` at the proposed location catches them with the `"{command_name} config_dir"` / `"{command_name} data_dir"` labels (`scripts/check_first_run_smoke.py:499-501`). Match strings align.

**2. Validator signature and `run_smoke(context)` threading is correct** — defaults `expected_config_dir="configs"` / `expected_data_dir="data"` match `imported_review_workflow_payload()` defaults (`tests/test_first_run_smoke.py:567-568`), so existing unit tests remain valid without kwargs. The `run_first_run_flow` call site at `scripts/check_first_run_smoke.py:2400` receives the payload from the real CLI invoked with `--config-dir str(context.config_dir)` (`scripts/check_first_run_smoke.py:2389`), so `str(context.config_dir)` is the correct expected value.

**3. Deterministic smoke-flow test uses temp-path payloads** — replacing `json.dumps(imported_review_workflow_payload())` at `tests/test_first_run_smoke.py:3571` with `build_imported_review_workflow(config_dir=context.config_dir, data_dir=context.data_dir, as_of=smoke.AS_OF, source_name=smoke.SOURCE_NAME).model_dump_json()` mirrors the existing `community-handoff-workflow` pattern at `tests/test_first_run_smoke.py:3572-3580`. `build_imported_review_workflow` accepts `Path` and `str | datetime` (`src/fashion_radar/imported_review_workflow.py:38-46`), and normalizes `AS_OF="2026-06-13T12:00:00Z"` to `"2026-06-13T12:00:00+00:00"` matching `EXPECTED_WORKFLOW_AS_OF`. `build_imported_review_workflow` is already imported at `tests/test_first_run_smoke.py:22`.

**4. Existing labels remain unchanged** — the plan adds two new labels (`config_dir`, `data_dir`) without renaming `step metadata`, `summary command`, `candidate command`, etc. The parametrized command-argv drift test at `tests/test_first_run_smoke.py:1981` (which drifts only the candidate step's `--config-dir` to `configsets` without touching `payload["config_dir"]`) still resolves to the `"candidate command"` label because the top-level assertion passes and command synthesis catches the mismatch. Same for the coordinated-drift test at `tests/test_first_run_smoke.py:2027`.

**5. Direct script verification is included** — `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .` appears in Task 3 Step 7, Task 4 Step 1, and the Task 4 Step 4 release gate.

**6. Runtime behavior remains unchanged** — scope (`docs/superpowers/specs/2026-06-22-stage-154-imported-review-top-level-field-exactness-design.md:34-45`) restricts modifications to `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and review artifacts. `src/fashion_radar/imported_review_workflow.py` is untouched.

### Minor Non-blocking Observations

- **TDD ordering is correct**: Task 3 Step 3 (thread runtime paths) and Step 4 (update deterministic payload) must both land before the deterministic test passes; the plan sequences them properly and runs `-k "deterministic_local_command_sequence"` only in Step 7 after both are in place.
- **Local cleanup**: removing `config_dir = str(payload.get("config_dir", ""))` and `data_dir = str(payload.get("data_dir", ""))` at `scripts/check_first_run_smoke.py:1055-1056` avoids ruff F841 unused-variable warnings; the synthesis call cleanly switches to `expected_config_dir` / `expected_data_dir`.
- **Integration coverage**: the real `python scripts/check_first_run_smoke.py --repo-root .` invocation is the end-to-end check that the live CLI's `config_dir`/`data_dir` output matches what the validator now pins; unit tests alone cannot prove this.

Proceed to implementation.
