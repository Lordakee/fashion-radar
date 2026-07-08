# OpenCode Stage 352 Code Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the current uncommitted Stage 352 changes in `/home/ubuntu/fashion-radar`.

## Scope

Stage 352 adds a generated-site-only Saved Article Reading Queue inside
`articles/index.html`. The feature reuses existing saved article library
entries and safe local article/detail anchors. It must not add persisted
artifacts, routes, schemas, app contracts, scraping, extraction, ranking, LLM
calls, scheduling, deployment, analytics, personalization, recommendation, or
compliance-review product behavior.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-352-saved-article-reading-queue-design.md`
- `docs/superpowers/plans/2026-07-08-stage-352-saved-article-reading-queue-plan.md`
- `src/fashion_radar/row_one/saved_article_reading_queue.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_reading_queue.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

## Expected Output

List blocking and non-blocking findings with exact file references. Focus on:

- generated-site-only boundary drift;
- unsafe href handling;
- accidental ranking or recommendation behavior;
- overlap/confusion with saved article reading paths;
- missing tests for caps, order, escaping, placement, homepage/detail absence,
  artifact denial, and contract denial.

If there are no Critical or Important findings, state that the code is approved
for commit.
