# Claude Code Stage 302 Plan Review Prompt

You are reviewing the Stage 302 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether adding nested compact segments to Daily Local Intelligence is a sound way to satisfy the user's content-organization requirement.
- Check whether the plan preserves the free-first/local-first boundary and avoids adding scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, or compliance-review product features.
- Check whether keeping `row-one-app/v7` stable while enriching only the separate `data/local-intelligence.json` artifact is technically sound.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
