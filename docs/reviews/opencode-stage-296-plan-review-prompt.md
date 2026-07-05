# opencode Stage 296 Plan Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review this implementation plan for Fashion Radar:

- `docs/superpowers/plans/2026-07-05-stage-296-row-one-unique-detail-pages-plan.md`

Also consider the Claude Code attempt:

- `docs/reviews/claude-code-stage-296-plan-review.md`

Context:

- The generated ROW ONE site for `2026-07-05` currently reports `story_count=19`
  but has only `17` unique story ids/detail hrefs and `17` detail HTML files.
- Duplicate ids silently overwrite generated detail pages, which undermines the
  user's requirement that article content be downloaded locally and published in
  the webpage.
- Stage 296 proposes generation de-dupe by `story.id` plus render-time fail-fast
  for duplicate `story.id` or `detail_path`.
- Do not add compliance-review product features.
- Do not change scraping/source acquisition/deployment behavior.
- Keep generated `reports/row-one/` ignored.

Review questions:

1. Is generation de-dupe plus render fail-fast the right boundary?
2. Is preserving the first ranked story for duplicate ids technically reasonable?
3. Is a contract bump unnecessary?
4. Are the tests sufficient to prove unique local detail-page publication?
5. Are there any Critical or Important issues that must be fixed before implementation?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 296 Plan Review`.
