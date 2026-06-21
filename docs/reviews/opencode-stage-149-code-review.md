# Stage 149 Code Review

## Findings

**No blocking issues.** The implementation is correct, minimal, well-scoped, and the TDD claims are verified.

### Verification Performed

- True RED proven empirically: stashed `scripts/check_first_run_smoke.py` and ran both new tests against the old validator. Both failed with `DID NOT RAISE`; restored implementation and both passed.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q` - 110 passed.
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py` - clean.
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py` - clean.
- `git diff --check` - clean.
- Pinned item values were cross-checked against runtime adapter metadata and `DEFAULT_ADAPTER_AS_OF`, including the `2026-06-13T12:00:00+00:00` ISO timestamp conversion.

### Review Questions

**1. New tests prove prior gaps with true RED cases.**

`tests/test_first_run_smoke.py` now covers a populated title drift and a populated `source_weight` drift. The old validator only checked non-empty fields, so both bypassed it. This was verified by running the tests against the old validator and seeing `DID NOT RAISE`.

**2. Exact item equality is placed after structural checks.**

`validate_external_tool_template()` now compares each item to `EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS[index - 1]` after the existing envelope, field, private/raw, unexpected-field, populated-field, and platform checks. Pinning covers row order, URL, title, `published_at`, summary, source name, platform, numeric source weight, and `collected_at`.

**3. Existing targeted structural errors remain intact.**

The implementation is additive and does not change the existing structural branches. The existing external template slice still passes, including wrong-platform, missing-field, private-field, and raw-field checks.

**4. Runtime behavior unchanged.**

No `src/` files changed. Only `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and Stage 149 docs/review artifacts are in scope.

**5. Pinned values match runtime builder and fixture.**

`EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS` is byte-identical to `external_tool_template_payload()["items"]`, and the fixture remains pinned to the real runtime builder by `test_external_tool_template_payload_matches_real_rednote_template`.

**6. Verification coverage is sufficient.**

Focused tests, full first-run smoke file, ruff, format, and whitespace checks are clean. The planned release gate covers full pytest, repo-wide ruff, lockfile check, and secret/auth-header scans.

### Non-Blocking Notes

- `EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS[index - 1]` relies on the earlier exact two-row guard. This is acceptable for the current first-run fixture contract.
- Item equality failures include full dict reprs. Verbose, but useful for diagnosis.

## Verdict

Stage 149 is ready for release gate, commit, push, and CI polling.
