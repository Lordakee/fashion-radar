Review and revise the Stage 332 plan for Fashion Radar / ROW ONE after Claude
Code's primary plan review.

Use model GLM 5.2 max. Read:

- `docs/reviews/claude-code-stage-332-plan-review.md`
- `docs/superpowers/specs/2026-07-07-stage-332-row-one-saved-article-library-content-groups-design.md`
- `docs/superpowers/plans/2026-07-07-stage-332-row-one-saved-article-library-content-groups-plan.md`
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`

Objective:

Stage 332 should add generated-site-only saved article content groups inside
`articles/index.html` by reusing the existing
`RowOneSavedArticleContentOrganization` model. The article-library page should
prefix already validated content-section and evidence links as
`../details/...`, while homepage links stay `details/...`.

Claude Code plan review found no Critical or Important issues and one Minor
item: make the `RowOneSavedArticleContentOrganization` import in `render.py`
mandatory in the plan. That plan update has been applied.

Please check whether any remaining plan or scope issues must be fixed before
implementation. Classify findings as Critical, Important, Minor, or None.
Focus on technical feasibility, test adequacy, generated-site-only boundaries,
and avoiding crawler/connector/schema/compliance-review scope creep.
