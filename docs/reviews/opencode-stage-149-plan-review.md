# Stage 149 Plan Review

## Findings

**No blocking issues.** The plan is sound and ready to implement.

### Detailed Assessment

**1. RED tests would correctly fail before and pass after.**

The current validator only checks whether each expected field is not `None` or `""`, so any populated-but-drifted value is accepted:

- Title drift mutates `items[0]["title"]` and is currently accepted, producing `DID NOT RAISE` before implementation.
- Source-weight drift mutates `items[1]["source_weight"] = 4.5` and is currently accepted, producing `DID NOT RAISE` before implementation.

After adding exact row equality, dict inequality raises `SmokeError` with labels `external-tool-template row 1 item` and `external-tool-template row 2 item`, which match the planned pytest regexes.

**2. Pinned values match runtime builder and fixture.**

`EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS` matches:

- runtime `_template_items()` in `src/fashion_radar/external_tool_templates.py`
- fixture `external_tool_template_payload()` in `tests/test_first_run_smoke.py`

The existing `test_external_tool_template_payload_matches_real_rednote_template` already asserts fixture output equals the runtime builder for Rednote.

**3. Existing targeted errors remain intact.**

The planned `assert_equal(... row {index} item ...)` is inserted after the current structural checks and platform assertion. This preserves existing labels and failure paths:

- missing field: `row N <field> is required`
- private/raw field: `private/raw field`
- extra field: `has unexpected field`
- wrong platform: `row N platform`

**4. Runtime behavior unchanged.**

The scope is limited to `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and review artifacts. `src/fashion_radar/external_tool_templates.py` remains unchanged.

**5. Focused verification is sufficient.**

The focused verification covers the external template slice, the full first-run smoke file, ruff, format, and `git diff --check`. The release gate adds full pytest, repo-wide ruff, lockfile check, and secret/auth-header checks.

### Non-Blocking Observation

The pinned constant becomes a third independent copy of the Rednote example data alongside the runtime builder and the test fixture. This is intentional for first-run smoke: the validator should catch drift instead of inheriting it.

## Verdict

Proceed to implementation.
