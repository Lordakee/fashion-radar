# Stage 113 Dashboard Candidate Stale Warning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a runtime stale-report warning in the dashboard Candidate Signals
tab when the latest report snapshot predates the newest local collected item.

**Architecture:** Keep report staleness presentation logic in
`src/fashion_radar/dashboard/app.py`, where `main()` already has both the local
SQLite summary and the latest report metadata. Preserve `generated_at` in
`latest_candidate_report()` so the app can compare real report metadata instead
of filename dates. Cover the change with one query-metadata assertion, focused
helper tests, and one dashboard `main()` rendering test.

**Tech Stack:** Python 3.11, pytest, Streamlit fakes, pathlib, uv, ruff.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-19-stage-113-dashboard-candidate-stale-warning-design.md`
  records the Stage 113 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-19-stage-113-dashboard-candidate-stale-warning-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-113-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-113-plan-review.md` records the local
  plan review.
- Modify: `src/fashion_radar/dashboard/queries.py` preserves report
  `generated_at` metadata.
- Modify: `src/fashion_radar/dashboard/app.py` adds the stale-warning helper and
  Candidate Signals warning rendering.
- Modify: `tests/test_dashboard.py` adds the failing tests and final passing
  assertions.
- Create: `docs/reviews/opencode-stage-113-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-113-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-113-plan-review-prompt.md` with this
      review request:

```markdown
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
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-113-plan-review-prompt.md)" > docs/reviews/opencode-stage-113-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-113-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Write The Failing Tests

- [ ] Update `tests/test_dashboard.py` with these failing expectations before
      changing production code:

```python
def test_latest_candidate_rows_reads_latest_report(tmp_path: Path) -> None:
    ...
    assert report["generated_at"] == "2026-06-11T00:15:00Z"


def test_candidate_report_stale_warning_returns_none_without_both_timestamps() -> None:
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at=None,
            report_generated_at="2026-06-11T00:00:00Z",
        )
        is None
    )
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T09:00:00Z",
            report_generated_at=None,
        )
        is None
    )


def test_candidate_report_stale_warning_returns_warning_when_collection_is_newer() -> None:
    warning = dashboard_app.candidate_report_stale_warning(
        latest_collected_at="2026-06-12T09:00:00Z",
        report_generated_at="2026-06-11T00:00:00Z",
    )

    assert warning is not None
    assert "stale" in warning.lower()
    assert "fashion-radar report" in warning


def test_candidate_report_stale_warning_returns_none_when_report_is_current() -> None:
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T09:00:00Z",
            report_generated_at="2026-06-12T09:00:00Z",
        )
        is None
    )
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T09:00:00Z",
            report_generated_at="2026-06-12T10:00:00Z",
        )
        is None
    )


def test_candidate_report_stale_warning_normalizes_naive_and_offset_datetimes() -> None:
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T12:00:00Z",
            report_generated_at="2026-06-12T08:00:00-04:00",
        )
        is None
    )
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T12:00:00",
            report_generated_at="2026-06-12T12:00:00Z",
        )
        is None
    )
```

- [ ] Add one `main()` rendering test that monkeypatches `dashboard_summary()`
      and `latest_candidate_report()` so the Candidate Signals tab receives one
      row plus an older `generated_at`, then assert a warning is emitted and the
      candidate dataframe still renders.

- [ ] Update the existing equality-shape tests so missing and empty latest
      report payloads explicitly expect `"generated_at": None`:
  - `test_latest_candidate_rows_returns_empty_for_missing_reports`
  - `test_latest_candidate_report_preserves_date_when_no_candidates`

- [ ] Extend the existing `FakeMainStreamlit` pattern instead of `FakeStreamlit`
      so the rendering test can capture `warnings`, `captions`, `dataframes`,
      `tabs()`, and current-tab routing in one fake without regressing the
      existing routing test.

- [ ] Run the focused test selection and confirm it fails for the expected
      reasons:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard.py -q -k "latest_candidate_rows_reads_latest_report or candidate_report_stale_warning or dashboard_main_warns_when_candidate_report_is_stale"
```

Expected: fail because `generated_at`, helper, and warning behavior are not yet
implemented.

