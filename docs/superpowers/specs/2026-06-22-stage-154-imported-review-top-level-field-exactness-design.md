# Stage 154 Imported Review Top-Level Field Exactness Design

## Goal

Harden `imported-review-workflow` first-run smoke validation so the top-level
`config_dir` and `data_dir` fields are checked against caller-supplied expected
values instead of being reused to synthesize expected command argv.

## Background

`validate_imported_review_workflow()` already pins:

- execution mode
- step count
- step names
- exact per-step `order`, `name`, `purpose`, and `suggested_effect` metadata
- top-level `as_of`, `source_name`, `lookback_days`, `current_days`, and
  `baseline_days`
- exact command argv for every workflow step
- final heat-movers step placement

It does not yet assert the top-level `config_dir` or `data_dir` fields directly.
Instead, it reads those values from the payload and uses them to synthesize the
expected command argv. Consistent drift in those fields and in the commands can
therefore pass validation.

The unit fixture uses `configs` and `data`, while the real first-run smoke flow
uses temporary config/data directories from `SmokeContext`. The validator should
therefore keep fixture defaults for unit tests and accept explicit expected
paths from the real smoke flow.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 154 plan/review artifacts

Do not change:

- `src/fashion_radar/imported_review_workflow.py`
- CLI behavior
- dashboard behavior
- import/runtime semantics

## Design

Change `validate_imported_review_workflow()` to accept keyword-only expected
path values:

```python
def validate_imported_review_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
```

After the existing top-level day-window assertions and before command synthesis,
assert the fields directly:

```python
    assert_equal(
        f"{command_name} config_dir",
        payload.get("config_dir"),
        expected_config_dir,
    )
    assert_equal(
        f"{command_name} data_dir",
        payload.get("data_dir"),
        expected_data_dir,
    )
```

Then build the expected command argv from `expected_config_dir` and
`expected_data_dir` instead of payload-derived values:

```python
    expected_commands = expected_imported_review_workflow_command_parts(
        config_dir=expected_config_dir,
        data_dir=expected_data_dir,
        as_of=as_of,
        source_name=source_name,
        lookback_days=lookback_days,
        current_days=current_days,
        baseline_days=baseline_days,
    )
```

In `run_first_run_flow()`, pass the real smoke context paths:

```python
    validate_imported_review_workflow(
        "imported-review-workflow",
        imported_review_workflow,
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
```

Update `test_run_first_run_flow_uses_deterministic_local_command_sequence()` so
the fake `imported-review-workflow` stdout uses the test context paths:

```python
"imported-review-workflow": build_imported_review_workflow(
    config_dir=context.config_dir,
    data_dir=context.data_dir,
    as_of=smoke.AS_OF,
    source_name=smoke.SOURCE_NAME,
).model_dump_json(),
```

## TDD Strategy

Add two focused RED tests near the existing imported-review workflow tests.
Each test mutates one top-level path field and rewrites matching command
fragments so command argv remains internally consistent with the drifted
payload.

Config-dir drift:

```python
def test_validate_imported_review_workflow_rejects_config_dir_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["config_dir"] = "other-configs"
    replace_workflow_command_fragments(
        payload,
        {"--config-dir configs": "--config-dir other-configs"},
    )

    with pytest.raises(smoke.SmokeError, match="imported-review-workflow config_dir"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

Data-dir drift:

```python
def test_validate_imported_review_workflow_rejects_data_dir_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["data_dir"] = "other-data"
    replace_workflow_command_fragments(
        payload,
        {"--data-dir data": "--data-dir other-data"},
    )

    with pytest.raises(smoke.SmokeError, match="imported-review-workflow data_dir"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

Before implementation, both tests should fail with `DID NOT RAISE` because the
validator still reuses payload paths to synthesize expected command argv. After
implementation, both should pass. Existing command-specific and metadata-specific
drift tests should keep their current labels.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and (config_dir_drift or data_dir_drift)"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "deterministic_local_command_sequence"
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```
