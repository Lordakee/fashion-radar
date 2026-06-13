# Claude Code Stage 24 Code Review Prompt

You are reviewing the current Fashion Radar working tree after Stage 24
implementation.

Repository: `/home/ubuntu/fashion-radar`

Review these changed/new files:

- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/cli.py`
- `tests/test_imported_review_workflow.py`
- `tests/test_cli.py`
- `README.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- Stage 24 plan/review docs under `docs/superpowers/...` and `docs/reviews/...`

Stage 24 goal:

Add `fashion-radar imported-review-workflow`, a local command that prints a
deterministic post-import review checklist for existing local Fashion Radar
commands.

Implementation summary:

- Added pure builder/renderer module with Pydantic models:
  - `ImportedReviewWorkflowStep`
  - `ImportedReviewWorkflow`
  - `build_imported_review_workflow()`
  - `render_imported_review_workflow_table()`
- Added Typer command:
  - `fashion-radar imported-review-workflow`
  - options: `--config-dir`, `--data-dir`, `--as-of`, `--source-name`,
    `--lookback-days`, `--current-days`, `--baseline-days`, `--format`.
- Added tests for deterministic steps, shell quoting, source-name behavior,
  table sanitization, CLI stable JSON keys, invalid input guards, no artifacts,
  and no data access / no execution monkeypatch guards.
- Updated docs and changelog.

Verification already run:

```bash
.venv/bin/python -m pytest tests/test_imported_review_workflow.py tests/test_cli.py -q -k "imported_review_workflow or imported_entity_deltas or imported_signals"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Review focus:

- The new command must only print suggested commands and must not execute them.
- It must not open SQLite, read configs, create artifacts, import rows, match
  rows, score entities, generate reports, schedule jobs, monitor folders, call
  platform APIs, crawl/scrape anything, or integrate externally.
- Invalid CLI inputs should fail before builder execution or data access where
  applicable.
- Shell quoting should be deterministic and copyable.
- JSON/table fields should be stable and not misleading:
  - `execution_mode` must remain `print_only`.
  - per-step `suggested_effect` must describe the printed command if the user
    later runs it.
- Docs must remain local and must not imply automation, source acquisition,
  external platform integration, ranking, coverage, source quality, audit,
  policy, authorization, or compliance workflows.
- Tests should cover the important boundaries without overfitting to internals.

Classify findings as:

- Critical: must fix before commit/push.
- Important: should fix before commit/push.
- Minor: can fix later.

Return either:

1. `APPROVED FOR COMMIT` if there are no Critical or Important issues, followed
   by any Minor notes; or
2. A findings list with severity, file/line, issue, and concrete fix.

Do not edit files.
