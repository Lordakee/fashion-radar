# Stage 142 Plan Review

## Findings

### No blocking issues.

## Info Observations

- **Expected install hint matches runtime exactly.** The design and plan specify `npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp`, which is byte-identical to the runtime builder source of truth in `src/fashion_radar/external_tool_readiness.py` and the existing test fixture in `tests/test_first_run_smoke.py`.

- **RED test is genuinely RED before implementation.** The planned drift payload preserves both currently required substrings while reversing the registry guidance in prose. The current substring loop accepts that payload and raises no `SmokeError`, so the `pytest.raises(..., match="install_hint")` assertion fails before implementation.

- **GREEN behavior is correct after exact equality.** Replacing the substring loop with `assert_equal(f"{command_name} check install_hint", install_hint, EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT)` raises a `SmokeError` with an `install_hint` label for drifted shell text.

- **Existing `missing_hint` test remains valid.** The existing test that sets `install_hint = "npm install rednote-mcp"` continues to raise an `install_hint`-labeled error after exact equality.

- **Runtime behavior remains unchanged.** Scope is limited to `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and stage artifacts. The CLI builder output is untouched.

- **Focused verification is sufficient.** The plan runs targeted readiness tests, the full first-run smoke test module, ruff check/format on touched code files, and `git diff --check`; the release gate then runs the full suite and repository checks.

## Verdict

**Proceed to implementation.** The exact expected install hint matches runtime output and the fixture, the RED test fails before and passes after exact equality, the population guard and existing drift tests continue to hold, runtime output is untouched, and the verification plan is adequate.
