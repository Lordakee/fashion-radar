# Stage 187 Plan Review

## Summary

Stage 187 is a test-only docs parity hardening node. It closes the Stage 181 M1
gap (`docs/reviews/opencode-stage-181-release-review.md:62-68`) by upgrading the
community docs adapter-catalog guard from per-row substring checks to an exact
`Known adapter ids` table-block equality assertion. The change is confined to
`tests/test_external_tool_contract_parity.py` plus staged review artifacts; no
runtime source, CLI, dependency, lockfile, docs-content, or boundary-relevant
behavior changes are introduced. The plan is sound and is approved for
implementation.

## Question Answers

1. Objective satisfied. The proposed
   `test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table`
   asserts `_known_adapter_catalog_doc_table(doc_text) == expected_table`, where
   `expected_table` is header + separator + registry-derived rows. A Python list
   equality check rejects stale extra rows (length mismatch), missing rows
   (length mismatch), row-order drift (positional mismatch), and header/separator
   drift in one assertion. This directly closes the substring-only weakness
   flagged in the Stage 181 M1.

2. Live registry derivation preserved. `expected_table` builds its data rows via
   `*[_adapter_catalog_doc_row(adapter) for adapter in registry.adapters]`, where
   `registry` is the existing module-scoped fixture calling
   `build_external_tool_adapter_registry(...)` (`tests/test_external_tool_contract_parity.py:83-90`).
   The only hardcoded literals are the structural header and separator strings,
   not adapter data, so no stale adapter constants are duplicated. The
   `ExternalToolAdapter` fields read by `_adapter_catalog_doc_row`
   (`id`, `display_name`, `platform_label`, `recommended_input_format`,
   `recommended_pattern`) all exist on the model
   (`src/fashion_radar/external_tool_adapters.py:62-67`), and Stage 181 already
   proved this helper renders byte-identical rows.

3. RED proof is meaningful and reversion is clearly specified. Temporarily
   appending `| `removed_adapter` | Removed Adapter | `community` | `json` | `*.json` |`
   makes the mutated doc's extracted table 11 lines vs the 10-line expected
   table, so the equality assertion deterministically fails. Task 2 Step 3
   removes the row, the Files section labels it "reverted before commit," and
   Task 4 Step 3 `git add` does not stage either community doc, so the mutation
   cannot reach the commit. (See Minor M2 for a coverage nuance.)

4. Scope is correctly limited. The sole source modification is
   `tests/test_external_tool_contract_parity.py`. Docs content changes are
   explicitly out of scope unless the exact-table test exposes real drift; the
   Task 2 mutation is temporary. All other additions are spec/plan/review
   artifacts. The existing substring/advisory test
   (`test_community_signal_docs_list_current_external_tool_adapter_catalog`,
   lines 120-142) is retained additively, preserving advisory-phrase coverage.

5. Boundary compliance verified. No source acquisition, scraping, browser
   automation, platform APIs, dependency/package changes, scheduling, ranking,
   demand proof, platform coverage verification, or compliance-review product
   behavior. The work is pure test hardening and honors all `AGENTS.md`
   community-tool boundaries.

## Critical

None.

## Important

None.

## Minor

- M1 (non-blocking, design spec
  `docs/superpowers/specs/2026-06-24-stage-187-community-adapter-catalog-exact-table-design.md:52-65`;
  plan Task 2). The proposed `_known_adapter_catalog_doc_table` uses
  `lines.index("Known adapter ids:")`, which raises an unhandled `ValueError`
   if the marker wording changes, producing a confusing collection error rather
   than a clean assertion failure. Optional hardening: guard with
   `assert "Known adapter ids:" in lines, "marker missing"` before calling
   `.index(...)`, or wrap in try/except to convert to an assertion. Not required;
   the existing substring test already guarantees marker presence today.

- M2 (non-blocking, plan Task 2 Step 1). The single RED mutation proves the guard
  catches a stale extra row but does not separately exercise the row-order-drift
  acceptance criterion (spec acceptance criteria lines 102-103). List equality is
  inherently order-sensitive, so order drift is caught, but the RED proof does
  not demonstrate that path. Optional: also temporarily swap two adjacent doc
  rows to confirm an order-only failure. Non-blocking because the extra-row RED
  proof is sufficient for the primary objective and the order check is implicit
  in `list.__eq__`.

- M3 (non-blocking, plan Task 2). The RED proof mutates only
  `docs/community-signal-quality.md` (the second doc in
  `COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS`). This is adequate since the test loops
  both docs and the per-doc assertion message correctly attributes the failure,
   and it incidentally proves the test does not short-circuit after the first doc
   passes. No change needed; flagged only for completeness.

Stage 187 is approved for implementation.
