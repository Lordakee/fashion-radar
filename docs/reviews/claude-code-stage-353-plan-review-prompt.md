# Claude Code Stage 353 Plan Review Prompt

Review the Stage 353 Saved Article Read Next Clusters plan before
implementation.

## Objective

Stage 353 should add a generated-site-only read-next cluster section inside
`articles/index.html` that groups existing saved local articles by existing
content-organization themes. It should show local article titles, source names,
body-source labels, short existing local leads, references, evidence counts,
and safe local article/detail anchors.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-353-saved-article-read-next-clusters-design.md`
- `docs/superpowers/plans/2026-07-08-stage-353-saved-article-read-next-clusters-plan.md`
- Nearby implementations:
  - `src/fashion_radar/row_one/saved_article_content_organization.py`
  - `src/fashion_radar/row_one/saved_article_reading_queue.py`
  - `src/fashion_radar/row_one/saved_article_theme_digest.py`
  - `src/fashion_radar/row_one/templates.py`

## Review Questions

1. Does the plan stay generated-site-only and avoid schemas, JSON artifacts,
   route families, app contracts, scraping, extraction, ranking, LLM calls,
   scheduling, deployment, analytics, personalization, recommendation, and
   compliance-review product behavior?
2. Are cluster inputs limited to existing saved article library entries,
   content organization cards, references, local leads, and safe local/detail
   anchors?
3. Does the plan avoid creating a ranking or recommendation surface while still
   organizing what to read next?
4. Are links constrained to safe local article page digest hrefs or safe
   same-site detail digest/content-section anchors?
5. Are tests sufficient for caps, order, dedupe, empty omission, escaping,
   homepage/detail absence, unsafe link filtering, placement, docs, and
   workflow guards?
6. Are names likely to conflict with existing reading queue, reading paths,
   theme digest, signal facets, or evidence board surfaces?

Return findings by severity. If there are no blocking issues, say the plan is
approved for implementation.
