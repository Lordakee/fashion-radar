# Stage 172 Release Review

Objective:

Confirm that Stage 172 is ready to commit, push, and close.

## Summary

Stage 172 is a tightly scoped, test-only hardening of
`tests/test_first_run_smoke.py`. It removes a stale Stage 66-era
`try/except ModuleNotFoundError` optional import and the companion
`@pytest.mark.skipif(build_external_tool_readiness is None, ...)` decorator
plus the now-dead `assert build_external_tool_readiness is not None` line from
the readiness parity test, replaces them with a direct, alphabetically ordered
`from fashion_radar.external_tool_readiness import build_external_tool_readiness`,
and adds a focused RED meta test
(`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`)
that guards against reintroducing a `skipif` mark on the parity function.

The working-tree change is limited to a single tracked file
(`tests/test_first_run_smoke.py`); every other listed path is an untracked
review/spec/plan artifact. `git diff HEAD -- tests/test_first_run_smoke.py`
shows exactly the import addition, the optional-import/skipif/assertion
removal, and the new meta test — nothing more. The runtime module
`src/fashion_radar/external_tool_readiness.py` and the
`scripts/check_first_run_smoke.py` smoke script are byte-for-byte unchanged
(zero diff lines), so the documented local read-only / `shutil.which`-only
readiness boundary, the `external_tool_readiness` payload shape, command
ordering, adapter metadata, readiness boundaries, install hints, and mirror
hints are all preserved exactly.

The change brings `tests/test_first_run_smoke.py` into import consistency with
its other direct builder imports (`community_handoff_workflow`,
`external_tool_adapters`, `external_tool_templates`, `external_tool_workflow`,
`imported_review_workflow`) and with `tests/test_external_tool_contract_parity.py`
and `tests/test_external_tool_readiness.py`, which already import
`build_external_tool_readiness` directly. With the module long-landed (Stage
66), failing loudly at collection/import time on regression is the correct,
consistent behavior, and it eliminates the silent-skip masking risk the stage
targets.

Both prior reviews (`opencode-stage-172-plan-review.md`,
`opencode-stage-172-code-review.md`) returned Approve with no critical and no
important findings.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The new meta test's mark-name coverage is intentionally narrow: it asserts
   no mark named `skipif` is attached to the parity function. It will not
   catch an unconditional `@pytest.mark.skip`, a `pytest.importorskip(...)`,
   or a bare `skip` mark on the same function. This is the documented,
   deliberate trade-off stated in the design, plan review, and code review:
   the guard targets the historically stale `skipif` pattern only and
   deliberately avoids banning legitimate platform-specific skips elsewhere.
   A broader future guard
   (`not any(mark.name in {"skipif", "skip"} for mark in marks)`) is explicitly
   out of scope for this stage. No action required for release.

2. The meta test couples to the parity function's module-level bare name via
   `getattr(test_external_tool_readiness_payload_matches_real_rednote_readiness,
   "pytestmark", [])`. If the parity function is ever renamed, the meta test
   must be updated in lockstep; otherwise the `[]` default would silently
   degrade the guard into a vacuous pass rather than fail loudly. Standard
   pytest introspection, ordinary refactoring hygiene, not a release blocker.

3. In the GREEN state the parity function's `pytestmark` is empty, so the
   meta test's `all(mark.name != "skipif" for mark in marks)` passes
   vacuously. This is the intended post-fix state; the guard's value is now
   purely as a regression guard going forward. The RED evidence (failure
   while the `skipif` decorator was present) is logically sound — a
   `Mark(name="skipif", ...)` would populate `pytestmark` and flip the
   assertion — so the meta test remains meaningful despite the vacuous GREEN.

## Verification Assessment

All claimed evidence was independently reproduced as part of this release
review. Focused and full-gate verification confirm the stage:

- Focused parity tests
  (`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`
   and `test_external_tool_readiness_payload_matches_real_rednote_readiness`):
  2 passed, reproducing the claimed GREEN. The claimed RED is logically sound
  and consistent with the final GREEN state: while the
  `@pytest.mark.skipif(...)` decorator was present, the parity function's
  `pytestmark` carried a `skipif` mark, which would make
  `all(mark.name != "skipif" ...)` fail.
- `tests/test_external_tool_readiness.py`: 19 passed.
- Full suite (`pytest -q`): `1368 passed`. Note: when the suite is run in a
  shell that exports a SOCKS proxy via `ALL_PROXY`/`HTTPS_PROXY` (and
  `socksio` is not installed), four unrelated collector/workflow tests fail
  with `ImportError: Using SOCKS proxy, but the 'socksio' package is not
  installed.`. Re-running the same suite with the proxy environment
  variables unset reproduces exactly `1368 passed`, and the four tests in
  isolation (`tests/test_collectors_runner.py tests/test_workflows.py`) pass
  10/10 without proxy. These four failures are therefore purely
  environmental (this shell's SOCKS proxy configuration), are confined to
  test files untouched by Stage 172, and do not reflect any defect in the
  stage. The "1368 passed" release-evidence claim is accurate and
  reproducible in a proxy-free environment.
- `scripts/check_first_run_smoke.py --repo-root .`: First-run sample smoke
  passed.
- `scripts/check_release_hygiene.py --repo-root .`: Release hygiene checks
  passed.
- `ruff check .`: All checks passed.
- `ruff format --check .`: 144 files already formatted.
- `UV_NO_CONFIG=1 uv lock --check` (with `UV_DEFAULT_INDEX`/`UV_INDEX_URL`/
  `UV_EXTRA_INDEX_URL` unset): Resolved 84 packages; no lockfile churn and no
  mirror-bound URLs introduced.
- `git diff --check`: no whitespace/errors output, exit 0.
- Secret scan `rg -n 'ghp_[A-Za-z0-9]+' .`: no matches (rg exit 1, zero
  result lines).
- `git config --get-all http.https://github.com/.extraheader`: no
  token-bearing header configured (key absent).

Scope confirmation: `git status` shows exactly one modified tracked file
(`tests/test_first_run_smoke.py`) and the expected untracked review/spec/plan
artifacts. `git diff HEAD -- src/fashion_radar/external_tool_readiness.py`
and `git diff HEAD -- scripts/check_first_run_smoke.py` both show zero changed
lines, confirming the runtime readiness module and the first-run smoke script
are untouched. No connectors, scraping, browser automation, platform APIs,
login/cookie/token behavior, monitoring, scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance-review behavior
was introduced. No JSON payload shapes, validators, command ordering, adapter
metadata, readiness boundaries, install hints, or mirror hints changed.

Review-history consistency: both `opencode-stage-172-plan-review.md` and
`opencode-stage-172-code-review.md` are present, complete (no stubs, tool
status, or truncation), and report no critical and no important findings,
matching `docs/REVIEW_PROTOCOL.md` staged workflow.

## Verdict

Approve. Stage 172 is in scope, boundary-compliant, and ready to commit,
push, and close.

1. In scope and ready to commit: yes — test-hygiene only, single tracked test
   file, runtime/smoke/payload behavior unchanged.
2. Plan/code review artifacts clean and consistent with `REVIEW_PROTOCOL.md`:
   yes — both present, complete, and free of critical/important findings.
3. Release verification evidence sufficient: yes — focused RED/GREEN, module
   tests, full 1368-passed gate (proxy-free), first-run smoke, release
   hygiene, ruff, lockfile, whitespace, and secret scans all reproduced.
4. Out-of-scope behavior, generated artifact, lockfile mirror churn, secret,
   token, or local private data in the working tree: none detected.
5. Critical or important findings before commit and push: none.
