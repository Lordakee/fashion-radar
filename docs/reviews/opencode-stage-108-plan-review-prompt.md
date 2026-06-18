# Stage 108 Plan Review Prompt

Review the Stage 108 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## Output Boundaries` section, so report/dashboard wording guidance
remains explicit about describing signals rather than certainty, safe
local-observed wording examples, and avoiding market-wide or verified-demand
claims.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-108-source-boundaries-output-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`

## Planned Test

The working tree already contains one uncommitted Stage 108 candidate test in
`tests/test_source_boundaries_docs.py`. This plan review should validate that
the current working-tree change is the right single implementation and that
Task 2 should now be treated as verify-only, not "append again". The intended
test extracts `## Output Boundaries` and asserts:

- `Reports and dashboards should describe signals, not assert certainty.`
- `Preferred wording:`
- `Mention count increased in this configured source set`
- `Needs human review`
- `Signal changed within this configured local source set`
- `Imported row platform provenance label`
- `Stored local provenance label, not platform coverage`
- `Avoid wording that implies complete market truth:`
- `This source-set signal proves external demand`
- `This celebrity caused the trend`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 108 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `README.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- dashboard, report, collector, robots/fetching, storage schema, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime wording filters, README parity checks,
robots/fetching behavior, source collection, platform search, social monitoring,
market rankings, dashboard logic, report logic, schema migrations, connector
behavior, or compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` Output Boundaries
   section without changing product behavior or docs text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Output Boundaries`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the existing
   source-boundaries docs test pattern?
4. Does the plan avoid overlap with full negative-claim scanning, heat movers,
   trend deltas, scoring, candidate discovery, dashboard/report behavior,
   package archive checks, and runtime code?
5. Are the verification commands sufficient for a docs-only guard?
6. Given the current working tree, should Task 2 explicitly say "verify the
   existing Stage 108 test body once" rather than "append" to avoid duplicate
   function definitions?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
