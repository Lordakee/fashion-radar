# Stage 185 Release Review

Review Stage 185 release readiness for a commit that includes:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `docs/superpowers/specs/2026-06-24-stage-185-first-run-trends-delta-shape-design.md`
- `docs/superpowers/plans/2026-06-24-stage-185-first-run-trends-delta-shape-plan.md`
- `docs/reviews/opencode-stage-185-plan-review-prompt.md`
- `docs/reviews/opencode-stage-185-plan-review.md`
- `docs/reviews/opencode-stage-185-code-review-prompt.md`
- `docs/reviews/opencode-stage-185-code-review.md`
- `docs/reviews/opencode-stage-185-release-review-prompt.md`
- `docs/reviews/opencode-stage-185-release-review.md`

Context:
- Stage 185 hardens first-run smoke `validate_trends(...)`.
- It rejects any non-object entry in `payload["deltas"]` with an indexed
  `SmokeError`.
- It keeps existing trend name/type/status checks unchanged.
- It does not change CLI runtime, trend generation, scoring, models, dashboard,
  dependencies, or lockfiles.

Verified commands already run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_trends_rejects_non_object_delta_entries -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "trends or candidates"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
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
- New test RED before runtime change: failed because no `SmokeError` was raised.
- New test GREEN after runtime change: passed.
- Trends/candidates subset: 7 passed, 157 deselected.
- Full `tests/test_first_run_smoke.py`: 164 passed.
- Full pytest: 1386 passed.
- First-run smoke passed.
- Release hygiene passed.
- Ruff check and format check passed.
- Lock check passed.
- `git diff --check` passed.
- Secret and extraheader absence checks produced no output.

Review for:
- Any release blocker in the scoped Stage 185 commit.
- Any unsanitized review artifact content.
- Any missing verification before commit and push.
- Any out-of-scope change beyond first-run smoke validation.

Respond with Critical / Important / Minor findings and a short verdict.

Start the body with:

```text
# Stage 185 Release Review
```
