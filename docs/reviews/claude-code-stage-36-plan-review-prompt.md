# Claude Code Stage 36 Plan Review Prompt

You are reviewing the Stage 36 report/dashboard quality plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make report output safer and more transparent, and make the local dashboard show
recent signals plus all entity-type mention tabs.

## Proposed Technical Approach

- Add a deterministic 500-character ASCII-ellipsis report snippet cap at the
  `RepresentativeItem.summary` model boundary.
- Add entity score component fields to `EntityReport`, populate them from
  `EntityHeatMetric`, and render them in Markdown.
- Add a local `recent_signals(data_dir, limit=20)` dashboard query that returns
  only local public/review fields and capped summaries.
- Render recent signals in the Daily Brief tab.
- Drive dashboard mention tabs from `EntityType` so brand, designer, celebrity,
  product, category, and trend are all covered.
- Keep Stage 36 local product-quality only: no schema migration, manual
  platform persistence, dependencies, `uv.lock`, source connectors, scraping,
  crawling, browser automation, login/cookie flows, account automation, proxy
  pools, CAPTCHA bypass, source acquisition, source ranking, demand proof,
  watchers, schedulers, or external platform API integrations.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-36-report-dashboard-quality-design.md`
- `docs/superpowers/plans/2026-06-14-stage-36-report-dashboard-quality-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 36 REPORT DASHBOARD QUALITY
```
