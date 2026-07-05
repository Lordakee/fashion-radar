# Claude Code Stage 306 Plan Review Prompt

You are reviewing the Stage 306 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-306-row-one-signal-dense-takeaways-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Confirm signal-dense local article takeaway selection is a sound next step after Stage 305 local article maps.
- Confirm the selection is deterministic, local-only, and based on existing story explicit references.
- Confirm fallback preserves current first-three non-empty paragraph behavior when no explicit reference term matches.
- Confirm paragraph indices remain original zero-based saved paragraph positions.
- Confirm Daily Local Intelligence should improve through existing `takeaways` consumption without model/schema/app contract changes.
- Confirm no forbidden scope is introduced: templates/CSS redesign, source acquisition, scraping, social connectors, scheduler, monitoring, platform coverage verification, demand proof, dependencies, schema, `data/edition.json`, `row-one-app/v7`, image generation, or compliance-review product features.
- Check whether planned tests are strong enough to catch ordering, fallback, paragraph index, docs drift, and local intelligence regressions.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
End with the exact line: REVIEW_COMPLETE
