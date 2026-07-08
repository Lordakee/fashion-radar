# opencode Stage 342 Plan Revision Prompt

Review the Stage 342 plan after Claude Code's primary plan review. Use
`zhipuai-coding-plan/glm-5.2 --variant max`. Operate read-only unless explicitly
asked later to revise artifacts.

Repository: `/home/ubuntu/fashion-radar`

Primary documents:

- `docs/superpowers/specs/2026-07-08-stage-342-row-one-saved-paragraph-context-cues-design.md`
- `docs/superpowers/plans/2026-07-08-stage-342-row-one-saved-paragraph-context-cues-plan.md`
- `docs/reviews/claude-code-stage-342-plan-review.md`

Objective: confirm whether the plan is ready to implement generated-site-only
saved paragraph context cues for ROW ONE local article pages. The implementation
must stay renderer-only, contract-safe, and generated-site-only.

Check for:

1. Any mismatch between the design and plan.
2. Any required fix from Claude Code's review that the plan should incorporate.
3. Any risk around strict paragraph index filtering, escaping, deduping, cue cap,
   bilingual rendering, or page-local anchors.
4. Any accidental addition of new JSON artifacts, app contracts, social-platform
   collection, scraping, browser automation, platform APIs, ranking, analytics,
   recommendation, scheduling, deployment, or compliance-review behavior.

Return a concise verdict. If the plan is acceptable, say so explicitly. If not,
list exact critical or important corrections required before implementation.
