Review Stage 335 plan for Fashion Radar / ROW ONE.

Read these files:
- docs/superpowers/specs/2026-07-08-stage-335-row-one-saved-article-reading-paths-design.md
- docs/superpowers/plans/2026-07-08-stage-335-row-one-saved-article-reading-paths-plan.md
- src/fashion_radar/row_one/detail_routes.py
- src/fashion_radar/row_one/saved_article_library.py
- src/fashion_radar/row_one/saved_article_content_organization.py
- src/fashion_radar/row_one/render.py
- src/fashion_radar/row_one/templates.py
- tests/test_row_one_render.py
- tests/test_row_one_docs.py

Goal: Stage 335 adds generated-site-only Saved Article Reading Paths to articles/index.html. It derives path cards from existing RowOneSavedArticleLibrary + RowOneSavedArticleContentOrganization, intersects cards with safe canonical saved-library detail paths, caps/dedupes steps, and renders only capped local leads/snippets plus safe generated detail anchors.

Boundaries: no app/runtime/manifest/schema/JSON contract changes, no data/saved-article-reading-paths.json, no full article publication on articles/index.html, no source fetching/extraction/scoring/ranking/LLM/connectors/scheduling/deployment/social/community/compliance-review behavior.

Please answer in this concise format:
- Verdict: Safe to implement / Needs revision
- Critical issues
- Important issues
- Minor issues
- Required plan changes before implementation

Focus on actual blockers in the plan. Do not suggest compliance-review product features.
