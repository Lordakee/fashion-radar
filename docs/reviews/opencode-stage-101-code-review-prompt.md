# Stage 101 Code Review Prompt

Review the Stage 101 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 101 adds `tests/test_first_run_docs.py`, a standalone docs drift guard for
the `## Boundary` section in `docs/first-run.md`. It asserts that first-run
docs keep the sample framed as local, deterministic content checks that do not
run live collection, `collect`, `run`, or `dashboard`; do not create repo
`data/` or `reports/` files; do not perform browser/account/platform automation
or external services; and do not claim demand proof, platform coverage, or
source ranking.

## Files To Review

- `tests/test_first_run_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-101-first-run-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-101-first-run-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-101-plan-review-prompt.md`
- `docs/reviews/opencode-stage-101-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_first_run_docs.py`
- Stage 101 review artifacts

Disallowed changes:

- `docs/first-run.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime first-run smoke tests
- data-retention, dashboard, scheduling, architecture/source-boundary,
  source-pack, entity-pack, candidate-discovery, manual import, scoring, or
  imported-candidate behavior

Do not propose first-run smoke command changes, generated sample data,
dashboard/report behavior, scheduling, source acquisition, connector behavior,
platform search, social monitoring, compliance/audit/legal review, or runtime
validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_first_run_docs.py -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_first_run_docs.py -q
uv --no-config run --frozen ruff check tests/test_first_run_docs.py
uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 101 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/first-run.md` `## Boundary` section?
3. Is the new standalone test independent from broad CLI docs tests and runtime
   first-run smoke tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
