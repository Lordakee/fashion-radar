# Stage 148 Plan Review

I reviewed the spec (`docs/superpowers/specs/2026-06-22-stage-148-readiness-detail-exactness-design.md`), the plan (`docs/superpowers/plans/2026-06-22-stage-148-readiness-detail-exactness-plan.md`), and the three source files against the current tree (HEAD = `5fc8053`).

## Findings

**[Info - no action] RED tests are true REDs; GREENs hold.**

- Detail drift test (`plan` Task 2 / `spec` lines 124-132): current validator only guards non-empty string (`scripts/check_first_run_smoke.py:1689-1691`), so the `curl ... | sh` detail passes through and fails with `DID NOT RAISE`. Post-implementation, `assert_equal` emits `"{command_name} check detail expected ..."`, which contains `"detail"`, satisfying `match="detail"`.
- Boundary drift, appended case (`spec` lines 143-148): appended `"May install npm dependencies..."` preserves all required boundary phrases and adds no forbidden phrase, so it is currently not rejected. Post-implementation, the 12-item list differs from the 11-item pinned tuple and raises `"boundaries"`.
- Boundary drift, collapsed case (`spec` lines 149-163): the single concatenated string contains every required phrase and none of the forbidden substrings, so it currently passes. Post-implementation, the 1-item list differs from the 11-item pinned tuple and raises `"boundaries"`.
- The `missing_detail`, `missing_hint`, and `missing_boundary` sub-checks still raise their guard messages first, so `match="detail"`, `"install_hint"`, and `"boundaries"` keep matching.

**[Info - no action] Pinned constants match runtime and fixture exactly.**

- `EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL` matches runtime `_UPSTREAM_COMMAND_SPECS["rednote_mcp"]["detail"]` and the first-run fixture byte-for-byte.
- `EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES` matches `EXTERNAL_TOOL_READINESS_BOUNDARIES` and the first-run fixture, including the long "No platform collection..." item and final `"Does not provide a compliance-review product feature."`.
- The existing parity test keeps the runtime builder and fixture aligned.

**[Info - no action] Runtime behavior unchanged.**

The scope limits edits to `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and review artifacts. `src/fashion_radar/external_tool_readiness.py` remains untouched.

The two old readiness constants are referenced only inside `validate_external_tool_readiness()`, and the joined-text pre-checks are subsumed by exact equality, so removing them is safe.

**[Info - no action] `forbidden scope` to `boundaries` regression update is required and correct.**

The existing appended-boundary regression now fails through the exact-equality path, whose message is labeled `boundaries`. Updating the test expectation to `match="boundaries"` preserves regression coverage while matching the new failure path.

**[Info - no action] Focused verification is sufficient.**

The focused gate runs the readiness slice, the full first-run smoke test file, ruff check and format on both changed files, and `git diff --check`. The release gate then runs the full suite, ruff, lockfile check, token scan, and persistent-auth check.

**[Low - suggestion] Commit message should include boundaries.**

The original plan suggested `"Pin readiness detail validation"`, but this stage also pins boundary validation. Prefer `"Pin readiness detail and boundary validation"`.

**[Low - process] Detail RED test was already in the working tree before the final plan review.**

This is not a plan defect, but the boundary drift RED test still needs to land so the boundary half also has explicit RED-to-GREEN evidence.

## Verdict

No blocking issues. The RED tests fail now and pass under exact equality, the pinned strings and lists match the runtime builder and first-run fixture verbatim, runtime is untouched, the `boundaries` assertion update is mandatory and correctly placed, and verification is sufficient.
