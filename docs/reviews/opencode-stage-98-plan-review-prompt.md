# Stage 98 Plan Review Prompt

Review the Stage 98 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/candidate-discovery.md`, scoped only
to the `## Boundaries` section, so candidate discovery remains documented as a
local review aid with no collectors, no new source types, no external inference,
and no background network reads.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-98-candidate-discovery-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-98-candidate-discovery-docs-boundary-plan.md`
- `docs/candidate-discovery.md`

## Planned Test

The implementation will add `tests/test_candidate_discovery_docs.py` with one
docs-only test that extracts `## Boundaries` and asserts:

- `candidate discovery adds no collectors`
- `no new source types`
- `no external inference calls`
- `no background network reads`
- `configured sources and imported local signals`
- `observed phrases that need review`

## Scope Constraints

Allowed changes:

- `tests/test_candidate_discovery_docs.py`
- Stage 98 review artifacts

Disallowed changes:

- `docs/candidate-discovery.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime candidate discovery tests
- data-retention, dashboard, architecture, source-pack, entity-pack, or
  imported-candidate behavior

## Review Questions

1. Does the plan protect a real candidate-discovery docs boundary without
   changing product behavior?
2. Are the planned phrases present in `docs/candidate-discovery.md` and scoped
   narrowly enough to `## Boundaries`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially data
   retention, dashboard, architecture/source boundaries, entity packs,
   entity-pack quality, and imported/community candidate workflows?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
