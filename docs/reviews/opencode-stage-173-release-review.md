# Stage 173 Release Review

Objective:

Make XPOZ MCP / Social Data API exports discoverable in the
`external-tool-readiness` docs and guard that discoverability with a docs parity
test.

## Summary

Stage 173 is a docs/test-only change that surfaces the pre-existing `xpoz_mcp`
`external-tool-readiness` adapter across eight user-facing docs and guards that
discoverability with one new pytest,
`test_external_tool_readiness_docs_include_xpoz_discoverability`. The objective
is fully met. XPOZ is consistently framed as
"XPOZ MCP / Social Data API exports created outside Fashion Radar" for
sanitized CSV/JSON local file handoff rows from user-controlled
external/community tools in every touched doc, the CLI reference and upload
checklist add the copyable
`fashion-radar external-tool-readiness --adapter xpoz_mcp --format json` command
(and the installed-wheel smoke variant in the checklist), and the CHANGELOG
entry is correctly scoped as docs/test-only with an explicit denial list.

Scope is exactly as claimed: `git diff --stat` over `src/`, `scripts/`,
`uv.lock`, and `pyproject.toml` is empty. The runtime files named in the scope
boundaries (`external_tool_adapters.py`, `external_tool_readiness.py`,
`check_first_run_smoke.py`) are untouched. The diff is exactly `CHANGELOG.md`,
`README.md`, `docs/architecture.md`, `docs/cli-reference.md`,
`docs/community-signal-import.md`, `docs/community-signal-quality.md`,
`docs/github-upload-checklist.md`, `docs/source-boundaries.md`, and
`tests/test_cli_docs.py` (+80/-28). The new test defines a narrow
`EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS` tuple (the eight changed
docs), asserts four phrases (`xpoz mcp`, `social data api`,
`external-tool-readiness`, `sanitized csv/json local file handoff`), and asserts
three exact command strings. Every touched doc retains its full boundary denial
list verbatim; the XPOZ additions are purely additive enumeration entries and
copyable command strings.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Plan-review Minor 1/2/3/4 and code-review Minor 1/2/3/4 remain acknowledged
   style notes only with no correctness, scope, or release-safety impact:
   intentional tuple overlap between
   `EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS` and the broader
   `EXTERNAL_TOOL_READINESS_DOCS` (AGENTS.md correctly excluded from both),
   path-reference style inconsistency (named aliases vs inline
   `ROOT / "..."` literals), acceptable per-doc line-wrap variation (the parity
   test normalizes whitespace and `test_cli_reference_external_tool_option_parity`
   keeps `--format table|json` on a single Markdown line), and correct CHANGELOG
   placement at the top of the Added block.
2. The new discoverability test is genuinely RED-to-GREEN. Diff inspection
   confirms six of the eight target docs previously lacked both `xpoz mcp` and
   `social data api`, and none of the three asserted command strings existed
   before this stage, so the reported pre-change failure
   (`README.md missing 'social data api'`) is credible and the reported GREEN
   reproduction is confirmed.

## Verification Assessment

Independent read-only reproduction with `uv --no-config run --frozen` and proxy
env stripped where relevant:

- Scope: `git diff --stat -- src/ scripts/` empty; `git status --porcelain uv.lock pyproject.toml` empty. Runtime adapter metadata (`xpoz_mcp` in
  `external_tool_adapters.py` and `external_tool_readiness.py`) already exists
  upstream of this stage, so the docs now match the runtime contract exactly
  with no payload, validator, command-order, install-hint, or mirror-hint drift.
- Focused tests:
  `test_external_tool_readiness_docs_include_xpoz_discoverability`,
  `test_cli_reference_external_tool_option_parity`,
  `test_external_tool_readiness_docs_are_linked_and_bounded`,
  `test_external_tool_readiness_upload_checklist_help_loop_and_smoke` -> 4 passed.
  `test_readiness_upstream_command_mapping` and
  `test_xpoz_mcp_adapter_has_expected_mapping_and_commands` -> 9 passed. This
  confirms the new discoverability test, the surviving boundary/parity
  neighbors, and the unchanged runtime adapter mapping all hold simultaneously.
- Release gate: full suite -> 1369 passed in 34.48s; first-run sample smoke
  passed; release hygiene checks passed; `ruff check .` -> All checks passed;
  `ruff format --check .` -> 144 files already formatted;
  `UV_NO_CONFIG=1 uv lock --check` -> Resolved 84 packages in 1ms;
  `git diff --check` -> no output, exit 0; `rg 'ghp_[A-Za-z0-9]+'` -> no matches;
  `git config --get-all http.https://github.com/.extraheader` -> no token-bearing
  header.
- Boundary preservation: every touched doc retains its full denial list (no
  install dependencies, no run adapters/upstream tools, no directory inspection,
  no handoff reads, no row import, no SQLite, no
  config/data/report/dashboard/workflow/handoff artifacts, no connectors, no
  scraping, no browser automation, no platform APIs, no account/cookie/token
  behavior, no monitoring/scheduling, no source acquisition, no demand proof, no
  ranking, no coverage verification, no compliance-review product feature). The
  CHANGELOG entry's explicit denial ("no XPOZ API calls, MCP execution, API
  keys, connectors, scraping, browser automation, platform APIs,
  login/cookie/token behavior, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product feature") matches the
  AGENTS.md `external-tool-readiness` boundary.
- Artifact hygiene: `docs/reviews/opencode-stage-173-plan-review.md` (134 lines,
  complete, ends with Approve, no critical/important findings) and
  `docs/reviews/opencode-stage-173-code-review.md` (101 lines, complete, ends
  with Approve, no critical/important findings) contain finished review output
  with no stubs, truncation, duplicated text, or tool-status messages. The
  spec, plan, plan-review prompt/artifact, code-review prompt/artifact, and
  release-review prompt are all present.

No contrary signal was found.

## Verdict

Approve. Stage 173 is in scope, docs/test-only, and ready to commit and push.

1. **In scope and ready to commit?** Yes. Docs/test-only, eight docs plus one
   test, +80/-28, runtime/adapter/readiness/smoke-script/lockfile unchanged.
2. **Plan/code review artifacts clean and consistent with REVIEW_PROTOCOL.md?**
   Yes. Both are complete, well-formed, end with Approve, and contain no
   critical/important findings, stubs, or tool-status chatter.
3. **Release verification evidence sufficient?** Yes. It covers RED/GREEN on the
   new test, surviving neighboring docs tests, unchanged runtime
   adapter/readiness tests, full suite (1369 passed), lint, format, lockfile
   stability, smoke, release hygiene, and secret hygiene.
4. **Out-of-scope runtime/payload/adapter/smoke-script/install-hint/mirror-hint/connector/source-acquisition/ranking/compliance-review drift?**
   None detected. `src/`, `scripts/`, `uv.lock`, and `pyproject.toml` are clean;
   all boundary denial lists are preserved verbatim.
5. **Critical or important findings before commit and push?** None.
