# Stage 142 Code Review

## Findings

### No blocking findings.

## Post-Review Reconciliation

- **Plan/design constant naming synchronized.** The Stage 142 design, plan, and
  plan-review artifacts now describe
  `EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT`, matching the implementation at
  `scripts/check_first_run_smoke.py:100`.

- **RED test payload synchronized.** The Stage 142 design and plan now show the
  same drift payload implemented at `tests/test_first_run_smoke.py:2700-2702`.
  The payload preserves both substrings accepted by the old validator while
  expressing the registry guidance incorrectly, proving the old substring check
  was too loose without documenting a valid extra shell pipeline.

## Verification (performed fresh)

- **RED proof.** Stashed `scripts/check_first_run_smoke.py`, ran the new test
  against the old substring validator: `Failed: DID NOT RAISE ... SmokeError`.
  The drifted hint was accepted, confirming the old check was loose.
- **GREEN proof.** Restored the implementation, ran the same test: `1 passed`.
  Exact equality via `assert_equal(...)` at
  `scripts/check_first_run_smoke.py:1480-1484` rejects the drift with an
  `install_hint`-labeled `SmokeError`.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness"`
  -> 12 passed.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q` -> 91
  passed.
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  -> All checks passed.
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
  -> 2 files already formatted.
- `git diff --check` -> clean.

## Requirement Check

- **Rejects Rednote MCP install-hint shell-text drift.** Yes.
  `validate_external_tool_readiness()` now uses `assert_equal` against
  `EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT`
  (`scripts/check_first_run_smoke.py:1480-1484`). The population guard
  (`scripts/check_first_run_smoke.py:1477-1479`) still fires first for
  empty/non-string hints, preserving the existing `missing_hint` test at
  `tests/test_first_run_smoke.py:2660-2665`.

- **Runtime builder/output unchanged.** Confirmed. No `src/` files are
  modified; the diff is confined to the smoke checker and its test. The
  expected string is byte-identical to the runtime source of truth at
  `src/fashion_radar/external_tool_readiness.py:47` and the fixture at
  `tests/test_first_run_smoke.py:1167-1170`, so
  `test_external_tool_readiness_payload_matches_real_rednote_readiness`
  (`tests/test_first_run_smoke.py:1348`) continues to lock fixture vs runtime
  parity.

- **RED/GREEN proves substring drift acceptance and exact rejection.** Yes, as
  demonstrated above.

## Verdict

**Proceed to release gate and commit.** The Stage 142 implementation meets all
three requirements: install-hint drift is rejected by exact equality, runtime
builder/output behavior is untouched, and RED/GREEN was demonstrated against
both the old substring validator and the new exact equality validator. The two
informational observations are cosmetic naming/payload choices that are equal
to or stronger than the plan, and do not block release.
