Review the Stage 350 ROW ONE Saved Article Daily Signal Leaderboard plan.

Scope:
- Generated-site-only section in `articles/index.html`.
- Aggregates Stage 349 saved article Signal Facets rows into brand, product, and theme support-count rollups.
- No raw article extraction, no external fetching, no schemas, no JSON artifacts, no app contracts, no route families, no scheduling/deployment, no ranking model, and no compliance-review product behavior.

Files to inspect:
- `docs/superpowers/specs/2026-07-08-stage-350-saved-article-daily-signal-leaderboard-design.md`
- `docs/superpowers/plans/2026-07-08-stage-350-saved-article-daily-signal-leaderboard-plan.md`
- `src/fashion_radar/row_one/saved_article_signal_facets.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`

Review questions:
1. Is the architecture the lowest-risk route for this repo?
2. Should Stage 350 be a separate builder module or an extension to Stage 349?
3. Are link safety, escaping, deterministic ordering, caps, and dedupe rules complete?
4. Are any planned tests missing?
5. Should any part of this plan be narrowed before coding?

Return findings by severity. Do not edit files.
