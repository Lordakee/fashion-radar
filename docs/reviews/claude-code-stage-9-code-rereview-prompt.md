# Claude Code Stage 9 Code Rereview Prompt

You are rereviewing the Stage 9 implementation for Fashion Radar after one
post-review fix. Run this as a read-only code review. Do not edit files, do not
run collectors, do not call the network, and do not execute platform/social
tooling.

Use maximum reasoning effort. The invoking command must be:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-9-code-rereview-prompt.md
```

## Review Base

Review the current uncommitted implementation changes on top of:

```text
862d9821d7d56ec136eee31e3f16a06dc7ac5f5d docs: add stage 9 manual import plan
```

## Context

The prior Claude Code review approved Stage 9 for commit and GitHub sync with
only Minor comments. A parallel Codex review found one Important issue:

- `published_at` values of JSON `null` or short CSV rows missing the
  `published_at` cell could raise raw `TypeError` from `dateutil` instead of
  the importer-level `ManualSignalImportError`.

The safety ordering was still correct because this happened before database
creation, but the CLI error path was not clean.

## Fix To Rereview

The implementation now:

- Adds importer tests for JSON `published_at: null`.
- Adds importer tests for short CSV rows where the required `published_at`
  value is missing.
- Adds a CLI regression test confirming JSON `published_at: null` exits with
  `Could not import signals: row 1`, does not show a traceback, and does not
  create the data directory or SQLite database.
- Updates `ManualSignalRow.normalize_published_at()` to reject `None` and blank
  values as `ValueError("field cannot be empty")`.
- Converts `TypeError` from `parse_datetime_utc()` into `ValueError` for both
  `published_at` and `collected_at` validators, so Pydantic wraps it and
  `load_manual_signal_rows()` converts it into `ManualSignalImportError`.

## Stage 9 Safety Boundary

Stage 9 remains a local-only manual import feature. It must not add or document:

- platform search or automated social collection
- crawlers, scrapers, browser automation, Playwright, Selenium, MCP platform
  scraping servers, or account automation
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining exports from Instagram, TikTok, X/Twitter,
  Xiaohongshu, or similar platforms
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile internals, images, videos, media downloading, or reposting
- claims of complete social listening, complete platform coverage, verified
  demand, market-wide trend proof, or real-time social monitoring

## Verification After Fix

Fresh verification commands completed successfully after the fix:

```bash
.venv/bin/python -m pytest tests/test_manual_signal_import.py::test_manual_signal_import_rejects_json_null_published_at tests/test_manual_signal_import.py::test_manual_signal_import_rejects_short_csv_rows tests/test_cli.py::test_import_signals_command_rejects_null_published_at_before_data_dir_creation -q
# 3 passed

.venv/bin/python -m pytest tests/test_manual_signal_import.py tests/test_cli.py -q
# 57 passed

.venv/bin/python -m pytest -q
# 203 passed

.venv/bin/python -m ruff check .
# All checks passed

.venv/bin/python -m ruff format --check .
# 65 files already formatted

git diff --check
# no output

uv lock --check
# Resolved 84 packages

uv sync --locked --dev --check
# Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
# Would make no changes
```

## Review Questions

Please focus on:

1. Whether the new validator behavior correctly converts bad local date values
   into `ManualSignalImportError` through the existing importer wrapper.
2. Whether the CLI invalid-input path remains validate-before-write and avoids
   data directory/database creation.
3. Whether the fix has any unintended side effects on valid CSV/JSON imports,
   optional `collected_at`, or source-weight/source-name handling.
4. Whether Stage 9 remains within the explicit local-only safety boundary.

## Response Format

Start with one of:

- `Approved for Stage 9 commit and GitHub sync`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before commit.
- `Important:` issues that should be fixed before commit.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
