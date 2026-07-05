# opencode Stage 304 Plan Review Prompt

You are reviewing the Stage 304 plan for `/home/ubuntu/fashion-radar` after Claude Code's primary plan review.

Plan: `docs/superpowers/plans/2026-07-05-stage-304-row-one-source-backed-reference-excerpts-plan.md`
Primary review: `docs/reviews/claude-code-stage-304-plan-review.md`

Review objective:
- Revise or validate the plan based on Claude Code's review and your own judgment.
- Confirm source-backed reference excerpts are technically reasonable and appropriately scoped.
- Check whether the plan should remain schema-neutral by reusing `RowOneLocalArticleContentItem.body`.
- Confirm matched references use saved local paragraph excerpts only when the reference name matches a saved paragraph, while unmatched or generic-label-only references retain deterministic fallback metadata.
- Confirm broad paragraph badge matching may still use reference name plus label, but excerpt body matching should not use generic labels such as `bag`, `new`, or `tracked`.
- Confirm tests cover generator output, rendered detail pages, local article JSON, docs drift, and no regression to metadata-only bodies.
- Confirm no forbidden scope is introduced: scraping, source acquisition, social connectors, platform APIs, browser automation, scheduler, monitoring, demand proof, platform coverage verification, app UI, image generation, dependency changes, or compliance-review product features.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
