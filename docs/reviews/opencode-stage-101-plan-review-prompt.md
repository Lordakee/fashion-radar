# Stage 101 Plan Review Prompt

Review the Stage 101 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/first-run.md`, scoped only to the
`## Boundary` section, so first-run docs remain documented as deterministic
local sample checks rather than live collection, platform automation, external
services, demand proof, platform coverage, or source ranking.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-101-first-run-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-101-first-run-docs-boundary-plan.md`
- `docs/first-run.md`

## Planned Test

The implementation will add `tests/test_first_run_docs.py` with one docs-only
test that extracts `## Boundary` and asserts:

- `first-run sample does not run live collection`
- `` automated smoke does not run `collect`, `run`, or `dashboard` ``
- `` should not create files under repo `data/` or `reports/` ``
- `does not perform browser automation, account login, cookies/sessions`
- `source/platform connectors, scraping, platform automation, monitoring`
- `scheduling, or external services`
- `candidate and trend outputs are local sample content checks from the checked-in example`
- `not proof of demand`
- `not platform coverage`
- `not source ranking`

## Scope Constraints

Allowed changes:

- `tests/test_first_run_docs.py`
- Stage 101 review artifacts

Disallowed changes:

- `docs/first-run.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime first-run smoke tests
- data-retention, dashboard, scheduling, architecture/source-boundary,
  source-pack, entity-pack, candidate-discovery, manual import, scoring, or
  imported-candidate behavior

Do not expand this stage into first-run smoke command changes, generated sample
data, dashboard/report behavior, scheduling, source acquisition, connector
behavior, platform search, social monitoring, compliance/audit/legal review, or
runtime validation.

## Review Questions

1. Does the plan protect a real `docs/first-run.md` local sample boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/first-run.md` and scoped narrowly
   enough to `## Boundary`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially
   dashboard, scheduling, candidate discovery, source-pack, and scoring
   boundaries?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
