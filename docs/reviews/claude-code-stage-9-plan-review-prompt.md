# Claude Code Stage 9 Plan Review Prompt

You are reviewing the Stage 9 plan for Fashion Radar. Run this as a read-only
architecture and implementation-plan review. Do not edit files, do not run
collectors, do not call the network, and do not execute platform tooling.

Use maximum reasoning effort. The invoking command must be:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-9-plan-review-prompt.md
```

## Goal

Stage 9 adds optional offline import of user-provided local CSV/JSON signal
files. Imported rows should enter the existing local SQLite item store so the
current match, report, candidate, and dashboard workflows can include the rows
after the user explicitly imports them.

## Architecture

- Add `SourceType.MANUAL_IMPORT = "manual_import"` as a provenance label.
- Reject `manual_import` in `sources.yaml`; it is import-only and must not be a
  configured collector source.
- Create a focused importer package under `src/fashion_radar/importers/`.
- Parse CSV/JSON with Python standard-library `csv` and `json`.
- Validate all rows before opening any write path.
- Store only sanitized item metadata in the existing `items` table with existing
  normalized-URL upsert semantics.
- Do not add a schema migration, collector, source pack, source health record,
  run history record, scheduler integration, or dashboard collection action.
- `--dry-run` should validate and print counts without initializing the
  database, creating `data_dir`, or writing rows.

## Tech Stack

- Python 3.11+
- Pydantic models and validators
- Typer CLI
- Existing SQLAlchemy repository and SQLite schema
- pytest and ruff
- uv for environment, lock, and build verification

## Files To Review

- `docs/superpowers/specs/2026-06-12-stage-9-manual-signal-import-design.md`
- `docs/superpowers/plans/2026-06-12-stage-9-manual-signal-import-plan.md`
- Existing integration points:
  - `src/fashion_radar/models/source.py`
  - `src/fashion_radar/models/item.py`
  - `src/fashion_radar/db/repositories.py`
  - `src/fashion_radar/cli.py`
  - `src/fashion_radar/workflows.py`
  - `tests/test_models.py`
  - `tests/test_cli.py`

## Explicit Out Of Scope

Stage 9 must not add or document:

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

## Review Questions

Please review for:

1. Whether the plan satisfies the goal without accidentally adding a collector
   or platform acquisition workflow.
2. Whether `manual_import` can be added safely without confusing configured
   source collection.
3. Whether the parser/validator tests are specific enough to drive a correct
   implementation.
4. Whether the CLI dry-run semantics are precise enough to prevent database or
   directory creation.
5. Whether the docs plan uses safe wording and avoids platform completeness
   claims.
6. Whether the verification plan is sufficient before code review and GitHub
   publication.

## Response Format

Start with one of:

- `Approved for Stage 9 implementation`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before implementation.
- `Important:` issues that should be fixed before implementation.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
