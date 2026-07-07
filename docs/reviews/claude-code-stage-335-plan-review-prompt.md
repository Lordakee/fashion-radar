Review the Stage 335 plan for Fashion Radar / ROW ONE.

Files to read:

- `docs/superpowers/specs/2026-07-08-stage-335-row-one-saved-article-reading-paths-design.md`
- `docs/superpowers/plans/2026-07-08-stage-335-row-one-saved-article-reading-paths-plan.md`
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `src/fashion_radar/row_one/detail_routes.py`
- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/saved_article_library.py`
- `src/fashion_radar/row_one/saved_article_content_organization.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_library.py`
- `tests/test_row_one_saved_article_content_organization.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Objective:

Stage 335 should add generated-site-only Saved Article Reading Paths inside
`articles/index.html`. The feature should organize already-saved local article
content into scan-first routes such as Read First, People & Brands, Products,
and Source Structure. It should reuse existing saved local article sidecars,
`RowOneSavedArticleLibrary`, `RowOneSavedArticleContentOrganization`, and
existing generated detail-page anchors.

Proposed architecture:

- Create private builder module:
  `src/fashion_radar/row_one/saved_article_reading_paths.py`.
- Use Python dataclasses for a generated-site-only view model:
  `RowOneSavedArticleReadingPaths`, `RowOneSavedArticleReadingPath`, and
  `RowOneSavedArticleReadingPathStep`.
- Builder input:
  `RowOneSavedArticleLibrary | None` and
  `RowOneSavedArticleContentOrganization | None`.
- Builder behavior:
  intersect content-organization cards with canonical safe saved-library detail
  paths, cap paths/steps, dedupe steps, and return `None` when no safe path is
  renderable.
- Render behavior:
  `render_row_one_site()` builds reading paths after saved article library and
  content organization, then passes them only to `_write_saved_article_library_page()`.
  `render_saved_article_library_html()` renders the section after the saved
  signal index and before saved article content organization/source-grid cards.

Tech stack and method:

- Python 3.11+ / existing ROW ONE generated-site renderer.
- Existing detail-route validation helpers in `detail_routes.py`.
- Existing static HTML templating in `templates.py`.
- pytest + Ruff.
- TDD: add failing builder/render/docs tests before implementation.
- Verification uses `UV_NO_CONFIG=1 uv --no-config run --frozen ...`.

Scope boundaries:

- No changes to `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`,
  schemas, public app payloads, generated article JSON sidecars, or new generated
  JSON artifacts.
- Do not create `data/saved-article-reading-paths.json`.
- Do not publish full articles on `articles/index.html`; render only capped
  organized leads/snippets and safe local detail links.
- Do not change source collection, fetching, matching, extraction, scoring,
  ranking, LLM behavior, connectors, scheduling, deployment, market grouping,
  domestic/international classification, social/community platform behavior, or
  compliance-review product behavior.

Please review for:

1. Whether the Stage 335 design is coherent and useful for the user's goal of
   organizing local ROW ONE fashion information rather than only listing links.
2. Whether the builder boundary and dataclasses are technically feasible against
   the current code after Stage 334.
3. Whether the safe-path intersection with saved article library entries is
   sufficient to avoid unsafe direct-render links.
4. Whether the planned render order and generated-site-only contract boundaries
   are correct.
5. Whether the planned tests cover builder behavior, unsafe href filtering,
   canonicalization, caps/dedupe, CSS, docs, and app-contract non-leakage without
   being brittle.
6. Whether any Critical or Important issues must be fixed before implementation.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and plan references where possible. Focus on actual blockers.
