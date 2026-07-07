Review and revise the Stage 333 plan for Fashion Radar / ROW ONE after Claude
Code's primary plan review and rereview.

Use model GLM 5.2 max. Read:

- `docs/reviews/claude-code-stage-333-plan-review.md`
- `docs/reviews/claude-code-stage-333-plan-rereview.md`
- `docs/superpowers/specs/2026-07-07-stage-333-row-one-saved-article-library-text-source-map-design.md`
- `docs/superpowers/plans/2026-07-07-stage-333-row-one-saved-article-library-text-source-map-plan.md`
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `src/fashion_radar/row_one/saved_article_library.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_library.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`

Objective:

Stage 333 should add a generated-site-only saved article library text-source map
inside `articles/index.html`. It reuses existing
`RowOneLocalArticle.body_source` values to show included-library counts and
per-card static text-source chips for extracted article text, ROW ONE summary
fallback, and skipped saved bodies. It must not expose fallback reasons, add new
JSON artifacts, change app/runtime/manifest contracts, or change collection,
fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling,
market grouping, domestic/international classification, or compliance-review
behavior.

Claude Code's Important plan finding about transient dataclass fixture failures
has been fixed and rereviewed as closed. Remaining Claude findings are Minor:
add end-to-end render coverage for the extracted chip and homepage metric if
convenient.

Please check whether any remaining plan or scope issues must be fixed before
implementation. Classify findings as Critical, Important, Minor, or None.
