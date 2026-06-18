# Stage 95 Code Review Prompt

Review the Stage 95 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 95 adds `tests/test_architecture_boundary_docs.py`, a standalone docs
drift guard for the `## Source Boundary` section in `docs/architecture.md`.
It asserts core collector scope, local manual import limits, no
connector/platform collector wording, the non-core platform collection release
boundary, and the `source-boundaries.md` cross-link.

## Files To Review

- `tests/test_architecture_boundary_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-95-architecture-source-boundary-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-95-architecture-source-boundary-docs-plan.md`
- `docs/reviews/opencode-stage-95-plan-review-prompt.md`
- `docs/reviews/opencode-stage-95-plan-review.md`
- `docs/reviews/opencode-stage-95-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-95-plan-rereview.md`
- `docs/reviews/opencode-stage-95-plan-rereview-2-prompt.md`
- `docs/reviews/opencode-stage-95-plan-rereview-2.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_architecture_boundary_docs.py -q
uv --no-config run --frozen ruff check tests/test_architecture_boundary_docs.py
uv --no-config run --frozen ruff format --check tests/test_architecture_boundary_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 95 reviewed/re-reviewed plan and
   scope?
2. Are the docs assertions present, stable enough, and limited to the
   architecture Source Boundary section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
