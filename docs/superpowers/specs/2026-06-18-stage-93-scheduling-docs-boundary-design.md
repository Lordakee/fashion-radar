# Stage 93 Scheduling Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/scheduling.md` so the scheduling
documentation keeps its local, serial, print-only, and manual-review
boundaries.

## Scope

Modify:

- `tests/test_scheduling_docs.py`
- Stage 93 spec/plan/review artifacts

Do not modify:

- `docs/scheduling.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime scheduling tests

## Design

Create a standalone docs-only test file that reads `docs/scheduling.md`,
normalizes whitespace/case, and asserts stable phrases for:

- Fashion Radar not running a background daemon
- scheduled usage delegating to the existing serial `run` command
- `run` executing `collect -> match -> report` in one local process
- no overlapping scheduled runs against the same SQLite database
- local digest artifacts remaining local and non-notifying
- `.eml` being a local handoff reviewed by the user
- `schedule-example` printing snippets and not installing anything

The test should not import application modules, inspect scheduler renderers,
touch SQLite, install scheduler entries, or execute CLI commands.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_scheduling_docs.py -q
uv --no-config run --frozen pytest tests/test_scheduling.py tests/test_scheduling_docs.py -q
uv --no-config run --frozen ruff check tests/test_scheduling_docs.py
uv --no-config run --frozen ruff format --check tests/test_scheduling_docs.py
```

## Boundaries

This stage is test-only. It does not add scheduling behavior, monitoring,
watchers, daemon behavior, scheduler installation, notification sending,
email sending, webhook calls, browser opening, source acquisition, schema
changes, platform coverage, demand proof, ranking, scraping, connectors,
platform APIs, new linter restrictions, or compliance-review product features.
