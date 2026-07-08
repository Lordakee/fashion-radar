# Claude Code Stage 352 Plan Review Prompt

Review the Stage 352 Saved Article Reading Queue plan before implementation.

## Objective

Stage 352 should add a generated-site-only reading queue inside
`articles/index.html` that links to existing safe local article page hrefs or
same-site detail digest anchors.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-352-saved-article-reading-queue-design.md`
- `docs/superpowers/plans/2026-07-08-stage-352-saved-article-reading-queue-plan.md`
- Nearby implementations:
  - `src/fashion_radar/row_one/templates.py`
  - `src/fashion_radar/row_one/saved_article_library.py`
  - `src/fashion_radar/row_one/saved_article_organization_jump_index.py`

## Review Questions

1. Does the plan stay generated-site-only and avoid schemas, JSON artifacts,
   route families, app contracts, scraping, extraction, ranking, LLM calls,
   scheduling, deployment, analytics, personalization, recommendation, and
   compliance-review product behavior?
2. Are queue links constrained to existing safe local article page hrefs or safe
   same-site detail digest anchors?
3. Does the queue preserve existing library order rather than creating a ranking
   or recommendation surface?
4. Are tests sufficient for caps, empty omission, escaping, homepage/detail
   absence, unsafe link filtering, placement, docs, and workflow guards?
5. Are any names likely to conflict with existing Stage 341 reading-improvement
   terminology?

Return findings by severity. If there are no blocking issues, say the plan is
approved for implementation.
