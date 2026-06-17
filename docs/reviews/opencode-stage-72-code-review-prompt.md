# Stage 72 Code Review Prompt

Review the Stage 72 implementation in `/home/ubuntu/fashion-radar`.

Use a code-review stance. Lead with Critical or Important findings if present;
Minor notes may follow. Do not propose adding scraping, connectors, browser
automation, platform APIs, login/cookie/session/token/proxy behavior, CAPTCHA
handling, media download, monitoring/scheduling, source acquisition, demand
proof, ranking, coverage verification, or compliance-review product behavior.

## Goal

Broaden the `external-tool-adapters --format json` CLI contract test so every
registered adapter is covered, not just the first `rednote_mcp` adapter.

## Changed Files

- `tests/test_cli.py`
- `docs/superpowers/specs/2026-06-18-stage-72-adapter-json-contract-design.md`
- `docs/superpowers/plans/2026-06-18-stage-72-adapter-json-contract-plan.md`
- `docs/reviews/opencode-stage-72-plan-review-prompt.md`
- `docs/reviews/opencode-stage-72-plan-review.md`
- `docs/reviews/opencode-stage-72-code-review-prompt.md`

## Implementation Summary

`tests/test_cli.py::test_external_tool_adapters_command_prints_json` now:

- Keeps top-level contract and execution-mode assertions.
- Pins all seven adapter ids through an ordered `expected_adapters` mapping.
- Asserts every serialized adapter has the stable JSON key order.
- Asserts `display_name`, `platform_label`, `suggested_source_name`,
  `recommended_input_format`, `recommended_pattern`,
  `suggested_export_directory`, non-empty `upstream_tool_examples`, and shared
  `field_mappings`.
- Asserts every recommended command starts with `fashion-radar` and follows the
  expected command-name sequence.
- Asserts every adapter's `external-tool-readiness` command carries the
  expected adapter-specific and shared flags.
- Uses `flag_value(parts, flag)` outside the loop to avoid ruff bugbear B023.
- The implementation also pins `display_name` and asserts command prefixes with
  `parts[:2]` rather than only `parts[1]`.
- It also collects `--config-dir` and `--data-dir` values across all adapter
  readiness commands and asserts each remains cross-adapter consistent.

No runtime code was changed.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json -q
# 1 passed in 0.69s after final reviewer Minor fixes

uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_adapters or external_tool_template or external_tool_workflow or external_tool_readiness"
# 29 passed, 269 deselected in 1.32s after final reviewer Minor fixes

uv --no-config run --frozen ruff check tests/test_cli.py
# All checks passed!

uv --no-config run --frozen ruff format --check tests/test_cli.py
# 1 file already formatted

uv --no-config run --frozen pytest tests/test_cli.py -q
# 298 passed in 11.89s

uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed.

git diff --check
# passed

uv --no-config run --frozen pytest
# 1099 passed in 27.75s
```

## Review Questions

1. Does the implementation cover all seven adapters without broadening runtime
   behavior?
2. Are the expected values and command sequence correct for the current
   registry?
3. Are there any Critical or Important issues that must be fixed before commit?
