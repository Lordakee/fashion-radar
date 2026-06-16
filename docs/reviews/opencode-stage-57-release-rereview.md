I'll perform the Stage 57 release rereview. Let me verify the fix and run fresh checks.
Let me verify the dashboard import doesn't cause environment issues and run the fresh verification commands.
Now let me run the full verification suite fresh.
# Stage 57 Release Rereview (`heat-movers`)

## Critical findings
None.

## Important findings
None.

## Minor findings
None. The initial Minor finding (tab-order drift in `docs/dashboard.md`) is fixed: the "Current Tabs" list now documents `Heat Movers` (line 65) before `Trend Deltas` (line 66), matching `DASHBOARD_TAB_LABELS` at `src/fashion_radar/dashboard/app.py:50-51`.

## Rereview focus verification
1. **Initial Minor tab-order finding fixed** — Pass. `docs/dashboard.md:63-73` lists the 11 tabs in the exact order of `DASHBOARD_TAB_LABELS` (`Daily Brief`, `Candidate Signals`, `Heat Movers`, `Trend Deltas`, entity mentions, `Source Health`).
2. **New docs drift test is appropriate and environment-safe** — Pass. `tests/test_cli_docs.py:365` adds `test_dashboard_docs_current_tab_order_matches_app_labels`, asserting `_dashboard_current_tab_labels() == list(DASHBOARD_TAB_LABELS)`. The helper (`tests/test_cli_docs.py:248-252`) parses the "Current Tabs" bullet list. The new top-level import `from fashion_radar.dashboard.app import DASHBOARD_TAB_LABELS` (`tests/test_cli_docs.py:14`) is safe because `dashboard/app.py` does not import `streamlit` at module load (lazy import confirmed), so no dashboard extra is required. Test passes standalone and in the full suite.
3. **No new Critical/Important issues introduced** — Pass. Test count went from 966 → 967 (the +1 is the new drift test), consistent with no other behavioral changes. Ruff, hygiene, first-run smoke, and `git diff --check` all clean. `uv.lock`/`pyproject.toml` are absent from the modified-files list.
4. **`uv.lock` and `pyproject.toml` unchanged and mirror-free** — Pass. `git diff --exit-code -- uv.lock pyproject.toml` clean; `rg` for mirror markers in `uv.lock` returned no matches.

## Verification commands run
- `env -u UV_* UV_NO_CONFIG=1 uv run pytest -q` → **967 passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_dashboard_docs_current_tab_order_matches_app_labels -v` → **1 passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run ruff check .` → **All checks passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run ruff format --check .` → **113 files already formatted**
- `env -u UV_* UV_NO_CONFIG=1 uv lock --check` → **Resolved 84 packages**
- `env -u UV_* UV_NO_CONFIG=1 uv sync --locked --dev --check` → **Would make no changes**
- `rg 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock` → **no matches**
- `git diff --exit-code -- uv.lock pyproject.toml` → **clean**
- `git diff --check` → **clean**
- `env -u UV_* UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .` → **Release hygiene checks passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .` → **First-run sample smoke passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run python -c "from fashion_radar.dashboard.app import DASHBOARD_TAB_LABELS; ..."` → confirms import works without dashboard extra

## Final verdict

```text
APPROVED FOR STAGE 57 RELEASE REREVIEW
```
