# Claude Code Stage 344 Code Review Prompt

Review completed Stage 344 changes in `/home/ubuntu/fashion-radar` read-only. Use maximum reasoning. Do not edit files.

## Goal

Stage 344 adds a generated-site-only Saved Article Organization Coverage Matrix inside `articles/index.html`.

## Files To Review

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-08-stage-344-saved-article-organization-coverage-matrix-design.md`
- `docs/superpowers/plans/2026-07-08-stage-344-saved-article-organization-coverage-matrix-plan.md`

## Scope

The feature must remain generated-site-only. It must not add app-facing contracts, schemas, JSON artifacts, route families, source collection, extraction, scoring, ranking, LLM calls, connectors, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

## Verification Already Passed

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> `2339 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check` -> passed
- `git diff --check` -> passed

Return concise severity-labeled findings. If there are no Critical or Important findings, state that Stage 344 is approved for commit and push.
