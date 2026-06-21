# Stage 156 External Tool Path Exactness Design

## Goal

Harden first-run smoke validation for `external-tool-workflow` and
`external-tool-readiness` so their top-level `directory`, `config_dir`, and
`data_dir` fields are checked against caller-supplied expected values instead of
being reused from the payload to synthesize expected nested command argv.

## Background

The real first-run smoke flow invokes both commands with runtime temp paths from
`SmokeContext`:

- `external-tool-workflow --directory <context.exports_dir> --config-dir <context.config_dir> --data-dir <context.data_dir>`
- `external-tool-readiness --directory <context.exports_dir> --config-dir <context.config_dir> --data-dir <context.data_dir>`

The current validators only check that those path fields are present/non-empty,
then use the payload values to validate nested recommended commands. Coordinated
drift in the top-level fields and every generated command can therefore pass.

Recent stages already closed the same gap for:

- `community-handoff-workflow`
- `imported-review-workflow`

Stage 156 applies that same explicit expected-path pattern to the remaining
external-tool workflow surfaces.

## Scope

Modify only:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 156 plan/review artifacts

Do not change:

- `src/fashion_radar/external_tool_workflow.py`
- `src/fashion_radar/external_tool_readiness.py`
- CLI behavior
- builder behavior
- lockfiles

The production builders already stringify supplied paths once and use those
strings consistently in top-level fields and generated commands.

## Design

Update `validate_external_tool_workflow()`:

```python
def validate_external_tool_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "exports",
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
```

Replace the current non-empty-only path checks with direct assertions:

```python
assert_equal(f"{command_name} directory", payload.get("directory"), expected_directory)
assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
assert_equal(f"{command_name} data_dir", payload.get("data_dir"), expected_data_dir)
```

Then synthesize expected nested commands from the explicit expected values:

```python
directory = expected_directory
config_dir = expected_config_dir
data_dir = expected_data_dir
```

Apply the same signature and assertion pattern to
`validate_external_tool_readiness()`.

In `run_first_run_flow()`, pass runtime context paths into both validators:

```python
validate_external_tool_workflow(
    "external-tool-workflow",
    external_tool_workflow,
    expected_directory=str(context.exports_dir),
    expected_config_dir=str(context.config_dir),
    expected_data_dir=str(context.data_dir),
)
```

```python
validate_external_tool_readiness(
    "external-tool-readiness",
    external_tool_readiness,
    expected_directory=str(context.exports_dir),
    expected_config_dir=str(context.config_dir),
    expected_data_dir=str(context.data_dir),
)
```

## Test Strategy

Add a test helper in `tests/test_first_run_smoke.py` that rewrites external-tool
payload paths by argv token, not raw string replacement:

```python
def rewrite_external_tool_payload_paths(
    payload: dict[str, object],
    *,
    directory: str = "exports",
    config_dir: str = "configs",
    data_dir: str = "data",
) -> None:
    payload["directory"] = directory
    payload["config_dir"] = config_dir
    payload["data_dir"] = data_dir
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        command = step.get("command")
        assert isinstance(command, str)
        parts = shlex.split(command)
        rewritten = [
            directory
            if part == "exports"
            else config_dir
            if part == "configs"
            else data_dir
            if part == "data"
            else part
            for part in parts
        ]
        step["command"] = shlex.join(rewritten)
```

Add RED tests proving coordinated top-level + command drift is rejected for both
validators and all three path fields:

- `directory`
- `config_dir`
- `data_dir`

Add acceptance tests proving the validators can accept explicit runtime path
expectations.

Update `test_run_first_run_flow_uses_deterministic_local_command_sequence()` so
the fake stdout for `external-tool-workflow` and `external-tool-readiness` uses
payloads rewritten to that test's temp `context` paths. Keep the existing static
default fixtures for builder parity tests.

## Verification

Focused RED/GREEN:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_surfaces_reject_coordinated_top_level_path_drift or external_tool_surfaces_accept_explicit_runtime_paths"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness or first_run_flow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
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
