# Stage 165 Plan Review

## Question 1: Scope correctness

Stage 165 is correctly scoped. The plan adds a single focused test module,
`tests/test_lint_formatting.py`, that imports only
`format_count_label` and `format_finding_counts` from
`fashion_radar.lint_formatting`. No production file is touched, no renderer or
caller test is expanded, and the out-of-scope list in the design doc explicitly
excludes renderer/CLI/JSON/docs/semantics/grammar changes. The plan matches the
design doc's scope.

## Question 2: Characterization-test approach

Appropriate. The helper already exists at `src/fashion_radar/lint_formatting.py`
and currently satisfies the intended contract. The plan and design both state
that the usual RED step does not apply, forbid editing the helper to manufacture
a failing test, and only allow production edits if the characterization tests
expose a real mismatch. This matches the project's characterization-test
convention for existing behavior.

## Question 3: Coverage of zero, one, plural, and mixed counts

Coverage is complete.

`format_count_label` is parametrized over `(0, 1, 2)` for `error`/`errors`,
which exercises zero, singular, and plural label selection directly.

`format_finding_counts` is covered by four direct assertions:

- zero: `format_finding_counts(0, 0, 0) == "0 errors, 0 warnings, 0 info"`
- singular: `format_finding_counts(1, 1, 1) == "1 error, 1 warning, 1 info"`
- plural: `format_finding_counts(2, 2, 2) == "2 errors, 2 warnings, 2 info"`
- mixed: `format_finding_counts(1, 0, 2) == "1 error, 0 warnings, 2 info"`

The `info` invariant is covered because the info slot is exercised at 0, 1, and
2 in the four `format_finding_counts` tests, and every expected string keeps the
word `info`. The production code passes `'info', 'info'` for both singular and
plural, so the invariant is a direct consequence and the tests pin it.

I verified each expected string against `src/fashion_radar/lint_formatting.py`
line by line; all four `format_finding_counts` assertions and all three
`format_count_label` rows match the current implementation exactly.

## Question 4: No behavior/renderer/CLI/JSON/docs/grammar changes

Confirmed. The plan creates only `tests/test_lint_formatting.py` plus review
artifacts. No file under `src/` is modified. The renderer regression step
(Task 1, Step 3) only *runs* existing renderer tests with `-k "render_"`; it
does not modify them. Row-count strings such as `Sources: ... total`,
`Entities: ... total`, `Rows: ... total`, and `Files: ...` live in the renderer
modules and are not touched by this stage, so row-count grammar is preserved.

The design doc's "Out of scope" list and the plan's "Architecture" note both
restate this constraint, and the implementation step explicitly forbids
temporarily breaking the helper.

## Question 5: Verification, review, release, commit, and push completeness

Complete.

- Focused verification (Task 1, Steps 2-4): focused pytest module, dependent
  renderer pytest selection with `-k "render_"`, and ruff check + format check
  on the new test file. Matches the design doc's focused verification block.
- Release gate (Task 2, Step 3): full pytest with proxy env vars stripped,
  `scripts/check_first_run_smoke.py`, `scripts/check_release_hygiene.py`,
  `ruff check .`, `ruff format --check .`, `UV_NO_CONFIG=1 uv lock --check`,
  `git diff --check`, `rg 'ghp_...'` token scan, and the GitHub extraheader
  check. This mirrors the design doc's release-gate block exactly.
- Code review (Task 2, Steps 1-2): prompt file requiring the
  `# Stage 165 Code Review` heading, then the documented `opencode run` capture
  flow with temp file, sed preview, copy, and cleanup.
- Release review (Task 2, Steps 4-5): prompt file requiring the
  `# Stage 165 Release Review` heading, then the same capture flow.
- Commit and push (Task 2, Step 6): `git status --short`, explicit `git add`
  list covering the spec, plan, four review artifacts, and the new test file,
  followed by `git commit -m "test: cover lint finding formatting helper"` and
  `git push origin main`. The added-files list matches the Files section.

The two prompt files requiring specific headings satisfy the review capture
hygiene rule in `docs/REVIEW_PROTOCOL.md`.

## Question 6: Critical or important findings before implementation

No critical findings.

No important findings.

## Minor findings

1. The release gate relies on `scripts/check_release_hygiene.py` to cover the
   package build, installed-wheel, packaged-resource, and optional dashboard
   extra smoke checks referenced in `docs/REVIEW_PROTOCOL.md` "Before GitHub
   Upload" step 3. The design doc's release-gate block makes the same
   assumption, so the plan is internally consistent. If a future stage splits
   `check_release_hygiene.py` into smaller scripts, this stage's release gate
   will need to track that change. Not blocking for Stage 165.

2. The parametrized test name
   `test_format_count_label_uses_singular_only_for_one` is accurate and clear;
   the wording is slightly long but matches the rest of the suite's descriptive
   style. Style observation only, not a change request.

## Verdict

No blocking findings. The plan is acceptable for implementation. Proceed to
Task 1.
