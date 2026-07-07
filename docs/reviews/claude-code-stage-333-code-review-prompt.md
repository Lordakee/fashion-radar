Review Stage 333 for Fashion Radar / ROW ONE.

Goal:

Add a generated-site-only saved article library text-source map inside
`articles/index.html`. The implementation should reuse existing
`RowOneLocalArticle.body_source` values to show included-library body-source
counts and per-card static text-source chips for extracted article text, ROW ONE
summary fallback, and skipped saved bodies. It must not expose fallback reasons,
add new JSON artifacts, change app/runtime/manifest contracts, or change
collection, fetching, matching, extraction, scoring, ranking, LLM, connector,
scheduling, market grouping, domestic/international classification, or
compliance-review behavior.

Files and artifacts to inspect:

- `docs/superpowers/specs/2026-07-07-stage-333-row-one-saved-article-library-text-source-map-design.md`
- `docs/superpowers/plans/2026-07-07-stage-333-row-one-saved-article-library-text-source-map-plan.md`
- `docs/reviews/claude-code-stage-333-plan-review.md`
- `docs/reviews/claude-code-stage-333-plan-rereview.md`
- `docs/reviews/opencode-stage-333-plan-review.md`
- `src/fashion_radar/row_one/saved_article_library.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_library.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py::test_saved_article_library_tracks_body_source_counts_for_included_articles tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page tests/test_row_one_docs.py::test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py tests/test_row_one_render.py -q -k "saved_article_library or body_source"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Please review the uncommitted diff from `origin/main` to the working tree for:

1. Correct propagation of `body_source` into `RowOneSavedArticleLibraryEntry`.
2. Correct count semantics: included library entries, not all sidecars.
3. Correct rendering of nonzero body-source metrics and static per-card chips.
4. No fallback reason display or outbound source-link additions.
5. JSON contract and generated-artifact boundaries.
6. Test adequacy and brittleness.
7. Documentation accuracy.
8. Accidental crawler, connector, schema, scheduler, extraction, ranking, LLM,
   market grouping, domestic/international classification, or compliance-review
   scope creep.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and line references where possible.
