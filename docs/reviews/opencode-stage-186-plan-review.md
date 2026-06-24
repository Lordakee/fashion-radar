# Stage 186 Plan Review

Objective:

Broaden the first-run smoke readiness parity meta guard so it rejects both
`pytest.mark.skipif` and bare `pytest.mark.skip` on
`test_external_tool_readiness_payload_matches_real_rednote_readiness`, closing
the documented Stage 172 follow-up gap.

## Summary

The Stage 186 plan is a clean, tightly scoped, test-only hardening of
`tests/test_first_run_smoke.py` that directly retires the narrowness flagged in
both Stage 172 reviews. It introduces a test-local
`BLOCKING_READINESS_PARITY_SKIP_MARKS = frozenset({"skipif", "skip"})` and a
small `has_blocking_readiness_parity_skip_mark(...)` helper, proves the helper
detects both mark kinds via a parametrized synthetic regression test, and
rewrites the existing
`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped` meta
test to delegate to that helper.

The plan is boundary-compliant and internally consistent with the current file
state. I confirmed `tests/test_first_run_smoke.py:1500-1507` still holds the
Stage 172 `all(mark.name != "skipif" for mark in marks)` guard, that the real
parity function at `:1487` carries no marks, and that `Callable` is already
imported at `:9` (`from collections.abc import Callable`), so the helper adds no
new dependency or import. The Files section limits code changes to
`tests/test_first_run_smoke.py`; every other listed path is a new
spec/plan/review artifact.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The focused verification `-k "readiness_payload_parity or skip_guard"`
   filter (Task 2, Step 1) selects the new skip-guard test and the existing
   meta test, but does not select the real parity test
   `test_external_tool_readiness_payload_matches_real_rednote_readiness`,
   whose name contains `readiness_payload_matches`, not `readiness_payload_parity`.
   This is acceptable because (a) the real parity test is unchanged by this
   stage and (b) the immediately following command runs the full
   `tests/test_first_run_smoke.py -q`, which covers it. If a quick focused
   signal on the real parity test is also desired, broadening the filter to
   `readiness_payload` would do it; not required for correctness.

2. The helper retains `getattr(test_func, "pytestmark", [])` with a `[]`
   default, so the Stage 172 Minor #2 trade-off (a future rename or a passed-in
   function lacking `pytestmark` degrades to a vacuous pass rather than failing
   loudly) carries forward unchanged. The new synthetic test mitigates this for
   the helper itself by always attaching a real mark, and adding an
   is-this-actually-the-function assertion is out of scope for this stage. No
   action required; noted for continuity with the documented Stage 172 position.

## Review Questions

1. Does the plan satisfy the objective: reject both `skipif` and bare `skip`
   marks on the readiness parity test? Yes. `frozenset({"skipif", "skip"})`
   covers both, the meta test delegates to the helper, and the parametrized
   synthetic test asserts detection of a synthetic `skipif` mark and a synthetic
   bare `skip` mark. `xfail` is correctly excluded (it is an expected failure,
   not a skip), and module-level `pytest.importorskip` remains a separate,
   out-of-scope mechanism, consistent with the Stage 172 notes.

2. Is the helper-focused RED/GREEN path meaningful for a test-only hardening
   stage? Yes, and it is a real improvement over Stage 172. In Stage 172 the
   meta test passed vacuously in GREEN (empty `pytestmark`), so its value was
   only "logically sound" as a regression guard. Here, the parametrized
   synthetic test builds a `fake_parity_test` with an actual mark attached and
   asserts the helper returns truthy for both mark kinds, so the helper is
   exercised against non-empty `pytestmark`. The RED (Step 3) is a genuine
   `NameError` while `has_blocking_readiness_parity_skip_mark` is undefined; the
   GREEN (Step 5) is a genuine pass once the helper and meta-test update land.

