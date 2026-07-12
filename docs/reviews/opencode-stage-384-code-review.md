# Stage 384 Code Review

## Critical

None.

## Important

None.

## Minor

1. `tests/test_workflows.py` keeps the Stage 383 test name and sentinel while Stage 384 tightens the sentinel with `raising=True`; this is traceability-only and does not affect behavior.
2. `.daily-local-synthesis-brief-opening` and `.daily-local-synthesis-brief-thesis` do not receive new long-token wrapping rules; Stage 384 targets card titles, source chips, and route labels only.
3. The `.daily-local-synthesis-brief-card` `min-width: 0` CSS assertion is satisfied by a pre-existing rule; Stage 384 adds the companion `min-width: 0` rule to `.daily-local-synthesis-brief-card-meta`.

## Recommendation

Ship Stage 384 as-is after frozen gates. The changes stay within the generated-site-only boundary: renderer conditional output, CSS wrapping, workflow sentinel strictness, docs/tests, and review records only. No builder, JSON artifact, app/runtime/manifest/schema, route, source collection, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior changes were found.
