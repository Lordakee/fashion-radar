Review the Stage 334 plan for Fashion Radar / ROW ONE.

Files to read:

- `docs/superpowers/specs/2026-07-07-stage-334-row-one-saved-article-library-local-excerpts-design.md`
- `docs/superpowers/plans/2026-07-07-stage-334-row-one-saved-article-library-local-excerpts-plan.md`
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

Stage 334 should add generated-site-only organized local excerpts to saved
article library cards inside `articles/index.html`. The feature should reuse the
existing `RowOneSavedArticleContentOrganization` view model and mirror safe
localized organization leads into matching source-grouped saved article cards by
canonical generated detail path. It must not publish full articles on the
library index, add new JSON artifacts, change app/runtime/manifest contracts,
or change collection, fetching, matching, extraction, scoring, ranking, LLM,
connector, scheduling, market grouping, domestic/international classification,
or compliance-review behavior.

Context:

Read-only scouts also considered a larger future "Saved Article Reading Paths"
section with a new builder and cross-article routes. The Stage 334 plan
deliberately chooses the smaller template-only card-snippet step first, because
it reuses existing organized local leads and is lower risk. Please call out if
you believe this scope is technically wrong or too small for the stated user
goal.

Please review for:

1. Whether the Stage 334 design is coherent and scoped to the user's goal of
   organizing local article content in the ROW ONE website rather than only
   linking outward.
2. Whether the implementation plan is technically feasible against the current
   code after Stage 333.
3. Whether the template-only snippet lookup and detail-path matching semantics
   are safe and useful.
4. Whether the plan avoids publishing full articles on the library index and
   keeps app/schema/JSON contracts stable.
5. Whether the planned tests are sufficient and not brittle.
6. Whether any Critical or Important issues must be fixed before implementation.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and plan references where possible.
