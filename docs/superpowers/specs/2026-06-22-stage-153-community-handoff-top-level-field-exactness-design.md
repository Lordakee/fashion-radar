# Stage 153 Community Handoff Top-Level Field Exactness Design

## Goal

Harden `community-handoff-workflow` first-run smoke validation so the top-level
`directory`, `config_dir`, and `data_dir` fields are pinned exactly instead of
being reused to synthesize expected command argv.

## Background

`validate_community_handoff_workflow()` already pins:

- execution mode
- step count
- step names
- top-level `input_format`, `pattern`, `as_of`, and `source_name`
- exact command argv for every step
- specific `suggested_effect` values for the import and post-import review
  steps
- exact per-step `order`, `name`, `purpose`, and `suggested_effect` metadata

It does not yet assert the top-level `directory`, `config_dir`, or `data_dir`
fields directly. Instead, it reads those values back out of the payload and uses
them to synthesize the expected command argv. That means drift in those fields
can still pass as long as the commands remain internally consistent with the
mutated payload.

The runtime builder and smoke fixture already agree on the current fixture
values, and the fixture parity test already locks the fixture to the runtime
builder for those fixed inputs. The real smoke flow, however, runs against a
temporary export/config/data tree, so the validator must receive the expected
paths from its caller.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 153 plan/review artifacts

Do not change:

- `src/fashion_radar/community_handoff_workflow.py`
- CLI behavior
- dashboard behavior
- import/runtime semantics

The new top-level field assertions must be added before command synthesis in
`validate_community_handoff_workflow()` so the exact field labels fire before
any command-specific checks. The validator should accept the expected path
values as keyword-only arguments so `run_smoke(context)` can pass the real
temporary runtime paths while the unit tests continue to use the fixture
values.

## Design

In `validate_community_handoff_workflow()`, keep the current top-level metadata
assertions and add exact field checks before command synthesis:

```python
def validate_community_handoff_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "/tmp/export",
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
    ...
    assert_equal(
        f"{command_name} directory",
        payload.get("directory"),
        expected_directory,
    )
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

Then use the pinned constants when building the expected command argv:

```python
    expected_commands = expected_community_handoff_workflow_command_parts(
        directory=expected_directory,
        input_format=input_format,
        pattern=pattern,
        config_dir=expected_config_dir,
        data_dir=expected_data_dir,
        as_of=as_of,
        source_name=source_name,
    )
```

This removes the validator's dependence on payload-provided path fields while
keeping command validation exact and preserving the current import/post-review
effect labels.

In `run_first_run_flow()`, pass the actual smoke context paths:

```python
    validate_community_handoff_workflow(
        "community-handoff-workflow",
        community_handoff_workflow,
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
```

The deterministic first-run flow unit test must also return a
`community-handoff-workflow` payload built from its temp `context` paths instead
of the fixed fixture payload:

```python
"community-handoff-workflow": build_community_handoff_workflow(
    directory=context.exports_dir,
    config_dir=context.config_dir,
    data_dir=context.data_dir,
    input_format="csv",
    pattern=smoke.DIR_PATTERN,
    as_of=smoke.AS_OF,
    source_name=smoke.SOURCE_NAME,
).model_dump_json(),
```

## TDD Strategy

Add three focused RED tests near the existing community handoff workflow tests.

Directory drift:

```python
def test_validate_community_handoff_workflow_rejects_directory_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["directory"] = "/tmp/other-export"
    replace_workflow_command_fragments(
        payload,
        {"/tmp/export": "/tmp/other-export"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow directory"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

Config-dir drift:

```python
def test_validate_community_handoff_workflow_rejects_config_dir_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["config_dir"] = "other-configs"
    replace_workflow_command_fragments(
        payload,
        {"--config-dir configs": "--config-dir other-configs"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow config_dir"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

Data-dir drift:

```python
def test_validate_community_handoff_workflow_rejects_data_dir_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["data_dir"] = "other-data"
    replace_workflow_command_fragments(
        payload,
        {"--data-dir data": "--data-dir other-data"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow data_dir"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

These tests should fail before implementation because the current validator
derives expected commands from the payload's path fields instead of asserting
them directly. After the change, they should pass. Existing command-specific
drift tests should remain unchanged because the validator receives the expected
runtime paths from `run_smoke(context)` and the tests continue to use the
fixture paths.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and (directory_drift or config_dir_drift or data_dir_drift)"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
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
