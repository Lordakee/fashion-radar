# opencode Stage 297 Plan Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review this implementation plan for Fashion Radar:

- `docs/superpowers/plans/2026-07-05-stage-297-row-one-short-local-article-context-plan.md`

Also consider:

- `docs/reviews/claude-code-stage-297-plan-review.md`

Context:

- The user wants article content downloaded/saved locally into the ROW ONE webpage, not just links to other websites.
- After Stage 296, today's generated site has 18 local article sidecars, but 8 have only one very short paragraph.
- Stage 297 supplements short extracted/fallback local articles with existing ROW ONE story context fields, while leaving substantial extracted articles unchanged.
- Do not add compliance-review product features.
- Do not change source collection, scraping behavior, app contract, deployment, or generated report retention.

Review questions:

1. Is supplementing only short local articles with existing story context a correct boundary?
2. Is it acceptable to keep `edition.json` unchanged and write only local article sidecars/HTML?
3. Are the RED tests sufficient?
4. Are there any Critical or Important issues before implementation?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 297 Plan Review`.
