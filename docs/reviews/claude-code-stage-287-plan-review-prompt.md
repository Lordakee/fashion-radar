# Stage 287 Plan Review Prompt

You are reviewing the Stage 287 implementation plan for Fashion Radar / ROW ONE.

## Objective

Stage 287 should add a deterministic ROW ONE `signal_synthesis` layer so app
clients and the homepage can show what brands, products, designers, and people
are rising today, instead of only showing story links/cards.

## Plan Under Review

`docs/superpowers/plans/2026-07-04-stage-287-row-one-signal-synthesis-plan.md`

## Constraints

- Read-only review. Do not edit files.
- Use maximum reasoning.
- Do not propose collectors, new social-platform integrations, LLM calls, image
  generation, new dependencies, compliance-review product features, scheduler
  changes, server/deployment changes, or scoring/ranking/story-ID changes.
- Evaluate whether the plan correctly bumps to `row-one-app/v6` for the new
  required top-level app field.
- Evaluate deterministic derivation from existing story payload fields:
  `entity_refs`, `product_refs`, `designer_refs`, `heat_delta`,
  `evidence_count`, section membership, and safe detail links.

## Review Questions

1. Is this the right next product node for the user request to organize fashion
   information rather than only links?
2. Does `signal_synthesis` correctly require a `row-one-app/v6` contract bump, and are all v6 consumers/validators covered?
3. Are the deterministic grouping and sorting rules sufficient and stable?
4. Are the schema, status/smoke validation, homepage rendering, docs, and tests
   scoped correctly?
5. Are there missing RED tests, escape tests, schema drift cases, or release
   hygiene risks?

## Output Format

Return exactly these sections:

- Verdict
- Critical Findings
- Important Findings
- Minor Findings
- Recommended Plan Changes

For each Critical or Important finding, include the file/plan section, why it
matters, and the smallest fix.
