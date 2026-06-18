# Stage 98 Code Review Prompt

Review the Stage 98 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 98 adds `tests/test_candidate_discovery_docs.py`, a standalone docs drift
guard for the `## Boundaries` section in `docs/candidate-discovery.md`. It
asserts that candidate discovery adds no collectors, no new source types, no
external inference calls, and no background network reads, and that outputs
remain observed phrases from configured sources and imported local signals that
need review.

## Files To Review

- `tests/test_candidate_discovery_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-98-candidate-discovery-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-98-candidate-discovery-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-98-plan-review-prompt.md`
- `docs/reviews/opencode-stage-98-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_candidate_discovery_docs.py`
- Stage 98 review artifacts

Disallowed changes:

- `docs/candidate-discovery.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime candidate discovery tests
- data-retention, dashboard, architecture/source-boundary, source-pack,
  entity-pack, entity-pack-quality, or imported/community candidate behavior

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py -q
uv --no-config run --frozen pytest tests/test_candidate_extraction.py tests/test_candidate_scoring.py tests/test_candidate_discovery_docs.py -q
uv --no-config run --frozen ruff check tests/test_candidate_discovery_docs.py
uv --no-config run --frozen ruff format --check tests/test_candidate_discovery_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 98 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the candidate
   discovery `## Boundaries` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   candidate discovery tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
