# Claude Code Stage 305 Plan Review Prompt

You are reviewing the Stage 305 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-305-row-one-local-article-map-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether a detail-page-only local article map and paragraph target highlight are a sound next step after Stage 304 source-backed reference excerpts.
- Confirm generated anchors are renderer-owned deterministic IDs, not title-derived or user-controlled.
- Confirm the plan preserves Stage 303 `local-article-paragraph-N` anchors and Stage 304 source-backed reference excerpts.
- Confirm plain paragraph-only local articles avoid unnecessary one-link maps.
- Confirm homepage Daily Local Intelligence cards do not receive detail-only local article map or paragraph href fragments.
- Confirm the CSS scope is restrained and does not introduce a broad redesign.
- Confirm the plan keeps `row-one-app/v7`, `data/edition.json`, dependencies, source acquisition, scraping, social connectors, scheduling, image generation, demand proof, platform coverage verification, and compliance-review product features out of scope.
- Check whether planned tests are strong enough to catch missing map anchors, homepage contamination, escaping regressions, and CSS omissions.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
