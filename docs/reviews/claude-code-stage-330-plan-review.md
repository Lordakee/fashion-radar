## Stage 330 Plan Review

### Critical

None.

---

### Important

**1. `PruneResult` field names unverified — integration test is the only guard.**

The plan uses `data_retention.items_deleted` and `data_retention.item_entities_deleted` in the `typer.echo` output string (Task 1 Step 4). The mocked pipeline test uses a `SimpleNamespace` with those names so it passes regardless. Only the real-SQLite integration test in Task 2 exercises the actual `PruneResult` return value. Before implementing Step 4, verify the exact attribute names on `PruneResult` from `fashion_radar.db.repositories`. If they differ (e.g. `pruned_items`, `pruned_item_entities`), the integration test gives RED for the wrong reason and the implementer may patch the wrong thing.

Action: Read `fashion_radar/db/repositories.py` before Step 4 and confirm the field names. Adjust the echo format string and the Task 2 assertion string together.

---

**2. `ItemRepository.count_items()` — method existence unverified.**

The integration test (Task 2 Step 1) ends with:
```python
assert repository.count_items() == 1
```
`count_items()` is not called anywhere in the existing test files read. If `ItemRepository` does not expose this method, the integration test cannot be written as planned. Check `fashion_radar/db/repositories.py` before writing Task 2. A fallback is `len(repository.list_items_for_matching())` or a direct `SELECT COUNT(*) FROM items` query, both of which already exist in the codebase.

---

**3. 1-day default vs. scoring window interaction — underdocumented risk.**

`write_row_one_site_files` queries items over a `current_window_days` window (default 7 in the minimal config, project default 30). After the second refresh with `--retention-days 1`, SQLite only contains items from the last 24 hours. Heat scores are then computed against a 1-item baseline instead of a 7–30-day baseline, producing misleading deltas. The design doc says this is intentional ("near-daily cleanup for the test site"), but the risk to scoring quality is not surfaced in the planned doc text. The sentinel `"default1-day retention"` is present, but no sentinel requires a warning about the scoring window interaction.

Action: Add a docs sentinel like `"scoring window"` or `"heat scores"` that forces the documentation to explicitly state the tradeoff. Operators who set `--retention-days 1` for disk reasons but expect multi-day heat deltas will be surprised otherwise.

---

**4. `clean_old_data` inside the try/except — misleading failure message.**

The plan places the call inside the existing `try/except Exception` block (after `prune_stale_daily_report_files`). If data retention fails for any reason after a fully successful site and report generation, the user sees `"ROW ONE refresh failed:..."` — which hides that the primary work completed. `prune_stale_daily_report_files` has the same placement, so this follows an existing pattern. But retention is more likely to fail on a corrupt or locked database than a filesystem prune, and the consequences of missing the message ("your site is fresh") are higher. Consider a separate `try/except` around `clean_old_data` that prints a warning rather than aborting. If the existing pattern is intentional policy, document the tradeoff as an explicit design choice in the spec.

---

### Medium

**5. Existing pipeline test must be updated atomically with Step 4.**

`test_row_one_refresh_runs_pipeline_and_writes_site` asserts `calls` ends after `prune_stale_daily_report_files`. After Step 4 adds the real `clean_old_data` call, this test becomes RED unless the mock is present. The plan handles this correctly in Step 1 (update the test first, verify RED, then implement). The order is sound, but the worker must not split the test update and implementation across separate commits.

---

**6. `skip_data_retention` Typer rendering.**

`typer.Option(False, help="...")` on a `bool` parameter named `skip_data_retention` renders as `--skip-data-retention / --no-skip-data-retention` in Typer ≥ 0.9 by default, not just `--skip-data-retention`. The help assertion `"--skip-data-retention" in result.output` passes either way, but the help output will include the `--no-skip-data-retention` variant, which is an odd double-negative. The cleaner pattern used in this codebase is `typer.Option(False, "--skip-data-retention",...)` to keep only the positive flag. Check the Typer version in `pyproject.toml` and pin the flag name explicitly if the double-negative is undesired.

---

**7. `as_of` forwarded as string, not `datetime`.**

The plan passes `as_of=as_of` to `clean_old_data()` where `as_of` is the raw `str` CLI parameter (not yet parsed). `clean_old_data` accepts `str | datetime` and calls `parse_datetime_utc(as_of)` internally, so this works. However, the existing refresh pipeline parses `as_of` implicitly inside each workflow helper. Confirm there is no case where `as_of` arrives as `None` at the `clean_old_data` call site — Typer enforces `AS_OF_OPTION = typer.Option(...)` is required (`...`), so this is safe, but worth noting.

---

### Minor

**8. `ROW_ONE_RETENTION_DAYS_OPTION` constant placement.**

The plan adds the constant near `RETENTION_DAYS_OPTION`. The existing constant block is in a consistent pattern. No issues.

---

**9. `_normalized()` in docs tests.**

The Task 3 sentinel list uses `phrase in docs` after `_normalized()`. Verify that `_normalized` lowercases content, since the sentinel `"sqlite retention"` is lowercase and the planned documentation likely writes "SQLite retention". If `_normalized` does not lowercase, the sentinel will never match. This is a one-line check in `test_row_one_docs.py`.

---

**10. `docs/cli-reference.md` not in the review scope.**

The plan adds this file to both the Files section and the commit, but it is not in the list of files provided for this review. This is not a blocker — just flagged so a follow-up review after implementation can cover it.

---
