# Stage 203 Code Review Prompt

Review the Stage 203 code changes.

Goal: make `scripts/check_release_hygiene.py` reject mirror/private index
material in the public root `uv.lock`, while preserving frozen local mirror
installs and avoiding any dependency or product behavior changes.

Changed files to review:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-203-uv-lock-release-hygiene-plan.md`
- `docs/reviews/opencode-stage-203-plan-review-prompt.md`
- `docs/reviews/opencode-stage-203-plan-review.md`

Verification already run before this review:

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
```

Notes:

- The `rg` command is expected to return exit code `1` with no output when
  there are no matches.
- Do not request dependency changes or `uv.lock` regeneration unless there is a
  concrete correctness problem.

Please review:

1. Does the implementation correctly scan only root `uv.lock` and avoid
   repo-wide mirror false positives?
2. Does it correctly reject non-PyPI registry URLs, non-`files.pythonhosted.org`
   artifact URLs, and lockfile-local index markers?
3. Does it allow current public PyPI `uv.lock` content, including the editable
   local project source?
4. Are all findings redacted and line-numbered?
5. Do the tests cover tracked/untracked states, redaction, public pass behavior,
   current-repo cleanliness, and marker labels?
6. Do docs and changelog accurately describe the behavior without implying that
   local frozen mirror installs are disallowed?
7. Does the change avoid dependency, source, connector, scraper, platform
   coverage, demand proof, and compliance-review product behavior changes?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
