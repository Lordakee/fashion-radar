# Stage 360 Plan Review Prompt

Review the Stage 360 design and plan:

- `docs/superpowers/specs/2026-07-09-stage-360-daily-local-article-capsules-design.md`
- `docs/superpowers/plans/2026-07-09-stage-360-daily-local-article-capsules-plan.md`

Goal: add a generated-site-only `Daily Local Article Capsules` section to
`index.html`. The section should reuse current `RowOneEdition.stories`,
`local_articles_by_story_id`, already-saved local article paragraphs, existing
body-source labels, existing story/local article references, and generated local
article page routes to show compact readable article cards on the homepage.

Please evaluate:

1. Product fit with the user's request for a professional daily fashion news
   website that organizes article content locally instead of only linking out.
2. Whether homepage placement after `.daily-local-heat-signals` and before
   `.saved-article-content-organization` is technically sound.
3. Whether using `edition.stories`, `local_articles_by_story_id`, and the
   generated story-id local article page href map avoids duplicating app
   payload contracts and avoids conflict with Stage 357, Stage 358, Stage 359,
   and Saved Article Content Organization.
4. Whether the planned link safety rules are sufficient for
   `articles/<story-id>.html#local-article-digest` and
   `articles/<story-id>.html#local-article-paragraph-N`.
5. Whether paragraph excerpts, body-source labels, why-it-matters lines,
   reference chips, caps, and ordering are enough for a useful MVP without
   overbuilding.
6. Whether the plan avoids app contracts, schemas, artifacts, sidecars,
   fetching, extraction, scoring, ranking, LLM calls, connectors, scheduling,
   deployment, analytics, personalization, recommendation, translation, and
   compliance-review behavior.
7. Whether template escaping and tests are sufficient.
8. Any concrete corrections needed before implementation.
