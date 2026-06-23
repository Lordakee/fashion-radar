# Stage 172 Plan Review

Objective: Make the first-run smoke readiness parity test fail loudly if
`fashion_radar.external_tool_readiness` is missing or broken, instead of
silently skipping behind a stale Stage 66 fallback.

## Summary

The plan is a focused, test-only hardening of `tests/test_first_run_smoke.py`.
It removes a stale optional-import fallback and `@pytest.mark.skipif` decorator
that predate the now-landed Stage 66 `external_tool_readiness` module, and adds
a RED meta test to prove and guard the removal. The change set is minimal (one
test file plus review artifacts), respects every project boundary rule, and
brings the readiness parity test into consistency with the other direct-import
parity tests already present in the same file. No runtime source, payload
shapes, command ordering, adapter metadata, readiness boundaries, or install
hints change. The plan follows the staged TDD and review-gated workflow defined
in `AGENTS.md` and `docs/REVIEW_PROTOCOL.md`.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Meta test mark-name coverage is intentionally narrow. The guard asserts no
   mark named `skipif` is attached to the parity function. It will not catch an
   unconditional `@pytest.mark.skip`, a `pytest.importorskip(...)`, or a `skip`
   mark on the same function. The design document explicitly scopes this to the
   historically stale `skipif` pattern and states it should not ban
   platform-specific skips elsewhere, so this is an acceptable, documented
   trade-off rather than a defect. If broader coverage is ever wanted, a
   follow-up could assert `not any(mark.name in {"skipif", "skip"} for mark in
   marks)`, but that is out of scope for this stage.

2. Meta test couples to the parity function's module-level name. The guard
   references `test_external_tool_readiness_payload_matches_real_rednote_readiness`
   by bare name and relies on `getattr(..., "pytestmark", [])`. This is
   standard and robust as long as the two functions stay in the same module and
   the parity test is defined first (which the plan specifies, and which yields
   an empty `pytestmark` after removal so `all(...)` is vacuously true). If the
   parity test is ever renamed, the meta test must be updated in lockstep; this
   is ordinary refactoring hygiene, not a blocker.

3. The `try/except ModuleNotFoundError` block is the only such fallback
   remaining in `tests/test_first_run_smoke.py`; every neighboring builder
   (`external_tool_adapters`, `external_tool_templates`,
   `external_tool_workflow`, `community_handoff_workflow`,
   `imported_review_workflow`) is already a direct import. Removing this single
   fallback completes the file's import consistency, which is a small positive
   side effect worth confirming during the code review rather than something
   the plan must call out.

## Plan Assessment

1. Appropriately scoped and safe: yes. The stage touches one test module plus
   review artifacts only. It explicitly excludes runtime source, the first-run
   smoke script, payload shapes, validators, command ordering, adapter metadata,
   readiness boundaries, install hints, and mirror hints. The TDD ordering (add
   the RED meta test, confirm it fails, replace the optional import with a
   direct import, remove the stale decorator and redundant
   `assert ... is not None`, then confirm GREEN) is sound and matches the
   design's implementation method. The parity test body still calls
   `build_external_tool_readiness(...)` directly, so removing the dead `None`
   assertion is safe.

2. Project boundary compliance: yes. This is pure test hygiene. It adds no
   connectors, scraping, browser automation, platform APIs, login/cookie/token
   behavior, monitoring, scheduling, source acquisition, demand proof, ranking,
   coverage verification, or compliance-review behavior.
   `src/fashion_radar/external_tool_readiness.py` is unchanged, so its
   documented local read-only / `shutil.which`-only boundary is preserved
   exactly.

3. Meta test usefulness: yes. The meta test is a useful RED guard for this
   specific stale-skip removal: it fails deterministically while the `skipif`
   mark is present, passes once it is removed, and then continues to act as a
   regression guard against reintroducing a conditional skip on that parity
   test. Its narrowness is documented and acceptable.

4. Failing at import/collection time: yes, appropriate.
   `external_tool_readiness` landed in Stage 66 and is a normal hard dependency
   of the first-run smoke contract, on equal footing with the other builders
   this file already imports directly. If the module is deleted or stops
   importing, a silent skip would mask real breakage of the first-run smoke
   contract. Failing at collection time is the correct, consistent behavior, and
   it matches how the rest of the file already treats its imports.

5. Planning findings: no critical or important planning findings. The focused
   verification commands, full release gate, secret scan, lockfile validation
   (`UV_NO_CONFIG=1 uv lock --check`), and review/commit/push flow all follow
   the `AGENTS.md` and `REVIEW_PROTOCOL.md` discipline.

## Verdict

Approve. The Stage 172 plan is correctly scoped, boundary-compliant, and safe
to implement as written. Proceed with Task 1 (add the RED meta test and confirm
it fails), then Task 2 (direct import plus stale-skip and redundant-assertion
removal, then confirm GREEN), then the Task 3 code review, full release gate,
release review, commit, and push.
