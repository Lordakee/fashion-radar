# opencode Stage 300 Plan Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the Stage 300 implementation plan in:

- `docs/superpowers/plans/2026-07-05-stage-300-row-one-local-article-content-sections-plan.md`

Repository:

- `/home/ubuntu/fashion-radar`
- Current base commit: `9107e3a` (`Stage 299: add row one local article brief sections`)

Goal:

- ROW ONE should publish organized local article content, not only a brief plus
  saved paragraphs.
- Stage 300 proposes an additive `content_sections` sidecar field with typed
  items, optional `RowOneReference` references, and paragraph indices.
- The website should render these sections inside the existing local article
  block, after `brief_sections` and before saved body paragraphs.

Scope constraints:

- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not alter source extraction, social connectors, translation services, or
  deployment.
- Do not add compliance-review product behavior.
- Keep old local article constructors and old sidecars compatible through
  default-empty fields.
- Keep the current local article gate: no body paragraphs means no local article
  section and no sidecar.

Review questions:

1. Is the proposed `content_sections/items` model technically compatible with
   current `RowOneLocalArticle` and Pydantic usage?
2. Does moving `RowOneReference` earlier in `models.py` avoid forward-reference
   risk without changing behavior?
3. Are the deterministic builder helpers reasonable and free of unnecessary
   dependencies?
4. Are optional sections correctly omitted when no refs/products exist?
5. Is the render strategy correctly limited to the existing `#local-article`
   block without nav/app/edition contract changes?
6. Are the proposed tests strong enough for builder behavior, JSON persistence,
   rendering, escaping, and backward compatibility?
7. Are there Critical or Important plan issues that should be fixed before
   implementation?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 300 Plan Review`.
