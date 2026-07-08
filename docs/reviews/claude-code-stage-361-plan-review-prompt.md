# Claude Code Stage 361 Plan Review Prompt

Review this Stage 361 plan before implementation:

- Spec: `docs/superpowers/specs/2026-07-09-stage-361-daily-local-article-reading-brief-design.md`
- Plan: `docs/superpowers/plans/2026-07-09-stage-361-daily-local-article-reading-brief-plan.md`

Goal:
- Add generated-site-only Daily Local Article Reading Brief as a homepage-only
  section after Daily Local Article Capsules and before Saved Article Content
  Organization.
- Reuse only current-edition stories, already-saved local article paragraphs,
  brief sections, content sections, body-source labels, story references,
  generated local article page routes, and paragraph anchors.
- Do not change app contracts, schemas, JSON artifacts, fetching, extraction,
  scoring, ranking, LLM, connector, scheduling, deployment, analytics,
  personalization, recommendation, or compliance-review behavior.

Evaluate:
- Feasibility and consistency with current ROW ONE architecture.
- Whether the plan keeps the feature generated-site-only and homepage-only.
- Whether the link safety rules are strong enough.
- Whether the proposed tests cover filtering, capping, ordering, escaping,
  placement, docs, workflow guards, and CSS.
- Whether any task is over-scoped, under-specified, or likely to conflict with
  existing Stage 356-360 surfaces.

Return findings ordered by Critical, Important, and Minor. If no Critical or
Important findings exist, say that explicitly.
