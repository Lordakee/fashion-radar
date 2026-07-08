You are reviewing the Stage 362 plan for /home/ubuntu/fashion-radar.

Goal: add a generated-site-only ROW ONE homepage section named Daily Local
Source Desk. It groups already-downloaded/current-edition local article text by
source/publication, showing source name, article count, saved paragraph count,
body-source labels, top reference chips, and same-site article/paragraph links.

Design doc:
docs/superpowers/specs/2026-07-09-stage-362-daily-local-source-desk-design.md

Implementation plan:
docs/superpowers/plans/2026-07-09-stage-362-daily-local-source-desk-plan.md

Tech stack: Python 3, existing ROW ONE static renderer, pytest, ruff.

Required boundaries:
- generated-site-only;
- homepage `index.html` only;
- no schemas or app-facing payload fields;
- no JSON artifacts such as `data/daily-local-source-desk.json`,
  `data/local-source-desk.json`, or `data/source-desk.json`;
- no new route families or standalone HTML artifacts;
- no changes to `articles/index.html`, `articles/<story-id>.html`, detail
  pages, runtime JSON, manifest JSON, or edition JSON;
- no fetching, extraction, scoring, ranking, LLM, connector, scheduling,
  deployment, analytics, personalization, recommendation, or compliance-review
  behavior.

Please inspect the design and implementation plan only. Do not edit files.

Return findings grouped by:

## Critical
## Important
## Minor
## Readiness

For every finding, include concrete file/line references where possible. Focus
on feasibility, boundary compliance, missing tests, unsafe link handling,
unreviewable implementation steps, inconsistencies with existing Stage 360/361
patterns, and whether the plan is ready to implement. If a group has no
findings, say `None`.
