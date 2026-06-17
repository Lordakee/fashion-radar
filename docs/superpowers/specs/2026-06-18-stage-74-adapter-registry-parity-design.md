# Stage 74 Adapter Registry Parity Design

## Goal

Make the first-run smoke test fixture for `external-tool-adapters --format json`
directly comparable with the runtime adapter registry output.

## Context

Stage 73 hardened `scripts/check_first_run_smoke.py::validate_external_tool_adapters`
so the smoke validator checks all seven adapter entries, public metadata, the
exact recommended command prefix sequence, and readiness command flags. The
fixture in `tests/test_first_run_smoke.py::external_tool_adapters_payload`
remains hand-built and intentionally independent from the smoke validator, but
there is not yet a direct test that compares that fixture with
`build_external_tool_adapter_registry(...)` for the same inputs.

Nearby fixtures already have this kind of parity coverage:

- `external_tool_template_payload` vs `build_external_tool_template`
- `external_tool_workflow_payload` vs `build_external_tool_workflow`
- `external_tool_readiness_payload` vs `build_external_tool_readiness`

## Scope

In scope:

- Update `tests/test_first_run_smoke.py` only.
- Import `build_external_tool_adapter_registry`.
- Make `external_tool_adapters_payload()` match the runtime registry JSON for
  the same deterministic inputs:
  - `directory=Path("./exports")`
  - `config_dir=Path("./configs")`
  - `data_dir=Path("./data")`
  - `as_of="2026-06-13T12:00:00Z"`
- Add `test_external_tool_adapters_payload_matches_real_registry`.
- Preserve Stage 73 negative tests and first-run flow behavior.

Out of scope:

- Runtime CLI or adapter registry behavior changes.
- Adding connectors, scraping, browser automation, platform APIs,
  login/cookie/session/token/proxy/CAPTCHA behavior, media downloads,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product behavior.

## Design

Add the runtime registry import near the other external-tool imports:

```python
from fashion_radar.external_tool_adapters import build_external_tool_adapter_registry
```

Update the test fixture helper data so `external_tool_adapters_payload()` is a
full-fidelity JSON equivalent of:

```python
json.loads(
    build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    ).model_dump_json()
)
```

That likely means replacing the Stage 73 generic fixture fields with exact
runtime values for:

- adapter `description`
- `upstream_tool_examples`
- `field_mappings` notes and required flags
- adapter `boundaries`
- registry-level `boundaries`

Then add the parity test near the existing external-tool fixture parity tests:

```python
def test_external_tool_adapters_payload_matches_real_registry() -> None:
    expected = json.loads(
        build_external_tool_adapter_registry(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        ).model_dump_json()
    )

    assert external_tool_adapters_payload() == expected
```

## Test Strategy

- Run the new parity test and expect it to fail before fixture-fidelity changes.
- Update the fixture to match runtime JSON exactly.
- Run:
  - `tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry`
  - `tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract`
  - `tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence`
  - `tests/test_first_run_smoke.py -q`
  - Ruff check/format on `tests/test_first_run_smoke.py`
  - release hygiene, `git diff --check`, and full pytest

## Acceptance Criteria

- The new parity test passes.
- The Stage 73 adapter contract negative tests still pass.
- The deterministic first-run command sequence remains unchanged.
- Runtime/source files remain untouched.
