# Opencode Stage 57 Release Rereview Prompt

You are rereviewing the Stage 57 release candidate for the `fashion-radar`
repository at `/home/ubuntu/fashion-radar`.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a release rereview only.
- Do not edit files.
- Do not narrate tool usage or file-reading steps.
- Keep the response concise.
- Treat Critical and Important findings as blockers.

## Context

The initial Stage 57 release review in
`docs/reviews/opencode-stage-57-release-review.md` approved the release with no
Critical or Important findings and one Minor finding:

- `docs/dashboard.md` documented `Heat Movers` after `Trend Deltas`, while the
  implementation and tests place `Heat Movers` before `Trend Deltas`.

## Fix Since Initial Release Review

- `docs/dashboard.md` now lists `Heat Movers` before `Trend Deltas`.
- `tests/test_cli_docs.py` now imports `DASHBOARD_TAB_LABELS` and adds
  `test_dashboard_docs_current_tab_order_matches_app_labels()` so the dashboard
  docs "Current Tabs" list must match the actual app tab labels and order.

## Rereview Focus

Please verify:

1. The initial Minor tab-order finding is fixed.
2. The new docs drift test is appropriate and does not create unrelated import
   or environment problems.
3. No new Critical or Important issues were introduced after the initial
   release review.
4. `uv.lock` and `pyproject.toml` remain unchanged and mirror-free.

## Fresh Verification After The Minor Fix

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
# 967 passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
# All checks passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
# 113 files already formatted

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 84 packages

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
# Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --frozen --dev --check
# Would make no changes

if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
# no matches

git diff --exit-code -- uv.lock pyproject.toml
# clean

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed.

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed.

git diff --check
# clean
```

Installed-wheel smoke was also rerun after the Minor fix and passed. It
verified:

```bash
fashion-radar --help
fashion-radar heat-movers --help
fashion-radar heat-movers --config-dir "$tmp_configs" --data-dir "$tmp_data" --as-of 2026-06-13T12:00:00Z --format json
fashion-radar heat-movers --config-dir "$tmp_configs" --data-dir "$tmp_data" --as-of 2026-06-13T12:00:00Z --baseline-as-of 2026-06-06T12:00:00Z --include-cooling --format json
```

The installed-wheel smoke verified that missing `$tmp_data` remained absent,
the JSON output used `"execution_mode": "local_read_only"`, the empty report
used `"row_count": 0`, and the cooling run included `"cooling_watchlist"`.

## Output Format

Return:

- Critical findings
- Important findings
- Minor findings
- Verification commands you ran
- Final verdict

If there are no Critical or Important findings, include this exact approval
line:

```text
APPROVED FOR STAGE 57 RELEASE REREVIEW
```
