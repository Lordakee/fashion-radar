# Stage 284 Plan Review Request

Please review the Stage 284 design and implementation plan in
`/home/ubuntu/fashion-radar`.

## Files To Review

- `docs/superpowers/plans/2026-07-03-stage-284-row-one-latest-report-retention-plan.md`

## Goal

Stage 284 should make `fashion-radar row-one refresh` honor ROW ONE's local
latest-only requirement for generated report artifacts: after producing the
current daily report and current ROW ONE site, stale dated
`fashion-radar-YYYY-MM-DD.md`, `.json`, and `.html` report files should be
removed from the selected reports directory.

## Current Gap

`render_row_one_site(..., latest_only=True)` already cleans the generated ROW
ONE static site directory. However, `row_one_refresh` still writes dated
Markdown, JSON, and HTML report files and leaves older dated report artifacts in
place. That conflicts with the user requirement to keep only the latest local
daily output while testing and avoiding unnecessary disk usage.

## Proposed Scope

- Add a narrow workflow helper that prunes only top-level regular files matching
  `fashion-radar-YYYY-MM-DD.(md|json|html)` for dates other than the active
  `as_of` date.
- Call that helper from `row_one_refresh` after `write_daily_report_files` and
  before ROW ONE site generation.
- Print a deterministic cleanup summary in CLI output.
- Update ROW ONE docs and reports README.
- Do not prune the SQLite database in this stage because stored item history is
  needed for scoring windows, trend deltas, and later heat movement work.

## Constraints

- Do not add source collection, scraping, platform APIs, social/community
  connectors, browser automation, login/cookie behavior, image generation,
  deployment, or timer installation.
- Do not change `row-one-app/v4`, `row-one-manifest/v1`, or
  `row-one-runtime/v1` schema shapes.
- Do not change scoring, matching, ranking, story IDs, report contents, or
  static site rendering beyond the CLI retention behavior.
- Do not prune the SQLite database in this stage.
- Keep dependency files unchanged.

## Please Evaluate

1. Is the scope tight enough for one stage?
2. Is the filename-pattern helper safe enough for a user-selected reports
   directory?
3. Is it correct to defer SQLite/database pruning until a config-aware retention
   plan exists?
4. Are the proposed tests specific enough and anchored to stable behavior?
5. Are there missing files, docs risks, CLI risks, or blockers before
   implementation?

Return:

- APPROVED or NOT APPROVED
- Findings ordered by severity with file/line references
- Required fixes before implementation
- Optional follow-ups
