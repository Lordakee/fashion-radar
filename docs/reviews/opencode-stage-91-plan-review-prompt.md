# Stage 91 Plan Review Prompt

Review the Stage 91 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-91-data-retention-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-91-data-retention-docs-boundary-plan.md`
- Current `docs/data-retention.md`
- Current `tests/test_workflows.py`
- Current `tests/test_cli.py`

## Intended Goal

Add a standalone docs drift guard for `docs/data-retention.md` that pins cleanup
boundaries for old `items`, explicit `item_entities` deletion, dry-run behavior,
non-pruned tables/artifacts, retained `entity_first_seen`, and backup guidance
without changing docs or runtime behavior.

## Scope Constraints

Allowed changes:

- `tests/test_data_retention_docs.py`
- Stage 91 review artifacts

Disallowed changes:

- `docs/data-retention.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime cleanup tests

Do not propose adding cleanup behavior, retention behavior, schema changes,
source acquisition, platform coverage, demand proof, ranking, scraping,
connectors, platform APIs, scheduling, new linter restrictions, or
compliance-review product features.

## Review Questions

1. Are the proposed docs assertions present in current `docs/data-retention.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 90, 92, and 93?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
