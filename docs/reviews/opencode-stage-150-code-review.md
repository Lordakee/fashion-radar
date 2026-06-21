# Stage 150 Code Review

## Findings

**No blocking issues.** The change is correct, minimal, and the RED-to-GREEN transition is proven for both validators.

### 1. New Test Proves The Prior Gap

`tests/test_first_run_smoke.py` parametrizes both `validate_external_tool_workflow()` and `validate_external_tool_readiness()` with the same mutation: `payload["display_name"] = "Unexpected Export Label"`.

The mutation changes a value, not a key, so the old key-order checks do not catch it. Earlier value assertions use unmutated fixture values and pass, so the current-base validator reaches the end and returns normally. The RED run against base `e4a59d0` failed both parametrizations with `DID NOT RAISE`.

### 2. Both Validators Check Exact Display-Name Equality

`validate_external_tool_workflow()` and `validate_external_tool_readiness()` now assert:

```python
payload.get("display_name") == EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME
```

The shared constant is `Rednote MCP Export`, matching runtime adapter metadata, the checker adapter tuple, and both first-run fixtures. The `assert_equal` label contains `display_name`, so the test regex matches the new failure path.

### 3. Existing Metadata Errors Remain Intact

The diff is additive in both validator bodies. Existing assertions for contract version, execution mode, adapter id, platform label, input format, pattern, as_of, source name, step count, and key order remain untouched.

### 4. Runtime Behavior Unchanged

No `src/` files changed. Runtime workflow, readiness, adapter, CLI, and model code remain untouched.

### 5. Verification Coverage Is Sufficient

Focused verification passed:

- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "display_name"` - 2 passed
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness"` - 30 passed
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q` - 112 passed
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py` - clean
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py` - clean
- `git diff --check` - clean

### Non-Blocking Observation

The literal `Rednote MCP Export` now appears in several pinned smoke-contract locations. This is consistent with the current first-run smoke approach, but future display-name changes must update all pinned copies together.

## Verdict

Proceed to the full release gate and commit.
