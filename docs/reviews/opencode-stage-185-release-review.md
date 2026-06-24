# Stage 185 Release Review

## Scope confirmation
- Runtime diff is confined to `validate_trends` in `scripts/check_first_run_smoke.py:2273-2278` (silent-skip comprehension -> indexed `SmokeError` loop, 1-based, matching the file's step/adapter/row convention).
- Test diff is one new regression, `tests/test_first_run_smoke.py:3538-3545`, placed immediately after the existing trends validator test.
- No CLI runtime, trend generation, scoring, model, dashboard, dependency, pyproject, or lockfile changes. Boundaries in AGENTS.md respected.

## Fresh verification (re-run)
- New test: 1 passed.
- Full `tests/test_first_run_smoke.py`: 164 passed.
- `ruff check` + `ruff format --check` on touched files: clean.
- `git diff --check`: clean.
- `UV_NO_CONFIG=1 uv lock --check`: LOCK_OK (84 packages).
- `rg 'ghp_...'`: exit 1, no output. `git config --get-all http.https://github.com/.extraheader`: exit 1, no output.
- `check_first_run_smoke.py`: passed. `check_release_hygiene.py`: passed.

## Artifact sanitization
- `opencode-stage-185-plan-review.md` and `opencode-stage-185-code-review.md` contain completed review output with verdicts. Scan for ANSI, `opencode run`, `tmp_review`/`mktemp`, tool-status, and exit-code chatter returned no matches. No stubs, duplication, or truncation.

## Findings

### Critical
None.

### Important
None.

### Minor
1. Spec/plan vs. shipped naming drift. The spec and plan propose `delta_rows: list[Mapping[str, Any]]` and renaming `deltas_by_name` -> `delta_rows_by_name`; the implementation uses `checked_deltas: list[dict[str, Any]]` and keeps `deltas_by_name`. This is benign and was already reconciled in the plan review (rename flagged optional; `dict[str, Any]` noted as marginally more precise) and acknowledged in the code review. Noisy only for spec-to-code traceability, not blocking.
2. `docs/reviews/opencode-stage-185-release-review.md` is not yet in the working tree (this review produces it). The plan's `git add` list (Task 3, Step 3) includes it, so write and stage this artifact before commit; otherwise the listed-file set in the commit prompt will be incomplete.

## Verdict
Approve. Minimal, convention-consistent hardening that converts a silent skip into a precise, indexed `SmokeError`. All release-gate checks independently re-verified green, artifacts sanitized, scope strictly limited to first-run smoke validation. Address Minor 2 (write this review to `opencode-stage-185-release-review.md` and stage it) before commit and push; Minor 1 is informational only.
