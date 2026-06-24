# Stage 185 Code Review

## Scope inspected
- `scripts/check_first_run_smoke.py` — `validate_trends` (lines 2261–2288)
- `tests/test_first_run_smoke.py` — new `test_validate_trends_rejects_non_object_delta_entries` (lines 3538–3545) plus `trends_payload()` fixture (lines 604–631)

## Fresh verification (re-run)
- New test + existing trends test: 2 passed.
- Full `tests/test_first_run_smoke.py`: 164 passed.
- `ruff check`: All checks passed. `ruff format --check`: already formatted.
- `git diff --check`: clean.

## Findings

### Critical
None.

### Important
None.

### Minor
1. Stylistic note only (not a fix): the introduced `checked_deltas: list[dict[str, Any]]` intermediate is slightly more verbose than the inline pattern used by the neighboring `adapters` validator (scripts/check_first_run_smoke.py:1362-1366), which narrows and consumes in one loop. Keeping the explicit list is defensible here because `deltas_by_name` is built with a `str(...)` coercion that reads cleaner as a comprehension over the pre-narrowed list, and the type annotation aids static narrowing. Consistent enough with the file; leave as-is.

## Answers to review questions

1. **Does the new test prove the previous silent-skip gap?** Yes. Under the old `if isinstance(delta, dict)` comprehension, appending `"not-a-delta"` to the 3-entry fixture would silently drop it, leaving `deltas_by_name` with exactly the 3 expected names, so `assert_equal(... entity delta names ...)` passed and no `SmokeError` was raised. The new test asserts that `SmokeError("trends delta 4 must be a JSON object")` is now raised, closing the gap. The user's report that the test first failed pre-change, then passed post-change, matches the logic.

2. **Minimal and correctly indexed?** Yes. The change replaces one dict-comprehension with an `enumerate(deltas, start=1)` loop that raises on the first non-`dict` entry before building `deltas_by_name`. This matches the established 1-based convention used throughout the file (step/adapter/row validators at scripts/check_first_run_smoke.py:1180, 1268, 1330, 1362, 1555 all use `enumerate(..., start=1)` with the same `must be a JSON object` phrasing). The `trends_payload()` fixture has exactly 3 deltas, so the appended string is the 4th entry → `delta 4` is correct.

3. **Preserves behavior for valid dict deltas?** Yes. For an all-dicts payload, `checked_deltas` is identical to the filtered input and `deltas_by_name` is built by the same `str(delta.get("name"))` comprehension. The existing happy-path call `smoke.validate_trends("trends", trends_payload())` (tests/test_first_run_smoke.py:3520) still passes, confirmed in the fresh run.

4. **Anything outside first-run smoke validation affected?** No. The runtime diff is confined to `validate_trends` in the smoke validator. The `trends_payload()` fixture is unchanged, and its other use site (tests/test_first_run_smoke.py:4038) consumes the untouched 3-delta fixture. No CLI runtime, trend generation, scoring, model, dashboard, dependency, or lockfile changes. `Any` was already imported (scripts/check_first_run_smoke.py:17), so the new annotation introduces no new dependency.

## Verdict
**Approve.** Minimal, convention-consistent hardening that converts a silent skip into an explicit, well-indexed error. Test correctly proves the prior gap and is scoped to the trends validator. No out-of-scope impact.
