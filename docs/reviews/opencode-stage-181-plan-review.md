# Stage 181 Plan Review

## Summary

The Stage 181 plan is a tight docs/test-only parity hardening that mirrors the
already-approved `Known adapter ids` table from `README.md:146-165` and
`docs/cli-reference.md:115-134` into the two community docs, guarded by a new
runtime-derived parity test. The plan is approved for implementation. Findings
below.

## Question Answers

1. Objective satisfied. The plan adds a docs parity test
   (`tests/test_external_tool_contract_parity.py`, Task 1) and inserts the
   current adapter catalog table into both `docs/community-signal-import.md`
   and `docs/community-signal-quality.md` (Task 2). Scope is explicitly
   docs/test-only: design "Out of scope" (design:39-48) and plan "Self-Review
   Notes" (plan:287-297) both exclude runtime/CLI/connector/scraping/API/
   monitoring/scheduling/demand-proof/ranking/coverage/compliance behavior.

2. Runtime-derived rows. The helper `_adapter_catalog_doc_row(adapter)`
   (plan:67-73) formats each row from `adapter.id`, `adapter.display_name`,
   `adapter.platform_label`, `adapter.recommended_input_format`, and
   `adapter.recommended_pattern` on the live `ExternalToolAdapter` model
   (fields confirmed at `src/fashion_radar/external_tool_adapters.py:62-73`).
   The test builds `expected_rows` by iterating the existing module-scoped
   `registry` fixture (plan:81), not a duplicated constant. This is strictly
   stronger than the hardcoded `EXTERNAL_TOOL_ADAPTER_DOC_ROWS` tuple at
   `tests/test_cli_docs.py:288-297` and gives the intended drift guard: any
   future registry addition will force a doc update.

3. RED is guaranteed before docs edits. Neither community doc currently
   contains `Known adapter ids:`, `Display/source name column`, or the eight
   registry rows (grep confirms those strings today exist only in README,
   cli-reference, and the new spec/plan/review files). The new test also
   asserts `Display/source name column`, which is absent from both target
   docs, so the assertion at plan:91-99 fails regardless of the advisory
   phrases. Both docs already carry `suggested_platform_labels` / `advisory
   local provenance` / `not a schema enum` / `not a linter restriction` /
   `not platform coverage` / `not demand proof`
   (`docs/community-signal-import.md:296-298`,
   `docs/community-signal-quality.md:20-22`), so the RED is driven cleanly by
   the missing header, missing `Display/source name column` phrase, and
   missing rows. Task 1 Step 5 expectation (plan:111-113) is accurate.

4. Advisory-only meaning preserved. The block proposed in Task 2 Step 1
   (plan:127-148) is byte-identical to the already-approved wording in
   `README.md:146-165` that passes the existing
   `test_external_tool_adapter_platform_label_docs_are_advisory` guard at
   `tests/test_cli_docs.py:1953-1976`. It states "advisory local provenance
   label guidance", "not a schema enum, not a linter restriction, not platform
   coverage, and not demand proof", and implies no platform coverage, demand
   proof, connectors, scraping, browser automation, platform APIs, monitoring,
   scheduling, source acquisition, ranking, or compliance-review behavior. The
   table only lists `platform_label` as a local provenance suggestion.

5. Verification sufficient for this node. Task 3 Step 1 (plan:177-190) runs
   the full touched test file, the two `test_cli_docs.py` boundary tests that
   read the edited community docs, and ruff check/format on the touched test
   file. Because the docs change is purely additive (it reuses already-passing
   README/cli-reference wording), it cannot remove terms required by any other
   docs test; the full release gate in Task 4 (plan:227-246) is the complete
   safety net. Anchor references for both insertions are valid:
   `docs/community-signal-import.md:202` ends with "used elsewhere in this
   guide." under `## External Tool Adapter Registry` (heading at line 184);
   `docs/community-signal-quality.md:25` ends with "does not run readiness or
   perform PATH lookup." immediately before the `external-tool-template`
   paragraph at line 26.

## Critical

None.

## Important

None.

## Minor

- M1 (plan:177-188, focused verification scope). The focused step runs only
  two specific `test_cli_docs.py` tests. Since both community docs are read
  by several other docs tests (e.g. `test_external_tool_template_docs_are_`
  `linked_and_bounded` at `tests/test_cli_docs.py:1979`), running the whole
  `tests/test_cli_docs.py` module in Task 3 Step 1 would give a stronger
  pre-gate signal. This is non-blocking because the edits are additive and the
  full release gate covers it, but it is a cheap robustness gain.
- M2 (design:76-83 and plan:132-139, illustrative hardcoded rows). The spec
  and plan each hardcode the eight table rows as pre-implementation reference.
  These match current registry values, and the runtime-derived test is the
  real guard, so any drift between plan authoring and implementation would be
  caught by the RED/GREEN cycle. No action required; noting that the
  illustrative rows are not themselves a contract.

The plan is approved for implementation.
