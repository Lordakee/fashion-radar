# Stage 173 Release Review Prompt

Review the Stage 173 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 173 Release Review

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
- Stage 173 spec, plan, plan-review prompt, plan-review artifact, code review
  prompt, and code review artifact.

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

Review history:

- `docs/reviews/opencode-stage-173-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: intentional overlap with existing readiness docs test,
    line-wrap variation across docs, possible constant reuse for doc paths, and
    confirming neighboring docs tests should continue to pass.
- `docs/reviews/opencode-stage-173-code-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: constant near-duplication, path-reference style
    inconsistency, acceptable line-wrap variation, and correct changelog
    placement.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q`
  - Result before docs updates: 1 failed with `README.md missing 'social data api'`.
- GREEN:
  - Same focused command after docs updates.
  - Result: 1 passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_cli_reference_external_tool_option_parity tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q`
  - Result: 2 passed after restoring `--format table|json` to a single Markdown line.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_are_linked_and_bounded tests/test_cli_docs.py::test_external_tool_readiness_upload_checklist_help_loop_and_smoke tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability -q`
  - Result: 3 passed.
- `uv --no-config run --frozen pytest tests/test_external_tool_readiness.py::test_readiness_upstream_command_mapping tests/test_external_tool_adapters.py::test_xpoz_mcp_adapter_has_expected_mapping_and_commands -q`
  - Result: 9 passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -q`
  - Result: 69 passed.
- Release gate:
  - `env -u ALL_PROXY -u HTTPS_PROXY -u HTTP_PROXY -u all_proxy -u https_proxy -u http_proxy uv --no-config run --frozen pytest -q`
  - Result: 1369 passed.
  - `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
    - Result: First-run sample smoke passed.
  - `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
    - Result: Release hygiene checks passed.
  - `uv --no-config run --frozen ruff check .`
    - Result: All checks passed.
  - `uv --no-config run --frozen ruff format --check .`
    - Result: 144 files already formatted.
  - `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
    - Result: Resolved 84 packages in 1ms.
  - `git diff --check`
    - Result: no output, exit 0.
  - `rg -n 'ghp_[A-Za-z0-9]+' .`
    - Result: no matches.
  - `git config --get-all http.https://github.com/.extraheader`
    - Result: no token-bearing header configured.

Release review questions:

1. Is Stage 173 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this docs/test stage?
4. Did any out-of-scope runtime, payload, adapter, smoke-script, install-hint,
   mirror-hint, connector, source-acquisition, ranking, or compliance-review
   behavior change slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
