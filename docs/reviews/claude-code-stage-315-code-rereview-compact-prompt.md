Quick re-review for `/home/ubuntu/fashion-radar`.

Read:
- `docs/reviews/claude-code-stage-315-code-review.md`
- `src/fashion_radar/row_one/article_readiness.py`
- `tests/test_row_one_article_readiness.py`

Review only the prior Important issue:
- `_source_by_story_url_host()` previously filtered hostname fallback matches by `row_one_article.enabled`.
- Current intended behavior: fallback matches any `source.enabled=True` source by `url` / `seed_urls` hostname, then the caller classifies it as eligible or disabled from `source.row_one_article.enabled`.
- Regression test added: `test_article_readiness_counts_host_matched_article_disabled_source_as_disabled`.

Verification already run after the fix:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_article_readiness.py::test_article_readiness_counts_host_matched_article_disabled_source_as_disabled tests/test_row_one_article_readiness.py -q`
- Result: `5 passed`.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_article_readiness.py tests/test_row_one_cli.py tests/test_row_one_docs.py tests/test_first_run_docs.py tests/test_config.py -q`
- Result: `137 passed`.

Return findings first. If the prior Important issue is fixed and no new Critical/Important issue exists, say exactly that and list only Minor/Nit items.
