# Stage 183 Release Review

Review Stage 183 release readiness for a partial commit that will include only:

- `tests/test_package_archives.py`
- `docs/superpowers/specs/2026-06-24-stage-183-package-archive-entry-point-case-design.md`
- `docs/superpowers/plans/2026-06-24-stage-183-package-archive-entry-point-case-plan.md`
- `docs/reviews/opencode-stage-183-plan-review-prompt.md`
- `docs/reviews/opencode-stage-183-plan-review.md`
- `docs/reviews/opencode-stage-183-code-review-prompt.md`
- `docs/reviews/opencode-stage-183-code-review.md`
- `docs/reviews/opencode-stage-183-release-review-prompt.md`
- `docs/reviews/opencode-stage-183-release-review.md`

Context:
- Stage 183 adds a test-only guard for case-sensitive wheel console-script names.
- It does not change runtime code.
- Stage 184 files may be present as intentionally pending work and are out of
  scope for this Stage 183 partial commit.

Verified commands already run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_entry_points_console_script_name_case_mismatch -q
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_package_archives.py
uv --no-config run --frozen ruff format --check tests/test_package_archives.py
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
- Focused Stage 183 target passed.
- `tests/test_package_archives.py`: 76 passed.
- Full pytest: 1385 passed.
- First-run smoke passed.
- Release hygiene passed.
- Ruff check and format check passed.
- Lock check passed.
- `git diff --check` passed.
- Secret and extraheader absence checks produced no output.

Review for:
- Any release blocker in the scoped Stage 183 commit.
- Any unsanitized review artifact content.
- Any missing verification before commit and push.

Respond with Critical / Important / Minor findings and a short verdict.

Start the body with:

```text
# Stage 183 Release Review
```
