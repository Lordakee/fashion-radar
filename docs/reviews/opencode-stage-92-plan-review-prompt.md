# Stage 92 Plan Review Prompt

Review the Stage 92 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-92-source-pack-quality-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-92-source-pack-quality-docs-boundary-plan.md`
- Current `docs/source-pack-quality.md`
- Current `tests/test_source_packs.py`
- Current `tests/test_cli_docs.py`

## Intended Goal

Add a standalone docs drift guard for `docs/source-pack-quality.md` that pins
local/read-only linting boundaries, non-fetching behavior, JSON non-data
boundaries, no demand-proof framing, and source-availability non-guarantees
without changing docs or runtime behavior.

## Scope Constraints

Allowed changes:

- `tests/test_source_pack_quality_docs.py`
- Stage 92 review artifacts

Disallowed changes:

- `docs/source-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source-pack lint tests

Do not propose adding lint behavior, source-pack behavior, source acquisition,
source availability checks, source fetching, collection, SQLite access,
generated artifacts, schema changes, platform coverage, demand proof, ranking,
scraping, connectors, platform APIs, scheduling, new linter restrictions, or
compliance-review product features.

## Review Questions

1. Are the proposed docs assertions present in current
   `docs/source-pack-quality.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 91, 93, and 94?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
