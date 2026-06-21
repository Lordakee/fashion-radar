# Stage 150 Display Name Exactness Design

## Goal

Harden `external-tool-workflow` and `external-tool-readiness` first-run smoke validation so their user-facing `display_name` fields must match the pinned first-run contract exactly.

## Background

`validate_external_tool_workflow()` and `validate_external_tool_readiness()` already pin most top-level contract metadata:

- contract version
- execution mode
- adapter id
- platform label
- input format
- pattern
- as_of
- source_name
- step/check counts
- step/check shape
- step/check commands and boundaries

Both validators include `display_name` in the required key order, but neither asserts its exact value. That leaves a small but real hole: a populated yet misleading label like `"Unexpected Export Label"` would still pass, even though the first-run smoke fixture and runtime builder both pin `"Rednote MCP Export"`.

Stage 150 closes that gap with exact equality for the top-level `display_name` field in both validators while leaving the runtime behavior unchanged.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 150 plan/review artifacts

Do not change runtime builders, CLI behavior, external integrations, scheduling, dashboard behavior, or compliance-review product features.

## Design

Add a pinned display-name constant beside the existing workflow/readiness metadata constants:

```python
EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME = "Rednote MCP Export"
```

In `validate_external_tool_workflow()`, after the existing `display_name` key-order check and before any downstream command parsing, add:

```python
    assert_equal(
        f"{command_name} display_name",
        payload.get("display_name"),
        EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME,
    )
```

In `validate_external_tool_readiness()`, add the same assertion after the existing top-level metadata assertions:

```python
    assert_equal(
        f"{command_name} display_name",
        payload.get("display_name"),
        EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME,
    )
```

This preserves the existing targeted failure messages for contract version, execution mode, adapter id, platform label, input format, pattern, source name, and step/check counts while rejecting a wrong user-facing title.

## TDD Strategy

Add one focused RED test that mutates both payload types and confirms the new exactness path.

```python
@pytest.mark.parametrize(
    ("payload_fn", "validator", "command_name"),
    [
        (external_tool_workflow_payload, smoke.validate_external_tool_workflow, "external-tool-workflow"),
        (external_tool_readiness_payload, smoke.validate_external_tool_readiness, "external-tool-readiness"),
    ],
)
def test_validate_external_tool_surfaces_reject_display_name_drift(
    payload_fn, validator, command_name
) -> None:
    payload = payload_fn()
    payload["display_name"] = "Unexpected Export Label"

    with pytest.raises(smoke.SmokeError, match="display_name"):
        validator(command_name, payload)
```

Before implementation, both cases should fail with `DID NOT RAISE`, because the current validators only require `display_name` to be present in the key list.

After implementation, both cases should pass because the wrong label no longer equals the pinned expected title.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "display_name"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```
