# Stage 72 Adapter JSON Contract Design

## Goal

Broaden the `external-tool-adapters --format json` contract test so every
registered adapter is covered, not only the first `rednote_mcp` adapter.

## Context

The adapter registry is already built through a shared `_adapter()` helper, so
runtime behavior should already be consistent across all seven adapters. The
current CLI JSON test verifies the top-level adapter order and then checks
field mappings and the `external-tool-readiness` command only for the first
adapter. A later adapter could drift in serialized metadata, command order, or
readiness command flags without the CLI contract test catching it.

## Scope

In scope:

- Extend `tests/test_cli.py::test_external_tool_adapters_command_prints_json`.
- Assert stable serialized metadata for all seven adapters.
- Assert every adapter has the shared field mapping contract.
- Assert every adapter exposes the same recommended command sequence.
- Assert every adapter's `external-tool-readiness` command carries the
  adapter-specific `--adapter`, `--input-format`, `--pattern`, and
  `--source-name` values.

Out of scope:

- Runtime code changes unless the broadened test reveals real drift.
- New adapters or adapter metadata changes.
- Source/platform connectors, scraping, browser automation, platform APIs,
  login/cookie/session/token/proxy/CAPTCHA behavior, media downloads,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product behavior.

## Design

Keep the existing test entry point and top-level assertions. Add an
`expected_adapters` mapping keyed by adapter id:

```python
expected_adapters = {
    "rednote_mcp": ("rednote", "Rednote MCP Export", "json", "*.json"),
    "xiaohongshu_crawler": ("xiaohongshu", "Xiaohongshu Crawler Export", "csv", "*.csv"),
    "instaloader": ("instagram", "Instaloader Export", "json", "*.json"),
    "tiktok_api": ("tiktok", "TikTok-Api Export", "json", "*.json"),
    "yt_dlp": ("media", "yt-dlp Metadata Export", "json", "*.json"),
    "x_search_export": ("x", "X Search Export", "csv", "*.csv"),
    "generic_community_export": ("community", "Generic Community Export", "csv", "*.csv"),
}
```

Loop over each serialized adapter and assert:

- `list(adapter)` stays in the stable JSON key order.
- Metadata values match `expected_adapters`, including `display_name` and
  `suggested_source_name`.
- `suggested_export_directory == "exports"`.
- `upstream_tool_examples` is non-empty.
- `field_mappings` equals the first adapter's `field_mappings`.
- The first field mapping is the existing required `url` mapping.
- `recommended_commands` parses with `shlex.split()`.
- Every recommended command starts with `fashion-radar`, and the command
  sequence is:
  `community-signal-profile`, `external-tool-readiness`,
  `community-handoff-manifest`, `community-handoff-workflow`,
  `community-signal-lint-dir`, `community-handoff-check-dir`,
  `import-signals-dir`, `import-signals-dir`, `imported-review-workflow`.
- The readiness command includes the expected adapter-specific and shared flags.
- `--config-dir` and `--data-dir` remain non-empty and consistent across every
  adapter readiness command.

Define the flag helper as `flag_value(parts, flag)` outside the per-adapter
loop so ruff's bugbear B023 rule does not flag a closure over the loop-local
`readiness_parts` variable.

## Test Strategy

- Run the existing CLI JSON test before changes for a baseline.
- Apply the test-only hardening.
- Run the targeted CLI JSON test.
- Run nearby external-tool CLI tests.
- Run `tests/test_cli.py`, ruff checks, release hygiene, `git diff --check`,
  and full pytest before commit.

## Acceptance Criteria

- The CLI JSON contract test covers all seven adapters.
- The expected adapter id order remains pinned.
- Every adapter's metadata, shared field mapping contract, recommended command
  order, and readiness command flags are asserted.
- Runtime code is unchanged unless the test exposes actual drift.
