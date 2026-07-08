# opencode Stage 343 Plan Revision Prompt

Review the Stage 343 plan after Claude Code's primary plan review. Use
`zhipuai-coding-plan/glm-5.2 --variant max`. Operate read-only unless explicitly
asked later to revise artifacts.

Repository: `/home/ubuntu/fashion-radar`

Primary documents:

- `docs/superpowers/specs/2026-07-08-stage-343-saved-article-content-organization-group-summary-design.md`
- `docs/superpowers/plans/2026-07-08-stage-343-saved-article-content-organization-group-summary-plan.md`
- `docs/reviews/claude-code-stage-343-plan-review.md`

Objective: confirm whether the plan is ready to implement generated-site-only
Saved Article Content Organization group summaries inside `articles/index.html`.
The implementation must stay renderer-only, contract-safe, and generated-site-only.

Check for:

1. Any mismatch between design and plan.
2. Any required fix from Claude Code's review that the plan should incorporate.
3. Any risk around safe href filtering, strict paragraph index counting,
   evidence dedupe by detail path plus paragraph index, reference dedupe/cap,
   escaping, or content organization section ordering.
4. Any accidental addition of new JSON artifacts, app contracts, source
   collection, scraping, browser automation, platform APIs, ranking, analytics,
   recommendation, scheduling, deployment, or compliance-review behavior.

Return a concise verdict. If the plan is acceptable, say so explicitly. If not,
list exact critical or important corrections required before implementation.
