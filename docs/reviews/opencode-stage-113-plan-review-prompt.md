# Stage 113 Plan Review Prompt

Review the Stage 113 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a runtime warning in the dashboard Candidate Signals tab when the latest
saved report snapshot predates the newest local collected item in SQLite.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-113-dashboard-candidate-stale-warning-design.md`
- `docs/superpowers/plans/2026-06-19-stage-113-dashboard-candidate-stale-warning-plan.md`
- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_dashboard.py`
- `docs/dashboard.md`

## Planned Change

Stage 113 will:

1. Preserve `metadata.generated_at` in `latest_candidate_report()` while
   keeping stale-decision logic out of the query layer.
2. Add a pure helper in `dashboard/app.py` that compares the latest local
   collected timestamp with the report generated timestamp after
   `parse_datetime_utc()` normalization.
3. Show one warning in the Candidate Signals tab when the latest local
   collected item is newer than the latest report snapshot.
4. Keep the existing candidate dataframe rendering and malformed-report warning
   behavior intact.

## Planned Tests

- Update the latest-report metadata test in `tests/test_dashboard.py` so it
  asserts `generated_at` is preserved.
- Add helper tests covering:
  - missing timestamps => `None`
  - newer local collection => warning
  - equal/newer report => `None`
  - naive/offset timestamp normalization
- Add one `main()` rendering test that asserts:
  - the stale warning appears in Candidate Signals
  - the candidate dataframe still renders

## Scope Constraints

Allowed changes:

- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_dashboard.py`
- Stage 113 review artifacts

Disallowed changes:

- `docs/dashboard.md`
- report generation semantics
- candidate discovery logic
- scoring logic
- trend delta logic
- heat mover logic
- SQLite schema or migrations
- CLI help/behavior
- external-tool adapters, collectors, connectors, platform search, scraping,
  scheduling, or browser automation
- README, project brief, package metadata, CI workflows, dependency manifests,
  or `uv.lock`
- compliance/audit/legal review product features

## Review Questions

1. Is preserving `generated_at` in `latest_candidate_report()` a reasonable
   minimal metadata extension for this warning?
2. Does the plan keep presentation logic in `app.py` and avoid overloading the
   query layer?
3. Are the planned tests strong enough to prove stale detection without becoming
   brittle?
4. Does the plan avoid overclaiming freshness for matching runs or imports that
   this surface cannot independently detect?
5. Are the focused and adjacent verification commands sufficient?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
