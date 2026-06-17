# Stage 76 Code Review Prompt

Review the current Stage 76 implementation in `/home/ubuntu/fashion-radar`.

Use a code-review stance. Lead with Critical or Important findings if present;
include Minor notes after. Do not propose adding scraping, connectors, browser
automation, platform APIs, login/cookie/session/token/proxy behavior, CAPTCHA
handling, media download, monitoring/scheduling, source acquisition, demand
proof, ranking, coverage verification, or compliance-review product behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Stage 76 hardens the first-run smoke validator for
`external-tool-adapters --format json` so it catches drift in JSON key order,
adapter descriptions, upstream examples, field mappings, full recommended
command strings, adapter boundaries, and registry boundaries.

## Expected Scope

- `scripts/check_first_run_smoke.py`
  - Sets smoke-local `FASHION_RADAR_CONFIG_DIR=configs` and
    `FASHION_RADAR_DATA_DIR=data` so the print-only adapter registry emits
    deterministic command paths in source and installed smoke modes.
  - Adds static full-contract expected constants and expected command helpers.
  - Extends `validate_external_tool_adapters` without breaking the Stage 73
    command/readiness diagnostic precedence.
- `tests/test_first_run_smoke.py`
  - Adds env-var coverage.
  - Adds smoke-helper-to-fixture-helper parity coverage.
  - Adds parameterized negative tests for the newly checked full-contract drift
    families.
- Stage 76 design/plan/plan-review/code-review artifacts.

Runtime `src/`, public docs, dependency manifests, and lockfiles should be
unchanged.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_command_environment_sets_deterministic_adapter_registry_dirs tests/test_first_run_smoke.py::test_expected_external_tool_adapter_commands_match_fixture_helper tests/test_first_run_smoke.py::test_validate_external_tool_adapters_rejects_full_static_contract_drift tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
# 17 passed

uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
# 67 passed

uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed.

uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
# All checks passed

uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
# 2 files already formatted

uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed

git diff --check
# passed

uv --no-config run --frozen pytest
# 1114 passed
```

## Review Questions

1. Does the validator now cover the full static adapter registry contract
   claimed by Stage 76?
2. Are Stage 73 command/readiness diagnostic labels still preserved?
3. Does the smoke-local env var change keep source and installed smoke behavior
   deterministic without changing runtime CLI behavior?
4. Are the new tests strong enough and localized enough?
5. Are runtime behavior, dependencies, public docs, and external-platform
   behavior unchanged?
6. Are there any Critical or Important issues to fix before commit?
