# Stage 57 Plan Review Prompt

You are the local planning reviewer for `/home/ubuntu/fashion-radar`.

Model requested by the project owner: `zhipuai-coding-plan/glm-5.2`.

Do not edit files. Review these Stage 57 planning documents:

- `docs/superpowers/specs/2026-06-17-stage-57-local-heat-movers-design.md`
- `docs/superpowers/plans/2026-06-17-stage-57-local-heat-movers-plan.md`

## Project Goal

Fashion Radar is a free-first, local-first fashion intelligence tool. The user
wants daily review of fashion signals including known brands, celebrities,
designers, and emerging brands/products such as bags and shoes.

The repo currently supports local collection from configured public sources,
manual/community local imports, matching, heat scoring, reports, candidate
signals, trend deltas, dashboard views, and local handoff tools.

## Stage 57 Goal

Add a read-only `heat-movers` view that groups local `new` and `rising` tracked
entities and candidate phrases from existing trend deltas.

Recommended technical approach:

- Create `src/fashion_radar/heat_movers.py` as a pure grouping/rendering layer
  over existing `TrendComparison`.
- Add `fashion-radar heat-movers` CLI using the same local config and read-only
  SQLite trend loading flow as `trends`.
- Add a dashboard "Heat Movers" tab using the same helper and existing
  `load_trend_comparison(...)`.
- Update docs/tests/guardrails.

## Required Boundary

Stage 57 must not add:

- platform connectors
- platform APIs
- scraping/crawling
- browser automation
- login/accounts/cookies/sessions/proxies
- media downloading
- monitoring/watch loops/scheduling/notifications/webhooks
- DB schema or migration changes
- new dependencies
- report schema/template changes
- report/dashboard/config/entity artifacts
- new scoring formulas
- demand proof, platform coverage verification, market-wide or platform-wide
  popularity claims
- compliance/legal/approval/policy/authorization/safety-review features

The only acceptable behavior is a local read-only review aid over existing local
data and existing trend scoring/candidate logic.

## Review Questions

Please answer:

1. Is `heat-movers` the right next node after Stage 56 for the user's goal of
   seeing local heat changes and emerging brands/products?
2. Is a separate `heat-movers` command better than overloading `trends` with a
   mode flag in this codebase?
3. Does the proposed module boundary keep grouping/rendering pure and avoid
   database/report/source side effects?
4. Does the CLI plan correctly preserve read-only behavior, missing database
   behavior, invalid-date/config handling, and per-group limits?
5. Does the dashboard plan reuse existing read-only query behavior without
   creating new data access paths or artifacts?
6. Are docs guardrails strong enough to avoid unsupported claims like
   "hottest", "viral", "market-wide", "platform-wide", "verified demand",
   "top social trend", "coverage verification", "demand proof", and
   "source ranking"?
7. Are tests sufficient for grouping semantics, CLI behavior, dashboard
   behavior, docs drift, read-only behavior, and release hygiene?
8. Are there any missing compatibility checks for existing `trends`,
   dashboard, report, candidate, or first-run behavior?
9. Does the plan avoid dependency, lockfile, schema, or generated artifact
   churn?

## Output Format

Return:

- Critical findings
- Important findings
- Minor findings
- Answers to the review questions
- Final verdict

If there are no Critical or Important findings, include this exact approval line:

```text
APPROVED FOR STAGE 57 LOCAL HEAT MOVERS
```
