Review the Stage 337 plan for Fashion Radar / ROW ONE.

Goal: add a generated-site-only Saved Article Reference Atlas to `articles/index.html`, derived only from existing saved local article content-organization references.

Files to inspect:
- docs/superpowers/specs/2026-07-08-stage-337-row-one-saved-article-reference-atlas-design.md
- docs/superpowers/plans/2026-07-08-stage-337-row-one-saved-article-reference-atlas-plan.md
- src/fashion_radar/row_one/render.py
- src/fashion_radar/row_one/templates.py
- src/fashion_radar/row_one/saved_article_content_organization.py
- src/fashion_radar/row_one/saved_article_theme_digest.py
- tests/test_row_one_render.py
- tests/test_row_one_docs.py

Checklist:
1. Does the plan keep Stage 337 generated-site-only?
2. Does it avoid app/runtime/manifest/schema/JSON contract changes?
3. Does it avoid collection/fetching/extraction/scoring/ranking/LLM/connectors/scheduling/deployment/social/compliance behavior?
4. Are the planned builder inputs sufficient and not dead-coupled?
5. Are reference bucketing, dedupe, source counts, support counts, caps, and safe-route filtering technically coherent?
6. Are render ordering and tests consistent with current Stage 326-336 patterns?
7. Are test helper names and fixture assumptions compatible with the current files?
8. Identify Critical, Important, and Minor findings. If no Critical/Important issues, say Safe to implement.