## Task 3: Write The Minimal Implementation

- [ ] Update `src/fashion_radar/dashboard/queries.py` so
      `latest_candidate_report()` preserves `metadata.generated_at` and returns a
      consistent payload shape on every path:

```python
metadata = payload.get("metadata", {})
report_date = metadata.get("report_date")
generated_at = metadata.get("generated_at")
...
return {
    "report_date": report_date,
    "generated_at": generated_at,
    "candidate_count": len(rows),
    "rows": rows,
}
```

- [ ] In the missing-report and malformed-report return paths, also include
      `"generated_at": None` so query payloads stay shape-consistent and the
      equality tests remain explicit.

- [ ] Add the helper to `src/fashion_radar/dashboard/app.py`:

```python
def candidate_report_stale_warning(
    *,
    latest_collected_at: str | datetime | None,
    report_generated_at: str | datetime | None,
) -> str | None:
    if latest_collected_at is None or report_generated_at is None:
        return None

    latest_collected = parse_datetime_utc(latest_collected_at)
    report_generated = parse_datetime_utc(report_generated_at)
    if latest_collected <= report_generated:
        return None

    return (
        "Candidate Signals may be stale: the latest report predates the newest "
        "local collected item. Run `fashion-radar report` to refresh candidate "
        "signals."
    )
```

- [ ] Wire the warning into Candidate Signals rendering in `main()` before the
      dataframe:

```python
warning = candidate_report_stale_warning(
    latest_collected_at=summary["latest_collected_at"],
    report_generated_at=candidate_report.get("generated_at") or candidate_report["report_date"],
)
if warning is not None:
    st.warning(warning)
```

- [ ] Keep the `report_date` fallback in place for older report fixtures that
      may lack `generated_at`:

```python
report_generated_at = candidate_report.get("generated_at") or candidate_report["report_date"]
```

- [ ] Run the focused selection again:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard.py -q -k "latest_candidate_rows_reads_latest_report or candidate_report_stale_warning or dashboard_main_warns_when_candidate_report_is_stale"
```

Expected: pass.

## Task 4: Adjacent Verification

- [ ] Run adjacent dashboard coverage:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard.py -q
```

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_dashboard.py
uv --no-config run --frozen ruff format --check src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_dashboard.py
git diff --check
```

## Task 5: Code Review

- [ ] Create `docs/reviews/opencode-stage-113-code-review-prompt.md` with this
      review request:

```markdown
# Stage 113 Code Review Prompt

Review the Stage 113 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 113 adds a runtime warning in the dashboard Candidate Signals tab when
the latest report snapshot predates the newest local collected item. It keeps
the stale-decision logic in `dashboard/app.py`, preserves `generated_at` report
metadata in `dashboard/queries.py`, and adds focused tests in
`tests/test_dashboard.py`.

## Files To Review

- `src/fashion_radar/dashboard/queries.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_dashboard.py`
- `docs/superpowers/specs/2026-06-19-stage-113-dashboard-candidate-stale-warning-design.md`
- `docs/superpowers/plans/2026-06-19-stage-113-dashboard-candidate-stale-warning-plan.md`
- `docs/reviews/opencode-stage-113-plan-review.md`

## Review Focus

1. Does the runtime warning trigger only when the newest local collected item is
   newer than the latest report timestamp?
2. Does the implementation avoid string-based timestamp comparison and use
   normalized datetimes instead?
3. Does the change preserve existing Candidate Signals parse-error behavior and
   dataframe rendering?
4. Is the query-layer metadata extension minimal and appropriate?
5. Are there any release-blocking regressions or missing tests?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-113-code-review-prompt.md)" > docs/reviews/opencode-stage-113-code-review.md
```

- [ ] Fix any Critical or Important findings before Task 6.

## Task 6: Full Release Gate And Commit

- [ ] Run the release hygiene gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
```

- [ ] If `uv.lock` is already dirty before this stage, do not stage it. Record
      that pre-existing state in the handoff summary and keep the commit scoped
      to Stage 113 files only.

- [ ] Run staged-file hygiene before commit:

```bash
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit only the intended files with message:

```bash
git commit -m "Add dashboard candidate stale warning"
```
```
