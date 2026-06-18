I'll review the Stage 107 implementation. Let me start by gathering the relevant context.
Now let me read the spec, plan, review artifacts, and the actual docs section being tested.
Let me run the verification commands and check the Stage 106 pattern for comparison.
All verification passes. Let me do a final independent check of phrase matching and section scoping.
I have all the information needed. Here are my findings.

---

# Stage 107 Code Review — Findings

## Critical
None.

## Important
None.

## Minor
None.

## Info

- **Implementation matches plan.** The appended test
  `test_source_boundarie# Stage 107 Code Review — Findings

**Critical: None. Important: None.**

The appended guard `test_source_boundaries_docs_keep_readme_requirements_boundary` (`tests/test_source_boundaries_docs.py:47-63`) matches the Stage 107 plan, reuses the Stage 106 helpers with no new imports, and all six phrases are present verbatim in the unique `## README Requirements` section (`docs/source-boundaries.md:351-418`).

Supporting detail:
- **Scope clean** — only `tests/test_source_boundaries_docs.py` modified; no `docs/source-boundaries.md`, `README.md`, `src/`, runtime/collector/robots/storage/CLI, or other disallowed surface touched.
- **Section scoping safe** — `## README Requirements` is the last `##` heading, so `_section()` runs to EOF; the `"\n## "` split can't false-match `###` (and none exist in-section). Independence from README parity, CLI docs, architecture docs, package archives, robots/fetching, and runtime code confirmed.
- **Verification green** — focused 2 passed; adjacent batch 96 passed; `ruff check`/`ruff format --check` clean; `git diff --check` clean.

Only note is **Info-level**: phrase 6's source line-wrap differs cosmetically from the plan snippet (identical concatenated string; `ruff format` produces the single-line form) — not a blocker.

**Verdict: approved to proceed to Task 4 (full verification, commit, push).** Full review written to `docs/reviews/opencode-stage-107-code-review.md`.
ified phrase anchors:
  - `The public README must explain:` — `docs/source-boundaries.md:353`
  - `The project does not provide full social-platform coverage.` — line 355
  - `Users are responsible for respecting source terms, robots rules, and API terms.` — line 356
  - `The default workflow avoids account-based collection and access-control bypasses.` — lines 357-358 (hard-wrapped bullet)
  - `Manual signal import is a local input path, not a platform connector or instructions for obtaining platform exports.` — lines 359-360 (hard-wrapped bullet)
  - `Community handoff check directory reports are local-only handoff readiness reports.` — lines 394-395 (hard-wrapped bullet)
  The hard-wrapped bullets match because `_normalized()`
  (`tests/test_source_boundaries_docs.py:13-14`) collapses all whitespace and
  case-folds, and the test phrases use single-space form.
- **Section extraction is safe.** `_section(doc, "README Requirements")`
  splits on `"## README Requirements"` (unique occurrence) then on the next
  `"\n## "`. Because `## README Requirements` is the last `##` heading in the
  file, the second split returns to EOF — no sibling-section bleed. The split
  pattern `"\n## "` (hash-hash-space) cannot match a `"### "` subheading
  (hash-hash-hash-space); the section also contains no `###` subheadings
  (independently verified). This matches the Stage 106 extraction semantics.
- **Pattern consistent with Stage 106.** The new test mirrors the existing
  `test_source_boundaries_docs_keep_storage_boundary()`
  (`tests/test_source_boundaries_docs.py:23-44`) exactly in structure: read →
  `_section` → `_normalized` → for-loop phrase assertion. Appending to the same
  module (rather than a new file) is the correct choice since the helpers and
  fixture doc are shared. This is strictly better than a second source-boundaries
  docs test file.
- **No overlap with adjacent guards.** The guard targets a distinct section
  (`## README Requirements`) from the existing Storage Boundaries guard
  (`## Storage Boundaries`). It does not read `README.md`, so it introduces no
  README parity check. `tests/test_cli_docs.py` (broad CLI boundary linkage),
  `tests/test_architecture_boundary_docs.py` (`docs/architecture.md`),
  `tests/test_package_archives.py` (archive-only), and the robots/fetching
  section are all untouched and unrelated. No runtime collector/storage code is
  imported or exercised.
- **Scope compliance verified.** `git status` shows only `tests/test_source_boundaries_docs.py`
  modified, plus Stage 107 spec, plan, and review artifacts as untracked. No
  changes to `docs/source-boundaries.md`, `README.md`, `src/`, `scripts/`,
  `examples/`, configs, schemas, dependency manifests, `uv.lock`, CI workflows,
  package metadata, archive tests, release-hygiene behavior, `.gitignore`,
  `tests/test_cli_docs.py`, or any runtime/collector/robots/storage/CLI surface.
- **Verification confirmed.** Focused run: `tests/test_source_boundaries_docs.py`
  — 2 passed. Adjacent batch (`test_source_boundaries_docs.py`,
  `test_architecture_boundary_docs.py`, `test_cli_docs.py`,
  `test_package_archives.py`) — 96 passed. `ruff check` clean,
  `ruff format --check` reports the file already formatted, `git diff --check`
  clean. An independent programmatic re-extraction of `## README Requirements`
  confirmed all six phrases match within the section and that the section
  terminates at EOF with no inner `###` subheading.
- **Intentional partial coverage (non-brittle).** The `## README Requirements`
  section contains many additional bullets (lines 361-418) covering
  command-specific obligations already pinned by other guards or out of scope
  for this stage. The design's "Risks" section
  (`docs/superpowers/specs/2026-06-18-stage-107-source-boundaries-readme-requirements-docs-design.md:74-80`)
  explicitly documents that Stage 107 pins only the general public-boundary
  obligations plus the local handoff-readiness concept. This is appropriately
  non-brittle.

## Review Question Answers

1. **Does the implementation match the Stage 107 plan and scope?** Yes. The
   appended test matches the plan's Task 2 snippet (modulo one cosmetic
   line-wrap that `ruff format` reconciled), only allowed files are touched,
   and no disallowed area is modified.
2. **Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## README Requirements` section?** Yes. All six
   phrases are present verbatim in the unique `## README Requirements` section
   (lines 351-418). `_section()` extraction is bounded by EOF (last `##`
   section) and is immune to `###` subheading false matches. Whitespace
   normalization makes the assertions robust to re-wrapping while still
   catching semantic drift.
3. **Is appending to `tests/test_source_boundaries_docs.py` clean and
   consistent with the Stage 106 helper pattern?** Yes. It reuses all three
   helpers with no new imports and mirrors the sibling Storage Boundaries test
   structure exactly. Appending is preferable to a second source-boundaries
   docs test file.
4. **Is the new guard independent from full README parity, CLI broad boundary
   checks, architecture source-boundary docs, robots/fetching, package archive
   checks, and runtime collector/storage behavior?** Yes. It reads only one
   section of `docs/source-boundaries.md`, never reads `README.md`, imports no
   application code, executes no CLI, opens no SQLite, and does not overlap
   with any adjacent docs/archive/runtime guard.
5. **Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?** No. No Critical or Important blockers.

**Conclusion: No Critical or Important blockers. The implementation is approved
to proceed to Task 4 (full verification, commit, push).**
