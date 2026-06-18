# Stage 113 Dashboard Candidate Stale Warning Design

## Goal

Add a runtime warning in the dashboard Candidate Signals tab when the latest
saved report snapshot is older than the newest local collected item in SQLite.
This closes a real operator gap: Daily Brief already reflects new local rows,
while Candidate Signals still reads the latest report JSON and can silently lag
behind after new local data lands.

## Scope

Stage 113 is a small runtime behavior completion stage. It should preserve the
existing dashboard layout and report-loading flow while making report staleness
explicit to the user.

Allowed changes:

- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_dashboard.py`
- Stage 113 spec, plan, and review artifacts

Out of scope:

- `docs/dashboard.md` product copy
- report generation semantics
- candidate discovery logic
- scoring logic
- trend delta behavior
- heat mover behavior
- SQLite schema changes
- CLI contract changes
- source collection, connectors, platform search, scraping, scheduling, or
  browser automation
- compliance, audit, or legal review product features
- dependency or lockfile changes
- README, project brief, packaging, or CI workflow changes

## Design

The warning decision belongs in `src/fashion_radar/dashboard/app.py`, not as a
dashboard query rewrite. `main()` already has the two inputs it needs:

- `dashboard_summary(args.data_dir)["latest_collected_at"]`
- `latest_candidate_report(args.reports_dir)` metadata

`latest_candidate_report()` should preserve `metadata.generated_at` when it is
available in the report JSON, alongside the existing `report_date` field. The
query layer remains a thin metadata extractor; it does not decide whether the
report is stale.

Add a small helper in `app.py`:

```python
def candidate_report_stale_warning(
    *,
    latest_collected_at: str | datetime | None,
    report_generated_at: str | datetime | None,
) -> str | None:
    ...
```

The helper should:

- return `None` when either timestamp is missing
- normalize values through `parse_datetime_utc()`
- return `None` when the report timestamp is equal to or newer than the latest
  local collected timestamp
- return one concise warning string when the latest local collected timestamp is
  newer than the report timestamp

The warning message must stay accurate to the data the dashboard actually has.
Stage 113 should warn only about a report predating the newest local collected
item. It must not claim to detect matching-run freshness or import-run
freshness independently, because this surface does not have a separate persisted
matching timestamp.

## Test Shape

Use TDD.

`tests/test_dashboard.py` should cover:

1. Query metadata preservation:
   - `latest_candidate_report()` keeps `generated_at` from report metadata when
     present.
2. Pure helper behavior:
   - missing timestamps return `None`
   - newer collection returns a warning
   - equal/newer report returns `None`
   - offset and naive datetimes normalize correctly
3. Dashboard rendering:
   - `main()` shows the stale warning in Candidate Signals when the report
     predates the newest local collected item
   - candidate rows still render when the warning is present

## Risks

- Do not compare raw timestamp strings lexicographically.
- Do not use the report filename date for freshness.
- Do not treat same calendar day as fresh by default; compare full timestamps.
- Do not add stale-decision logic to the query layer beyond preserving report
  metadata needed by the app.
- Do not regress the existing parse-error warning path for malformed report
  JSON.
