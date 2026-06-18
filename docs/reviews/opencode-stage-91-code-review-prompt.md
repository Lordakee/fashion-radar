# Stage 91 Code Review Prompt

Review the Stage 91 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 91 adds `tests/test_data_retention_docs.py`, a standalone docs drift
guard for `docs/data-retention.md`. It asserts cleanup cutoff, explicit
`item_entities` pruning, dry-run reporting, non-pruned retention surfaces, and
backup guidance boundaries.

## Files To Review

- `tests/test_data_retention_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-91-data-retention-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-91-data-retention-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-91-plan-review-prompt.md`
- `docs/reviews/opencode-stage-91-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_data_retention_docs.py`
- Stage 91 review artifacts

Disallowed changes:

- `docs/data-retention.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime cleanup tests

Do not propose adding cleanup behavior, retention behavior, schema changes,
source acquisition, platform coverage, demand proof, ranking, scraping,
connectors, platform APIs, scheduling, new linter restrictions, or
compliance-review product features.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_data_retention_docs.py -q
uv --no-config run --frozen pytest tests/test_workflows.py::test_clean_old_data_prunes_by_collected_at tests/test_cli.py::test_clean_old_data_command_prunes_old_items tests/test_data_retention_docs.py -q
uv --no-config run --frozen ruff check tests/test_data_retention_docs.py
uv --no-config run --frozen ruff format --check tests/test_data_retention_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 91 plan and scope?
2. Are the docs assertions present, stable enough, and limited to data-retention
   cleanup boundaries?
3. Is the new standalone test independent from runtime cleanup behavior tests
   and broad CLI docs tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
