Review Stage 332 for Fashion Radar / ROW ONE.

Goal:

Render existing saved article content groups inside `articles/index.html` so
the dedicated saved article library organizes local saved bodies by read-first,
people/brands, products, and source structure. The implementation must reuse
the existing `RowOneSavedArticleContentOrganization` model, prefix
article-library links as `../details/...` only after existing safety validation,
keep homepage links as `details/...`, and leave JSON contracts unchanged.

Files and artifacts to inspect:

- `docs/superpowers/specs/2026-07-07-stage-332-row-one-saved-article-library-content-groups-design.md`
- `docs/superpowers/plans/2026-07-07-stage-332-row-one-saved-article-library-content-groups-plan.md`
- `docs/reviews/claude-code-stage-332-plan-review.md`
- `docs/reviews/opencode-stage-332-plan-review.md`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_content_organization_in_article_library tests/test_row_one_render.py::test_render_saved_article_library_filters_content_organization_links_on_library_page tests/test_row_one_render.py::test_render_saved_article_library_canonicalizes_content_organization_links tests/test_row_one_docs.py::test_row_one_docs_describe_stage_332_saved_article_library_content_groups_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page tests/test_row_one_render.py::test_render_row_one_site_includes_saved_signal_index_in_article_library tests/test_row_one_render.py::test_render_index_html_filters_saved_article_content_organization_evidence_links tests/test_row_one_render.py::test_render_row_one_site_saved_article_content_organization_links_evidence_paragraphs tests/test_row_one_saved_article_content_organization.py tests/test_row_one_docs.py::test_row_one_docs_describe_daily_saved_article_library_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Please review the uncommitted diff from `origin/main` to the working tree for:

1. Correctness of `articles/index.html` rendering and placement.
2. Route and fragment safety, including validate-then-prefix behavior and
   canonical path output.
3. Homepage behavior remaining unchanged.
4. JSON contract and generated-artifact boundaries.
5. Test adequacy and brittleness.
6. Documentation accuracy.
7. Accidental crawler, connector, schema, scheduler, extraction, ranking, LLM,
   market grouping, domestic/international classification, or compliance-review
   scope creep.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and line references where possible.
