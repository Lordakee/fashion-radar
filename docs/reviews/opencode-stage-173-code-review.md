# Stage 173 Code Review

## Summary

Stage 173 is a docs/test-only change that makes the existing `xpoz_mcp`
`external-tool-readiness` adapter discoverable across the user-facing docs, and
guards that discoverability with a new parity test
(`test_external_tool_readiness_docs_include_xpoz_discoverability`). The
objective is met cleanly: XPOZ is consistently framed as
"XPOZ MCP / Social Data API exports created outside Fashion Radar" for
sanitized CSV/JSON local file handoff rows from user-controlled
external/community tools, the boundary language in every touched doc is
preserved intact, and no runtime, adapter, smoke-script, payload,
install-hint, or mirror-hint behavior was modified. Verification reproduces the
reported RED/GREEN evidence and the runtime contract is unchanged. No critical
or important findings; release verification may proceed.

## Findings

### Critical

None.

### Important

None.

### Minor

1. **Constant near-duplication (acknowledged in plan review).**
   `EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS`
   (tests/test_cli_docs.py:259) reproduces 8 of the 9 entries of the existing
   `EXTERNAL_TOOL_READINESS_DOCS` (tests/test_cli_docs.py:247), differing only
   by the intentional omission of `AGENTS.md`. The exclusion is defensible
   (AGENTS.md is an agent-instructions file, not a user-facing discoverability
   surface, and is not in the stage's changed-files list), but the two tuples
   could share a base or the new one could be derived via slicing to reduce
   future drift. Low impact; acceptable as-is.

2. **Path-reference style inconsistency.** The new tuple uses named aliases
   (`COMMUNITY_SIGNAL_IMPORT_DOC`, `SOURCE_BOUNDARIES_DOC`, `ARCHITECTURE_DOC`,
   `UPLOAD_CHECKLIST`, `CHANGELOG`) while the immediately preceding
   `EXTERNAL_TOOL_READINESS_DOCS` uses inline `ROOT / "docs" / "..."` literals
   for those same files. Cosmetic only; both resolve to identical paths.

3. **Line-wrap variation across docs (acknowledged in plan review).**
   Wrapping differs by file (e.g., docs/architecture.md breaks "Social Data /
   API exports" across lines, docs/community-signal-quality.md keeps it on one
   line). This is safe because the parity test normalizes via
   `_normalized_doc_text(...).casefold()` which collapses whitespace, and the
   existing wrapping-regression guard (`test_cli_reference_external_tool_option_parity`)
   keeps `--format table|json` on a single Markdown line. The reported
   intermediate failure of that guard and its fix are consistent with the diff.

4. **CHANGELOG placement.** The Stage 173 entry is correctly placed at the top
   of the `### Added` section under the unreleased heading and explicitly states
   the docs/test-only boundary plus the full negative-scope list. No issue.

## Verification Assessment

Reproduction of the reported evidence (all run with
`uv --no-config run --frozen`):

- Scope boundary: `git diff --stat -- src/ scripts/` is empty; only 8 docs +
  `tests/test_cli_docs.py` changed. Confirmed no runtime, adapter, or
  smoke-script edits.
- RED (credible from diff inspection): README.md and the other 7 docs gain
  "xpoz mcp" / "social data api" in this stage; the new test asserts those
  substrings, so the pre-change run would fail with "README.md missing
  'social data api'" as reported.
- GREEN: `pytest tests/test_cli_docs.py::test_external_tool_readiness_docs_include_xpoz_discoverability`
  -> 1 passed.
- Full file: `pytest tests/test_cli_docs.py` -> 69 passed (matches reported
  final count after the `--format table|json` single-line fix).
- Neighboring + runtime contract:
  `test_external_tool_readiness_docs_are_linked_and_bounded`,
  `test_external_tool_readiness_upload_checklist_help_loop_and_smoke`, the new
  XPOZ test, plus
  `test_readiness_upstream_command_mapping` and
  `test_xpoz_mcp_adapter_has_expected_mapping_and_commands` -> 12 passed;
  running the two runtime tests alone -> 9 passed, matching the report.
- Lint/format: `ruff check tests/test_cli_docs.py` -> All checks passed;
  `ruff format --check tests/test_cli_docs.py` -> 1 file already formatted.
- Runtime parity spot-check:
  `fashion-radar external-tool-readiness --adapter xpoz_mcp --format json`
  returns an unchanged payload (`execution_mode: local_read_only`,
  `upstream_command` status `not_applicable`, `install_hint` reading
  "Use XPOZ MCP / Social Data API docs to create a sanitized local JSON
  export"), confirming the docs framing matches the pre-existing runtime
  metadata and that this stage added no runtime behavior.

## Verdict

Approve. The implementation satisfies the Stage 173 objective, the parity test
is useful and narrowly scoped to XPOZ readiness discoverability, the docs
preserve every existing boundary statement and never imply Fashion Radar runs
XPOZ, calls its APIs, manages MCP servers, stores keys, validates access,
verifies coverage, or collects platform data, and no out-of-scope runtime,
payload, adapter, smoke-script, install-hint, or mirror-hint change was
introduced. Only previously-acknowledged minor style notes remain; none block
release verification.
