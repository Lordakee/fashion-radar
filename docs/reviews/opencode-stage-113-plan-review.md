# Stage 113 Plan Review

I've reviewed all files. Here are my findings.

---

## Findings

### Critical
None.

### Important
None.

**I1. `generated_at` shape ambiguity in non-happy `latest_candidate_report()` return paths.**
The Task 3 snippet only shows the happy-path return (`queries.py:67`) gaining
`generated_at`. There are three other return paths in
`latest_candidate_report()`:

- missing reports path (`queries.py:41`): `{"report_date": None, "cand# Stage 113 Plan Review

## Findings

### Critical
None.

### Important
None.

**I1. `generated_at` shape ambiguity in non-happy `latest_candidate_report()` return paths.**
The Task 3 snippet only shows the happy-path return (`queries.py:67`) gaining
`generated_at`. There are three other return paths (`queries.py:41` missing-reports,
`queries.py:45-50` malformed-JSON). The plan doesn't say whether they also gain
`"generated_at": None`.

- If the implementer adds it to all paths (cleaner), two existing **equality**
  tests break and aren't mentioned in "Planned Tests":
  `test_latest_candidate_rows_returns_empty_for_missing_reports`
  (`tests/test_dashboard.py:1161`) and
  `test_latest_candidate_report_preserves_date_when_no_candidates`
  (`tests/test_dashboard.py:1176`). The malformed-JSON test uses per-key
  asserts and survives either way.
- If the implementer follows the snippet literally, the dict shape is
  inconsistent across paths. The `.get("generated_at")` wiring tolerates it,
  but future equality tests become brittle.

Fix: explicitly add `"generated_at": None` to all return paths and note the
two equality tests need updating.

### Minor

- **M1.** The `report_date` fallback in `main()` wiring
  (`candidate_report.get("generated_at") or candidate_report["report_date"]`)
  is untested. Add a helper or query test for older reports lacking
  `generated_at`.
- **M2.** Task 2 asserts `report["generated_at"] == "2026-06-11T00:15:00Z"`,
  but the existing fixture (`tests/test_dashboard.py:1120-1138`) has no
  `generated_at`. The implementer must add it; the plan's `...` hides this.
- **M3.** `test_candidate_report_stale_warning_normalizes_naive_and_offset_datetimes`
  only tests `Z` and `-04:00` inputs - neither is actually naive. Either
  rename or add a genuinely naive input like `"2026-06-12T12:00:00"`.
- **M4.** The `main()` rendering test needs a fake that captures both tab
  labels and warnings. Existing `FakeMainStreamlit` lacks warnings capture;
  `FakeStreamlit` lacks `tabs()`/`set_page_config`/`metric`. Plan should
  specify which fake to extend.

## Answers To Review Questions

1. **Reasonable metadata extension?** Yes. `ReportMetadata` already requires
   `generated_at` (`models/report.py:26`) and `render_json_report` already
   serializes it. Stage 113 only adds the dashboard read side; no semantics
   change, and avoids repurposing `report_date` (which is scoring `as_of`).
2. **Presentation logic in `app.py`?** Yes. Query layer only extracts a
   field; the stale-decision helper lives in `app.py`. No comparison logic
   leaks into `queries.py`, consistent with the spec's risk list.
3. **Tests strong enough?** Mostly. Helper tests cover the core branches
   (missing, newer, equal/newer, offset). Gaps: I1 (non-happy equality
   tests), M1 (fallback), M3 (naive mismatch). Not brittle - behavior-based
   substring asserts.
4. **Avoids overclaiming freshness?** Yes. Warning text matches what the
   helper detects. Note: `latest_collected_at` includes `MANUAL_IMPORT` rows,
   so post-report imports trip the warning - that's correct behavior, but the
   spec could mention it.
5. **Verification sufficient?** Yes. Focused `-k` selection, full file run,
   ruff check/format, `git diff --check`, full release gate. Note the two
   equality tests in I1 will be caught by the Task 4 full-file run even
   though they aren't in the `-k` filter.

## Recommendation

Proceed to Task 2 after addressing I1 (add `generated_at: None` to all
return paths; note the two equality test updates; pin the fixture metadata
block per M2). M1-M4 are non-blocking polish.

Review written to `docs/reviews/opencode-stage-113-plan-review.md`.
fig`,
`title`, `metric`, and `tabs`. The new rendering test needs both behaviors.
The implementer will need to extend one of these fakes or add a third. Not a
blocker - the existing patterns make this straightforward - but the plan
should mention which fake to extend so the rendering test does not regress
`test_dashboard_main_routes_heat_movers_and_trend_deltas_by_label`.

