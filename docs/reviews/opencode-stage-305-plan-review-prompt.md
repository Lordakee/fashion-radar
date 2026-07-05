# opencode Stage 305 Plan Review Prompt

You are reviewing the Stage 305 plan for `/home/ubuntu/fashion-radar` after Claude Code's primary plan review.

Plan: `docs/superpowers/plans/2026-07-05-stage-305-row-one-local-article-map-plan.md`
Primary review: `docs/reviews/claude-code-stage-305-plan-review.md`

Review objective:
- Revise or validate the plan based on Claude Code's review and your own judgment.
- Confirm the local article map is an appropriately scoped detail-page readability improvement.
- Confirm generated IDs are deterministic and renderer-owned, preserving Stage 303 paragraph anchors.
- Confirm homepage behavior and app/data contracts stay stable.
- Confirm planned tests cover map rendering, wrapper IDs, CSS, escaping, paragraph target feedback, plain article negative behavior, docs drift, and homepage fragment contamination.
- Confirm no forbidden scope is introduced: scraping, source acquisition, social connectors, platform APIs, browser automation, scheduler, monitoring, demand proof, platform coverage verification, app UI, image generation, dependency changes, or compliance-review product features.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
