# Stage 111 Plan Review Prompt

Review the Stage 111 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a docs drift guard for `docs/dashboard.md` so dashboard warning,
empty-state, and stale-report expectations remain explicit: invalid trend config
warns without creating local state, Daily Brief empty states avoid creating the
data directory or database, and Candidate Signals reads the latest report JSON
and may be stale until a new report is written.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-111-dashboard-warning-staleness-docs-design.md`
- `docs/superpowers/plans/2026-06-19-stage-111-dashboard-warning-staleness-docs-plan.md`
- `docs/dashboard.md`
- `tests/test_dashboard_docs.py`
- `tests/test_dashboard.py`
- `tests/test_scoring_docs.py`
- `tests/test_candidate_discovery_docs.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_dashboard_docs.py`. It will normalize `docs/dashboard.md` and
assert:

- `Invalid or missing trend config shows a concise dashboard warning without creating the data directory or database.`
- `If the local database has not been initialized or has no retained items, the tab shows an empty-state message without creating the data directory or database.`
- `Reads candidate signals from the latest report JSON when that file is available.`
- `The Candidate Signals tab reads the latest generated report JSON.`
- `If the latest report was generated before the latest collection, local import, or matching run, the tab may be stale until a new report is written.`

## Scope Constraints

Allowed changes:

- `tests/test_dashboard_docs.py`
- Stage 111 review artifacts

Disallowed changes:

- `docs/dashboard.md`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_dashboard.py`
- `tests/test_scoring_docs.py`
- `tests/test_candidate_discovery_docs.py`
- dashboard runtime behavior, Streamlit rendering, SQLite queries, report
  loading, candidate extraction, scoring, source collection, dashboard tab
  routing, CLI behavior, source acquisition, connectors, scraping, browser
  automation, platform APIs, monitoring, scheduling, ranking, demand proof,
  coverage verification, account/cookie/session/proxy/CAPTCHA/paywall behavior,
  or compliance/audit/legal review product features

Do not expand this stage into runtime dashboard tests, dashboard docs rewrites,
report generation behavior, candidate discovery behavior, scoring behavior,
source collection, platform search, social monitoring, schema migrations,
connector behavior, README/project-brief parity, or compliance features.

## Review Questions

1. Does the plan protect real `docs/dashboard.md` warning/staleness wording
   without changing product behavior or docs text?
2. Are the planned phrases present in `docs/dashboard.md` and suitable for the
   existing whole-doc normalized dashboard docs test pattern?
3. Does appending to `tests/test_dashboard_docs.py` fit the existing dashboard
   docs test pattern?
4. Does the plan avoid overlap with scoring docs, candidate-discovery docs,
   report behavior, dashboard runtime tests, package archive checks, and runtime
   code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
