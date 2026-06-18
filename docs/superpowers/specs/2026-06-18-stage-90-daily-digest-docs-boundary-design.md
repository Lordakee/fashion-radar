# Stage 90 Daily Digest Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/daily-digest.md` so local daily digest
documentation keeps its local-file-only, manual-review, and source-set boundary
language.

## Scope

Modify:

- `tests/test_daily_digest_docs.py`
- Stage 90 spec/plan/review artifacts

Do not modify:

- `docs/daily-digest.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- `tests/test_digests.py`
- review protocol docs/tests

## Design

Create a standalone docs-only test file that reads `docs/daily-digest.md` and
asserts short, stable phrases for:

- digest packaging reads generated Markdown/JSON report files only
- no collection, SQLite access, email sending, webhooks, browser opening, or
  daemon installation
- local `.eml` files are for manual review, have no recipient headers, and are
  never sent by Fashion Radar
- digest artifacts are generated locally inside the reports directory
- the Review Boundary section describes local observed signals, configured
  source set, imported local signals, review aids, and no demand claims outside
  that source set

Use a local `_normalized()` helper for case-insensitive whitespace-normalized
checks.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_daily_digest_docs.py -q
uv --no-config run --frozen pytest tests/test_digests.py tests/test_daily_digest_docs.py -q
uv --no-config run --frozen ruff check tests/test_daily_digest_docs.py
uv --no-config run --frozen ruff format --check tests/test_daily_digest_docs.py
```

## Boundaries

This stage is test-only. It does not add digest behavior, network behavior,
email sending, webhooks, browser automation, scheduling, source acquisition,
platform coverage, demand proof, ranking, scraping, connectors, platform APIs,
schema enums, new linter restrictions, or compliance-review product features.
