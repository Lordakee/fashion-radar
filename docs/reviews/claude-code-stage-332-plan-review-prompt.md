Review the Stage 332 plan for Fashion Radar / ROW ONE.

Files to read:

- `docs/superpowers/specs/2026-07-07-stage-332-row-one-saved-article-library-content-groups-design.md`
- `docs/superpowers/plans/2026-07-07-stage-332-row-one-saved-article-library-content-groups-plan.md`
- `AGENTS.md`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/saved_article_content_organization.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Objective:

Add generated-site-only saved article content groups to `articles/index.html`.
The feature reuses the existing `RowOneSavedArticleContentOrganization` model
that already renders on the homepage, threads it into the dedicated saved
article library page, and prefixes already validated links as `../details/...`
for the article-library page. Homepage links must remain `details/...`.

Architecture and tech stack:

- Python 3.13
- Existing ROW ONE static site renderer
- Existing dataclass view model, no schema migration
- Existing HTML safety helpers and pytest coverage
- No new crawler, connector, scheduler, extraction, ranking, LLM, JSON contract,
  app-contract, or compliance-review functionality

Please review for:

1. Whether the Stage 332 design is coherent and scoped to the user's goal of
   organizing local article content rather than showing only links.
2. Whether the implementation plan is technically feasible against the current
   code.
3. Whether the planned link-prefix approach preserves current route and fragment
   safety.
4. Whether the tests are sufficient and not brittle.
5. Whether any Critical or Important issues must be fixed before implementation.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and plan references where possible.
