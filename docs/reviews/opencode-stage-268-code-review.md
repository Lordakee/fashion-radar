## Stage 268 Review: `row-one refresh`

### Verification performed
- Read design/plan docs, full diff of all 12 files, and existing `run`/`build`/`preview` command patterns for comparison.
- Ran focused suite: **215 passed**; `ruff check` clean; `ruff format --check` clean; `check_first_run_smoke.py` passed.

### Critical
None. The implementation meets every stated criterion:
- Reuses workflow helpers in-process (`collect_configured_sources` → `match_stored_items` → `write_daily_report_files` → `_write_row_one_site_from_cli_options`), no subprocess/cli shelling (`cli.py:1483-1531`).
- Order is collect → match → report → site, asserted by `test_row_one_refresh_runs_pipeline_and_writes_site` via call-order list.
- `latest_only=True` hardcoded (`cli.py:1510`), not user-toggleable.
- Cron/systemd/local-ops renderers now emit the single `row-one refresh` command with no `--latest-only`.
- Smoke loop + deterministic sequence both add `row-one refresh --help` consistently; fake outputs updated.
- No docs show `row-one refresh --latest-only` (only hit is the smoke forbidden-text guard at `check_first_run_smoke.py:1101`, which is correct).
- No timers, daemon, schema, collector, LLM, or compliance-review changes.

### Important
- **Resolved during release prep: review artifacts needed cleanup.** The initial capture included process narration before the substantive findings. The Stage 268 plan-review, rereview, final-review, and code-review artifacts were trimmed to start at their Markdown review headings before commit.

### Minor
- **Output phrasing drift from `run`.** `run` prints `Stored {N} matches`; `refresh` prints `Stored matches: {N}` (`cli.py:1521`). Cosmetic and self-consistent with its test, but diverges from the sibling command and the plan's Step-1 expectation text ("Stored 1 matches").
- **Config loaded twice.** `refresh` loads scoring/entity config for the report, then `_write_row_one_site_from_cli_options` reloads them again (`cli.py:1543-1547`). Mirrors existing `build`/`preview` behavior and the old two-step flow, so not a regression — noting only.
- Plan-vs-test divergence: plan Step 1 specified call-order labels `["collect","match","report","row-one"]`, but the test uses the actual symbol names. Harmless; test is correct.

### Verdict
**Approved to commit.** The code, tests, scheduling snippets, smoke harness, and docs are correct, internally consistent, and pass all focused gates. The Minor items are optional polish.
