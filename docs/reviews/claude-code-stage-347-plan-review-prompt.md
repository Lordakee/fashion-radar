# Claude Code Stage 347 Plan Review Prompt

You are reviewing a planned development node in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Goal

Stage 347 will add a generated-site-only Saved Article Source Brief inside each
saved article source group on `articles/index.html`, plus a small
`build_row_one_saved_article_coverage()` story-id parity guard.

## Design And Plan

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-347-saved-article-source-brief-design.md`
- `docs/superpowers/plans/2026-07-08-stage-347-saved-article-source-brief-plan.md`

## Intended Scope

- Reuse existing saved article library source groups, entries, safe article
  page routes, detail anchors, and existing body-guide/content-organization
  snippets.
- Render a compact source-level explanation before each source card grid.
- Keep the feature generated-site-only.
- Fix homepage saved article coverage to skip mismatched local article sidecars
  by checking `article.story_id == story.id`.
- Do not change app-facing contracts, schemas, JSON artifacts, route families,
  source collection, extraction, scoring, ranking, LLM, connectors, scheduling,
  deployment, market grouping, analytics, personalization, recommendation, or
  compliance-review product behavior.

## Review Questions

1. Is the Stage 347 scope narrow and feasible?
2. Does the plan preserve generated-site-only boundaries?
3. Does Source Brief avoid duplicating Daily Summary, Body Guide, Coverage
   Matrix, Theme Digest, Reference Atlas, and Evidence Board?
4. Are the tests sufficient for placement, escaping, cap/dedupe, safe links,
   empty omission, coverage story-id parity, docs, workflow boundaries, and
   artifact absence?
5. Are there Critical or Important issues that should block implementation?

Return a concise severity-labeled review. If no Critical or Important issues
exist, state that Stage 347 is approved for implementation.
