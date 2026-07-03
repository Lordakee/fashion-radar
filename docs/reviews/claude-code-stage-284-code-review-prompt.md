# Stage 284 Code Review Request

Please review the Stage 284 changes in `/home/ubuntu/fashion-radar`.

## Goal

`fashion-radar row-one refresh` should keep generated dated report artifacts latest-only for the selected `--reports-dir`: after report writing and successful site generation, stale top-level `fashion-radar-YYYY-MM-DD.md`, `.json`, and `.html` files older than the active `--as-of` date are pruned. Current-day artifacts remain. Nonmatching files are preserved.

## Changed Files

- `src/fashion_radar/workflows.py`
  - Adds `ReportRetentionResult`.
  - Adds `prune_stale_daily_report_files`.
  - Reuses `digests._parse_daily_report_path` for md/json and adds matching HTML date parsing.
  - Deletes only top-level regular files whose report date is strictly less than `as_of.date()`.
  - Uses `Path.unlink(missing_ok=True)` so concurrent stale-file removal does not fail refresh.
- `src/fashion_radar/cli.py`
  - Calls the helper in `row_one_refresh` after `_write_row_one_site_from_cli_options(...)` succeeds.
  - Prints `Latest-only reports: removed X stale files for YYYY-MM-DD; kept Y current files`.
- Tests/docs/smoke updated:
- `tests/test_workflows.py`
  - `tests/test_row_one_cli.py`
  - `tests/test_row_one_docs.py`
  - `tests/test_first_run_smoke.py`
  - `scripts/check_first_run_smoke.py`
  - `docs/row-one.md`, `reports/README.md`, `README.md`
- Review artifacts/plan added under `docs/reviews/` and `docs/superpowers/plans/`.

## Constraints

No DB pruning, no source collection, no scraping, no platform/social connectors, no browser automation, no login/cookie behavior, no image generation, no schema changes, no scoring/matching/ranking/story ID changes, no dependency changes, and no compliance product feature.

## Verification Evidence

Focused tests:
- `UV_NO_CONFIG=1 uv --no-config run pytest tests/test_workflows.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_smoke.py -q` -> `240 passed`
- `UV_NO_CONFIG=1 uv --no-config run pytest tests/test_workflows.py::test_prune_stale_daily_report_files_tolerates_concurrent_removal tests/test_workflows.py::test_prune_stale_daily_report_files_removes_old_dated_artifacts tests/test_workflows.py::test_prune_stale_daily_report_files_missing_directory_is_noop -q` -> `3 passed`

Full checks:
- `UV_NO_CONFIG=1 uv --no-config run ruff check .` -> passed
- `UV_NO_CONFIG=1 uv --no-config run ruff format --check .` -> `179 files already formatted`
- `UV_NO_CONFIG=1 uv --no-config run pytest -q` -> `1854 passed`
- `UV_NO_CONFIG=1 uv --no-config lock --check` -> passed
- `git diff --check` -> passed
- `git diff --exit-code -- uv.lock pyproject.toml` -> passed

Note: direct `UV_NO_CONFIG=1 uv --no-config run python scripts/check_first_run_smoke.py --repo-root .` currently fails on pre-existing repo-local candidate data (`candidates expected []`) before Stage 284-specific ROW ONE assertions complete. The pytest first-run smoke fixtures were updated and pass.

## Diff Summary

 README.md                        |  9 +++++
 docs/row-one.md                  | 31 +++++++++++------
 reports/README.md                |  8 +++++
 scripts/check_first_run_smoke.py | 35 +++++++++++++++++++
 src/fashion_radar/cli.py         | 11 ++++++
 src/fashion_radar/workflows.py   | 72 +++++++++++++++++++++++++++++++++++++++-
 tests/test_first_run_smoke.py    | 41 +++++++++++++++++++++++
 tests/test_row_one_cli.py        | 19 +++++++++++
 tests/test_row_one_docs.py       | 14 +++++---
 tests/test_workflows.py          | 59 ++++++++++++++++++++++++++++++++
 10 files changed, 283 insertions(+), 16 deletions(-)

## Please Evaluate

Return:
- APPROVED or NOT APPROVED
- Critical/Important findings with file/line references
- Required fixes before commit
- Optional follow-ups
