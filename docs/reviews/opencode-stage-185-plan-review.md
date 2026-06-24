# Stage 185 Plan Review

## Summary

The plan is a focused, minimal first-run smoke hardening change. It replaces
the silent-skip comprehension in `scripts/check_first_run_smoke.py::validate_trends`
with an explicit per-entry object check that raises an indexed `SmokeError`, and
adds one direct regression test. Scope, boundaries, and verification flow are all
appropriate.

## Critical

None.

## Important

None.

## Minor

1. The rename `deltas_by_name` → `delta_rows_by_name` is optional. The original
   name remains accurate after the change, but the new name is slightly more
   descriptive of "built from validated rows." Harmless either way; just be
   aware it touches two downstream references at `scripts/check_first_run_smoke.py:2276`
   and `:2280` plus the definition at `:2273`.
2. The proposed annotation `list[Mapping[str, Any]]` is fine and `Mapping` is
   already imported (`scripts/check_first_run_smoke.py:14`), but the runtime
   objects are JSON dicts, so `list[dict[str, Any]]` would be marginally more
   precise. Not blocking.

## Question Coverage

1. **Objective satisfied?** Yes. The current comprehension at
   `scripts/check_first_run_smoke.py:2273`
   (`... if isinstance(delta, dict)`) silently drops non-object entries. The
   proposed loop raises `SmokeError(f"{command_name} delta {index} must be a JSON object")`
   with a 1-based index, matching the established pattern used for steps
   (`:1182`, `:1270`, `:1332`), adapters (`:1364`), and rows (`:1557`).
2. **Failing test meaningful and consistently placed?** Yes. It builds a valid
   `trends_payload()`, appends `"not-a-delta"` as the 4th entry, and asserts
   `match="trends delta 4 must be a JSON object"`. Placement "immediately after"
   `test_validate_candidates_and_trends_pin_expected_first_run_state`
   (`tests/test_first_run_smoke.py:3518`) groups it with the existing trends
   validator tests and matches existing style.
3. **Runtime change minimal and limited?** Yes. Touched lines are confined to
   `validate_trends(...)`. The structural check runs before the existing
   expected-names, `signal_kind`, `signal_type`, and `status` assertions, which
   are otherwise unchanged. `deltas_by_name` is a local variable with exactly
   three in-function references, all covered by the rename.
4. **Focused verification sufficient?** Yes. Task 2 runs the trends/candidates
   subset, then the full smoke file, then `ruff check` and `ruff format --check`
   on both touched files before Task 3's full release gate (full pytest, smoke
   script, release hygiene, repo-wide ruff, `uv lock --check`, `git diff --check`,
   and secret/extra-header scans).
5. **Boundaries respected?** Yes. No source acquisition, scraping, browser
   automation, platform APIs, monitoring, scheduling, ranking, demand proof,
   coverage verification, or compliance-review behavior. No dependency,
   lockfile, or package archive changes (no `uv add`/pyproject edits). Change
   is strictly structural first-run smoke validation.

## TDD Discipline

The plan correctly separates the pre-check (Step 1 confirms the test is not yet
collected) from the RED check (Step 3 confirms the new test fails because
validation silently skips), then GREEN (Step 5). This is sound.

## Verdict

Approve implementation. No critical or important findings; the two minor notes
are stylistic and non-blocking.
