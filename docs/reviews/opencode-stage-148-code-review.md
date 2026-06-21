# Stage 148 Code Review

## Findings

**No blocking issues.** All review criteria are satisfied.

**1. RED tests are genuine (verified empirically).** I reverted only `scripts/check_first_run_smoke.py` to the base commit and reran the new tests - all 3 fail with `Failed: DID NOT RAISE`, then pass on the head tree:
- `test_validate_external_tool_readiness_rejects_detail_extra_shell_text` - `tests/test_first_run_smoke.py:2909`. Old validator only rejected empty/non-string detail, so the populated `curl ... | sh` drift passed.
- `test_validate_external_tool_readiness_rejects_boundary_drift[boundaries0]` (appended item) and `[boundaries1]` (collapsed single string) - `tests/test_first_run_smoke.py:2921`. Old joined-text phrase scan could not detect either drift; the collapsed case also dodged the old forbidden-phrase list because it contains `no source acquisition`/`no platform apis` rather than the forbidden `runs source acquisition`/`opens platform apis`.

**2. Exact detail equality is in place.** `scripts/check_first_run_smoke.py:1687-1691` now calls `assert_equal(...)` against `EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL` (`scripts/check_first_run_smoke.py:108-110`), which matches the runtime spec at `src/fashion_radar/external_tool_readiness.py:49` exactly. The prior non-empty guard is retained so missing/non-string detail still raises the clearer `"... must be populated"` message before the equality check.

**3. Exact boundary equality is in place.** `scripts/check_first_run_smoke.py:1888-1892` replaces the old phrase/blacklist scan with `assert_equal(...)` against `list(EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES)` (`scripts/check_first_run_smoke.py:292-309`). I diffed this tuple against `EXTERNAL_TOOL_READINESS_BOUNDARIES` at `src/fashion_radar/external_tool_readiness.py:24-41` - all 11 items match byte-for-byte. The dead `REQUIRED_EXTERNAL_TOOL_READINESS_BOUNDARY_PHRASES` / `FORBIDDEN_EXTERNAL_TOOL_READINESS_SCOPE_PHRASES` constants were removed with no dangling references (only the plan doc mentions them as a removal instruction).

**4. Existing regression matches the new failure path.** `tests/test_first_run_smoke.py:2888` now expects `match="boundaries"`, which aligns with the `assert_equal` label `external-tool-readiness boundaries` raised for both the appended acquisition string and the `["local read-only"]` replacement case at `tests/test_first_run_smoke.py:2893`.

**5. Runtime behavior unchanged.** `src/fashion_radar/external_tool_readiness.py` is unmodified; only the smoke validator and its tests changed. The pinned constants are intentionally independent of the runtime builder, so first-run smoke will catch future runtime drift rather than inheriting it.

**6. Verification coverage is sufficient.**
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q` - 108 passed.
- `ruff check` + `ruff format --check` on both files - clean.
- `git diff --check` - clean.
- The release-gate block in the design/plan covers full suite, ruff, lockfile, and secret/auth-header sweeps.

### Minor observations

- The parametrized boundary-drift test calls `external_tool_readiness_payload()["boundaries"]` at collection time. This is safe because the helper returns a fresh dict and case 0 spreads into a new list, but a future reader may want a comment noting no aliasing occurs.
