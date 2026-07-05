# Claude Code Stage 304 Plan Review Prompt

You are reviewing the Stage 304 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-304-row-one-source-backed-reference-excerpts-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether source-backed reference excerpts are a sound next step after Stage 303 local paragraph anchors.
- Check whether reusing `RowOneLocalArticleContentItem.body` is preferable to adding new schema for this narrow stage.
- Confirm matched entity/designer/product cards should use saved local paragraph excerpts only when the reference name matches a saved paragraph, while unmatched or generic-label-only refs keep deterministic `type / label` fallback text.
- Confirm broad paragraph badge matching may still use reference name plus label, but excerpt body matching should not use generic labels such as `bag`, `new`, or `tracked`.
- Confirm the plan preserves Stage 303 paragraph anchor semantics and homepage Daily Local Intelligence behavior.
- Confirm the plan keeps `row-one-app/v7`, `data/edition.json`, dependencies, source acquisition, scraping, social connectors, scheduling, image generation, demand proof, platform coverage verification, and compliance-review product features out of scope.
- Check whether planned tests are strong enough to catch a regression back to metadata-only reference bodies.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
