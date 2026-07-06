Re-review the Stage 315 implementation after fixing the prior code-review Important issue in `/home/ubuntu/fashion-radar`.

Prior review:
- `docs/reviews/claude-code-stage-315-code-review.md`

Important issue fixed:
- `_source_by_story_url_host()` no longer filters host fallback matches by `row_one_article.enabled`.
- Host fallback now matches any `source.enabled=True` source by `url` / `seed_urls` hostname, then the caller classifies that source as eligible or disabled from `source.row_one_article.enabled`.
- Added regression test:
  - `tests/test_row_one_article_readiness.py::test_article_readiness_counts_host_matched_article_disabled_source_as_disabled`

Files to review:
- `src/fashion_radar/row_one/article_readiness.py`
- `src/fashion_radar/cli.py`
- `tests/test_row_one_article_readiness.py`
- `tests/test_row_one_cli.py`
- `tests/test_config.py`
- `tests/test_row_one_docs.py`
- `tests/test_first_run_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/first-run.md`
- `docs/superpowers/specs/2026-07-06-stage-315-row-one-article-readiness-design.md`
- `docs/superpowers/plans/2026-07-06-stage-315-row-one-article-readiness-plan.md`

Verification after the fix:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_article_readiness.py::test_article_readiness_counts_host_matched_article_disabled_source_as_disabled \
  tests/test_row_one_article_readiness.py -q
```

Result: `5 passed`.

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_article_readiness.py \
  tests/test_row_one_cli.py \
  tests/test_row_one_docs.py \
  tests/test_first_run_docs.py \
  tests/test_config.py -q
```

Result: `137 passed`.

Please evaluate whether the prior Important issue is fully fixed and whether any new Critical or Important issue remains before commit.

Return findings first, ordered by severity. If no Critical/Important findings exist, say that explicitly and list Minor/Nit findings separately.
