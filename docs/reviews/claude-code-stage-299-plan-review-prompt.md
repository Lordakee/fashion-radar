# Claude Code Stage 299 Plan Review Prompt

Use maximum reasoning effort. Do not edit files.

Review the Stage 299 plan in `/home/ubuntu/fashion-radar`:

- `docs/superpowers/plans/2026-07-05-stage-299-row-one-local-article-brief-sections-plan.md`

Context:

- User wants ROW ONE to organize fashion information locally, not just provide
  external links.
- Stage 297 made local article sidecars long enough to read.
- Stage 298 made local article bodies bilingual/compatible with the existing
  language toggle.
- Current next step is adding a structured brief inside each local article
  sidecar and detail page.

Planned approach:

- Add optional `brief_sections` to `RowOneLocalArticle` sidecars.
- Build four sections from existing `RowOneStory` localized fields:
  `what_happened`, `why_it_matters`, `signal_context`, `watch_next`.
- Render the brief inside the existing local article section, above body
  paragraphs, using existing language-toggle spans.
- Do not change `row-one-app/v7`, `data/edition.json`, collection, scraping,
  platform APIs, translation services, deployment, app UI, or compliance-review
  behavior.

Review questions:

1. Is this plan technically feasible with the current model/article/template
   architecture?
2. Does it preserve backward compatibility for local articles without
   `brief_sections`?
3. Are the planned tests sufficient for builder population, sidecar JSON,
   bilingual rendering, escaping via existing `_esc`, and empty brief fallback?
4. Are there any Critical or Important issues to fix before implementation?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly.
