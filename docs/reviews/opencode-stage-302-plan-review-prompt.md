# opencode Stage 302 Plan Review Prompt

You are reviewing the Stage 302 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md`
Claude Code review: `docs/reviews/claude-code-stage-302-plan-review.md`

After Claude Code's review, revise the plan based on that review and your own judgment. If Claude Code is unavailable, act as fallback reviewer. Use GLM 5.2 max judgment.

Review objective:
- Confirm that compact nested Daily Local Intelligence segments are technically reasonable.
- Check that implementation remains local-first and deterministic, with no scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, or compliance-review product features.
- Check that the new segment JSON remains outside `data/edition.json` and does not break `row-one-app/v7`.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required plan changes, if any
