# Stage 172 Code Review

Objective:

Make the first-run smoke readiness parity test fail loudly if
`fashion_radar.external_tool_readiness` is missing or broken, instead of
silently skipping behind a stale Stage 66 fallback.

## Summary

The Stage 172 implementation is a clean, minimal, test-only hardening of
`tests/test_first_run_smoke.py`. It replaces the stale
`try/except ModuleNotFoundError` optional import with a direct
`from fashion_radar.external_tool_readiness import build_external_tool_readiness`
that is alphabetically ordered alongside the other `fashion_radar.*` builder
imports, removes the `@pytest.mark.skipif(build_external_tool_readiness is None, ...)`
decorator and the now-dead `assert build_external_tool_readiness is not None`
line from the parity test body, and adds a focused RED meta test that guards
against reintroducing a `skipif` mark on the readiness parity function.

The change is boundary-compliant and brings this test file into import
consistency with every neighboring builder
(`community_handoff_workflow`, `external_tool_adapters`,
`external_tool_templates`, `external_tool_workflow`, `imported_review_workflow`),
all of which were already direct imports, and with
`tests/test_external_tool_contract_parity.py` and
`tests/test_external_tool_readiness.py`, which already import
`build_external_tool_readiness` directly. The
`src/fashion_radar/external_tool_readiness.py` module is untouched, so its
documented local read-only / `shutil.which`-only boundary is preserved exactly,
and the parity test's `which=lambda command: None` injection (unchanged) still
produces the deterministic `path: None` / `status: "missing"` payload.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The meta test's mark-name coverage is intentionally narrow. It asserts no
   mark named `skipif` is attached to
   `test_external_tool_readiness_payload_matches_real_rednote_readiness`. It
   will not catch an unconditional `@pytest.mark.skip`, a module-level
   `pytest.importorskip(...)`, or a bare `skip` mark on the same function. This
   is the documented, intentional trade-off stated in the stage design and the
   plan review: the guard targets the historically stale `skipif` pattern only
   and deliberately avoids banning legitimate platform-specific skips
   elsewhere. Acceptable as written; a future broader guard
   (`not any(mark.name in {"skipif", "skip"} for mark in marks)`) would be a
   separate, explicitly out-of-scope follow-up.

2. The meta test couples to the parity function's module-level bare name via
   `getattr(test_external_tool_readiness_payload_matches_real_rednote_readiness,
   "pytestmark", [])`. This is standard pytest introspection and is robust for
   the current layout where the parity test is defined immediately above the
   meta test. If the parity function is ever renamed, the meta test must be
   updated in lockstep; this is ordinary refactoring hygiene, not a defect. The
   `getattr(..., [], [])` default also means a rename would silently degrade
   the guard into a vacuous pass rather than fail loudly, so a future
   hardening could assert the resolved attribute is the function object first.

3. With the `skipif` decorator removed, the parity function's `pytestmark` is
   empty, so the meta test's `all(mark.name != "skipif" for mark in marks)` is
   vacuously `True`. This is correct and is the intended GREEN state, but it
   means the meta test's value is purely as a regression guard going forward;
   it no longer exercises a non-empty `pytestmark`. The RED evidence (failure
   while the decorator was still present) is logically sound — a `skipif` mark
   would populate `pytestmark` with a `Mark(name="skipif", ...)` and flip the
   assertion — so the guard is meaningful even though it now passes vacuously.

## Verification Assessment

- `uv --no-config run --frozen pytest
  tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped
  tests/test_first_run_smoke.py::test_external_tool_readiness_payload_matches_real_rednote_readiness
  -q` reproduced the claimed GREEN: 2 passed.
- `uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q`
  reproduced the claimed result: 19 passed.
- `uv --no-config run --frozen ruff check tests/test_first_run_smoke.py`:
  All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py`:
  1 file already formatted.
- The claimed RED is logically sound and consistent with the final GREEN state:
   while the `@pytest.mark.skipif(...)` decorator was present, the parity
   function's `pytestmark` carried a `skipif` mark, which would make
   `all(mark.name != "skipif" ...)` fail; after removal the list is empty and
   the assertion passes.
- Scope check: `git status` and `git diff HEAD -- tests/test_first_run_smoke.py`
  confirm the only tracked change is the test file, and the diff is limited to
  the direct import addition, the optional-import/`skipif`/redundant-assertion
   removal, and the new meta test. All other listed paths are untracked review
  artifacts. No runtime source, smoke script, payload shape, command ordering,
  adapter metadata, readiness boundaries, install hints, or mirror hints
  changed. No connectors, scraping, browser automation, platform APIs,
  login/cookie/token behavior, monitoring, scheduling, source acquisition,
  demand proof, ranking, coverage verification, or compliance-review behavior
  was introduced.

## Verdict

Approve. The implementation meets the Stage 172 objective: the first-run smoke
readiness parity test now fails loudly at collection/import time if
`fashion_radar.external_tool_readiness` is missing or broken, instead of
silently skipping behind the stale Stage 66 fallback. The direct import is
appropriate and consistent with the rest of the file and codebase now that the
module is implemented and tested. The meta test is meaningful, correctly scoped
to the stale readiness `skipif`, and acts as a regression guard. No critical or
important findings. No out-of-scope runtime, payload, adapter, smoke-script, or
boundary behavior changed. The stage is clear for release verification.
