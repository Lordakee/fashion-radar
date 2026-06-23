# Stage 173 Plan Review Prompt

Review the Stage 173 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 173 Plan Review

Objective:

Make XPOZ MCP / Social Data API exports discoverable in the
`external-tool-readiness` docs and guard that discoverability with a docs parity
test.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-173-xpoz-readiness-docs-discoverability-design.md`
- `docs/superpowers/plans/2026-06-23-stage-173-xpoz-readiness-docs-discoverability-plan.md`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- `src/fashion_radar/external_tool_adapters.py`
- `src/fashion_radar/external_tool_readiness.py`
- `tests/test_external_tool_adapters.py`
- `tests/test_external_tool_readiness.py`

Scope boundaries:

- Docs/test-only.
- Surface XPOZ in existing `external-tool-readiness` user-facing known-tool
  prose and copyable CLI/checklist examples.
- Keep XPOZ framed as `XPOZ MCP / Social Data API exports` for sanitized
  CSV/JSON local file handoff rows from user-controlled external/community
  tools.
- No changes to runtime source, adapter metadata, readiness builder behavior,
  first-run smoke script behavior, payload shapes, validators, command order,
  install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance-review product feature.

Planned implementation:

1. Add a RED docs test in `tests/test_cli_docs.py`:
   `test_external_tool_readiness_docs_include_xpoz_discoverability`.
2. Run that test before docs updates and confirm it fails because readiness
   docs currently omit XPOZ wording and the copyable `xpoz_mcp` readiness
   command.
3. Add XPOZ wording to existing readiness known-tool prose in user-facing docs.
4. Add `fashion-radar external-tool-readiness --adapter xpoz_mcp --format json`
   to `docs/cli-reference.md` and `docs/github-upload-checklist.md`.
5. Add the installed-wheel smoke command
   `"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter xpoz_mcp --format json`
   to `docs/github-upload-checklist.md`.
6. Add a Stage 173 docs/test-only changelog entry.
7. Run focused docs/runtime checks, code review, full release gate, release
   review, commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is the docs parity test useful without being too broad or brittle?
4. Does the proposed wording avoid implying that Fashion Radar runs XPOZ,
   calls external APIs, manages MCP servers, stores keys, or verifies platform
   coverage?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
