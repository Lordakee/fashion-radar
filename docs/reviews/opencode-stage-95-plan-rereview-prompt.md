# Stage 95 Plan Re-Review Prompt

Re-review the Stage 95 design and implementation plan in
`/home/ubuntu/fashion-radar` after addressing the prior Critical and Important
findings.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-95-architecture-source-boundary-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-95-architecture-source-boundary-docs-plan.md`
- `docs/reviews/opencode-stage-95-plan-review.md`
- Current `docs/architecture.md`

## Prior Findings

The first review found:

1. A Critical issue: the verification command referenced a non-existent test
   node `tests/test_cli_docs.py::test_docs_reference_existing_paths`.
2. An Important issue: the markdown section helper should use a stronger
   heading anchor pattern.

The plan has been updated to remove the broken test node, tighten the section
helper anchor, and pin the release boundary phrase to `non-core platform
collection is not part of v0.1.0`.

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

1. Are the prior Critical and Important findings resolved?
2. Are all remaining proposed docs assertions present in the current
   `## Source Boundary` section of `docs/architecture.md`?
3. Are there any remaining Critical or Important blockers before
   implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
