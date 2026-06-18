I'll review the Stage 106 plan. Let me start by reading the three target files in parallel.
I have all three files. Let me verify the supporting facts: confirm the referenced adjacent test files exist, the target test file doesn't already exist, and check the `## Storage Boundaries` section content precisely.
I have verified everything needed. Here is my review.

---

# Stage 106 Plan Review — Findings

## Critical
None.

## Important
None.

## Minor
None.

## Info

- **Phrase presence verified.** All 9 planned phrases appear verbatim in the `## Storage Boundaries` section of `docs/source-boundaries.md` (lines 266–277), confirmed by ripgrep. The section is bounded by `## Robots And Fetching` at line 279, so `_section()` captures only the intended lines.
- **Wrapped-line phrase matches correctly.** The long phrase (plan line 173–175 / spec line 39) spans a hard-wrapped bullet in the doc (lines 268–270, with leading continuation spaces). The `" ".join(text.split()).casefold()` normalization collapses that whitespace to single spaces, and the phrase's own single-space form is a substring of the result. Verified by inspection.
- **Section scoping is robust.** `_section()` splits on `"\n## "`, which is not a substring of `"\n### "` (an `H3` would need `\n## ` = `\n`,`#`,`#`,` ` but `###` gives `\n`,`#`,`#`,`#`). So an `H3` subheading inside the section would not prematurely terminate extraction. There are no `H3`s in this section anyway, and `## Storage Boundaries` occurs exactly once.
- **No scope duplication.** The 9 phrases are unique to `## Storage Boundaries`; none recur in `## Robots And Fetching`, `## Output Boundaries`, `## README Requirements`, or elsewhere — so the guard catches real drift rather than duplicating wording that other tests cover.
- **Adjacent files intact.** `tests/test_source_boundaries_docs.py` does not yet exist (correct, it is new). The three adjacent modules referenced by the focused-verification command — `tests/test_architecture_boundary_docs.py`, `tests/test_cli_docs.py`, `tests/test_package_archives.py` — all exist and are not modified. `docs/reviews/` exists for the review artifacts.
- **No behavior change.** Allowed-changes list (`tests/test_source_boundaries_docs.py` + Stage 106 review artifacts) and disallowed-changes list (`docs/source-boundaries.md`, `src/`, `scripts/`, schemas, `uv.lock`, CI, runtime/collector/robots/storage/dashboard/report code, compliance features, etc.) match the design doc and keep the stage docs-test-only. No product behavior is touched.
- **Verification is sufficient.** Task 2 covers focused test + adjacent docs tests + `ruff check` + `ruff format --check` + `git diff --check`. Task 4 adds the full release gate (release hygiene, full pytest with proxy vars unset, repo-wide ruff check/format, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene + staged secret scan). Appropriate for a docs-only guard.

## Review Question Answers

1. **Does the plan protect a real storage boundary without changing product behavior?** Yes. It adds a read-only docs drift guard over `## Storage Boundaries` and touches no `src/`, schema, CLI, collector, robots/fetching, storage, dashboard, or report code.
2. **Are the planned phrases present and scoped narrowly enough?** Yes. All 9 phrases are present verbatim within `## Storage Boundaries` (lines 266–277), the `_section()` helper extracts only that section, and the phrases are unique to it.
3. **Does the plan avoid overlap with adjacent concerns?** Yes. It excludes robots/fetching, output wording, README requirements, architecture source-boundary docs, package-archive checks, and runtime collector/storage code; it neither modifies nor duplicates `tests/test_cli_docs.py`, `tests/test_architecture_boundary_docs.py`, or `tests/test_package_archives.py`.
4. **Are the verification commands sufficient?** Yes. Focused + adjacent + style checks in Task 2, plus the full release gate in Task 4, are adequate for a docs-only guard.

**Conclusion: No Critical or Important blockers. The plan is approved to proceed to Task 2.**
