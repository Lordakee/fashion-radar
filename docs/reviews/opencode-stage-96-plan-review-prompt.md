# Stage 96 Plan Review Prompt

Review the Stage 96 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-96-entity-packs-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-96-entity-packs-docs-boundary-plan.md`
- Current `docs/entity-packs.md`
- Current `tests/test_entity_packs.py`
- Current `tests/test_cli_docs.py`

## Intended Goal

Add a standalone docs drift guard for `docs/entity-packs.md` that pins optional
local entity-pack template wording, local matching-only limits, no source or
ingestion additions, no demand/ranking/platform coverage claims, and optional
local sample boundaries without changing docs or runtime behavior.

## Scope Constraints

Allowed changes:

- `tests/test_entity_packs_docs.py`
- Stage 96 review artifacts

Disallowed changes:

- `docs/entity-packs.md`
- `configs/entity-packs/`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime entity-pack tests

Do not propose adding entity-pack behavior, entity config behavior, runtime
matching behavior, source collection, ingestion, source setup, platform or
community ingestion, scraping, social monitoring, current-hotness detection,
ranking semantics, demand proof, platform coverage verification, schema
changes, dependency changes, CI changes, new linter restrictions, or
compliance-review product features.

## Review Questions

1. Are the proposed docs assertions present in current `docs/entity-packs.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 91 through 95?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
