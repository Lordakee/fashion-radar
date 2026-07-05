# opencode Stage 297 Code Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the current uncommitted Stage 297 changes in `/home/ubuntu/fashion-radar`.

Base commit:

- `8c99c53061a0a91b03234e45bf2cf48292969bd0` (`Stage 296: enforce row one unique detail pages`)

Plan and prior reviews:

- `docs/superpowers/plans/2026-07-05-stage-297-row-one-short-local-article-context-plan.md`
- `docs/reviews/claude-code-stage-297-plan-review.md`
- `docs/reviews/opencode-stage-297-plan-review.md`
- `docs/reviews/opencode-stage-297-plan-rereview.md`

Changed implementation/test files:

- `src/fashion_radar/row_one/articles.py`
- `tests/test_row_one_articles.py`

Changed planning/review files:

- `docs/superpowers/plans/2026-07-05-stage-297-row-one-short-local-article-context-plan.md`
- `docs/reviews/claude-code-stage-297-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-297-plan-review.md`
- `docs/reviews/opencode-stage-297-plan-review-prompt.md`
- `docs/reviews/opencode-stage-297-plan-review.md`
- `docs/reviews/opencode-stage-297-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-297-plan-rereview.md`

Implementation summary:

- Adds `LOCAL_ARTICLE_MIN_CONTEXT_CHARS = 240`.
- Adds `_story_local_article_paragraphs(...)`, which first builds cleaned local
  article paragraphs from extracted or fallback text.
- If cleaned paragraphs are empty, the helper returns empty so extracted text
  that cleans to boilerplate falls back to the stored story summary instead of
  publishing a context-only article.
- If cleaned paragraphs are below the 240-character threshold, appends existing
  ROW ONE story context (`editorial_takeaway`, `why_it_matters`,
  `signal_context`, `reader_path`) within the source `row_one_article.max_chars`
  budget.
- Appends context after already accepted source paragraphs, so an unusable
  truncated source tail cannot block useful context.
- Leaves substantial extracted articles unchanged.
- Does not change `edition.json`, app contract version, scraping acquisition,
  source matching, rendering schema, deployment, app UI, or compliance-review
  product behavior.

Tests added/updated:

- Updated fallback-on-extractor-failure expectation to include ROW ONE context.
- Updated skipped/cleaned summary fallback expectation while preserving the
  non-mutating summary assertion.
- Added short extracted text enrichment coverage.
- Added clean-empty extracted text fallback coverage.
- Added unusable source-tail enrichment and `max_chars` cap coverage.
- Added substantial extracted text non-enrichment coverage.

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_cleans_fallback_without_mutating_story_summary \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_short_extracted_text \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text \
  -q
# RED before implementation: 3 failed, 1 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_short_extracted_text \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_falls_back_when_extracted_text_cleans_empty \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_after_unusable_source_tail \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text \
  -q
# RED for review-boundary fixes: 2 failed, 2 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
# 69 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py
# 2 files already formatted

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 1960 passed

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
# Wrote ROW ONE site: reports/row-one/site/index.html
# Wrote 18 stories
```

Sidecar proof after rebuild:

- `story_count`: 18
- `details`: 18
- `articles`: 18
- unique story ids: 18
- unique detail hrefs: 18
- paragraph count distribution: `{5: 9, 9: 1, 10: 1, 11: 1, 12: 1, 14: 1, 16: 1, 18: 1, 25: 2}`
- `short_lt240`: 0
- `one_para_short_lt240`: 0
- shortest article: 332 chars, 5 paragraphs

Review questions:

1. Does the enrichment logic preserve extracted source paragraphs and only add
   ROW ONE context when local content is short?
2. Does clean-empty extracted text correctly fall back to stored summary rather
   than using the extracted title/context-only content?
3. Does the implementation respect `row_one_article.max_chars`, including low
   budgets?
4. Are substantial extracted articles protected from unwanted enrichment?
5. Are tests sufficient for fallback, short extraction, empty cleaning,
   unusable tail, and non-enrichment boundaries?
6. Are any Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 297 Code Review`.
