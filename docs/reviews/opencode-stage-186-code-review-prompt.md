# Stage 186 Code Review

Review only the Stage 186 changes:

- `tests/test_first_run_smoke.py`

Context:
- Stage 186 broadens the first-run external-tool readiness parity meta guard.
- Before this stage, the meta test rejected only `pytest.mark.skipif`.
- The new helper rejects both `skipif` and bare `skip` marks attached to
  `test_external_tool_readiness_payload_matches_real_rednote_readiness`.
- A synthetic parametrized test proves both mark kinds are detected.
- No runtime files were changed.

Verified commands already run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "readiness_payload_parity or skip_guard"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
git diff --check
```

Observed results:
- RED: new helper-focused test failed with `NameError` before the helper was
  defined.
- GREEN targeted tests: 3 passed.
- Focused subset: 3 passed, 163 deselected.
- Full `tests/test_first_run_smoke.py`: 166 passed.
- Ruff check and format check passed.
- `git diff --check` passed.

Review questions:

1. Does the helper and synthetic test meaningfully close the Stage 172 `skip`
   follow-up gap?
2. Does the existing readiness parity meta test now reject both `skipif` and
   bare `skip` marks?
3. Is the change appropriately test-only and limited to
   `tests/test_first_run_smoke.py`?
4. Is the helper placement/naming acceptable for this test module?

Report Critical / Important / Minor findings and a short verdict.

Start the body with:

```text
# Stage 186 Code Review
```
