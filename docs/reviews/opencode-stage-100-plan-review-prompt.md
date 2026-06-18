# Stage 100 Plan Review Prompt

Review the Stage 100 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/source-packs.md`, scoped only to the
`## Public Fashion Pack` section, so the starter pack remains documented as
using existing public source types and excluding unsupported acquisition
categories.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-100-source-packs-public-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-100-source-packs-public-docs-boundary-plan.md`
- `docs/source-packs.md`

## Planned Test

The implementation will add `tests/test_source_packs_docs.py` with one
docs-only test that extracts `## Public Fashion Pack` and asserts:

- `configs/source-packs/fashion-public.example.yaml`
- `it uses only existing v0.1.0 source types`
- `` `rss` ``
- `` `gdelt` ``
- `keeps the rss entries conservative`
- `bounded gdelt lanes`
- `inside the configured source set`
- `it does not include google news rss, google trends, account-based source access, browser automation, access-control bypasses, paywall bypass, or private data collection.`

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

Do not expand this stage into source-pack lint quality, source availability,
article extraction, source acquisition, connector behavior, platform search,
social monitoring, compliance/audit/legal review, or runtime validation.

## Review Questions

1. Does the plan protect a real `docs/source-packs.md` public starter-pack
   boundary without changing product behavior?
2. Are the planned phrases present in `docs/source-packs.md` and scoped narrowly
   enough to `## Public Fashion Pack`?
3. Does the plan avoid overlap with recent docs-boundary stages, especially
   Stage 92 source-pack quality and Stage 95 architecture/source boundaries?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
