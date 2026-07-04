# Claude Code Stage 290 Plan Review Prompt

Review this implementation plan:

`docs/superpowers/plans/2026-07-04-stage-290-row-one-card-information-sections-plan.md`

Context:
- Repo: `/home/ubuntu/fashion-radar`
- Product: ROW ONE daily fashion intelligence static site and app JSON payload.
- User goal: the app should show organized fashion information, not just links.
- Stage 289 added `signal_synthesis.groups[].signals[].story_refs` and pushed commit `e0da959`.
- Proposed Stage 290 adds ordered `information_sections` to every app `contentCard` so app clients can render display-ready story information panels from existing localized story fields.
- Constraints: no dependency changes, no generated report artifacts, no collection/scraping/platform API work, no matching/scoring/ranking/sorting/story-ID changes, no LLM/image generation, no deployment automation, no compliance-review product feature.

Please evaluate:
1. Is `contentCard.information_sections` the right next low-risk information-organization layer?
2. Is bumping the app contract from `row-one-app/v7` to `row-one-app/v8` appropriate?
3. Are schema, renderer, status, smoke, docs, and test changes scoped correctly?
4. Are any files missing or unnecessary?
5. Are there critical/important plan flaws that must be fixed before implementation?

Return findings grouped as Critical, Important, Minor, or None. Include concrete file references and actionable fixes. If there are no blocking issues, say so directly.
