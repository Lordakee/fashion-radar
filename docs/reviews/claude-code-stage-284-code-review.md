I've completed a thorough review of all Stage 284 changes. The codegraph source is re-read from disk (reflecting the uncommitted changes), so I traced the full flow: the pruning helper, both regexes, the CLI integration, the digest "latest"/index/eml interactions, the dashboard `latest_report_path` semantics, and both new unit tests plus the CLI test.

## APPROVED

The implementation precisely matches the stated goal and respects every constraint. No required fixes before commit.

### Why it's correct

The core retention property holds: `prune_stale_daily_report_files` computes the current date with `parse_datetime_utc(as_of).date()` (workflows.py:137) — the *same* derivation `write_daily_report_files`/`report_output_paths` use to name the artifacts (workflows.py:47, 112). So the files just written for `as_of` always compare equal and are kept; there is no timezone/off-by-one skew between writing and pruning even for non-UTC `as_of` offsets.

The classification logic (workflows.py:148-160) is sound: sorted-by-name (deterministic `removed_paths`), skips non-files, `None` (non-matching) preserved, `== current` kept+counted, `> current` (future) preserved, `< current` unlinked. Both patterns are anchored/`fullmatch` and restricted to `fashion-radar-YYYY-MM-DD.(md|json)` (digests.py:38) and `.html` (workflows.py:54); invalid dates fall through `date.fromisoformat`'s `ValueError` to `None` in both branches (workflows.py:126-129).

Ordering in the CLI is right: pruning runs *after* `_write_row_one_site_from_cli_options` succeeds (cli.py:1511-1522), and the printed message matches the spec exactly (cli.py:1536-1541).

### Test quality
`test_prune_stale_daily_report_files_removes_old_dated_artifacts` (test_workflows.py:267) is strong — it explicitly asserts preservation of `latest.md`, `latest.json`, `report-index.json`, `.eml`, `.txt`, a **future** date, `not-a-date`, and `notes.md`, while removing stale md/json/html plus an older md, and checks `removed_count`/`kept_current_count`/`current_date`/sorted `removed_paths` and on-disk existence. The missing-dir no-op and the CLI call-order/message test round it out. `_parse_daily_report_retention_path` has no direct test but is fully exercised transitively.

### Critical / Important findings
None.

### Optional follow-ups
1. **Retention is fatal to the whole refresh.** `prune_stale_daily_report_files` sits inside the `row_one_refresh` try block (cli.py:1519), *after* the report and site are already written. A transient `unlink()` `FileNotFoundError` (concurrent removal) or a permission error would abort with "ROW ONE refresh failed" despite the primary artifacts succeeding. Consider `path.unlink(missing_ok=True)` (workflows.py:159) and/or treating retention as best-effort so cleanup can't mask a successful refresh. Most worthwhile of these.
2. **SYMLINK digest-latest can dangle.** `write_latest_artifacts` (digests.py:88-109) may create `latest.md`/`latest.json` as symlinks to a dated report. Pruning correctly never removes `latest.*` (name doesn't match), but if the symlink target is an *older* date (e.g., `report --digest-latest symlink --as-of <old>` then `row-one refresh --as-of <new>`), the target is deleted and the symlink dangles. Cross-command edge, outside the row-one flow — worth a docs note or accepting as known behavior.
3. **`report-index.json` staleness.** A prior `report --digest-index` index lists dates that a later `row-one refresh` will prune; refresh doesn't regenerate it. Informational — it's rebuilt on the next `--digest-index`.
4. **`.eml` dated artifacts accumulate** under latest-only (intentional per scope and the test, but confirm that's the desired retention boundary).
5. **Cross-module private import.** workflows.py reaches into `digests._parse_daily_report_path` (underscore API). Pragmatic reuse; consider promoting to a shared non-underscore helper if the coupling grows.

### Verification note
The disclosed `scripts/check_first_run_smoke.py` direct-invocation failure (`candidates expected []`) reads as pre-existing repo-local working-tree data rather than a Stage 284 regression, and the pytest smoke fixtures were updated and pass. If you want that fully airtight, confirm the same failure occurs on the base commit before this stage — otherwise the evidence (1854 passed, ruff check/format, lock --check, git diff --check/--exit-code) is complete and green.

## Post-Review Follow-Up

Codex accepted optional follow-up 1 by changing the stale artifact unlink to
`Path.unlink(missing_ok=True)` and adding
`test_prune_stale_daily_report_files_tolerates_concurrent_removal`.

Final verification after that follow-up:

- `UV_NO_CONFIG=1 uv --no-config run ruff check .` -> passed
- `UV_NO_CONFIG=1 uv --no-config run ruff format --check .` -> passed
- `UV_NO_CONFIG=1 uv --no-config run pytest tests/test_workflows.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_smoke.py -q` -> `241 passed`
- `UV_NO_CONFIG=1 uv --no-config run pytest -q` -> `1855 passed`
- `UV_NO_CONFIG=1 uv --no-config lock --check` -> passed
- `git diff --check` -> passed
- `git diff --exit-code -- uv.lock pyproject.toml` -> passed
