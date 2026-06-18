I'll review the Stage 107 plan. Let me first read all the relevant files.
Let me check the review protocol to ensure I follow the right format, and verify there are no overlapping test files.
Let me do a final automated verification that all 6 planned phrases actually match within the extracted section.
# Stage 107 Plan Review

## Findings

**Critical: None.**

**Important: None.**

The plan is a clean, docs-test-only drift guard. All six planned phrases were verified present in the `## README Requirements` section of `docs/source-boundaries.md` after whitespace normalization and case-folding (lines 353, 355, 356, 357–358, 359–360, 394–395).

## Review Questions

**1. Does the plan protect a real boundary without changing product behavior or README text?**
Yes. The only code change is appending one test to `tests/test_source_boundaries_docs.py`. `docs/source-boundaries.md`, `README.md`, `src/`, and all runtime surfaces are explicitly disallowed and untouched. No behavior changes.

**2. Are the planned phrases present and scoped narrowly enough?**
Yes. `_section(doc, "README Requirements")` extracts only lines 351–418 (the section is last in the file, so it terminates at EOF; no `\n## ` follows). The `\n## ` split pattern does not false-match `\n### ` headings, and the section contains no `###` subheadings anyway. All six phrases verified present. The phrase set deliberately pins the general public-boundary obligations plus the handoff-readiness concept rather than every command-specific bullet — appropriately non-brittle.

**3. Does appending fit the Stage 106 file pattern?**
Yes, strictly better than a new file. The module already exposes `_read_source_boundaries_doc()`, `_normalized()`, `_section()`, and one sibling test (`test_source_boundaries_docs_keep_storage_boundary`). The new test reuses all three helpers with no new imports and mirrors the existing test's structure exactly.

**4. Does the plan avoid overlap with adjacent guards?**
Yes. It tests a distinct section (`## README Requirements`) from the existing Storage Boundaries guard. It does not touch `tests/test_cli_docs.py`, `tests/test_architecture_boundary_docs.py`, `tests/test_package_archives.py`, the robots/fetching section, or any runtime code. No README parity check is introduced.

**5. Are verification commands sufficient?**
Yes. Focused run on the target file, an adjacent docs/reference test batch, `ruff check`, `ruff format --check`, and `git diff --check`; Task 4 adds the full release gate (release hygiene, full pytest with proxy unset, repo-wide ruff, `uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, staged secret scan). More than sufficient for a docs-only guard.

## Minor Observations (optional, non-blocking)

- **O1 (Low):** The adjacent-test batch in Task 2 (`tests/test_package_archives.py`) is not docs-boundary related, but it is a harmless "don't break neighbors" grouping and runs fast.
- **O2 (Low):** The design doc's "Risks" section already notes the phrase set is intentionally partial. Consider that the wording in the design's "Test Shape" and the plan's Task 2 code are consistent — no drift between spec and plan.

**Verdict: Plan is acceptable. Proceed to Task 2.**
