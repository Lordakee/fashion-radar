# Stage 203 Release Review Prompt

Review Stage 203 final release readiness.

Goal: release a narrow hygiene stage that rejects mirror/private index material
in the public root `uv.lock` while preserving frozen local mirror installs.

Changed files expected in this stage:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-203-uv-lock-release-hygiene-plan.md`
- `docs/reviews/opencode-stage-203-plan-review-prompt.md`
- `docs/reviews/opencode-stage-203-plan-review.md`
- `docs/reviews/opencode-stage-203-code-review-prompt.md`
- `docs/reviews/opencode-stage-203-code-review.md`
- `docs/reviews/opencode-stage-203-release-review-prompt.md`

Verification evidence already run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "uv_lock"
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py docs/dependency-mirrors.md docs/github-upload-checklist.md CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-203-uv-lock-release-hygiene-plan.md docs/reviews/opencode-stage-203-plan-review.md docs/reviews/opencode-stage-203-plan-review-prompt.md
uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py
git diff --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
git status --short --branch --untracked-files=all
```

Important command interpretation:

- The `rg` mirror-marker scan of `uv.lock` is expected to return exit code `1`
  and no output when there are no matches.
- Full pytest collected 1492 tests and passed.
- `uv.lock` and `pyproject.toml` are expected to have no diff.

Please review:

1. Are the implementation, tests, docs, changelog, and review artifacts ready to
   commit and push?
2. Does release hygiene pass on the current working tree, including all Stage
   203 review artifacts?
3. Are verification commands sufficient for a release-hygiene-only change?
4. Does the stage preserve local mirror install workflow and keep public
   lockfile validation isolated with `UV_NO_CONFIG=1` / `uv --no-config`?
5. Does the stage avoid dependency, source, connector, scraper, platform
   coverage, demand proof, and compliance-review product behavior changes?
6. Is the current git status limited to expected Stage 203 files?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
