# Stage 317 Plan Review Prompt

Review these two files in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-07-06-stage-317-row-one-detail-saved-paragraph-previews-design.md`
- `docs/superpowers/plans/2026-07-06-stage-317-row-one-detail-saved-paragraph-previews-plan.md`

Stage 317 goal: add generated-site detail-page saved paragraph previews inside
organized local article content items, so readers landing from Stage 316 homepage
links see source paragraph snippets inline.

Required boundaries:

- presentation-only generated HTML/CSS behavior
- reuse existing `data/articles/<story-id>.json` sidecars, saved local
  paragraphs, `content_sections`, detail routes, and paragraph anchors
- no changes to `row-one-app/v7`, `data/edition.json`,
  `row-one-manifest/v1`, `data/manifest.json`, `row-one-runtime/v1`,
  `data/runtime.json`, schemas, source collection, extraction, scoring,
  connectors, LLM calls, or compliance-review behavior
- no new JSON artifact

Please check:

- whether this is a reasonable next node after Stage 316
- whether the touched files and test plan are scoped correctly
- whether the plan proves rendering, filtering, escaping, bilingual behavior,
  caps, anchor behavior, and generated-contract boundaries
- whether anything must be fixed before implementation

Return only:

- Critical findings
- Important findings
- Minor findings
- Final recommendation

If there are no Critical or Important findings, say so clearly.