3. Is the change appropriately limited to `tests/test_first_run_smoke.py`? Yes.
   The only modified source file is `tests/test_first_run_smoke.py`; all other
   listed paths are new spec/plan/review artifacts. No runtime source, smoke
   script, payload shape, command ordering, adapter metadata, readiness
   boundaries, install hints, mirror hints, or dependencies change. The needed
   `Callable` import already exists.

4. Are focused verification commands sufficient before the full release gate?
   Yes. Task 2 Step 1 runs the focused parity/skip-guard subset, then the full
   `tests/test_first_run_smoke.py`, then `ruff check` and `ruff format --check`
   on that file. Because only one test file changes, this is appropriately
   scoped, and the full release gate in Task 3 runs the complete suite plus
   first-run smoke, release hygiene, full ruff, `UV_NO_CONFIG=1 uv lock
   --check`, `git diff --check`, the `ghp_` secret scan, and the GitHub
   extraheader check afterward.

5. Does the plan avoid source acquisition, scraping, platform APIs, dependency
   changes, and compliance-review product behavior? Yes. The change is pure
   pytest mark introspection on test functions. There is no fetch, no
   connector, no browser automation, no platform API, no account/cookie/token
   behavior, no monitoring, no scheduling, no source acquisition, no demand
   proof, no ranking, no coverage verification, no dependency/lockfile change,
   and no compliance-review product behavior. The design's Out-of-scope section
   and the plan's Self-Review Notes both state this explicitly and accurately.

## Verification Assessment

- Current-state confirmation: `tests/test_first_run_smoke.py:1500-1507` holds
  the Stage 172 narrow `all(mark.name != "skipif" for mark in marks)` guard;
  `:1487` defines the real parity function with no skip marks attached; `:9`
  already imports `Callable` from `collections.abc`. These match the design's
  assumptions and make the helper/code insertions import-free.
- RED/GREEN logic: the Step 3 RED claim (the new parametrized test fails while
  `has_blocking_readiness_parity_skip_mark` is undefined) is sound — the name
  is resolved inside the test body at call time, producing a `NameError` per
  parametrized case, not a collection error. The Step 5 GREEN is sound — once
  defined, the helper returns `True` for both synthetic `skipif` and `skip`
  marks, and the meta test passes because the real parity function's
  `pytestmark` is empty.
- Mark semantics: `pytest.mark.skipif(True, reason=...)` and
  `pytest.mark.skip(reason=...)` both yield `MarkDecorator` objects whose
  `.mark` is a `Mark` with `name` equal to `"skipif"` / `"skip"`, so
  `fake_parity_test.pytestmark = [mark_decorator.mark]` is correctly shaped for
  the helper's `mark.name in BLOCKING_READINESS_PARITY_SKIP_MARKS` check.
- Review-gate conformance: Task 2 Step 3 and Task 3 Step 2 invoke
  `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir
  /home/ubuntu/fashion-radar`, matching AGENTS.md, and require review bodies
  starting with `# Stage 186 Code Review` and `# Stage 186 Release Review`.
- Release-gate conformance: Task 3 Step 1 runs the full suite with proxy
  variables unset (addressing the SOCKS-proxy environmental noise documented in
  the Stage 172 release review), `UV_NO_CONFIG=1 uv lock --check` with index
  env unset, the `ghp_` secret scan, and the `http.https://github.com/.extraheader`
  check, matching AGENTS.md and the prior release gate.
- Scope: no runtime module, smoke script, payload, validator, command order,
  adapter metadata, readiness boundary, install hint, mirror hint, dependency,
  or lockfile change is planned.

## Verdict

Approve implementation. The plan satisfies the Stage 186 objective, gives a
test-only stage a genuine non-vacuous RED/GREEN path, stays limited to
`tests/test_first_run_smoke.py`, uses sufficient focused verification before
the full release gate, and avoids source acquisition, scraping, platform APIs,
dependency changes, and compliance-review product behavior. No critical or
important findings. Proceed with Task 1 implementation, then code review and
release gate per the plan.
