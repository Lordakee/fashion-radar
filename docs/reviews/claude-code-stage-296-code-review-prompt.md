# Claude Code Stage 296 Code Review Prompt

Use maximum reasoning effort. Do not edit files.

Review the current uncommitted Stage 296 changes in `/home/ubuntu/fashion-radar`.

Base commit:

- `18f02dc1b6e28b17f4c0b46c894cdc356f626f4b` (`Stage 295: deepen row one editorial briefing`)

Plan and prior reviews:

- `docs/superpowers/plans/2026-07-05-stage-296-row-one-unique-detail-pages-plan.md`
- `docs/reviews/opencode-stage-296-plan-review.md`

Changed implementation/test files:

- `src/fashion_radar/row_one/edition.py`
- `src/fashion_radar/row_one/render.py`
- `tests/test_row_one_edition.py`
- `tests/test_row_one_render.py`

Implementation summary:

- Adds `_unique_stories_by_id(...)` in ROW ONE edition generation.
- Applies per-section de-dupe before section caps and a final invariant guard
  after optional `max_stories`.
- Adds render-time `_validate_unique_story_routes(...)` and calls it before
  cleaning or writing generated site files.
- Adds tests for duplicate candidate story ids, duplicate rendered story ids,
  and distinct story ids sharing one detail path.
- Does not change app schema, app version, scraping, matching, ranking scoring,
  local article extraction, deployment, app UI, or compliance-review behavior.

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_edition.py \
  tests/test_row_one_render.py \
  tests/test_row_one_app_contract.py \
  -q
# 216 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 1956 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
# 183 files already formatted

UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages
```

Generated-site verification:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
# Wrote 18 stories
```

Count proof after rebuild:

- `story_count`: 18
- `len(stories)`: 18
- unique story ids: 18
- unique detail hrefs: 18
- `details/*.html`: 18
- `data/articles/*.json`: 18
- duplicate ids/hrefs: none

Review questions:

1. Is generation de-dupe correct and deterministic?
2. Is render fail-fast placed early enough to avoid partial output?
3. Are app contract and existing rendering behavior preserved?
4. Are tests sufficient for the duplicate-id and duplicate-detail-path cases?
5. Are any Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly.
