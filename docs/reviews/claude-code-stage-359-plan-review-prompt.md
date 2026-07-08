# Stage 359 Plan Review Prompt

Review the Stage 359 design and plan:

- `docs/superpowers/specs/2026-07-08-stage-359-daily-local-heat-signals-design.md`
- `docs/superpowers/plans/2026-07-08-stage-359-daily-local-heat-signals-plan.md`

Goal: add a generated-site-only `Daily Local Heat Signals` section to
`index.html`. The section should reuse existing
`app_payload["daily_digest"]["briefing_topics"]` heat fields
(`positive_heat_delta_sum` and `max_heat_delta`), existing topic `source_refs`,
current `local_articles_by_story_id` availability, and a generated local article
page href map to show current-edition heated brands/products that have saved
local article text. It should not create historical trend deltas or any new
app/data contract.

Please evaluate:

1. Product fit with the user's request for organized daily fashion information,
   brand heat changes, and newly hot brands/products/shoes/bags.
2. Whether reusing `daily_digest.briefing_topics` avoids duplicating topic heat
   aggregation and avoids conflict with Daily Edit, Signal Synthesis, Stage 357
   Daily Local Key Signals Digest, and Stage 358 Daily Local Signal Momentum.
3. Whether homepage placement after `.daily-local-signal-momentum` and before
   `.saved-article-content-organization` is technically sound.
4. Whether local article gating from `local_articles_by_story_id` plus the
   generated local article page href map is sufficient for a homepage section
   that should link to saved local article pages.
5. Whether the planned safe story-id-to-local-article page href validation is
   adequate for `articles/<story-id>.html#local-article-digest`.
6. Whether the plan avoids app contracts, schemas, artifacts, sidecars,
   fetching, extraction, scoring, ranking, LLM calls, connectors, scheduling,
   deployment, analytics, personalization, recommendation, and
   compliance-review behavior.
7. Whether template escaping and tests are sufficient.
8. Any concrete corrections needed before implementation.
