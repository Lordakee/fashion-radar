# Claude Code Stage 345 Plan Review Prompt

You are reviewing a planned development node in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Goal

Stage 345 will add a generated-site-only Saved Article Daily Summary section
inside `articles/index.html`.

## Design And Plan

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-345-saved-article-daily-summary-design.md`
- `docs/superpowers/plans/2026-07-08-stage-345-saved-article-daily-summary-plan.md`

## Intended Scope

- Reuse existing saved article library groups and existing generated-page
  article-library surfaces.
- Show compact factual orientation metrics and quick links to existing sections.
- Keep the feature generated-site-only.
- Avoid duplicating theme leads, paragraph excerpts, reference buckets, coverage
  matrix rows, or content organization cards.
- Do not change app-facing contracts, schemas, JSON artifacts, route families,
  source collection, extraction, scoring, ranking, LLM, connectors, scheduling,
  deployment, market grouping, analytics, personalization, recommendation, or
  compliance-review behavior.

## Review Questions

1. Is the scope narrow and feasible as a single Stage 345 node?
2. Does the plan preserve the generated-site-only boundary?
3. Does the plan avoid overlap with Theme Digest, Reference Atlas, Evidence
   Board, Content Organization, and Organization Coverage Matrix?
4. Are the proposed tests sufficient for ordering, safe links, empty omission,
   escaping, CSS selectors, docs, workflow boundaries, and artifact absence?
5. Are there any Critical or Important issues that should block implementation?

Return a concise severity-labeled review. If there are no Critical or Important
issues, state that Stage 345 is approved for implementation.
