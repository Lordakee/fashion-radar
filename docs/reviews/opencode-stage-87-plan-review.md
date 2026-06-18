I'll review the Stage 87 plan. Let me read all the relevant files first.
I've reviewed all four files. Let me verify one detail about the helper function existence and the exact current assertion structure before finalizing.
All details confirmed. Here are my findings.

---

# Stage 87 Plan Review Findings

## Summary

**No Critical or Important blockers.** The plan is well-scoped, correct, and safely test-only. Implementation may proceed.

---

## Findings Ordered By Severity

### Minor (informational, non-blocking)

**M1 — Boundary paragraph placement makes the narrowed test meaningful.**
`docs/community-signal-import.md:72-74` contains all 8 required phrases inside the `## External Tool Import Roadmap` section:
```
This roadmap does not run upstream tools, does not search platforms, does not
scrape, does not call platform APIs, does not add connectors, does not prove
demand, does not rank brands, and does not verify platform coverage.
```
After `_normalized_text(...).casefold()`, each term (`"does not call platform apis"`, etc.) matches as a substring. The narrowed assertion will pass without docs changes. Verified by tracing each of the 8 terms against the casefolded/normalized roadmap text.

**M2 — Variable name choice is consistent with existing convention.**
The proposed `normalized_roadmap = _normalized_text(roadmap).casefold()` mirrors the pattern already used in `tests/test_cli_docs.py:577` (`normalized = _normalized_text(section).casefold()` for heat-movers section tests). Idiomatic for this file.

**M3 — Dead-variable check passes.**
Confirmed via grep: within `test_community_signal_import_docs_have_external_tool_import_roadmap` (`tests/test_cli_docs.py:1192-1229`), the variable `normalized` is assigned once at line 1194 and referenced once at line 1228. Removing both is safe — no other consumer exists. After the change, `COMMUNITY_SIGNAL_IMPORT_DOC` is only referenced via `_read(...)` at line 1193.

**M4 — Helper function exists with correct signature.**
`_normalized_text(text: str) -> str` is defined at `tests/test_cli_docs.py:317`. The plan correctly uses it (not `_normalized_doc_text`, which takes a `Path`). No new helper needed.

---

## Answers To Review Questions

**1. Does the plan correctly narrow the boundary assertions to the roadmap section?**
Yes. The plan replaces the full-document `normalized` (`tests/test_cli_docs.py:1194`) with a section-scoped `normalized_roadmap` computed from the already-extracted `roadmap` string, then retargets the final loop's `assert term in normalized` (line 1228) to `normalized_roadmap`. The table/phase assertions (lines 1201-1216) remain scoped to `roadmap` unchanged. Net effect: boundary phrases must now appear inside the roadmap section itself, not elsewhere in the doc.

**2. Does the current roadmap section already contain the required phrases, so docs content can remain unchanged?**
Yes. All 8 boundary terms are present in the closing paragraph of the roadmap section at `docs/community-signal-import.md:72-74`. Verified each term against the casefolded normalized form. No docs edit needed.

**3. Is this safely test-only without runtime behavior implications?**
Yes. Change is confined to `tests/test_cli_docs.py`. No `src/`, schemas, lint/import behavior, adapter/template/workflow/readiness behavior, manifests, `uv.lock`, CI, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md` modifications. The change narrows assertion scope (stricter locality) without altering runtime behavior.

**4. Are the verification commands sufficient?**
Yes. Task 3 runs the focused test plus the full `tests/test_cli_docs.py` module. Task 4 adds the full pytest suite, `ruff check`, `ruff format --check`, `uv lock --check`, mirror-URL scan of `uv.lock`, release hygiene script, secret scan, and `git diff --check`. Covers test correctness, lint, format, lockfile integrity, and release hygiene.

**5. Are there any Critical or Important blockers before implementation?**
**No Critical or Important blockers.** Only the four Minor notes above, all confirming the plan is sound.

---

## Scope Boundary Compliance

The plan respects all `AGENTS.md` boundaries:
- Test-only; no docs content, `src/`, schemas, or lint/import changes
- No scraping, connectors, browser automation, platform APIs, account/cookie/session/token behavior, media downloads, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, schema enums, new linter restrictions, or compliance-review features introduced
- The narrowed assertion does not weaken boundary enforcement — it makes boundary enforcement more precise by requiring the phrases inside the roadmap section rather than anywhere in the doc
