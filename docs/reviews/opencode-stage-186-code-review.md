# Stage 186 Code Review

Scope reviewed: the Stage 186 diff in `tests/test_first_run_smoke.py`
(+28/-5). Confirmed via `git status` that this is the only modified
tracked file; remaining paths are untracked spec/plan/review artifacts.

## Verification re-run (independent)

- `pytest tests/test_first_run_smoke.py -q -k "readiness_payload_parity or skip_guard"`:
  3 passed, 163 deselected.
- `pytest tests/test_first_run_smoke.py -q`: 166 passed.

These match the reported results.

## Findings

### Critical

None.

### Important

None.

### Minor

1. **Meta-test name now slightly understates the guard.**
   `test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`
   (tests/test_first_run_smoke.py:1508) still says "conditionally_skipped",
   but after delegating to `has_blocking_readiness_parity_skip_mark` it also
   rejects an *unconditional* bare `pytest.mark.skip`. The word
   "conditionally" is now a mild misnomer. A future rename to
   `..._is_not_skipped_or_skipif_marked` would be more precise, but renaming
   is pure churn and out of this stage's scope; flagged for awareness only.

2. **Vacuous-pass trade-off carried forward from Stage 172 Minor #2.**
   `has_blocking_readiness_parity_skip_mark` still does
   `getattr(test_func, "pytestmark", [])` with an empty-list default, so a
   caller passing a function that legitimately lacks `pytestmark` would get
   a vacuous pass rather than a loud failure. This is unchanged from Stage
   172, is explicitly documented in the Stage 186 plan review (Minor #2),
   and is mitigated here in two ways: (a) the new parametrized synthetic
   test always attaches a real mark, exercising the non-empty path; and
   (b) the meta test references the real parity function by direct
   same-module name, so it cannot silently drift to a wrong target without
   a two-site rename. No action required; noted for continuity.

3. **`mark_name` parameter is used only as an assertion message.**
   In `test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks`
   (tests/test_first_run_smoke.py:1521-1530) `mark_name` is passed solely as
   the `assert ..., mark_name` failure message; it does not drive logic.
   This is a reasonable readability choice (parametrize IDs alone are less
   explicit on failure) and needs no change — recorded only so the intent
   is not mistaken for dead input.

## Review questions

1. **Does the helper and synthetic test meaningfully close the Stage 172
   `skip` follow-up gap?** Yes. The Stage 172 code review
   (docs/reviews/opencode-stage-172-code-review.md:49-56) explicitly named
   bare `@pytest.mark.skip`, module-level `pytest.importorskip`, and bare
   `skip` marks as uncaught, and proposed
   `not any(mark.name in {"skipif", "skip"} for mark in marks)` as an
   "explicitly out-of-scope follow-up." Stage 186 implements that exact
   membership test (`frozenset({"skipif", "skip")`) inside a reusable
   helper and proves detection of both mark kinds with a parametrized
   synthetic regression. This closes the `skipif`+`skip` portion of the
   gap. `pytest.importorskip` is a separate module-level mechanism that
   does not populate a per-function `pytestmark` the same way, so leaving
   it out of scope is faithful to the Stage 172 framing, not a regression.

2. **Does the existing readiness parity meta test now reject both
   `skipif` and bare `skip` marks?** Yes.
   `test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`
   now asserts
   `not has_blocking_readiness_parity_skip_mark(<parity fn>)`, and the
   helper checks `mark.name in {"skipif", "skip"}`, so both decorators
   are rejected. The real parity function at
   tests/test_first_run_smoke.py:1487 carries no marks, so the meta test
   passes for the right reason (empty `pytestmark`), and the synthetic
   test proves the guard actually fires when a mark is present — so this
   is no longer a purely vacuous GREEN like Stage 172's was.

3. **Is the change appropriately test-only and limited to
   `tests/test_first_run_smoke.py`?** Yes. `git status --porcelain` shows
   only ` M tests/test_first_run_smoke.py` as modified (+28/-5); every
   other path is an untracked review/plan/spec artifact. No runtime
   module, smoke script, payload shape, command ordering, adapter
   metadata, readiness boundary, install hint, mirror hint, dependency,
   or lockfile changes. `Callable` is already imported at
   tests/test_first_run_smoke.py:9, so the helper's annotation adds no
   new import. No source acquisition, scraping, platform API, account /
   cookie / token behavior, ranking, coverage verification, or
   compliance-review product behavior is introduced.

4. **Is the helper placement/naming acceptable for this test module?**
   Yes. `BLOCKING_READINESS_PARITY_SKIP_MARKS` is a module-level
   `frozenset` constant co-located with the helper and the meta test that
   consumes both, sitting directly between the parity function (line 1487)
   and the meta test (line 1508). This matches the file's existing
   convention of defining small local helpers near their callers. The
   name `has_blocking_readiness_parity_skip_mark` is descriptive and
   boolean-shaped, consistent with sibling predicate helpers.

## Verdict

Approve. The change is a clean, test-only hardening that closes the
documented Stage 172 `skip`/`skipif` follow-up gap with the exact
membership expression Stage 172 proposed, gives a previously vacuous meta
test a genuine non-vacuous RED/GREEN path via the parametrized synthetic
regression, stays strictly within `tests/test_first_run_smoke.py`, adds
no new imports or dependencies, and touches no runtime source, payload,
boundary, or compliance behavior. No critical or important findings; the
three minor notes are awareness items and do not block commit/push.
