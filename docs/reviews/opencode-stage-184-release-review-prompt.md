# Stage 184 Release Review

Review Stage 184 release readiness for a commit that includes:

- `tests/test_lint_formatting.py`
- `docs/superpowers/specs/2026-06-24-stage-184-lint-formatting-edge-cases-design.md`
- `docs/superpowers/plans/2026-06-24-stage-184-lint-formatting-edge-cases-plan.md`
- `docs/reviews/opencode-stage-184-plan-review-prompt.md`
- `docs/reviews/opencode-stage-184-plan-review.md`
- `docs/reviews/opencode-stage-184-code-review-prompt.md`
- `docs/reviews/opencode-stage-184-code-review.md`
- `docs/reviews/opencode-stage-184-release-review-prompt.md`
- `docs/reviews/opencode-stage-184-release-review.md`

Context:
- Stage 184 broadens the direct `format_count_label(...)` test coverage.
- It proves caller-supplied labels are used for multi-word labels,
  identical singular/plural labels, and irregular plurals.
- It preserves original `error/errors` coverage for counts 0, 1, and 2.
- It does not change runtime code.
- Negative-count behavior is intentionally out of scope.

Verified commands already run:

```bash
uv --no-config run --frozen pytest tests/test_lint_formatting.py::test_format_count_label_uses_supplied_label_for_count -q
uv --no-config run --frozen pytest tests/test_lint_formatting.py -q
uv --no-config run --frozen ruff check tests/test_lint_formatting.py
uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py
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
- Focused Stage 184 target: 8 passed.
- `tests/test_lint_formatting.py`: 12 passed.
- Full pytest: 1385 passed.
- First-run smoke passed.
- Release hygiene passed.
- Ruff check and format check passed.
- Lock check passed.
- `git diff --check` passed.
- Secret and extraheader absence checks produced no output.

Review for:
- Any release blocker in the scoped Stage 184 commit.
- Any unsanitized review artifact content.
- Any missing verification before commit and push.

Respond with Critical / Important / Minor findings and a short verdict.

Start the body with:

```text
# Stage 184 Release Review
```
