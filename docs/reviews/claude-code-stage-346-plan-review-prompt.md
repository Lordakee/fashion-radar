# Claude Code Stage 346 Plan Review Prompt

You are reviewing a planned development node in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Goal

Stage 346 will add a generated-site-only Saved Article Body Guide inside saved
article cards on `articles/index.html`.

## Design And Plan

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-346-saved-article-body-guide-design.md`
- `docs/superpowers/plans/2026-07-08-stage-346-saved-article-body-guide-plan.md`

## Intended Scope

- Reuse existing saved article library and saved article content-organization
  objects.
- Render up to two concise body-guide bullets inside each saved article card.
- Source guide text only from existing saved local article content already used
  by ROW ONE generated pages.
- Keep the feature generated-site-only.
- Reuse existing safe detail-path and local paragraph anchor validation.
- Avoid creating a new top-level module or duplicate dashboard section.
- Do not change app-facing contracts, schemas, JSON artifacts, route families,
  source collection, extraction, scoring, ranking, LLM, connectors, scheduling,
  deployment, market grouping, analytics, personalization, recommendation, or
  compliance-review product behavior.

## Review Questions

1. Is the scope narrow and feasible as a single Stage 346 node?
2. Does the plan preserve the generated-site-only boundary?
3. Does the plan avoid overlap with Daily Summary, Theme Digest, Reference
   Atlas, Evidence Board, Content Organization, and Organization Coverage
   Matrix?
4. Are the proposed tests sufficient for per-card rendering, placement, caps,
   dedupe, escaping, unsafe href filtering, empty omission, CSS selectors, docs,
   workflow boundaries, and artifact absence?
5. Are there any Critical or Important issues that should block implementation?

Return a concise severity-labeled review. If there are no Critical or Important
issues, state that Stage 346 is approved for implementation.
