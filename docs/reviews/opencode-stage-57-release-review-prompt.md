# Opencode Stage 57 Release Review Prompt

You are reviewing the Stage 57 release candidate for the `fashion-radar`
repository at `/home/ubuntu/fashion-radar`.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a release review only.
- Do not edit files.
- Do not narrate tool usage or file-reading steps.
- Keep the response concise.
- Treat Critical and Important findings as blockers.

## Goal

Add a local read-only `heat-movers` view that groups observed new and rising
tracked entities and candidate phrases from existing trend deltas. The view is
available through:

- `fashion-radar heat-movers`
- the optional Streamlit dashboard `Heat Movers` tab

## Expected Technical Approach

- Add a pure `src/fashion_radar/heat_movers.py` module over
  `TrendComparison`.
- Keep strict Pydantic models, stable group order, optional cooling group, and
  stable JSON/table output.
- Reuse existing trend comparison loading and read-only SQLite schema checks.
- Add CLI tests, dashboard tests, docs drift tests, and direct unit tests.
- Add bounded docs that describe local observed heat movement for one
  configured source set.
- Do not add platform/social/source connectors, collection, scraping, crawling,
  API clients, browser automation, accounts/cookies/sessions, monitoring,
  scheduling, schema changes, migrations, dependency changes, report writes,
  dashboard writes, config writes, entity generation, ranking, demand proof,
  platform coverage verification, or compliance/legal/authorization/safety
  review features.

## Files Changed Or Added In This Stage

Modified:

- `AGENTS.md`
- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `docs/dashboard.md`
- `docs/github-upload-checklist.md`
- `docs/source-boundaries.md`
- `docs/trend-deltas.md`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `tests/test_dashboard.py`

Added:

- `src/fashion_radar/heat_movers.py`
- `tests/test_heat_movers.py`
- `docs/superpowers/specs/2026-06-17-stage-57-local-heat-movers-design.md`
- `docs/superpowers/plans/2026-06-17-stage-57-local-heat-movers-plan.md`
- `docs/reviews/opencode-stage-57-plan-review-prompt.md`
- `docs/reviews/opencode-stage-57-plan-review.md`
- `docs/reviews/opencode-stage-57-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-57-plan-rereview.md`
- `docs/reviews/opencode-stage-57-release-review-prompt.md`
- Added after this prompt runs:
  `docs/reviews/opencode-stage-57-release-review.md`

## Implementation Summary

- `build_heat_movers()` groups `TrendComparison.deltas` into:
  - `new_tracked_entities`
  - `rising_tracked_entities`
  - `new_candidate_phrases`
  - `rising_candidate_phrases`
  - optional `cooling_watchlist`
- The helper is pure over `TrendComparison`; it has no DB, file, network,
  source, platform, or browser behavior.
- `render_heat_movers_table()` states:
  - local observed heat movers need review
  - configured source set only
  - no demand proof
  - no platform coverage verification
  - no local observed heat movers for empty comparisons
- The CLI command mirrors the existing `trends` command validation and
  read-only database flow:
  - validates `--as-of`
  - supports `--baseline-as-of`
  - rejects baseline timestamps at or after `as_of`
  - validates local config before database access
  - returns an empty report when the SQLite database is missing without
    creating the data directory or SQLite file
  - uses `create_readonly_sqlite_engine`, `verify_readonly_trend_schema`, and
    `build_trend_comparison(..., include_dropped=False, limit=None)`
  - supports `--limit`, `--format table|json`, and `--include-cooling`
- The dashboard adds a `Heat Movers` tab before `Trend Deltas` and routes tabs
  by label instead of positional slicing.
- Docs and docs drift tests freeze the local-only boundary wording and public
  CLI flag docs, including `--baseline-as-of` and `--include-cooling`.

## Review Focus

Please inspect the diff and verify:

1. `heat-movers` is local read-only and cannot create SQLite/data/report/config
   artifacts in the missing-database path.
2. The CLI path validates timestamps/config before touching the database and
   keeps existing DBs read-only.
3. The command uses existing trend helpers and does not introduce schema,
   migration, dependency, lockfile, source, scraper, crawler, platform API,
   browser automation, account/cookie/session, monitoring, or scheduling
   changes.
4. The dashboard reuses `load_trend_comparison()` and `build_heat_movers()`,
   and routes tabs by label after adding `Heat Movers`.
5. Core grouping output is deterministic, stable by group, validates group
   names, applies `limit_per_group` per group, and handles empty comparisons.
6. Docs do not make platform-wide, demand, or social trend claims; docs say the
   output needs review, uses configured sources and imported local signals, is
   one configured source set, has no demand proof, and has no platform coverage
   verification.
7. `docs/cli-reference.md` documents all public `heat-movers` flags:
   `--config-dir`, `--data-dir`, `--as-of`, `--baseline-as-of`, `--limit`,
   `--format table|json`, and `--include-cooling`.
8. `docs/github-upload-checklist.md` installed-wheel help loop includes
   `heat-movers`.
9. `uv.lock` and `pyproject.toml` are unchanged and mirror-free.

## Verification Evidence Already Run

Targeted Stage 57 checks:

```bash
uv run pytest tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py -q
# 333 passed

uv run ruff check src/fashion_radar/heat_movers.py src/fashion_radar/cli.py src/fashion_radar/dashboard/app.py tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py
# All checks passed

uv run ruff format --check src/fashion_radar/heat_movers.py src/fashion_radar/cli.py src/fashion_radar/dashboard/app.py tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py
# 7 files already formatted

git diff --check
# clean
```

Full release checks:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
# 966 passed

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

Installed-wheel smoke also passed with a temporary build and venv. The install
used the Tsinghua PyPI mirror for dependency download only; no project files or
lockfiles were changed. It verified:

```bash
fashion-radar --help
fashion-radar heat-movers --help
fashion-radar heat-movers --config-dir "$tmp_configs" --data-dir "$tmp_data" --as-of 2026-06-13T12:00:00Z --format json
fashion-radar heat-movers --config-dir "$tmp_configs" --data-dir "$tmp_data" --as-of 2026-06-13T12:00:00Z --baseline-as-of 2026-06-06T12:00:00Z --include-cooling --format json
```

The installed-wheel smoke verified that missing `$tmp_data` remained absent,
the JSON output used `"execution_mode": "local_read_only"`, the empty report
used `"row_count": 0`, and the cooling run included `"cooling_watchlist"`.

Two read-only Codex subagents reviewed docs/core risk. Their Important finding
about missing empty table wording was fixed before the full release checks.

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
APPROVED FOR STAGE 57 RELEASE
```
