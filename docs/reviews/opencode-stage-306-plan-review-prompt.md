# opencode Stage 306 Plan Review Prompt

You are reviewing the Stage 306 plan for `/home/ubuntu/fashion-radar` after Claude Code's primary plan review.

Plan: `docs/superpowers/plans/2026-07-05-stage-306-row-one-signal-dense-takeaways-plan.md`
Primary review: `docs/reviews/claude-code-stage-306-plan-review.md`

Review objective:
- Validate or revise the plan based on Claude Code's review and your own judgment.
- Confirm signal-dense local article takeaway selection is appropriately scoped as a content-quality improvement.
- Confirm deterministic paragraph scoring uses existing explicit references and preserves original paragraph indices.
- Confirm fallback behavior and app/data contracts remain stable.
- Confirm planned tests cover signal-rich later paragraph priority, first-three fallback, original paragraph indices, Daily Local Intelligence consumption, docs drift, and forbidden-scope boundaries.
- Confirm no forbidden scope is introduced: templates/CSS redesign, source acquisition, scraping, social connectors, scheduler, monitoring, platform coverage verification, demand proof, dependencies, schema, `data/edition.json`, `row-one-app/v7`, image generation, or compliance-review product features.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
