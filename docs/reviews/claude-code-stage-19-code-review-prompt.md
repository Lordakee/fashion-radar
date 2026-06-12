# Claude Code Stage 19 Code Review Prompt

You are reviewing Stage 19 implementation for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Goal

Stage 19 upgrades `fashion-radar import-signals-dir` from Stage 18 dry-run-only
diagnostics to actual local directory import execution for user-provided
CSV/JSON manual signal files.

The command should:

- preserve Stage 18 `--dry-run` table and JSON diagnostics shape;
- validate `--imported-at` before reading files, even during `--dry-run`;
- match only regular direct-child files using the existing non-recursive
  `iterdir()` + `fnmatch` approach;
- validate every matched file before opening SQLite or creating `--data-dir`;
- import nothing if any matched file, directory check, no-match check, or
  timestamp validation fails;
- use existing `store_manual_signal_rows(...)` for successful imports, keeping
  existing normalized-URL upsert behavior and `manual_import` source type;
- ignore unknown/private input fields as the single-file importer already does;
- add no new dependencies and no lockfile changes;
- update user docs and upload checklist without implying platform acquisition,
  scraping, monitoring, authorization verification, or compliance/audit/policy
  workflow features.

## Files Changed

Implementation:

- `src/fashion_radar/importers/manual_signals.py`
- `src/fashion_radar/cli.py`

Tests:

- `tests/test_manual_signal_import.py`
- `tests/test_cli.py`

Docs and process artifacts:

- `README.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-12-stage-19-import-signals-directory-execution-design.md`
- `docs/superpowers/plans/2026-06-12-stage-19-import-signals-directory-execution-plan.md`
- `docs/reviews/claude-code-stage-19-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-19-plan-review.md`
- `docs/reviews/claude-code-stage-19-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-19-plan-rereview.md`
- this code review prompt/result.

## Prior Reviews

- Initial plan review:
  `docs/reviews/claude-code-stage-19-plan-review.md`
- Plan rereview approval:
  `docs/reviews/claude-code-stage-19-plan-rereview.md`

## Verification Already Run

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_manual_signal_import.py -q -k "directory_load or directory_import" -p no:cacheprovider
# 3 passed, 39 deselected

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_manual_signal_import.py -q -k "directory_dry_run or directory_load or directory_import" -p no:cacheprovider
# 13 passed, 29 deselected

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_cli.py -q -k import_signals_dir -p no:cacheprovider
# 16 passed, 80 deselected

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_manual_signal_import.py tests/test_cli.py -q -k "directory_load or directory_import or directory_dry_run or import_signals_dir" -p no:cacheprovider
# 29 passed, 109 deselected

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
# 395 passed

.venv/bin/python -m ruff check . --no-cache
# All checks passed!

.venv/bin/python -m ruff format --check .
# 78 files already formatted

git diff --check
# exit 0
```

Docs boundary scan was also run. Matches were command examples or explicit
negative boundary language.

## Review Request

Please review the uncommitted diff from `origin/main` to the working tree.
Focus on:

1. Does Stage 18 dry-run table/JSON behavior remain compatible?
2. Does actual import validate all matched files before SQLite/data-dir creation?
3. Do invalid directory, unreadable directory, no-match, invalid file, invalid
   `--imported-at`, and invalid `--dry-run --imported-at` fail without creating
   project artifacts?
4. Does the new directory load helper retain validated rows instead of re-reading
   files before import?
5. Does import success reuse the existing single-file storage semantics,
   including sanitized storage and normalized URL upserts?
6. Is CLI output deterministic and JSON-only when `--output-format json` is used?
7. Are tests sufficient and correctly asserting atomic validation-before-import?
8. Do docs avoid source acquisition, scraping, platform coverage, authorization
   verification, approval/audit/policy workflow features, and market-wide
   ranking claims?
9. Is there any unnecessary abstraction, hidden side effect, or regression risk?

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 19 release`
- `Not approved`

Do not modify files.
