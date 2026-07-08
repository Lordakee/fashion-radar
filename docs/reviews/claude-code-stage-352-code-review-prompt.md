# Claude Code Stage 352 Code Review Prompt

Review the current uncommitted Stage 352 changes in `/home/ubuntu/fashion-radar`.

## Goal

Stage 352 adds a generated-site-only Saved Article Reading Queue inside
`articles/index.html`. The feature must reuse existing saved article library
entries, existing local article page hrefs, safe detail digest anchors,
body-source labels, saved paragraph counts, and organized section counts. It
must preserve existing saved article library order and must not become a
ranking, recommendation, analytics, scraping, extraction, LLM, scheduler,
deployment, schema, JSON artifact, route-family, app-contract, or
compliance-review product feature.

## Files And Artifacts To Inspect

- `docs/superpowers/specs/2026-07-08-stage-352-saved-article-reading-queue-design.md`
- `docs/superpowers/plans/2026-07-08-stage-352-saved-article-reading-queue-plan.md`
- `docs/reviews/claude-code-stage-352-plan-review-prompt.md`
- `docs/reviews/opencode-stage-352-plan-review-prompt.md`
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
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_queue.py -q
# 5 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_queue.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q -k "reading_queue or stage_352"
# 10 passed, 339 deselected

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 2408 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
# 219 files already formatted

UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
# Resolved 85 packages

git diff --check
# passed
```

## Review Questions

1. Does `build_row_one_saved_article_reading_queue(...)` preserve saved library
   order, cap at five safe entries, and omit unsafe/missing entries correctly?
2. Does the builder prefer safe local article page hrefs and safely fall back
   to canonical `../details/<safe-detail-file>.html#local-article-digest` links?
3. Does template rendering escape titles, source names, body-source labels, and
   counts, and reject outbound, protocol-relative, JavaScript, traversal,
   whitespace-bearing, empty, or wrong-fragment hrefs?
4. Is the queue rendered only in `articles/index.html`, after the Organization
   Jump Index and before Signal Facets, with no homepage/detail-page exposure?
5. Do workflow and docs guards keep this generated-site-only without schemas,
   JSON artifacts, route families, app contracts, ranking, recommendation,
   analytics, scraping, extraction, LLM, scheduler, deployment, or
   compliance-review behavior?
6. Are there brittle tests, naming conflicts with reading paths, or missing
   edge cases that should block committing?

Classify findings as Critical, Important, Minor, or None. Include concrete file
and line references where possible. If there are no Critical or Important
findings, state that the code is approved for commit.
