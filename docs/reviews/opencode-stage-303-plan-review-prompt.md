# opencode Stage 303 Plan Review Prompt

You are reviewing the Stage 303 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`
Claude Code review: `docs/reviews/claude-code-stage-303-plan-review.md`
Claude Code rereview: `docs/reviews/claude-code-stage-303-plan-rereview.md`

After Claude Code's review, revise the plan based on that review and your own judgment. If Claude Code is unavailable, act as fallback reviewer. Use GLM 5.2 max judgment.

Review objective:
- Confirm the detail-page paragraph-anchor/linking approach is technically reasonable.
- Check that homepage paragraph links are deliberately deferred to avoid nested anchors, wrong-article aggregate links, and broken fragment links.
- Check that implementation remains local-first and deterministic, with no scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product feature.
- Check that links are safe and that `data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` remain unchanged.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required plan changes, if any
