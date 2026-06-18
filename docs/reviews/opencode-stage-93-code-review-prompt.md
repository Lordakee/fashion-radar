# Stage 93 Code Review Prompt

Review the Stage 93 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 93 adds `tests/test_scheduling_docs.py`, a standalone docs drift guard
for `docs/scheduling.md`. It asserts local serial run boundaries, local digest
handoff boundaries, and print-only `schedule-example` boundaries.

## Files To Review

- `tests/test_scheduling_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-93-scheduling-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-93-scheduling-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-93-plan-review-prompt.md`
- `docs/reviews/opencode-stage-93-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_scheduling_docs.py`
- Stage 93 review artifacts

Disallowed changes:

- `docs/scheduling.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime scheduling tests

Do not propose adding scheduling behavior, monitoring, watchers, daemon
behavior, scheduler installation, notification sending, email sending, webhook
calls, browser opening, source acquisition, schema changes, platform coverage,
demand proof, ranking, scraping, connectors, platform APIs, new linter
restrictions, or compliance-review product features.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_scheduling_docs.py -q
uv --no-config run --frozen pytest tests/test_scheduling.py tests/test_scheduling_docs.py -q
uv --no-config run --frozen ruff check tests/test_scheduling_docs.py
uv --no-config run --frozen ruff format --check tests/test_scheduling_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 93 plan and scope?
2. Are the docs assertions present, stable enough, and limited to scheduling
   boundaries?
3. Is the new standalone test independent from runtime scheduling tests and
   broad CLI docs tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
