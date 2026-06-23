# Stage 183 Release Review

Scope: partial commit containing only the Stage 183 test-only change and its
spec/plan/review artifacts. Stage 184 working-tree changes
(`tests/test_lint_formatting.py`, `docs/...stage-184...`) are intentionally
pending and must be excluded.

## Independent re-verification

I re-ran the release gate rather than trusting the prompt:

- `pytest ...::test_rejects_wheel_entry_points_console_script_name_case_mismatch`
  -> 1 passed.
- `pytest tests/test_package_archives.py -q` -> 76 passed.
- Full `pytest -q` (proxy vars unset) -> 1385 passed.
- `ruff check` + `ruff format --check` on the touched file and repo-wide -> pass.
- `check_release_hygiene.py` -> passed.
- `check_first_run_smoke.py` -> passed.
- `UV_NO_CONFIG=1 uv lock --check` -> OK.
- `git diff --check` -> clean.
- `rg 'ghp_[A-Za-z0-9]+'` and `git config --get-all http.https://github.com/.extraheader`
  -> no output (clean).

All claimed results reproduced.

## Artifact sanitization

Reviewed all four committed review artifacts (plan-review prompt/response,
code-review prompt/response, release-review prompt). No live-capture stubs, no
duplicated or truncated text, no tool-status/ANSI chatter, no empty sections.
The spec and plan are complete with no placeholders. The plan/code reviews'
Minor nits (Traceback-assertion convention, hardcoded label) are acknowledged
and non-blocking.

## Scope integrity

`git status` confirms exactly two modified files:
`tests/test_package_archives.py` (Stage 183, in scope) and
`tests/test_lint_formatting.py` (Stage 184, out of scope). No runtime file under
`src/` or `scripts/` is modified, consistent with the "test-only, no runtime
change" claim. The plan's explicit `git add` list (plan lines 184-193) matches
the declared Stage 183 scope exactly and excludes the Stage 184 file, so the
partial commit will be correctly scoped as long as that list is used verbatim
(no `git add -A`/`git add .`).

## Critical
None.

## Important
None.

## Minor
1. `docs/reviews/opencode-stage-183-release-review.md` does not yet exist on
   disk; it is produced from this output. Ensure it is written before `git add`
   so the declared file list resolves and the partial commit is not missing a
   tracked artifact.
2. The Stage 184 modifications remain in the working tree (modified
   `tests/test_lint_formatting.py` plus four untracked Stage 184 docs). They are
   correctly excluded by the explicit `git add` list; just keep using that list
   verbatim so no Stage 184 work leaks into the Stage 183 commit.

## Verdict

Approve release. Test-only change, no runtime code touched, correct scoped
file set, and the full release gate (re-verified independently) is green with
no secrets or extraheader present. Only the two Minor notes above, neither of
which blocks commit and push.
