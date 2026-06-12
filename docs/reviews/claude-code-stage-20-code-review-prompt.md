# Claude Code Stage 20 Code Review Prompt

Please review the current Stage 20 code and docs before GitHub upload. Do not
edit files. Use maximum reasoning.

## Goal

Stage 20 adds:

```bash
fashion-radar imported-signals --data-dir ./data --as-of 2026-06-12T12:00:00Z
```

The command reviews retained local SQLite rows where
`items.source_type == "manual_import"` after `import-signals` or
`import-signals-dir`. It is intended for local post-import inspection before
matching, candidate discovery, trend comparison, reports, or dashboard review.

## Plan Review Status

- Stage 20 plan review prompt:
  `docs/reviews/claude-code-stage-20-plan-review-prompt.md`
- First plan review:
  `docs/reviews/claude-code-stage-20-plan-review.md`
- Plan rereview:
  `docs/reviews/claude-code-stage-20-plan-rereview.md`
- Final plan rereview:
  `docs/reviews/claude-code-stage-20-plan-rereview-2.md`
- Final plan result ended with `Approved for Stage 20 implementation`.
- The final Important notes were addressed in the plan before implementation:
  Pydantic match assertions use `model_dump()`, direct helper calls reject
  negative `limit`, JSON uses `model_dump_json(indent=2)`, and docs changes are
  minimal examples plus local-only boundaries.

## Files Changed

Created:

- `src/fashion_radar/imported_signals.py`
- `tests/test_imported_signals.py`
- `docs/superpowers/specs/2026-06-13-stage-20-imported-signals-review-design.md`
- `docs/superpowers/plans/2026-06-13-stage-20-imported-signals-review-plan.md`
- `docs/reviews/claude-code-stage-20-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-20-plan-review.md`
- `docs/reviews/claude-code-stage-20-plan-rereview.md`
- `docs/reviews/claude-code-stage-20-plan-rereview-2.md`
- `docs/reviews/claude-code-stage-20-code-review-prompt.md`

Modified:

- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `README.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/trend-deltas.md`
- `docs/dashboard.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

## Implementation Summary

`src/fashion_radar/imported_signals.py` adds:

- Pydantic output models:
  - `ImportedSignalMatch`
  - `ImportedSignalItem`
  - `ImportedSignalsReview`
- `query_imported_signals(...)`
  - validates `lookback_days >= 1`;
  - rejects negative `limit`;
  - parses `as_of` to UTC;
  - computes `window_start = as_of - lookback_days`;
  - returns an empty review if the database file is missing without creating
    directories;
  - opens existing databases through `create_readonly_sqlite_engine`;
  - verifies required tables, schema version, and command-required columns;
  - filters `items.source_type == "manual_import"`;
  - filters `window_start < collected_at <= as_of`;
  - optionally filters exact stored `source_name`;
  - optionally filters unmatched rows with a `NOT EXISTS`-style condition;
  - computes counts before display limit;
  - fetches matches separately to avoid one-to-many count inflation.
- `render_imported_signals_table(...)`
  - deterministic header and row order;
  - source/match counts;
  - cell sanitization replacing CR/LF with spaces and `|` with `/`.

`src/fashion_radar/cli.py` adds:

- `imported-signals --data-dir PATH`
- required command-specific `--as-of`
- `--lookback-days`, default `7`, min `1`
- `--limit`, default `50`, min `0`
- exact `--source-name`
- `--unmatched-only`
- `--format table|json`

## Scope Guard

Stage 20 did not add:

- scraping, crawling, browser automation, Playwright/Selenium, MCP platform
  scraping servers, platform APIs, account automation, login cookies, browser
  profiles, proxies, CAPTCHA/rate-limit/access-control bypass, or source export
  acquisition instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, import behavior changes, DB migrations,
  matching/scoring/report changes, dashboard writes, or digest changes;
- product-facing approval, audit, policy checklist, authorization verification,
  or legal-review workflow features.

## Verification Already Run

Focused tests:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py -q -k "imported_signals"
```

Result:

```text
28 passed, 98 deselected
```

Full tests:

```bash
.venv/bin/python -m pytest -q
```

Result:

```text
425 passed
```

Lint and format:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Results:

```text
ruff check: All checks passed.
ruff format --check: 80 files already formatted.
git diff --check: no output.
```

Docs boundary scans were run with both the focused and broad scope-guard regexes
from the implementation plan. Hits were command examples, existing negative
boundary language, or established project docs. No new Stage 20 wording
instructs source acquisition, platform automation, platform coverage, market
ranking, approval/audit/legal workflow, or bypass behavior.

No dependencies or lockfile changes were made.

## Review Request

Please review for:

1. correctness of read-only SQLite behavior and missing DB behavior;
2. correctness of time-window filtering and boundary semantics;
3. count correctness when `item_entities` has multiple rows per item;
4. schema verification and error handling;
5. deterministic table/JSON output;
6. CLI option naming/help and JSON shape;
7. no hidden writes, migrations, matching, scoring, report/dashboard writes, or
   source acquisition behavior;
8. test coverage quality;
9. documentation wording and boundary preservation.

Return findings by severity:

- Critical: must fix before release checks and upload.
- Important: should fix before release checks and upload.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 20 release checks`
- `Not approved`

Do not modify files.
