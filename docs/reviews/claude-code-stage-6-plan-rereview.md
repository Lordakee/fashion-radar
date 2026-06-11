# Claude Code Stage 6 Plan Rereview

Base: `3d97313 feat: add stage 5 cli and dashboard workflow`, plus uncommitted
Stage 6 plan-review records and plan updates only.

## Summary

Claude Code rereviewed the Stage 6 plan after the fixes applied in response to
`docs/reviews/claude-code-stage-6-plan-review.md`. Both Important findings are
now resolved in the plan text and task list, and all four Minor items are
folded in. The plan remains scoped to documentation, CI, hygiene, and GitHub
readiness; it does not introduce social scraping or any risky connector work.
The repository state matches the plan's assumptions: the referenced modules
(`fashion_radar.dashboard.app`, `fashion_radar.dashboard.queries`) and the
packaged template `fashion_radar.templates/daily_report.md` all exist, and the
`dashboard` optional extra is defined in `pyproject.toml`.

## 1. Are the previous Important findings fixed?

Yes.

- **Dashboard extra resolution/import smoke (Important #1).** Fixed. The
  CI/package contract now requires Stage 6 verification to resolve/install the
  `dashboard` extra and import `fashion_radar.dashboard.app` and
  `fashion_radar.dashboard.queries` without launching Streamlit. A matching
  task ("Run a dashboard extra smoke...") is added to the task list. The named
  modules exist on disk, so the smoke is implementable as written.

- **Packaged `daily_report.md` verification (Important #2).** Fixed. The
  CI/package contract now requires the installed-wheel check to explicitly
  verify `fashion_radar.templates/daily_report.md`, either via report smoke or
  `importlib.resources`. A matching task ("Run an installed-wheel
  packaged-resource smoke...") is added. The template exists in the package
  tree.

All four Minor items are also addressed:

- Planned-files list now reuses `docs/REVIEW_PROTOCOL.md` and
  `docs/dependency-mirrors.md` instead of `docs/review-workflow.md`, and tasks
  say "Update" rather than "Write" for README, source-boundaries, and the
  review-workflow doc where files already exist.
- The hygiene audit task and contract now name `AGENTS.md`, `.mcp.json`,
  `.claude/settings.json`, and `.codegraph/.gitignore` for a secrets/absolute-path
  check.
- Scoring known-limits now require documenting omitted `current_mentions == 0`
  entities and the redundant `stable` fallback.

## 2. Remaining blockers before Stage 6 implementation?

None at Critical or Important severity.

## 3. Is the plan still safely scoped?

Yes. Stage 6 is limited to README/docs, architecture/scoring/retention docs,
hygiene audit, CI/package smoke checks, issue/PR templates, and preparing for
user-controlled remote creation. The publishing boundary explicitly forbids
creating a remote, pushing, or publishing to PyPI without explicit user action,
and the source-boundary documentation continues to mark Instagram/TikTok/X/
Xiaohongshu scraping, login cookies, proxy/account pools, CAPTCHA/paywall
bypass, and private data collection as out of scope. No social-scraping
implementation is introduced.

## Findings

### Critical

None.

### Important

None.

### Minor

1. **`docs/architecture.md`, `docs/scoring.md`, and `docs/data-retention.md`
   do not yet exist.** This is expected (they are net-new Stage 6 docs), so the
   plan correctly says "Write" for them. No action needed before implementation;
   noted only so the implementer treats these as new files and the README/
   source-boundaries/REVIEW_PROTOCOL files as updates.

## Verdict

**Approved for Stage 6 implementation.**

Both Important findings from the prior review are resolved, no Critical or
Important blockers remain, and the plan is safely scoped to docs/CI/GitHub
readiness. Handle the single Minor note opportunistically while writing docs.
