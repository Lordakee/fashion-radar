# Stage 173 Code Review Prompt

Review the Stage 173 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to the focused
commands listed below and return one final review body.
Start the response exactly with:

# Stage 173 Code Review

Objective:

Make XPOZ MCP / Social Data API exports discoverable in the
`external-tool-readiness` docs and guard that discoverability with a docs parity
test.

Changed files:

- `tests/test_cli_docs.py`
  - Adds `EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS`.
  - Adds `test_external_tool_readiness_docs_include_xpoz_discoverability`.
- `README.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
- `docs/cli-reference.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
  - Adds `fashion-radar external-tool-readiness --adapter xpoz_mcp --format json`.
- `docs/community-signal-import.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
- `docs/community-signal-quality.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
- `docs/source-boundaries.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
- `docs/architecture.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
- `docs/github-upload-checklist.md`
  - Adds XPOZ MCP / Social Data API exports to readiness discoverability prose.
  - Adds the public and installed-wheel `xpoz_mcp` readiness JSON commands.
- `CHANGELOG.md`
  - Adds a Stage 173 docs/test-only changelog entry.
- Stage 173 spec, plan, plan-review prompt, and plan-review artifact.

Scope boundaries:

- Docs/test-only.
- Keep XPOZ framed as `XPOZ MCP / Social Data API exports created outside
  Fashion Radar` for sanitized CSV/JSON local file handoff rows from
  user-controlled external/community tools.
- No changes to `src/fashion_radar/external_tool_adapters.py`.
- No changes to `src/fashion_radar/external_tool_readiness.py`.
- No changes to `scripts/check_first_run_smoke.py`.
- No changes to runtime adapter metadata, readiness builder behavior, payload
  shapes, validators, command order, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance-review product feature.

Plan review history:

- `docs/reviews/opencode-stage-173-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: intentional overlap with existing readiness docs test,
    line-wrap variation across docs, possible constant reuse for doc paths, and
    confirming neighboring docs tests should continue to pass.

RED/GREEN evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q`
  - Result before docs updates: 1 failed with `README.md missing 'social data api'`.
- GREEN:
  - Same focused command after docs updates.
  - Result: 1 passed.
- Neighboring readiness docs tests:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_are_linked_and_bounded tests/test_cli_docs.py::test_external_tool_readiness_upload_checklist_help_loop_and_smoke tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q`
  - Result: 3 passed.
- Related XPOZ runtime contract tests:
  - `uv --no-config run --frozen pytest tests/test_external_tool_readiness.py::test_readiness_upstream_command_mapping tests/test_external_tool_adapters.py::test_xpoz_mcp_adapter_has_expected_mapping_and_commands -q`
  - Result: 9 passed.
- Full CLI docs test file:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py -q`
  - Initial result found one docs wrapping regression:
    `test_cli_reference_external_tool_option_parity` failed because
    `--format table|json` had been split across Markdown lines.
  - Final result after restoring that phrase on one Markdown line: 69 passed.
- `uv --no-config run --frozen ruff check tests/test_cli_docs.py`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
  - Result: 1 file already formatted.

Review questions:

1. Does the implementation meet the Stage 173 objective?
2. Is the docs parity test useful and narrowly scoped to XPOZ readiness
   discoverability?
3. Do the docs avoid implying Fashion Radar runs XPOZ, calls XPOZ APIs, manages
   MCP servers, stores API keys, validates access, verifies platform coverage,
   or collects platform data?
4. Did any out-of-scope runtime, payload, adapter, smoke-script, install-hint,
   mirror-hint, connector, source-acquisition, ranking, or compliance-review
   behavior change slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
