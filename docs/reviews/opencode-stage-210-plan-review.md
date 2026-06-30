# Stage 210 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important
None.

## Nits
- Task 1 Step 5 "Expected" prose grouped the `None` sub-case of
  `test_markdown_recent_runs_omits_error_segment_when_snippet_is_none` with the
  GREEN "contract-pinning" tests ("the `no error` fallback, `None` recent-runs,
  and JSON raw-field tests already pass"). That single test function is actually
  RED overall at `e8567fc` because its WWD `WHITESPACE_ONLY_ERROR` row trips the
  `wwd_line.endswith("9/9 stored")` and `";" not in wwd_line` assertions, even
  though its Fashionista `None` row already passes. The plan's net RED/GREEN
  outcome was already correct (the plan explicitly stated "the whitespace-only
  recent-runs test fails"), so this was wording clarity only.

  **Resolved 2026-06-29:** The Task 1 Step 5 "Expected" block was rewritten to
  enumerate each Task 1 test explicitly with its individual RED/GREEN verdict
  and one-line reasoning, removing the ambiguous grouping. No test was added,
  removed, or renamed; the post-fix plan checksum (md5) is
  `42ffc5c11a9999d6e91f4599d6c25622`, and the plan file has been set read-only
  (`chmod 444`). The Verdict, Critical, Important, Scope-guardrail,
  Plan-literality, and Existing-tests sections above remain accurate against
  the wording-fixed plan.

## Scope-guardrail checklist
1. Markdown-only change in `reports.py`: PASS — only `_render_source_health_line` (reports.py:746-753) and `_render_recent_runs` (reports.py:756-766) are edited; both are Markdown renderers called from `render_markdown_report`.
2. No new model fields: PASS — `src/fashion_radar/models/report.py` is not in the File Map and `Out of scope` explicitly excludes model edits.
3. No new validator on `last_error_message`/`error_message`: PASS — `SourceHealthReport` (report.py:113-127) and `CollectorRunReport` (report.py:130-146) keep only their existing datetime validators; snippet is applied at render time only.
4. No `DailyBrief.contract_version` / `daily-report/v1` change: PASS — no brief/model change; `contract_version` stays `daily-brief/v1` (report.py:191).
5. No Daily Brief source-caveat change: PASS — `_brief_item_for_source_health` (reports.py:347-374) and `_brief_item_for_recent_run` (reports.py:377-388) already route through `report_safe_snippet` and are not in the edit set.
6. Empty-section Markdown fallbacks unchanged: PASS — `"No source health issues recorded."` (reports.py:742) and `"No recent collector runs recorded."` (reports.py:758) are preserved verbatim in the Task 2 Step 2 replacement body.
7. `templates/daily_report.md` unchanged: PASS — not in the File Map; the `{source_health_section}` / `{recent_runs_section}` placeholders stay.
8. No dependency/lockfile/DB/schema/collector/dashboard change: PASS — `Out of scope` excludes all of these and Task 5 Step 1 asserts `git diff --exit-code -- uv.lock pyproject.toml`.
9. No social/platform/scraping/source-acquisition behavior: PASS — render-only presentation change; no collector, fetch, or source-config code touched.
10. `report_safe_snippet` already imported (no import edit): PASS — imported at `reports.py:25` inside the existing `from fashion_radar.models.report import (...)` block; Task 2 adds no import statement.

## Plan-literality check
The plan defines these tests in Task 1 (quote each name verbatim from the plan
and predict RED or GREEN before the Task 2 edit, with one line of reasoning
that references the current `src/fashion_radar/reports.py` implementation):
- `test_markdown_source_health_collapses_and_truncates_long_error` — RED — current `_render_source_health_line` interpolates raw `source.last_error_message`, so the full `LONG_ERROR` (with `TAIL_MARKER`) lands in the section and it ends with `TAIL_MARKER`, not `...`.
- `test_markdown_source_health_collapses_multiline_error` — RED — current renderer emits `MULTILINE_ERROR` verbatim, so the collapsed `"connection reset by peer retry exhausted TAIL_MARKER"` substring is absent and the raw `"connection reset\n  by peer"` substring is present.
- `test_markdown_source_health_without_error_keeps_no_error_fallback` — GREEN — current renderer uses `source.last_error_message or 'no error'`, so `None` yields `no error` and the literal string `"None"` never appears.
- `test_markdown_recent_runs_collapses_and_truncates_long_error` — RED — current `_render_recent_runs` appends raw `run.error_message` after `; ` when truthy, so `TAIL_MARKER` appears and the section ends with `TAIL_MARKER`, not `...`.
- `test_markdown_recent_runs_collapses_multiline_error` — RED — current renderer appends raw `MULTILINE_ERROR`, so the collapsed single-line form is absent and the raw multiline substring `"connection reset\n  by peer"` is present.
- `test_markdown_recent_runs_omits_error_segment_when_snippet_is_none` — RED — current renderer guards on `if run.error_message:`, which is truthy for `WHITESPACE_ONLY_ERROR = "   \n\t  "`, so the WWD line gains `; <whitespace>`, fails `wwd_line.endswith("9/9 stored")`, and contains `;`.
- `test_json_report_keeps_raw_source_health_and_run_error_fields` — GREEN — `render_json_report` calls `report.model_dump_json`, and neither `SourceHealthReport.last_error_message` nor `CollectorRunReport.error_message` has a normalizer validator, so both fields serialize raw.

## Existing-tests regression check
Will these existing tests stay green after the Task 2 edit? One line each:
- `test_markdown_report_renders_daily_brief_before_top_signals` — GREEN — Stage 210 touches neither brief/candidate rendering nor the `## Daily Brief`/`## Top Signals` ordering; no source-health or run error is exercised by this test.
- `test_daily_report_includes_stable_daily_brief_json_shape` — GREEN — JSON shape, `contract_version`, `execution_mode`, section names, and boundaries are all model/template derived and untouched by the Markdown-only edit.
- `test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs` — GREEN — exercises `build_daily_brief` -> `_brief_item_for_source_health` / `_brief_item_for_recent_run`, which already use `report_safe_snippet` and are not in the Stage 210 edit set.
- `tests/test_first_run_smoke.py` Source Health / Recent Collector Runs assertions — GREEN — the smoke fixture pins only the empty-list fallbacks (`No source health issues recorded.`, `No recent collector runs recorded.`) at test_first_run_smoke.py:722-725, and Task 2 preserves both empty-list guards verbatim.

## Summary
The plan is a tight Markdown-only hygiene change that correctly reuses the already-imported `report_safe_snippet` helper on the two remaining unfiltered error surfaces, preserves the `no error` and omit-`; <error>` fallbacks for `None`/whitespace-only snippets, and pins the raw JSON contract with a dedicated test. All five RED tests are genuinely RED at `e8567fc`, the two GREEN pinning tests are correct, the four named existing tests stay green, and Task 5's verification matrix (including the Task 5 Step 4 secret scan over the staged diff) is complete. The sole nit is a wording clarity issue in the Task 1 Step 5 "Expected" description of test 6's RED/GREEN split.
