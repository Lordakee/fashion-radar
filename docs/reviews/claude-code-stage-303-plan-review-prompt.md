# Claude Code Stage 303 Plan Review Prompt

You are reviewing the Stage 303 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether stable local paragraph anchors and detail-page paragraph-index links are a sound next step after Stage 302 content segments.
- Check that the plan intentionally defers homepage paragraph links to avoid nested anchors and wrong-article aggregate links.
- Check that the plan preserves the free-first/local-first boundary and avoids scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features.
- Check that generated links are safe, deterministic, and do not affect `data/edition.json`, `data/local-intelligence.json`, or `row-one-app/v7`.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
