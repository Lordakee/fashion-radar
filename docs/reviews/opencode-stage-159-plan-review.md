# Stage 159 Plan Review

## Verdict

One critical finding blocks the stage as designed. The proposed U+2192 UI-marker
check is a bare substring match and will reject legitimate review prose.
Existing opencode reviews from stages 150-158 already contain 14 arrow
occurrences in lines such as `pytest tests/test_first_run_smoke.py -q -> 115
passed` and `updates_local_matches -> read_only is a real semantic change`. The
established reviewer style will carry into Stage 159+, so this gate would block
well-formed Stage 159+ reviews, which conflicts with the low-false-positive
goal.

Two important findings and several minor findings were reported.

## Answers To Review Questions

1. Stage 159+ review artifact hygiene is a safe and useful next narrow stage.
   Reusing `scripts/check_release_hygiene.py`, staying process-only, and leaving
   product/runtime behavior untouched is consistent with the project workflow.

2. The Stage 159 enforcement floor is appropriate. It cleanly excludes older
   records and legacy capture styles.

3. The proposed markers are not all narrow enough. ANSI, empty-output,
   first-line process chatter, and most tool-status prefixes are narrow. The
   bare U+2192 marker is too broad.

4. The RED tests substantively cover tracked/untracked files plus prompt and
   Stage 158 exclusions. The prompt exclusion test should be selected by the
   focused test filter.

5. The plan preserves product scope boundaries. No social connectors, scraping,
   browser automation, platform APIs, login/session/cookie behavior, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage verification,
   or compliance-review product features are introduced.

6. Release-gate/review-gate steps need minor additions: include release hygiene
   in the final gate and account for the final release review artifact.

## Findings

### Critical

- C1: Bare U+2192 substring matching rejects legitimate review analysis.
  `has_review_tool_ui_marker` as planned flags any line containing the arrow,
  but existing valid reviews use arrows in normal prose and command summaries.
  Fix by requiring the arrow or star marker at the start of the stripped line,
  or by dropping the bare-arrow marker and relying on specific opencode status
  phrases. Add a RED test proving a Stage 159 review body containing
  `pytest -q -> 120 passed` is accepted.

### Important

- I1: The path regex misses numbered rereviews such as `-rereview-2.md` and
  `-rereview-3.md`. The repository already uses numbered rereview files. Extend
  the pattern to match `rereview-N` files or explicitly document that exclusion.
  Add a RED test for a numbered rereview artifact.

### Minor

- M1: Add a RED test for empty review output.

- M2: Ensure the focused `-k "review_artifact or review_capture"` command
  selects the prompt-exclusion test, either by renaming the test or broadening
  the filter.

- M3: Add `uv --no-config run --frozen python scripts/check_release_hygiene.py
  --repo-root .` to the final release gate.

- M4: Add an explicit note that `opencode-stage-159-plan-review.md` is created
  by this plan-review capture. Add a Stage 159 release-review artifact or
  document why the code review suffices.

- M5: Use a commit prefix that reflects both tests and implementation, such as
  `chore:`.

## Summary

Not ready to implement until C1 is resolved and I1 is fixed or explicitly
scoped. With those changes, the design is sound and the scope boundaries are
preserved.
