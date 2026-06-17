# Stage 76 Adapter Smoke Full Contract Design

## Goal

Harden the first-run smoke validator for `external-tool-adapters --format json`
so it validates the full static adapter registry JSON surface that the smoke
already receives from the CLI.

## Context

Stage 73 made `scripts/check_first_run_smoke.py::validate_external_tool_adapters`
loop all seven adapters and validate adapter order, core public metadata,
recommended command prefix order, shell parseability, and the
`external-tool-readiness` command flags.

Stage 74 made `tests/test_first_run_smoke.py::external_tool_adapters_payload()`
match `build_external_tool_adapter_registry(...).model_dump_json()` exactly for
deterministic local inputs.

Stage 75 documented the complete public adapter matrix and first-run smoke
registry-contract claim.

The remaining smoke gap is that the release smoke script itself does not yet
validate the full registry JSON surface. It still misses:

- exact top-level key order;
- exact adapter key order;
- registry-level `boundaries`;
- adapter `description`;
- adapter `upstream_tool_examples`;
- adapter `field_mappings`;
- full adapter `recommended_commands` strings;
- adapter-level `boundaries`.

The fixture parity test catches fixture/runtime drift, but the actual first-run
smoke path can still miss drift in those fields. Stage 76 should close that gap
without importing runtime registry code into the smoke script.

The smoke also currently invokes `external-tool-adapters --format json` without
explicit `--config-dir` or `--data-dir` flags. The CLI would therefore render
platformdirs user paths in printed recommended commands. To keep the command
sequence unchanged while making the full-command expectation deterministic, the
smoke command environment should set `FASHION_RADAR_CONFIG_DIR=configs` and
`FASHION_RADAR_DATA_DIR=data`. These are local environment defaults for the
smoke process only; they do not alter runtime code or execute generated
commands.

## Scope

In scope:

- Update `scripts/check_first_run_smoke.py`.
- Update `tests/test_first_run_smoke.py`.
- Add static expected values and helper functions to the smoke script.
- Add focused parameterized negative tests proving the validator rejects drift
  across the full static adapter contract.
- Set smoke-local config/data env vars so the print-only adapter registry emits
  deterministic `configs` and `data` handoff paths.
- Preserve the single existing `external-tool-adapters --format json` smoke
  command in `run_first_run_flow()`.

Out of scope:

- Runtime CLI or adapter registry behavior changes.
- Public documentation or changelog changes.
- Dependency changes.
- Changing the first-run command sequence.
- Running generated recommended commands.
- Adding connectors, scraping, browser automation, platform APIs,
  login/cookie/session/token/proxy/CAPTCHA behavior, media downloads,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product behavior.

## Design

Keep the existing `EXPECTED_EXTERNAL_TOOL_ADAPTERS` map as the adapter-order and
core metadata source. Add static expectations near it for:

- top-level registry key order;
- adapter key order;
- adapter descriptions and upstream tool examples;
- shared field mappings;
- adapter boundaries;
- registry boundaries.

Set `FASHION_RADAR_CONFIG_DIR` and `FASHION_RADAR_DATA_DIR` inside
`command_environment(...)` before the source-checkout branch. Use the relative
strings `configs` and `data` so both source-checkout and installed-wheel smoke
modes make the print-only adapter registry emit deterministic local handoff
paths while keeping all explicit command flags unchanged.

Add a helper that generates the full expected nine-command string list from the
same static adapter values using `shlex.join(...)`. This mirrors how the test
fixture and smoke-configured CLI output quote globs and multi-word source names,
while keeping the smoke script independent from
`fashion_radar.external_tool_adapters`.

Extend `validate_external_tool_adapters` without changing the existing
diagnostic precedence for Stage 73 checks:

1. Keep the existing payload type, `contract_version`, `execution_mode`,
   adapters-list, adapter object type, adapter id order, core metadata,
   `recommended_commands` type, shell parseability, command-prefix,
   readiness-count, and readiness-flag checks first.
2. After those existing checks have run for each adapter, assert each adapter
   object has the exact adapter key order with `list(adapter)`.
3. Still inside the per-adapter loop, assert:
   - `description` equals the pinned adapter description;
   - `upstream_tool_examples` equals the pinned adapter example list;
   - `field_mappings` equals the pinned shared mapping list;
   - `recommended_commands` equals the full generated command list;
   - `boundaries` equals the pinned adapter boundary list.
4. After the adapters have been validated, assert `list(payload)` equals the
   expected top-level key order and registry-level `boundaries` equals the
   pinned registry boundary list.

This is stricter than Stage 73 but preserves its core design: static smoke
expectations, no runtime registry imports, no generated command execution, and
the original Stage 73 shell/readiness error labels.

## Test Strategy

Add helper-driven parameterized negative tests in `tests/test_first_run_smoke.py`
instead of adding more cases to the already large Stage 73 test. Each case
starts from `external_tool_adapters_payload()`, mutates one contract family, and
asserts `validate_external_tool_adapters(...)` raises `SmokeError` with a
specific label:

- extra top-level key;
- missing registry boundary;
- extra adapter key;
- missing adapter description;
- later adapter description drift;
- upstream tool example drift;
- field mapping `required` drift;
- field mapping note drift;
- adapter boundary drift;
- later-adapter full non-readiness command string drift;
- readiness command extra flag drift.

Add a small helper-parity test proving the smoke script's expected command
helper returns the same strings as the existing fixture helper for one JSON
adapter and one CSV adapter. This makes the smoke helper drift visible without
importing runtime registry code into the smoke script.

Add a command-environment test proving the smoke sets
`FASHION_RADAR_CONFIG_DIR=configs` and `FASHION_RADAR_DATA_DIR=data` in both
source-checkout and installed modes. That test guards the end-to-end path that
caused the full-command comparison to depend on platformdirs defaults.

Run the new parameterized test before implementation and observe at least the
first case fail with `DID NOT RAISE`. Then implement the validator checks and
rerun the focused tests.

## Acceptance Criteria

- `validate_external_tool_adapters` rejects missing or extra registry keys,
  missing or extra adapter keys, registry boundary drift, adapter description
  drift, upstream examples drift, field mapping drift, full recommended command
  string drift, and adapter boundary drift.
- The existing Stage 73 adapter contract negative tests still pass with their
  current error-label expectations.
- The Stage 74 fixture-to-runtime registry parity test still passes.
- The deterministic first-run command sequence remains unchanged.
- The smoke command environment makes `external-tool-adapters --format json`
  print deterministic `configs`/`data` command arguments in both source and
  installed smoke modes.
- `src/`, public docs, dependency manifests, and lockfiles remain untouched.
