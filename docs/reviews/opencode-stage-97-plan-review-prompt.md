# Stage 97 Plan Review Prompt

Review the Stage 97 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-97-entity-pack-quality-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-97-entity-pack-quality-docs-boundary-plan.md`
- Current `docs/entity-pack-quality.md`
- Current `tests/test_entity_pack_lint.py`
- Current `tests/test_cli_docs.py`

## Intended Goal

Add a standalone docs drift guard for `docs/entity-pack-quality.md` that pins
local/read-only entity-pack lint boundaries, non-matching/non-scoring/non-SQLite
behavior, no source/social/page fetching/artifact creation, and no
hot-list/ranking/demand/platform/social/compliance/audit claims without
changing docs or runtime behavior.

## Scope Constraints

Allowed changes:

- `tests/test_entity_pack_quality_docs.py`
- Stage 97 review artifacts

Disallowed changes:

- `docs/entity-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime entity-pack lint tests

Do not propose adding entity-pack lint behavior, entity config behavior, runtime
matching behavior, source collection, source acquisition, social-platform
search, page fetching, SQLite inspection, report/digest/workflow artifacts,
ranking semantics, demand proof, market/platform-wide claims, schema changes,
dependency changes, CI changes, new linter restrictions, or compliance-review
product features.

## Review Questions

1. Are the proposed docs assertions present in current
   `docs/entity-pack-quality.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 91 through 96?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
