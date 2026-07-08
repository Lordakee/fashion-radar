# Claude Code Stage 344 Plan Review Prompt

You are reviewing a planned development node in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Goal

Stage 344 will add a generated-site-only Saved Article Organization Coverage
Matrix inside `articles/index.html`.

## Design And Plan

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-344-saved-article-organization-coverage-matrix-design.md`
- `docs/superpowers/plans/2026-07-08-stage-344-saved-article-organization-coverage-matrix-plan.md`

## Intended Scope

- Reuse existing Saved Article Content Organization groups and cards.
- Group safe organization cards by validated saved article detail page path.
- Show article-by-article coverage across organization groups.
- Show factual counts: organized sections/cards, strict evidence paragraph count,
  and capped first-seen reference chips.
- Keep the feature generated-site-only.
- Do not change app-facing contracts, schemas, JSON artifacts, route families,
  source collection, extraction, scoring, ranking, LLM, connectors, scheduling,
  deployment, market grouping, analytics, personalization, recommendation, or
  compliance-review behavior.

## Review Questions

1. Is the scope narrow and feasible as a single Stage 344 node?
2. Does the plan preserve the generated-site-only boundary?
3. Are the proposed tests sufficient for safe paths, unsafe paths, strict
   paragraph counts, dedupe, escaping, caps, docs, workflow boundaries, and
   artifact absence?
4. Is the implementation path compatible with existing renderer helpers and
   surrounding ROW ONE design?
5. Are there any Critical or Important issues that should block implementation?

Return a concise severity-labeled review. If there are no Critical or Important
issues, state that Stage 344 is approved for implementation.
