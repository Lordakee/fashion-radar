# Stage 95 Plan Review Prompt

Review the Stage 95 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-95-architecture-source-boundary-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-95-architecture-source-boundary-docs-plan.md`
- Current `docs/architecture.md`
- Current `docs/source-boundaries.md`
- Current `tests/test_cli_docs.py`

## Intended Goal

Add a standalone docs drift guard for the `## Source Boundary` section in
`docs/architecture.md` that pins core collector scope, local manual import
limits, non-connector/platform-collector wording, non-core platform collection
boundary, and the `source-boundaries.md` cross-link without changing docs or
runtime behavior.

## Scope Constraints

Allowed changes:

- `tests/test_architecture_boundary_docs.py`
- Stage 95 review artifacts

Disallowed changes:

- `docs/architecture.md`
- `docs/source-boundaries.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime tests

Do not propose adding source collection, collectors, manual import behavior,
external tool behavior, connectors, source acquisition, platform coverage,
demand proof, ranking, scraping, browser automation, platform APIs,
account/cookie handling, scheduling, monitoring, schema changes, dependency
changes, CI changes, new linter restrictions, or compliance-review product
features.

## Review Questions

1. Are the proposed docs assertions present in the current `## Source Boundary`
   section of `docs/architecture.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 91, 92, 93, and
   94?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
