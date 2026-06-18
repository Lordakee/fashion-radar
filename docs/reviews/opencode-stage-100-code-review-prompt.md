# Stage 100 Code Review Prompt

Review the Stage 100 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 100 adds `tests/test_source_packs_docs.py`, a standalone docs drift guard
for the `## Public Fashion Pack` section in `docs/source-packs.md`. It asserts
the starter pack path, existing v0.1.0 source types (`rss` and `gdelt`),
conservative RSS/bounded GDELT language, configured-source-set framing, and the
explicit exclusion of Google News RSS, Google Trends, account-based access,
browser automation, access-control bypasses, paywall bypass, and private data
collection.

## Files To Review

- `tests/test_source_packs_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-100-source-packs-public-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-100-source-packs-public-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-100-plan-review-prompt.md`
- `docs/reviews/opencode-stage-100-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_packs_docs.py`
- Stage 100 review artifacts

Disallowed changes:

- `docs/source-packs.md`
- `configs/source-packs/`
- `docs/source-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source-pack tests
- data-retention, dashboard, architecture/source-boundary, entity-pack,
  entity-pack-quality, candidate-discovery, manual import, source-pack-quality,
  scheduling, or imported-candidate behavior

Do not propose source-pack lint quality, source availability, article
extraction, source acquisition, connector behavior, platform search, social
monitoring, compliance/audit/legal review, or runtime validation changes.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 100 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-packs.md` `## Public Fashion Pack` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   source-pack tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
