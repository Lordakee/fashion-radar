I'll start by examining the relevant files and git state to perform this review.
Now let me examine the actual diff and the `## Output Boundaries` section in `docs/source-boundaries.md` to verify the phrases are present and scoped.
Let me run the verification commands to confirm everything passes.
Let me check the existing code-review artifacts to understand the expected output format.
Let me look at the Stage 107 code review for format reference, then write the proper review.
All verification passes. I have everything needed for the review.

---

# Stage 108 Code Review

Reviewed the working-tree change, design, plan, plan review, `docs/source-boundaries.md` `## Output Boundaries` section, and re-ran focused verification. Empirically confirmed: 3 tests pass, `test_source_boundaries_docs_keep_output_boundary` defined exactly once, ruff + format clean, `git diff --check` clean, all 10 phrases present in `## Output Boundaries` (`docs/source-boundaries.md:299-324`).

## Findings

**Critical:** None.

**Important:** None.

**Minor / Nitpick:** None.

## Answers To Review Questions

1. **Does the implementation match the Stage 108 plan and scope?** Yes. The net diff vs. HEAD appends one test, `test_source_boundaries_docs_keep_output_boundary` (`tests/test_source_boundaries_docs.py:66-85`), after the existing README-requirements test. It matches the plan's Task 2 snippet verbatim. The plan correctly treated Task 2 as verify-only because the body was already in the working tree (`docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md:145-152`), and there is no duplicate definition. `git status` shows only `tests/test_source_boundaries_docs.py` modified plus Stage 108 spec/plan/review artifacts untracked — no disallowed surface touched.

2. **Are the docs assertions present, stable enough, and limited to the `## Output Boundaries` section?** Yes. All 10 phrases are present verbatim in `docs/source-boundaries.md:299-324`:
   - `Reports and dashboards should describe signals, not assert certainty.` — line 301
   - `Preferred wording:` — line 303
   - `Mention count increased in this configured source set` — line 307
   - `Needs human review` — line 308
   - `Signal changed within this configured local source set` — line 312
   - `Imported row platform provenance label` — line 313
   - `Stored local provenance label, not platform coverage` — line 314
   - `Avoid wording that implies complete market truth:` — line 316
   - `This source-set signal proves external demand` — line 319
   - `This celebrity caused the trend` — line 320

   `_section("Output Boundaries")` extracts from `## Output Boundaries` to the next `\n## ` heading (`## Quality Boundaries`, line 333). The included `### Heat Movers` sub-block (lines 326-331) does not contain any of the 10 asserted phrases — its text has "needs review" but not "needs human review", so no false positive. Whitespace collapse + casefold makes the assertions robust to re-wrapping. Matches the design Risks section's explicit non-overlap with heat-mover/trend/scoring/candidate guards (`...design.md:79-84`).

3. **Is appending to `tests/test_source_boundaries_docs.py` clean and consistent with the existing helper pattern?** Yes. The new test reuses `_section`, `_read_source_boundaries_doc`, and `_normalized` with no new imports and mirrors the exact structure of the two sibling tests (`tests/test_source_boundaries_docs.py:23-44` and `:47-63`): read → `_section` → `_normalized` → `for phrase in (...): assert phrase.casefold() in normalized`. Appending to the shared module is preferable to a second source-boundaries docs file.

4. **Is the new guard independent from full negative-claim scanning, heat movers, trend deltas, scoring, candidate discovery, dashboard/report behavior, package archive checks, and runtime code?** Yes. Docs-only: reads one section of `docs/source-boundaries.md`, imports only `pathlib` and `Path`, executes no CLI, opens no SQLite, fetches no network, renders no dashboard/report, runs no collectors. The asserted phrases are output-wording-specific and intentionally do not duplicate heat-mover/trend-delta/scoring/candidate phrases (per design Risks section). `tests/test_cli_docs.py`, archive tests, robots/fetching, storage schema, and runtime code are untouched.

5. **Are there any Critical or Important issues that must be fixed before final verification, commit, and push?** No. No Critical or Important blockers.

## Verification Confirmed

- Focused: `uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q` → 3 passed.
- `uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py` → All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py` → 1 file already formatted.
- `git diff --check` → clean.
- `def test_source_boundaries_docs_keep_output_boundary` count = 1.

**Conclusion: No Critical or Important blockers. The implementation is approved to proceed to Task 4 (full verification, commit, push).**
