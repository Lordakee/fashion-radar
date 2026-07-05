# Claude Code Stage 295 Code Review Prompt

Use maximum reasoning effort. Do not edit files.

Review the current uncommitted Stage 295 changes in `/home/ubuntu/fashion-radar`.

Base commit:

- `1c4a66008b95076f427c870a2f619362eee30b5d` (`Stage 294: clean row one summary display`)

Plan and prior reviews:

- `docs/superpowers/plans/2026-07-05-stage-295-row-one-editorial-briefing-depth-plan.md`
- `docs/reviews/opencode-stage-295-plan-review.md`
- `docs/reviews/opencode-stage-295-plan-rereview.md`

Changed implementation/test/doc files:

- `src/fashion_radar/row_one/render.py`
- `tests/test_row_one_briefing_topics.py`
- `tests/test_row_one_app_contract.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `docs/row-one.md`

Review artifact files are also staged for this node under `docs/reviews/`.

Implementation summary:

- Keeps `row-one-app/v7`.
- Adds topic-mix and heat-watch localized points to the existing
  `edition_brief.summary_points` array.
- Derives topic mix from existing `daily_digest.briefing_topics`.
- Derives heat watch from positive local `heat_delta` values already present in
  story payloads.
- Uses existing edition-brief HTML rendering and escaping path.
- Does not change source collection, scraping, matching, ranking, local article
  extraction, scheduler, app UI, or compliance-review behavior.

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_briefing_topics.py \
  tests/test_row_one_app_contract.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  -q
# 215 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 1953 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
# 183 files already formatted

UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages in 1ms
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
# Wrote 19 stories

rg --no-ignore -n "Topic mix|主题结构|Heat watch|升温观察" \
  reports/row-one/site/index.html reports/row-one/site/data/edition.json
# Found topic-mix and heat-watch points
```

Review questions:

1. Is the implementation correct and narrow for the Stage 295 plan?
2. Is keeping `row-one-app/v7` safe for this payload change?
3. Are HTML escaping and link safety preserved?
4. Are the tests sufficient, including the new direct `briefing_topics_payload`
   regression coverage?
5. Are any Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly.
