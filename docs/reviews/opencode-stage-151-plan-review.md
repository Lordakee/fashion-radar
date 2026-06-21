# Stage 151 Plan Review

## Findings

**No blocking issues.** The imported-review step metadata exactness plan is sound and safe to implement.

### Low Finding Addressed

The plan originally pinned `order`, `name`, `purpose`, and `suggested_effect`, but only included RED tests for `purpose` and `suggested_effect`. The review noted that `order` drift is also currently accepted and should have direct RED coverage. The plan and design were updated to add `test_validate_imported_review_workflow_rejects_step_order_drift()`.

### RED To GREEN Behavior

The current `validate_imported_review_workflow()` checks execution mode, step count, step names, top-level as_of/source/window metadata, command argv, and final heat-movers name. It does not inspect per-step `order`, `purpose`, or `suggested_effect`. Therefore populated metadata drift currently passes and produces `DID NOT RAISE`. After exact metadata equality is added, the validator raises a `SmokeError` labeled `step metadata`.

### Pinned Metadata

The expected `order`, `name`, `purpose`, and `suggested_effect` values match both:

- `src/fashion_radar/imported_review_workflow.py`
- `tests/test_first_run_smoke.py` fixture `imported_review_workflow_payload()`

The existing fixture parity test already ties the fixture to the runtime builder.

### Existing Command Drift Tests

Existing command-argv drift tests mutate only `command`, leaving metadata untouched. The new metadata equality check passes for those cases, so the existing command-specific failure labels still surface.

### Runtime Scope

Runtime behavior remains unchanged. The implementation is scoped to the first-run smoke checker, tests, and Stage 151 review artifacts.

### Verification

Focused verification is sufficient: new RED/GREEN tests, all imported-review workflow tests, the full first-run smoke file, ruff, format, and `git diff --check`, followed by the full release gate.

## Verdict

Proceed to implementation.
