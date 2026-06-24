# Stage 187 Release Review

## Summary

Stage 187 is a test-only docs-parity hardening node that closes the Stage 181 M1
gap by upgrading the community-docs adapter-catalog guard from per-row substring
checks to an exact `Known adapter ids` table-block equality assertion. The
change is confined to `tests/test_external_tool_contract_parity.py` (+31 lines:
one helper and one test); the existing substring/advisory test is retained
additively. `git status` shows the sole tracked modification is the test file,
plus new spec/plan/review artifacts. Neither `docs/community-signal-import.md`
nor `docs/community-signal-quality.md` is modified, confirming the temporary
stale-row RED mutation was fully reverted. The full release gate (1389 tests,
first-run smoke, release hygiene, ruff check/format, frozen `uv lock --check`,
`git diff --check`, token and extraheader absence checks) is clean. The state
is approved for the full release gate and commit.

## Verification Performed

- Independent table replay: both community docs contain identical 10-line
  `Known adapter ids` tables (2 header + 8 adapter rows) in registry order
  (`rednote_mcp` ... `generic_community_export`), matching
  `build_external_tool_adapter_registry(...)` exactly.
- `rg -n "removed_adapter" .`: matches only in plan/spec/review artifacts as
  RED-proof documentation; no matches in either community doc, confirming the
  temporary mutation is gone from the working tree.
- `git status --short` / `git diff --stat HEAD`: only
  `tests/test_external_tool_contract_parity.py` modified (+31); all other
  additions are untracked spec/plan/review artifacts. No `src/`, `pyproject.toml`,
  `uv.lock`, CLI, or community-doc content changes.
- Full release gate per the prompt: all listed commands passed.

## Question Answers

1. Objective satisfied. The new
   `test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table`
   (`tests/test_external_tool_contract_parity.py:161-173`) asserts
   `_known_adapter_catalog_doc_table(doc_text) == expected_table`, where
   `expected_table` is header + separator + registry-derived rows. Python list
   equality rejects stale extra rows (length mismatch), missing rows (length
   mismatch), row-order drift (positional mismatch), and header/separator drift
   in one check, closing the substring-only weakness flagged in Stage 181 M1.
   Both docs verified byte-identical to the registry-derived table.

2. Code and review artifacts are clean and internally consistent. The RED
   mutation is fully removed: `removed_adapter` appears only inside the plan,
   spec, and review artifacts as RED-proof narrative, never in the guarded
   community docs. The test diff is exactly the helper plus the new test with no
   unrelated edits; the plan and code reviews are complete with no stubs,
   truncation, or duplicated drafts.

3. Scope is correctly limited. The sole source modification is
   `tests/test_external_tool_contract_parity.py`. All other additions are
   Stage 187 spec/plan/review artifacts. No runtime source, CLI, docs-content,
   dependency, lockfile, source-pack, entity-pack, package archive, first-run
   smoke, or release hygiene behavior changes.

4. Boundary compliance verified. No source acquisition, scraping, browser
   automation, platform APIs, login/cookie/token behavior, dependency or package
   changes, scheduling, ranking, demand proof, platform coverage verification,
   or compliance-review product behavior. The work is pure test hardening and
   honors all `AGENTS.md` community-tool boundaries.

## Critical

None.

## Important

None.

## Minor

- M1 (non-blocking, confirmation of plan-review M1, addressed by
  implementation). `_known_adapter_catalog_doc_table` uses
  `lines.index("Known adapter ids:")` after
  `assert lines.count("Known adapter ids:") == 1`
  (`tests/test_external_tool_contract_parity.py:104-105`). Because the count
  guard runs first, `.index()` only executes when count is exactly 1, so a
  missing or duplicate marker raises a clean `AssertionError` rather than
  `ValueError`. No change required.

- M2 (non-blocking, `tests/test_external_tool_contract_parity.py:161-173`). The
  temporary RED proof exercised only the stale-extra-row path; the
  row-order-drift acceptance criterion is covered implicitly by `list.__eq__`
  and confirmed by replay, but not separately demonstrated during verification.
  Optional: also swap two adjacent rows during a future RED proof. Non-blocking
  because list equality is inherently order-sensitive.

Stage 187 is approved for the full release gate and commit.
