# Stage 92 Code Review Prompt

Review the Stage 92 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 92 adds `tests/test_source_pack_quality_docs.py`, a standalone docs
drift guard for `docs/source-pack-quality.md`. It asserts the local,
read-only, non-fetching, non-data, non-demand-proof, and non-guarantee
boundaries of source-pack linting.

## Files To Review

- `tests/test_source_pack_quality_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-92-source-pack-quality-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-92-source-pack-quality-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-92-plan-review-prompt.md`
- `docs/reviews/opencode-stage-92-plan-review.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 92 plan and scope?
2. Are the docs assertions present, stable enough, and limited to source-pack
   quality boundaries?
3. Is the new standalone test independent from runtime source-pack lint tests
   and broad CLI docs tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