## Answers To Review Questions

1. **Is preserving `generated_at` reasonable?** Yes. `ReportMetadata`
   (`src/fashion_radar/models/report.py:23-33`) already requires `generated_at`
   and normalizes it through `parse_datetime_utc`. `render_json_report`
   (`src/fashion_radar/reports.py:75-76`) serializes the full model, so
   `generated_at` is already on disk for every report. Stage 113 only adds
   the read side in the dashboard query layer. This is the minimal metadata
   extension needed and avoids repurposing `report_date` (which is the scoring
   `as_of`, not the generation instant).

2. **Does the plan keep presentation logic in `app.py`?** Yes. The query
   layer only extracts an additional metadata field; the stale-decision helper
   lives in `app.py` and `main()` calls it. No comparison logic leaks into
   `queries.py`. The spec's risk list (`design.md:98-106`) explicitly forbids
   adding stale-decision to the query layer, and the plan respects that.

3. **Are the planned tests strong enough?** Mostly yes. The four helper tests
   cover missing-input, newer-collection, equal/newer-report, and offset
   normalization, which are the core decision branches. Gaps: see I1 (equality
   tests for non-happy query paths), M1 (fallback path), and M3 (naive-input
   coverage mismatch). None are brittle - they assert behavior, not
   formatting, and the warning-string assertions use lowercase substring
   checks (`"stale"`, `"fashion-radar report"`) that tolerate reasonable
   wording tweaks.

4. **Does the plan avoid overclaiming freshness?** Yes. The warning text -
   "the latest report predates the newest local collected item" - is exactly
   what the helper detects. It does not claim matching-run or import-run
   freshness, consistent with the spec (`design.md:73-77`). One observation:
   `latest_collected_at` from `dashboard_summary` includes `MANUAL_IMPORT`
   rows (they share the `items` table, `repositories.py:58`), so a manual
   import after the report will trip the warning. This is correct behavior
   (imports are local data the report doesn't reflect), not overclaiming, but
   the spec could call it out so reviewers don't read it as a bug.

5. **Are verification commands sufficient?** Yes. The focused selection
   (`-k "latest_candidate_rows_reads_latest_report or candidate_report_stale_warning or dashboard_main_warns_when_candidate_report_is_stale"`)
   targets exactly the touched code paths; the adjacent run executes the full
   `tests/test_dashboard.py`; Task 4 adds `ruff check`, `ruff format --check`,
   and `git diff --check`; Task 6 runs the full release gate including
   `UV_NO_CONFIG=1 uv lock --check`. Appropriate for a three-file dashboard
   stage. Note: `tests/test_dashboard.py:1161` and `:1176` will also need to
   be touched (see I1) and should be in the focused selection's blast radius
   even though they aren't named in the `-k` filter - running the full file in
   Task 4 catches them.

## Recommendation

Proceed to Task 2 after addressing I1. Concretely:

- In the Task 3 snippet, add `"generated_at": None` to the missing-reports
  return (`queries.py:41`) and the malformed-JSON return (`queries.py:45-50`).
- In Task 2, note that `test_latest_candidate_rows_returns_empty_for_missing_reports`
  and `test_latest_candidate_report_preserves_date_when_no_candidates` must
  include `"generated_at": None` in their expected dicts.
- In Task 2, pin the exact metadata block for the
  `test_latest_candidate_rows_reads_latest_report` fixture, including
  `"generated_at": "2026-06-11T00:15:00Z"` (see M2).

M1-M4 are non-blocking polish items and can be addressed during implementation.
