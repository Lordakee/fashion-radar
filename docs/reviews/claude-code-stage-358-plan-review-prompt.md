# Stage 358 Plan Review Prompt

Review the Stage 358 design and plan:

- `docs/superpowers/specs/2026-07-08-stage-358-daily-local-signal-momentum-design.md`
- `docs/superpowers/plans/2026-07-08-stage-358-daily-local-signal-momentum-plan.md`

Goal: add a generated-site-only `Daily Local Signal Momentum` section to
`index.html`. The section should reuse existing Stage 350
`RowOneSavedArticleDailySignalLeaderboard` data to show current-edition saved
local brands, products, and themes by article/source support counts. It should
not create historical trend deltas or any new app/data contract.

Please evaluate:

1. Product fit with the user's request for organized daily fashion information,
   brand/product heat, and what is currently concentrated in saved local
   sources.
2. Whether reusing Stage 350 leaderboard data avoids duplicating aggregation
   logic and avoids conflict with Stage 357 Daily Local Key Signals Digest.
3. Whether homepage placement after `.daily-local-key-signals-digest` and
   before `.saved-article-content-organization` is technically sound.
4. Whether the plan avoids app contracts, schemas, artifacts, sidecars,
   fetching, extraction, scoring, ranking, LLM calls, connectors, scheduling,
   deployment, analytics, personalization, recommendation, and
   compliance-review behavior.
5. Whether the planned safe detail-path-to-local-article-page href mapping is
   adequate given that `index.html` is written before `articles/<story-id>.html`
   files.
6. Whether template href validation and tests are sufficient.
7. Any concrete corrections needed before implementation.
