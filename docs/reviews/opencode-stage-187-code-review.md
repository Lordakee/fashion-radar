# Stage 187 Code Review

## Summary

Stage 187 is a test-only docs-parity hardening node that closes the Stage 181 M1
gap by upgrading the community-docs adapter-catalog guard from per-row substring
checks to an exact `Known adapter ids` table-block equality assertion. The
change is confined to `tests/test_external_tool_contract_parity.py` (a new
helper `_known_adapter_catalog_doc_table` and a new test
`test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table`);
the existing substring/advisory test is retained additively. `git status` shows
no runtime source, CLI, dependency, lockfile, or community-doc content changes,
and neither `docs/community-signal-import.md` nor
`docs/community-signal-quality.md` is modified, confirming the temporary
stale-row RED mutation was reverted. The implementation is sound and is
approved for release-gate verification.

## Verification Performed

- `git diff tests/test_external_tool_contract_parity.py`: +31 lines, helper +
  new test only, no other test changes.
- `git status`: sole tracked modification is the test file; both community docs
  clean (no leftover RED mutation).
- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q`:
  8 passed.
- `uv --no-config run --frozen pytest ... -k "adapter_catalog or community_signal_docs"`:
  2 passed, 6 deselected.
- `ruff check` / `ruff format --check` on the test file: both clean.
- Independent harness replay: registry id order matches
  `EXPECTED_ADAPTER_IDS` and both doc tables; a synthetic stale extra row is
  rejected (`stale-row caught: True`); an adjacent-row swap is rejected
  (`order-drift caught: True`); a missing marker raises `AssertionError`.

## Question Answers

1. Closes the Stage 181 M1 gap. The new test asserts
   `_known_adapter_catalog_doc_table(doc) == expected_table`, where
   `expected_table` is header + separator + registry-derived rows
   (`tests/test_external_tool_contract_parity.py:164-173`). Python list
   equality rejects stale extra rows (length mismatch), missing rows (length
   mismatch), row-order drift (positional mismatch), and header/separator drift
   in one check. Empirically confirmed: stale-row and order-drift mutations
   both flip the equality to False.

2. Helper is appropriate and does not mask drift.
   `_known_adapter_catalog_doc_table`
   (`tests/test_external_tool_contract_parity.py:101-114`) requires exactly one
   `Known adapter ids:` marker via `assert lines.count(...) == 1`, pins the blank
   line at `marker_index + 1`, and extracts only the contiguous `|`-prefixed
   block after `marker_index + 2`. The `count == 1` assertion executes before
   `lines.index(...)`, so the plan-review M1 `ValueError` concern is already
   neutralized: a missing marker (count 0) or duplicate marker (count 2) raises
   a clean `AssertionError`, and `.index()` only runs when count is exactly 1.
   Verified: a marker-less document raises `AssertionError`, not a collection
   error. Marker/table drift is surfaced, not masked.

3. Live registry derivation preserved. `expected_table` data rows come from
   `*[_adapter_catalog_doc_row(adapter) for adapter in registry.adapters]`
   (`tests/test_external_tool_contract_parity.py:167`), where `registry` is the
   existing module-scoped fixture calling
   `build_external_tool_adapter_registry(...)` (lines 83-90). The only hardcoded
   literals are the structural header and separator. Registry id order
   (`rednote_mcp ... generic_community_export`) matches both community doc
   tables exactly.

4. RED proof is meaningful and reverted. Appending one well-formed stale row
   makes the mutated doc's extracted block 11 lines versus the 10-line expected
   block, a deterministic length-mismatch failure
   (`docs/community-signal-import.md` table is 10 lines: 2 header + 8 adapters).
   `git status` lists neither community doc as modified, so no temporary
   mutation remains in the working tree.

5. Boundary compliance verified. The sole code change is a test file. No
   `src/`, `pyproject.toml`, `uv.lock`, CLI, or docs-content changes. No source
   acquisition, scraping, browser automation, platform APIs, login/cookie/token
   behavior, scheduling, ranking, demand proof, platform coverage verification,
   or compliance-review product behavior. Pure test hardening honoring all
   `AGENTS.md` community-tool boundaries.

## Critical

None.

## Important

None.

## Minor

- M1 (non-blocking, confirmation of plan-review M1).
  `_known_adapter_catalog_doc_table` uses `lines.index("Known adapter ids:")`
  after `assert lines.count("Known adapter ids:") == 1`
  (`tests/test_external_tool_contract_parity.py:104-105`). Because the count
  guard runs first and `.index()` only runs when count is exactly 1, a missing
  or duplicate marker cannot reach `.index()` and cannot raise `ValueError`.
  The plan-review M1 concern is therefore already addressed by the
  implementation; no change required.

- M2 (non-blocking, `tests/test_external_tool_contract_parity.py:161-173`).
  The temporary RED proof exercises only the stale-extra-row path; the
  row-order-drift acceptance criterion is covered implicitly by `list.__eq__`
  and confirmed by replay, but not separately demonstrated during verification.
  Optional: also temporarily swap two adjacent rows during a future RED proof.
  Non-blocking because list equality is inherently order-sensitive.

Stage 187 is approved for release-gate verification.
