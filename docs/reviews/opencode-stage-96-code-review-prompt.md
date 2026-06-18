# Stage 96 Code Review Prompt

Review the Stage 96 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 96 adds `tests/test_entity_packs_docs.py`, a standalone docs drift guard
for `docs/entity-packs.md`. It asserts optional local template wording, local
matching-only limits, no source/ingestion/live collection additions, no
demand/ranking/platform coverage claims, and optional local sample boundaries.

## Files To Review

- `tests/test_entity_packs_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-96-entity-packs-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-96-entity-packs-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-96-plan-review-prompt.md`
- `docs/reviews/opencode-stage-96-plan-review.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_entity_packs_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_packs.py tests/test_entity_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_packs_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 96 plan and scope?
2. Are the docs assertions present, stable enough, and limited to entity-pack
   docs boundaries?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   entity-pack tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
