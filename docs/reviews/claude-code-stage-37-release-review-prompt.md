# Claude Code Stage 37 Release Review Prompt

You are reviewing the completed Stage 37 local platform provenance changes for
the `fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a release review only; do not edit files.
- Treat Critical and Important findings as blockers.
- Review the working tree diff, tests, docs, and release evidence.

## Goal

Preserve sanitized local manual/community signal `platform` provenance through
SQLite storage and local imported-signal review output.

## Boundaries

This stage must remain local provenance only:

- No source connectors.
- No scraping, crawling, browser automation, login/cookie flow, account
  automation, proxy/CAPTCHA handling, source acquisition, source ranking,
  demand proof, watcher, scheduler, or external platform API integration.
- No heat-score formula changes or platform-spread scoring.
- No storage of raw/private fields such as handles, raw comments, account IDs,
  private exports, local paths, cookies, sessions, browser profiles, generated
  reports, or tokens.
- No dependency or `uv.lock` changes.

## Implemented Approach

- Added nullable `items.platform` storage and schema v5 migration.
- Added idempotent v4-to-v5 migration for old databases, including the case
  where `platform` already exists but metadata still reports v4.
- Kept `CollectedItem` generic; added
  `ItemRepository.upsert_item(..., platform=...)` instead.
- Normalized repository platform labels by preserving `None`, trimming
  whitespace, and collapsing blanks to `None`.
- Passed `ManualSignalRow.platform` into the repository during local manual
  import storage.
- Exposed stored platform provenance in `imported-signals` review items,
  filtered platform counts, and table output.
- Exposed stored platform counts in `imported-signals-summary`, including
  per-source counts.
- Updated docs/changelog to describe `platform` as local provenance only.

## Files To Review

Run `git diff --stat` and inspect the full diff for:

- `src/fashion_radar/db/schema.py`
- `src/fashion_radar/db/repositories.py`
- `src/fashion_radar/importers/manual_signals.py`
- `src/fashion_radar/imported_signals.py`
- `tests/test_db.py`
- `tests/test_manual_signal_import.py`
- `tests/test_imported_signals.py`
- `tests/test_cli.py`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `README.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-14-stage-37-local-platform-provenance-design.md`
- `docs/superpowers/plans/2026-06-14-stage-37-local-platform-provenance-plan.md`
- `docs/reviews/claude-code-stage-37-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-37-plan-review.md`

## Plan Review Evidence

Claude Code plan review returned:

```text
Critical Findings: None.
Important Findings: None.
APPROVED FOR STAGE 37 LOCAL PLATFORM PROVENANCE
```

Minor recommendations were implemented:

- `platform_counts` use the same retained row conditions as the review query,
  including window/source/unmatched filters and excluding null/blank labels.
- repository normalization preserves `None` instead of turning it into the
  literal string `"None"`.
- migration tests cover the v4 metadata plus pre-existing platform column case.

## RED/GREEN Evidence

Observed RED before implementation:

- `UV_NO_CONFIG=1 uv run pytest tests/test_db.py -q -k "schema or platform or item_repository"`
  failed on missing `items.platform`, schema version still v4, v4-to-v5 missing,
  and unexpected `upsert_item(platform=...)`.
- Manual import storage tests failed because stored `platform` stayed `None`
  before `store_manual_signal_rows()` passed `row.platform`.
- Imported-signals tests failed because DTOs, schema validation, platform
  counts, and table outputs did not know about platform.

Observed GREEN after implementation:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py -q -k "schema or platform or item_repository"
# 14 passed, 4 deselected

UV_NO_CONFIG=1 uv run pytest \
  tests/test_manual_signal_import.py::test_store_manual_signal_rows_writes_sanitized_items \
  tests/test_manual_signal_import.py::test_store_manual_signal_rows_preserves_existing_normalized_url_upsert \
  tests/test_cli.py::test_import_signals_command_imports_csv \
  tests/test_cli.py::test_import_signals_dir_imports_csv_directory \
  -q
# 4 passed

UV_NO_CONFIG=1 uv run pytest tests/test_imported_signals.py -q
# 23 passed

UV_NO_CONFIG=1 uv run pytest \
  tests/test_cli.py::test_imported_signals_command_prints_table \
  tests/test_cli.py::test_imported_signals_command_prints_json_with_stable_keys \
  tests/test_cli.py::test_imported_signals_command_json_match_keys_exclude_internal_fields \
  tests/test_cli.py::test_imported_signals_summary_command_prints_table \
  tests/test_cli.py::test_imported_signals_summary_command_prints_json_with_stable_keys \
  -q
# 5 passed
```

## Full Verification Evidence

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py -q -k "schema or platform or import_signals or imported_signals"
# 85 passed, 187 deselected

UV_NO_CONFIG=1 uv lock --check
# Resolved 84 packages in 1ms

UV_NO_CONFIG=1 uv sync --locked --dev
# Resolved 84 packages in 1ms
# Checked 36 packages

UV_NO_CONFIG=1 uv sync --locked --dev --check
# Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
# Would make no changes

UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
# 582 passed

UV_NO_CONFIG=1 uv run ruff check .
# All checks passed

UV_NO_CONFIG=1 uv run ruff format --check .
# 92 files already formatted

git diff --check && git diff --cached --check && git diff --quiet -- uv.lock
# passed; uv.lock unchanged
```

## Boundary And Secret Evidence

- Diff-scoped boundary scan found only newly added negative boundary language
  such as "not scraping", "not source acquisition", "not platform coverage", and
  "not demand proof".
- Diff-scoped secret scan found no token/private-key patterns.
- `git config --get-regexp '^http\..*extraheader$' || true` produced no output.
- `git remote -v` shows token-free HTTPS remote:
  `https://github.com/Lordakee/fashion-radar.git`.

## Next Phase Plan

If approved:

1. Stage only Stage 37 files.
2. Commit with message `Preserve local platform provenance`.
3. Push to `origin/main` with a one-shot HTTP extraheader only; do not persist
   the GitHub token in files, remotes, or git config.
4. Confirm the latest GitHub Actions run for the pushed commit completes
   successfully.
5. Do not begin another development node until its own plan is submitted for
   Claude Code max review.

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 37 COMMIT AND PUSH
```
