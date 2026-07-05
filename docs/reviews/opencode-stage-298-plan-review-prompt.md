# opencode Stage 298 Plan Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the Stage 298 plan in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/plans/2026-07-05-stage-298-row-one-bilingual-local-article-body-plan.md`

Context:

- User wants ROW ONE to publish organized local daily fashion-news content, not
  just external links.
- Stage 297 already enriched very short local article sidecars so today's
  generated site has 18 article sidecars and none below 240 characters.
- Current gap: local article section headings are bilingual, but the local
  article body is plain/source-language text and does not participate in the
  existing English/Chinese toggle.

Planned approach:

- Add optional `paragraphs_zh: list[str] = Field(default_factory=list)` to
  `RowOneLocalArticle`.
- Populate `paragraphs_zh` from existing `RowOneStory` Chinese fields for
  ROW ONE-generated fallback/context paragraphs.
- Duplicate source-extracted paragraphs into `paragraphs_zh` when there is no
  actual Chinese translation, so Chinese mode still has readable local article
  content.
- Render bilingual paragraph spans only when `len(paragraphs_zh) ==
  len(paragraphs)`; otherwise preserve plain paragraph rendering.
- Do not add translation services, scraping, platform APIs, app UI work,
  compliance-review behavior, or schema/app contract changes.

Review questions:

1. Is the plan technically feasible with the current `RowOneLocalArticle`,
   article-builder, sidecar writer, and detail template architecture?
2. Does it preserve backward compatibility for old/legacy local articles without
   `paragraphs_zh`?
3. Are the planned tests sufficient for bilingual rendering, missing/mismatched
   Chinese paragraph lists, escaping, and article-builder population?
4. Are there any Critical or Important issues that should be fixed before
   implementation?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 298 Plan Review`.
