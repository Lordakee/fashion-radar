# Stage 209 Plan Review Prompt

Review the Stage 209 implementation plan in
`docs/superpowers/plans/2026-06-26-stage-209-daily-brief-candidate-component-cues-plan.md`.

Goal: add candidate score-component cues to generated Daily Brief candidate
summaries by reusing existing `CandidateReport.weighted_mention_component`,
`growth_component`, and `source_diversity_component`.

Context:

- Stage 191 added Daily Brief Heat Narrative content to generated reports.
- Stage 202 exposed candidate score components in daily report JSON/Markdown
  and candidate CLI JSON.
- Stage 205 carried candidate score components into the dashboard Candidate
  Signals table.
- Daily Brief candidate summaries currently show mentions, baseline mentions,
  and source counts, but not why the score landed where it did.
- This plan intentionally chooses summary-only Daily Brief output: no new
  `DailyBriefItem` fields and no `daily-brief/v1` contract version change.

Please review:

1. Is the report-only summary approach useful and scoped correctly?
2. Is avoiding new `DailyBriefItem` fields the safest compatibility choice?
3. Are the planned RED tests sufficient for JSON summary, Markdown summary, and
   direct `build_daily_brief(...)` behavior?
4. Does the plan preserve scoring, ranking, candidate extraction, report model
   schemas, source acquisition, dashboard, dependencies, and lockfiles?
5. Are docs/changelog updates appropriately local/review-oriented and free of
   demand/platform coverage claims?
6. Are release verification and review gates sufficient?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
