# Stage 102 Code Review Prompt

Review the Stage 102 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 102 adds `tests/test_scoring_docs.py`, a standalone docs drift guard for
the `## Limits` section in `docs/scoring.md`. It asserts that scoring,
candidate signals, and trend deltas remain framed as configured-source and
imported-local-signal views; counts use collected time rather than necessarily
publication time; dashboard/candidate views have their documented data-source
boundary; and v0.1.0 does not include image/video or external engagement
analysis.

## Files To Review

- `tests/test_scoring_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-102-scoring-docs-limits-design.md`
- `docs/superpowers/plans/2026-06-18-stage-102-scoring-docs-limits-plan.md`
- `docs/reviews/opencode-stage-102-plan-review-prompt.md`
- `docs/reviews/opencode-stage-102-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_scoring_docs.py`
- Stage 102 review artifacts

Disallowed changes:

- `docs/scoring.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime scoring, candidate discovery, trend delta, report, dashboard, or CLI
  tests

Do not propose scoring algorithm changes, generated data, dashboard/report
behavior, scheduling, source acquisition, connector behavior, platform search,
social monitoring, compliance/audit/legal review, or runtime validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_scoring_docs.py -q
uv --no-config run --frozen pytest tests/test_scoring.py tests/test_candidate_scoring.py tests/test_trends.py tests/test_scoring_docs.py -q
uv --no-config run --frozen ruff check tests/test_scoring_docs.py
uv --no-config run --frozen ruff format --check tests/test_scoring_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 102 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/scoring.md` `## Limits` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   scoring/trend tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
