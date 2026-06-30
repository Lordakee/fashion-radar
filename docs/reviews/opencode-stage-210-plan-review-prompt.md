# Stage 210 Plan Review Request (Authoritative, Read-Only)

You are reviewing an implementation plan for Fashion Radar Stage 210. This is
an authoritative read-only review.

## Hard process rules (read first)

1. You may ONLY write to `docs/reviews/opencode-stage-210-plan-review.md`.
   Do NOT modify, create, or delete any other file. In particular, do NOT
   modify the plan file
   `docs/superpowers/plans/2026-06-29-stage-210-markdown-report-snippet-hygiene-plan.md`
   (it has been set read-only on purpose).
2. Quote test names, fixture variable names, and code snippets **exactly as
   written in the plan**. Do not invent, rename, or "improve" them. If you
   think a test is missing, say so as a finding — do not pretend it exists.
3. Do NOT narrate tool calls or thinking in the output document. Produce only
   the structured review.

## Output format (write this, and only this, to the review file)

```markdown
# Stage 210 Plan Review

**Verdict:** APPROVE | APPROVE_WITH_NITS | REQUEST_CHANGES

## Critical
<list, or "None.">

## Important
<list, or "None.">

## Nits
<list, or "None.">

## Scope-guardrail checklist
1. Markdown-only change in `reports.py`: PASS|FAIL — <one line>
2. No new model fields: PASS|FAIL — <one line>
3. No new validator on `last_error_message`/`error_message`: PASS|FAIL — <one line>
4. No `DailyBrief.contract_version` / `daily-report/v1` change: PASS|FAIL — <one line>
5. No Daily Brief source-caveat change: PASS|FAIL — <one line>
6. Empty-section Markdown fallbacks unchanged: PASS|FAIL — <one line>
7. `templates/daily_report.md` unchanged: PASS|FAIL — <one line>
8. No dependency/lockfile/DB/schema/collector/dashboard change: PASS|FAIL — <one line>
9. No social/platform/scraping/source-acquisition behavior: PASS|FAIL — <one line>
10. `report_safe_snippet` already imported (no import edit): PASS|FAIL — <one line>

## Plan-literality check
The plan defines these tests in Task 1 (quote each name verbatim from the plan
and predict RED or GREEN before the Task 2 edit, with one line of reasoning
that references the current `src/fashion_radar/reports.py` implementation):
- <test name 1>
- <test name 2>
- ... (list every Task 1 test defined in the plan, no more, no less)

## Existing-tests regression check
Will these existing tests stay green after the Task 2 edit? One line each:
- `test_markdown_report_renders_daily_brief_before_top_signals`
- `test_daily_report_includes_stable_daily_brief_json_shape`
- `test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs`
- `tests/test_first_run_smoke.py` Source Health / Recent Collector Runs assertions

## Summary
<2-3 sentences>
```

## Repo context

- Repo root: `/home/ubuntu/fashion-radar`
- Baseline commit: `e8567fc` (Stage 209)
- Plan under review (read it in full — it is read-only):
  `docs/superpowers/plans/2026-06-29-stage-210-markdown-report-snippet-hygiene-plan.md`

## Stage 210 objective

Apply the existing `report_safe_snippet(...)` helper to the Markdown-only
renderers `_render_source_health_line(...)` and `_render_recent_runs(...)` in
`src/fashion_radar/reports.py`, so long/multi-line/whitespace-heavy local
source/collector error messages are collapsed and truncated in the generated
Markdown `## Source Health` and `## Recent Collector Runs` sections. The JSON
report and the Pydantic model fields must stay raw and unchanged. When
`report_safe_snippet(...)` returns `None`, the Markdown fallbacks (`'no error'`
for source health; omit the fragment for recent runs) must be preserved.

## Review questions

Answer these inside the structured format above:

1. Will the Task 2 edits produce the behavior the Task 1 RED tests expect, while
   preserving the `None`/empty/whitespace-only fallbacks?
2. Is every Task 1 RED test genuinely RED against commit `e8567fc`? Quote each
   test name verbatim and predict RED or GREEN.
3. Will the named existing tests stay green after the Task 2 edit?
4. Is anything in the plan out of scope (model, JSON, DB, collector, dashboard,
   dependency, lockfile, source acquisition, social/platform)?
5. Are the Task 5 verification commands complete? Is the secret-scan step
   present?
