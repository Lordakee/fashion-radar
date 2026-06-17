# Stage 73 Adapter Smoke Contract Design

## Goal

Extend the first-run smoke validator so the `external-tool-adapters --format
json` smoke contract covers all seven adapter entries, not only the first
`rednote_mcp` entry.

## Context

Stage 72 hardened the CLI JSON test to validate every adapter in
`external-tool-adapters --format json`. The first-run smoke validator still
checks only `adapters[0]`, and its test fixture contains only one adapter. That
means the release smoke path can miss drift in later adapter entries even when
the direct CLI test is stronger.

## Scope

In scope:

- Update `scripts/check_first_run_smoke.py::validate_external_tool_adapters`.
- Update `tests/test_first_run_smoke.py::external_tool_adapters_payload`.
- Keep validation focused on static JSON contract, command parseability,
  registry-like public metadata, exact recommended command prefixes, readiness
  command presence, required readiness flags, adapter-specific `--adapter`,
  `--input-format`, `--pattern`, `--source-name`, and stable `--format table`
  output.
- Update existing negative tests so at least one later adapter failure proves
  the validator is no longer first-adapter-only.

Out of scope:

- Runtime CLI or adapter registry behavior changes.
- Adding connectors, scraping, browser automation, platform APIs,
  login/cookie/session/token/proxy/CAPTCHA behavior, media downloads,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product behavior.

## Design

Add a small expected-adapter map in `scripts/check_first_run_smoke.py`:

```python
EXPECTED_EXTERNAL_TOOL_ADAPTERS = {
    "rednote_mcp": ("rednote", "json", "*.json", "Rednote MCP Export"),
    "xiaohongshu_crawler": ("xiaohongshu", "csv", "*.csv", "Xiaohongshu Crawler Export"),
    "instaloader": ("instagram", "json", "*.json", "Instaloader Export"),
    "tiktok_api": ("tiktok", "json", "*.json", "TikTok-Api Export"),
    "yt_dlp": ("media", "json", "*.json", "yt-dlp Metadata Export"),
    "x_search_export": ("x", "csv", "*.csv", "X Search Export"),
    "generic_community_export": ("community", "csv", "*.csv", "Generic Community Export"),
}
```

Keep this map pinned independently of the runtime registry so the smoke script
can catch registry-output drift instead of importing the code under test.

Then refactor `validate_external_tool_adapters`:

- Require `adapters` to be a list of JSON objects.
- Assert adapter ids exactly match `EXPECTED_EXTERNAL_TOOL_ADAPTERS` order.
- Loop over every adapter.
- Assert public metadata fields match the pinned adapter values:
  `display_name`, `platform_label`, `suggested_source_name`,
  `recommended_input_format`, `recommended_pattern`, and
  `suggested_export_directory`.
- Require `recommended_commands` to be a list.
- Parse every recommended command and assert the exact nine
  `fashion-radar <command>` prefixes in order.
- Require exactly one adapter `external-tool-readiness` command.
- Assert the readiness command starts with
  `["fashion-radar", "external-tool-readiness"]`.
- Assert `--adapter`, `--directory`, `--input-format`, `--pattern`,
  `--source-name`, and `--format` match expectations.
- Require non-empty values for `--config-dir`, `--data-dir`, and `--as-of`.

The test fixture should include all seven adapters with a registry-like shape:
`id`, `display_name`, `platform_label`, `suggested_source_name`,
`recommended_input_format`, `recommended_pattern`,
`suggested_export_directory`, `field_mappings`, `recommended_commands`, and
`boundaries`. Each adapter should include the same nine-command sequence the
real registry emits. Use a helper based on `shlex.join(...)` to shell-quote
glob patterns and multi-word `--source-name` values.

Negative tests should include later-adapter id/list drift, metadata drift,
ordering drift, command-prefix drift, duplicate/missing readiness command drift,
and at least one later-adapter readiness-value drift.

## Test Strategy

- Run the current first-run smoke validator test before changes for baseline.
- Apply validator and fixture changes.
- Run the focused validator test.
- Run all external-tool first-run smoke tests.
- Run `tests/test_first_run_smoke.py`, ruff checks for touched files, release
  hygiene, `git diff --check`, and full pytest before commit.

## Acceptance Criteria

- The smoke fixture contains all seven adapter ids.
- `validate_external_tool_adapters` fails when a later adapter id or readiness
  command drifts.
- `validate_external_tool_adapters` fails when adapter order, public metadata,
  recommended command prefix sequence, or duplicate readiness command count
  drifts.
- Every adapter readiness command is parsed and checked for the expected
  adapter-specific fields.
- Runtime CLI and adapter code remain unchanged.
