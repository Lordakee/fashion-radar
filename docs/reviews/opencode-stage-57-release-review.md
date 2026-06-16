I'll perform the Stage 57 release review. Let me start by examining the changes systematically.
Let me compare with the existing `trends` command to verify the flow matches.
The CLI flow mirrors `trends_command` correctly. Now let me check the test files and verify the read-only behavior.
I noticed a potential doc ordering issue. Let me check the remaining docs and verify the tab order claim.
Now let me run the verification commands to confirm everything passes.
Let me run the full test suite and full lint to independently verify.
All verification passes. Here is my Stage 57 release review.

---

# Stage 57 Release Review (`heat-movers`)

## Critical findings
None.

## Important findings
None.

## Minor findings
- **Doc tab-order drift in `docs/dashboard.md`.** The "Current Tabs" list (lines 63-66) documents `Heat Movers` **after** `Trend Deltas`, but the implementation places `Heat Movers` **before** `Trend Deltas` in `DASHBOARD_TAB_LABELS` (`src/fashion_radar/dashboard/app.py:40-48`), and `test_dashboard_tab_labels_include_heat_movers_before_trend_deltas` asserts that order. The documented tab order does not match the rendered order. No drift test currently guards the documented tab ordering. This is cosmetic documentation drift and does not affect correctness, the read-only boundary, or safety.

## Focus-point verification
1. **Local read-only / no artifact creation on missing DB** — Pass. The missing-DB branch builds an in-memory `TrendComparison(..., deltas=[])` and returns without creating the data dir or SQLite file; `test_heat_movers_command_missing_database_writes_nothing_and_prints_empty_outputs` asserts `not json_data_dir.exists()` and `not (json_data_dir / "fashion-radar.sqlite").exists()`.
2. **Timestamp/config validation before DB; existing DBs read-only** — Pass. `--as-of`, `--baseline-as-of`, baseline `< as_of`, and `ConfigError` are all handled before `default_database_path`; four rejection tests assert `not data_dir.exists()`. `test_heat_movers_command_existing_database_remains_read_only` and `...rejects_incompatible_database_without_schema_mutation` confirm no row/schema mutation.
3. **Reuses trend helpers; no schema/migration/deps/scrape/platform/scheduling** — Pass. `diff --stat` shows only the new pure `heat_movers.py`, CLI/dashboard edits, tests, and docs. `uv.lock` and `pyproject.toml` are byte-identical (`git diff --exit-code` clean). Command uses `create_readonly_sqlite_engine`, `verify_readonly_trend_schema`, `build_trend_comparison(..., include_dropped=False, limit=None)`.
4. **Dashboard reuses `load_trend_comparison()` + `build_heat_movers()`; tab routing by label** — Pass. `render_heat_movers` calls both helpers; `main()` builds `tab_by_label = dict(zip(DASHBOARD_TAB_LABELS, tabs, strict=True))` and routes `tab_by_label["Heat Movers"]`. `test_dashboard_main_routes_heat_movers_and_trend_deltas_by_label` verifies heat→"Heat Movers", trend→"Trend Deltas".
5. **Deterministic grouping, stable order, validated names, per-group limit, empty handling** — Pass. Fixed `specs` list, `HeatMoverGroupName` Literal rejects unknown names, `_limited` slices each group independently, empty comparisons yield empty groups; all covered by `tests/test_heat_movers.py`.
6. **Docs boundary wording (needs review, configured sources + imported local signals, one configured source set, no demand proof, no platform coverage verification; no platform-wide/demand/social claims)** — Pass. `test_heat_movers_public_docs_are_linked_and_bounded` and `test_heat_movers_sections_do_not_make_positive_scope_claims` enforce the wording and forbid `hottest`/`viral`/`market-wide trend`/`platform-wide popularity`/`verified demand`/`top social trend`.
7. **`docs/cli-reference.md` lists all public flags** — Pass. Section documents `--config-dir`, `--data-dir`, `--as-of`, `--baseline-as-of`, `--limit`, `--format table|json`, `--include-cooling`; `test_heat_movers_cli_reference_lists_public_flags` verifies each.
8. **`docs/github-upload-checklist.md` help loop includes `heat-movers`** — Pass. `heat-movers` added to the bash loop; `test_heat_movers_upload_checklist_help_loop_includes_command` verifies it.
9. **`uv.lock` and `pyproject.toml` unchanged and mirror-free** — Pass. `git diff --exit-code` clean; `rg` for mirror markers in `uv.lock` returned no matches.

## Verification commands run
- `env -u UV_* UV_NO_CONFIG=1 uv run pytest tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py -q` → **333 passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run pytest -q` → **966 passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run ruff check .` → **All checks passed**
- `env -u UV_* UV_NO_CONFIG=1 uv run ruff format --check <7 stage files>` → **7 files already formatted**
- `env -u UV_* UV_NO_CONFIG=1 uv lock --check` → **Resolved 84 packages**
- `env -u UV_* UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .` → **Release hygiene checks passed**
- `rg 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock` → **no matches**
- `git diff --exit-code -- uv.lock pyproject.toml` → **clean**
- `git diff --check` → **clean**
- `uv run fashion-radar heat-movers --help` → lists all seven public flags

## Final verdict

```text
APPROVED FOR STAGE 57 RELEASE
```
