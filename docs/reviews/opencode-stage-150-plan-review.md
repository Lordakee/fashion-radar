# Stage 150 Plan Review

## Findings

**No blocking issues.** The plan is sound and ready to implement.

### RED To GREEN Transition

`validate_external_tool_workflow()` and `validate_external_tool_readiness()` currently verify `display_name` only through the top-level key-order list. Neither validator asserts its value.

Mutating `payload["display_name"] = "Unexpected Export Label"` leaves every other pinned field untouched, so the current validators return normally and the new test fails with `DID NOT RAISE`. After adding exact equality, the failure message includes `display_name`, satisfying the planned `pytest.raises(..., match="display_name")`.

### Pinned Value

The pinned value `Rednote MCP Export` matches every source of truth:

- runtime adapter metadata for `rednote_mcp`
- `build_external_tool_workflow()` output
- `build_external_tool_readiness()` output
- first-run workflow fixture
- first-run readiness fixture

### Existing Errors

The planned assertions are additive and land between existing platform-label and input-format assertions. Existing targeted metadata checks for contract version, execution mode, adapter id, platform label, input format, pattern, as_of, source name, and step/check counts remain intact.

### Runtime Scope

Runtime behavior remains unchanged. The plan limits edits to the smoke checker, tests, and Stage 150 review artifacts.

### Verification

Focused verification is sufficient for the touched files and is followed by the full release gate. The narrower plan selector `-k "display_name_drift"` is preferable for RED/GREEN evidence.

## Verdict

Proceed to implementation.
