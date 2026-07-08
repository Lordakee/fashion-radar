# Claude Code Stage 351 Plan Review Prompt

Review the Stage 351 Saved Article Organization Jump Index plan before
implementation.

## Objective

Stage 351 should add a generated-site-only navigation index inside
`articles/index.html` that points to existing saved article organization
surfaces using safe same-page anchors.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-351-saved-article-organization-jump-index-design.md`
- `docs/superpowers/plans/2026-07-08-stage-351-saved-article-organization-jump-index-plan.md`
- Existing nearby implementations:
  - `src/fashion_radar/row_one/render.py`
  - `src/fashion_radar/row_one/templates.py`
  - `src/fashion_radar/row_one/saved_article_daily_signal_leaderboard.py`
  - `src/fashion_radar/row_one/saved_article_signal_facets.py`

## Review Questions

1. Does the plan stay generated-site-only and avoid schemas, JSON artifacts,
   route families, app contracts, scraping, extraction, ranking, LLM calls,
   scheduling, deployment, analytics, personalization, recommendation, and
   compliance-review product behavior?
2. Is the proposed data model small enough for a navigation index rather than a
   duplicated summary/ranking surface?
3. Are same-page hrefs constrained to existing saved article library anchors,
   including concrete per-source anchors instead of a non-existent aggregate
   source-route anchor?
4. Are the planned tests sufficient for caps, placement, escaping, empty
   omission, homepage absence, and generated-site-only boundary guards?
5. Should any file names, anchor names, or denial-list aliases be changed before
   implementation?

Return findings by severity. If there are no blocking issues, say the plan is
approved for implementation.
