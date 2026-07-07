Review the Stage 333 plan for Fashion Radar / ROW ONE.

Files to read:

- `docs/superpowers/specs/2026-07-07-stage-333-row-one-saved-article-library-text-source-map-design.md`
- `docs/superpowers/plans/2026-07-07-stage-333-row-one-saved-article-library-text-source-map-plan.md`
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/saved_article_library.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_library.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Objective:

Add a generated-site-only saved article library text-source map inside
`articles/index.html`. The feature should reuse existing
`RowOneLocalArticle.body_source` values to render included-library counts and
per-card static text-source chips for extracted article text, ROW ONE summary
fallback, and skipped saved bodies. It must not expose fallback reasons, add
new JSON artifacts, change app/runtime/manifest contracts, or change collection,
fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling,
market grouping, domestic/international classification, or compliance-review
behavior.

Please review for:

1. Whether the Stage 333 design is coherent and scoped to the user's goal of
   organizing local article content in the ROW ONE website.
2. Whether the implementation plan is technically feasible against the current
   code after Stage 332.
3. Whether count semantics are correct: included saved article library entries,
   not all sidecars.
4. Whether the planned tests are sufficient and not brittle.
5. Whether any Critical or Important issues must be fixed before implementation.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and plan references where possible.
