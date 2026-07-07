I'll provide a comprehensive review of the Stage 329 plan in the requested format.

## Critical

**Bind probe race condition**: The `_can_bind()` implementation at plan lines 357-365 uses `SO_REUSEADDR` which can give false positives. If another process is already bound to the port with `SO_REUSEADDR`, this bind test will succeed even though the port is actually occupied. This could misclassify `port_in_use` as `not_running`.

**Recommendation**: Add exception handling around the bind attempt and consider the bind test as a heuristic only. Document that `port_in_use` vs `not_running` distinction is best-effort.

## Important

**Missing directory handling**: The plan doesn't specify behavior when `--unit-dir` doesn't exist. Line 369 in `_systemd_payload()` calls `(unit_dir / unit).is_file()` which will work, but the overall design should clarify whether missing unit directories are equivalent to "all units missing" or should emit a different status.

**Recommendation**: Explicitly handle missing unit directory case in tests and implementation. Consider adding a note in the status payload when the unit directory doesn't exist.

**Datetime parsing duplication**: The plan shows datetime parsing logic in both `_parse_row_one_ops_check_as_of()` (cli.py, lines 541-551) and `_parse_datetime()` (ops_check.py, lines 305-315). These implementations should be unified or explicitly use an existing utility.

**Recommendation**: Use the existing `parse_datetime_utc` from `fashion_radar.utils.dates` which is already imported in cli.py, or document why a different implementation is needed.

**Missing error handling test**: The CLI tests don't include a test for malformed `--as-of` input to verify the `BadParameter` exception handling works correctly.

**Recommendation**: Add a test case `test_row_one_ops_check_rejects_malformed_as_of()` to Task 2.

## Medium

**Probe injection verification**: While the plan shows injectable probe functions for deterministic tests, there's no explicit test verifying that the probe function is actually called and used correctly by `build_row_one_ops_check_payload()`.

**Recommendation**: Add an assertion in tests that verifies the probe was called with expected host/port/timeout values.

**IPv6 handling untested**: The `_can_bind()` implementation includes IPv6 logic (line 359: `family = socket.AF_INET6if ":" in host`), but no tests cover IPv6 addresses.

**Recommendation**: Either add a test for IPv6 or document that IPv6 is untested in this stage and may need future work.

**Exception safety in bind probe**: The `_can_bind()` function could raise exceptions beyond `OSError` during socket operations (e.g., `socket.gaierror` for invalid addresses). The exception handling should be comprehensive.

**Recommendation**: Wrap the entire `_can_bind()` body in a try-except that catches all exceptions and returns False for any error.

**Helper availability**: Plan line 516-518 mentions that `_write_minimal_row_one_site` helper may not exist in test files but doesn't provide the fallback implementation.

**Recommendation**: Either verify the helper exists or include its implementation in the plan.

## Minor

**Server probe detail field**: The `RowOneServerProbeResult.detail` field could potentially leak internal network information in error messages. While this is a local-only command, the JSON output might be shared.

**Recommendation**: Review exception messages in the probe implementation to ensure they don't include sensitive network details. Current implementation looks safe but should be noted in docs.

**Hard-coded timeout**: The plan uses `ROW_ONE_SERVER_TIMEOUT_SECONDS = 1.0` as a constant (line 220) with no option to override it. For slow local environments, this might be too short.

**Recommendation**: Consider making timeout configurable via CLI option or environment variable in a future iteration. Document the current1-second timeout.

**Missing runtime.json validation**: While the plan tests site files presence, it doesn't validate that runtime.json can be parsed before attempting to read it in the pure tests.

**Recommendation**: The helper `_write_site()` at test line 68-86 correctly writes valid JSON, but add a comment noting this is intentional test data.

**Actions array ordering**: The `_actions()` helper (lines 388-410) builds an actions list, but the test assertions check for substring presence rather than exact action messages. This could mask ordering issues.

**Recommendation**: Current approach is acceptable for flexibility, but document that action ordering is not guaranteed.

## Verdict

**APPROVE WITH CONDITIONS**

This plan is well-structured, follows TDD rigorously, and stays safely within the read-only diagnostic boundaries. The approach is sound and feasible.

**Must fix before implementation**:
1. Add exception handling around `_can_bind()` to handle all socket errors safely
2. Add test for malformed `--as-of` input
3. Unify datetime parsing or explicitly document why duplication is needed
4. Clarify unit-dir missing directory behavior

**Should address**:
5. Add IPv6 test or document limitation
6. Verify probe injection in tests

The core design is solid. The stdlib-only HTTP/bind probes are appropriately scoped and safe. The injectable probe pattern enables deterministic testing. The workflow sentinels correctly prevent contract drift. After addressing the critical bind exception handling and the important items, this plan is ready for implementation.
