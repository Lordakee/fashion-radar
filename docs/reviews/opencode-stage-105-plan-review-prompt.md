# Stage 105 Plan Review Prompt

Review the Stage 105 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/trend-deltas.md`, scoped only to the
`## What Is Compared` section, so trend-delta comparison guidance remains
explicit about local heat scoring reuse, candidate discovery snapshot reuse,
configured candidate-discovery thresholds, current-window mention fields,
separate internal baseline-window fields, and local observed review statuses
rather than market-wide rankings.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-105-trend-deltas-what-compared-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-105-trend-deltas-what-compared-docs-plan.md`
- `docs/trend-deltas.md`

## Planned Test

The implementation will add `tests/test_trend_deltas_docs.py` with one
docs-only test that extracts `## What Is Compared` and asserts:

- `Entity deltas reuse the same local heat scoring used by reports.`
- `Candidate deltas reuse candidate discovery snapshots.`
- `configured `candidate_discovery` settings`
- `not a complete raw phrase inventory.`
- `` `current_mentions` is the current comparison snapshot's current-window mention count. ``
- `` `baseline_mentions` is the baseline comparison snapshot's current-window mention count. ``
- `` Scoring's internal baseline-window counts are exposed only as `current_internal_baseline_mentions` and `baseline_internal_baseline_mentions`. ``
- `` Existing signals are labeled `rising` or `cooling` only when score and mention movement agree. ``
- `` Mixed-direction movement is `stable`. ``
- `These statuses are local observed signals for review, not market-wide rankings.`

## Scope Constraints

Allowed changes:

- `tests/test_trend_deltas_docs.py`
- Stage 105 review artifacts

Disallowed changes:

- `docs/trend-deltas.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- scoring, candidate discovery, heat movers, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime scoring checks, source collection,
platform search, social monitoring, market rankings, dashboard logic, report
logic, schema migrations, connector behavior, or compliance features.

## Review Questions

1. Does the plan protect a real `docs/trend-deltas.md` comparison boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/trend-deltas.md` and scoped narrowly
   enough to `## What Is Compared`?
3. Does the plan avoid overlap with CLI usage examples, manual signals,
   dashboard behavior, scoring implementation, and candidate discovery logic?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
