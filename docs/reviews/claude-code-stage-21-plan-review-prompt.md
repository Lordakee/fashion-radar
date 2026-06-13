# Claude Code Stage 21 Plan Review Prompt

You are reviewing the Stage 21 plan for `/home/ubuntu/fashion-radar` in
read-only mode. Do not edit files. Use maximum reasoning.

## Goal

Stage 21 proposes a narrow polish pass for the already shipped local read-only
`imported-signals` command:

1. Clarify the table summary label from `Matches:` to `Matched rows:`.
2. Add CLI regressions for invalid `--lookback-days 0`, `--limit -1`, and
   `--format xml`, proving validation fails before query/database access.
3. Add full CLI path coverage for a `--data-dir` containing URI-special
   characters (`? # & %`).
4. Add a direct read-only SQLite engine regression proving special-character
   paths open correctly and writes fail.
5. Update documentation examples to use the clarified table label.

## Architecture And Tech Stack

- Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, SQLite read-only URI mode,
  pytest, ruff, uv.
- No new dependencies and no lockfile changes.
- Keep the existing `ImportedSignalsReview` model and JSON output contract.
- Keep the existing query shape and CLI options.
- Change only human-readable table wording in production code unless tests
  expose a real path handling bug.

## Scope Guard

Stage 21 must not add or document:

- scraping, crawling, browser automation, Playwright/Selenium, platform APIs,
  account automation, login cookies, browser profiles, proxy pools, CAPTCHA
  bypass, rate-limit bypass, source acquisition, or platform export
  instructions;
- collectors, source types, background jobs, watch folders, schedulers,
  recursive scanning, import behavior changes, database migrations, matching
  changes, scoring changes, report generation changes, dashboard writes, or
  digest changes;
- product-facing approval, audit, policy checklist, authorization
  verification, or legal-review workflows.

Wording should remain bounded to retained local rows, imported local signals,
and stored match presence derived from `item_entities`. It should not imply
platform coverage, market-wide ranking, verified demand, real-time monitoring,
or source acquisition.

## Documents To Review

- `docs/superpowers/specs/2026-06-13-stage-21-imported-signals-polish-design.md`
- `docs/superpowers/plans/2026-06-13-stage-21-imported-signals-polish-plan.md`

These are currently planning artifacts. Stage 21 production code has not been
implemented yet.

## Review Request

Please evaluate whether the design and implementation plan are ready for
implementation. Focus on:

1. Is changing table output from `Matches:` to `Matched rows:` the right
   minimal way to clarify that counts are imported item rows with/without
   stored matches?
2. Does preserving JSON field names avoid unnecessary machine-readable
   contract churn?
3. Are the CLI validation tests sufficient to prove invalid values fail before
   query/database access?
4. Is the special-character `--data-dir` CLI test useful without duplicating the
   lower-level query test too much?
5. Is the direct read-only SQLite engine test an appropriate location for
   write-rejection and URI-special-character coverage?
6. Are the planned docs updates limited to Stage 21 artifacts, user-facing
   examples, and changelog entries, without rewriting historical Stage 20
   process docs just to change an old example?
7. Are the planned docs updates free of source-acquisition, platform coverage,
   market-wide ranking, verified demand, or audit/policy workflow claims?
8. Does the plan avoid new dependencies, DB migrations, matching/scoring
   changes, reports, dashboard writes, schedulers, watch folders, collectors,
   or platform/API integrations?
9. Are the verification commands adequate before code review, release checks,
   commit, and push?
10. Is anything missing before implementation begins?

Return findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: optional polish.

Please end with one of:

- `Approved for Stage 21 implementation`
- `Not approved`

Do not modify files.
