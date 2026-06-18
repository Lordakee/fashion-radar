# Stage 97 Code Review Prompt

Review the Stage 97 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 97 adds `tests/test_entity_pack_quality_docs.py`, a standalone docs drift
guard for `docs/entity-pack-quality.md`. It asserts local/read-only
`entity-pack-lint` boundaries, non-matching/non-scoring/non-SQLite behavior, no
source/social/page fetching/artifact creation, and no
hot-list/ranking/demand/platform/social/compliance/audit claims.

## Files To Review

- `tests/test_entity_pack_quality_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-97-entity-pack-quality-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-97-entity-pack-quality-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-97-plan-review-prompt.md`
- `docs/reviews/opencode-stage-97-plan-review.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_pack_quality_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 97 plan and scope?
2. Are the docs assertions present, stable enough, and limited to entity-pack
   quality docs boundaries?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   entity-pack lint tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
