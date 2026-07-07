# Stage 337 Code Review - Saved Article Reference Atlas

## Critical

None.

## Important

None.

## Resolved Review Item

The earlier bucket-alias concern is resolved. The Stage 337 spec now documents
the accepted brand, people, and product aliases, plus the Source Context fallback
for every other non-empty reference with non-empty metadata. The builder tests
cover alias routing, fallback behavior, canonical bucket order, support caps,
dedupe behavior, first non-empty metadata backfill, and unsafe local-link
rejection.

## Release Notes

- The feature remains generated-site-only and renders on `articles/index.html`.
- No app, runtime, manifest, schema, JSON artifact, collection, fetching,
  extraction, scoring, LLM, connector, social, scheduling, deployment, or
  compliance-review behavior is added.
- Support links stay local to saved article detail pages and content-section
  fragments.

## Verification

- Focused Stage 337 tests passed in prior review.
- Full repository verification is run by the release gate before commit.
