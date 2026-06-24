# Stage 186 Release Review

Review Stage 186 release readiness for a commit that includes:

- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-24-stage-186-readiness-skip-mark-guard-design.md`
- `docs/superpowers/plans/2026-06-24-stage-186-readiness-skip-mark-guard-plan.md`
- `docs/reviews/opencode-stage-186-plan-review-prompt.md`
- `docs/reviews/opencode-stage-186-plan-review.md`
- `docs/reviews/opencode-stage-186-code-review-prompt.md`
- `docs/reviews/opencode-stage-186-code-review.md`
- `docs/reviews/opencode-stage-186-release-review-prompt.md`
- `docs/reviews/opencode-stage-186-release-review.md`

Context:
- Stage 186 broadens the external-tool readiness parity meta guard.
- It rejects both `skipif` and bare `skip` marks on the readiness parity test.
- It adds a synthetic helper-focused test proving both marks are detected.
- It is test-only and changes no runtime source files.

Verified commands already run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "readiness_payload_parity or skip_guard"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Observed results:
- RED: helper-focused test failed with `NameError` before the helper existed.
- Targeted GREEN: 3 passed.
- Focused subset: 3 passed, 163 deselected.
- Full `tests/test_first_run_smoke.py`: 166 passed.
- Full pytest: 1388 passed.
- First-run smoke passed.
- Release hygiene passed.
- Ruff check and format check passed.
- Lock check passed.
- `git diff --check` passed.
- Secret and extraheader absence checks produced no output.

Review for:
- Any release blocker in the scoped Stage 186 commit.
- Any unsanitized review artifact content.
- Any missing verification before commit and push.
- Any out-of-scope runtime/source/dependency change.

Respond with Critical / Important / Minor findings and a short verdict.

Start the body with:

```text
# Stage 186 Release Review
```
