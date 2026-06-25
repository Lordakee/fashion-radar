# Stage 205 Plan Review Prompt

Review the Stage 205 implementation plan in
`docs/superpowers/plans/2026-06-25-stage-205-dashboard-candidate-score-parity-plan.md`.

Goal: make the dashboard Candidate Signals table preserve Stage 202 candidate
score-component fields from the latest report JSON, while staying
backward-compatible with older reports.

Context:

- Stage 202 added `weighted_mention_component`, `growth_component`, and
  `source_diversity_component` to candidate report JSON/Markdown and candidate
  CLI JSON.
- `latest_candidate_report()` in `src/fashion_radar/dashboard/queries.py`
  currently projects only the final score, mention counts, distinct sources,
  and report date, dropping the component fields before `app.py` renders
  `st.dataframe(rows)`.
- `app.py` already renders the row dictionaries directly. The minimal fix is a
  query projection change plus tests/docs.
- This stage must not change scoring, candidate ranking, report generation,
  database schema, source packs, entity packs, collectors, dashboard write
  behavior, external/community/imported command surfaces, social/platform
  connectors, scraping, demand proof, platform coverage verification,
  dependency files, `uv.lock`, `pyproject.toml`, or compliance-review product
  features.

Please review:

1. Is this a reasonable next report/dashboard transparency stage after Stage
   204?
2. Is adding the five fields to `latest_candidate_report()` row projection the
   right minimal implementation?
3. Are the proposed defaults for legacy reports correct?
4. Should representative items or entity match evidence be left out of this
   node?
5. Are the RED tests sufficient for preserving Stage 202 fields and keeping
   older report JSON compatible?
6. Are docs/changelog changes and verification commands sufficient?
7. Does the plan avoid source acquisition, connectors, scraping, demand proof,
   platform coverage verification, dependency changes, and compliance-review
   behavior?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
