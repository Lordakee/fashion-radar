I'll review the Stage 87 implementation. Let me first read the relevant files.
Now let me check the actual docs file and the git diff to verify the change.
The `git diff HEAD~1` included the previous commit. Let me get just the unstaged Stage 87 working tree change and verify the docs content.
Let me verify the test passes and check whether the 8 boundary phrases appear elsewhere in the doc (relevant to the "weakens coverage" question).
Test passes. Now let me confirm the full module passes cleanly and ruff has no issues, and check what section line 142/224 belong to (to assess the "weakens coverage" question).
All verification green: focused test passes (1 passed), full module passes (58 passed), ruff clean. Here is the review.

---

# Stage 87 Code Review Findings

## Summary

**No Critical or Important blockers.** The implementation matches the Stage 87 plan and scope exactly, is correctly scoped to the roadmap section, and does not weaken docs drift coverage — it tightens it.

---

## Findings Ordered By Severity

### Minor (informational, non-blocking)

**M1 — Implementation matches plan precisely; scope respected.**
`tests/test_cli_docs.py:1192-1228` — the unstaged diff is exactly the 3 planned edits: drop the whole-doc `normalized = _normalized_doc_text(COMMUNITY_SIGNAL_IMPORT_DOC).casefold()`, add `normalized_roadmap = _normalized_text(roadmap).casefold()` after the section extraction, and retarget the final loop's `assert term in normalized` → `assert term in normalized_roadmap`. No other code touched; only the test file plus the Stage 87 review/spec/plan artifacts are present in the working tree. `COMMUNITY_SIGNAL_IMPORT_DOC` is still consumed by `_read(...)` at `:1193`, so no dead constant. The removed `normalized` had a single reader; ruff (F841) is clean.

**M2 — Boundary phrases are correctly required inside the roadmap section.**
All 8 terms live in the closing roadmap paragraph at `docs/community-signal-import.md:72-74`. Two terms span line breaks in the raw source (`"does not scrape"` across 72-73, `"does not prove demand"` across 73-74); these resolve correctly because `_normalized_text` collapses runs of whitespace to single spaces before the substring check. Verified: focused test `1 passed`, full module `58 passed`.

**M3 — No docs-drift weakening; the change is net-strictly-stronger for the roadmap.**
I traced every phrase's locations across the doc:
- 6 of 8 phrases exist *only* in the roadmap section — old and new behavior identical on deletion.
- 2 phrases also occur outside the roadmap: `"does not run upstream tools"` at `:142` (readiness section) and `"does not prove demand"`/`"does not verify platform coverage"` at `:224` (contract-parity section). Pre-change, deleting the roadmap paragraph for these two would still *pass* via the elsewhere occurrence (false negative); post-change it correctly *fails*. So for the roadmap's own boundary this is strictly stricter.
- Those two non-roadmap occurrences remain protected by their own dedicated tests: the readiness boundary test (`EXTERNAL_TOOL_READINESS_BOUNDARY_PHRASES`) and `test_community_signal_import_docs_describe_external_tool_contract_parity`, which still asserts `"does not prove demand"` and `"does not verify platform coverage"` against the full doc. No coverage gap is introduced.

---

## Answers To Review Questions

1. **Does the implementation match the Stage 87 plan and scope?** Yes — diff is exactly the 3 planned edits in `tests/test_cli_docs.py`, test-only, no disallowed files touched (M1).
2. **Does it correctly require the boundary phrases inside the roadmap section?** Yes — all 8 phrases are asserted against `normalized_roadmap`, and all 8 are present at `docs/community-signal-import.md:72-74` (M2).
3. **Is there any risk that this weakens docs drift coverage?** No. The two non-roadmap phrase occurrences stay covered by their own section tests, and the roadmap boundary is now enforced more precisely (M3).
4. **Critical/Important issues before final verification, commit, push?** None. Proceed to Task 4 (full verification, commit, push).
