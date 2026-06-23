# Stage 181 Code Review

## Summary

Stage 181 is a docs/test-only parity hardening that adds a runtime-derived
docs drift guard and inserts the current `Known adapter ids` table into both
community docs. The implementation matches the approved plan, derives every
table row from the live `ExternalToolAdapter` registry, and preserves the
advisory-only platform-label semantics. The new test was independently
verified as a genuine RED/GREEN guard. Approved for release verification.

## Question Answers

1. Matches plan. `test_community_signal_docs_list_current_external_tool_adapter_catalog`
   (`tests/test_external_tool_contract_parity.py:120`), the `ROOT` /
   `COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS` constants
   (`tests/test_external_tool_contract_parity.py:29-33`), and the
   `_adapter_catalog_doc_row` helper
   (`tests/test_external_tool_contract_parity.py:93-98`) are added as
   specified. The `Known adapter ids` table lands under
   `## External Tool Adapter Registry` in
   `docs/community-signal-import.md:204` (heading at line 184, after the
   "...used elsewhere in this guide." paragraph at line 202), and near the
   `external-tool-adapters` guidance in `docs/community-signal-quality.md:27`
   (right after "...does not run readiness or perform PATH lookup." at line
   25). Both blocks are byte-identical to the plan's Task 2 reference block.
   The only deviation from the plan text is positive: the helper carries an
   explicit `ExternalToolAdapter` type annotation (import added at
   `tests/test_external_tool_contract_parity.py:14`).

2. Runtime-derived and drift-guarding. `expected_rows` is built from
   `[_adapter_catalog_doc_row(adapter) for adapter in registry.adapters]`
   (`tests/test_external_tool_contract_parity.py:121`), where `registry` is the
   module-scoped fixture that calls `build_external_tool_adapter_registry(...)`
   (`tests/test_external_tool_contract_parity.py:83-90`). Each row formats
   `adapter.id`, `adapter.display_name`, `adapter.platform_label`,
   `adapter.recommended_input_format`, and `adapter.recommended_pattern`
   straight off the live `ExternalToolAdapter` model
   (`src/fashion_radar/external_tool_adapters.py:62-73`); no hardcoded row
   constant is used. The test loops both docs and asserts every row with a
   file-relative failure message
   (`tests/test_external_tool_contract_parity.py:123-128`). Independent
   experiment: removing the `instaloader` row from the import doc makes the
   test fail; restoring it makes the test pass. Any future registry addition
   will force a doc update in both files.

3. Doc values match runtime exactly. All eight rows in
   `docs/community-signal-import.md:208-215` and
   `docs/community-signal-quality.md:31-38` match the `display_name`,
   `platform_label`, `recommended_input_format`, and `recommended_pattern`
   arguments passed to `_adapter(...)` in
   `src/fashion_tool_adapters.py:108-251` (rednote_mcp, xiaohongshu_crawler,
   instaloader, tiktok_api, yt_dlp, x_search_export, xpoz_mcp,
   generic_community_export). Backtick wrapping is consistent with the
   formatter: `id`/`platform_label`/`format`/`pattern` are backticked and
   `display_name` is plain, exactly as rendered in the docs. The test
   normalizes whitespace (`" ".join(text.split())`,
   `tests/test_external_tool_contract_parity.py:124`) so reflowed line breaks
   cannot mask a real mismatch.

4. Advisory-only wording preserved. Both explanatory paragraphs
   (`docs/community-signal-import.md:217-223`,
   `docs/community-signal-quality.md:40-46`) state the labels are "advisory
   local provenance label guidance" and "local provenance suggestions only:
   they are not a schema enum, not a linter restriction, not platform
   coverage, and not demand proof." The wording is byte-identical to the
   README/cli-reference blocks already covered by
   `test_external_tool_adapter_platform_label_docs_are_advisory`. The table
   lists `platform_label` purely as a local provenance suggestion and implies
   no platform coverage, demand proof, connectors, scraping, browser
   automation, platform APIs, monitoring, scheduling, source acquisition,
   ranking, or compliance-review behavior. The import doc's boundary
   paragraph at `docs/community-signal-import.md:229-234` re-asserts the full
   exclusion list. Scope boundaries in the spec ("Out of scope",
   design:39-48) and plan ("Self-Review Notes", plan:291-295) are honored:
   no runtime/CLI/connector/lockfile change.

5. No missing tests or overbroad assertions. The full
   `tests/test_external_tool_contract_parity.py` (7 passed) and the full
   `tests/test_cli_docs.py` (69 passed) are green, and ruff check/format are
   clean on the touched file. The docs change is purely additive and reuses
   already-approved wording, so it cannot break other docs tests.

## Critical

None.

## Important

None.

## Minor

- M1 (test scope, `tests/test_external_tool_contract_parity.py:126-139`).
  The guard asserts `"Known adapter ids:"`, every data row, and the
  advisory paragraph phrases, but it does not directly assert the table
  header row `| Adapter id | Display/source name | Platform label | Format |
  Pattern |`. A header-only rename (e.g. "Platform label" -> "Platform")
  with data rows left intact would not trip the test, because the header
  wording is only partially anchored via the explanatory paragraph's
  "Display/source name column" phrase. Non-blocking: any actual value drift
  in id/name/label/format/pattern is caught by the per-row assertions, which
  is the real contract. Optional hardening: add the header row
  (`| Adapter id | Display/source name | Platform label | Format | Pattern |`)
  to `expected_rows` or as an explicit `assert` in the phrase loop.

The implementation is approved for release verification.
