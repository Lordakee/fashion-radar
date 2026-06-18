# Stage 113 Code Review

Verified implementation against spec/plan, re-ran the full dashboard suite, ruff
check/format, `git diff --check`, and `UV_NO_CONFIG=1 uv lock --check`.

---

## Findings

### Critical
None.

### Important
None.

The Stage 113 change is correct, minimal, and well-tested. It matches the spec
(`design.md`) and plan, and it addresses every Critical/Important/Major item from
the plan review (`opencode-stage-113-plan-review.md`):

- I1 resolved: `"generated_at": None` is present on all three return paths in
  `latest_candidate_report()` (`queries.py:41-46`, `:50-56`, `:75-80`), and the
  two equality tests
  (`test_latest_candidate_rows_returns_empty_for_missing_reports`,
  `test_latest_candidate_report_preserves_date_when_no_candidates`) now assert the
  full shape explicitly.
- M1 resolved: the `main()` rendering test exercises the `report_date` fallback
  (`generated_at: None` in the fake report), and the bonus parse-error boundary
  test (`test_dashboard_main_parse_error_does_not_emit_extra_stale_warning`)
  proves n## Stage 113 Code Review

**Critical:** None.
**Important:** None.

The implementation is correct, minimal, and well-tested. It satisfies all five review-focus points:

1. Warning fires only when `latest_collected > report_generated` (strict, post-normalization); missing/equal/older → `None`.
2. Both timestamps pass through `parse_datetime_utc()` and compare as `datetime` objects — no string comparison (`app.py:216-218`).
3. Parse-error path still emits exactly the error warning; both `generated_at` and `report_date` are `None` there so no extra stale warning leaks (`test_dashboard_main_parse_error_does_not_emit_extra_stale_warning`). Dataframe rendering unchanged.
4. Query layer only extracts `metadata.generated_at` on all three return paths — no decision logic leaked into `queries.py`.
5. No release blockers. I re-ran verification: 41 passed, ruff check/format clean, `git diff --check` clean, `UV_NO_CONFIG=1 uv lock --check` passes.

The change also resolves every item from the plan review (I1, M1–M4).

**Minor (informational):** the `main()` rendering test exercises the `report_date` fallback rather than a present `generated_at`; the helper doesn't catch corrupt-timestamp parse errors (negligible, both inputs are system-generated); the spec could note that `latest_collected_at` includes `MANUAL_IMPORT` rows. Also flagging: the large `uv.lock` working-tree diff is pre-existing mirror-URL bleed (`pypi.org` → tsinghua), not a Stage 113 change — leave it unstaged per the plan's Task 6.

Review written to `docs/reviews/opencode-stage-113-code-review.md`. Proceed to Task 6.

  the shared `items` table, which includes `MANUAL_IMPORT` rows. A post-report
  import therefore trips the warning. This is correct and the warning text
  ("newest local collected item") stays accurate, but a one-line note in
  `design.md` would prevent a future reader from mistaking it for a bug. The
  warning does not overclaim matching/import-run freshness, consistent with
  `design.md:73-77`.

- **m4. Pre-existing `uv.lock` working-tree dirtiness.** `git diff` shows a large
  `uv.lock` change, but it is entirely a registry-URL bleed
  (`https://pypi.org/simple` → `https://pypi.tuna.tsinghua.edu.cn/simple`) from a
  local mirror config, not a Stage 113 dependency change.
  `UV_NO_CONFIG=1 uv lock --check` confirms the committed lockfile is valid in
  isolation. Per the plan's Task 6, `uv.lock` must not be staged with the Stage
  113 commit. Flagging here so it is not mistaken for a stage regression.

---

## Answers To Review Focus

1. **Warning triggers only when the newest local collected item is newer than the
   report?** Yes. `candidate_report_stale_warning` (`app.py:208-225`) returns the
   warning only when `latest_collected > report_generated` after normalization;
   equal-or-older collection returns `None`, and either missing timestamp returns
   `None`. Covered by the four helper tests and the rendering test.

2. **Avoids string comparison; uses normalized datetimes?** Yes. Both inputs pass
   through `parse_datetime_utc()` (`utils/dates.py:8-17`), which converts offsets
   to UTC and assumes UTC for naive values, then compares `datetime` objects.
   `test_candidate_report_stale_warning_normalizes_naive_and_offset_datetimes`
   proves `-04:00` and naive inputs normalize to the same instant as `Z` inputs.

3. **Preserves parse-error behavior and dataframe rendering?** Yes. The Candidate
   Signals block (`app.py:256-273`) still emits the parse-error warning first, and
   because the parse-error return path sets both `generated_at` and `report_date`
   to `None` (`queries.py:50-56`), the stale helper short-circuits to `None` and
   adds no second warning. The rows dataframe still renders via the unchanged
   `if rows / else st.info` branch. Verified by
   `test_dashboard_main_parse_error_does_not_emit_extra_stale_warning` and the
   stale-rendering test.

4. **Query-layer metadata extension minimal and appropriate?** Yes. The query
   layer only extracts `metadata.generated_at` and returns it on every path; no
   stale-decision logic leaked into `queries.py`, respecting `design.md:103-104`.
   Shape is consistent across all three return paths.

5. **Release-blocking regressions or missing tests?** None. `pytest
   tests/test_dashboard.py -q` → 41 passed; `ruff check` and `ruff format
   --check` clean on the three touched files; `git diff --check` clean;
   `UV_NO_CONFIG=1 uv lock --check` passes. The added tests cover query metadata
   preservation, all four helper decision branches, offset/naive normalization,
   `main()` rendering with candidate rows, and the parse-error/no-extra-warning
   boundary.

---

## Recommendation

Proceed to Task 6 (full release gate and commit). When committing, stage only the
Stage 113 source/test/spec/plan/review files and leave the pre-existing
mirror-bleed `uv.lock` change unstaged, per the plan's Task 6 instruction.
