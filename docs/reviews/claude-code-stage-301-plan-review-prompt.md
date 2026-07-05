# Claude Code Stage 301 Plan Review Prompt

You are reviewing the Stage 301 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-301-row-one-daily-local-intelligence-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether the plan preserves the free-first/local-first boundary and avoids adding social scraping, platform APIs, app UI work, compliance-review product features, paywall bypass, or platform monitoring.
- Check whether keeping `row-one-app/v7` stable while adding a separate local-intelligence site artifact is technically sound.
- Check whether the proposed deterministic aggregation is testable and compatible with the existing ROW ONE renderer and generated-site cleanup.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
