I'll review the Stage 112 plan. Let me read all the relevant files first.
I've reviewed all files. Here are my findings.

---

# Stage 112 Plan Review

## Findings

### Critical
None.

### Important
None.

### Minor

**M1. README insertion anchor is mildly ambiguous.**
The spec (line 37-38) and plan (Task 2) both say *"immediately after the opening paragraph in README `## What It Does Not Do`"*. The section opens with one Markdown paragraph block (README.md:87-94, no blank lines between the "Fashion Radar v0.1.0…", "Manual signal import…", and "Stored imported `platform` labels…" sentences) followed by a blank line and the external-tool-handoff content at README.md:96. "Opening paragraph" could be misread as only the first two sentences. The parity test passes regardless of placement (it does presence checks over the whole section up to `## Quickstart`), so this is not test-breaking, but pinning the anchor to e.g. *"after the paragraph ending '…coverage, or demand proof.'"* would remove ambiguity for the implementer.

**M2. Brief-side assertions are duplicated.**
The new `test_readme_keeps_project_brief_mvp_non_goal_parity` re-asserts each `brief_phrase.casefold() in normalized_brief`, which is already fully pinned by the existing `test_project_brief_docs_keep_mvp_non_goals_boundary` (tests/test_project_brief_docs.py:23-42). This is an intentional, self-contained parity test and the redundancy documents intent in one place, but it creates two update sites if brief wording changes. Acceptable as-is; consider whether the brief-side half is needed at all.

**M3. Design's extraction-scope claim vs. actual extraction.**
The design (line 84-86) says the README side "should remain scoped to the opening `What It Does Not Do` non-goals text … not the later external-tool-handoff boundary matrix." The reused `_section` helper (tests/test_project_brief_docs.py:17-20) splits on `\n## `, so it actually captures the entire section from README.md:85 through `## Quickstart` at README.md:223, including all external-tool-handoff/adapter-registry/boundary-matrix content. This is harmless because the guard only does positive presence checks, but the design sentence overstates the extraction precision.

## Answers To Review Questions

1. **README paragraph alignment** — Accurate. The paragraph covers exactly the 8 of 9 brief MVP non-goals (correctly excluding the internal-pipeline "No LLM dependency…" bullet by design). Rewording "No claim that the tool provides full-platform … coverage" → "no full-platform … coverage claim" is semantically equivalent and appropriate for a public summary. No behavior change.

2. **Guard narrowness and file placement** — Yes. Single test function in the correct file (`tests/test_project_brief_docs.py`, the brief-side guard file). I verified all 8 `readme_phrase` substrings match the planned paragraph after whitespace-normalization + casefold, and all 8 `brief_phrase` substrings match PROJECT_BRIEF.md:65-73. No source-boundaries, CLI-docs, or adapter-registry content is pulled in.

3. **Phrase stability / overlap** — Stable and public-facing. Existing `test_source_boundaries_docs.py` checks `docs/source-boundaries.md` (not README) for different phrasing ("The project does not provide full social-platform coverage."), and `test_cli_docs.py` README tests target Quickstart/Start Here/External Tool Import Path — none pin these 8 MVP non-goal phrases in README's `## What It Does Not Do`. No existing coverage; the guard adds genuine value.

4. **Scope avoidance** — Clean. Only `README.md` + `tests/test_project_brief_docs.py` + review artifacts. No runtime, connector, scraping, platform, dependency, CI, or compliance changes. The Task 4 `git diff --exit-code -- uv.lock pyproject.toml` guard and the disallowed-changes list reinforce this.

5. **Verification commands** — Sufficient. Focused (`test_project_brief_docs.py`), adjacent (adds `test_cli_docs.py` + `test_source_boundaries_docs.py` which pin nearby README/CLI wording), ruff check + format check + `git diff --check`, then full release gate in Task 4. Appropriate for a docs/docs-test stage.

## Recommendation

Proceed to Task 2. No Critical/Important blockers. Optionally address M1 (pin the exact insertion anchor) before implementation to avoid a misplaced paragraph.
